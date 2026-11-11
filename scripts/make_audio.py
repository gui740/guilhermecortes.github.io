"""Trilha original + efeitos sonoros, sintetizados do zero (livres de direitos), sincronizados com src/data/timeline.json.

Trilha: jingle de programa infantil anos 90, animado (124 bpm, Dó maior): baixo saltitante, piano de brinquedo,
xilofone + glockenspiel na melodia, bumbo/palma/chocalho. A partir do "mostra quem ele é de verdade" o jingle
continua animado, mas desafinado e com acordes "errados"; tape-stop no "não era".
Saída: build/music.wav, build/sfx.wav
"""
import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
T = json.load(open("src/data/timeline.json"))
B = T["blocks"]
DUR = T["total"] / 30 + 0.4
N = int(DUR * SR)
rng = np.random.default_rng(11)

def lp(x, f, o=2): return sosfilt(butter(o, f, "lp", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "hp", fs=SR, output="sos"), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], "bp", fs=SR, output="sos"), x)
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def bstart(i): return B[i]["start"] / 30
def wtime(i, j): return (B[i]["start"] + max(0, B[i]["words"][j]["f"])) / 30

# ------------------------------------------------------------------ TRILHA
BPM = 124; BEAT = 60 / BPM; BAR = 4 * BEAT
L = int((DUR + 4) * SR)               # buffer "reto" (antes do tape-stop)
tracks = {k: np.zeros(L) for k in ("bass", "keys", "mel", "glock", "drums", "fx")}
DARK = bstart(8)                      # "e o Buddy mostra quem ele é de verdade"

def put(track, x, at):
    s = int(at * SR)
    if s >= L: return
    e = min(L, s + len(x)); tracks[track][s:e] += x[:e - s]

def tone(f, d, parts, decay, attack=0.003, detune=0.0):
    n = int(d * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for m, a, tau in parts:
        y += a * np.sin(2 * np.pi * f * m * (1 + detune) * t) * np.exp(-t / (tau * decay))
    return y * np.minimum(1, t / attack)

XYLO = [(1, 1, 0.35), (3.93, 0.35, 0.08), (9.2, 0.12, 0.03)]
GLOCK = [(1, 1, 0.9), (2.76, 0.4, 0.3), (5.4, 0.2, 0.12)]
TOYP = [(1, 1, 0.5), (2, 0.5, 0.25), (3, 0.3, 0.12), (4.1, 0.15, 0.06)]

def bassnote(f, d):
    n = int(d * SR); t = np.arange(n) / SR
    ph = (f * t) % 1
    tri = 2 * np.abs(2 * ph - 1) - 1
    sq = np.sign(np.sin(2 * np.pi * f * t)) * 0.25
    y = lp(tri + sq, 900) * np.exp(-t / 0.35) * np.minimum(1, t / 0.004)
    return y

def kick():
    n = int(0.3 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (48 + 110 * np.exp(-t * 28)) * t) * np.exp(-t * 11) + 0.15 * hp(rng.normal(0, 1, n), 3000) * np.exp(-t * 120)
def clap():
    n = int(0.25 * SR); t = np.arange(n) / SR
    env = sum(np.exp(-np.clip(t - o, 0, None) * 60) * (t >= o) for o in (0, 0.011, 0.022)) + np.exp(-t * 18) * 0.4
    return bp(rng.normal(0, 1, n), 900, 5000) * env * 0.6
def shaker():
    n = int(0.08 * SR); t = np.arange(n) / SR
    return hp(rng.normal(0, 1, n), 6000) * np.exp(-t * 55) * 0.25

# progressão: alegre (C Am F G) e versão "errada" depois do DARK (C Ab F G / Cm)
HAPPY = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [59, 62, 67])]
WRONG = [(48, [60, 64, 67]), (44, [56, 60, 63]), (41, [56, 60, 65]), (43, [59, 62, 66])]
# melodia original do jingle (2 compassos, colcheias; None = pausa) — repete com variação
MEL_A = [72, 76, 79, 76, 77, 76, 74, None, 72, 74, 76, 72, 74, None, 67, None]
MEL_B = [72, 76, 79, 81, 79, 76, 74, 76, 77, 76, 74, 72, 71, 74, 72, None]

