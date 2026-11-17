"""Mix final do episódio a partir de timeline.json.

Narração + áudio das falas de arquivo + trilha com ducking + efeitos. Normaliza para -14 LUFS / -1 dBTP (loudnorm 2 passes).
Uso: python3 mixar.py <timeline.json> <narr_dir> <arquivo_dir> <som_dir> <saida.wav>
"""
import json, os, subprocess, sys, wave
import numpy as np

SR = 48000
tl_path, narr_dir, arq_dir, som_dir, out = sys.argv[1:6]
tl = json.load(open(tl_path, encoding="utf8"))
N = int((tl["duracao"] + 1) * SR)


def load(path):
    """Decodifica qualquer áudio para float32 estéreo 48 kHz."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).reshape(-1, 2).astype(np.float64)


def db(x):
    return 10 ** (x / 20)


def put(bus, x, t, g=1.0):
    i = int(round(t * SR))
    if i >= len(bus):
        return
    n = min(len(x), len(bus) - i)
    bus[i:i + n] += x[:n] * g


voz = np.zeros((N, 2)); arq = np.zeros((N, 2)); fx = np.zeros((N, 2))
mus_env = np.full(N, db(-17.0))   # trilha sozinha (respiros)

for tr in tl["trechos"]:
    t0 = tr["start"]
    a, b = int(t0 * SR), int((t0 + tr["dur"]) * SR)
    if tr["tipo"] == "narr":
        put(voz, load(os.path.join(narr_dir, os.path.basename(tr["audio"]))), t0, db(0))
        mus_env[a:b] = db(-27.0)
    elif tr["tipo"] == "arq":
        x = load(os.path.join(arq_dir, f"{tr['id']}.mp4"))
        put(arq, x, t0 + tr.get("pre", 0), db(-1.5))
        mus_env[a:b] = db(-34.0)
# o hook abre seco: só o áudio original, sem trilha
hook = next(t for t in tl["trechos"] if t["id"] == "HOOK")
mus_env[: int((hook["start"] + hook["dur"]) * SR)] = 0.0

# suaviza o ducking (ataque/soltura ~0,35 s)
k = int(0.35 * SR)
ker = np.ones(k) / k
mus_env = np.convolve(mus_env, ker, mode="same")

trilha = load(os.path.join(som_dir, "trilha.wav"))
mus = np.zeros((N, 2)); put(mus, trilha, 0.0)
mus *= mus_env[:, None]

GAIN_FX = {"click": -16, "bip": -22, "geiger": -20, "crt_on": -17, "crt_off": -16, "sweep": -22, "carimbo": -15, "papel": -21,
           "plin": -23, "registradora": -18, "tecla": -20}
cache = {}
for e in tl["fx"]:
    name = e["som"]
    if name not in cache:
        cache[name] = load(os.path.join(som_dir, "fx", f"{name}.wav"))
    fam = name.rsplit("_", 1)[0]
    put(fx, cache[name], e["t"], db(GAIN_FX.get(fam, -20)))

mix = voz + arq + mus + fx
pre = os.path.splitext(out)[0] + "_pre.wav"
pcm = np.clip(mix, -1, 1)
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((pcm * 32767).astype(np.int16).tobytes())

# loudnorm 2 passes
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", pre, "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample={SR}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print("\n".join(l for l in m.splitlines()[-12:] if l.strip()))
