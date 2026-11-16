"""Trilha de reggae roots instrumental sintetizada (livre de direitos): bateria one-drop, guitarra skank
(corda plucked Karplus–Strong), órgão 'bubble', baixo melódico, eco dub e reverb. Estéreo, 48 kHz."""
import numpy as np, subprocess, sys
from scipy.signal import sosfilt, butter, fftconvolve
SR = 48000; rng = np.random.default_rng(1830)
BPM = 72; B = 60 / BPM; BAR = 4 * B
def lp(x, f, o=2): return sosfilt(butter(o, f / (SR / 2), output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f / (SR / 2), "high", output="sos"), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a / (SR / 2), b / (SR / 2)], "band", output="sos"), x)
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)
def add(buf, x, t, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[1] or i < 0: return
    m = min(len(x), buf.shape[1] - i); l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + m] += x[:m] * g * l * 1.414; buf[1, i:i + m] += x[:m] * g * r * 1.414
def ks(f, dur, damp=0.996, bright=0.5):
    """corda dedilhada (Karplus–Strong)"""
    n = int(dur * SR); N = max(2, int(SR / f)); buf = rng.uniform(-1, 1, N) * bright + lp(rng.uniform(-1, 1, N + 64), 3000)[:N] * (1 - bright)
    out = np.zeros(n); idx = 0
    for i in range(n):
        out[i] = buf[idx]; nx = (idx + 1) % N; buf[idx] = damp * 0.5 * (buf[idx] + buf[nx]); idx = nx
    return out
M = lambda m: 440 * 2 ** ((m - 69) / 12)
# progressão: Am | Am | D | D  (i – IV, clássico de riddim) e variação Em no fim do ciclo de 8
PROG = [("Am", [57, 64, 69, 72, 76], 45), ("Am", [57, 64, 69, 72, 76], 45), ("D", [57, 62, 66, 69, 74], 50), ("D", [57, 62, 66, 69, 74], 50),
        ("Am", [57, 64, 69, 72, 76], 45), ("Am", [57, 64, 69, 72, 76], 45), ("Em", [59, 64, 67, 71, 76], 52), ("D", [57, 62, 66, 69, 74], 50)]
def strum(notes, up=False, dur=0.16):
    x = np.zeros(int((dur + 0.05) * SR))
    for k, m in enumerate(notes[::-1] if up else notes):
        s = ks(M(m), dur, damp=0.993, bright=0.65); i = int(k * 0.006 * SR); x[i:i + len(s)] += s
    x *= env(len(x), 0.002, 0.085)  # chop abafado típico do skank
    x = hp(x, 280); x = x + 0.35 * bp(x, 1800, 4500)          # brilho de captador do braço
    return x * 0.8
