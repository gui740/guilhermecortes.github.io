"""Monta a trilha do Reel a partir de src/timings.json.

- Marchinha: composição ORIGINAL feita por código (melodia/harmonia/percussão sintetizadas aqui),
  dedicada ao domínio público (CC0). Passa por um filtro de "disco de 78 rpm".
  Na virada (audio.musicWarpStart → musicWarpEnd) ela freia como fita, fica lenta, grave e distorcida.
- Efeitos: arquivos CC0 / domínio público baixados do Internet Archive (ver creditos.md).

Uso: python3 tools/build_audio.py      → out/audio_mix.wav (+ out/stems/*.wav)
"""
import json, os, subprocess
import numpy as np
from scipy import signal
import scipy.io.wavfile as wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
T = json.load(open(os.path.join(ROOT, "src/timings.json")))
A = T["audio"]; DUR = T["duration"]
N = int(DUR * SR)
rng = np.random.default_rng(7)
RAW = os.path.join(ROOT, "assets/audio/raw")


def load(name):
    p = os.path.join(RAW, name)
    wav = p.rsplit(".", 1)[0] + "_48k.wav"
    if not os.path.exists(wav):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ac", "1", "-ar", str(SR), wav], check=True)
    sr, x = wavfile.read(wav)
    return x.astype(np.float32) / 32768


def seg(x, a, b): return x[int(a * SR):int(b * SR)].copy()
def fade(x, fi=.02, fo=.05):
    n1, n2 = int(fi * SR), int(fo * SR)
    if n1: x[:n1] *= np.linspace(0, 1, n1)
    if n2: x[-n2:] *= np.linspace(1, 0, n2)
    return x
def place(track, x, at, gain=1.0):
    i = int(at * SR); j = min(len(track), i + len(x))
    if j > i: track[i:j] += x[:j - i] * gain
def resample_rate(x, rate):  # muda velocidade (e afinação) junto, como fita
    idx = np.arange(0, len(x) - 1, rate)
    return np.interp(idx, np.arange(len(x)), x).astype(np.float32)
def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"); return signal.sosfilt(sos, x).astype(np.float32)
def lp(x, f, order=2):
    sos = signal.butter(order, f, "lowpass", fs=SR, output="sos"); return signal.sosfilt(sos, x).astype(np.float32)
def hp(x, f, order=2):
    sos = signal.butter(order, f, "highpass", fs=SR, output="sos"); return signal.sosfilt(sos, x).astype(np.float32)
def norm(x, peak=.9):
    m = np.abs(x).max() or 1; return x * (peak / m)


# ---------------------------------------------------------------- marchinha original
BPM = 116; E8 = 60 / BPM / 2          # colcheia
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
C4, D4, E4, F4, G4, A4, B4, C5, D5, E5, B3 = 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 59
# (nota, colcheias)
PA = [(G4, 1), (G4, 1), (A4, 1), (G4, 1), (E4, 2), (C4, 2), (D4, 1), (E4, 1), (F4, 1), (D4, 1), (G4, 4),
      (A4, 1), (A4, 1), (B4, 1), (A4, 1), (F4, 2), (D4, 2), (E4, 1), (F4, 1), (G4, 1), (E4, 1), (C5, 4)]
PB = [(E5, 1), (E5, 1), (D5, 1), (C5, 1), (B4, 2), (G4, 2), (A4, 1), (B4, 1), (C5, 1), (A4, 1), (G4, 4),
      (F4, 1), (G4, 1), (A4, 1), (F4, 1), (E4, 2), (C4, 2), (D4, 1), (E4, 1), (D4, 1), (B3, 1), (C4, 4)]
CA = ["C", "C", "G", "G", "F", "Dm", "G", "C"]
CB = ["C", "G", "F", "C", "F", "C", "G", "C"]
ROOTS = {"C": (48, 55), "G": (43, 50), "F": (41, 48), "Dm": (38, 45)}
SCALE = [0, 2, 4, 5, 7, 9, 11]
def third_below(m):
    pc = (m - 60) % 12; octv = (m - 60) // 12
    i = SCALE.index(pc) if pc in SCALE else 0
    j = i - 2; o = octv
    if j < 0: j += 7; o -= 1
    return 60 + o * 12 + SCALE[j]

