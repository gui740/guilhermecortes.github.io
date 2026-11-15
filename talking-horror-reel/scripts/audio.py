"""Mixagem: narração em primeiro plano + trilha de tensão (drone grave + timbres de gamelão/sino sintetizados, -18 dB)
+ efeitos sincronizados com a câmera (whoosh segue a velocidade, papel nos pop-ups, carimbo, sino por parada).
Tudo sintetizado aqui (numpy) => 100% livre de direitos."""
import json, os, sys
import numpy as np, soundfile as sf
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
cam = json.load(open(os.path.join(ROOT, 'src/camera_export.json')))
DUR = cam['duration']; N = int(DUR * SR)
rng = np.random.default_rng(11)
t = np.arange(N) / SR
db = lambda d: 10 ** (d / 20)

def place(buf, x, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf): return
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), len(buf) - i); buf[i:i + n] += x[:n] * gain

def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))

def metal(f0, dur, partials, decay, bright=1.0):
    """timbre de metalofone/gongo: parciais inarmônicos com decaimentos próprios e leve batimento"""
    n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for k, (r, a) in enumerate(partials):
        f = f0 * r
        y += a * np.sin(2 * np.pi * f * tt + rng.uniform(0, 6.28)) * np.exp(-tt / (decay / (1 + 0.55 * k * bright)))
        y += 0.35 * a * np.sin(2 * np.pi * f * 1.004 * tt) * np.exp(-tt / (decay / (1 + 0.5 * k * bright)))
    att = np.minimum(1, tt / 0.004)
    return y * att / max(1e-6, np.abs(y).max())

GENDER = [(1, 1), (2.76, 0.45), (5.4, 0.22), (8.93, 0.1)]            # lâminas de bronze (gendèr/saron)
GONG = [(1, 1), (1.48, 0.6), (2.0, 0.5), (2.63, 0.3), (3.4, 0.2), (4.2, 0.12)]
BELL = [(1, 1), (2.0, 0.6), (2.99, 0.45), (4.2, 0.3), (5.43, 0.2), (6.8, 0.12)]

def reverb(x, wet=0.3, seed=1):
    r = np.random.default_rng(seed); n = int(2.2 * SR)
    ir = r.normal(0, 1, n) * np.exp(-np.arange(n) / (0.55 * SR)); ir = signal.lfilter(*signal.butter(2, 3500 / (SR / 2)), ir); ir /= np.sqrt((ir ** 2).sum())
    return x + wet * signal.fftconvolve(x, ir)[:len(x)]

# ---------------- trilha ----------------
music = np.zeros(N)
# drone grave (ré) com batimento lento e respiração
for f, a in ((36.7, 0.9), (55.0, 0.7), (73.4, 0.5), (110.3, 0.22), (146.9, 0.1)):
    music += a * np.sin(2 * np.pi * f * t + 2.5 * np.sin(2 * np.pi * 0.07 * t + f)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t + f * 0.1))
air = signal.lfilter(*signal.butter(2, [180 / (SR / 2), 520 / (SR / 2)], 'band'), rng.normal(0, 1, N))
music += 0.5 * air * (0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t))
music *= 0.5
# escala pélog (aprox.) sobre ré: figura esparsa de metalofone, mais densa nas paradas indonésias
PELOG = [146.8, 158.5, 174.0, 207.0, 220.5, 235.0, 277.0]
notes = []
pat = [0, 3, 4, 2, 6, 4, 3, 1]
tm = 1.2; i = 0
while tm < DUR - 1.5:
    dense = 17.5 < tm < 31.5
    notes.append((tm, PELOG[pat[i % len(pat)]] * (2 if (i % 5 == 4) else 1), 0.5 if dense else 0.32))
    tm += (0.62 if dense else 1.24) * (1 + 0.04 * np.sin(i)); i += 1
mel = np.zeros(N)
for at, f, g in notes: place(mel, metal(f, 2.6, GENDER, 0.9), at, g)
# sininhos de templo (parada da Tailândia) e gongos de frase
for at in (5.7, 7.9, 10.2, 12.3): place(mel, metal(1244.5 * (1 if at < 9 else 0.89), 2.5, BELL, 0.9, 0.6), at, 0.16)
music += reverb(mel, 0.45, 2) * 0.55
gongs = np.zeros(N)
for at, f, g in ((0.0, 61.7, 1.0), (17.55, 55.0, 0.8), (25.6, 49.0, 0.9), (33.0, 73.4, 0.5)):
    place(gongs, metal(f, 7.0, GONG, 3.2, 0.5), at, g)
# o gongo final ressoa até o corte, para emendar com o gongo do frame 0 (loop)
place(gongs, metal(61.7, 3.0, GONG, 3.2, 0.5)[::-1] * np.linspace(0, 1, int(3.0 * SR)) ** 2, DUR - 3.0, 0.55)
music += reverb(gongs, 0.35, 3) * 0.9
music /= np.abs(music).max()

