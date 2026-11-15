"""Mixagem: narração em primeiro plano + trilha de rock sintetizada (guitarra distorcida, baixo, bateria; ~-17 dB) com gongo nas pontas
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

# ---------------- trilha: rock (guitarra distorcida + baixo + bateria), com gongo nas pontas p/ o loop ----------------
BPM = 150.0; E8 = 60 / BPM / 2            # colcheia = 0,2 s ; compasso = 1,6 s
D2, Eb2, F2, G2, Ab2 = 73.42, 77.78, 87.31, 98.0, 103.83

def ks(f, dur, damp=0.996, bright=0.5, seed=0):
    """corda dedilhada (Karplus-Strong)"""
    r = np.random.default_rng(seed); n = int(dur * SR); L = int(SR / f)
    buf = r.uniform(-1, 1, L); buf = signal.lfilter([1 - bright, bright], [1], buf)
    y = np.zeros(n); y[:L] = buf
    for i in range(L, n): y[i] = damp * 0.5 * (y[i - L] + y[i - L + 1])
    return y

def amp(x, gain=9.0, lp=4200):
    x = signal.lfilter(*signal.butter(2, 110 / (SR / 2), 'high'), x)
    y = np.tanh(gain * x) + 0.3 * np.tanh(gain * 2.5 * x)
    y = signal.lfilter(*signal.butter(2, lp / (SR / 2)), y)
    return signal.lfilter(*signal.butter(1, 1700 / (SR / 2), 'high'), y) * 0.35 + y * 0.8      # presença

_chord = {}
def chord(f, dur, mute=False):
    key = (round(f, 1), round(dur, 2), mute)
    if key not in _chord:
        d = 0.985 if mute else 0.9975
        x = ks(f, dur, d, 0.3 if mute else 0.6, 1) + ks(f * 1.4983, dur, d, 0.5, 2) + 0.7 * ks(f * 2, dur, d, 0.6, 3) + 0.5 * ks(f * 1.004, dur, d, 0.5, 4)
        if mute: x = signal.lfilter(*signal.butter(2, 900 / (SR / 2)), x) * np.exp(-np.arange(len(x)) / (0.07 * SR)) * 2.2
        y = amp(x / np.abs(x).max(), 7 if mute else 11)
        f_ = int(0.012 * SR); y[-f_:] *= np.linspace(1, 0, f_)
        _chord[key] = y
    return _chord[key]

def kick():
    n = int(0.28 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (48 * tt + 70 / 28 * (1 - np.exp(-tt * 28)))) * np.exp(-tt / 0.09) + 0.35 * rng.normal(0, 1, n) * np.exp(-tt / 0.004)
def snare():
    n = int(0.3 * SR); tt = np.arange(n) / SR
    nz = signal.lfilter(*signal.butter(2, [900 / (SR / 2), 7000 / (SR / 2)], 'band'), rng.normal(0, 1, n)) * np.exp(-tt / 0.07)
    return nz * 1.3 + 0.6 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / 0.05)
def hat(open_=False):
    n = int((0.25 if open_ else 0.05) * SR); tt = np.arange(n) / SR
    return signal.lfilter(*signal.butter(2, 7000 / (SR / 2), 'high'), rng.normal(0, 1, n)) * np.exp(-tt / (0.09 if open_ else 0.015))
def crash():
    n = int(1.8 * SR); tt = np.arange(n) / SR
    return signal.lfilter(*signal.butter(2, 3500 / (SR / 2), 'high'), rng.normal(0, 1, n)) * np.exp(-tt / 0.5)
def tom(f):
    n = int(0.3 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (f * tt + f * 0.5 / 20 * (1 - np.exp(-tt * 20)))) * np.exp(-tt / 0.1)
def bass(f, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = signal.sawtooth(2 * np.pi * f * tt) * 0.6 + np.sin(2 * np.pi * f * tt)
    y = signal.lfilter(*signal.butter(2, 420 / (SR / 2)), y) * np.minimum(1, tt / 0.005) * np.exp(-tt / 0.35)
    return np.tanh(2 * y)

stops = cam['stops']
def section(tm):
    """intensidade por trecho: gancho abafado -> voos com tambores -> paradas com banda cheia"""
    if tm < 4.0: return 'hook'
    for s in stops:
        if s['ta'] - 0.2 <= tm < s['td']: return 'full'
    return 'fly' if tm < DUR - 3.4 else 'end'

RIFF_A = [D2, D2, D2, F2, D2, D2, Eb2, D2]
RIFF_B = [D2, D2, D2, F2, D2, Ab2, G2, F2]
gtr = np.zeros(N); bs = np.zeros(N); dr = np.zeros(N)
nb = int(DUR / E8)
for k in range(nb):
    tm = 0.15 + k * E8; sec = section(tm); step = k % 8; bar = k // 8
    root = (RIFF_B if bar % 4 == 3 else RIFF_A)[step]
    if sec == 'hook':
        place(gtr, chord(root, E8 * 0.95, True), tm, 0.75)
        if step % 2 == 0: place(dr, kick(), tm, 0.7)
        place(dr, hat(), tm, 0.16)
    elif sec == 'full':
        acc = step in (0, 3, 6)
        place(gtr, chord(root, E8 * (1.9 if acc else 0.95), not acc), tm, 1.0 if acc else 0.7)
        place(bs, bass(root / 2, E8 * 0.95), tm, 0.7)
        if step in (0, 3, 5): place(dr, kick(), tm, 0.95)
        if step in (2, 6): place(dr, snare(), tm, 0.8)
        place(dr, hat(step == 7), tm, 0.2 if step % 2 == 0 else 0.13)
    elif sec == 'fly':
        if step in (0, 4): place(gtr, chord(root, E8 * 3.8), tm, 0.8)
        place(bs, bass(root / 2, E8 * 0.95), tm, 0.6)
        place(dr, tom([95, 95, 120, 95, 80, 80, 120, 150][step]), tm, 0.55)
        if step in (0, 4): place(dr, kick(), tm, 0.9)
        if step == 6: place(dr, snare(), tm, 0.6)
    else:
        if step == 0 and bar % 2 == 0: place(gtr, chord(D2, 3.0), tm, 0.9); place(dr, crash(), tm, 0.3)
        if step in (0, 4): place(dr, kick(), tm, 0.7)
        place(dr, hat(), tm, 0.12)
for s in stops:                                              # viradas e pratos nas chegadas e nos títulos
    for j, f in enumerate((150, 150, 120, 120, 95, 95, 80, 80)): place(dr, tom(f), s['ta'] - 0.8 + j * 0.1, 0.6)
    place(dr, crash(), s['ta'], 0.42); place(dr, crash(), s['tt'], 0.36)
    place(gtr, chord(D2, 1.4), s['tt'], 0.8)
place(dr, crash(), 0.15, 0.3)
band = reverb(gtr * 0.5, 0.12, 4) + bs * 0.42 + reverb(dr * 0.6, 0.1, 5)
gongs = np.zeros(N)
place(gongs, metal(61.7, 7.0, GONG, 3.2, 0.5), 0.0, 1.0)
place(gongs, metal(61.7, 3.0, GONG, 3.2, 0.5)[::-1] * np.linspace(0, 1, int(3.0 * SR)) ** 2, DUR - 3.0, 0.55)
band *= np.interp(t, [0, 0.3, DUR - 1.2, DUR], [0.4, 1, 1, 0.25])
music = band / np.abs(band).max() + reverb(gongs, 0.35, 3) * 0.5
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
music *= vrms * db(-17) / mrms * 1.0                 # trilha 18 dB abaixo da voz
music_boost = 1 + 0.8 * (np.interp(t, [0, 0.1, 1.0, DUR - 2.2, DUR - 0.3, DUR], [1, 1, 0, 0, 1, 1]))  # abre/fecha no gongo
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
