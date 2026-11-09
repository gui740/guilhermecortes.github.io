#!/usr/bin/env python3
"""Narração com Gemini TTS — o roteiro INTEIRO numa chamada só (fala contínua e natural),
depois dividida por cena usando os timestamps por palavra do Whisper.

Requer GEMINI_API_KEY.   Uso: python3 scripts/narracao.py [Voz] [modelo]
Saídas: assets/narracao/<cena>.wav, assets/narracao/completa.wav, src/data/narracao.json
"""
import sys, json, re, pathlib, subprocess, base64, os, time, urllib.request, urllib.error
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from whisper_util import load16k
from faster_whisper import WhisperModel

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOZ = sys.argv[1] if len(sys.argv) > 1 else "Charon"
MODEL = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
KEY = os.environ.get("GEMINI_API_KEY") or sys.exit("Defina GEMINI_API_KEY")
ROT = json.loads((ROOT / "config" / "roteiro.json").read_text())
ORDEM = list(ROT)
ND = ROOT / "assets" / "narracao"; ND.mkdir(parents=True, exist_ok=True)

# Direção curta: conversa natural de brasileiro. Nada de "voz baixa / pausas / respiração",
# que deixa a fala arrastada e com cara de outro idioma.
DIRECAO = ("Leia em português do Brasil, com sotaque brasileiro natural, como um brasileiro de uns 30 anos "
           "contando pra um amigo sobre filmes de terror que viu. Tom de conversa, descontraído e um pouco intrigado, "
           "ritmo normal de fala, fluido, sem pausas longas e sem dramatizar:\n\n")

def gerar(texto, saida):
    body = {"contents": [{"parts": [{"text": DIRECAO + texto}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"languageCode": "pt-BR",
                                                  "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOZ}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    for t in range(5):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r); break
        except urllib.error.HTTPError as e:
            corpo = e.read().decode(errors="ignore")
            if "PerDay" in corpo: sys.exit(f"Cota diária do {MODEL} esgotada.")
            if e.code in (429, 500, 503) and t < 4:
                print("  ", e.code, "esperando..."); time.sleep(30 * (t + 1))
            else:
                sys.exit(f"{e.code}: {corpo[:400]}")
    pcm = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    raw = saida.with_suffix(".pcm"); raw.write_bytes(pcm)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(raw), str(saida)], check=True)
    raw.unlink()

def ler24(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", "24000", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def salvar(p, x):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", str(p)],
                   input=x.astype(np.float32).tobytes(), check=True)

if __name__ == "__main__":
    texto = "\n\n".join(ROT[k] for k in ORDEM)
    comp = ND / "completa.wav"
    if "--reusar" not in sys.argv:
        gerar(texto, comp)
    x = ler24(comp)
    model = WhisperModel("small", compute_type="int8")
    a16 = load16k(str(comp))
    # 1) idioma detectado sem forçar (mede se soa como português)
    _, info = model.transcribe(a16[:16000 * 20], language=None)
    print(f"idioma detectado: {info.language} ({info.language_probability:.2f})")
    segs, _ = model.transcribe(a16, language="pt", word_timestamps=True, initial_prompt=texto)
    ws = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]
    tokens = {k: ROT[k].split() for k in ORDEM}
    total = sum(len(v) for v in tokens.values())
    dur = len(x) / 24000
    print(f"{VOZ}/{MODEL}: {dur:.1f}s, {len(ws)} palavras (roteiro {total}), {len(ws)/dur:.2f} palavras/s")
    if len(ws) != total:
        sys.exit("contagem de palavras não bate com o roteiro — gere de novo")
    # 2) corta por cena no meio do silêncio entre a última palavra de uma e a primeira da próxima
    dados = {"voz": VOZ, "modelo": MODEL, "cenas": {}}
    i = 0; cortes = [0.0]
    limites = []
    for k in ORDEM:
        n = len(tokens[k]); limites.append((i, i + n - 1)); i += n
    for (a, b), (c, _) in zip(limites, limites[1:]):
        cortes.append((ws[b]["e"] + ws[c]["s"]) / 2)
    cortes.append(dur)
    for j, k in enumerate(ORDEM):
        t0, t1 = cortes[j], cortes[j + 1]
        a, b = limites[j]
        ini = max(t0, ws[a]["s"] - 0.08)   # começa logo antes da 1ª palavra
        fim = min(t1, ws[b]["e"] + 0.25)   # termina pouco depois da última
        seg = x[int(ini * 24000):int(fim * 24000)].copy()
        f = int(0.01 * 24000); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        salvar(ND / f"{k}.wav", seg)
        pal = [{"w": tok, "s": round(ws[a + q]["s"] - ini, 3), "e": round(ws[a + q]["e"] - ini, 3)} for q, tok in enumerate(tokens[k])]
        dados["cenas"][k] = {"dur": round(len(seg) / 24000, 3), "palavras": pal}
        print(f"  {k}: {len(seg)/24000:.2f}s")
    (ROOT / "src" / "data" / "narracao.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1))
    print("total narração:", round(sum(c["dur"] for c in dados["cenas"].values()), 2), "s")