nbars = int(DUR / BAR) + 2
for bar in range(nbars):
    t0 = bar * BAR
    dark = t0 >= DARK
    root, chord = (WRONG if dark else HAPPY)[bar % 4]
    det = 0.012 * np.sin(bar * 1.7) if dark else 0.0           # desafinação
    # baixo "oompah": tônica no 1 e 3, quinta no 2 e 4 (pulando oitava)
    for b, n in enumerate([root, root + 7, root + 12, root + 7]):
        put("bass", bassnote(mtof(n) * (1 + det), BEAT * 0.95), t0 + b * BEAT)
    # piano de brinquedo nos contratempos
    for b in range(4):
        for n in chord:
            put("keys", tone(mtof(n), 0.4, TOYP, 0.6, detune=det * 1.5) * 0.18, t0 + b * BEAT + BEAT / 2)
    # bateria
    for b in range(4):
        put("drums", kick(), t0 + b * BEAT if b in (0, 2) else t0 + b * BEAT + (BEAT * 0.5 if b == 3 and bar % 2 else 99))
        if b in (1, 3): put("drums", clap(), t0 + b * BEAT)
        for s in range(2): put("drums", shaker() * (1.2 if s else 0.7), t0 + b * BEAT + s * BEAT / 2)
    # melodia (xilofone) + glockenspiel uma oitava acima nos compassos pares
    mel = MEL_A if (bar // 2) % 2 == 0 else MEL_B
    half = 8 * (bar % 2)
    for k in range(8):
        n = mel[half + k]
        if n is None: continue
        if dark and k % 3 == 2: n -= 1                         # notas "tortas"
        put("mel", tone(mtof(n), 0.6, XYLO, 1.0, detune=det) * 0.32, t0 + k * BEAT / 2)
        if bar % 2 == 0 and k % 2 == 0:
            put("glock", tone(mtof(n + 12), 1.0, GLOCK, 0.8, detune=det * 2) * 0.12, t0 + k * BEAT / 2)

mix = (tracks["bass"] * 0.55 + tracks["keys"] * 0.8 + tracks["mel"] * 0.9 + tracks["glock"] * 0.9 + tracks["drums"] * 0.65)
# reverb de sala pequena (estúdio de TV)
ir = rng.normal(0, 1, int(0.9 * SR)) * np.exp(-np.arange(int(0.9 * SR)) / (0.18 * SR)); ir[0] = 25
mix = fftconvolve(mix, ir / np.abs(ir).sum() * 6, "full")[:L]
# depois do DARK: leve "fita velha" (wow & flutter) + um pouco de saturação
t_all = np.arange(L) / SR
dark_amt = np.clip((t_all - DARK) / 2.0, 0, 1)
mix = np.tanh(mix * (1 + 1.2 * dark_amt)) / np.tanh(1 + 1.2 * dark_amt)

# tape-stop no "não era" e volta (leitura com velocidade variável)
TS = wtime(12, 2) - 0.02            # "não"
rate = np.ones(N)
t_out = np.arange(N) / SR
seg = (t_out >= TS) & (t_out < TS + 0.45)
rate[seg] = np.cos((t_out[seg] - TS) / 0.45 * np.pi / 2) ** 2
gap = (t_out >= TS + 0.45) & (t_out < TS + 0.75)
rate[gap] = 0
# wow & flutter contínuo no trecho sombrio
rate *= 1 + 0.006 * np.sin(2 * np.pi * 0.7 * t_out) * np.clip((t_out - DARK) / 2, 0, 1)
pos = np.cumsum(rate) - rate[0]
music = np.interp(pos, np.arange(L), mix)
music = hp(music, 40)
sf.write("build/music.wav", (music / np.abs(music).max() * 0.8).astype(np.float32), SR)

# ------------------------------------------------------------------ EFEITOS
sfx = np.zeros(N)
def add(x, at, g):
    s = int(at * SR)
    if s < 0: x = x[-s:]; s = 0
    e = min(N, s + len(x))
    if s < N: sfx[s:e] += x[:e - s] * g
def tt(d): return np.arange(int(d * SR)) / SR

def whoosh(d=0.35, up=True):
    t = tt(d); n = len(t); x = rng.normal(0, 1, n)
    out = np.zeros(n); seg = 256
    for i in range(0, n, seg):
        p = i / n; c = (300 + 6000 * p ** 1.6) if up else (6300 - 6000 * p ** 0.7)
        out[i:i + seg] = bp(x[i:i + seg], max(80, c * 0.55), min(c * 1.7, 20000))
    tonal = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * 0.15
    return (out + tonal) * np.sin(np.pi * t / d) ** 1.5

def pop():
    t = tt(0.09)
    body = np.sin(2 * np.pi * np.cumsum(1300 * np.exp(-t * 35) + 250) / SR) * np.exp(-t * 45)
    return body + hp(rng.normal(0, 1, len(t)), 4000) * np.exp(-t * 400) * 0.4

def boing():
    t = tt(0.5)
    f = 180 + 320 * np.exp(-t * 6) * (1 + 0.35 * np.sin(2 * np.pi * 18 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)

def impact(g_sub=1.0):
    t = tt(1.6)
    sub = np.sin(2 * np.pi * (38 + 90 * np.exp(-t * 9)) * t) * np.exp(-t * 2.6) * g_sub
    crack = lp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 18)
    tail = bp(rng.normal(0, 1, len(t)), 200, 1200) * np.exp(-t * 3) * 0.25
    return sub + crack * 0.7 + tail

def riser(d=1.0):
    t = tt(d); x = rng.normal(0, 1, len(t))
    out = np.zeros(len(t)); seg = 256
    for i in range(0, len(t), seg):
        c = 400 + 7000 * (i / len(t)) ** 2; out[i:i + seg] = bp(x[i:i + seg], c * 0.7, min(c * 1.4, 20000))
    tone_ = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2 * t / d)) / SR) * 0.3
    return (out + tone_) * (t / d) ** 2

