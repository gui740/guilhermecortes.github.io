"""Trilha lo-fi + efeitos sintetizados + narração (out/narr), sincronizados com out/tempos.json.
Uso: python3 audio.py  -> out/audio.wav"""
import json, os, re, subprocess, wave
import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SR = 44100
TP = json.load(open(os.path.join(OUT, "tempos.json")))
DUR = TP["total"]
N = int(round(DUR * SR))
src = open(os.path.join(HERE, "narracao_tempos.js")).read()
TEMPOS = json.loads(src[src.index("{"):src.rindex("};") + 1])
CEN = {c["id"]: c for c in TP["cenas"]}
rng = np.random.default_rng(5)


def real(cid, c):
    """tempo real (s) de um instante c do relógio da cena"""
    x = CEN[cid]
    return x["t0"] - x["pre"] + c


def word(cid, frag, fb, nth=0):
    ws = [w for w in TEMPOS[cid]["palavras"] if w[0].startswith(frag)]
    return ws[nth][1] if len(ws) > nth else fb


def tt(n):
    return np.arange(n) / SR


def place(buf, x, t0, g=1.0):
    i = int(round(t0 * SR))
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i] * g


def st(y, pan=0.0):
    return np.stack([y * (1 - pan), y * (1 + pan)], 1)


def lp(x, fc, o=2):
    b, a = signal.butter(o, min(fc, SR / 2 - 100) / (SR / 2), "low"); return signal.lfilter(b, a, x)


def hp(x, fc, o=2):
    b, a = signal.butter(o, fc / (SR / 2), "high"); return signal.lfilter(b, a, x)


def bp(x, lo, hi, o=2):
    b, a = signal.butter(o, [lo / (SR / 2), hi / (SR / 2)], "band"); return signal.lfilter(b, a, x)


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- trilha lo-fi
BPM = 80
BEAT = 60 / BPM
CHORDS = [(41, [53, 57, 60, 64]), (40, [52, 55, 59, 62]), (38, [50, 53, 57, 60]), (36, [48, 52, 55, 59])]  # Fmaj7 Em7 Dm7 Cmaj7


def rhodes(f, n):
    t = tt(n)
    y = np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t * 3))
    y += 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t * 5)
    return y * np.exp(-t * 0.9) * np.minimum(t / 0.01, 1)


def music():
    keys, bass, dr = np.zeros(N), np.zeros(N), np.zeros(N)
    bar = 4 * BEAT
    for b in range(int(DUR / bar) + 2):
        root, notes = CHORDS[b % 4]
        n = int(bar * 1.1 * SR)
        y = sum(rhodes(mtof(m), n) for m in notes) * 0.07
        place(keys, y, b * bar + 0.02 * rng.random())
        place(keys, sum(rhodes(mtof(m + 12), int(BEAT * SR)) for m in notes[1:3]) * 0.03, b * bar + BEAT * 2.5)
        for k, off in enumerate((0, BEAT * 1.5, BEAT * 2, BEAT * 3.5)):
            nn = int(BEAT * 0.9 * SR); tl = tt(nn)
            f = mtof(root - 12 + (7 if k == 3 else 0))
            place(bass, np.sin(2 * np.pi * f * tl) * np.exp(-tl * 3) * np.minimum(tl / 0.01, 1) * 0.28, b * bar + off)
    sw = BEAT / 2 * 0.62   # swing
    kick = lambda: np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-tt(int(0.4 * SR)) * 25)) / SR) * np.exp(-tt(int(0.4 * SR)) * 7)
    snare = lambda: bp(rng.standard_normal(int(0.25 * SR)), 1200, 6000) * np.exp(-tt(int(0.25 * SR)) * 18) * 0.5 + \
        np.sin(2 * np.pi * 190 * tt(int(0.25 * SR))) * np.exp(-tt(int(0.25 * SR)) * 25) * 0.3
    hat = lambda g: hp(rng.standard_normal(int(0.05 * SR)), 7000) * np.exp(-tt(int(0.05 * SR)) * 70) * 0.18 * g
    for i in range(int(DUR / BEAT) + 1):
        t = i * BEAT
        if i % 4 in (0,) or (i % 4 == 2 and i % 8 == 6):
            place(dr, kick(), t, 0.8)
        if i % 4 == 2 and i % 8 != 6:
            place(dr, kick(), t + sw, 0.5)
        if i % 2 == 1:
            place(dr, snare(), t + 0.012, 0.7)
        place(dr, hat(1.0), t)
        place(dr, hat(0.6), t + sw)
    mus = lp(keys, 2600) + bass + lp(dr, 7000)
    # oscilação de fita (wow) + chiado de vinil
    tN = tt(N)
    wob = 1 + 0.004 * np.sin(2 * np.pi * 0.5 * tN)
    idx = np.clip(np.cumsum(wob) - 1, 0, N - 1).astype(int)
    mus = mus[idx]
    crackle = (rng.random(N) < 0.0009) * rng.standard_normal(N) * 0.35
    crackle = hp(crackle, 1500) + lp(rng.standard_normal(N), 900) * 0.012
    # fita parando no plot twist
    tdrop = real("cena4", word("cena4", "despencou", 4.4))
    a, b = int((tdrop - 0.9) * SR), int((tdrop + 1.6) * SR)
    env = np.ones(N)
    stop = np.linspace(1, 0, int(0.9 * SR)) ** 1.5
    env[a:a + len(stop)] = stop
    env[a + len(stop):b] = 0
    env[b:b + int(0.6 * SR)] = np.linspace(0, 1, int(0.6 * SR))
    seg = mus[a:a + len(stop)]
    slow = np.clip(np.cumsum(stop) .astype(int), 0, len(seg) - 1)
    mus[a:a + len(stop)] = seg[slow]
    return st(mus * env, 0.0) + st(crackle, 0.2)


