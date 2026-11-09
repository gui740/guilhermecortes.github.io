"""Trilha de fundo original (sintetizada, livre de direitos), sincronizada com src/timeline.json.
Drone grave + pulso de "coração" que acelera a cada filme + tensão aguda + impactos nos cortes.
Uso: python3 audio/trilha.py out/trilha.wav"""
import json, os, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(os.path.join(HERE, '..', 'src', 'timeline.json')))
FPS, SR = tl['fps'], 48000
TOTAL = tl['total'] / FPS
N = int(TOTAL * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(13)
L = np.zeros(N); R = np.zeros(N)


def sec(k):
    a, d = tl[k]
    return a / FPS, (a + d) / FPS


def env(a, b, fade=1.0):
    """janela 0→1→0 entre a e b (s)"""
    return np.clip(np.minimum((t - a) / fade, (b - t) / fade), 0, 1)


def saw(freq, nh=10):
    out = np.zeros(N)
    ph = 2 * np.pi * np.cumsum(freq) / SR if np.ndim(freq) else 2 * np.pi * freq * t
    for h in range(1, nh + 1):
        out += np.sin(ph * h) / h * (0.9 ** h)
    return out


def smooth(x, n):
    k = np.ones(n) / n
    return np.convolve(x, k, mode='same')


# --- raiz harmônica por bloco (Lá menor, sem ostinato de semitom) ---
roots = {'hook': 55.0, 'data': 55.0, 'm1': 55.0, 'm2': 49.0, 'm3': 43.65,
         'spielberg': 55.0, 'brasil': 41.2, 'cta': 55.0}
freq = np.full(N, 55.0)
for k, f0 in roots.items():
    a, b = sec(k); freq[(t >= a) & (t < b)] = f0
freq = smooth(freq, int(0.25 * SR))

# drone: duas serras levemente desafinadas + quinta, abafadas
drone = saw(freq, 8) + saw(freq * 1.004, 8) * 0.8 + 0.35 * np.sin(2 * np.pi * np.cumsum(freq * 1.5) / SR)
drone = smooth(drone, 18)
swell = 0.75 + 0.25 * np.sin(2 * np.pi * t / 9)
dlev = np.ones(N) * 0.22
a, b = sec('spielberg'); dlev = dlev * (1 - 0.55 * env(a, b, 0.4))
L += drone * swell * dlev; R += drone * swell * dlev * 0.95

# --- pulso tipo batimento (lub-dub), andamento por bloco ---
bpm = {'hook': 84, 'data': 88, 'm1': 96, 'm2': 104, 'm3': 112, 'spielberg': 0, 'brasil': 118, 'cta': 0}


def thump(d=0.35, f0=62):
    tt = np.arange(int(d * SR)) / SR
    f = f0 * np.exp(-tt * 9) + 38
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 11)


TH, TH2 = thump(), thump(0.3, 54) * 0.6
for k, bp in bpm.items():
    if not bp: continue
    a, b = sec(k)
    beat = 60 / bp
    x = a + 0.05
    while x < b - 0.25:
        for s0, sig in ((x, TH), (x + beat * 0.28, TH2)):
            i = int(s0 * SR); n = min(len(sig), N - i)
            L[i:i + n] += sig[:n] * 0.55; R[i:i + n] += sig[:n] * 0.55
        x += beat

# --- tique metálico (8ths) nos filmes ---
click = rng.standard_normal(int(0.03 * SR)) * np.exp(-np.arange(int(0.03 * SR)) / SR * 160)
click = click - smooth(click, 6)  # tira grave → som de metal/sonar
for k in ('m1', 'm2', 'm3', 'brasil'):
    a, b = sec(k); beat = 60 / bpm[k] / 2; x = a + 0.4; j = 0
    while x < b - 0.3:
        i = int(x * SR); n = min(len(click), N - i); g = 0.05 if j % 2 else 0.08
        (L if j % 2 else R)[i:i + n] += click[:n] * g
        x += beat; j += 1

# --- tensão aguda (cluster com tremolo) que cresce ao longo dos filmes ---
cl = sum(np.sin(2 * np.pi * f * t + p) for f, p in ((880, 0), (933, 1), (1046, 2), (1244, 3)))
trem = 0.6 + 0.4 * np.sin(2 * np.pi * 6.5 * t)
lvl = np.zeros(N)
for k, g in (('m1', 0.010), ('m2', 0.016), ('m3', 0.022), ('spielberg', 0.03), ('brasil', 0.026)):
    a, b = sec(k); lvl = np.maximum(lvl, env(a, b, 1.2) * g)
L += cl * trem * lvl; R += np.roll(cl, 400) * trem * lvl

# --- água (ruído grave) de fundo ---
water = smooth(rng.standard_normal(N), 60) * 1.4
water *= 0.5 + 0.5 * np.sin(2 * np.pi * t / 5.3) ** 2
L += water * 0.25; R += np.roll(water, 2400) * 0.25


# --- impactos (braam) nos inícios de bloco e riser antes do CTA ---
def braam(d=2.2, f0=55):
    tt = np.arange(int(d * SR)) / SR
    s = sum(np.sin(2 * np.pi * f0 * m * tt + m) / m for m in (1, 2, 3, 4, 5, 6))
    s += np.sin(2 * np.pi * f0 / 2 * tt) * 1.2
    return np.tanh(s * 1.5) * np.exp(-tt * 2.2) * np.minimum(1, tt * 60)


for k, g in (('data', 0.32), ('m1', 0.38), ('m2', 0.38), ('m3', 0.38), ('brasil', 0.3), ('cta', 0.55)):
    a, _ = sec(k); sig = braam(f0=roots[k]); i = int(a * SR); n = min(len(sig), N - i)
    L[i:i + n] += sig[:n] * g; R[i:i + n] += sig[:n] * g
a, _ = sec('cta'); n = int(2.0 * SR); i = int(a * SR) - n
rz = rng.standard_normal(n) * np.linspace(0, 1, n) ** 2
rz = rz - smooth(rz, 30)
L[i:i + n] += rz * 0.18; R[i:i + n] += rz * 0.18

# --- final: cauda e fade ---
mix = np.stack([L, R], 1)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.4) * 0.8
fo = int(1.2 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
fi = int(0.05 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', sys.argv[1], f'{TOTAL:.1f}s')
