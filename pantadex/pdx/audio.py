# -*- coding: utf-8 -*-
"""Trilha chiptune original + efeitos sintetizados (numpy) + mixagem com a narração."""
import os, math
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from .common import ROOT, FPS

SR = 44100
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def _t(dur): return np.arange(int(dur * SR)) / SR
def adsr(n, a=0.004, d=0.05, s=0.6, r=0.03):
    e = np.full(n, s, np.float32)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); e[:na] = np.linspace(0, 1, na)
    nd = min(nd, max(0, n - na)); e[na:na + nd] = np.linspace(1, s, nd)
    nr = min(nr, n); e[n - nr:] *= np.linspace(1, 0, nr)
    return e
def _phase(f, dur):
    n = int(dur * SR)
    f = np.full(n, f, np.float64) if np.isscalar(f) else np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(f)), f)
    return np.cumsum(f) / SR
def sq(f, dur, duty=0.5, vol=1.0, **kw):
    ph = _phase(f, dur) % 1.0
    return (np.where(ph < duty, 1.0, -1.0) * adsr(len(ph), **kw) * vol).astype(np.float32)
def tri(f, dur, vol=1.0, **kw):
    ph = _phase(f, dur) % 1.0
    w = np.round((2 * np.abs(2 * ph - 1) - 1) * 7.5) / 7.5      # triângulo em degraus (4 bits)
    return (w * adsr(len(ph), **kw) * vol).astype(np.float32)
