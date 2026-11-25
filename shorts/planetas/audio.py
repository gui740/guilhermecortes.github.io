"""Trilha + efeitos sintetizados + narração. Uso: python audio.py <pasta_narracao> -> out/audio.wav
A pasta de narração tem n00.mp3, n01.mp3... na ordem de narracao.json."""
import os, sys, json, subprocess, wave
import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
DUR = 25.0
N = int(SR * DUR)
BPM = 110
BEAT = 60 / BPM
rng = np.random.default_rng(42)

T_RISER, T_SUN, T_ARROW, T_FINAL, T_Q, T_LOOP = 12.4, 15.4, 17.6, 19.8, 22.4, 24.0


def tt(n):
    return np.arange(n) / SR


def place(buf, x, t0, gain=1.0):
    i = int(round(t0 * SR))
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i] * gain


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def saw(f, t, phase=0.0):
    return 2 * ((f * t + phase) % 1) - 1


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR / 2 - 100) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def env_ad(n, a, d):
    t = tt(n)
    e = np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-np.maximum(t - a, 0) / d)
    return e


# ---------------------------------------------------------------- música
CHORDS = [  # Am, F, C, G (raiz do baixo, notas do pad)
    (45, [57, 60, 64, 69]),
    (41, [53, 57, 60, 65]),
    (48, [55, 60, 64, 67]),
    (43, [55, 59, 62, 67]),
]
BAR = 4 * BEAT


def drums_on(t):
    if T_RISER <= t < T_SUN:
        return 0.0
    if T_SUN <= t < T_ARROW:
        return 0.0
    if t >= T_LOOP:
        return 0.0
    return 1.0


def kick():
    n = int(0.45 * SR)
    t = tt(n)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) * 0.95 + np.sin(ph * 2) * np.exp(-t * 30) * 0.15


def clap():
    n = int(0.25 * SR)
    x = bp(rng.standard_normal(n), 900, 4000)
    e = np.zeros(n)
    for k, o in enumerate([0, 0.011, 0.022]):
        i = int(o * SR)
        e[i:] += np.exp(-tt(n - i) * (60 if k < 2 else 16))
    return x * e * 0.5


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    x = hp(rng.standard_normal(n), 7000)
    return x * np.exp(-tt(n) * (18 if open_ else 80)) * 0.25


