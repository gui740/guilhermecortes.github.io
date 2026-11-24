"""Trilha + efeitos sintetizados e sincronizados com as cenas do render.py."""
import json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import render as R

SR = 44100
rng = np.random.default_rng(7)
T = json.load(open("timings.json"))
durs, total = T["durations"], T["total"]
N = int((total + 0.5) * SR)
music = np.zeros(N); sfx = np.zeros(N)

def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    k = int(a * SR)
    if k: e[:k] *= np.linspace(0, 1, k)
    return e

def lp(x, f):
    b, a = butter(2, f / (SR / 2)); return lfilter(b, a, x)
def hp(x, f):
    b, a = butter(2, f / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, f1, f2):
    b, a = butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band"); return lfilter(b, a, x)

def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += g * x

# ---------------- instrumentos
def kick():
    n = int(.45 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .16) * 1.1
def snare():
    n = int(.3 * SR); t = np.arange(n) / SR
    noise = bp(rng.standard_normal(n), 1200, 7000) * env(n, .001, .09)
    tone = np.sin(2 * np.pi * 190 * t) * env(n, .001, .05)
    return noise * .8 + tone * .5
def clap():
    n = int(.25 * SR); x = bp(rng.standard_normal(n), 900, 4000)
    e = np.zeros(n)
    for o in (0, .012, .024):
        k = int(o * SR); e[k:] += env(n - k, .0005, .05 if o < .02 else .12)
    return x * e * .7
def hat(open_=False):
    n = int((.25 if open_ else .06) * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, .0005, .08 if open_ else .018) * .35
def bass(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + .35 * np.sin(2 * np.pi * freq * 2 * t)
    return np.tanh(1.6 * x) * env(n, .005, dur * .8) * .5
def pluck(freq, dur=.35):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * freq * h * t) / h for h in (1, 2, 3, 4))
    return lp(x, 3500) * env(n, .002, .12) * .22
def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t + .3 * np.sin(2 * np.pi * .3 * t)) for f in freqs)
    e = np.minimum(1, t / .4) * np.minimum(1, (dur - t) / .4)
    return lp(x, 1800) * e * .05

# ---------------- trilha: tenso/hype, 100 BPM, Lá menor
BPM = 100; beat = 60 / BPM; bar = 4 * beat
chords = [  # (raiz do baixo, notas do pad)
    (55.00, [220.0, 261.6, 329.6]),   # Am
    (43.65, [174.6, 220.0, 261.6]),   # F
    (48.99, [196.0, 246.9, 293.7]),   # G
    (41.20, [164.8, 207.7, 246.9]),   # E (tensão)
]
melody = [440, 523.3, 493.9, 440, 392, 440, 329.6, 0]
t, b = 0.0, 0
intro = 1.0  # primeiro segundo só pad + hit
while t < total:
    root, notes = chords[b % 4]
    music_t = t
    add(music, pad(notes, bar), t)
    if t >= intro:
        for s in range(4):  # semicolcheias: kick/snare/hats
            tb = t + s * beat
            add(music, kick(), tb, .9 if s in (0, 2) else 0)
            if s == 2 and b % 2: add(music, kick(), tb + beat * .75, .6)
            if s in (1, 3): add(music, snare(), tb, .55); add(music, clap(), tb, .5)
            for h in range(4):
                add(music, hat(open_=(h == 2 and s == 3)), tb + h * beat / 4, .9 if h % 2 == 0 else .55)
        for s, step in enumerate([0, 1.5, 2, 3, 3.5]):
            add(music, bass(root * (2 if s == 4 else 1), beat * .9), t + step * beat, .9)
        if b % 2 == 0:
            for k, f in enumerate(melody):
                if f: add(music, pluck(f * (1.5 if b % 4 == 2 else 1)), t + k * beat / 2, 1)
    t += bar; b += 1
# fade out final
fo = int(1.2 * SR); music[-fo:] *= np.linspace(1, 0, fo)

