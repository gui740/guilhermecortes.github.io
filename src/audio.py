# Trilha folk de tensão + efeitos sonoros, 100% sintetizados (livres de direitos), e mixagem final.
# Uso: python3 src/audio.py  -> assets/audio/mix_reel.wav, mix_gancho_{A,B,C}.wav
import json, os, subprocess
import numpy as np
from scipy import signal
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rock import rock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
rng = np.random.default_rng(11)
D = json.load(open(f'{ROOT}/src/timeline_dump.json'))

def t_(n): return np.arange(int(n * SR)) / SR
def env(n, a, r):  # ataque/decay exponencial
    t = t_(n); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
def lp(x, f, o=2): b, a = signal.butter(o, f / (SR / 2)); return signal.lfilter(b, a, x)
def hp(x, f, o=2): b, a = signal.butter(o, f / (SR / 2), 'high'); return signal.lfilter(b, a, x)
def bp(x, f1, f2, o=2): b, a = signal.butter(o, [f1 / (SR / 2), f2 / (SR / 2)], 'band'); return signal.lfilter(b, a, x)
def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
def place(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += x * g

IR = rng.normal(0, 1, int(2.8 * SR)) * np.exp(-t_(2.8) / 0.7); IR = lp(IR, 5000); IR /= np.sqrt(np.sum(IR ** 2))
def reverb(x, wet=0.5): return (1 - wet) * x + wet * signal.fftconvolve(x, IR)[:len(x)] * 3

# ---------------- trilha ----------------
def music(L, intensity):
    t = t_(L); out = np.zeros_like(t)
    # drone: Ré grave + Lá, serrilhado detunado, filtro respirando
    for f, g in [(36.71, 0.5), (73.42, 0.6), (110.0, 0.35), (73.6, 0.4)]:
        ph = 2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.07 * t)
        saw = 2 * ((f * t + 0.1 * np.sin(2 * np.pi * 0.05 * t)) % 1) - 1
        out += g * (0.6 * np.sin(ph) + 0.25 * saw)
    out = lp(out, 420) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t))
    # tambor grave (bumbo de couro) ~ 72 bpm, padrão folk "1 . . (e) 3 ."
    beat = 60 / 72; n = int(L / beat) + 1
    for k in range(n):
        for off, g in [(0, 1.0), (0.75, 0.55), (2, 0.8)] if k % 4 == 0 else [(0, 0.7)] if k % 2 == 0 else []:
            at = (k + off) * beat
            if at >= L: continue
            g *= intensity(at)
            dur = 0.9; tt = t_(dur)
            f = 48 + 70 * np.exp(-tt / 0.05)
            hit = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.32)
            hit += 0.25 * lp(rng.normal(0, 1, len(tt)), 900) * np.exp(-tt / 0.03)
            place(out, hit, at, 0.9 * g)
    # canto distante: vozes com formantes ("ah"/"oh"), vibrato, muito reverb
    notes = [(1.0, 146.83, 2.6), (5.2, 174.61, 2.2), (9.0, 130.81, 2.8), (13.5, 146.83, 2.4), (18.0, 155.56, 2.6), (22.4, 146.83, 3.0), (27.0, 130.81, 3.2)]
    for at, f0, dur in notes:
        if at >= L: continue
        tt = t_(dur); vib = 1 + 0.012 * np.sin(2 * np.pi * 5.2 * tt)
        ph = np.cumsum(f0 * vib) / SR
        src = sum(np.sin(2 * np.pi * h * ph) / h for h in range(1, 18))
        v = bp(src, 650, 1150) * 0.9 + bp(src, 280, 520) * 0.6 + bp(src, 2300, 3000) * 0.15
        e = np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 1.5
        voice = v * e
        voice += 0.6 * np.roll(v * e, int(0.013 * SR))  # segunda voz levemente atrasada
        place(out, voice, at, 0.22)
    out = reverb(out, 0.35)
    return out

# ---------------- efeitos ----------------
def whoosh(d=0.45):
    n = rng.normal(0, 1, int(d * SR)); tt = t_(d)
    sweep = np.zeros_like(n)
    for i, (f1, f2) in enumerate([(200, 500), (500, 1200), (1200, 3200)]):
        w = np.clip(1 - np.abs(tt / d - (0.3 + 0.2 * i)) * 3, 0, 1)
        sweep += bp(n, f1, f2) * w
    e = np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 2
    return sweep * e * 0.9
def pop():
    tt = t_(0.09); f = 380 + 700 * np.exp(-tt / 0.012)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.03) * 0.8
def boom():  # impacto nas revelações de título
    tt = t_(1.2); f = 40 + 60 * np.exp(-tt / 0.08)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.45) + 0.2 * lp(rng.normal(0, 1, len(tt)), 400) * np.exp(-tt / 0.1))
def wind(d):
    n = rng.normal(0, 1, int(d * SR)); tt = t_(d)
    w = bp(n, 250, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * tt + 1)) + bp(n, 900, 2200) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.21 * tt))
    fade = np.minimum(1, np.minimum(tt / 0.25, (d - tt) / 0.25))
    return w * fade
