"""Gera efeitos sonoros sutis (sonar, água, batida grave) sincronizados com o Reel.
Uso: python3 tools/sfx.py out/sfx_opcional.wav"""
import sys, wave
import numpy as np

SR = 44100
DUR = 43.0
rng = np.random.default_rng(7)
mix = np.zeros(int(SR * DUR))


def onepole_lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y


def add(sig, t, gain=1.0):
    i = int(t * SR); n = min(len(sig), len(mix) - i)
    mix[i:i + n] += sig[:n] * gain


def sonar(f=1150, d=1.6):
    t = np.arange(int(SR * d)) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) * np.minimum(1, t * 400)
    echo = np.zeros_like(s); k = int(0.32 * SR); echo[k:] = s[:-k] * 0.35
    return s + echo


def boom(d=1.4, f0=70):
    t = np.arange(int(SR * d)) / SR
    f = f0 * np.exp(-t * 2.5) + 32
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 3.0) * np.minimum(1, t * 300)


def whoosh(d=0.75):
    n = int(SR * d); t = np.arange(n) / SR
    env = np.sin(np.pi * t / d) ** 2
    noise = rng.standard_normal(n)
    a = np.linspace(0.02, 0.25, n)  # varredura simples via ganho de filtro
    y = np.empty(n); acc = 0.0
    for i in range(n):
        acc += a[i] * (noise[i] - acc); y[i] = acc
    return y * env * 2.2


def dive(d=1.3):
    n = int(SR * d); t = np.arange(n) / SR
    rumble = onepole_lp(rng.standard_normal(n), 0.01) * 6 * np.exp(-t * 1.5) * np.minimum(1, t * 8)
    bub = np.zeros(n)
    for _ in range(18):
        st = rng.uniform(0, d - 0.1); f = rng.uniform(500, 1400); ln = int(0.06 * SR)
        tt = np.arange(ln) / SR
        b = np.sin(2 * np.pi * (f + 3000 * tt) * tt) * np.exp(-tt * 60) * 0.25
        i = int(st * SR); bub[i:i + ln] += b[:n - i]
    return rumble + bub


def bite():
    n = int(SR * 0.5); t = np.arange(n) / SR
    crunch = rng.standard_normal(n) * np.exp(-t * 28) * 0.5
    return crunch + boom(0.5, 110)[:n] * 0.9


# linha do tempo (segundos) — casa com src/data.ts
for t in (0.0, 1.2):
    add(sonar(), t, 0.22)
add(boom(), 0.0, 0.55)
for t in (2.17, 23.67, 38.17):          # barbatana atravessando
    add(whoosh(), t, 0.35)
for t in (6.6, 32.1):                   # mergulho
    add(dive(), t, 0.45)
for t in (15.2, 35.2):                  # mordida
    add(bite(), t, 0.5)
add(boom(1.2, 60), 5.57, 0.4)            # "quem devia ter medo de quem?"
for start in (7.0, 15.5, 24.0):          # pins do mapa
    add(sonar(1350, 1.2), start + 5.5, 0.16)
add(boom(1.8, 55), 38.5, 0.6)            # CTA

mix = np.tanh(mix * 1.2) * 0.85
fade = int(0.5 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
st = np.stack([mix, mix], 1)
pcm = (st * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', sys.argv[1])
