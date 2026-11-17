"""Efeitos sonoros sintetizados + mixagem final (voz, trilha com ducking, SFX)."""
import json, os, sys
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets", "audio")
SR = 48000
rng = np.random.default_rng(11)
VO = 0.4


def env(n, a, r, shape=2.0):
    t = np.linspace(0, 1, n)
    e = np.minimum(1, t / max(a, 1e-4)) * np.clip((1 - t) / max(r, 1e-4), 0, 1) ** shape
    return e


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def lp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def norm(x, peak=0.9):
    return x / (np.abs(x).max() + 1e-9) * peak


# ---------------- efeitos
def click():
    n = int(0.12 * SR)
    out = np.zeros(n)
    for off, f, amp in [(0, 2600, 1.0), (int(0.028 * SR), 1900, 0.6)]:
        m = int(0.03 * SR)
        t = np.arange(m) / SR
        s = (np.sin(2 * np.pi * f * t) * 0.5 + rng.normal(0, 1, m)) * np.exp(-t * 260)
        out[off:off + m] += amp * hp(s, 600)
    return norm(out, 0.8)


def whoosh(dur=0.9):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    t = np.linspace(0, 1, n)
    y = np.zeros(n)
    hop = 512
    for i in range(0, n, hop):
        fc = 300 + 3200 * np.sin(np.pi * t[i]) ** 2
        seg = x[max(0, i - 2048):i + hop]
        f = bp(seg, fc * 0.6, min(fc * 1.6, 20000))
        y[i:i + hop] = f[-min(hop, n - i):]
    e = np.sin(np.pi * t) ** 1.6
    return norm(y * e, 0.8)


def rip(dur=0.55):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    crack = (rng.random(n) < 0.012).astype(float) * rng.uniform(0.5, 1.5, n)
    crack = np.convolve(crack, np.exp(-np.arange(200) / 25), "same")
    am = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * (60 + 140 * t / dur) * t))
    y = bp(x * am, 900, 7000) * 0.6 + bp(crack * x, 1500, 9000) * 1.2
    y *= env(n, 0.04, 0.5, 1.5)
    return norm(y, 0.85)


def creak(dur=1.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rate = 18 + 30 * np.sin(np.pi * t / dur) + 8 * np.sin(2 * np.pi * 3.1 * t)
    ph = np.cumsum(rate) / SR
    pulses = np.zeros(n)
    idx = np.where(np.diff(np.floor(ph)) > 0)[0]
    pulses[idx] = rng.uniform(0.6, 1.0, len(idx))
    y = np.zeros(n)
    for f, q in [(420, 18), (780, 22), (1350, 25), (2100, 30)]:
        b, a = signal.iirpeak(f / (SR / 2), q)
        y += signal.lfilter(b, a, pulses)
    y = y + 0.15 * bp(rng.normal(0, 1, n), 300, 2500) * (pulses.cumsum() % 2)
    y *= env(n, 0.1, 0.3)
    return norm(y, 0.8)


def step():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (85 - 40 * t) * t) * np.exp(-t * 22)
    scuff = bp(rng.normal(0, 1, n), 400, 3000) * np.exp(-t * 60) * 0.35
    return norm(thump + scuff, 0.9)


def breath(dur=1.0):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    x = rng.normal(0, 1, n)
    y = bp(x, 350, 1800, 2)
    b, a = signal.iirpeak(900 / (SR / 2), 4)
    y = y + 0.6 * signal.lfilter(b, a, x) * 0.05
    e = np.sin(np.pi * np.clip(t / 0.42, 0, 1)) ** 2 * 0.8 + np.sin(np.pi * np.clip((t - 0.5) / 0.5, 0, 1)) ** 2
    y = lp(y * e, 2200)  # abafado (máscara)
    return norm(y, 0.8)


