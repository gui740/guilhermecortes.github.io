"""Sintetiza os efeitos sonoros (numpy), mixa com a narração e normaliza em -16 LUFS."""
import json, subprocess, numpy as np
from scipy.signal import butter, lfilter
SR = 48000; rng = np.random.default_rng(7)
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t / d)
def bp(x, lo, hi): b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
def lp(x, f): b, a = butter(2, f / (SR / 2)); return lfilter(b, a, x)
def tone(f0, f1, dur, a=.002, d=.1):
    n = int(dur * SR); f = np.geomspace(f0, f1, n); return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, a, d)
def noise(dur): return rng.normal(0, 1, int(dur * SR))
def pad(x, n): return np.pad(x, (0, max(0, n - len(x))))
def mix(*xs): n = max(map(len, xs)); return sum(pad(x, n) for x in xs)
def whoosh(dur, f0=300, f1=2500):
    n = int(dur * SR); x = noise(dur); out = np.zeros(n); k = 8
    for i in range(k):
        seg = slice(i * n // k, (i + 1) * n // k); f = f0 * (f1 / f0) ** (i / (k - 1)); out[seg] = bp(x, f * .6, f * 1.6)[seg]
    t = np.linspace(0, 1, n); return out * np.sin(np.pi * t) ** 2
FX = {
 "boom":   lambda: mix(tone(95, 38, .7, .003, .22) * 1.0, bp(noise(.05), 80, 900) * env(int(.05 * SR), .001, .012) * .5),
 "impact": lambda: mix(tone(140, 55, .3, .002, .08) * .9, bp(noise(.06), 300, 3000) * env(int(.06 * SR), .001, .012) * .35),
 "impact_low": lambda: tone(80, 40, .5, .003, .16) * .9,
 "stamp":  lambda: mix(tone(170, 60, .25, .001, .05) * .9, bp(noise(.09), 500, 5000) * env(int(.09 * SR), .001, .018) * .55),
 "pop":    lambda: tone(620, 980, .09, .002, .03) * .45,
 "pop_low": lambda: tone(260, 420, .14, .004, .05) * .5,
 "tick":   lambda: bp(noise(.02), 2500, 7000) * env(int(.02 * SR), .0005, .004) * .5,
 "click":  lambda: mix(bp(noise(.03), 1200, 6000) * env(int(.03 * SR), .0005, .006) * .6, tone(220, 150, .06, .001, .02) * .5),
 "shutter": lambda: np.concatenate([bp(noise(.035), 1500, 8000) * env(int(.035 * SR), .0005, .008) * .6, np.zeros(int(.045 * SR)), bp(noise(.05), 900, 6000) * env(int(.05 * SR), .0005, .012) * .6]),
 "beep":   lambda: tone(880, 880, .14, .008, .06) * .3,
 "scratch": lambda: bp(noise(.24), 1800, 6500) * np.sin(np.pi * np.linspace(0, 1, int(.24 * SR))) ** .6 * (0.6 + 0.4 * np.sin(np.linspace(0, 60, int(.24 * SR)))) * .32,
 "whoosh": lambda: whoosh(.42) * .5,
 "whoosh_s": lambda: whoosh(.26, 500, 3500) * .32,
}
info = json.load(open("build/info.json")); dur = info["dur"]
bed = np.zeros(int(dur * SR) + SR)
for s in info["sfx"]:
    x = FX[s["n"]](); i = max(0, int((s["t"] - (0.2 if s["n"] == "whoosh" else 0)) * SR)); bed[i:i + len(x)] += x[:len(bed) - i]
bed = (bed * 0.5).astype(np.float32)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "build/sfx.wav"], input=bed.tobytes(), check=True)
MIX = "[0:a][1:a]amix=inputs=2:normalize=0:duration=first"
def lufs(extra=""):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", "build/narracao.wav", "-i", "build/sfx.wav", "-filter_complex", MIX + extra + ",ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float([l for l in r.stderr.splitlines() if l.strip().startswith("I:")][-1].split()[1])
g = -16.0 - (lufs() + 3.01)                          # +3 LU: a saída é estéreo (duplo mono)
post = f",volume={g:.2f}dB,alimiter=limit=0.84:level=false"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "build/narracao.wav", "-i", "build/sfx.wav", "-filter_complex",
  MIX + post + ",aresample=48000,pan=stereo|c0=c0|c1=c0", "-t", f"{dur:.3f}", "build/audio.wav"], check=True)
print("audio ok", dur)
