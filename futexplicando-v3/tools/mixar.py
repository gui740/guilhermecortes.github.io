"""Mixagem final: narração + trilha (ducking ~10 dB) + efeitos reais nos tempos exatos do vídeo.
Uso: python3 tools/mixar.py historias/lusa2013.json  ->  public/<id>/mix.wav (master -14 LUFS, pico -1,5 dBTP)"""
import json, os, subprocess, sys, unicodedata, wave
import numpy as np

SR, FPS, TRANS = 48000, 30, 10
H = json.load(open(sys.argv[1])); vid = H["id"]
T = json.load(open(f"videos/{vid}/tempos.json"))
B = "biblioteca"

def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float64) / 32768
db = lambda x: 10 ** (x / 20)
rms = lambda x: float(np.sqrt(np.mean(x ** 2)) + 1e-9)

# ---------------- linha do tempo (mesma lógica de src/motor/tempo.ts e Video.tsx)
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); return "".join(c for c in s if c.isalnum() or c == "º")
def quando(pal, chave, base, desde=0.0):
    if chave is None: return base
    if isinstance(chave, (int, float)): return base + chave
    k = norm(chave)
    for cond in (lambda p: p["t"] >= desde - 0.01 and norm(p["w"]) == k, lambda p: norm(p["w"]) == k,
                 lambda p: p["t"] >= desde - 0.01 and norm(p["w"]).startswith(k), lambda p: norm(p["w"]).startswith(k)):
        m = next((p for p in pal if cond(p)), None)
        if m: return m["t"]
    return base
def inicios(pal, planos):
    ini = []
    for i, p in enumerate(planos):
        ini.append(0.0 if i == 0 else max(ini[-1] + 0.3, quando(pal, p.get("de"), ini[-1], ini[-1]) - 0.05))
    return ini

frames = [round(c["dur"] * FPS) for c in T]
ini_cena, acc = [], 0
for f in frames:
    ini_cena.append(acc / FPS); acc += f - TRANS
total = (sum(frames) - TRANS * (len(frames) - 1)) / FPS
N = int((total + 0.3) * SR)

