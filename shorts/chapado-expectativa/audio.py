"""Trilha (trap 100 bpm) + efeitos + narração, sincronizados com render.py. -> out/audio.wav"""
import os, sys, math, subprocess, wave
import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as RV

SR = 44100
DUR = RV.DUR
N = int(round(DUR * SR))
EV = RV.sound_events()
rng = np.random.default_rng(9)


def tt(n): return np.arange(n) / SR


def place(buf, x, t0, g=1.0):
    i = int(round(t0 * SR))
    if i < 0: x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[: j - i] * g


def st(y, pan=0.0): return np.stack([y * (1 - pan), y * (1 + pan)], 1)
def lp(x, fc, o=2): b, a = signal.butter(o, min(fc, SR / 2 - 100) / (SR / 2), "low"); return signal.lfilter(b, a, x)
def hp(x, fc, o=2): b, a = signal.butter(o, fc / (SR / 2), "high"); return signal.lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = signal.butter(o, [lo / (SR / 2), hi / (SR / 2)], "band"); return signal.lfilter(b, a, x)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)


BPM = 100
BEAT = 60 / BPM
CHORDS = [(45, [57, 60, 64]), (41, [53, 57, 60]), (48, [55, 60, 64]), (43, [55, 59, 62])]


def kick():
    n = int(0.45 * SR); t = tt(n)
    return np.sin(2 * np.pi * np.cumsum(48 + 120 * np.exp(-t * 30)) / SR) * np.exp(-t * 6)


def k808(f, dur):
    n = int(dur * SR); t = tt(n)
    y = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.5 * np.exp(-t * 25))) / SR) * np.exp(-t * 1.8)
    return np.tanh(y * 2) * 0.6


def clap():
    n = int(0.25 * SR); x = bp(rng.standard_normal(n), 900, 5000); e = np.zeros(n)
    for o in (0, 0.01, 0.02):
        i = int(o * SR); e[i:] += np.exp(-tt(n - i) * 30)
    return x * e * 0.45


def hat(g=1.0):
    n = int(0.04 * SR); return hp(rng.standard_normal(n), 8000) * np.exp(-tt(n) * 90) * 0.2 * g


def pluck(f, dur=0.35):
    n = int(dur * SR); t = tt(n)
    y = sum(np.sign(np.sin(2 * np.pi * f * d * t)) for d in (1, 1.005)) * 0.5
    return lp(y, 3000) * np.exp(-t * 9)


def music():
    m = np.zeros(N)
    bar = 4 * BEAT
    pah = EV["pah"]
    quiet = lambda t: (EV["marca"] - 0.05 <= t < EV["marca"] + 0.1) or (pah - 0.7 <= t < pah)
    for b in range(int(DUR / bar) + 1):
        root, notes = CHORDS[b % 4]
        for i in range(16):                     # semicolcheias
            t = b * bar + i * BEAT / 4
            if t >= DUR or quiet(t):
                continue
            if i in (0, 7, 10):
                place(m, kick(), t, 0.9)
            if i in (0, 10):
                place(m, k808(mtof(root - 12), BEAT * 1.4), t, 0.8)
            if i in (4, 12):
                place(m, clap(), t, 0.8)
            roll = (b % 2 == 1 and i >= 12)
            place(m, hat(1.0 if i % 2 == 0 else 0.6), t)
            if roll:
                place(m, hat(0.7), t + BEAT / 8)
            if i in (0, 3, 6, 8, 11, 14):
                place(m, pluck(mtof(notes[[0, 1, 2, 1, 2, 0][[0, 3, 6, 8, 11, 14].index(i)]] + 12)), t, 0.12)
    return st(m)


def whoosh(dur=0.35):
    n = int(dur * SR); u = tt(n) / dur
    y = bp(rng.standard_normal(n), 500, 6000) * np.sin(np.pi * u) ** 2
    return np.stack([y * (1.2 - u), y * (0.2 + u)], 1) * 0.5


def hit():
    n = int(0.5 * SR); t = tt(n)
    y = np.sin(2 * np.pi * np.cumsum(60 + 120 * np.exp(-t * 20)) / SR) * np.exp(-t * 8) + bp(rng.standard_normal(n), 200, 3000) * np.exp(-t * 25) * 0.6
    return st(np.tanh(y * 1.5) * 0.8)


def boom():
    n = int(2.4 * SR); t = tt(n)
    y = np.sin(2 * np.pi * np.cumsum(30 + 80 * np.exp(-t * 5)) / SR) * np.exp(-t * 1.5) + lp(rng.standard_normal(n), 900) * np.exp(-t * 5)
    return st(np.tanh(y * 2) * 0.9)


