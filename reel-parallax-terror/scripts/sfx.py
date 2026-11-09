#!/usr/bin/env python3
"""Sintetiza a trilha (drone sombrio, sem vocal) e os efeitos sonoros do reel.
Tudo gerado proceduralmente (numpy/scipy) => livre de direitos.
Saídas: assets/trilha/drone.wav, assets/sfx/{papel,fita,caneta,rasgo,queda,whoosh,batida}.wav"""
import numpy as np, pathlib, wave
from scipy import signal
ROOT = pathlib.Path(__file__).resolve().parent.parent
SR = 44100
rng = np.random.default_rng(13)

def salvar(path, x, stereo=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    if x.ndim == 1 and stereo: x = np.stack([x, x], 1)
    if x.ndim == 1: x = x[:, None]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    print("ok", path.relative_to(ROOT))

def bp(x, lo, hi, o=4):
    return signal.sosfilt(signal.butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def lp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, "high", fs=SR, output="sos"), x)
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-np.maximum(t - a, 0) / d)

# ---------- trilha: drone em Ré grave com batimento, ruído de vento e pulso lento ----------
def drone(seg=90):
    n = seg * SR; t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for f, amp, det in [(36.7, 1, .11), (55.0, .55, .07), (73.4, .35, .13), (77.8, .12, .05), (110, .10, .2)]:  # D1, A1, D2, Eb2 (dissonância), A2
        for ch, s in ((0, -1), (1, 1)):
            lfo = 1 + .35 * np.sin(2 * np.pi * (.03 + det * .1) * t + ch)
            out[:, ch] += amp * lfo * np.sin(2 * np.pi * (f + s * det) * t + .3 * np.sin(2 * np.pi * .05 * t))
    vento = np.stack([bp(rng.standard_normal(n), 180, 900, 2), bp(rng.standard_normal(n), 200, 1000, 2)], 1)
    vento *= (0.5 + 0.5 * np.sin(2 * np.pi * .021 * t))[:, None] ** 2
    out += .35 * vento / np.abs(vento).max()
    # pulso de coração bem distante a cada ~1.6s
    k = np.zeros(n)
    for s0 in np.arange(2, seg, 1.62):
        for dd in (0, .28):
            i = int((s0 + dd) * SR); m = min(int(.25 * SR), n - i)
            if m > 0: k[i:i + m] += np.sin(2 * np.pi * 48 * np.arange(m) / SR) * env(m, .005, .07) * (1 if dd == 0 else .6)
    out += .4 * k[:, None]
    out = lp(out.T, 2500).T
    fade = np.minimum(np.minimum(t / 3, 1), np.minimum((seg - t) / 4, 1))
    return out * fade[:, None]

# ---------- efeitos ----------
def papel():          # papel caindo/assentando + leve amassado
    n = int(.6 * SR); x = np.zeros(n)
    for _ in range(40):
        i = rng.integers(0, int(.35 * SR)); m = rng.integers(200, 1600)
        x[i:i + m] += rng.standard_normal(m) * env(m, .001, .006) * rng.uniform(.2, 1)
    x = bp(x, 1200, 9000) + .5 * lp(rng.standard_normal(n) * env(n, .01, .05), 400)
    return x
def fita():           # fita adesiva sendo puxada: estalos rápidos crescentes
    n = int(.55 * SR); t = np.arange(n) / SR; x = np.zeros(n)
    rate = 300 + 900 * t / t[-1]
    pos = np.cumsum(rate / SR); idx = np.where(np.diff(np.floor(pos)) > 0)[0]
    for i in idx:
        m = min(120, n - i); x[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / 25)
    x = bp(x, 1500, 12000) * np.minimum(t / .05, 1) * np.minimum((t[-1] - t) / .05, 1)
    return x
def caneta():         # risco de caneta/marcador no papel
    n = int(.5 * SR); t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 2500, 7000) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 9 * t)))
    return x * np.minimum(t / .03, 1) * np.minimum((t[-1] - t) / .06, 1)
def rasgo():          # papel rasgando de cima a baixo (~0.9s)
    n = int(1.0 * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for _ in range(900):
        i = rng.integers(0, n - 400); m = rng.integers(60, 400)
        x[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 4)) * rng.uniform(.3, 1)
    x = bp(x, 700, 11000) + .3 * bp(rng.standard_normal(n), 300, 1500)
    return x * np.minimum(t / .04, 1) * np.minimum((t[-1] - t) / .2, 1) * (0.6 + .4 * np.sin(2 * np.pi * 3 * t) ** 2)
def queda():          # polaroide batendo na mesa
    n = int(.4 * SR); t = np.arange(n) / SR
    return lp(rng.standard_normal(n), 900) * env(n, .001, .04) + .6 * np.sin(2 * np.pi * 95 * t) * env(n, .001, .05) + .2 * papel()[:n]
def whoosh():         # câmera correndo seguindo a seta
    n = int(.9 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); f = 300 + 2500 * np.sin(np.pi * t / t[-1]) ** 2
    y = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        fc = f[i]; y[i:i + blk] = bp(x[i:i + blk + 0][:blk], max(fc * .5, 80), min(fc * 1.5, 18000), 2)[:len(y[i:i + blk])]
    return lp(y, 6000) * np.sin(np.pi * t / t[-1]) ** 2
def batida():         # impacto grave para o título / CTA
    n = int(1.6 * SR); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 6) + 38
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, .45) + .3 * lp(rng.standard_normal(n), 300) * env(n, .001, .1)

if __name__ == "__main__":
    salvar(ROOT / "assets" / "trilha" / "drone.wav", drone())
    for nome, fn in [("papel", papel), ("fita", fita), ("caneta", caneta), ("rasgo", rasgo), ("queda", queda), ("whoosh", whoosh), ("batida", batida)]:
        salvar(ROOT / "assets" / "sfx" / f"{nome}.wav", fn(), stereo=True)