def sparkle():
    out = np.zeros(int(0.9 * SR))
    for k, m in enumerate([84, 88, 91, 96, 100]):
        s = int(k * 0.06 * SR); x = tone(mtof(m), 0.6, GLOCK, 0.5)
        out[s:s + len(x)] += x[:len(out) - s] * 0.5
    return out

def cash():
    # "ka-ching": clique mecânico + gaveta + sino
    t = tt(1.0)
    clickk = hp(rng.normal(0, 1, len(t)), 2000) * np.exp(-t * 200) * (t < 0.05)
    drawer = bp(rng.normal(0, 1, len(t)), 300, 1800) * np.exp(-((t - 0.08) * 30) ** 2) * 0.6
    bell = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-np.clip(t - 0.12, 0, None) * 4.5) * (t > 0.12)
               for f, a in ((2093, 1), (2637, 0.6), (3136, 0.5), (4186, 0.3)))
    return clickk + drawer + bell * 0.45

def click():
    t = tt(0.04)
    return hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 300) + np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 200) * 0.5

def snip():
    out = np.zeros(int(0.5 * SR))
    for o in (0.0, 0.22):
        t = tt(0.12); x = (bp(rng.normal(0, 1, len(t)), 3000, 9000) * np.exp(-t * 60)
                         + np.sin(2 * np.pi * 5200 * t) * np.exp(-t * 90) * 0.4)
        s = int(o * SR); out[s:s + len(x)] += x
    return out

def rub(d=0.5):
    t = tt(d); x = bp(rng.normal(0, 1, len(t)), 600, 3000)
    return x * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 9 * t))) * np.sin(np.pi * t / d)

def squeak():
    t = tt(0.32)
    f = 1100 + 700 * np.sin(np.pi * t / 0.32)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR)) * np.sin(np.pi * t / 0.32)

def scratch():
    t = tt(0.4)
    f = 900 * np.abs(np.sin(2 * np.pi * 3.2 * t)) + 120
    return bp(rng.normal(0, 1, len(t)), 300, 4000) * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 * np.exp(-t * 3)

def glitch(d=0.35):
    t = tt(d); x = np.sign(np.sin(2 * np.pi * 110 * t)) * (rng.random(len(t)) > 0.3)
    x = x * (np.repeat(rng.random(int(d * 40) + 1) > 0.4, SR // 40 + 1)[:len(t)])
    return lp(x, 3500) * 0.7

def static(d):
    t = tt(d); x = bp(rng.normal(0, 1, len(t)), 1200, 9000)
    x *= 0.6 + 0.4 * (np.repeat(rng.random(int(d * 100) + 1), SR // 100 + 1)[:len(t)] > 0.3)
    return x * np.minimum(1, t / 0.01) * np.minimum(1, (t[-1] - t) / 0.08)

def tv_on():
    t = tt(0.9)
    thunk = np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 30)) * t) * np.exp(-t * 14)
    whine = np.sin(2 * np.pi * 15734 * t) * 0.08 * np.minimum(1, t / 0.2)
    return thunk + whine + static(0.9) * 0.5 * np.exp(-t * 3)

def ding():
    t = tt(1.2)
    return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * 3.5) for f, a in ((1568, 1), (3136, 0.4), (4704, 0.15)))

def heartbeat():
    out = np.zeros(int(0.6 * SR))
    for o, a in ((0, 1), (0.2, 0.7)):
        t = tt(0.25); x = np.sin(2 * np.pi * (50 + 40 * np.exp(-t * 30)) * t) * np.exp(-t * 14) * a
        s = int(o * SR); out[s:s + len(x)] += x
    return out

