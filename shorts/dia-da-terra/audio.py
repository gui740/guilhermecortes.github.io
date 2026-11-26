"""Trilha + efeitos sintetizados + narração, sincronizados com render.py.  -> out/audio.wav"""
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
BPM = 120
BEAT = 60 / BPM
rng = np.random.default_rng(11)


def tt(n):
    return np.arange(n) / SR


def place(buf, x, t0, g=1.0):
    i = int(round(t0 * SR))
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i] * g


def st(y):
    return np.stack([y, y], 1)


def lp(x, fc, o=2):
    b, a = signal.butter(o, min(fc, SR / 2 - 100) / (SR / 2), "low"); return signal.lfilter(b, a, x)


def hp(x, fc, o=2):
    b, a = signal.butter(o, fc / (SR / 2), "high"); return signal.lfilter(b, a, x)


def bp(x, lo, hi, o=2):
    b, a = signal.butter(o, [lo / (SR / 2), hi / (SR / 2)], "band"); return signal.lfilter(b, a, x)


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def saw(f, t, ph=0.0):
    return 2 * ((f * t + ph) % 1) - 1


T_SLOWMO = EV["boom"]          # depois do boom: tudo desacelera
EV["flip"] = EV["loop"]


# ---------------------------------------------------------------- música
CHORDS = [(40, [52, 55, 59, 64]), (36, [48, 52, 55, 60]), (43, [55, 59, 62, 67]), (38, [50, 54, 57, 62])]  # Em C G D
BAR = 4 * BEAT