def tone(f, dur, kind="brass", amp=.3):
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + .004 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / .15, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    out = np.zeros(n, np.float32)
    if kind == "brass":
        bright = np.clip(t / .05, 0, 1) * np.exp(-t * 2.5) * .7 + .3
        for k in range(1, 14): out += (np.sin(k * ph) / k * np.clip(bright * 12 / k, 0, 1)).astype(np.float32)
        env = np.clip(t / .025, 0, 1) * np.exp(-t * 1.2)
    elif kind == "clar":
        for k in (1, 3, 5, 7, 9): out += (np.sin(k * ph) / k ** 1.3).astype(np.float32)
        env = np.clip(t / .03, 0, 1) * np.exp(-t * .8)
    else:  # tuba
        out = (np.sin(ph) + .45 * np.sin(2 * ph) + .2 * np.sin(3 * ph)).astype(np.float32)
        env = np.clip(t / .015, 0, 1) * np.exp(-t * 6)
    rel = int(min(.04, dur * .3) * SR)
    if rel: env[-rel:] *= np.linspace(1, 0, rel)
    return (out * env * amp).astype(np.float32)

def drum(kind):
    if kind == "snare":
        n = int(.18 * SR); t = np.arange(n) / SR
        x = bp(rng.standard_normal(n).astype(np.float32), 1200, 6000) * np.exp(-t * 28) * .5
        x += np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40) * .35
    elif kind == "surdo":
        n = int(.6 * SR); t = np.arange(n) / SR
        f = 70 * np.exp(-t * 3) + 48
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * .9
    else:  # ganzá
        n = int(.06 * SR); t = np.arange(n) / SR
        x = bp(rng.standard_normal(n).astype(np.float32), 4000, 11000) * np.exp(-t * 60) * .18
    return x.astype(np.float32)

def marchinha(seconds):
    n = int(seconds * SR); out = np.zeros(n + SR * 2, np.float32)
    form = [(PA, CA), (PA, CA), (PB, CB), (PA, CA)] * 3
    t = 0.0
    snare_pat = [1, 0, 1, 1, 0, 1, 1, 0]   # em colcheias, 2 compassos
    for phrase, chords in form:
        if t > seconds: break
        tt = t
        for m, d in phrase:
            dur = d * E8
            place(out, tone(mtof(m), dur * .95, "clar", .22), tt)
            place(out, tone(mtof(m), dur * .95, "brass", .16), tt)
            place(out, tone(mtof(third_below(m)), dur * .95, "brass", .09), tt)
            tt += dur
        for b, ch in enumerate(chords):  # tuba + percussão por compasso (2 tempos)
            bt = t + b * 4 * E8
            r, fth = ROOTS[ch]
            place(out, tone(mtof(r), E8 * 1.6, "tuba", .5), bt)
            place(out, tone(mtof(fth), E8 * 1.6, "tuba", .42), bt + 2 * E8)
            place(out, drum("surdo"), bt + 2 * E8, .9); place(out, drum("surdo"), bt, .35)
            for k in range(4):
                if snare_pat[(b % 2) * 4 + k]: place(out, drum("snare"), bt + k * E8, .55 + .25 * (k == 0))
            for k in range(8): place(out, drum("ganza"), bt + k * E8 / 2, .8 if k % 2 else .5)
        t = tt
    return out[:n]

def gramophone(x):
    x = bp(x, 260, 3800, 2)
    # wow: leve oscilação de velocidade
    t = np.arange(len(x)) / SR
    idx = np.clip(np.arange(len(x)) + 30 * np.sin(2 * np.pi * .55 * t), 0, len(x) - 1)
    x = np.interp(idx, np.arange(len(x)), x).astype(np.float32)
    x = np.tanh(x * 2.2) / np.tanh(2.2)
    crackle = np.zeros(len(x), np.float32)
    pos = rng.integers(0, len(x), int(len(x) / SR * 14)); crackle[pos] = rng.uniform(-.6, .6, len(pos))
    crackle = hp(crackle, 900); hiss = hp(rng.standard_normal(len(x)).astype(np.float32), 3000) * .012
    return (x + crackle * .5 + hiss).astype(np.float32)


