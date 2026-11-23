"""Mixagem 'A história do Vasco' (mesmo padrão da Copa do Brasil v2):
narração Gemini na frente, trilha CC0 bem audível por baixo (abaixa um pouco sob a voz),
torcida gravada de verdade (SSE Library, CC0) no gancho e em momentos de estádio,
e só efeitos limpos (pop/batida em senoide) — nada de ruído/whoosh sintetizado."""
import json, os, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt
ROOT = os.path.join(os.path.dirname(__file__), ".."); PUB = os.path.join(ROOT, "public")
D = json.load(open(os.path.join(ROOT, "src", "data", "vasco.json")))
SR = 48000; DUR = D["duracaoSegundos"]; N = int(DUR * SR); tt = np.arange(N) / SR
def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float64) / 32768
db = lambda x: 10 ** (x / 20)
def place(bus, clip, at, g=1.0, fade=0.0):
    clip = clip.copy()
    if fade:
        f = int(fade * SR); f = min(f, len(clip) // 2)
        clip[:f] *= np.linspace(0, 1, f)[:, None]; clip[-f:] *= np.linspace(1, 0, f)[:, None]
    i = int(round(at * SR))
    if i >= len(bus): return
    n = min(len(clip), len(bus) - i); bus[i:i + n] += clip[:n] * g
rms = lambda x: np.sqrt(np.mean(x ** 2)) + 1e-9
# voz
voice = np.zeros((N, 2)); place(voice, load(os.path.join(PUB, D["audio"]["narracao"])), D["audio"]["narracaoEm"])
voice = sosfilt(butter(2, 90, "hp", fs=SR, output="sos"), voice, axis=0)
voice = np.tanh(voice * 1.4) / np.tanh(1.4)
# trilha: loop se precisar, volume ~ -9 dB em relação à voz, ducking leve
mus = load(os.path.join(PUB, D["audio"]["trilha"]))
off = int(38 * SR); mus = mus[off:]   # a faixa tem 20 s de introdução baixa: começa na parte cheia
# nivela o volume da trilha (janela de 3 s) para ela ficar audível o vídeo todo
_w = int(3 * SR); _e = np.sqrt(np.convolve((mus ** 2).mean(1), np.ones(_w) / _w, mode="same")) + 1e-6
mus = mus * (np.median(_e) / _e)[:, None] ** 0.8
while len(mus) < N: mus = np.concatenate([mus, mus])
music = mus[:N].copy()
music *= rms(voice[voice.any(1)]) / rms(music) * db(-6)
env = np.convolve(np.abs(voice).mean(1), np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
music *= (1 - 0.3 * np.clip(env / 0.06, 0, 1))[:, None]
music *= np.clip(tt / 0.6, 0, 1)[:, None] * np.clip((DUR - tt) / 1.2, 0, 1)[:, None]
# torcida real (SSE Library, CC0 — reaproveitada da Copa do Brasil)
cro = load(os.path.join(PUB, "copa-do-brasil", "audio", "sfx", "torcida-futebol.mp3"))
amb = load(os.path.join(PUB, "copa-do-brasil", "audio", "sfx", "torcida-ambiente.mp3"))
cro = cro / rms(cro[int(6 * SR):int(20 * SR)]); amb = amb / rms(amb[int(20 * SR):int(40 * SR)])
sfx = np.zeros((N, 2)); V = rms(voice[voice.any(1)])
cena = {c["id"]: c for c in D["cenas"]}
def torcida(c0, c1, nivel, src=cro, start=6.0):
    seg = src[int(start * SR): int(start * SR) + int((c1 - c0) * SR)]
    place(sfx, seg * V, c0, db(nivel), fade=0.4)
torcida(cena["camisas"]["fim"] - 1.7, cena["camisas"]["fim"] + 0.2, -11, cro, 12)    # campeões de 1923
torcida(cena["saojanuario"]["fim"] - 3.0, cena["saojanuario"]["fim"] + 0.2, -10, cro, 18)
torcida(cena["expresso"]["fim"] - 4.2, cena["expresso"]["fim"], -15, amb, 25)
torcida(cena["idolos"]["fim"] - 4.0, cena["idolos"]["fim"] + 0.3, -8, cro, 30)     # Libertadores 98
torcida(cena["cta"]["inicio"], DUR, -17, amb, 40)
# efeitos limpos (senoides, sem ruído)
def tone(f0, f1, d, decay, amp=1.0):
    t = np.arange(int(d * SR)) / SR; f = np.linspace(f0, f1, len(t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay) * amp
    return np.stack([x, x], 1)
pop = tone(900, 300, 0.12, 30); thump = tone(140, 50, 0.35, 12)
g = cena["gancho"]; dur_g = g["fim"] - g["inicio"]
place(sfx, thump * V * 3, g["inicio"] + dur_g * (5.5 / 8.33) + 1.0, db(-9))      # carimbo NÃO!
place(sfx, thump * V * 3, cena["liga"]["inicio"] + 2.4 + 0.27, db(-12))          # CORTEM 12!
place(sfx, thump * V * 3, cena["resposta"]["fim"] - 2.3, db(-10))                # RESPOSTA HISTÓRICA
for k, d in [("gancho", 0.07), ("fundacao", 0.13), ("nome", 2.3), ("camisas", 2.2), ("expresso", 0.07)]:
    place(sfx, pop * V * 2, cena[k]["inicio"] + d, db(-12))                       # carimbos de ano
mix = voice + music + sfx
mix = np.tanh(mix * 1.05) / np.tanh(1.05); mix *= 0.93 / max(np.max(np.abs(mix)), 1e-9)
out = os.path.join(PUB, D["audio"]["mix"])
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("mix ->", out, "| voz rms", round(rms(voice), 4), "| trilha rms", round(rms(music), 4))