def music():
    pad = np.zeros(N); pad_lo = np.zeros(N); arp = np.zeros(N); bass = np.zeros(N); dr = np.zeros(N)
    nb = int(DUR / BAR) + 2
    for b in range(nb):
        root, notes = CHORDS[b % 4]
        n = int((BAR + 0.3) * SR)
        tl = tt(n)
        ch = np.zeros(n); lo = np.zeros(n)
        for m in notes:
            for det in (-0.1, 0.0, 0.1):
                ch += saw(mtof(m) * 2 ** (det / 12), tl, rng.random())
                lo += saw(mtof(m - 12) * 2 ** (det / 12), tl, rng.random())   # "fita lenta": oitava abaixo
        e = np.minimum(tl / 0.05, 1) * np.clip((BAR + 0.3 - tl) / 0.3, 0, 1)
        place(pad, ch * e * 0.05, b * BAR)
        place(pad_lo, lo * e * 0.05, b * BAR)
    pad = lp(pad, 1500)
    pad_lo = lp(pad_lo, 600)
    # arpejo e baixo em colcheias (só antes do asteroide)
    k, tc = 0, 0.0
    while tc < DUR:
        root, notes = CHORDS[int(tc // BAR) % 4]
        on = (EV["rw"][1] <= tc < EV["ast"]) or EV["cta"] <= tc < EV["loop"]
        if on:
            m = notes[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
            n = int(0.3 * SR); tl = tt(n)
            x = (np.sin(2 * np.pi * mtof(m) * tl) + 0.3 * saw(mtof(m), tl)) * np.exp(-tl * 12)
            place(arp, x * (0.09 if tc < EV["ast"] else 0.06), tc)
            n = int(BEAT / 2 * SR); tl = tt(n)
            f = mtof(root - 12)
            place(bass, (np.sin(2 * np.pi * f * tl) + 0.2 * np.sin(4 * np.pi * f * tl)) * np.exp(-tl * 5) * 0.3, tc)
        k += 1; tc += BEAT / 2
    # bateria
    K = kick(); Hh = hat()
    for i in range(int(DUR / BEAT) + 1):
        tb = i * BEAT
        if EV["rw"][1] <= tb < EV["ast"] - 0.05:
            place(dr, K, tb, 0.75)
            place(dr, Hh, tb + BEAT / 2, 0.5)
            if tb >= EV["eras"][1]:
                place(dr, Hh, tb + BEAT * 0.25, 0.25); place(dr, Hh, tb + BEAT * 0.75, 0.25)
            if i % 2 == 1:
                place(dr, clap(), tb, 0.6)
    # câmera lenta: batida de coração lenta
    for tc in np.arange(0.0, EV["rw"][0], 1.25):     # gancho: coração lento
        place(dr, kick(0.6), tc, 0.55); place(dr, kick(0.6), tc + 0.28, 0.35)
    tc = EV["slow"] + 0.3
    while tc < EV["loop"] - 0.2:
        place(dr, kick(0.6), tc, 0.55); place(dr, kick(0.6), tc + 0.28, 0.35)
        tc += 1.25
    # mistura por seção
    t = tt(N)
    fast = ((t >= EV["rw"][1]) & (t < T_SLOWMO)).astype(float)
    xf = np.clip((t - T_SLOWMO) / 0.6, 0, 1)
    mus = pad * (fast + (1 - fast) * (1 - xf)) + pad_lo * (1 - fast) * xf * 1.3 + arp + bass + dr
    return st(mus)


def kick(slow=1.0):
    n = int(0.5 * SR / slow); t = tt(n)
    f = (45 + 110 * np.exp(-t * 28 * slow)) * slow
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7 * slow)


def hat():
    n = int(0.05 * SR)
    return hp(rng.standard_normal(n), 7000) * np.exp(-tt(n) * 80) * 0.22


def clap():
    n = int(0.22 * SR)
    x = bp(rng.standard_normal(n), 900, 4000)
    e = np.zeros(n)
    for o in (0, 0.011, 0.022):
        i = int(o * SR); e[i:] += np.exp(-tt(n - i) * 40)
    return x * e * 0.4


# ---------------------------------------------------------------- efeitos
def tick(f=2600, g=1.0, dec=260):
    n = int(0.05 * SR); t = tt(n)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * dec) + hp(rng.standard_normal(n), 3000) * np.exp(-t * 500) * 0.4
    return st(y * g)


def ticks():
    """tique-taque: frequência sobe com a velocidade do relógio; na câmera lenta fica grave e lento"""
    out = np.zeros((N, 2))
    t, k = 0.02, 0
    while t < DUR:
        rw = any(a <= t < b for a, b in (EV["rw"], (EV["loop"], DUR)))
        if t < EV["rw"][0]:
            place(out, tick(900 if k % 2 == 0 else 700, 1.0, 60), t, 0.5)
            t += 0.9
        elif rw:
            place(out, tick(3400 if k % 2 == 0 else 2800, 0.4), t, 0.4)
            t += 1 / 22
        elif t < EV["slow"]:
            v = abs(RV.clock_speed(t))
            rate = 2.0 + 13.0 * min(1.0, math.log10(1 + v) / 4.6)
            place(out, tick(2900 if k % 2 == 0 else 2200, 0.55), t, 0.6)
            t += 1 / rate
        else:
            place(out, tick(900 if k % 2 == 0 else 700, 1.0, 60), t, 0.5)
            t += 0.9
        k += 1
    return out


def whoosh(dur=0.8, peak=0.55, lo=250, hi=3500, reverse=False):
    n = int(dur * SR); u = tt(n) / dur
    x = rng.standard_normal(n); out = np.zeros(n)
    for i in range(0, n, 512):
        c = lo + (hi - lo) * math.exp(-((u[i] - peak) / 0.25) ** 2)
        seg = bp(x[max(0, i - 2048):i + 512], c * 0.6, min(c * 1.6, SR / 2 - 200))
        out[i:i + 512] = seg[-len(out[i:i + 512]):]
    e = np.where(u < peak, (u / peak) ** 2.5, np.exp(-(u - peak) / (1 - peak) * 4))
    y = out * e
    if reverse:
        y = y[::-1]
    pan = np.linspace(-0.6, 0.6, n)
    return np.stack([y * (1 - pan) * 0.5, y * (1 + pan) * 0.5], 1)


def pop_snd(f0=600):
    n = int(0.12 * SR); t = tt(n)
    f = f0 * (1 + 0.8 * np.exp(-t * 60))
    return st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(t / 0.002, 1) * np.exp(-t * 30))


