"""Timestamps por palavra para a voz do Gemini (que não devolve word boundaries).
1) gera a mesma fala com edge-tts só como REFERÊNCIA de tempos (WordBoundary);
2) alinha referência x Gemini com DTW sobre MFCC e transfere o início/fim de cada palavra.
Saída: assets/vo_gemini/<bloco>.json"""
import asyncio, json, os, subprocess, sys
import numpy as np, librosa
sys.path.insert(0, os.path.dirname(__file__))
import certifi
_CA = os.environ.get("SSL_CERT_FILE")
if _CA and os.path.exists(_CA): certifi.where = lambda: _CA
import edge_tts
from gemini_tts import BLOCKS, block_text, texts
SR, HOP = 16000, 160
def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
async def ref(b):
    os.makedirs("assets/vo_ref", exist_ok=True)
    c = edge_tts.Communicate(block_text(b), "pt-BR-AntonioNeural", boundary="WordBoundary", proxy=os.environ.get("HTTPS_PROXY") or None)
    words = []
    with open(f"assets/vo_ref/{b}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    return words
def feats(x):
    m = librosa.feature.mfcc(y=x, sr=SR, n_mfcc=20, hop_length=HOP, n_fft=400)[1:]
    m = np.vstack([m, librosa.feature.delta(m)])
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
def align(b):
    words = asyncio.run(ref(b))
    T = texts(); expect = []
    for i in BLOCKS[b]: expect += [(i, w) for w in T[i].replace(",", " ").replace(".", " ").replace(":", " ").replace("?", " ").split()]
    assert len(words) == len(expect), (b, len(words), len(expect), [w["w"] for w in words])
    xr, xg = load(f"assets/vo_ref/{b}.mp3"), load(f"assets/vo_gemini/{b}.wav")
    D, wp = librosa.sequence.dtw(X=feats(xr), Y=feats(xg), metric="cosine", subseq=False)
    wp = wp[::-1]                                     # (frame_ref, frame_gemini) crescente
    fr, fg = wp[:, 0], wp[:, 1]
    def to_g(t, first=True):
        f = int(round(t * SR / HOP)); idx = np.where(fr == min(f, fr.max()))[0]
        return float(fg[idx[0] if first else idx[-1]] * HOP / SR)
    out = []
    for (line, _), w in zip(expect, words):
        t0 = to_g(w["t"]); t1 = max(t0 + 0.04, to_g(w["t"] + w["d"], first=False))
        out.append({"w": w["w"].strip(".,:?!"), "t": round(t0, 3), "d": round(t1 - t0, 3), "line": line})
    # monotonia
    for a, c in zip(out, out[1:]):
        if c["t"] < a["t"] + 0.03: c["t"] = round(a["t"] + 0.03, 3)
    json.dump({"text": block_text(b), "words": out}, open(f"assets/vo_gemini/{b}.json", "w"), ensure_ascii=False)
    print(b, len(out), "palavras | custo médio DTW", round(float(D[-1, -1]) / len(wp), 3), "| fim", out[-1]["t"])
if __name__ == "__main__":
    for b in (sys.argv[1:] or BLOCKS): align(b)