def fire(d):
    tt = t_(d); out = lp(rng.normal(0, 1, len(tt)), 600) * 0.25
    for _ in range(int(d * 28)):
        at = rng.uniform(0, d - 0.02); c = hp(rng.normal(0, 1, int(0.012 * SR)), 1500) * np.exp(-t_(0.012) / 0.003)
        i = int(at * SR); out[i:i + len(c)] += c * rng.uniform(0.3, 1.2)
    fade = np.minimum(1, np.minimum(tt / 0.2, (d - tt) / 0.2))
    return out * fade
def bell():
    tt = t_(3.0); out = np.zeros_like(tt)
    for r, g, dec in [(1, 1, 1.4), (2.4, 0.5, 0.9), (2.98, 0.35, 0.7), (4.1, 0.25, 0.5), (5.4, 0.15, 0.35)]:
        out += g * np.sin(2 * np.pi * 392 * r * tt) * np.exp(-tt / dec)
    return reverb(out * 0.5, 0.4)
def static(d=0.25):
    tt = t_(d); return hp(rng.normal(0, 1, len(tt)), 2000) * np.exp(-tt / 0.12) * 0.6

def norm_to(x, ref_db, rel_db):
    return x * 10 ** ((ref_db + rel_db - rms_db(x)) / 20)

def load_wav(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def save(p, x):
    x = np.clip(x, -1, 1)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', p], input=(x * 32767).astype(np.int16).tobytes())

def build(L, voice_path, blocks, transitions, extra_whoosh, is_full):
    voice = load_wav(voice_path); voice = np.pad(voice, (0, max(0, int(L * SR) - len(voice))))[:int(L * SR)]
    vref = rms_db(voice[np.abs(voice) > 0.02])  # nível da fala ativa
    # intensidade da trilha cresce até o nº 1
    inten = (lambda at: 0.7 + 0.3 * min(1, at / 27)) if is_full else (lambda at: 0.8)
    if is_full:
        sh = next(b for b in blocks if b['scene'] == 'share')
        nxt = [b for b in blocks if b['scene'] == 'i'][0]
        marks = {'breakdown': (sh['from'], nxt['from']), 'big': nxt['from'], 'end': D['loop']}
    else:
        marks = {'end': L + 1}
    mus = rock(L, marks)
    mus = norm_to(mus, vref, -18)               # trilha -18 dB em relação à voz
    # sidechain leve: abaixa 3 dB quando há voz
    ve = np.convolve(np.abs(voice), np.ones(2400) / 2400, 'same'); duck = 1 - 0.3 * np.clip(ve / (ve.max() * 0.25), 0, 1)
    mus *= duck
    fx = np.zeros(int(L * SR))
    W = whoosh(); P = pop(); Bm = boom()
    for at in [tr['at'] for tr in transitions] + extra_whoosh:
        place(fx, W, max(0, at - 0.22), 1.0)
    for b in blocks:
        for t in b['toks']:
            if t['hl']: place(fx, P, t['at'], 0.9)
        for g in b.get('nums', []):
            if g['k'] == 'star': place(fx, Bm, g['at'], 1.0)
            else: place(fx, P, g['at'], 0.7)
        # ambiência curta por bloco
        d = b['to'] - b['from']
        lay = ' '.join(b.get('layers', []))
        if 'flames' in lay: place(fx, fire(d) * 0.5, b['from'])
        elif b.get('scene') in ('hook', 'e', 'a', 'share', 'two', None): place(fx, wind(d) * 0.35, b['from'])
    if is_full:
        place(fx, bell(), 21.10, 0.8); place(fx, bell(), 25.15, 0.6)
        place(fx, static(), 21.10, 0.9)
    fx = norm_to(fx, vref, -14) if rms_db(fx) > -80 else fx  # efeitos bem abaixo da voz
    mix = voice + mus + fx
    # loop: fade curtíssimo nas pontas para não estalar
    f = int(0.01 * SR); mix[:f] *= np.linspace(0, 1, f); mix[-f:] *= np.linspace(1, 0, f)
    print(f'voz {vref:.1f} dB | trilha {rms_db(mus):.1f} dB | fx {rms_db(fx):.1f} dB')
    return mix

out = build(D['total'], f'{ROOT}/assets/audio/narracao.wav', D['blocks'], D['transitions'], [0.15, D['loop'], D['loop'] + 0.5], True)
save(f'{ROOT}/assets/audio/mix_reel.wav', out)
for k in 'ABC':
    v = f'{ROOT}/assets/audio/narracao.wav' if k == 'A' else f'{ROOT}/assets/audio/narracao_{k}.wav'
    hb = [dict(b, scene='hook', layers=['flames'] if i == 0 else []) for i, b in enumerate(D['hooks'][k])]
    save(f'{ROOT}/assets/audio/mix_gancho_{k}.wav', build({'A': 4.1, 'B': 3.95, 'C': 3.9}[k], v, hb, [], [0.15], False))
