"""Trilha chiptune procedural + SFX 8-bit + narração com ducking.

Onda quadrada (melodia/arpejos) + triângulo (baixo) + ruído (bateria),
tom menor, andamento lento que acelera na perseguição.
Tudo sincronizado pela mesma timeline do vídeo (timeline.py).
"""
import math
import os
import wave

import numpy as np

import timeline as T

SR = T.SR


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def n(s):
    """'A4' -> número MIDI."""
    name, octv = s[:-1], int(s[-1])
    return 12 * (octv + 1) + NOTE[name]


# --------------------------------------------------------------- osciladores
def osc(kind, f, dur, duty=0.5, f_end=None, vib=0.0):
    N = max(1, int(dur * SR))
    t = np.arange(N) / SR
    if f_end is None:
        freq = np.full(N, f, np.float64)
    else:
        freq = f * (f_end / f) ** (t / max(dur, 1e-6))
    if vib:
        freq = freq * (1 + vib * np.sin(2 * np.pi * 5.5 * t))
    ph = np.cumsum(freq) / SR
    ph -= np.floor(ph)
    if kind == 'sq':
        return np.where(ph < duty, 1.0, -1.0)
    if kind == 'tri':
        return 4 * np.abs(ph - 0.5) - 1
    if kind == 'saw':
        return 2 * ph - 1
    raise ValueError(kind)


_noise_rng = np.random.RandomState(1234)