def organ(notes, dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in notes[1:4]:
        f = M(m)
        for h, a in [(1, 1), (2, .6), (3, .35), (4, .25), (6, .12), (8, .08)]: x += a * np.sin(2 * np.pi * f * h * t)
    return lp(x * env(n, 0.004, dur * 0.45), 4000) * 0.12
def bass_note(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = M(m)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    pluck = lp(rng.normal(0, 1, n), 900) * env(n, .001, .012) * .25            # ataque de dedo
    x = x * env(n, 0.006, dur * 1.4) * np.minimum(1, (n - np.arange(n)) / (0.03 * SR)) + pluck
    x = lp(x, 900) + 0.6 * lp(x, 110)                                        # grave gordo (60–90 Hz)
    return x * 1.0
BASSLINES = {  # (beat, semitom relativo à fundamental, duração em beats)
    "Am": [(0, 0, .75), (1, 7, .4), (1.5, 10, .4), (2, 12, .9), (3.25, 7, .4), (3.5, 3, .45)],
    "D":  [(0, 0, .75), (1, 4, .4), (1.5, 7, .4), (2, 9, .9), (3.25, 7, .4), (3.5, 4, .45)],
    "Em": [(0, 0, .75), (1, 3, .4), (1.5, 7, .4), (2, 10, .9), (3.25, 7, .4), (3.5, 5, .45)],
}
def kick(): return lp(np.sin(2 * np.pi * np.cumsum(np.geomspace(95, 45, int(.35 * SR))) / SR) * env(int(.35 * SR), .002, .12), 400)
def rim():
    n = int(.14 * SR); t = np.arange(n) / SR; nz = rng.normal(0, 1, n)
    body = sum(np.sin(2 * np.pi * f * t) * env(n, .0005, d) for f, d in [(420, .03), (1120, .012), (2350, .008)])   # aro de madeira/metal
    return bp(nz, 1800, 9000) * env(n, .0005, .02) * .7 + body * .55
def hat(op=False): n = int((.12 if op else .04) * SR); return hp(rng.normal(0, 1, n), 7000) * env(n, .0005, .045 if op else .012) * .25
def snare(): n = int(.2 * SR); return (bp(rng.normal(0, 1, n), 900, 7000) * env(n, .001, .05) * .5 + np.sin(2 * np.pi * 190 * np.arange(n) / SR) * env(n, .001, .03) * .3)
def spring(x, mix=.22):
    n = int(1.6 * SR); ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 4.2); ir = bp(ir, 300, 5000); ir /= np.sqrt((ir ** 2).sum()) * 3
    return x * (1 - mix) + np.vstack([fftconvolve(x[0], ir)[:x.shape[1]], fftconvolve(x[1], ir[::-1].copy())[:x.shape[1]]]) * mix
def make(total):
    n = int((total + 2) * SR); drums = np.zeros((2, n)); gtr = np.zeros((2, n)); org = np.zeros((2, n)); bass = np.zeros((2, n)); dub = np.zeros((2, n))
    sw = lambda beat: beat + (0.11 if (beat * 2) % 2 == 1 else 0)   # swing ~56%
    hum = lambda: rng.normal(0.012, 0.006)                              # toca um pouco "atrás" do tempo
    bar = 0; t0 = 0.0
    while t0 < total + 1:
        name, chord, root = PROG[bar % 8]
        for b8 in range(8):                      # chimbal em colcheias
            tb = t0 + sw(b8 / 2) * B + hum(); add(drums, hat(op=(b8 == 7 and bar % 2)), tb, (.75 if b8 % 2 else .5) * rng.uniform(.75, 1.1), pan=.25)
            if rng.random() < .25: add(drums, hat(), tb + B / 4, rng.uniform(.15, .3), pan=.25)   # fantasma em semicolcheia
        add(drums, kick(), t0 + 2 * B + hum(), 1.0); r = rim(); add(drums, r, t0 + 2 * B + hum(), .95, pan=-.1); add(dub, r * .35, t0 + 2 * B, 1, pan=-.1)   # one drop
        if bar % 8 == 7: [add(drums, snare(), t0 + (3 + k / 4) * B, .35 + .1 * k, pan=-.1) for k in range(4)]   # virada
        for bt in (1, 3):                        # skank no 2 e no 4
            s = strum(chord, up=False); tt = t0 + bt * B + hum(); add(gtr, s, tt, rng.uniform(.85, 1.0), pan=-.35); add(gtr, s, tt + .012, .35, pan=.2); add(dub, s * .45, tt, 1, pan=-.35)
        for bt in (0.5, 1.5, 2.5, 3.5):         # órgão bubble nas "e"
            add(org, organ(chord, B * .45), t0 + sw(bt) * B + hum(), (.85 if bt in (1.5, 3.5) else .55) * rng.uniform(.85, 1.05), pan=.4)
        for (bt, semi, dl) in BASSLINES[name]: add(bass, bass_note(root + semi - 12 if root + semi > 52 else root + semi, dl * B), t0 + bt * B + hum() * 1.5, rng.uniform(.9, 1.05))
        bar += 1; t0 += BAR
    d = int(B * .75 * SR); echo = np.zeros_like(dub)                # eco dub (colcheia pontuada) com realimentação
    for k in range(1, 6): echo[:, d * k:] += dub[:, :-d * k] * (.5 ** k) * (1 if k % 2 else .8)
    echo = np.vstack([lp(echo[0], 2200), lp(echo[1], 2200)])[::-1]   # ping-pong
    mix = spring(drums, .12) * .9 + spring(gtr + echo * .6, .3) * 1.1 + spring(org, .2) * .8 + bass * 1.15
    mix = mix[:, :int(total * SR)]; fi = int(.25 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
    return mix / (np.abs(mix).max() + 1e-9) * .8
if __name__ == "__main__":
    total = float(sys.argv[1]); out = sys.argv[2]; x = make(total)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", out], input=x.T.astype(np.float32).tobytes(), check=True)
    print("ok", out, total)
