"""Trilha de rock (guitarra distorcida + baixo + bateria) e efeitos sonoros, tudo sintetizado aqui
(100% original, sem material de terceiros), e mixagem final em estéreo.
Voz em primeiro plano; trilha ~18 dB abaixo, com ducking leve quando a voz entra. Saída: build/mix_<nome>.wav"""
import json, subprocess, numpy as np
from scipy.signal import butter, sosfilt, lfilter, fftconvolve
SR = 48000
BPM = 124; BEAT = 60 / BPM; E8 = BEAT / 2
rng = np.random.default_rng(13)
def db(x): return 10 ** (x / 20)
def rms_db(x):
    a = x[np.abs(x) > 1e-4]; return 20 * np.log10(np.sqrt((a ** 2).mean()) + 1e-9) if len(a) else -99
def filt(x, kind, f, order=2): return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)
def norm(x): return x / (np.abs(x).max() + 1e-9)
def stereo(x, pan=0.0):  # pan -1..1
    a = (pan + 1) * np.pi / 4; return np.stack([x * np.cos(a), x * np.sin(a)], 1)
_ir = None
def reverb(x, wet=0.25, t=0.7):
    global _ir
    if _ir is None:
        n = int(1.2 * SR); _ir = filt(rng.normal(0, 1, n), "band", [300, 6000]) * np.exp(-np.arange(n) / (0.22 * SR)); _ir /= np.sqrt((_ir ** 2).sum())
    return x + wet * fftconvolve(x, _ir[:int(t * SR * 1.7)])[:len(x)]

# ───────────── instrumentos ─────────────
def ks(freq, dur, damp=0.996, bright=0.5, seed=0):
    """Corda (Karplus-Strong) via filtro IIR: rápido e com timbre de corda palhetada."""
    n = int(dur * SR); N = max(2, int(round(SR / freq)))
    r = np.random.default_rng(seed)
    x = np.zeros(n); burst = r.uniform(-1, 1, N); burst = bright * burst + (1 - bright) * np.convolve(burst, np.ones(4) / 4, "same"); x[:N] = burst[:min(N, n)]
    a = np.zeros(N + 2); a[0] = 1; a[N] = -0.5 * damp; a[N + 1] = -0.5 * damp
    return lfilter([1], a, x)
NOTE = {"E": 82.41, "F": 87.31, "G": 98.0, "A": 110.0, "Bb": 116.54, "D": 73.42}
def chord(root, dur, mute, seed, detune=1.0):
    f = NOTE[root] * detune
    damp = 0.972 if mute else 0.9975
    y = ks(f, dur, damp, 0.6, seed) + 0.9 * ks(f * 1.5, dur, damp, 0.6, seed + 1) + (0 if mute else 0.7 * ks(f * 2, dur, damp, 0.6, seed + 2))
    n = len(y); env = np.ones(n); rel = int(0.02 * SR); env[-rel:] = np.linspace(1, 0, rel)
    if mute: env *= np.exp(-np.arange(n) / (0.09 * SR))
    return y * env
def amp(x, gain=7.0):
    """Pré + distorção + caixa: é isso que transforma a corda em guitarra de rock.
    O sinal é nivelado e filtrado ANTES de saturar, para o acorde continuar definido (sem virar chiado)."""
    x = filt(filt(x, "high", 90), "low", 2600); x = x / (np.abs(x).max() + 1e-9)
    x = np.tanh(x * gain); x = np.tanh(x * 1.6 + 0.2 * x ** 2)          # dois estágios, o segundo assimétrico
    y = filt(x, "band", [85, 4200]) + 0.22 * filt(x, "band", [1500, 2800])
    return filt(y, "low", 4800, 4)
def kick():
    n = int(0.28 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * (50 * t + 95 * (1 - np.exp(-t * 34)) / 34)) * np.exp(-t * 13); y[:int(.004 * SR)] += 0.5 * rng.normal(0, 1, int(.004 * SR))
    return np.tanh(y * 2.2)
def snare():
    n = int(0.26 * SR); t = np.arange(n) / SR
    y = 0.8 * filt(rng.normal(0, 1, n), "band", [900, 7500]) * np.exp(-t * 19) + 0.6 * np.sin(2 * np.pi * (185 * t + 60 * (1 - np.exp(-t * 40)) / 40)) * np.exp(-t * 26)
    return np.tanh(reverb(y, 0.35, 0.35) * 2.0)
def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR); t = np.arange(n) / SR
    return filt(rng.normal(0, 1, n), "high", 7000) * np.exp(-t * (14 if open_ else 80))