def ding(f=1318.5, g=1.0):
    n = int(1.6 * SR); t = tt(n)
    y = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d) for m, a, d in
            [(1, 1.0, 2.5), (2.0, 0.4, 4), (2.76, 0.25, 6), (5.4, 0.1, 9)])
    return st(y * np.minimum(t / 0.003, 1) * 0.35 * g)


def falling(dur):
    """assobio do asteroide caindo"""
    n = int(dur * SR); t = tt(n); u = t / dur
    f = 2200 * (1 - u) ** 1.5 + 300
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.15 + 0.6 * u ** 1.5)
    y += lp(rng.standard_normal(n), 800) * u ** 2 * 1.2
    return st(y * 0.45)


def boom():
    n = int(3.5 * SR); t = tt(n)
    f = 28 + 75 * np.exp(-t * 5)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.1)
    hit = lp(rng.standard_normal(n), 900) * np.exp(-t * 5)
    crack = hp(rng.standard_normal(n), 2000) * np.exp(-t * 16) * 0.3
    return st(np.tanh((sub * 1.5 + hit + crack) * 1.6) * 0.9)


def slow_drone(dur):
    """grave estendido da câmera lenta: sub que desce de tom + sopro grave"""
    n = int(dur * SR); t = tt(n); u = t / dur
    f = 70 * (1 - 0.45 * np.minimum(u * 2.5, 1))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.7 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.2
    y += lp(rng.standard_normal(n), 220) * 0.5
    env = np.minimum(u / 0.05, 1) * (1 - u) ** 0.6 * (1 + 0.15 * np.sin(2 * np.pi * 0.8 * t))
    return st(y * env * 0.5)


def tape_rewind(dur):
    n = int(dur * SR); t = tt(n); u = t / dur
    f = 900 + 2600 * np.sin(np.pi * u) ** 0.7
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.15
    y = bp(y + rng.standard_normal(n) * 0.4, 600, 6000) * np.sin(np.pi * u) ** 0.5
    y *= 1 + 0.5 * np.sin(2 * np.pi * 31 * t)
    return st(y * 0.5)


def sfx():
    S = np.zeros((N, 2))
    S += ticks()
    for te in EV["eras"]:
        place(S, whoosh(0.9, 0.55), te - 0.5, 0.7)
    place(S, whoosh(1.2, 0.5, lo=120, hi=1200), EV["slow"] - 0.6, 0.9)       # entrada da câmera lenta
    for tp in EV["pops"]:
        place(S, pop_snd(), tp, 0.45)
    place(S, falling(EV["boom"] - EV["ast"]), EV["ast"], 1.0)
    place(S, boom(), EV["boom"], 1.0)
    place(S, slow_drone(EV["card"] - EV["boom"] + 1.0), EV["boom"] + 0.25, 1.0)
    place(S, ding(1318.5), EV["dec"] + 0.25, 0.9)           # revelação: 0,1 segundo
    place(S, ding(1567.98, 1.2), EV["card"] + 0.05, 1.0)    # cartão final
    place(S, ding(1046.5, 0.8), EV["cta"], 0.9)
    for a, b in (EV["rw"], (EV["loop"], DUR)):          # rebobinar: fita voltando + whoosh reverso
        place(S, tape_rewind(b - a), a, 1.0)
        place(S, whoosh(b - a, 0.3, lo=200, hi=4500, reverse=True), a, 1.2)
    place(S, boom(), EV["theia"], 0.6)                    # Theia
    place(S, falling(1.4), EV["theia"] - 1.4, 0.5)
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
    M, S = music(), sfx()
    env = np.abs(V)
    b, a = signal.butter(1, 6 / (SR / 2))
    env = np.clip(signal.filtfilt(b, a, env) / (np.abs(V).max() * 0.12 + 1e-9), 0, 1)
    mix = M * 0.5 * (1 - 0.55 * env)[:, None] + S * 0.75 * (1 - 0.3 * env)[:, None] + V[:, None]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    f = int(0.004 * SR)
    mix[:f] *= np.linspace(0, 1, f)[:, None]; mix[-f:] *= np.linspace(1, 0, f)[:, None]
    out = os.path.join(RV.OUT, "audio.wav")
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("audio ok")


if __name__ == "__main__":
    main()
