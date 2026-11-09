"""Gera efeitos sonoros sutis (sonar, água, batida grave) sincronizados com src/timeline.json.
Uso: python3 audio/sfx.py out/sfx.wav"""
import json, os, re, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, '..', 'src', 'timeline.json')))
CUES = [float(x) for x in re.findall(r'numbers: ([0-9.]+)', open(os.path.join(HERE, '..', 'src', 'data.ts')).read())]
SR = 48000
DUR = TL['total'] / TL['fps']


def st(k):
    return TL[k][0] / TL['fps']

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


# linha do tempo — tudo derivado de src/timeline.json
for t in (0.0, 1.4):
    add(sonar(), t, 0.22)
add(boom(), 0.0, 0.5)
for k in ('data', 'm3', 'cta'):              # barbatana atravessando (corte no meio)
    add(whoosh(), st(k) - 0.36, 0.35)
for k in ('m1', 'spielberg'):                # mergulho
    add(dive(), st(k) - 0.4, 0.45)
for k in ('m2', 'brasil'):                   # mordida
    add(bite(), st(k) - 0.3, 0.5)
add(boom(1.2, 60), st('data') + 232 / 30, 0.35)   # "quem devia ter medo de quem?"
for k, c in zip(('m1', 'm2', 'm3'), CUES):   # pins do mapa
    add(sonar(1350, 1.2), st(k) + c + 1.1, 0.14)
add(boom(1.8, 55), st('cta'), 0.55)          # CTA

mix = np.tanh(mix * 1.2) * 0.85
fade = int(0.5 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
st = np.stack([mix, mix], 1)
pcm = (st * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', sys.argv[1])