def music():
    L = np.zeros(N); R = np.zeros(N)
    t = tt(N)
    # pad: saws desafinadas por acorde, filtro abrindo no riser
    pad = np.zeros(N)
    nb = int(np.ceil(DUR / BAR)) + 1
    for b in range(nb):
        root, notes = CHORDS[b % 4]
        t0 = b * BAR
        n = int(BAR * SR) + int(0.3 * SR)
        tl = tt(n)
        ch = np.zeros(n)
        for m in notes:
            f = mtof(m)
            for det in (-0.12, 0.0, 0.11):
                ch += saw(f * 2 ** (det / 12), tl, rng.random())
        e = np.minimum(tl / 0.05, 1) * np.minimum(np.maximum((BAR + 0.3 - tl) / 0.3, 0), 1)
        place(pad, ch * e * 0.06, t0)
    # filtro variável (em blocos)
    out = np.zeros(N)
    blk = 2048
    zi = None
    for i in range(0, N, blk):
        tc = i / SR
        if T_RISER <= tc < T_SUN:
            fc = 900 + 5000 * ((tc - T_RISER) / (T_SUN - T_RISER)) ** 2
        elif T_SUN <= tc < T_ARROW:
            fc = 2600
        else:
            fc = 1300
        b, a = signal.butter(2, fc / (SR / 2), "low")
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0
        y, zi = signal.lfilter(b, a, pad[i:i + blk], zi=zi)
        out[i:i + blk] = y
    pad = out
    # pluck arpejado em colcheias
    arp = np.zeros(N)
    step = BEAT / 2
    k = 0
    tc = 0.0
    while tc < DUR:
        b = int(tc // BAR)
        root, notes = CHORDS[b % 4]
        m = notes[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
        n = int(0.35 * SR)
        tl = tt(n)
        f = mtof(m)
        x = (np.sin(2 * np.pi * f * tl) + 0.3 * saw(f, tl)) * np.exp(-tl * 11)
        g = 0.10 if not (T_SUN <= tc < T_ARROW) else 0.05
        if T_RISER <= tc < T_SUN:
            g = 0.06
        place(arp, lp(x, 3500, 1) * g, tc)
        k += 1
        tc += step
    # baixo
    bass = np.zeros(N)
    tc = 0.0
    while tc < DUR:
        b = int(tc // BAR)
        root = CHORDS[b % 4][0] - 12
        n = int(step * SR)
        tl = tt(n)
        f = mtof(root)
        x = (np.sin(2 * np.pi * f * tl) + 0.25 * np.sin(4 * np.pi * f * tl)) * np.minimum(tl / 0.005, 1) * np.exp(-tl * 4)
        g = 0.32 * (1.0 if drums_on(tc) else 0.6)
        place(bass, x * g, tc)
        tc += step
    # bateria
    dr = np.zeros(N)
    K, C, Hc, Ho = kick(), clap(), hat(), hat(True)
    pump = np.ones(N)
    nbeats = int(DUR / BEAT) + 1
    for i in range(nbeats):
        tb = i * BEAT
        if drums_on(tb):
            place(dr, K, tb, 0.8)
            ip = int(tb * SR)
            m = min(N - ip, int(0.3 * SR))
            if m > 0:
                pump[ip:ip + m] = np.minimum(pump[ip:ip + m], 0.45 + 0.55 * np.minimum(tt(m) / 0.22, 1) ** 0.6)
            if i % 2 == 1:
                place(dr, C, tb, 0.8)
            place(dr, Hc if i % 4 != 3 else Ho, tb + BEAT / 2, 0.8)
            if i % 2 == 0:
                place(dr, Hc, tb + BEAT * 0.75, 0.4)
    # virada de caixa acelerando no riser
    tc = T_RISER + 1.0
    while tc < T_SUN - 0.02:
        u = (tc - T_RISER - 1.0) / (T_SUN - T_RISER - 1.0)
        place(dr, C, tc, 0.25 + 0.6 * u)
        tc += BEAT / 2 if u < 0.4 else (BEAT / 4 if u < 0.75 else BEAT / 8)
    mus = (pad + arp) * pump + bass * pump + dr
    # estéreo simples
    L = mus + 0.3 * arp * pump
    R = mus - 0.3 * arp * pump + 0.0
    return np.stack([L, R], 1)


# ---------------------------------------------------------------- efeitos
def whoosh(dur=0.8, peak=0.5, reverse=False, lo=250, hi=3500):
    n = int(dur * SR)
    t = tt(n) / dur
    x = rng.standard_normal(n)
    out = np.zeros(n)
    blk = 512
    for i in range(0, n, blk):
        u = t[i]
        c = lo + (hi - lo) * np.exp(-((u - peak) / 0.25) ** 2)
        seg = bp(x[max(0, i - 2048):i + blk], c * 0.6, min(c * 1.6, SR / 2 - 200))
        out[i:i + blk] = seg[-len(out[i:i + blk]):]
    e = np.where(t < peak, (t / peak) ** 2.5, np.exp(-(t - peak) / (1 - peak) * 4))
    y = out * e
    if reverse:
        y = y[::-1]
    pan = np.linspace(-0.6, 0.6, n) if not reverse else np.linspace(0.6, -0.6, n)
    return np.stack([y * (1 - pan) * 0.5, y * (1 + pan) * 0.5], 1)


def blip(f0=880, f1=1480):
    n = int(0.14 * SR)
    t = tt(n)
    f = f0 + (f1 - f0) * np.minimum(t / 0.05, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * env_ad(n, 0.003, 0.05)
    return np.stack([y, y], 1)


def tick(f=2600, g=1.0):
    n = int(0.03 * SR)
    t = tt(n)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 220) * g + hp(rng.standard_normal(n), 3000) * np.exp(-t * 400) * 0.3 * g
    return np.stack([y, y], 1)


def riser(dur):
    n = int(dur * SR)
    t = tt(n)
    u = t / dur
    nz = hp(rng.standard_normal(n), 1500) * u ** 2.2 * 0.5
    f = 160 * 2 ** (u * 3.2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + 0.4 * np.sin(ph * 1.5) + 0.3 * np.sin(ph * 2.01)) * u ** 1.6 * 0.35
    trem = 1 + 0.3 * np.sin(2 * np.pi * (4 + 18 * u ** 2) * t)
    y = (nz + tone) * trem
    w = np.linspace(-1, 1, n) * 0.3
    return np.stack([y * (1 - w), y * (1 + w)], 1) * 0.6


def boom():
    n = int(3.2 * SR)
    t = tt(n)
    f = 30 + 70 * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 1.3)
    hit = lp(rng.standard_normal(n), 900, 2) * np.exp(-t * 6) * 0.9
    crack = hp(rng.standard_normal(n), 2000) * np.exp(-t * 18) * 0.25
    y = np.tanh((sub * 1.4 + hit + crack) * 1.6) * 0.9
    # cauda tipo reverb
    ir = rng.standard_normal(int(1.8 * SR)) * np.exp(-tt(int(1.8 * SR)) * 3)
    tail = signal.fftconvolve(hit * 0.5, ir)[:n] * 0.02
    return np.stack([y + tail, y - tail * 0.5 + tail * 0.5], 1)


def sfx():
    S = np.zeros((N, 2))
    for tp in [1.75, 4.35, 6.2, 8.2, 10.2]:      # picos de movimento de câmera
        place(S, whoosh(0.9, 0.55), tp - 0.5, 0.7)
    place(S, whoosh(1.6, 0.8, lo=150, hi=2500), T_SUN - 1.3, 0.6)
    for tb in [1.70, 1.85, 2.00]:
        place(S, blip(700, 1100), tb, 0.35)
    for tb in [4.9, 6.9, 8.9, 10.9, T_ARROW, T_FINAL, T_Q]:
        place(S, blip(), tb, 0.45)
    # ticks dos km
    for tb in [4.9, 6.9, 8.9, 10.9]:
        tc = tb + 0.05
        while tc < tb + 0.9:
            place(S, tick(3200, 0.5), tc, 0.25)
            tc += 0.055 + 0.08 * (tc - tb)
    # ticks do contador 1x -> 109x (mesma curva do vídeo)
    last, lt = 1, -1
    for i in range(int(T_SUN * SR), int((T_SUN + 1.8) * SR), int(SR * 0.005)):
        tc = i / SR
        u = min(max((tc - T_SUN - 0.1) / 1.5, 0), 1)
        n = 1 + int(round(108 * (1 - (1 - u) ** 2.2)))
        if n != last and tc - lt > 0.032:
            place(S, tick(2200 + 8 * n, 0.8), tc, 0.35)
            last, lt = n, tc
    place(S, riser(T_SUN - T_RISER), T_RISER, 0.9)
    place(S, boom(), T_SUN, 1.0)
    place(S, whoosh(1.0, 0.95, reverse=False, lo=200, hi=4000), T_LOOP, 0.0)
    place(S, whoosh(1.0, 0.3, reverse=True, lo=200, hi=4000), T_LOOP, 1.6)  # whoosh reverso
    return S


# ---------------------------------------------------------------- narração
def load_mono(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af",
                          "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                          "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                          "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x / (np.abs(x).max() + 1e-9) * 0.9


def narration(folder):
    lines = json.load(open(os.path.join(HERE, "narracao.json")))
    V = np.zeros(N)
    for i, l in enumerate(lines):
        p = None
        for ext in ("wav", "mp3"):
            c = os.path.join(folder, f"n{i:02d}.{ext}")
            if os.path.exists(c):
                p = c; break
        if p is None:
            continue
        x = load_mono(p)
        end = l["t"] + len(x) / SR
        nxt = lines[i + 1]["t"] if i + 1 < len(lines) else DUR
        if end > nxt - 0.05:
            print(f"aviso: fala {i} invade a próxima ({end:.2f} > {nxt:.2f})")
        place(V, x, l["t"])
    return V


def main():
    folder = sys.argv[1]
    M = music()
    S = sfx()
    V = narration(folder)
    # ducking da música sob a voz
    env = np.abs(V)
    b, a = signal.butter(1, 6 / (SR / 2))
    env = signal.filtfilt(b, a, env)
    env = np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
    duck = 1 - 0.55 * env
    mix = M * 0.55 * duck[:, None] + S * 0.8 + V[:, None] * 1.0
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    # micro fade nas pontas para o loop não estalar
    f = int(0.004 * SR)
    mix[:f] *= np.linspace(0, 1, f)[:, None]
    mix[-f:] *= np.linspace(1, 0, f)[:, None]
    out = os.path.join(HERE, "out", "audio.wav")
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("audio ok", out)


if __name__ == "__main__":
    main()