def noise(dur, rate=8000, vol=1.0, seed=0, **kw):
    n = int(dur * SR); rs = np.random.RandomState(seed)
    k = max(1, int(SR / rate)); v = rs.uniform(-1, 1, n // k + 2)
    return (np.repeat(v, k)[:n] * adsr(n, **kw) * vol).astype(np.float32)
def decay(sig, tau):
    return sig * np.exp(-np.arange(len(sig)) / (tau * SR)).astype(np.float32)

class Bus:
    def __init__(s, dur): s.b = np.zeros(int(dur * SR) + SR, np.float32)
    def put(s, t, sig):
        i = int(t * SR)
        if i < 0 or i >= len(s.b): return
        sig = sig[: len(s.b) - i]; s.b[i:i + len(sig)] += sig

# ------------------------------------------------------------------ música
MEL = [[66, 69, 71, 72, 71, 69, 66, 69], [74, 0, 72, 71, 69, 0, 66, 0], [64, 67, 72, 76, 74, 72, 67, 64], [66, 69, 74, 72, 69, 0, 74, 0],
       [78, 76, 74, 72, 74, 0, 69, 0], [71, 72, 71, 69, 66, 0, 62, 0], [64, 67, 69, 72, 71, 69, 67, 64], [62, 66, 69, 74, 0, 0, 0, 0]]
ROOTS = [38, 38, 36, 38, 38, 43, 36, 38]

def world_theme(dur, start_bar=0, vol=1.0):
    """baião em Ré mixolídio, 132 bpm"""
    beat = 60 / 132; e8 = beat / 2; bar = beat * 4
    out = Bus(dur + 1)
    nb = int(dur / bar) + 2
    for bi in range(nb):
        b = (start_bar + bi) % 8; t0 = bi * bar
        row = MEL[b]; i = 0
        while i < 8:
            if row[i]:
                L = 1
                while i + L < 8 and row[i + L] == 0: L += 1
                out.put(t0 + i * e8, sq(hz(row[i]), L * e8 * 0.92, 0.25, 0.20, d=0.08, s=0.55))
                out.put(t0 + i * e8 + 0.012, sq(hz(row[i]) * 1.004, L * e8 * 0.9, 0.125, 0.06))
                i += L
            else: i += 1
        r = ROOTS[b]
        for st, L, n in [(0, 1.5, r), (1.5, 1.5, r), (3, 1, r + 7)]:
            out.put(t0 + st * beat, tri(hz(n), L * beat * 0.9, 0.42))
        for st in (0.5, 1.0, 2.0, 2.5, 3.5):      # acordes no contratempo
            for n in (r + 24 + 4 if b not in () else 0, r + 24 + 7):
                out.put(t0 + st * beat, sq(hz(n), 0.07, 0.5, 0.045, r=0.02))
        for st in (0, 1.5):                        # zabumba
            out.put(t0 + st * beat, decay(tri(np.linspace(150, 45, 50), 0.14, 0.7), 0.05))
        out.put(t0 + 3 * beat, noise(0.05, 3000, 0.16, seed=bi))
        for k in range(8):                         # triângulo
            out.put(t0 + k * e8, decay(noise(0.04, 22000, 0.07 if k % 2 == 0 else 0.13, seed=k), 0.012))
    return out.b[: int(dur * SR)] * vol

def ficha_theme(dur):
    beat = 60 / 96; e8 = beat / 2; bar = beat * 4
    out = Bus(dur + 1)
    prog = [50, 48, 43, 50]
    lead = [[78, 81], [79, 76], [74, 71], [69, 74]]
    for bi in range(int(dur / bar) + 2):
        r = prog[bi % 4]; t0 = bi * bar
        for k, o in enumerate([12, 19, 24, 28, 24, 19, 24, 19]):
            out.put(t0 + k * e8, decay(sq(hz(r + o), e8 * 0.95, 0.125, 0.11), 0.22))
        out.put(t0, tri(hz(r - 12), bar * 0.96, 0.30))
        for k, n in enumerate(lead[bi % 4]):
            out.put(t0 + k * 2 * beat, sq(hz(n), beat * 1.8, 0.5, 0.05, a=0.03, r=0.2))
    return out.b[: int(dur * SR)]

def fade(x, fin=0.02, fout=0.08):
    x = x.copy(); a = int(fin * SR); b = int(fout * SR)
    x[:a] *= np.linspace(0, 1, a); x[-b:] *= np.linspace(1, 0, b); return x

# ------------------------------------------------------------------ efeitos
def sfx(name, arg):
    if name == "click":
        return np.concatenate([noise(0.012, 9000, 0.35), decay(tri(110, 0.05, 0.5), 0.015)])
    if name == "blip":
        return sq(1320, 0.022, 0.25, 0.07, a=0.001, r=0.01)
    if name == "row":
        return sq(hz(81 + (arg % 4) * 2), 0.04, 0.125, 0.10)
    if name == "tick":
        return sq(hz(72 + arg), 0.045, 0.25, 0.10)
    if name == "power":
        return np.concatenate([sq(np.linspace(110, 880, 20), 0.28, 0.5, 0.18), sq(1760, 0.08, 0.25, 0.14)])
    if name == "logo":
        b = Bus(2.2)
        seq = [62, 66, 69, 74, 66, 69, 74, 78, 69, 74, 78, 81, 74, 78, 81, 86]
        for k, n in enumerate(seq):
            b.put(k * 0.115, decay(sq(hz(n), 0.16, 0.25, 0.20), 0.09)); b.put(k * 0.115, tri(hz(n - 24), 0.1, 0.18))
        return b.b[: int(2.0 * SR)]
    if name == "chord":
        b = Bus(1.6)
        for k, n in enumerate([62, 69, 74, 78, 81, 86]):
            b.put(k * 0.03, decay(sq(hz(n), 1.2, 0.25, 0.13), 0.4))
        b.put(0, decay(tri(hz(38), 1.0, 0.45), 0.4)); b.put(0, decay(noise(0.2, 16000, 0.12), 0.05))
        return b.b[: int(1.4 * SR)]
    if name == "confirm":
        return np.concatenate([sq(hz(81), 0.07, 0.25, 0.16), sq(hz(86), 0.16, 0.25, 0.16)])
    if name == "excl":
        return np.concatenate([sq(hz(88), 0.06, 0.5, 0.2), sq(hz(93), 0.06, 0.5, 0.2), sq(hz(100), 0.22, 0.25, 0.2)])
    if name == "flash":
        b = Bus(0.9)
        for k in range(4): b.put(k * 0.045, sq(np.linspace(1800, 300, 10), 0.04, 0.5, 0.16))
        b.put(0.18, noise(0.55, np.linspace(1, 1, 1)[0] * 6000, 0.16, a=0.2, r=0.3))
        b.put(0.18, sq(np.linspace(200, 1400, 30), 0.5, 0.125, 0.10, a=0.1, r=0.1))
        return b.b[: int(0.8 * SR)]
    if name == "scan":
        b = Bus(arg + 0.3); t = 0.0; k = 0
        while t < arg * 0.9:
            p = t / arg
            b.put(t, decay(sq(hz(76 + int(p * 12)), 0.09, 0.5, 0.15), 0.04)); t += 0.26 - 0.14 * p; k += 1
        n = int(arg * SR); trem = 0.6 + 0.4 * np.sin(2 * np.pi * 9 * np.arange(n) / SR)
        b.b[:n] += tri(np.linspace(55, 82, 40), arg, 0.22, a=0.1, r=0.1) * trem
        return b.b[: int((arg + 0.1) * SR)]
    if name == "ident":
        return np.concatenate([sq(hz(79), 0.07, 0.25, 0.18), sq(hz(83), 0.07, 0.25, 0.18), sq(hz(86), 0.07, 0.25, 0.18), sq(hz(91), 0.25, 0.25, 0.18)])
    if name == "reveal":
        return decay(noise(0.3, 12000, 0.22), 0.08)
    if name == "cry":
        if arg == "onca":      # rosnado grave
            n = int(0.75 * SR); tt = np.arange(n) / SR
            g = sq(np.linspace(105, 62, 60), 0.75, 0.3, 0.42, a=0.05, r=0.3) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 27 * tt)))
            return g + noise(0.75, 1400, 0.16, a=0.05, r=0.3)
        if arg == "tuiuiu":    # bater de bico
            b = Bus(0.9); t = 0.0
            for k in range(11):
                b.put(t, decay(noise(0.03, 5000, 0.4, seed=k), 0.008)); b.put(t, decay(sq(900 + 40 * (k % 2), 0.03, 0.5, 0.15), 0.01)); t += 0.075 - k * 0.003
            return b.b[: int(0.85 * SR)]
        b = Bus(0.7)           # capivara: assobio curto
        for k in range(2):
            b.put(k * 0.2, sq(np.array([1300, 2000, 1800, 1500.0]), 0.15, 0.125, 0.2, a=0.01, r=0.05))
        b.put(0.4, sq(np.array([1500, 2300.0]), 0.1, 0.125, 0.2))
        return b.b[: int(0.6 * SR)]
    if name == "stamp":
        return decay(tri(np.linspace(140, 50, 30), 0.25, 0.9), 0.07) + np.pad(decay(noise(0.08, 4000, 0.4), 0.02), (0, int(0.17 * SR)))[: int(0.25 * SR)]
    if name == "save":
        b = Bus(1.3)
        for k in range(10): b.put(k * 0.11, sq(hz(72 + (k % 5) * 2), 0.05, 0.125, 0.10))
        return b.b[: int(1.2 * SR)]
    if name == "saved":
        return np.concatenate([sq(hz(n), 0.09, 0.25, 0.18) for n in (74, 78, 81)] + [sq(hz(86), 0.4, 0.25, 0.18, r=0.25)])
    if name == "off":
        return np.concatenate([sq(np.linspace(900, 60, 40), 0.4, 0.5, 0.2, r=0.2), noise(0.06, 2000, 0.12)])
    return np.zeros(1, np.float32)