# ---------------- efeitos ----------------
sfx = np.zeros(N)
# whoosh contínuo: ruído filtrado cujo volume e brilho seguem a velocidade da câmera
sp = np.interp(t, np.arange(len(cam['speeds'])) / 30, cam['speeds'])
sp = signal.lfilter(*signal.butter(1, 6 / (SR / 2)), sp)
lvl = np.clip(sp / 60, 0, 1) ** 0.6
noise = rng.normal(0, 1, N)
lo = signal.lfilter(*signal.butter(2, [120 / (SR / 2), 700 / (SR / 2)], 'band'), noise)
hi = signal.lfilter(*signal.butter(2, [700 / (SR / 2), 4200 / (SR / 2)], 'band'), noise)
whoosh = (lo * (0.25 + lvl) + hi * lvl ** 2 * 1.4) * (0.02 + lvl)
sfx += whoosh * 0.55

def paper(dur=0.5, seed=0):
    r = np.random.default_rng(seed); n = int(dur * SR); y = np.zeros(n)
    for _ in range(26):
        p = int(r.uniform(0, n * 0.85)); l = int(r.uniform(0.004, 0.03) * SR)
        g = r.normal(0, 1, l) * np.hanning(l) * r.uniform(0.3, 1)
        y[p:p + l] += g[:n - p]
    y = signal.lfilter(*signal.butter(2, [1800 / (SR / 2), 9000 / (SR / 2)], 'band'), y)
    return y / np.abs(y).max() * np.hanning(n) ** 0.3

def stamp():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (95 * np.exp(-tt * 18) + 48) * tt) * np.exp(-tt / 0.07)
    click = signal.lfilter(*signal.butter(2, 2500 / (SR / 2), 'high'), rng.normal(0, 1, n)) * np.exp(-tt / 0.012)
    return thud + 0.5 * click

def hit(f=180):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.12) * 0.6 + signal.lfilter(*signal.butter(2, 900 / (SR / 2)), rng.normal(0, 1, n)) * np.exp(-tt / 0.05) * 0.5

for k, s in enumerate(cam['stops']):
    place(sfx, stamp(), s['ta'] - 0.42, 0.9)                       # carimbo na chegada
    for i in range(8): place(sfx, paper(0.34, k * 10 + i), s['ta'] - 0.55 + i * 0.1, 0.30)   # dioramas se levantando (cascata)
    for i in range(8): place(sfx, paper(0.3, k * 10 + 50 + i), s['td'] + 0.05 + i * 0.1, 0.22)  # deitando de volta
    place(sfx, paper(0.4, 99 + k), s['tt'] - 0.9, 0.3)             # camada de primeiro plano sobe
    place(sfx, hit(150 + 20 * k), s['tt'] - 0.02, 0.5)             # revelação do título
# ambiência curta de cada parada
place(sfx, reverb(metal(1568, 2.2, BELL, 0.8, 0.6), 0.5, 5), 5.75, 0.22)        # sino de templo (Tailândia)
place(sfx, reverb(metal(293.7, 3.0, GENDER, 1.4), 0.5, 6), 17.85, 0.35)          # bonang/kenong (Indonésia)
place(sfx, reverb(metal(220.5, 3.0, GENDER, 1.4), 0.5, 7), 25.95, 0.35)          # gendèr do wayang (Java)
sfx = np.clip(sfx, -1.5, 1.5)

# ---------------- narração + mix ----------------
OFF = 0.15
voice = np.zeros(N)
vp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets/audio/narracao.wav')
v, vsr = sf.read(vp)
if v.ndim > 1: v = v.mean(1)
if vsr != SR: v = signal.resample_poly(v, SR, vsr)
place(voice, v, OFF)
voice *= db(-3) / max(1e-6, np.abs(voice).max())
vrms = np.sqrt((voice[np.abs(voice) > 0.02] ** 2).mean())
mrms = np.sqrt((music ** 2).mean())
music *= vrms * db(-18) / mrms * 1.0                 # trilha 18 dB abaixo da voz
music_boost = 1 + 1.6 * (np.interp(t, [0, 0.1, 1.0, DUR - 2.2, DUR - 0.3, DUR], [1, 1, 0, 0, 1, 1]))  # abre/fecha no gongo
mix = voice + music * music_boost + sfx * 0.22
# estéreo leve: trilha/efeitos com pequena largura
wide = signal.lfilter([0] * 480 + [1], [1], music * music_boost + sfx * 0.22)
L = voice + 0.75 * (music * music_boost + sfx * 0.22) + 0.25 * wide
Rr = voice + 0.75 * (music * music_boost + sfx * 0.22) - 0.25 * wide + 0.25 * (music * music_boost + sfx * 0.22)
st = np.stack([L, Rr], 1)
st = np.tanh(st * 1.05) / np.tanh(1.05) * db(-1.0) / max(1.0, np.abs(st).max())
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'assets/audio/mix.wav')
sf.write(out, st[:N], SR)
sf.write(os.path.join(ROOT, 'assets/audio/trilha.wav'), (music / max(1e-6, np.abs(music).max()) * 0.5)[:N], SR)
print('mix', out, 'dur', len(st) / SR, 'voz rms', vrms, 'trilha rel dB', 20 * np.log10(np.sqrt((music ** 2).mean()) / vrms))