def noise(dur, step=1):
    N = max(1, int(dur * SR))
    x = _noise_rng.uniform(-1, 1, N // step + 2)
    return np.repeat(x, step)[:N]


def env(N, a=0.004, d=0.06, s=0.6, r=0.04, hold=None):
    t = np.arange(N) / SR
    dur = N / SR
    e = np.ones(N)
    ia = t < a
    e[ia] = t[ia] / a
    idd = (t >= a) & (t < a + d)
    e[idd] = 1 - (1 - s) * (t[idd] - a) / d
    e[t >= a + d] = s
    rel = t > dur - r
    e[rel] *= np.clip((dur - t[rel]) / r, 0, 1)
    return e


def lowpass(x, k):
    """média móvel (k amostras) – filtro passa-baixa barato."""
    if k <= 1:
        return x
    c = np.cumsum(np.concatenate([[0], x]))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([y, np.full(k - 1, y[-1] if len(y) else 0)])


class Bus:
    def __init__(self, dur):
        self.x = np.zeros(int(dur * SR) + SR * 2)

    def add(self, t, sig, gain=1.0):
        i = int(t * SR)
        if i < 0:
            sig = sig[-i:]
            i = 0
        j = min(len(self.x), i + len(sig))
        if j > i:
            self.x[i:j] += sig[:j - i] * gain


# --------------------------------------------------------------- instrumentos
def note_sq(m, dur, vel=1.0, duty=0.5, vib=0.0, dec=0.08, sus=0.55):
    s = osc('sq', midi(m), dur, duty, vib=vib)
    return s * env(len(s), 0.003, dec, sus, 0.03) * vel


def note_tri(m, dur, vel=1.0):
    s = osc('tri', midi(m), dur)
    return s * env(len(s), 0.003, 0.05, 0.85, 0.03) * vel


def kick(vel=1.0):
    s = osc('tri', 150, 0.16, f_end=40)
    return s * env(len(s), 0.001, 0.12, 0.0, 0.03) * vel


def snare(vel=1.0):
    s = noise(0.14, 2)
    return s * env(len(s), 0.001, 0.12, 0.0, 0.02) * vel


def hat(vel=1.0):
    s = noise(0.035, 1)
    s = s - lowpass(s, 4)
    return s * env(len(s), 0.0005, 0.03, 0.0, 0.005) * vel


# --------------------------------------------------------------- sequenciador
def bar_loop(bus, t0, t1, bpm, bars, fn, gain=1.0):
    """bars: número de compassos do padrão; fn(bus, t_start, beat_dur, bar_index) desenha 1 compasso."""
    beat = 60.0 / bpm
    t, k = t0, 0
    while t < t1 - 0.01:
        fn(bus, t, beat, k % bars, t1, gain)
        t += beat * 4
        k += 1


def clip_add(bus, t, sig, t1, gain):
    """adiciona sem ultrapassar o fim da seção (com fade curto)."""
    maxn = int((t1 - t) * SR)
    if maxn <= 0:
        return
    if len(sig) > maxn:
        sig = sig[:maxn].copy()
        f = min(len(sig), int(0.01 * SR))
        if f > 0:
            sig[-f:] *= np.linspace(1, 0, f)
    bus.add(t, sig, gain)


# ----- TÍTULO: arpejo arcade em Lá menor
def pat_title(bus, t, beat, k, t1, g):
    chords = [['A4', 'C5', 'E5', 'A5'], ['F4', 'A4', 'C5', 'F5'], ['G4', 'B4', 'D5', 'G5'], ['E4', 'G#4', 'B4', 'E5']]
    roots = ['A2', 'F2', 'G2', 'E2']
    ch = chords[k % 4]
    for i in range(16):
        m = n(ch[[0, 1, 2, 3, 2, 1, 2, 3][i % 8]])
        clip_add(bus, t + i * beat / 4, note_sq(m + (12 if i >= 12 else 0), beat / 4 * 0.9, 0.22, 0.25), t1, g)
    for i in range(4):
        clip_add(bus, t + i * beat, note_tri(n(roots[k % 4]) + (12 if i % 2 else 0), beat * 0.9, 0.5), t1, g)
        clip_add(bus, t + i * beat, (kick(0.5) if i % 2 == 0 else snare(0.25)), t1, g)


# ----- LEVEL 1: calmo mas sombrio (Am - F - Dm - E)
def pat_level1(bus, t, beat, k, t1, g):
    mel = [[('E5', 0, 1.5), ('D5', 1.5, 0.5), ('C5', 2, 1), ('A4', 3, 1)],
           [('F4', 0, 1), ('A4', 1, 1), ('C5', 2, 1.5), ('B4', 3.5, 0.5)],
           [('D5', 0, 1.5), ('C5', 1.5, 0.5), ('A4', 2, 1), ('F4', 3, 1)],
           [('E4', 0, 1), ('G#4', 1, 1), ('B4', 2, 2)]]
    roots = ['A2', 'F2', 'D2', 'E2']
    arp = [['A3', 'C4', 'E4'], ['F3', 'A3', 'C4'], ['D3', 'F3', 'A3'], ['E3', 'G#3', 'B3']]
    for (nm, st, du) in mel[k % 4]:
        clip_add(bus, t + st * beat, note_sq(n(nm), du * beat * 0.95, 0.16, 0.125, vib=0.006, dec=0.2, sus=0.5), t1, g)
    for i in range(8):
        clip_add(bus, t + i * beat / 2, note_sq(n(arp[k % 4][[0, 1, 2, 1][i % 4]]), beat / 2 * 0.7, 0.07, 0.5, dec=0.05, sus=0.3), t1, g)
    for i in range(2):
        clip_add(bus, t + i * 2 * beat, note_tri(n(roots[k % 4]), beat * 1.9, 0.5), t1, g)
    for i in range(4):
        clip_add(bus, t + i * beat + beat / 2, hat(0.12), t1, g)


# ----- TENSÃO após o puxão: drone + batida de coração
def pat_tension(bus, t, beat, k, t1, g):
    clip_add(bus, t, note_tri(n('A1'), beat * 4, 0.55), t1, g)
    for i in range(8):
        m = n('A5') if i % 2 == 0 else n('A#5')
        clip_add(bus, t + i * beat / 2, note_sq(m, beat / 2 * 0.8, 0.05 + 0.01 * k, 0.125), t1, g)
    for i in range(2):
        clip_add(bus, t + i * 2 * beat, kick(0.7), t1, g)
        clip_add(bus, t + i * 2 * beat + 0.18, kick(0.45), t1, g)


# ----- NOITE: Ré menor com eco (Dm - Bb - Gm - A)
def pat_night(bus, t, beat, k, t1, g, show=False, red=False):
    arps = [['D4', 'F4', 'A4', 'D5'], ['A#3', 'D4', 'F4', 'A#4'], ['G3', 'A#3', 'D4', 'G4'], ['A3', 'C#4', 'E4', 'A4']]
    roots = ['D2', 'A#1', 'G1', 'A1']
    ar = arps[k % 4]
    for i in range(8):
        m = n(ar[[0, 1, 2, 3, 2, 1, 2, 3][i]])
        s = note_sq(m, beat / 2 * 0.8, 0.10, 0.25, dec=0.1, sus=0.35)
        clip_add(bus, t + i * beat / 2, s, t1, g)
        clip_add(bus, t + i * beat / 2 + beat * 0.75, s * 0.4, t1, g)   # eco
        if show and not red:
            clip_add(bus, t + i * beat / 2 + beat / 4, note_sq(m + 24, beat / 4 * 0.7, 0.05, 0.125), t1, g)
    clip_add(bus, t, note_tri(n(roots[k % 4]), beat * 3.9, 0.5), t1, g)
    if red:
        clip_add(bus, t, note_sq(n(roots[k % 4]) + 6 + 24, beat * 4, 0.04, 0.5, vib=0.02, dec=0.5, sus=0.8), t1, g)
        for i in range(2):
            clip_add(bus, t + i * 2 * beat, kick(0.7), t1, g)
            clip_add(bus, t + i * 2 * beat + 0.2, kick(0.45), t1, g)


# ----- PERSEGUIÇÃO: Lá menor, baixo em colcheias, acelera
CHASE_BASS = ['A2', 'A2', 'A3', 'A2', 'C3', 'A2', 'D3', 'E3']
CHASE_LEAD = [[('E5', 0, .5), ('E5', .5, .5), ('F5', 1, .5), ('E5', 1.5, .5), ('D5', 2, .5), ('C5', 2.5, .5), ('B4', 3, 1)],
              [('C5', 0, .5), ('D5', .5, .5), ('E5', 1, 1), ('A4', 2, .5), ('B4', 2.5, .5), ('C5', 3, .5), ('B4', 3.5, .5)],
              [('A5', 0, .5), ('G5', .5, .5), ('F5', 1, .5), ('E5', 1.5, .5), ('F5', 2, .5), ('E5', 2.5, .5), ('D5', 3, .5), ('E5', 3.5, .5)],
              [('E5', 0, .25), ('F5', .25, .25), ('E5', .5, .25), ('D#5', .75, .25), ('E5', 1, 1), ('G#4', 2, 1), ('B4', 3, 1)]]


def chase_music(bus, t0, t1, tl):
    """compassos com bpm crescente (120 -> 176)."""
    t, k = t0, 0
    while t < t1 - 0.01:
        tb = tl.to_base(t)
        u = T.clamp((tb - T.CHASE_T0) / (T.CHASE_T1 - T.CHASE_T0))
        bpm = 120 + 56 * u ** 1.3
        beat = 60 / bpm
        trans = [0, 0, 3, -2][(k // 2) % 4] if k >= 8 else 0
        for i in range(8):
            clip_add(bus, t + i * beat / 2, note_tri(n(CHASE_BASS[i]) + trans, beat / 2 * 0.85, 0.6), t1, 1)
            clip_add(bus, t + i * beat / 2, hat(0.18), t1, 1)
        for i in range(4):
            clip_add(bus, t + i * beat, kick(0.7) if i % 2 == 0 else snare(0.4), t1, 1)
        octv = 12 if u > 0.7 else 0
        for (nm, st, du) in CHASE_LEAD[k % 4]:
            clip_add(bus, t + st * beat, note_sq(n(nm) + trans + octv, du * beat * 0.9, 0.13, 0.25, dec=0.05, sus=0.6), t1, 1)
        if u > 0.45:
            for i in range(16):
                clip_add(bus, t + i * beat / 4, note_sq(n(['A5', 'C6', 'E6', 'C6'][i % 4]) + trans, beat / 4 * 0.6, 0.04, 0.125), t1, 1)
        t += beat * 4
        k += 1


# --------------------------------------------------------------- SFX
def sfx_coin():
    a = note_sq(n('B5'), 0.07, 0.5, 0.5, dec=0.01, sus=1)
    b = osc('sq', midi(n('E6')), 0.4, 0.5) * np.exp(-np.arange(int(0.4 * SR)) / SR * 8) * 0.5
    return np.concatenate([a, b])


def sfx_start():
    out = []
    for m in ['A4', 'C5', 'E5', 'A5', 'C6', 'E6']:
        out.append(note_sq(n(m), 0.055, 0.4, 0.25, dec=0.01, sus=1))
    out.append(note_sq(n('A6'), 0.3, 0.4, 0.25, dec=0.25, sus=0.2))
    return np.concatenate(out)


def sfx_step():
    s = noise(0.05, 3)
    s = lowpass(s, 6) * env(len(s), 0.001, 0.04, 0, 0.005)
    th = osc('tri', 90, 0.06, f_end=50) * env(int(0.06 * SR), 0.001, 0.05, 0, 0.005)
    out = th * 0.4
    out[:len(s)] += s * 0.5
    return out


def sfx_splash():
    d = 1.1
    s = noise(d, 1)
    N = len(s)
    e = np.exp(-np.arange(N) / SR * 4)
    lo = lowpass(s, 12) * 1.6
    out = (s * 0.35 + lo) * e
    for k in range(6):
        b = osc('sq', 600 + k * 130, 0.06, 0.5, f_end=1200 + k * 200) * env(int(0.06 * SR), 0.002, 0.05, 0, 0.005) * 0.12
        i = int((0.15 + k * 0.1) * SR)
        out[i:i + len(b)] += b[:max(0, N - i)]
    return out * 0.8


def sfx_alert():
    a = note_sq(n('A6'), 0.08, 0.5, 0.5, dec=0.01, sus=1)
    gap = np.zeros(int(0.04 * SR))
    b = note_sq(n('A6'), 0.08, 0.5, 0.5, dec=0.01, sus=1)
    sw = osc('sq', 300, 0.35, 0.5, f_end=1600) * env(int(0.35 * SR), 0.005, 0.3, 0.3, 0.05) * 0.3
    x = np.concatenate([a, gap, b, gap, a, gap])
    out = np.zeros(max(len(x), len(sw)))
    out[:len(x)] += x
    out[:len(sw)] += sw
    return out


def sfx_patience_drop():
    s = osc('sq', 1200, 1.0, 0.5, f_end=70) * env(int(1.0 * SR), 0.005, 0.2, 0.7, 0.1)
    return s * 0.35


def sfx_crack():
    s = noise(0.05, 1) * env(int(0.05 * SR), 0.0005, 0.04, 0, 0.005)
    out = np.zeros(int(0.5 * SR))
    out[:len(s)] += s * 1.0
    for k, dt in enumerate([0.03, 0.07, 0.12, 0.2]):
        c = noise(0.015, 1) * env(int(0.015 * SR), 0.0005, 0.012, 0, 0.002) * (0.7 - k * 0.12)
        i = int(dt * SR)
        out[i:i + len(c)] += c
    th = osc('sq', 160, 0.12, 0.5, f_end=60) * env(int(0.12 * SR), 0.001, 0.1, 0, 0.01) * 0.5
    out[:len(th)] += th
    return out


def sfx_jumpscare():
    d = 1.5
    N = int(d * SR)
    t = np.arange(N) / SR
    s = noise(d, 1) * 0.6
    for det in (1.0, 1.06, 0.94, 1.5):
        s += osc('sq', 2400 * det, d, 0.5, f_end=260 * det) * 0.35
    s += osc('saw', 90, d, f_end=45) * 0.6
    e = np.where(t < 0.02, t / 0.02, np.exp(-(t - 0.02) * 1.8))
    s = s * e
    return np.tanh(s * 1.6) * 0.95


def sfx_lamp_off():
    a = note_sq(n('A2'), 0.07, 0.45, 0.5, dec=0.05, sus=0.2)
    c = noise(0.02, 1) * env(int(0.02 * SR), 0.0005, 0.015, 0, 0.003) * 0.5
    out = np.zeros(len(a) + int(0.05 * SR))
    out[:len(c)] += c
    out[:len(a)] += a
    z = osc('sq', 1800, 0.06, 0.5, f_end=600) * 0.08 * env(int(0.06 * SR), 0.001, 0.05, 0, 0.005)
    out[:len(z)] += z
    return out


def sfx_laugh():
    out = []
    for f in (620, 0, 540, 0, 600, 0, 500):
        if f == 0:
            out.append(np.zeros(int(0.05 * SR)))
        else:
            out.append(osc('sq', f, 0.07, 0.25, f_end=f * 0.85) * env(int(0.07 * SR), 0.003, 0.05, 0.3, 0.01) * 0.25)
    return np.concatenate(out)


def sfx_heart():
    return np.concatenate([note_sq(n('E6'), 0.06, 0.25, 0.25, dec=0.01, sus=1),
                           note_sq(n('A6'), 0.14, 0.25, 0.25, dec=0.12, sus=0.2)])


def sfx_glitch(d=0.25):
    s = noise(d, 8) * 0.5
    s *= (np.sin(np.arange(len(s)) / SR * 2 * np.pi * 37) > 0)
    return s * env(len(s), 0.002, d * 0.8, 0.3, 0.02) * 0.45


def sfx_whoosh():
    s = noise(0.3, 1)
    s = s - lowpass(s, 3)
    return s * np.sin(np.linspace(0, np.pi, len(s))) * 0.3


def sfx_splash_small():
    return sfx_splash()[:int(0.5 * SR)] * 0.4


def sfx_blip(m, d=0.1, v=0.3):
    return note_sq(m, d, v, 0.5, dec=0.05, sus=0.5)


def gameover_jingle():
    seq = [('E5', .18), ('D#5', .18), ('D5', .18), ('C#5', .36), ('C5', .18), ('B4', .18), ('A#4', .18), ('A4', .9)]
    out = []
    for nm, d in seq:
        a = note_sq(n(nm), d * 0.95, 0.28, 0.5, vib=0.01 if d > 0.5 else 0, dec=0.1, sus=0.6)
        b = note_tri(n(nm) - 24, d * 0.95, 0.45)
        out.append(a + b)
    return np.concatenate(out)


# --------------------------------------------------------------- render
def render(tl, out_mix, out_music=None):
    R = tl.to_real
    dur = tl.duration
    mus = Bus(dur)
    sfx = Bus(dur)

    # música por seção (início/fim em tempo base -> real)
    def sec(b0, b1, bpm, fn, gain=1.0, **kw):
        if kw:
            f = lambda bus, t, beat, k, t1, g: fn(bus, t, beat, k, t1, g, **kw)
        else:
            f = fn
        bar_loop(mus, R(b0), R(b1), bpm, 4, f, gain)

    sec(0.0, 3.6, 132, pat_title)
    sec(5.0, 19.5, 92, pat_level1, 0.65)
    sec(20.4, 25.0, 76, pat_tension)
    sec(25.0, 27.6, 72, pat_night, 0.75)
    sec(27.6, 31.1, 72, pat_night, 0.8, show=True)
    sec(31.1, 35.0, 72, pat_night, 0.9, show=True, red=True)
    chase_music(mus, R(35.0), R(52.0), tl)
    mus.add(R(58.0), gameover_jingle(), 1.0)
    sec(60.6, 63.0, 92, pat_level1, 0.7)
    # aviso: pad suave
    t0, t1 = R(63.0), dur
    d = t1 - t0
    pad = (osc('tri', midi(n('A2')), d) * 0.35 + osc('tri', midi(n('E3')), d) * 0.2 + osc('sq', midi(n('C4')), d, 0.125) * 0.03)
    tt = np.arange(len(pad)) / SR
    pad *= np.clip(tt / 1.0, 0, 1) * np.clip((d - tt) / 1.5, 0, 1) * (0.8 + 0.2 * np.sin(tt * 2 * np.pi * 0.5))
    mus.add(t0, pad, 0.8)
    # drone baixo no preto pós-jumpscare
    t0, t1 = R(53.5), R(58.0)
    d = t1 - t0
    hum = osc('tri', 55, d) * 0.25
    tt = np.arange(len(hum)) / SR
    hum *= np.clip(tt / 0.5, 0, 1) * np.clip((d - tt) / 0.3, 0, 1)
    mus.add(t0, hum)

    # SFX
    sfx.add(R(0.0), sfx_glitch(0.35), 0.8)
    sfx.add(R(3.6), sfx_coin(), 0.9)
    sfx.add(R(4.05), sfx_start(), 0.8)
    sfx.add(R(4.55), sfx_glitch(0.2), 0.6)
    for t in (17.0, 17.9, 18.4):      # risadas
        sfx.add(R(t), sfx_laugh(), 0.8)
    cap_stop_t = 7.0 + (330 - 196) / 34
    sfx.add(R(cap_stop_t + 0.2), sfx_heart(), 0.9)
    for k in range(int((15.3 + 3.0 - 15.3) * 4)):   # passos dos visitantes chegando
        sfx.add(R(15.3 + k * 0.25), sfx_step(), 0.35)
    sfx.add(R(19.25), sfx_whoosh(), 0.8)
    sfx.add(R(19.5), sfx_alert(), 1.0)
    sfx.add(R(19.5), sfx_glitch(0.6), 0.7)
    sfx.add(R(19.6), sfx_patience_drop(), 0.8)
    sfx.add(R(20.4), sfx_blip(n('A2'), 0.25, 0.5), 1.0)
    sfx.add(R(24.0), sfx_splash(), 1.0)
    sfx.add(R(25.0), sfx_glitch(0.4), 0.6)
    for k in range(5):                # postes acendendo
        sfx.add(R(27.0 + k * 0.16), sfx_blip(n('E5') + k * 2, 0.06, 0.18), 1.0)
    sfx.add(R(27.6), sfx_whoosh(), 0.7)
    sfx.add(R(31.0), sfx_glitch(0.35), 0.8)
    sfx.add(R(31.1), sfx_alert()[:int(0.25 * SR)], 0.6)
    sfx.add(R(31.5), sfx_splash_small(), 0.8)
    sfx.add(R(34.7), sfx_glitch(0.35), 0.8)
    for t in T.step_times():
        sfx.add(R(t), sfx_step(), 0.45)
    for t in T.lamp_events():
        sfx.add(R(t), sfx_lamp_off(), 0.8)
    sfx.add(R(T.STICK_HIT - 0.3), sfx_whoosh(), 0.9)
    sfx.add(R(T.STICK_HIT), sfx_crack(), 1.2)
    sfx.add(R(40.6), sfx_splash_small(), 0.0)
    sfx.add(R(52.0), sfx_jumpscare(), 1.25)
    sfx.add(R(53.4), noise(0.3, 1) * np.linspace(0.6, 0, int(0.3 * SR)), 0.6)
    for k in range(6):                # CONTINUE? 5..0
        sfx.add(R(52.0 + 2.6 + k * 0.6), sfx_blip(n('A4') - k, 0.12, 0.3), 1.0)
    sfx.add(R(58.0), sfx_glitch(0.3), 0.6)
    for k in range(7):                # paciência recarregando
        sfx.add(R(59.2 + k * 0.5), sfx_blip(n('C5') + k * 2, 0.05, 0.12), 1.0)
    sfx.add(R(63.0), sfx_glitch(0.25), 0.4)

    music = mus.x * 0.55
    effects = sfx.x * 0.7
    N = int(dur * SR)
    music, effects = music[:N], effects[:N]

    voice = np.zeros(N)
    if tl.narr is not None:
        x = tl.narr
        if tl.line_audio:
            for (a, b), r in zip(tl.line_audio, tl.real_starts):
                seg = x[int(max(0, a - 0.04) * SR):int((b + 0.12) * SR)]
                i = int(r * SR)
                j = min(N, i + len(seg))
                voice[i:j] += seg[:j - i]
        else:
            i = int(tl.real_starts[0] * SR)
            j = min(N, i + len(x))
            voice[i:j] += x[:j - i]
        pk = np.abs(voice).max()
        if pk > 0:
            voice *= 0.9 / pk
        # ducking: envelope da voz suavizado
        e = lowpass(np.abs(voice), int(0.05 * SR))
        e = lowpass(np.minimum(1, e / (e.max() * 0.25 + 1e-9)), int(0.25 * SR))
        duck = 1 - 0.6 * e
        music *= duck
        effects *= 1 - 0.3 * e

    bed = music + effects
    if out_music:
        write_wav(out_music, limit(bed))
    mix = bed + voice * 1.0
    write_wav(out_mix, limit(mix))
    return out_mix


def limit(x):
    pk = np.abs(x).max() + 1e-9
    x = x / pk * 1.15
    x = np.tanh(x) / np.tanh(1.15) * 0.93
    return x


def write_wav(path, x):
    st = np.stack([x, x], 1)
    data = (np.clip(st, -1, 1) * 32767).astype('<i2').tobytes()
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)


if __name__ == '__main__':
    tl = T.Timeline()
    root = T.ROOT
    os.makedirs(os.path.join(root, 'output'), exist_ok=True)
    render(tl, os.path.join(root, 'output', 'trilha_mix.wav'), os.path.join(root, 'output', 'trilha_sem_narracao.wav'))
    print('ok', tl.mode)
