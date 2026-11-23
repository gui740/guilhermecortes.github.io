"""Mixagem 'A história da Copa do Brasil': narração Gemini + trilha CC0 baixa + whoosh nos cortes + torcida no gancho."""
import json, os, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt
ROOT = os.path.join(os.path.dirname(__file__), ".."); PUB = os.path.join(ROOT, "public")
D = json.load(open(os.path.join(ROOT, "src", "data", "copa-do-brasil.json")))
SR = 48000; DUR = D["duracaoSegundos"]; N = int(DUR * SR)
def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float64) / 32768
db = lambda x: 10 ** (x / 20)
def place(bus, clip, at, g=1.0):
    i = int(round(at * SR));
    if i >= len(bus): return
    n = min(len(clip), len(bus) - i); bus[i:i + n] += clip[:n] * g
voice = np.zeros((N, 2)); place(voice, load(os.path.join(PUB, D["audio"]["narracao"])), D["audio"]["narracaoEm"])
voice = sosfilt(butter(2, 110, "hp", fs=SR, output="sos"), voice, axis=0); voice = np.tanh(voice * 1.5) / np.tanh(1.5)
tt = np.arange(N) / SR
music = np.zeros((N, 2)); mus = load(os.path.join(PUB, D["audio"]["trilha"])); place(music, mus[: N], 0.0)
env = np.convolve(np.abs(voice).mean(1), np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
music *= (1 - 0.5 * np.clip(env / 0.05, 0, 1))[:, None] * db(-4)
music *= np.clip(tt / 1.0, 0, 1)[:, None] * np.clip((DUR - tt) / 1.0, 0, 1)[:, None]
sfx = np.zeros((N, 2)); S = lambda n: load(os.path.join(PUB, "sao-paulo", "audio", "sfx", n + ".wav"))
place(sfx, S("torcida"), 0.0, db(-2))
# cortes: mesmas proporções de planos usadas em Cenas.tsx
PLANOS = {"ameaca": [1.8, 1.6, 1.6], "fica": [1, 1], "comecou": [1.4, 1.4], "teixeira": [1.5, 1.5], "estados": [2.4, 2.4], "matamata": [2.2, 1.4],
          "numeros": [1.9, 1.9, 2], "primeiro": [1.9, 1.9], "pequenos": [1.4, 1.2], "criciuma": [1.8, 1.8], "santoandre": [2.1, 2.1], "paulista": [2.1, 2.1],
          "semlibertadores": [2, 1.8], "oitavas": [2, 1.9, 1.8], "maiores": [2.6, 1.4, 1.4], "hoje": [3, 3.1], "impacto": [1.9, 2]}
for c in D["cenas"]:
    if c["inicio"] > 0: place(sfx, S("whoosh"), c["inicio"] - 0.25, db(-9))
    p = PLANOS.get(c["id"])
    if p:
        tot = sum(p); acc = 0
        for d in p[:-1]:
            acc += d; place(sfx, S("whoosh"), c["inicio"] + (c["fim"] - c["inicio"]) * acc / tot - 0.25, db(-13))
cena = {c["id"]: c for c in D["cenas"]}
place(sfx, S("carimbo"), cena["ameaca"]["inicio"] + 1.85, db(-3))
place(sfx, S("impacto"), cena["ameaca"]["inicio"] + 1.85, db(-8))
place(sfx, S("contagem"), cena["numeros"]["inicio"] + 0.1, db(-9))
place(sfx, S("placar"), cena["primeiro"]["inicio"] + 0.15, db(-6))
place(sfx, S("placar"), cena["criciuma"]["inicio"] + 0.1, db(-6))
place(sfx, S("placar"), cena["santoandre"]["inicio"] + 0.1, db(-6))
place(sfx, S("torcida"), cena["paulista"]["inicio"], db(-10))
place(sfx, S("pop"), cena["oitavas"]["inicio"] + (cena["oitavas"]["fim"] - cena["oitavas"]["inicio"]) * 2 / 5.7 + 0.5, db(-2))
place(sfx, S("torcida"), cena["maiores"]["inicio"], db(-10))
place(sfx, S("impacto"), cena["impacto"]["inicio"] + 1.3, db(-5))
place(sfx, S("torcida"), cena["impacto"]["inicio"] + 1.4, db(-6))
place(sfx, S("torcida"), cena["cta"]["inicio"], db(-12))
mix = voice * db(-1) + music * db(-14) + sfx * db(-4)
mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix *= 0.93 / max(np.max(np.abs(mix)), 1e-9)
out = os.path.join(PUB, D["audio"]["mix"])
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("mix ->", out)