def crash():
    n = int(1.6 * SR); t = np.arange(n) / SR
    return filt(rng.normal(0, 1, n), "band", [3500, 13000]) * np.exp(-t * 2.6)
def band(dur, seed=0, intro=False):
    """Banda tocando 'dur' segundos a partir do tempo forte. Riff em Mi frígio (E5 E5 G5 F5): tenso, com cara de terror."""
    n = int(dur * SR) + SR; gL, gR, bass, drums = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros((n, 2))
    K, S, H, HO, C = kick(), snare(), hat(), hat(True), crash()
    def put(buf, x, t, g=1.0):
        i = int(t * SR); m = min(len(x), len(buf) - i)
        if m > 0: buf[i:i + m] += x[:m] * g
    put(drums[:, 0], C, 0, 0.5); put(drums[:, 1], C, 0, 0.42)
    prog = ["E", "E", "G", "F"]; bars = int(np.ceil(dur / (8 * E8)))
    for b in range(bars):
        t0 = b * 8 * E8; root = prog[b % 4]; last = b % 4 == 3
        riff = [(0, 2, False), (2, 1, True), (3, 1, True), (4, 1, False), (5, 1, True), (6, 2, False)] if not last else [(0, 3, False), (3, 1, True), (4, 1, True), (5, 1, True), (6, 1, False), (7, 1, False)]
        for k, (pos, ln, mute) in enumerate(riff):
            r = root if not (last and pos >= 3) else "E"
            sd = seed * 1000 + b * 10 + k
            put(gL, chord(r, ln * E8 * 0.98, mute, sd), t0 + pos * E8)
            put(gR, chord(r, ln * E8 * 0.98, mute, sd + 5000, 1.004), t0 + pos * E8 + 0.007)   # dobra, levemente fora
        for e in range(8):                                              # baixo em colcheias
            r = root if not (last and e >= 3) else "E"; f = NOTE[r] / 2
            tt = np.arange(int(E8 * 0.92 * SR)) / SR
            note = np.tanh(3 * (np.sin(2 * np.pi * f * tt) + 0.5 * np.sign(np.sin(2 * np.pi * f * tt)))) * np.exp(-tt * 5)
            put(bass, filt(note, "low", 900), t0 + e * E8)
            if not (intro and b == 0):
                put(drums[:, 0], H, t0 + e * E8, 0.16 if e % 2 else 0.24); put(drums[:, 1], H, t0 + e * E8, 0.22 if e % 2 else 0.3)
        if intro and b == 0: continue                                   # 1º compasso: só guitarra e baixo
        for e in ([0, 3, 4] if not last else [0, 3, 4, 7]): put(drums[:, 0], K, t0 + e * E8, 0.95); put(drums[:, 1], K, t0 + e * E8, 0.95)
        for e in [2, 6]: put(drums[:, 0], S, t0 + e * E8, 0.7); put(drums[:, 1], S, t0 + e * E8, 0.7)
        if last:                                                        # virada
            for q in range(4): put(drums[:, 0], S, t0 + 7 * E8 + q * E8 / 4, 0.35 + 0.1 * q); put(drums[:, 1], S, t0 + 7 * E8 + q * E8 / 4, 0.35 + 0.1 * q)
            put(drums[:, 1], HO, t0 + 6 * E8, 0.3)
    g = np.stack([norm(amp(gL)) * 0.85 + norm(amp(gR)) * 0.18, norm(amp(gR)) * 0.85 + norm(amp(gL)) * 0.18], 1)
    bs = norm(bass)[:, None] * 0.75
    y = 0.62 * g + 0.5 * bs + 0.9 * drums / (np.abs(drums).max() + 1e-9)
    return y[:int(dur * SR)]
def tape_stop_fx(y, d=0.45):
    """Últimos d segundos: a fita 'morre' (andamento e afinação caem)."""
    n = int(d * SR)
    if len(y) <= n: return y
    tail = y[-n:]; pos = np.cumsum(np.linspace(1, 0.05, n)); pos = pos[pos < n - 1]
    i = pos.astype(int); fr = (pos - i)[:, None]
    slowed = (tail[i] * (1 - fr) + tail[i + 1] * fr) * np.linspace(1, 0, len(pos))[:, None] ** 0.6
    return np.concatenate([y[:-n], slowed, np.zeros((n - len(slowed), 2))])
def music(dur, cues):
    out = np.zeros((int(dur * SR), 2))
    for k, (a, b) in enumerate(cues["segments"]):
        a = max(0.0, a); b = min(dur, b)
        if b - a < 0.3: continue
        seg = band(b - a, seed=k, intro=(k == 0))
        f = int(0.03 * SR); seg[-f:] *= np.linspace(1, 0, f)[:, None]
        if k in cues.get("tape_stop", []): seg = tape_stop_fx(seg)
        i = int(a * SR); m = min(len(seg), len(out) - i); out[i:i + m] += seg[:m]
    return out / (np.abs(out).max() + 1e-9)

