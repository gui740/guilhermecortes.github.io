"""Trilha tensa + SFX sintetizados (100% originais, livres de direitos) e mixagem final.
Voz em primeiro plano; trilha ~18 dB abaixo. Saída: build/mix_<nome>.wav"""
import json, subprocess, sys, numpy as np
from scipy.signal import butter, sosfilt
SR = 48000
rng = np.random.default_rng(13)
def db(x): return 10 ** (x / 20)
def rms_db(x):
    a = x[np.abs(x) > 1e-4]; return 20 * np.log10(np.sqrt((a ** 2).mean()) + 1e-9)
def filt(x, kind, f, order=2): return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)
def env(n, a, r):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 2; return e
def music(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a in ((36.71, .9), (55.0, .5), (73.42, .45), (77.78, .22), (110.0, .12)):   # ré grave + segunda menor = tensão
        ph = 2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 0.07 * t + f)
        y += a * (np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t + f))
    for f in (587.3, 622.3, 880.0):                                                    # cluster agudo, bem baixo
        y += 0.035 * np.sin(2 * np.pi * f * t + 2 * np.sin(2 * np.pi * 4.3 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.19 * t + f))
    beat = 60 / 84                                                                     # pulso tipo batimento
    for k in np.arange(0.0, dur, beat):
        for off, g in ((0, 1.0), (0.17, 0.6)):
            i = int((k + off) * SR); m = min(int(0.22 * SR), n - i)
            if m <= 0: continue
            tt = np.arange(m) / SR
            y[i:i + m] += g * 1.1 * np.sin(2 * np.pi * (48 * tt + 30 * (1 - np.exp(-tt * 30)) / 30)) * np.exp(-tt * 22)
    y += 0.05 * filt(rng.normal(0, 1, n), "low", 900)
    y = filt(y, "low", 2600)
    return y / np.abs(y).max()
def whoosh(d=0.34):
    n = int(d * SR); x = rng.normal(0, 1, n); out = np.zeros(n); blk = 512
    for i in range(0, n, blk):                                   # banda que sobe e desce
        p = i / n; fc = 500 + 3800 * np.sin(np.pi * p) ** 1.5
        seg = x[max(0, i - blk):i + blk]
        out[i:i + blk] = filt(seg, "band", [fc * 0.6, fc * 1.5])[-len(x[i:i + blk]):]
    return out * np.sin(np.pi * np.arange(n) / n) ** 2 / np.abs(out).max()
def pop():
    n = int(0.05 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * (1100 * t - 6000 * t ** 2)) * np.exp(-t * 90); y[:24] += 0.6 * np.hanning(48)[24:]
    return y / np.abs(y).max()
def thud():
    n = int(0.45 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * (42 * t + 70 * (1 - np.exp(-t * 26)) / 26)) * np.exp(-t * 9) + 0.25 * filt(rng.normal(0, 1, n), "low", 1800) * np.exp(-t * 40)
    return y / np.abs(y).max()
def riser(d):
    n = int(d * SR); p = np.arange(n) / n
    y = filt(rng.normal(0, 1, n), "high", 1500) * p ** 2.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(300 + 900 * p ** 2) / SR) * p ** 2
    return y / np.abs(y).max()
def vhs(d):
    n = int(d * SR); t = np.arange(n) / SR
    y = 0.6 * filt(rng.normal(0, 1, n), "band", [1800, 9000]) + 0.35 * np.sign(np.sin(2 * np.pi * 60 * t)) * 0.3 + 0.2 * np.sin(2 * np.pi * 15734 * t)
    for k in rng.uniform(0, d, 14):                               # estalos de tracking
        i = int(k * SR); m = min(int(0.012 * SR), n - i); y[i:i + m] += rng.normal(0, 2.2, m) * np.linspace(1, 0, m)
    return y / np.abs(y).max()
def put(mixbus, x, t, gain_db):
    i = max(0, int(t * SR)); m = min(len(x), len(mixbus) - i)
    if m > 0: mixbus[i:i + m] += x[:m] * db(gain_db)
def mix(name, tl, events, dur):
    vo = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"build/vo_{name}.wav", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout, np.float32).astype(np.float64)
    n = int(dur * SR); voice = np.zeros(n); voice[:min(n, len(vo))] = vo[:n]
    vdb = rms_db(voice)
    mu = music(dur); mu *= db(vdb - 18 - rms_db(mu))             # -18 dB em relação à voz
    mu *= env(n, 0.02, 0.05)
    fx = np.zeros(n)
    for kind, t in events:
        if kind == "whoosh": put(fx, whoosh(), t - 0.12, vdb - 9 - (-12))
        elif kind == "pop": put(fx, pop(), t, vdb - 14 - (-8))
        elif kind == "thud": put(fx, thud(), t, vdb - 5 - (-10))
        elif kind == "riser": put(fx, riser(0.32), t - 0.32, vdb - 14 - (-12))
        elif kind == "vhs": put(fx, vhs(1.25) * env(int(1.25 * SR), 0.01, 0.7), t, vdb - 12 - (-12))
    y = voice + mu + fx
    y = np.tanh(y * 1.5) / np.tanh(1.5)                           # limitador suave
    y = y / np.abs(y).max() * db(-1.0)
    st = np.stack([y, y], 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", f"build/mix_{name}.wav"], input=st.tobytes(), check=True)
    print(name, "voz", round(vdb, 1), "dB | trilha", round(rms_db(mu), 1), "dB | dur", dur)
if __name__ == "__main__":
    T = json.load(open("public/timeline.json")); ev = json.load(open("public/events.json"))
    for name in ["main", "gA", "gB", "gC"]:
        mix(name, T[name], ev[name]["sfx"], ev[name]["duration"])