def scratch():
    n = int(0.45 * SR); t = tt(n)
    y = bp(rng.standard_normal(n), 300, 3500) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 7 * t)))
    return st(y * np.exp(-t * 3) * 0.6)


def boing():
    n = int(0.6 * SR); t = tt(n)
    f = 180 + 260 * np.exp(-t * 6) * (1 + 0.5 * np.sin(2 * np.pi * 14 * t))
    return st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.6)


def ding(f=1568, g=1.0):
    n = int(1.3 * SR); t = tt(n)
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * d) for k, a, d in ((1, 1, 2.5), (2, .4, 4), (2.76, .25, 6)))
    return st(y * 0.3 * g)


def register():
    n = int(0.8 * SR); y = np.zeros(n)
    for o in (0, 0.06, 0.12):
        place(y, bp(rng.standard_normal(int(0.05 * SR)), 2000, 7000) * np.exp(-tt(int(0.05 * SR)) * 60) * 0.6, o)
    place(y, ding(2093)[:, 0] * 2, 0.18)
    return st(y)


def tick(f=3000, g=0.5):
    n = int(0.03 * SR); t = tt(n); return st(np.sin(2 * np.pi * f * t) * np.exp(-t * 250) * g)


def rewind(dur=1.5):
    n = int(dur * SR); t = tt(n)
    f = 1500 + 1500 * np.sin(np.pi * t / dur)
    y = bp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.2 + rng.standard_normal(n) * 0.3, 600, 6000) * np.sin(np.pi * t / dur)
    return st(y * 0.4)


def heartbeat():
    n = int(0.5 * SR); y = np.zeros(n)
    for off, f, g in ((0, 52, 1.0), (0.16, 64, 0.7)):
        m = int(0.3 * SR); tl = tt(m)
        place(y, np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-tl * 30))) / SR) * np.exp(-tl * 14) * g, off)
    return st(np.tanh(y * 1.3))


def riser(dur):
    n = int(dur * SR); t = tt(n); u = t / dur
    return st((hp(rng.standard_normal(n), 2000) * u ** 2 * 0.5 + np.sin(2 * np.pi * np.cumsum(200 * 2 ** (u * 3)) / SR) * u ** 1.5 * 0.3) * 0.6)


def sfx():
    S = np.zeros((N, 2))
    for t0, flash in EV["cuts"][1:]:
        place(S, whoosh(0.35), t0 - 0.18, 0.8)
        if flash:
            place(S, hit(), t0, 0.5)
    place(S, scratch(), EV["nao"] - 0.5, 0.9)
    place(S, hit(), EV["nao"], 1.0)
    place(S, riser(0.9), EV["marca"] - 0.9, 0.8)
    place(S, boom(), EV["marca"], 0.5)
    place(S, boing(), EV["tio"], 1.0)
    place(S, hit(), EV["mente"], 0.8)
    place(S, boom(), EV["pah"], 1.0)
    place(S, rewind(1.6), EV["S"]["pah"] + 5.2, 0.8)
    place(S, ding(), EV["recorde"], 1.0)
    place(S, hit(), EV["tenta"], 0.8)
    place(S, register(), EV["boleto"] + 0.05, 1.0)
    a, b = EV["heart"]
    t = a
    while t < b - 0.2:
        place(S, heartbeat(), t, 0.7); t += 0.75
    place(S, ding(1318), EV["cta"], 0.9)
    # ticks dos contadores
    for a, b in ((0.3, EV["S"]["hook"] + 2.2), (EV["S"]["bebes"] + 3.0, EV["S"]["bebes"] + 4.2), (EV["S"]["jeanne"] + 1.0, EV["S"]["jeanne"] + 2.0)):
        t = a
        while t < b:
            place(S, tick(), t, 0.5); t += 0.06
    return S


def load_mono(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x / (np.abs(x).max() + 1e-9) * 0.9


def main():
    V = np.zeros(N)
    for l in RV.P["lines"]:
        place(V, load_mono(l["file"]), l["start"])
    M, S = music(), sfx()
    env = np.abs(V)
    b, a = signal.butter(1, 6 / (SR / 2))
    env = np.clip(signal.filtfilt(b, a, env) / (np.abs(V).max() * 0.12 + 1e-9), 0, 1)
    mix = M * 0.45 * (1 - 0.5 * env)[:, None] + S * 0.7 * (1 - 0.3 * env)[:, None] + V[:, None]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    with wave.open(os.path.join(RV.OUT, "audio.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("audio ok")


if __name__ == "__main__":
    main()
