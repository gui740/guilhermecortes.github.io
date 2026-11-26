"""Trilha + efeitos sintetizados + narração (60 s exatos). -> out/audio.wav"""
import os, sys, math, subprocess, wave
import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as RV

SR = 44100
DUR = RV.DUR
N = int(round(SR * DUR))
EV = RV.sound_events()
rng = np.random.default_rng(21)


def tt(n):
    return np.arange(n) / SR


def place(buf, x, t0, g=1.0):
    i = int(round(t0 * SR))
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i] * g


def st(y, pan=0.0):
    return np.stack([y * (1 - pan), y * (1 + pan)], 1)


def lp(x, fc, o=2):
    b, a = signal.butter(o, min(fc, SR / 2 - 100) / (SR / 2), "low"); return signal.lfilter(b, a, x)


def hp(x, fc, o=2):
    b, a = signal.butter(o, fc / (SR / 2), "high"); return signal.lfilter(b, a, x)


def bp(x, lo, hi, o=2):
    b, a = signal.butter(o, [lo / (SR / 2), hi / (SR / 2)], "band"); return signal.lfilter(b, a, x)


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def thump(f0=55, dec=14, g=1.0):
    n = int(0.35 * SR); t = tt(n)
    f = f0 * (1 + 0.6 * np.exp(-t * 30))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dec)
    y += lp(rng.standard_normal(n), 180) * np.exp(-t * 30) * 0.4
    return y * g


def heartbeat():
    """lub-dub"""
    n = int(0.6 * SR)
    y = np.zeros(n)
    place(y, thump(52, 13, 1.0), 0.0)
    place(y, thump(64, 18, 0.7), 0.17)
    return st(np.tanh(y * 1.4))


def pad():
    chords = [(45, [57, 60, 64]), (41, [53, 57, 60]), (48, [55, 60, 64]), (43, [55, 59, 62])]
    out = np.zeros(N)
    bar = 4.0
    for b in range(int(DUR / bar) + 1):
        root, notes = chords[b % 4]
        n = int((bar + 0.5) * SR); t = tt(n)
        y = np.zeros(n)
        for m in notes + [root]:
            for det in (-0.08, 0.08):
                f = mtof(m) * 2 ** (det / 12)
                y += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
        e = np.minimum(t / 0.8, 1) * np.clip((bar + 0.5 - t) / 0.8, 0, 1)
        place(out, y * e * 0.03, b * bar)
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * tt(N) / 8)
    return st(lp(out, 1800) * lfo)


def hats():
    out = np.zeros(N)
    n = int(0.04 * SR)
    h = hp(rng.standard_normal(n), 7000) * np.exp(-tt(n) * 90)
    step = 60 / 120 / 2
    t = 6.0
    while t < EV["sofa"]:
        g = 0.05 + 0.12 * min(1, (t - 6) / 40)
        place(out, h, t, g)
        t += step
    return st(out, 0.2)


def bip(f1=1320, f2=1980):
    n = int(0.22 * SR); t = tt(n)
    y = np.where(t < 0.08, np.sin(2 * np.pi * f1 * t), np.sin(2 * np.pi * f2 * t)) * np.exp(-t * 14)
    return st(y * 0.5)


def tick(f=3000, g=1.0):
    n = int(0.03 * SR); t = tt(n)
    return st((np.sin(2 * np.pi * f * t) * np.exp(-t * 300) + hp(rng.standard_normal(n), 4000) * np.exp(-t * 600) * 0.3) * g)


def whoosh(dur=0.5, rev=False):
    n = int(dur * SR); u = tt(n) / dur
    y = bp(rng.standard_normal(n), 400, 5000) * np.sin(np.pi * u) ** 2
    if rev:
        y = y * u ** 2
    return st(y * 0.4)


def crackle():
    n = int(0.6 * SR); t = tt(n)
    y = hp(rng.standard_normal(n), 1500) * np.exp(-t * 6) * (rng.random(n) < 0.15)
    y += lp(rng.standard_normal(n), 300) * np.exp(-t * 4) * 0.8
    return st(y * 0.6)


