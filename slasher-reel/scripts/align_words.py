"""Timestamps por palavra (Whisper) frase a frase, alinhados ao texto do roteiro -> assets/audio/words.json"""
from faster_whisper import WhisperModel
import librosa, json, re, numpy as np, os
A = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
m = WhisperModel("medium", device="cpu", compute_type="int8")
y, sr = librosa.load(f"{A}/narracao.wav", sr=16000)
marks = json.load(open(f"{A}/phrase_marks_raw.json"))
P = [p[0] for p in json.load(open(f"{A}/phrases.json"))]
disp = lambda t: t.replace("Agá Bê Ó", "HBO").replace("Lúqui", "Looke").replace("Práime Vídeo", "Prime Video").replace("Tóquin Hórror", "Talking Horror").replace("esquiar", "esqui")
vow = lambda w: max(1, len(re.findall(r"[aeiouáéíóúâêôãõà]+", w.lower())))
out = []
for mk in marks:
    i = mk["i"]; a, b = mk["start"], mk["end"]
    seg = y[int(a * sr):int(b * sr) + 800]
    words = disp(P[i]).split()
    ws = [w for s in m.transcribe(seg, language="pt", word_timestamps=True)[0] for w in s.words]
    ok = len(ws) == len(words)
    if ok:
        tl = [(a + w.start, a + w.end) for w in ws]
    else:  # mesmo nº de palavras não bateu: distribui pelas sílabas dentro da frase
        v = np.array([vow(w) for w in words], float); c = np.concatenate([[0], np.cumsum(v)]) / v.sum()
        tl = [(a + c[k] * (b - a), a + c[k + 1] * (b - a)) for k in range(len(words))]
    for k, w in enumerate(words):
        out.append({"w": w, "s": round(tl[k][0], 3), "e": round(tl[k][1], 3), "phrase": i})
    print(i, "whisper" if ok else f"PROP({len(ws)} vs {len(words)})", " ".join(f"{w}@{tl[k][0]:.2f}" for k, w in enumerate(words)))
json.dump(out, open(f"{A}/words.json", "w"), ensure_ascii=False, indent=0)
