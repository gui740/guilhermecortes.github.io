"""Mixagem do vídeo do Palmeiras: narração Gemini + trilha CC0 (FreePD) + SFX sintetizados.
Uso: python3 scripts/mix-palmeiras.py -> public/palmeiras/audio/mix-palmeiras.wav"""
import json, os, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt

ROOT = os.path.join(os.path.dirname(__file__), "..")
PUB = os.path.join(ROOT, "public")
D = json.load(open(os.path.join(ROOT, "src", "data", "corinthians.json")))
SR = 48000
DUR = D["duracaoSegundos"]; N = int(DUR * SR); C = D["cenas"]


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float64) / 32768


def db(x): return 10 ** (x / 20)


def place(bus, clip, at, gain=1.0):
    i = int(round(at * SR))
    if i >= len(bus): return
    n = min(len(clip), len(bus) - i); bus[i:i + n] += clip[:n] * gain


# narração
voice = np.zeros((N, 2))
src = load(os.path.join(PUB, D["audio"]["narracao"]))
for c in D["audio"]["narracaoCortes"]:
    place(voice, src[int(c["de"] * SR):int(c["ate"] * SR)], c["em"])
voice = sosfilt(butter(2, 120, "hp", fs=SR, output="sos"), voice, axis=0)
voice = np.tanh(voice * 1.6) / np.tanh(1.6)

# trilha: entra com o escudo na virada; abafada e baixa na guerra; volta forte na Arrancada
tt = np.arange(N) / SR
mus = load(os.path.join(PUB, D["audio"]["trilha"]))
start = D["audio"]["trilhaEntra"]; o = int(D["audio"]["trilhaOffset"] * SR)
music = np.zeros((N, 2)); place(music, mus[o:o + N], start)
# fila e ditadura: trilha abafada; volta cheia no gol do Basílio e na Democracia
segs = [(C["fila"]["inicio"], C["fila"]["fimFilaEm"] - 1.5), (C["democracia"]["inicio"], C["democracia"]["tituloEm"])]
dark = np.zeros(N)
for a, b in segs:
    dark = np.maximum(dark, np.clip((tt - a) / 0.4, 0, 1) * np.clip((b - tt) / 0.3, 0, 1))
muff = sosfilt(butter(2, 500, "lp", fs=SR, output="sos"), music, axis=0)
music = music * (1 - dark[:, None]) + muff * db(-6) * dark[:, None]
music *= np.clip((DUR - tt) / 0.35, 0, 1)[:, None]
env = np.convolve(np.abs(voice).mean(1), np.ones(int(0.12 * SR)) / int(0.12 * SR), mode="same")
music *= (1 - 0.55 * np.clip(env / 0.05, 0, 1))[:, None] * db(-10)

# SFX
sfx = np.zeros((N, 2))
S = lambda n: load(os.path.join(PUB, "sao-paulo", "audio", "sfx", n + ".wav"))
g = C["gancho"]
place(sfx, S("lampiao"), g["acendeEm"] - 0.05, db(-3))
place(sfx, S("impacto"), C["virada"]["inicio"], db(-2)); place(sfx, S("drop"), C["virada"]["inicio"], db(-6))
n = C["nascimento"]
place(sfx, S("carimbo"), n["dataEm"], db(-4)); place(sfx, S("whoosh"), n["lugarEm"] - 0.2, db(-10)); place(sfx, S("pop"), n["inglesEm"], db(-7))
place(sfx, S("whoosh"), n["operariosEm"] - 0.2, db(-10)); place(sfx, S("impacto"), n["tituloEm"], db(-6))
f = C["fila"]
place(sfx, S("contagem"), f["contadorEm"], db(-8)); place(sfx, S("whoosh"), f["basilioEm"] - 0.2, db(-9)); place(sfx, S("placar"), f["placarEm"], db(-5)); place(sfx, S("impacto"), f["fimFilaEm"], db(-3))
dm = C["democracia"]
place(sfx, S("carimbo"), dm["ditaduraEm"], db(-5)); place(sfx, S("whoosh"), dm["socratesEm"] - 0.2, db(-9)); place(sfx, S("impacto"), dm["tituloEm"], db(-5)); place(sfx, S("carimbo"), dm["votoEm"], db(-5))
for at in D["transicoesLampiao"]: place(sfx, S("lampiao"), at - 0.3, db(-9)); place(sfx, S("whoosh"), at - 0.3, db(-11))
m = C["mundo"]
place(sfx, S("placar"), m["m2000"]["em"] + 0.3, db(-6)); place(sfx, S("carimbo"), m["queda"]["em"], db(-4)); place(sfx, S("whoosh"), m["volta"]["em"] - 0.2, db(-9))
for p in m["placares"]: place(sfx, S("placar"), p["em"], db(-6))
st = C["stat"]
place(sfx, S("impacto"), st["numeroEm"], db(-3)); place(sfx, S("pop"), st["mundiaisEm"], db(-7)); place(sfx, S("whoosh"), st["torcidaEm"] - 0.2, db(-9)); place(sfx, S("impacto"), st["fielEm"], db(-5))
ct = C["cta"]
place(sfx, S("whoosh"), ct["inicio"] - 0.1, db(-9)); place(sfx, S("pop"), ct["acaoEm"], db(-6)); place(sfx, S("lampiao"), ct["apagaEm"], db(-6))

mix = voice * db(-1) + music + sfx * db(-3)
mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix *= 0.93 / max(np.max(np.abs(mix)), 1e-9)
out = os.path.join(PUB, D["audio"]["mix"])
with wave.open(out, "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((mix * 32767).astype(np.int16).tobytes())
print("mix ->", out)
