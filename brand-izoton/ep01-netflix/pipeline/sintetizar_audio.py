"""Trilha e efeitos 100% sintetizados para o Brand by Izoton.

Trilha: ambient eletrônico retrô-sci-fi, pulso lento, pad analógico desafinado, sub grave, arpejo esparso,
chiado de fita bem baixo. Gerada em blocos para ter a duração pedida e variar ao longo do episódio.
Efeitos: famílias com variações (click, bip, geiger, crt_on, crt_off, sweep, carimbo, papel, plin, registradora, tecla).

Uso: python3 sintetizar_audio.py <dir_saida> <duracao_trilha_s>
"""
import os, sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(1977)


def save(path, x, stereo=True):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1 and stereo:
        x = np.stack([x, x], 1)
    peak = np.max(np.abs(x)) or 1
    x = x / peak * 0.89
    pcm = (x * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2 if stereo else 1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def env(n, a=0.005, r=0.1, sus=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    rel = np.exp(-t / max(r, 1e-4))
    return e * rel if sus is None else e * np.where(t < sus, 1, np.exp(-(t - sus) / r))


def lp(x, cutoff):
    """passa-baixa de 1 polo (aceita cutoff variável no tempo)."""
    c = np.broadcast_to(np.asarray(cutoff, dtype=np.float64), x.shape)
    a = np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def lp_fast(x, cutoff):
    """passa-baixa de 1 polo com cutoff fixo, vetorizado via scipy se houver."""
    try:
        from scipy.signal import lfilter
        a = np.exp(-2 * np.pi * cutoff / SR)
        return lfilter([1 - a], [1, -a], x)
    except Exception:
        return lp(x, cutoff)


def hp_fast(x, cutoff):
    return x - lp_fast(x, cutoff)


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * f + phase) % 1) - 1


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- trilha
def trilha(dur):
    bpm = 60.0
    beat = 60 / bpm
    bar = 4 * beat
    n = int(dur * SR) + SR * 2
    L = np.zeros(n); R = np.zeros(n)
    # progressão modal em ré menor: Dm9 · Bbmaj7 · Fadd9 · C6/E · Gm9 · Dm/A
    chords = [[50, 57, 60, 64, 65], [46, 53, 57, 62, 65], [41, 53, 57, 60, 67], [40, 52, 55, 60, 64],
              [43, 55, 58, 62, 65], [45, 50, 57, 60, 64]]
    bars = int(np.ceil(dur / bar))
    chord_len = 2  # compassos por acorde
    for ci in range(int(np.ceil(bars / chord_len))):
        notes = chords[ci % len(chords)]
        t0 = int(ci * chord_len * bar * SR)
        m = int(chord_len * bar * SR) + int(1.5 * SR)
        if t0 >= n:
            break
        m = min(m, n - t0)
        pad_l = np.zeros(m); pad_r = np.zeros(m)
        for k, nt in enumerate(notes[1:]):
            f = mtof(nt)
            pad_l += saw(f * 0.997, m, rng.random()) + saw(f * 1.004, m, rng.random())
            pad_r += saw(f * 1.003, m, rng.random()) + saw(f * 0.995, m, rng.random())
        e = env(m, a=1.4, r=1.2, sus=chord_len * bar)
        # brilho do filtro varia lentamente ao longo do episódio
        bright = 650 + 450 * np.sin(2 * np.pi * ci / 11.0) ** 2
        pad_l = lp_fast(lp_fast(pad_l, bright), bright) * e * 0.05
        pad_r = lp_fast(lp_fast(pad_r, bright), bright) * e * 0.05
        L[t0:t0 + m] += pad_l; R[t0:t0 + m] += pad_r
        # sub grave sustentado
        sub = np.sin(2 * np.pi * mtof(notes[0] - 12) * np.arange(m) / SR) * env(m, a=0.8, r=1.0, sus=chord_len * bar) * 0.16
        L[t0:t0 + m] += sub; R[t0:t0 + m] += sub
    # pulso lento: um "batimento" grave e abafado por tempo
    for b in range(int(dur / beat)):
        t0 = int(b * beat * SR)
        m = int(0.45 * SR)
        if t0 + m > n:
            break
        t = np.arange(m) / SR
        f = 58 * np.exp(-t * 9) + 41
        k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * (0.22 if b % 4 == 0 else 0.13)
        L[t0:t0 + m] += k; R[t0:t0 + m] += k
    # arpejo esparso de "terminal", a cada 2 compassos em parte do tempo
    for b in range(0, bars, 2):
        if rng.random() < 0.45:
            continue
        notes = chords[(b // chord_len) % len(chords)]
        for s in range(8):
            if rng.random() < 0.35:
                continue
            t0 = int((b * bar + s * beat / 2) * SR)
            m = int(0.35 * SR)
            if t0 + m > n:
                break
            f = mtof(notes[(s * 3) % len(notes)] + 24)
            t = np.arange(m) / SR
            tone = (np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t)) * np.exp(-t * 11) * 0.035
            tone = lp_fast(tone, 2500)
            pan = rng.random()
            L[t0:t0 + m] += tone * (1 - pan); R[t0:t0 + m] += tone * pan
            # eco
            d = int(beat * 0.75 * SR)
            if t0 + d + m < n:
                L[t0 + d:t0 + d + m] += tone * pan * 0.4; R[t0 + d:t0 + d + m] += tone * (1 - pan) * 0.4
    # chiado de fita
    hiss = lp_fast(rng.standard_normal(n), 6000) * 0.004
    L += hiss; R += lp_fast(rng.standard_normal(n), 6000) * 0.004
    # fade de entrada e saída
    f_in = np.minimum(1, np.arange(n) / (3 * SR)); f_out = np.minimum(1, (n - np.arange(n)) / (5 * SR))
    out = np.stack([L * f_in * f_out, R * f_in * f_out], 1)[: int(dur * SR)]
    return out


# ---------------------------------------------------------------- efeitos
def fx_click(v):
    m = int(0.06 * SR); t = np.arange(m) / SR
    x = rng.standard_normal(m) * np.exp(-t * (300 + 80 * v)) + np.sin(2 * np.pi * (1800 + 300 * v) * t) * np.exp(-t * 200) * 0.6
    return hp_fast(x, 700)


def fx_bip(v):
    m = int(0.14 * SR); t = np.arange(m) / SR
    f = [880, 1175, 1320, 990][v % 4]
    return np.sin(2 * np.pi * f * t) * env(m, 0.003, 0.05) * 0.8


def fx_geiger(v):
    m = int((0.9 + 0.3 * v) * SR); x = np.zeros(m)
    rate = np.linspace(8, 45, m) if v % 2 == 0 else np.linspace(40, 6, m)
    t = 0
    while t < m:
        k = int(0.004 * SR)
        if t + k < m:
            x[t:t + k] += rng.standard_normal(k) * np.exp(-np.arange(k) / (0.0006 * SR))
        t += int(SR / rate[t] * rng.exponential(1.0)) + 1
    return hp_fast(x, 1500) * 0.7


def fx_crt_on(v):
    m = int(0.55 * SR); t = np.arange(m) / SR
    whine = np.sin(2 * np.pi * (15734 / 4) * t) * 0.05 * np.minimum(1, t * 6)
    pop = rng.standard_normal(m) * np.exp(-t * 25) * 0.9
    hum = np.sin(2 * np.pi * 60 * t) * 0.25 * np.minimum(1, t * 4)
    return hp_fast(pop, 300) + whine + hum * np.exp(-t * 3)


def fx_crt_off(v):
    m = int(0.7 * SR); t = np.arange(m) / SR
    thunk = np.sin(2 * np.pi * (90 * np.exp(-t * 6) + 40) * t) * np.exp(-t * 12)
    zap = rng.standard_normal(m) * np.exp(-t * 18) * 0.5
    whine = np.sin(2 * np.pi * (3900 * np.exp(-t * 4)) * t) * np.exp(-t * 5) * 0.08
    return thunk + hp_fast(zap, 1200) + whine


def fx_sweep(v):
    m = int((0.6 + 0.2 * v) * SR); t = np.arange(m) / SR
    x = rng.standard_normal(m)
    cut = np.linspace(400, 5000, m) if v % 2 == 0 else np.linspace(5000, 500, m)
    y = lp(x, cut) * np.sin(np.pi * t / t[-1]) ** 2
    return y * 1.5


def fx_carimbo(v):
    m = int(0.35 * SR); t = np.arange(m) / SR
    thud = np.sin(2 * np.pi * (110 * np.exp(-t * 20) + 55) * t) * np.exp(-t * 18)
    snap = hp_fast(rng.standard_normal(m), 2000) * np.exp(-t * 90) * 0.6
    return thud + snap


def fx_papel(v):
    m = int((0.45 + 0.1 * v) * SR); t = np.arange(m) / SR
    x = rng.standard_normal(m) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * (7 + v) * t)))
    x = hp_fast(lp_fast(x, 6000), 1200)
    return x * np.sin(np.pi * t / t[-1]) * 0.8