# ───────────── efeitos ─────────────
def fx_whoosh(d=0.42):
    n = int(d * SR); p = np.arange(n) / n; x = rng.normal(0, 1, n); out = np.zeros(n); blk = 480
    for i in range(0, n, blk):
        fc = 350 + 5200 * np.sin(np.pi * p[i]) ** 1.3
        seg = x[max(0, i - blk):i + blk]; out[i:i + blk] = filt(seg, "band", [fc * 0.55, fc * 1.6])[-len(x[i:i + blk]):]
    out = norm(out * np.sin(np.pi * p) ** 2) + 0.35 * np.sin(2 * np.pi * np.cumsum(900 - 700 * p) / SR) * np.sin(np.pi * p) ** 3   # camada tonal que desce
    pan = np.linspace(-0.8, 0.8, n); a = (pan + 1) * np.pi / 4
    return np.stack([reverb(out, 0.2) * np.cos(a), reverb(out, 0.2) * np.sin(a)], 1)
def fx_glitch():
    n = int(0.11 * SR); x = rng.normal(0, 1, n); hold = 14
    x = np.repeat(x[::hold], hold)[:n]                                    # bit-crush
    gate = (np.sin(2 * np.pi * 38 * np.arange(n) / SR) > -0.2).astype(float)
    y = filt(x, "band", [600, 9000]) * gate * np.linspace(1, 0.2, n) + 0.5 * np.sign(np.sin(2 * np.pi * 1760 * np.arange(n) / SR)) * (np.arange(n) < 0.02 * SR)
    return stereo(norm(y), rng.uniform(-0.5, 0.5))
def fx_impact():
    n = int(1.5 * SR); t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (34 * t + 90 * (1 - np.exp(-t * 9)) / 9)) * np.exp(-t * 3.2)
    crack = filt(rng.normal(0, 1, n), "band", [120, 3000]) * np.exp(-t * 22)
    stab = amp(chord("E", 1.5, False, 777) + chord("Bb", 1.5, False, 778) * 0.6, 9) * np.exp(-t * 2.2)   # trítono: acorde "do mal"
    y = np.tanh(1.6 * (1.0 * sub + 0.6 * crack)) + 0.55 * norm(stab) + 0.25 * crash()[:n] * 0.6
    return stereo(reverb(norm(y), 0.3, 1.0))
def fx_riser(d=0.6):
    n = int(d * SR); p = np.arange(n) / n
    y = crash()[:n][::-1] * p ** 2 + 0.4 * np.sin(2 * np.pi * np.cumsum(200 + 1400 * p ** 2) / SR) * p ** 3     # prato invertido + subida
    return stereo(norm(y))
def fx_tape_start(d=1.3):
    n = int(d * SR); t = np.arange(n) / SR
    hiss = 0.5 * filt(rng.normal(0, 1, n), "band", [2000, 9000]); hum = 0.25 * np.sign(np.sin(2 * np.pi * 60 * t)) * 0.4
    wob = np.sin(2 * np.pi * np.cumsum(180 + 420 * np.minimum(1, t / 0.35) + 25 * np.sin(2 * np.pi * 9 * t)) / SR) * np.exp(-t * 4) * 0.7   # motor da fita acelerando
    y = hiss + hum + wob
    for k in rng.uniform(0, d, 16):
        i = int(k * SR); m = min(int(0.012 * SR), n - i); y[i:i + m] += rng.normal(0, 2.0, m) * np.linspace(1, 0, m)
    e = np.minimum(1, t / 0.01) * np.clip((d - t) / 0.7, 0, 1) ** 1.5
    return stereo(norm(y) * e)
def fx_tape_stop():
    n = int(0.5 * SR); p = np.arange(n) / n
    y = np.sign(np.sin(2 * np.pi * np.cumsum(420 * (1 - p) ** 2 + 30) / SR)) * (1 - p) ** 1.5 * 0.6 + 0.3 * filt(rng.normal(0, 1, n), "low", 1200) * (1 - p)
    return stereo(filt(y, "low", 3000))
def fx_rec():
    n = int(0.34 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 1320 * t) * ((t < 0.07) | ((t > 0.12) & (t < 0.19))) + 0.5 * rng.normal(0, 1, n) * (t < 0.004)
    return stereo(reverb(y * 0.8, 0.12, 0.2), 0.3)