# ---------------- efeitos
def whoosh(d=.45):
    """Varrido limpo em senoide (sem ruído: o ruído soava como chiado)."""
    n = int(d * SR); t = np.arange(n) / SR
    f = 180 + 900 * (t / d) ** 1.6
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + .4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    e = np.sin(np.pi * t / d) ** 2
    return x * e * .35
def pop():
    n = int(.12 * SR); t = np.arange(n) / SR
    f = 500 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .03) * .45
def thud():  # carimbo
    n = int(.35 * SR); t = np.arange(n) / SR
    low = np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-t * 30)) / SR) * env(n, .001, .12)
    crack = lp(rng.standard_normal(n), 2500) * env(n, .0005, .025)
    return (low * 1.1 + crack * .8)
def knock():  # martelo
    n = int(.25 * SR); t = np.arange(n) / SR
    wood = sum(np.sin(2 * np.pi * f * t) * env(n, .0005, d) for f, d in ((420, .05), (980, .025), (1700, .012)))
    return (wood + bp(rng.standard_normal(n), 800, 3000) * env(n, .0005, .01)) * .8
def ding():
    n = int(.9 * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * env(n, .001, .35) / k for k, f in enumerate((1318, 1975, 2637), 1)) * .25
import subprocess as _sp
_CROWD = None
def crowd(d):
    """Torcida gravada de verdade (SSE Library – CROWDS, CC0), em vez de ruído filtrado."""
    global _CROWD
    if _CROWD is None:
        raw = _sp.run(["ffmpeg", "-v", "quiet", "-i", "sfx/torcida-futebol.mp3", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                      capture_output=True, check=True).stdout
        _CROWD = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
        _CROWD = _CROWD / (np.sqrt(np.mean(_CROWD[6 * SR:20 * SR] ** 2)) + 1e-9)
    n = int(d * SR); i0 = int((6 + rng.random() * 20) * SR)
    x = _CROWD[i0:i0 + n].copy(); t = np.arange(len(x)) / SR
    e = np.minimum(1, t / .3) * np.minimum(1, (d - t) / .6)
    return x * e * .12
def apito():
    """Apito de árbitro: senoide aguda com trinado (sem ruído)."""
    n = int(.55 * SR); t = np.arange(n) / SR
    f = 2900 + 120 * np.sin(2 * np.pi * 28 * t)
    e = np.minimum(1, t / .02) * np.minimum(1, (.55 - t) / .08)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * e * .22
def hit():  # impacto de abertura
    return thud() * 1.2

add(sfx, hit(), 0.0, 1.0)
start = 0.0
for k, sc in enumerate(R.SCENES):
    dur = durs[k]
    _, sprites = R.build(sc, dur, R.word_times(k, dur))
    if k > 0: add(sfx, whoosh(), max(0, start - .25), .8)
    for sp in sprites:
        kind = sp.img.info.get("kind")
        tt = start + sp.t0
        if kind == "stamp": add(sfx, thud(), tt + .05, .9)
        elif kind == "gavel":
            for j in range(3): add(sfx, knock(), tt + .1 + j * .32, .9)
        elif kind == "trophy": add(sfx, ding(), tt, .8)
        elif kind == "card": add(sfx, apito(), tt, .7)
        elif kind == "whistle": add(sfx, apito(), tt, .7)
        elif sp.t0 > 0.05: add(sfx, pop(), tt, .6)
    if sc["id"] in ("gancho", "lance", "resultado", "cta"):
        add(sfx, crowd(min(dur, 4.5)), start + dur * .4, 1.0)
    start += dur

def norm(x, peak):
    return x / (np.max(np.abs(x)) + 1e-9) * peak
mix_music = norm(music, .30)          # trilha baixa, pra narração por cima
mix_sfx = norm(sfx, .55)
mix = np.tanh((mix_music + mix_sfx) * 1.2) * .9
st = np.stack([mix, mix], 1)
wavfile.write("trilha_efeitos.wav", SR, (st * 32767).astype(np.int16))
wavfile.write("so_efeitos.wav", SR, (np.stack([mix_sfx] * 2, 1) * 32767).astype(np.int16))
wavfile.write("so_trilha.wav", SR, (np.stack([mix_music] * 2, 1) * 32767).astype(np.int16))
print("ok", total)
