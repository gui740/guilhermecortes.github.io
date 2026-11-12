# Trilha de rock instrumental original, 100% sintetizada (sem direitos de terceiros).
# Guitarra: Karplus-Strong em power chords + distorção + simulação de caixa; baixo; bateria sintetizada.
# rock(L, marks) -> np.array mono 48 kHz.  marks: {'breakdown': (t0, t1), 'big': t, 'end': t}
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(5)
BPM = 126
BEAT = 60 / BPM
E8 = BEAT / 2

def lp(x, f, o=2): b, a = signal.butter(o, f / (SR / 2)); return signal.lfilter(b, a, x)
def hp(x, f, o=2): b, a = signal.butter(o, f / (SR / 2), 'high'); return signal.lfilter(b, a, x)
def bp(x, f1, f2, o=2): b, a = signal.butter(o, [f1 / (SR / 2), f2 / (SR / 2)], 'band'); return signal.lfilter(b, a, x)
def peak(x, f, g_db, q=1.0):
    A = 10 ** (g_db / 40); w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return signal.lfilter(b, a, x)
def place(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf) or i < 0: return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += x * g

def ks(freq, dur, damp=0.996, bright=0.5):
    """Karplus-Strong: corda dedilhada."""
    n = int(dur * SR); N = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, N); buf = lp(buf, 2000 + 6000 * bright)
    out = np.zeros(n); idx = 0
    for i in range(n):
        out[i] = buf[idx]
        nxt = (idx + 1) % N
        buf[idx] = damp * 0.5 * (buf[idx] + buf[nxt])
        idx = nxt
    return out

_cache = {}
def chord(root_hz, dur, mute):
    key = (round(root_hz, 2), round(dur, 3), mute)
    if key in _cache: return _cache[key]
    damp = 0.982 if mute else 0.9975
    x = ks(root_hz, dur, damp, 0.35 if mute else 0.6) + 0.8 * ks(root_hz * 1.4983, dur, damp, 0.4) + 0.5 * ks(root_hz * 2, dur, damp, 0.4)
    env = np.exp(-np.arange(len(x)) / SR / (0.09 if mute else 1.6))
    x = x * env
    _cache[key] = x
    return x

def amp(x, gain=14):
    """distorção + 'caixa 4x12'"""
    x = hp(x, 90)
    x = peak(x, 700, 4, 0.8)
    x = np.tanh(gain * x) * 0.6 + 0.4 * np.tanh(gain * 2.5 * x)
    x = lp(x, 5200, 4); x = peak(x, 2400, 3, 1.2); x = peak(x, 400, -3, 1.0); x = hp(x, 70)
    return x

def kick():
    t = np.arange(int(0.45 * SR)) / SR; f = 50 + 110 * np.exp(-t / 0.035)
    k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    k[:300] += rng.normal(0, 0.6, 300) * np.exp(-np.arange(300) / 60)
    return np.tanh(k * 1.6)
def snare():
    t = np.arange(int(0.35 * SR)) / SR
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    nz = bp(rng.normal(0, 1, len(t)), 1500, 9000) * np.exp(-t / 0.11)
    return 0.6 * tone + 0.9 * nz
def hat(open_=False):
    t = np.arange(int((0.3 if open_ else 0.06) * SR)) / SR
    return hp(rng.normal(0, 1, len(t)), 7000, 4) * np.exp(-t / (0.12 if open_ else 0.018)) * 0.5
def crash():
    t = np.arange(int(2.2 * SR)) / SR
    return hp(rng.normal(0, 1, len(t)), 4000, 2) * np.exp(-t / 0.7) * 0.55
def tom(f):
    t = np.arange(int(0.4 * SR)) / SR; ff = f * (1 + 0.6 * np.exp(-t / 0.03))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t / 0.16)

# Mi menor "de terror": E5 E5 G5 A5 | E5 E5 Bb5 A5 (trítono no Bb)
E2 = 82.41
ROOTS = [E2, E2, E2 * 2 ** (3 / 12), E2 * 2 ** (5 / 12), E2, E2, E2 * 2 ** (6 / 12), E2 * 2 ** (5 / 12)]
# padrão de palhetadas por compasso (8 colcheias): 'm' abafada, 'O' aberta acentuada, '.' pausa
RIFF = ['O', 'm', 'm', 'O', 'm', 'm', 'O', 'm']

def rock(L, marks):
    n = int(L * SR)
    gtr = np.zeros(n); bass = np.zeros(n); drums = np.zeros(n)
    bd0, bd1 = marks.get('breakdown', (-1, -1)); big = marks.get('big', 1e9); end = marks.get('end', L)
    K, S, H, HO, C = kick(), snare(), hat(), hat(True), crash()
    place(drums, C, 0.0, 0.8)
    bar = 0; t = 0.0
    while t < end:
        root = ROOTS[bar % len(ROOTS)]
        half = bd0 <= t < bd1         # respiro: meio-tempo, guitarra só no 1 do compasso
        for i, p in enumerate(RIFF):
            at = t + i * E8
            if at >= end: break
            if half:
                if i == 0:
                    place(gtr, chord(root, BEAT * 4, False), at, 0.9)
            elif p != '.':
                mute = p == 'm'
                place(gtr, chord(root, E8 * (1.0 if mute else 1.9), mute), at, 0.75 if mute else 1.0)
            # baixo dobra a tônica em colcheias
            if not half or i in (0, 4):
                bt = np.arange(int(E8 * 0.95 * SR)) / SR
                b = (np.sin(2 * np.pi * root / 2 * bt) + 0.35 * np.sign(np.sin(2 * np.pi * root / 2 * bt))) * np.exp(-bt / 0.4)
                place(bass, lp(b, 600), at, 0.7)
            # bateria
            heavy = at >= big
            if half:
                if i == 0: place(drums, K, at)
                if i == 4: place(drums, S, at, 0.9)
                place(drums, H, at, 0.35)
            else:
                if i in (0, 3, 5) or (heavy and i == 6): place(drums, K, at)
                if i in (2, 6): place(drums, S, at)
                place(drums, HO if (heavy and i % 2 == 0) else H, at, 0.55 if i % 2 == 0 else 0.35)
        t += 8 * E8; bar += 1
        # virada de tom antes da parte pesada
    if big < end:
        for j, f in enumerate([220, 180, 140, 110]):
            place(drums, tom(f), big - BEAT + j * BEAT / 4, 0.9)
        place(drums, C, big, 1.0)
    if bd1 > 0: place(drums, C, bd1, 0.8)
    # acorde final soando
    place(gtr, chord(E2, 3.0, False), end, 1.1); place(drums, C, end, 1.0); place(drums, K, end, 1.0)
    g = amp(gtr * 0.5)
    g = 0.7 * g + 0.3 * np.roll(g, int(0.012 * SR))          # dobra de guitarra
    mix = 1.2 * g + 0.75 * lp(bass, 900) + 0.7 * drums
    mix = np.tanh(mix * 0.9) * 0.9                             # cola/compressão
    f = int(0.02 * SR); mix[-f:] *= np.linspace(1, 0, f)
    return mix
