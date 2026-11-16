"""Trilha (dub/boom-bap instrumental sintetizado, livre de direitos), efeitos e mix final.
Narração em primeiro plano (-16 LUFS); trilha ~18 dB abaixo da voz."""
import json, subprocess, sys, numpy as np
from scipy.signal import butter, lfilter, sosfilt
SR = 48000; rng = np.random.default_rng(37)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)
def lp(x, f, o=2): return sosfilt(butter(o, f / (SR / 2), output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f / (SR / 2), "high", output="sos"), x)
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)
def tone(f0, f1, dur, a=.002, d=.1, wave=np.sin):
    n = int(dur * SR); f = np.geomspace(f0, f1, n); return wave(2 * np.pi * np.cumsum(f) / SR) * env(n, a, d)
def S(*xs):
    n = max(len(x) for x in xs); return sum(np.pad(x, (0, n - len(x))) for x in xs)
def noise(dur): return rng.normal(0, 1, int(dur * SR))
def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    if i >= len(buf): return
    m = min(len(x), len(buf) - i); buf[i:i + m] += x[:m] * g
def reverb(x, mix=.25, decay=1.6):
    ir_n = int(decay * SR); ir = rng.normal(0, 1, ir_n) * np.exp(-np.arange(ir_n) / SR * 6.5 / decay); ir = lp(ir, 6000); ir /= np.abs(ir).sum() ** .5 * 6
    from scipy.signal import fftconvolve
    return x * (1 - mix) + fftconvolve(x, ir)[:len(x)] * mix
def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float([l for l in r.stderr.splitlines() if l.strip().startswith("I:")][-1].split()[1])
def wav(path, x, ch=1):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", str(ch), "-i", "-", path], input=x.astype(np.float32).tobytes(), check=True)