def fx_plin(v):
    m = int(0.9 * SR); t = np.arange(m) / SR
    f = [1568, 1760, 2093, 1319][v % 4]
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)) * np.exp(-t * 4.5) * 0.6


def fx_registradora(v):
    m = int(0.6 * SR); x = np.zeros(m)
    for k, d in enumerate([0, 0.07, 0.13, 0.31]):
        s = int(d * SR); seg = fx_click(k)
        x[s:s + len(seg)] += seg[: m - s] * (0.7 if k < 3 else 1)
    t = np.arange(m) / SR
    bell = np.sin(2 * np.pi * 2400 * t) * np.exp(-(t - 0.31).clip(0) * 9) * (t > 0.31) * 0.4
    return x + bell


def fx_tecla(v):
    m = int(0.05 * SR); t = np.arange(m) / SR
    return hp_fast(rng.standard_normal(m), 2500 + 300 * v) * np.exp(-t * 160)


FX = {"click": fx_click, "bip": fx_bip, "geiger": fx_geiger, "crt_on": fx_crt_on, "crt_off": fx_crt_off,
      "sweep": fx_sweep, "carimbo": fx_carimbo, "papel": fx_papel, "plin": fx_plin,
      "registradora": fx_registradora, "tecla": fx_tecla}

if __name__ == "__main__":
    out = sys.argv[1]; dur = float(sys.argv[2])
    os.makedirs(os.path.join(out, "fx"), exist_ok=True)
    for name, fn in FX.items():
        for v in range(4):
            save(os.path.join(out, "fx", f"{name}_{v}.wav"), fn(v), stereo=False)
    print("efeitos ok", flush=True)
    save(os.path.join(out, "trilha.wav"), trilha(dur))
    print("trilha ok")
