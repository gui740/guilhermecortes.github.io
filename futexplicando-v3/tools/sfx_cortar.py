"""Recorta efeitos individuais das gravações CC0 (biblioteca/sfx/raw_*.mp3) nos picos de energia."""
import subprocess, numpy as np, wave, os
SR = 48000
B = "biblioteca/sfx"
def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
def save(x, p):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    f = wave.open(p, "wb"); f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((x * 32767).astype(np.int16).tobytes()); f.close()
def picos(x, n, min_gap=0.4):
    hop = int(0.01 * SR); e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    out = []
    for i in np.argsort(-e):
        if all(abs(i - j) > min_gap * 100 for j in out): out.append(i)
        if len(out) >= n: break
    return sorted(out), e
def corta(x, i, antes, depois, fade=0.01):
    a = max(0, int((i / 100 - antes) * SR)); b = min(len(x), int((i / 100 + depois) * SR))
    y = x[a:b].copy(); f = int(fade * SR); y[:f] *= np.linspace(0, 1, f); y[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR)); return y
x = load(f"{B}/raw_boom.mp3"); p, e = picos(x, 1); save(corta(x, p[0], 0.05, 2.2), f"{B}/boom.wav")
x = load(f"{B}/raw_swish.mp3"); p, e = picos(x, 3, 1.0); save(corta(x, p[1], 0.35, 0.35), f"{B}/whoosh.wav")
x = load(f"{B}/raw_ariete.mp3"); p, e = picos(x, 2, 1.0); save(corta(x, p[0], 0.02, 0.8), f"{B}/impacto.wav")
x = load(f"{B}/raw_machado.mp3"); p, e = picos(x, 3, 0.5); save(corta(x, p[0], 0.01, 0.35), f"{B}/martelo.wav")
x = load(f"{B}/raw_sino.mp3"); p, e = picos(x, 1); save(corta(x, p[0], 0.01, 1.8), f"{B}/ding.wav")
x = load(f"{B}/raw_torcida_festa.mp3"); p, e = picos(x, 1, 5); save(corta(x, p[0], 1.5, 6.0, 0.3), f"{B}/torcida_festa.wav")
x = load(f"{B}/raw_torcida_amb.mp3"); save(x[int(20 * SR):int(45 * SR)], f"{B}/torcida_amb.wav")
x = load(f"{B}/raw_chuva.mp3"); save(x[int(2 * SR):int(22 * SR)], f"{B}/chuva.wav")
for f in sorted(os.listdir(B)):
    if f.endswith(".wav"): w = wave.open(f"{B}/{f}"); print(f, round(w.getnframes() / SR, 2))