def music(total, bpm=88):
    beat = 60 / bpm; n = int((total + 2) * SR); drums = np.zeros(n); bass = np.zeros(n); skank = np.zeros(n); dly = np.zeros(n)
    kick = lambda: S(tone(110, 42, .45, .002, .16) * 1.0, lp(noise(.02), 2000) * env(int(.02 * SR), .0005, .004) * .3)
    snare = lambda: S(bp(noise(.25), 900, 6000) * env(int(.25 * SR), .001, .06) * .55, tone(210, 170, .12, .001, .04) * .35)
    hat = lambda o: hp(noise(.06 if o else .03), 7000) * env(int((.06 if o else .03) * SR), .0005, .02 if o else .008) * .22
    # Am – Dm – Em – Am (dub), baixo em notas longas com swing
    roots = [55.0, 73.42, 82.41, 55.0]
    chords = [[220, 261.6, 329.6], [293.7, 349.2, 440], [329.6, 392, 493.9], [220, 261.6, 329.6]]
    bar = 4 * beat; t = 0.0; b = 0
    while t < total + 1:
        ci = (b // 2) % 4
        for s in range(16):  # semicolcheias com swing
            ts = t + s * beat / 4 + (beat / 4 * 0.18 if s % 2 else 0)
            if s in (0, 7, 10) or (s == 14 and b % 2): add(drums, kick(), ts)
            if s in (4, 12): add(drums, snare(), ts)
            if s % 2 == 0: add(drums, hat(s % 4 == 2), ts, .9 if s % 4 else .6)
            if s in (4, 12):  # skank no contratempo
                ch = S(*[tone(f, f, .16, .003, .07, wave=lambda p: np.sign(np.sin(p)) * .5 + np.sin(p) * .5) for f in chords[ci]])
                add(skank, lp(ch, 2600) * .22, ts); add(dly, lp(ch, 1800) * .22, ts + beat * .75)
        for (s, l) in [(0, 1.5), (6, .5), (8, 1.0), (11, .75), (14, .5)]:
            f = roots[ci] * (1.5 if s == 11 else 1.0)
            x = S(tone(f, f, l * beat, .01, l * beat * .8), .3 * tone(2 * f, 2 * f, l * beat, .01, l * beat * .5))
            add(bass, lp(x, 300) * .9, t + s * beat / 4)
        t += bar; b += 1
    # dub delay com realimentação
    out = np.zeros(n); d = int(beat * .75 * SR); fb = dly.copy()
    for k in range(5): out[d * k:] += fb[:n - d * k] * (.55 ** k)
    mixm = drums * .8 + bass * 1.0 + skank + lp(out, 1500) * .5
    mixm = reverb(mixm, .18, 1.2)
    fade = np.ones(n); fi = int(.4 * SR); fade[:fi] = np.linspace(0, 1, fi)
    return (mixm * fade)[:int(total * SR)]

def sfx(total, E):
    n = int(total * SR); out = np.zeros(n)
    # whoosh contínuo acompanhando a velocidade da câmera (ruído com filtro e ganho pela velocidade)
    sp = np.interp(np.arange(n) / SR, np.arange(len(E["speed"])) / 30, E["speed"]); spn = np.clip(sp / 30, 0, 1)
    w = noise(total)[:n]; lo = bp(w, 150, 900); hi = bp(w, 900, 4500)
    out += (lo * (.05 + .55 * spn) + hi * (.02 + .45 * spn ** 1.5)) * .5
    # farfalhar de folhas passando perto (rajadas aleatórias moduladas pela velocidade)
    rust = bp(noise(total)[:n], 2500, 9000) * .5
    gate = np.zeros(n); t = 0.0
    while t < total:
        t += rng.uniform(.18, .6); i = int(t * SR); L = int(rng.uniform(.06, .22) * SR)
        if i + L < n: gate[i:i + L] += np.hanning(L) * (.25 + .9 * spn[i])
    out += rust * gate * .22
    for e in E["ev"]:
        nme, t = e["n"], e["t"]
        if nme == "stamp": x = S(tone(150, 60, .22, .001, .05) * .9, bp(noise(.08), 400, 4000) * env(int(.08 * SR), .001, .015) * .7)
        elif nme == "stamp_big": x = S(tone(120, 45, .35, .001, .08) * 1.1, bp(noise(.12), 300, 5000) * env(int(.12 * SR), .001, .025) * .9)
        elif nme == "tick": x = S(bp(noise(.02), 2500, 8000) * env(int(.02 * SR), .0005, .003) * .55, tone(1900, 1900, .015, .0005, .004) * .15)
        elif nme == "thump": x = tone(90, 35, .5, .002, .15) * 1.0
        elif nme == "flick": x = bp(noise(.07), 1500, 7000) * env(int(.07 * SR), .002, .018) * .25
        elif nme == "pen": x = bp(noise(.16), 2500, 7000) * np.hanning(int(.16 * SR)) * .12
        elif nme == "whoosh_big":
            L = int(.55 * SR); x = noise(.55)[:L]; x = np.concatenate([bp(x[:L // 2], 300, 1800), bp(x[L // 2:], 600, 4000)]) * np.hanning(L) * .9
        elif nme == "scratch":   # record scratch: ruído filtrado com tom deslizante para frente e para trás
            L = int(.5 * SR); tt = np.arange(L) / SR; f = 700 + 900 * np.sin(2 * np.pi * 5.5 * tt) * np.exp(-tt * 1.5)
            x = (bp(noise(.5)[:L], 400, 5000) * .5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .4) * np.hanning(L) * 1.0
        else: continue
        add(out, x, t)
    return out

if __name__ == "__main__":
    E = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "build/h_eventos.json")); total = E["total"]
    narr_path = sys.argv[2] if len(sys.argv) > 2 else "build/h_narracao.wav"; out_path = sys.argv[3] if len(sys.argv) > 3 else "assets/historia/audio/mix.wav"
    m = music(total); wav("build/h_music.wav", m); gm = (-34.0) - lufs("build/h_music.wav")   # trilha -18 dB abaixo da voz (-16)
    s = sfx(total, E); wav("build/h_sfx.wav", s); gs = (-27.0) - lufs("build/h_sfx.wav")
    import os; os.makedirs(os.path.dirname(out_path), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", narr_path, "-i", "build/h_music.wav", "-i", "build/h_sfx.wav", "-filter_complex",
        f"[0:a]apad,atrim=0:{total}[v];[1:a]volume={gm:.2f}dB[m];[2:a]volume={gs:.2f}dB[s];[v][m][s]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.89:level=false,pan=stereo|c0=c0|c1=c0",
        "-ar", "48000", "-t", f"{total:.3f}", out_path], check=True)
    print("mix", out_path, "LUFS", lufs(out_path))
