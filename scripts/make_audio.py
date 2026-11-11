"""Trilha original (sintetizada, livre de direitos) + efeitos, sincronizados com src/data/timeline.json.
Caixinha de música infantil que vai desafinando/distorcendo até virar tensão.
Saída: build/music.wav, build/sfx.wav"""
import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000
T = json.load(open("src/data/timeline.json"))
DUR = T["total"]/30 + 0.3
N = int(DUR*SR); t = np.arange(N)/SR
rng = np.random.default_rng(7)

def env_exp(n, tau): return np.exp(-np.arange(n)/(tau*SR))
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], "bp", fs=SR, output="sos"), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, "lp", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "hp", fs=SR, output="sos"), x)

# ---------- caixinha de música ----------
# melodia original simples (graus da escala maior), 2 compassos repetidos
mel = [0, 4, 7, 4, 9, 7, 4, 2, 0, 2, 4, 7, 5, 4, 2, -1]
scale = {-1: -1, 0: 0, 2: 2, 4: 4, 5: 5, 7: 7, 9: 9, 11: 11, 12: 12}
base = 784.0  # G5
beat = 0.30
music = np.zeros(N)
k = 0; pos = 0.0
while pos < DUR:
    prog = min(1, pos/DUR)
    # desafina progressivamente + "corda acabando" (lentidão) a partir de ~8s
    detune = 0 if pos < 8 else (pos-8)/(DUR-8)
    semis = mel[k % len(mel)]
    wob = 1 + 0.03*detune*np.sin(pos*5.1) - 0.06*detune**1.5
    f0 = base*2**(semis/12)*wob
    n = int(1.6*SR); s0 = int(pos*SR)
    tt = np.arange(n)/SR
    note = np.zeros(n)
    for m, a, tau in [(1, 1, 0.9), (2.0, 0.35, 0.4), (3.01, 0.18, 0.25), (5.43, 0.12, 0.12), (8.9, 0.05, 0.05)]:
        note += a*np.sin(2*np.pi*f0*m*(1+0.004*detune*m)*tt)*np.exp(-tt/tau)
    note *= np.minimum(1, tt/0.002)
    e = min(N, s0+n); music[s0:e] += note[:e-s0]*0.22
    k += 1
    pos += beat*(1 + 0.45*detune**1.3)
# reverb simples
ir = rng.normal(0, 1, int(1.8*SR))*env_exp(int(1.8*SR), 0.45); ir[0] = 6
music = fftconvolve(music, ir/np.abs(ir).sum()*8, "full")[:N]

# ---------- camada de tensão ----------
def ramp(a, b): return np.clip((t-a)/(b-a), 0, 1)
drone = (np.sin(2*np.pi*55*t) + 0.6*np.sin(2*np.pi*58.3*t) + 0.4*np.sin(2*np.pi*82.4*t*(1+0.002*np.sin(t*0.7))))
drone = lp(drone + 0.3*np.sign(np.sin(2*np.pi*55*t)), 400)*0.18*ramp(7.5, 30)**1.2
cluster = sum(np.sin(2*np.pi*f*t) for f in (311.1, 329.6, 349.2, 370.0))*0.025*ramp(16, 34)
noise_bed = bp(rng.normal(0, 1, N), 2000, 6000)*0.02*ramp(18, 36)
# batida de coração a partir do "recusa a brincar"
heart = np.zeros(N); hb0 = 16.3
for st in np.arange(hb0, DUR, 0.82):
    for off, a in ((0, 1), (0.18, 0.7)):
        s0 = int((st+off)*SR); n = int(0.25*SR); tt = np.arange(n)/SR
        thump = np.sin(2*np.pi*(52+40*np.exp(-tt*30))*tt)*np.exp(-tt*14)*a
        e = min(N, s0+n); heart[s0:e] += thump[:e-s0]*0.35*min(1, (st-hb0)/6+0.4)
tension = drone + cluster + noise_bed + heart
# distorção crescente sobre a caixinha
drive = 1 + 9*ramp(9, 34)**1.3
music = np.tanh(music*drive)/np.tanh(drive)*0.25*(1-0.35*ramp(20, 36)) + tension
# "impactos" nos momentos-chave
blocks = T["blocks"]; F = lambda b: b["start"]/30
def boom(at, g=0.6):
    s0 = int(at*SR); n = int(1.4*SR); tt = np.arange(n)/SR
    x = np.sin(2*np.pi*(45+70*np.exp(-tt*8))*tt)*np.exp(-tt*3.2) + lp(rng.normal(0, 1, n), 900)*np.exp(-tt*9)*0.5
    e = min(N, s0+n); music[s0:e] += x[:e-s0]*g
boom(F(blocks[4]), 0.55)                  # "É Buddy" (título)
boom(F(blocks[12]) + blocks[12]["words"][2]["f"]/30, 0.7)   # "não era"
boom(F(blocks[8]), 0.4)                   # "mostra quem ele é de verdade"
music = hp(music, 35)
sf.write("build/music.wav", music.astype(np.float32), SR)

# ---------- efeitos ----------
sfx = np.zeros(N)
def add(x, at, g):
    s0 = int(at*SR); e = min(N, s0+len(x))
    if s0 < N: sfx[s0:e] += x[:e-s0]*g
def whoosh(d=0.28):
    n = int(d*SR); tt = np.arange(n)/SR
    x = rng.normal(0, 1, n)
    fc = 600 + 5000*(tt/d)**1.5
    out = np.zeros(n); seg = 512
    for i in range(0, n, seg):
        c = fc[i]; out[i:i+seg] = bp(x[i:i+seg], c*0.6, min(c*1.6, 20000))
    w = np.sin(np.pi*tt/d)**2
    return out*w
def pop():
    n = int(0.06*SR); tt = np.arange(n)/SR
    return np.sin(2*np.pi*(900-500*tt/0.06)*tt)*np.exp(-tt*70)
def click():
    n = int(0.02*SR); tt = np.arange(n)/SR
    return hp(rng.normal(0, 1, n), 2500)*np.exp(-tt*300)
def static(d):
    n = int(d*SR); x = bp(rng.normal(0, 1, n), 1500, 9000)
    x *= (0.6 + 0.4*(rng.random(n//480+1).repeat(480)[:n] > 0.3))
    return x*np.minimum(1, np.arange(n)/(0.01*SR))*np.minimum(1, (n-np.arange(n))/(0.08*SR))
for i, b in enumerate(blocks):
    if i > 0: add(whoosh(), F(b) - 0.12, 0.22)
    for w in b["words"]:
        if w["hl"]: add(pop(), F(b) + max(0, w["f"])/30, 0.32)
    if b.get("fx") == "cursor": add(click(), F(b) + b["words"][3]["f"]/30, 0.5)
    if b.get("handle"): add(click(), F(b) + (b["words"][3]["f"]+10)/30, 0.5)
add(static(0.55), 0.0, 0.10)                         # chuvisco na abertura
add(static(0.45), F(blocks[5]), 0.09)               # chuvisco na TV
sf.write("build/sfx.wav", sfx.astype(np.float32), SR)
print("ok", DUR)