# ---------------------------------------------------------------- montagem
music_src = gramophone(norm(marchinha(DUR + 6), .7))
w0, w1 = A["musicWarpStart"], A["musicWarpEnd"]
t = np.arange(N) / SR
rate = np.ones(N, np.float32)
k = np.clip((t - w0) / (w1 - w0), 0, 1)
rate = np.where(t < w0, 1.0, np.where(t < w1, 1 - .68 * (k ** 1.6), .42 + .05 * np.sin(2 * np.pi * .3 * (t - w1)))).astype(np.float32)
phi = np.cumsum(rate) - 1
music = np.interp(phi, np.arange(len(music_src)), music_src).astype(np.float32)
drive = np.where(t < w0, 1.0, 1 + 7 * np.clip((t - w0) / 2.0, 0, 1))
music = (np.tanh(music * drive) / np.tanh(drive)).astype(np.float32)
dark = lp(music, 900, 2)                                       # depois da virada: grave e abafada
mixk = np.clip((t - w0) / (w1 - w0), 0, 1)
music = music * (1 - mixk) + dark * mixk
mgain = np.interp(t, [0, .2, 12.4, 13.0, w0, w1, w1 + 3, 34, 36], [0, 1, 1, .7, .7, .55, .32, .12, 0])
music *= mgain.astype(np.float32)

sfx = np.zeros(N, np.float32)
storm = load("thunder_rain.mp3"); car = load("car.mp3"); door = load("door.mp3"); drone_src = load("drone.mp3")
# chuva (trecho contínuo do arquivo de trovão+chuva, sem o trovão)
r0, r1 = A["rainStart"], A["rainEnd"]
rain = fade(seg(storm, 16, 16 + (r1 - r0) + 1.5), .8, 1.5); place(sfx, hp(rain, 300) * 2.2, r0)
# trovão
place(sfx, fade(seg(storm, 3.6, 9.0), .01, 1.0) * 1.6, A["thunder"] - .6)
# motor: marcha lenta (laço) e arrancada
idle = seg(car, 12.5, 17.5); idle = np.concatenate([idle, idle[::-1], idle])
place(sfx, fade(lp(idle[:int((A["engineAccelerate"] - A["engineStart"]) * SR)], 2500), .6, .3) * .55, A["engineStart"])
place(sfx, fade(seg(car, 1.0, 8.0), .05, 1.5) * .9, A["engineAccelerate"])
# portão de ferro rangendo: rangido real, desacelerado (mais grave e longo) + eco
creak = resample_rate(seg(door, 4.0, 7.2), .55); creak = fade(creak, .05, .4)
creak = creak + np.concatenate([np.zeros(int(.12 * SR), np.float32), creak[:-int(.12 * SR)]]) * .35
place(sfx, creak * 2.4, A["gateCreak"])
# drone sombrio
d0 = A["droneStart"]; drone = fade(seg(drone_src, 30, 30 + DUR - d0 + .5), 2.5, 2.0)
dg = np.interp(np.arange(len(drone)) / SR + d0, [d0, w0, w1, 38, DUR], [.6, .8, 1.3, 1.4, .9]).astype(np.float32)
place(sfx, drone * dg * .6, d0)
# batida do livro, sustos
def boom(dur=1.6, f0=55, amp=.9):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 1.5) + 28) / SR) * np.exp(-tt * 2.6)
    x += lp(rng.standard_normal(n).astype(np.float32), 400) * np.exp(-tt * 9) * .5
    return (x * amp).astype(np.float32)
place(sfx, boom(.9, 90, .7), A["bookThud"])
rev = (hp(rng.standard_normal(int(1.2 * SR)).astype(np.float32), 2500) * np.linspace(0, 1, int(1.2 * SR)) ** 3 * .35).astype(np.float32)
place(sfx, rev, A["stingAt"] - 1.2); place(sfx, boom(2.2, 60, 1.0), A["stingAt"])
place(sfx, rev, A["finalHit"] - 1.2); place(sfx, boom(3.0, 50, 1.1), A["finalHit"])

mix = music * .55 + sfx * .5
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix = norm(mix, .89)                       # ~ -1 dBFS de pico; a narração entra por cima depois
os.makedirs(os.path.join(ROOT, "out/stems"), exist_ok=True)
def save(p, x):
    st = np.stack([x, x], 1); wavfile.write(os.path.join(ROOT, p), SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))
save("out/audio_mix.wav", mix)
save("out/stems/marchinha.wav", norm(music, .89)); save("out/stems/efeitos.wav", norm(sfx, .89))
print("ok → out/audio_mix.wav", round(len(mix) / SR, 2), "s")