voz = np.zeros((N, 2)); sfx = np.zeros((N, 2)); amb = np.zeros((N, 2))
def place(bus, clip, at, g=1.0, fade=0.0):
    c = clip.copy()
    if fade:
        f = min(int(fade * SR), len(c) // 2); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
    i = int(round(at * SR))
    if i < 0: c = c[-i:]; i = 0
    if i >= len(bus): return
    n = min(len(c), len(bus) - i); bus[i:i + n] += c[:n] * g

S = {k: load(f"{B}/sfx/{k}.wav") for k in ["boom", "whoosh", "impacto", "martelo", "ding", "torcida_festa", "torcida_amb", "chuva"]}
for k in S: S[k] = S[k] / rms(S[k])

# narração
for k, c in enumerate(T):
    place(voz, load(f"videos/{vid}/narracao/cena_{k+1:02d}.wav"), ini_cena[k] + 0.15)
VR = rms(voz[np.abs(voz).sum(1) > 1e-4])

eventos = []  # (tempo, tipo)
silencio = []  # janelas sem música
for k, (cena, tc) in enumerate(zip(H["cenas"], T)):
    pal = tc["palavras"]; ini = inicios(pal, cena["planos"]); base = ini_cena[k]
    if k > 0: eventos.append((base + TRANS / FPS * 0.5 - 0.25, "whoosh"))
    for i, p in enumerate(cena["planos"]):
        fim = ini[i + 1] if i + 1 < len(ini) else tc["dur"]
        if i > 0: eventos.append((base + ini[i] - 0.12, "whoosh_leve"))
        for c in p["camadas"]:
            t0 = quando(pal, c.get("em"), ini[i], ini[i])
            if t0 > fim + 0.01: continue
            g = base + t0; tipo = c["tipo"]
            if tipo == "titulo" and t0 >= ini[i]: eventos.append((g + 0.12, "boom" if k == 0 else "impacto"))
            if tipo == "carimbo": eventos.append((g + 0.12, "impacto"))
            if tipo == "bloco": eventos.append((g + 0.30, "impacto"))
            if tipo == "martelo":
                for j in range(c.get("batidas", 1)): eventos.append((g + j * 0.36 + 0.1, "martelo"))
            if tipo == "personagem" and c.get("entra") == "queda": eventos.append((g + 0.32, "impacto_leve"))
            if tipo in ("placar", "logo", "relogio"): eventos.append((g + 0.25, "ding"))
            if tipo == "confete": eventos.append((g, "festa"))
            if tipo == "chuva": eventos.append((base + ini[i], f"chuva:{fim - ini[i]}"))
            if tipo == "silhueta":
                silencio.append((base + ini[i] - 0.5, base + ini[i])); eventos.append((base + ini[i], "boom"))
        if p["fundo"] in ("estadio", "contraluz"):
            place(amb, S["torcida_amb"][int(5 * SR):int((5 + fim - ini[i]) * SR)], base + ini[i], db(-26) * VR, fade=0.25)
    if cena["id"] == "flamengo": eventos.append((base + 0.05, "scratch"))

for t, tipo in eventos:
    if tipo == "boom": place(sfx, S["boom"], t, db(-6) * VR)
    elif tipo == "whoosh": place(sfx, S["whoosh"], t, db(-10) * VR)
    elif tipo == "whoosh_leve": place(sfx, S["whoosh"], t, db(-17) * VR)
    elif tipo == "impacto": place(sfx, S["impacto"], t, db(-8) * VR)
    elif tipo == "impacto_leve": place(sfx, S["impacto"], t, db(-14) * VR)
    elif tipo == "martelo": place(sfx, S["martelo"], t, db(-5) * VR)
    elif tipo == "ding": place(sfx, S["ding"], t, db(-16) * VR)
    elif tipo == "festa": place(sfx, S["torcida_festa"], t - 0.4, db(-9) * VR, fade=0.3)
    elif tipo.startswith("chuva:"): place(amb, S["chuva"][: int(float(tipo[6:]) * SR)], t, db(-14) * VR, fade=0.5)

# ---------------- trilha
mus = load(f"{B}/musica/hiphop-dark-shot.mp3")
while len(mus) < N: mus = np.concatenate([mus, mus])
music = mus[:N] / rms(mus[: int(60 * SR)])
triste = load(f"{B}/musica/urban-sad-demo.mp3"); triste = triste / rms(triste[: int(60 * SR)])
kd = next(k for k, c in enumerate(H["cenas"]) if c.get("clima") == "chuva")
a, b = int(ini_cena[kd] * SR), int((ini_cena[kd] + T[kd]["dur"]) * SR)
cross = int(0.6 * SR)
env_t = np.zeros(N); env_t[a:b] = 1
env_t = np.convolve(env_t, np.ones(cross) / cross, mode="same")
tri = np.zeros((N, 2)); seg = triste[int(30 * SR): int(30 * SR) + (b - a) + cross * 2]; tri[a - cross: a - cross + len(seg)] = seg[: N - (a - cross)]
music = music * (1 - env_t)[:, None] + tri * env_t[:, None] * 1.1
for s0, s1 in silencio:  # silêncio dramático
    i0, i1 = int(s0 * SR), int(s1 * SR); f = int(0.06 * SR)
    music[i0:i1] *= 0; music[i0 - f:i0] *= np.linspace(1, 0, f)[:, None]
# record scratch com a própria trilha (vinil indo e voltando), no "Detalhe"
ks = next(k for k, c in enumerate(H["cenas"]) if c["id"] == "flamengo"); ts = ini_cena[ks] + 0.02
src = music[int((ts - 0.6) * SR): int(ts * SR)].mean(1)
n = int(0.42 * SR); ph = np.cumsum(np.sin(np.linspace(0, 3 * np.pi, n)) * 2.2 + 0.4); ph = (ph - ph.min()) / (ph.max() - ph.min() + 1e-9) * (len(src) - 2)
scr = np.interp(ph, np.arange(len(src)), src) * np.hanning(n) * 1.6
music[int(ts * SR): int(ts * SR) + n] *= 0.0
place(sfx, np.stack([scr, scr], 1), ts, 1.0)
music[int(ts * SR) + n: int((ts + 0.5) * SR)] *= np.linspace(0, 1, int((ts + 0.5) * SR) - int(ts * SR) - n)[:, None]
# ducking ~10 dB quando há voz
env = np.convolve(np.abs(voz).mean(1), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
duck = 1 - (1 - db(-10)) * np.clip(env / (np.percentile(env[env > 1e-4], 40) + 1e-9), 0, 1)
music = music * VR * db(-4) * duck[:, None]
fi, fo = int(0.3 * SR), int(1.5 * SR)
music[:fi] *= np.linspace(0, 1, fi)[:, None]; music[-fo:] *= np.linspace(1, 0, fo)[:, None]

mix = voz + music + sfx + amb
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
os.makedirs(f"public/{vid}", exist_ok=True)
tmp = f"videos/{vid}/render/mix_bruto.wav"; os.makedirs(os.path.dirname(tmp), exist_ok=True)
w = wave.open(tmp, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix * 0.7, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
# master em duas passagens: mede e depois normaliza linear para -14 LUFS / -1,5 dBTP
med = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(med[med.rindex("{"): med.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", str(SR), f"public/{vid}/mix.wav"], check=True)
print("mix ->", f"public/{vid}/mix.wav", "| total", round(total, 2), "s | eventos", len(eventos))
