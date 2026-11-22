"""Mixagem do vídeo do Palmeiras: narração Gemini + trilha CC0 (FreePD) + SFX sintetizados.
Uso: python3 scripts/mix-palmeiras.py -> public/palmeiras/audio/mix-palmeiras.wav"""
import json, os, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt

ROOT = os.path.join(os.path.dirname(__file__), "..")
PUB = os.path.join(ROOT, "public")
D = json.load(open(os.path.join(ROOT, "src", "data", "palmeiras.json")))
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
g0, g1 = C["guerra"]["inicio"], C["guerra"]["fim"]
dark = np.clip((tt - g0) / 0.4, 0, 1) * np.clip((g1 - tt) / 0.3, 0, 1)
muff = sosfilt(butter(2, 450, "lp", fs=SR, output="sos"), music, axis=0)
music = music * (1 - dark[:, None]) + muff * db(-7) * dark[:, None]
music *= np.clip((DUR - tt) / 0.35, 0, 1)[:, None]
env = np.convolve(np.abs(voice).mean(1), np.ones(int(0.12 * SR)) / int(0.12 * SR), mode="same")
music *= (1 - 0.55 * np.clip(env / 0.05, 0, 1))[:, None] * db(-10)

# SFX
sfx = np.zeros((N, 2))
S = lambda n: load(os.path.join(PUB, "sao-paulo", "audio", "sfx", n + ".wav"))
g = C["gancho"]
place(sfx, S("letreiro"), g["trocaEm"], db(-3))
place(sfx, S("carimbo"), g["carimboEm"], db(-2))
place(sfx, S("impacto"), C["virada"]["inicio"], db(-2)); place(sfx, S("drop"), C["virada"]["inicio"], db(-6))
n = C["nascimento"]
place(sfx, S("carimbo"), n["dataEm"], db(-4)); place(sfx, S("whoosh"), n["notaEm"] - 0.2, db(-10)); place(sfx, S("impacto"), n["nomeEm"], db(-7))
w = C["guerra"]
place(sfx, S("carimbo"), w["anoEm"], db(-3))
for f in w["frases"]: place(sfx, S("carimbo"), f["em"], db(-8))
place(sfx, S("letreiro"), w["trocaMeioEm"], db(-4)); place(sfx, S("letreiro"), w["trocaFinalEm"], db(-4)); place(sfx, S("impacto"), w["trocaFinalEm"] + 0.9, db(-8))
for at in D["transicoesLetreiro"]: place(sfx, S("letreiro"), at - 0.35, db(-9)); place(sfx, S("whoosh"), at - 0.3, db(-9))
a = C["arrancada"]
place(sfx, S("placar"), a["placarEm"], db(-6)); place(sfx, S("whoosh"), a["bandeiraEm"] - 0.2, db(-9)); place(sfx, S("impacto"), a["tituloEm"], db(-4))
p = C["porco"]
place(sfx, S("carimbo"), p["ano1Em"], db(-4)); place(sfx, S("pop"), p["insultoEm"], db(-4)); place(sfx, S("carimbo"), p["ano2Em"], db(-4)); place(sfx, S("impacto"), p["viradaEm"], db(-8))
gl = C["glorias"]
for k in ["academia", "liberta99", "quedas", "abel"]: place(sfx, S("whoosh"), gl[k]["em"] - 0.2, db(-9))
place(sfx, S("placar"), gl["abel"]["biEm"], db(-6))
st = C["stat"]
place(sfx, S("impacto"), st["numeroEm"], db(-3)); place(sfx, S("whoosh"), st["abel"]["em"] - 0.2, db(-9))
ct = C["cta"]
place(sfx, S("whoosh"), ct["inicio"] - 0.1, db(-9)); place(sfx, S("pop"), ct["acaoEm"], db(-6)); place(sfx, S("letreiro"), ct["letreiroVoltaEm"], db(-4))

mix = voice * db(-1) + music + sfx * db(-3)
mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix *= 0.93 / max(np.max(np.abs(mix)), 1e-9)
out = os.path.join(PUB, D["audio"]["mix"])
with wave.open(out, "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((mix * 32767).astype(np.int16).tobytes())
print("mix ->", out)