def place(buf, x, t, gain_db, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[1]:
        return
    x = x[: buf.shape[1] - i] * (10 ** (gain_db / 20))
    l = np.sqrt(0.5 * (1 - pan))
    r = np.sqrt(0.5 * (1 + pan))
    buf[0, i:i + len(x)] += x * l * 1.41
    buf[1, i:i + len(x)] += x * r * 1.41


if __name__ == "__main__":
    narr_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(A, "narracao.wav")
    out_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(A, "mix_final.wav")
    total = float(sys.argv[3]) if len(sys.argv) > 3 else json.load(open(os.path.join(A, "music_edit.json")))["total"]
    music_only = "--music-only" in sys.argv
    ev = json.load(open(os.path.join(A, "events.json")))
    N = int(total * SR)
    meter = pyln.Meter(SR)

    # voz
    v, _ = sf.read(narr_file)
    if v.ndim > 1:
        v = v.mean(1)
    voice = np.zeros(N)
    i0 = int(VO * SR)
    voice[i0:i0 + len(v)] = v[: N - i0]
    vl = meter.integrated_loudness(np.stack([v, v], 1))  # loudness medida como estéreo (voz no centro)
    voice *= 10 ** ((-16 - vl) / 20)

    # trilha
    m, sr2 = sf.read(os.path.join(A, "music_edit.wav"))
    assert sr2 == SR
    m = m.T[:, :N]
    if m.shape[1] < N:
        m = np.pad(m, ((0, 0), (0, N - m.shape[1])))
    ml = meter.integrated_loudness(m.T)
    # envelope de atividade da voz (ducking)
    a = np.abs(voice)
    win = int(0.05 * SR)
    a = np.convolve(a, np.ones(win) / win, "same")
    act = (a > 10 ** (-38 / 20)).astype(float)
    # ataque 80ms / release 450ms
    sm = np.zeros(N)
    up, dn = 1 / (0.08 * SR), 1 / (0.45 * SR)
    cur = 0.0
    for k in range(0, N, 64):
        tgt = act[k]
        cur = min(tgt, cur + up * 64) if tgt > cur else max(tgt, cur - dn * 64)
        sm[k:k + 64] = cur
    under = -16 - 16.5  # trilha ~16,5 dB abaixo da voz enquanto ele fala
    gaps = -16 - 8.0    # nos respiros a trilha sobe
    gain_db = gaps + (under - gaps) * sm
    if music_only:
        gain_db = np.full(N, -16 - 4.0)
    music = m * (10 ** ((gain_db - ml) / 20))[None, :]

    # efeitos (sempre abaixo da voz)
    fx = np.zeros((2, N))
    if not music_only:
        place(fx, click(), 0.12, -14)
        place(fx, whoosh(1.0), 0.28, -24, -0.2)
        place(fx, step(), ev["reveal"][0] - 0.02, -16, 0.1)
        place(fx, breath(0.9), ev["reveal"][0] - 0.95, -27)
        place(fx, whoosh(0.9), ev["cross3"] - 0.45, -19, 0.3)
        place(fx, rip(), ev["ripTape"] - 0.05, -15, -0.1)
        place(fx, step(), ev["reveal"][1] - 0.02, -16, -0.1)
        place(fx, creak(1.3), ev["doorPass"] - 1.05, -17, 0.2)
        place(fx, whoosh(0.9), ev["cross2"] - 0.45, -19, -0.3)
        place(fx, breath(0.7), 25.02, -21)   # respiração atrás da máscara no breque
        place(fx, step(), ev["reveal"][2] - 0.02, -15, 0.1)
        place(fx, whoosh(0.9), ev["cross1"] - 0.5, -19, 0.25)
        place(fx, click(), 38.14, -14)
        place(fx, click(), 38.48, -15)
    else:
        place(fx, click(), 0.12, -14)
    mix = music + fx + voice[None, :]
    # limitador simples (true peak ~ -1 dBTP)
    peak = np.abs(mix).max()
    lim = 10 ** (-1.2 / 20)
    if peak > lim:
        g = np.ones(N)
        over = np.abs(mix).max(0) / lim
        g = 1 / np.maximum(1, over)
        g = np.minimum.accumulate(g[::-1])[::-1] if False else g
        gs = np.convolve(g, np.ones(240) / 240, "same")
        mix *= np.minimum(g, gs)[None, :]
    print("LUFS final", round(meter.integrated_loudness(mix.T), 2), "voz", round(meter.integrated_loudness(np.stack([voice, voice], 1)), 2), "trilha", round(meter.integrated_loudness(music.T), 2), "pico", round(20 * np.log10(np.abs(mix).max()), 2))
    sf.write(out_file, mix.T, SR, subtype="PCM_24")
    # stems p/ conferência
    sf.write(os.path.join(A, "stem_fx.wav"), fx.T, SR)