# ---------------------------------------------------------------- efeitos
def rip(dur=0.9):
    n = int(dur * SR); t = tt(n); u = t / dur
    y = bp(rng.standard_normal(n), 1500, 7000) * (rng.random(n) < 0.35)
    y = y * (np.sin(np.pi * u) ** 0.5) * (1 + 0.6 * np.sin(2 * np.pi * 37 * t))
    return st(y * 0.5, 0.3)


def slap():
    n = int(0.12 * SR); t = tt(n)
    return st(bp(rng.standard_normal(n), 300, 3000) * np.exp(-t * 40) * 0.5)


def scratch():
    n = int(0.6 * SR); t = tt(n)
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3.2 * t))
    y = bp(rng.standard_normal(n), 200, 3000) * 0.6 + np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.15
    return st(y * np.exp(-t * 2) * 0.7)


def boom():
    n = int(2.6 * SR); t = tt(n)
    y = np.sin(2 * np.pi * np.cumsum(30 + 70 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.4)
    y += lp(rng.standard_normal(n), 800) * np.exp(-t * 6)
    return st(np.tanh(y * 2) * 0.85)


def heartbeat():
    n = int(0.5 * SR); y = np.zeros(n)
    for off, f, g in ((0, 52, 1.0), (0.16, 64, 0.7)):
        m = int(0.3 * SR); tl = tt(m)
        place(y, np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-tl * 30))) / SR) * np.exp(-tl * 14) * g, off)
    return st(np.tanh(y * 1.3))


def click(f=2500, g=1.0):
    n = int(0.03 * SR); t = tt(n)
    return st(np.sin(2 * np.pi * f * t) * np.exp(-t * 250) * g)


def chord_hit(notes, g=1.0):
    n = int(1.8 * SR)
    return st(sum(rhodes(mtof(m), n) for m in notes) * 0.25 * g)


def sfx():
    S = np.zeros((N, 2))
    for c in TP["cenas"][1:]:                      # papel rasgando em cada transição
        place(S, rip(0.9), c["t0"] - 0.9, 1.0)
    for c in TP["cenas"]:                          # recortes batendo na mesa no começo de cada cena
        for k in range(4):
            place(S, slap(), real(c["id"], 0.3 + c["pre"] + k * 0.18), 0.5)
    # cena 1: caveira batendo os dentes
    tc = real("cena1", word("cena1", "provavelmente", 3.2) + 0.8)
    for k in range(28):
        place(S, click(1800 + 300 * (k % 2), 0.6), tc + k / 14, 0.5)
    # cena 2: vinheta (pancada + acorde)
    place(S, boom(), real("cena2", 0.95), 0.35)
    place(S, chord_hit([53, 57, 60, 64, 69]), real("cena2", 1.0), 0.8)
    # cena 3/4/5/7: ticks dos números contando
    for cid, a, b in (("cena3", 0.4, word("cena3", "setenta", 11.4, 1)), ("cena4", word("cena4", "despencou", 4.4) - 1.8, word("cena4", "despencou", 4.4) + 0.2),
                      ("cena5", word("cena5", "setenta", 7.0, 1) - 1.2, word("cena5", "setenta", 7.0, 1) + 0.2),
                      ("cena7", word("cena7", "setenta", 6.0) - 0.6, word("cena7", "setenta", 6.0) + 0.8)):
        t = a
        while t < b:
            place(S, click(3200, 0.35), real(cid, t), 0.6)
            t += 0.09
    # cena 4: disco arranhando + BOOM no "despencou"
    td = word("cena4", "despencou", 4.4)
    place(S, scratch(), real("cena4", td - 0.5), 1.0)
    place(S, boom(), real("cena4", td), 1.0)
    # cena 7: coração batendo (no ritmo do desenho: 1,2 Hz)
    c7 = CEN["cena7"]
    k = 0
    while True:
        tq = (0.25 + k) / 1.2
        if tq > c7["dur"] + c7["pre"] - 0.5:
            break
        place(S, heartbeat(), real("cena7", tq) - 0.05, 0.8)
        k += 1
    # cena 8: acorde de festa no "comenta"
    place(S, chord_hit([60, 64, 67, 72, 76], 1.2), real("cena8", word("cena8", "comenta", 4.6)), 1.0)
    return S


def load_mono(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af",
                          "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x / (np.abs(x).max() + 1e-9) * 0.9


def main():
    V = np.zeros(N)
    for c in TP["cenas"]:
        place(V, load_mono(c["wav"]), c["start"])
    M, S = music(), sfx()
    env = np.abs(V)
    b, a = signal.butter(1, 5 / (SR / 2))
    env = np.clip(signal.filtfilt(b, a, env) / (np.abs(V).max() * 0.12 + 1e-9), 0, 1)
    mix = M * 0.55 * (1 - 0.55 * env)[:, None] + S * 0.75 * (1 - 0.3 * env)[:, None] + V[:, None]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    with wave.open(os.path.join(OUT, "audio.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("audio ok", round(DUR, 2), "s")


if __name__ == "__main__":
    main()