def build(show, path):
    dur = show.total
    mus, fx, nar = Bus(dur), Bus(dur), Bus(dur)
    for kind, t0, t1 in show.music:
        L = t1 - t0
        if kind == "world": m = world_theme(L)
        elif kind == "end": m = world_theme(L, start_bar=4)
        else: m = ficha_theme(L) * 1.0
        mus.put(t0, fade(m))
    for t, name, arg in show.sfx:
        fx.put(t, sfx(name, arg))
    for key, t in show.narr:
        a, sr = sf.read(os.path.join(ROOT, "assets", "narration", key + ".wav"), dtype="float32")
        nar.put(t, resample_poly(a, SR, sr).astype(np.float32))
    n = int(dur * SR)
    # envelope da narração (ducking + vibração do alto-falante)
    win = int(0.03 * SR)
    env = np.sqrt(np.convolve(nar.b ** 2, np.ones(win) / win, "same"))
    rel = int(0.35 * SR); sm = np.convolve((env > 0.01).astype(np.float32), np.ones(rel) / rel, "same")
    duck = 1 - 0.62 * np.clip(sm * 1.6, 0, 1)
    mix = nar.b * 1.0 + mus.b * 0.55 * duck + fx.b * 0.55 * (1 - 0.3 * np.clip(sm * 1.6, 0, 1))
    mix = np.tanh(mix[:n] * 1.15) * 0.92
    mix[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    sf.write(path, np.stack([mix, mix], 1), SR, subtype="PCM_16")
    nf = int(dur * FPS) + 2
    spk = np.array([env[int(i * SR / FPS): int((i + 1) * SR / FPS)].max() if int(i * SR / FPS) < len(env) else 0 for i in range(nf)])
    return np.clip(spk / 0.25, 0, 1)
