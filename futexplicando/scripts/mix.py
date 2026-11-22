"""Monta a trilha final (narração Gemini + trilha CC0 + SFX sintetizados) a partir de src/data/sao-paulo.json.

Uso: python3 scripts/mix.py -> public/sao-paulo/audio/mix-sao-paulo.wav
"""
import json
import os
import subprocess
import wave

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = os.path.join(os.path.dirname(__file__), "..")
PUB = os.path.join(ROOT, "public")
D = json.load(open(os.path.join(ROOT, "src", "data", "sao-paulo.json")))
SR = 48000
DUR = D["duracaoSegundos"]
N = int(DUR * SR)
C = D["cenas"]


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "quiet", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float64) / 32768


def db(x):
    return 10 ** (x / 20)


def place(bus, clip, at, gain=1.0):
    i = int(round(at * SR))
    if i >= len(bus):
        return
    n = min(len(clip), len(bus) - i)
    bus[i:i + n] += clip[:n] * gain


# ---------- narração ----------
narr_src = load(os.path.join(PUB, D["audio"]["narracao"]))
voice = np.zeros((N, 2))
for c in D["audio"]["narracaoCortes"]:
    seg = narr_src[int(c["de"] * SR):int(c["ate"] * SR)].copy()
    f = int(0.01 * SR)
    seg[:f] *= np.linspace(0, 1, f)[:, None]
    seg[-f:] *= np.linspace(1, 0, f)[:, None]
    place(voice, seg, c["em"])
# leve compressão/realce de presença
sos = butter(2, 120, "hp", fs=SR, output="sos")
voice = sosfilt(sos, voice, axis=0)
voice = np.tanh(voice * 1.6) / np.tanh(1.6)

# ---------- trilha ----------
mus_src = load(os.path.join(PUB, D["audio"]["trilha"]))
start = D["audio"]["trilhaEntra"]
OFFSET_TRILHA = 3.0  # pula a introdução mais vazia da faixa
music = np.zeros((N, 2))
seg = mus_src[int(OFFSET_TRILHA * SR):int(OFFSET_TRILHA * SR) + (N - int(start * SR))]
place(music, seg, start)

tt = np.arange(N) / SR
# cena 1935: abafa e abaixa a trilha (passa-baixa + -9 dB), volta na cena da fé
m0, m1 = C["morte"]["inicio"], C["fe"]["inicio"]
dark = np.clip((tt - m0) / 0.4, 0, 1) * np.clip((C["fe"]["remontaEm"] + 2.5 - tt) / 2.5, 0, 1)
muffled = sosfilt(butter(2, 500, "lp", fs=SR, output="sos"), music, axis=0)
music = music * (1 - dark[:, None]) + muffled * db(-6) * dark[:, None]
# corta a trilha um instante antes da quebra do escudo (silêncio dramático) e volta com a remontagem
q = C["morte"]["quebraEm"]
gap = np.clip(np.abs(tt - (q + 0.5)) / 0.6, 0, 1) ** 0.5
gap = np.where((tt > q - 0.15) & (tt < C["fe"]["remontaEm"] + 0.2), np.minimum(gap, 0.15), 1)
music *= gap[:, None]
# fade final
fade_end = np.clip((DUR - tt) / 0.35, 0, 1)
music *= fade_end[:, None]

# ducking pela envelope da voz
env = np.abs(voice).mean(1)
win = int(0.12 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
music *= duck[:, None] * db(-11)

# ---------- SFX ----------
sfx = np.zeros((N, 2))
S = lambda n: load(os.path.join(PUB, "sao-paulo", "audio", "sfx", n + ".wav"))
g = C["gancho"]["moeda"]
place(sfx, S("moeda-girando"), 0.0, db(-4))
place(sfx, S("moeda-quicando"), g["quiques"][0], db(-1))
place(sfx, S("impacto"), C["virada"]["inicio"], db(-2))
place(sfx, S("drop"), C["virada"]["inicio"], db(-6))
n = C["nascimento"]
place(sfx, S("carimbo"), n["dataEm"], db(-4))
place(sfx, S("whoosh"), n["notaEm"] - 0.2, db(-12))
place(sfx, S("pop"), n["paulistanoEm"], db(-8))
place(sfx, S("pop"), n["palmeirasEm"], db(-8))
place(sfx, S("whoosh"), n["fusaoEm"] - 0.5, db(-8))
place(sfx, S("impacto"), n["fusaoEm"], db(-7))
mo = C["morte"]
for fr in mo["frases"]:
    place(sfx, S("carimbo"), fr["em"], db(-10))
place(sfx, S("carimbo"), mo["anoEm"], db(-3))
place(sfx, S("quebra"), mo["quebraEm"], db(-1))
fe = C["fe"]
place(sfx, S("remonta"), fe["remontaEm"], db(-5))
place(sfx, S("carimbo"), fe["dataEm"], db(-4))
place(sfx, S("impacto"), fe["apelidoEm"], db(-6))
mb = C["morumbi"]
place(sfx, S("whoosh"), mb["subtituloEm"] - 0.2, db(-10))
place(sfx, S("impacto"), mb["tituloEm"], db(-7))
for at in D["transicoesMoeda"]:
    place(sfx, S("moeda-transicao"), at - 0.3, db(-6))
mu = C["mundo"]
place(sfx, S("whoosh"), mu["tele"]["biLibertaEm"] - 0.2, db(-10))
place(sfx, S("whoosh"), mu["tele"]["biMundialEm"] - 0.2, db(-10))
for p in mu["placares"]:
    place(sfx, S("placar"), p["em"], db(-6))
place(sfx, S("whoosh"), mu["ano2005"]["em"] - 0.2, db(-8))
for at in mu["tri"]["anosEm"]:
    place(sfx, S("carimbo"), at, db(-5))
st = C["stat"]
place(sfx, S("impacto"), st["numeroEm"], db(-3))
place(sfx, S("whoosh"), st["ceni"]["em"] - 0.2, db(-8))
place(sfx, S("contagem"), st["ceni"]["golsEm"], db(-8))
place(sfx, S("pop"), st["ceni"]["punchEm"], db(-5))
cta = C["cta"]
place(sfx, S("whoosh"), cta["inicio"] - 0.1, db(-9))
place(sfx, S("pop"), cta["acaoEm"], db(-6))
place(sfx, S("moeda-girando"), cta["moedaSobeEm"], db(-5))

mix = voice * db(-1) + music + sfx * db(-3)
# limitador simples
peak = np.max(np.abs(mix))
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix *= 0.93 / max(np.max(np.abs(mix)), 1e-9)

out = os.path.join(PUB, D["audio"]["mix"])
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("mix ->", out, DUR, "s; pico antes do limitador", round(peak, 2))