def breath(dur=1.6):
    n = int(dur * SR); u = tt(n) / dur
    return st(bp(rng.standard_normal(n), 300, 2500) * np.sin(np.pi * u) ** 2 * 0.12)


def riser(dur):
    n = int(dur * SR); t = tt(n); u = t / dur
    f = 200 * 2 ** (u * 3)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 * u ** 1.5 + hp(rng.standard_normal(n), 2000) * u ** 2 * 0.4
    return st(y * 0.6)


def boom():
    n = int(3.0 * SR); t = tt(n)
    f = 30 + 70 * np.exp(-t * 6)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.3)
    y += lp(rng.standard_normal(n), 900) * np.exp(-t * 6) + hp(rng.standard_normal(n), 2000) * np.exp(-t * 18) * 0.3
    return st(np.tanh(y * 2.0) * 0.9)


def ding(f=1567.98, g=1.0):
    n = int(1.4 * SR); t = tt(n)
    y = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 2.5), (2, 0.4, 4), (2.76, 0.25, 6)])
    return st(y * 0.3 * g)


def sfx():
    S = np.zeros((N, 2))
    hb = heartbeat()
    for b in EV["beats"]:
        place(S, hb, b - 0.02, 0.9)
    for c in EV["cards"]:
        place(S, bip(), c, 0.55)
    order = EV["order"]
    for i, k in enumerate(order):        # whoosh quando o cartão vira linha do painel
        a, b = RV.hero_window(k)
        place(S, whoosh(0.45), b - 0.4, 0.6)
    a_bl = EV["S"]["piscadas"] - 0.15
    for b in EV["blinks"]:
        place(S, tick(4200, 0.6), b, 0.6 if b >= a_bl else 0.25)
    for b in EV["breaths"]:
        if EV["S"]["respira"] - 1.5 <= b < EV["boom"]:
            place(S, breath(), b - 0.8, 1.0)
    place(S, crackle(), EV["S"]["raios"], 1.0)
    # ticks rápidos de contagem nos contadores grandes
    for k in ("celulas", "raios", "bebes", "rotacao", "orbita", "sol", "galaxia"):
        a, b = RV.hero_window(k)
        t = a + 0.3
        while t < b - 0.4:
            place(S, tick(2600, 0.25), t, 0.35)
            t += 0.07
    place(S, riser(EV["boom"] - EV["sofa"]), EV["sofa"], 1.0)
    place(S, boom(), EV["boom"], 1.0)
    place(S, ding(), EV["cta"], 1.0)
    # loop: cronômetro girando de volta
    t = EV["loop"]
    while t < DUR - 0.03:
        u = (t - EV["loop"]) / (DUR - EV["loop"])
        place(S, tick(2000 + 3000 * u, 0.6), t, 0.5)
        t += 0.035
    place(S, whoosh(DUR - EV["loop"], rev=True), EV["loop"], 1.4)
    return S


def load_mono(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af",
                          "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x / (np.abs(x).max() + 1e-9) * 0.9


def main():
    V = np.zeros(N)
    for l in RV.P["lines"]:
        place(V, load_mono(l["file"]), l["start"])
    M = pad() + hats()
    S = sfx()
    env = np.abs(V)
    b, a = signal.butter(1, 6 / (SR / 2))
    env = np.clip(signal.filtfilt(b, a, env) / (np.abs(V).max() * 0.12 + 1e-9), 0, 1)
    mix = M * 0.7 * (1 - 0.5 * env)[:, None] + S * 0.7 * (1 - 0.35 * env)[:, None] + V[:, None]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    f = int(0.004 * SR)
    mix[:f] *= np.linspace(0, 1, f)[:, None]; mix[-f:] *= np.linspace(1, 0, f)[:, None]
    with wave.open(os.path.join(RV.OUT, "audio.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("audio ok")


if __name__ == "__main__":
    main()