def fx_ding():
    n = int(1.1 * SR); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((659.3, 1, 5), (987.8, 0.7, 6), (1318.5, 0.5, 8), (1975.5, 0.25, 10)))
    return stereo(reverb(norm(y), 0.35, 0.9))
def fx_send():
    n = int(0.32 * SR); p = np.arange(n) / n
    y = np.sin(2 * np.pi * np.cumsum(500 + 2600 * p ** 1.5) / SR) * np.sin(np.pi * p) ** 2 + 0.4 * filt(rng.normal(0, 1, n), "high", 5000) * p * (1 - p) * 4
    pan = np.linspace(-0.6, 0.9, n); a = (pan + 1) * np.pi / 4
    return np.stack([y * np.cos(a), y * np.sin(a)], 1)
def fx_save():
    n = int(0.2 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 60) + 0.8 * np.sin(2 * np.pi * 140 * t) * np.exp(-t * 35) + 0.6 * rng.normal(0, 1, n) * (t < 0.003)
    y2 = np.roll(y, int(0.07 * SR)) * 0.8; y2[:int(0.07 * SR)] = 0
    return stereo(norm(y + y2))
def fx_bubble():
    n = int(0.18 * SR); p = np.arange(n) / n
    return stereo(np.sin(2 * np.pi * np.cumsum(380 + 900 * p) / SR) * np.sin(np.pi * p) ** 1.5, 0.2)
def fx_tick():
    n = int(0.09 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 110 * t) * np.exp(-t * 55) + 0.6 * filt(rng.normal(0, 1, n), "high", 3500) * np.exp(-t * 180)
    return stereo(norm(y))
FX = {"whoosh": (fx_whoosh, -10, 0.14), "glitch": (fx_glitch, -15, 0.02), "impact": (fx_impact, -8, 0.0), "riser": (fx_riser, -13, 0.6),
      "tape_start": (fx_tape_start, -11, 0.0), "tape_stop": (fx_tape_stop, -12, 0.0), "rec": (fx_rec, -15, 0.0), "ding": (fx_ding, -11, 0.0),
      "send": (fx_send, -12, 0.05), "save": (fx_save, -10, 0.0), "bubble": (fx_bubble, -11, 0.0), "tick": (fx_tick, -13, 0.0)}   # (gerador, dB rel. à voz, antecipação)

def mix(name, ev):
    dur = ev["duration"]; n = int(dur * SR)
    vo = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"build/vo_{name}.wav", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout, np.float32).astype(np.float64)
    voice = np.zeros(n); voice[:min(n, len(vo))] = vo[:n]
    vdb = rms_db(voice)
    mu = music(dur, ev["music"])
    mu *= db(vdb - 15 - rms_db(mu.mean(1)))                           # base 15 dB abaixo; com o ducking fica ~18 dB sob a fala
    # ducking: quando a voz entra, a trilha recua mais 3 dB; nas pausas ela sobe 3 dB
    envv = np.sqrt(np.convolve(voice ** 2, np.ones(int(0.12 * SR)) / int(0.12 * SR), "same"))
    active = (envv > db(vdb - 22)).astype(float)
    active = np.convolve(active, np.ones(int(0.18 * SR)) / int(0.18 * SR), "same")
    mu *= db(3 - 6 * active)[:, None]
    fx = np.zeros((n, 2))
    for kind, t in ev["sfx"]:
        gen, level, lead = FX[kind]; x = gen()
        x = x * db(vdb + level - rms_db(x.mean(1)) + 6)
        i = max(0, int((t - lead) * SR)); m = min(len(x), n - i)
        if m > 0: fx[i:i + m] += x[:m]
    y = np.stack([voice, voice], 1) + mu + fx
    y *= db(-15.0 - vdb)                                              # voz em ~-15 dBFS RMS (alto o bastante pro Reels)
    y = np.tanh(y * 1.1) / 1.1                                        # limitador suave nos picos
    y = np.clip(y, -db(-0.8), db(-0.8))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", f"build/mix_{name}.wav"], input=y.astype(np.float32).tobytes(), check=True)
    stems = {"music": mu, "fx": fx}
    if name == "main":
        for k, v in stems.items():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", f"build/stem_{k}.wav"], input=(v / (np.abs(v).max() + 1e-9) * 0.8).astype(np.float32).tobytes(), check=True)
    print(name, "voz", round(vdb, 1), "dB | trilha", round(rms_db(mu.mean(1)), 1), "dB | fx pico", round(20 * np.log10(np.abs(fx).max() + 1e-9), 1), "| dur", round(dur, 2))
if __name__ == "__main__":
    ev = json.load(open("public/events.json"))
    for name in ["main", "gA", "gB", "gC"]: mix(name, ev[name])