def kids_cheer(d=0.8):
    # "êêê" de plateia infantil sintetizado (vogais com vibrato, várias vozes)
    t = tt(d); out = np.zeros(len(t))
    for k in range(7):
        f0 = rng.uniform(320, 520); vib = 1 + 0.03 * np.sin(2 * np.pi * rng.uniform(5, 7) * t + k)
        src = np.sign(np.sin(2 * np.pi * np.cumsum(f0 * vib * (1 + 0.15 * t / d)) / SR))
        v = bp(src, 700, 1300) + 0.6 * bp(src, 2200, 3000)
        out += v * np.sin(np.pi * np.clip((t - k * 0.02) / (d - 0.1), 0, 1)) ** 0.8
    return out / 7

# --- transições: whoosh em toda troca de bloco (alterna sobe/desce), sub em cortes fortes
for i, b in enumerate(B):
    if i == 0: continue
    add(whoosh(0.32, up=i % 2 == 0), bstart(i) - 0.2, 0.55)
    if b.get("enter") == "whip": add(whoosh(0.22, up=True), bstart(i) - 0.08, 0.4)
# --- pop em toda palavra de destaque, boing quando o Buddy entra com pop
for i, b in enumerate(B):
    for w in b["words"]:
        if w["hl"]: add(pop(), (b["start"] + max(0, w["f"])) / 30, 0.55)
    if b.get("enter") == "pop" and "buddy" in b["cut"]: add(boing(), bstart(i) + 0.02, 0.22)

# --- momentos específicos
add(static(0.6), 0.0, 0.22)                                  # chuvisco na abertura
add(whoosh(0.3, up=True), 0.0, 0.7)                          # Buddy atravessa a tela
add(cash(), wtime(2, 1), 0.45)                               # "dinheiro" de volta
add(click(), wtime(2, 3), 0.8)                               # mãozinha clica no "volta"
add(scratch(), wtime(3, 6) + 0.1, 0.35)                      # risco no "infantil"
add(riser(0.9), bstart(4) - 0.9, 0.35)                       # sobe pro título
add(impact(), wtime(4, 1) - 0.06, 0.55)                      # "Buddy" (estrela): sub por baixo, sem tapar a palavra
add(sparkle(), wtime(4, 1) + 0.42, 0.3)
add(kids_cheer(0.7), wtime(4, 1) + 0.40, 0.16)              # plateia infantil comemora (depois da palavra)
add(impact(0.8), wtime(4, 6), 0.45)                          # "terror"
add(tv_on(), bstart(5), 0.5)                                 # TV liga
add(sparkle(), bstart(6) - 0.12, 0.3)                         # entra "música, cores"
add(heartbeat(), wtime(7, 7) + 0.15, 0.5)                    # depois de "brincar"
add(glitch(0.18), bstart(8) - 0.05, 0.4); add(impact(1.2), wtime(8, 8) + 0.05, 0.5)  # "de verdade"
add(rub(0.55), (B[10]["start"] + B[10]["words"][4]["f"] + 8) / 30, 0.45)  # borracha no "trailer"
add(snip(), wtime(11, 2) - 0.1, 0.6)                         # tesoura "curtinhos"
add(squeak(), wtime(11, 7), 0.25)                            # logo após "fofo"
add(scratch(), wtime(12, 2) - 0.05, 0.5)                     # "não era" (com tape-stop)
add(impact(1.3), wtime(12, 2), 0.7); add(glitch(0.3), wtime(12, 2), 0.35)
add(heartbeat(), wtime(13, 2), 0.5)                          # "chorando"
add(ding(), wtime(14, 5), 0.4); add(cash(), wtime(14, 7), 0.35)   # "5 milhões de dólares"
add(impact(0.7), wtime(15, 5), 0.45); add(cash(), wtime(15, 6), 0.3)  # "5 vezes"
add(whoosh(0.8, up=True), wtime(16, 0), 0.25)                # linha tracejada se desenhando
add(pop(), wtime(16, 5), 0.6)                                # "Brasil"
add(heartbeat(), wtime(17, 4) - 0.1, 0.55)                   # "encarar?"
add(click(), wtime(18, 4) - 0.02, 0.6)                      # clica em SEGUIR (entre "segue" e "Talking")
add(ding(), wtime(18, 6) + 0.45, 0.25)                      # sino depois de "Horror"

sfx = hp(sfx, 30)
sf.write("build/sfx.wav", (sfx / np.abs(sfx).max() * 0.9).astype(np.float32), SR)
print("ok", round(DUR, 2), "tape-stop em", round(TS, 2), "s; trecho sombrio a partir de", round(DARK, 2), "s")
