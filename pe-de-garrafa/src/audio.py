"""Original chiptune score + 8-bit SFX + narration mix for PÉ DE GARRAFA."""
import json, os, sys, subprocess, wave
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import timeline as TL

SR = 48000
R = np.random.default_rng(7)


def T(sec):
    return int(round(sec * SR))


def tt(d):
    return np.arange(T(d)) / SR


def _fftfilt(x, mag):
    n = len(x)
    if n == 0:
        return x
    N = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, N)
    f = np.fft.rfftfreq(N, 1 / SR)
    return np.fft.irfft(X * mag(f), N)[:n]


def lp(x, fc, order=2):
    return _fftfilt(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def hp(x, fc, order=2):
    return _fftfilt(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))


def bp(x, lo, hi):
    return hp(lp(x, hi), lo)


def phase(freq, d):
    f = np.broadcast_to(np.asarray(freq, np.float64), (T(d),)) if np.ndim(freq) else np.full(T(d), float(freq))
    return np.cumsum(f) / SR


def square(freq, d, duty=0.5):
    p = phase(freq, d) % 1
    return np.where(p < duty, 1.0, -1.0)


def tri(freq, d):
    p = phase(freq, d) % 1
    t = 4 * np.abs(p - 0.5) - 1
    return np.round(t * 7) / 7  # 4-bit NES-ish triangle


def nes_noise(d, rate=8000):
    n = int(d * rate) + 2
    v = R.choice([-1.0, 1.0], n)
    return np.repeat(v, int(np.ceil(SR / rate)))[:T(d)]


def env(d, a=0.005, r=0.1, hold=None):
    n = T(d)
    e = np.ones(n)
    na, nr = max(1, T(a)), max(1, T(r))
    e[:na] = np.linspace(0, 1, na)
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def expdec(d, k):
    return np.exp(-tt(d) * k)


def crush(x, bits=5):
    q = 2 ** (bits - 1)
    return np.round(x * q) / q


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


class Bus:
    def __init__(self, dur):
        self.a = np.zeros((T(dur) + SR * 2, 2))

    def add(self, t, sig, vol=1.0, pan=0.0):
        if t < 0:
            sig = sig[T(-t):]
            t = 0
        i = T(t)
        if sig.ndim == 1:
            l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
            sig = np.stack([sig * l, sig * r], 1) * 1.41
        n = min(len(sig), len(self.a) - i)
        if n > 0:
            self.a[i:i + n] += sig[:n] * vol


def echo(x, taps=((0.19, 0.45), (0.38, 0.25), (0.6, 0.12))):
    out = np.concatenate([x, np.zeros(T(max(d for d, _ in taps)) + 10)])
    for dl, g in taps:
        out[T(dl):T(dl) + len(x)] += x * g
    return out


# ---------------------------------------------------------------- SFX
def whistle(dist=1.0):
    def tone(f0, f1, f2, d):
        n = T(d)
        f = np.interp(np.linspace(0, 1, n), [0, 0.35, 1], [f0, f1, f2])
        f = f * (1 + 0.012 * np.sin(2 * np.pi * 6 * tt(d)))
        s = np.sin(2 * np.pi * phase(f, d)) * env(d, 0.04, 0.12)
        s += 0.08 * hp(R.normal(0, 1, n), 2500) * env(d, 0.02, 0.1)
        return s
    s = np.concatenate([tone(1050, 1500, 1450, 0.26), np.zeros(T(0.09)), tone(1250, 2150, 1750, 0.62)])
    s = crush(s * 0.8, 6)
    s = echo(s)
    if dist > 1:
        s = lp(s, 4000 / dist)
    return s * 0.6


def tonk():
    d = 0.6
    thud = np.sin(2 * np.pi * phase(np.linspace(110, 45, T(d)), d)) * expdec(d, 9)
    ring = sum(np.sin(2 * np.pi * f * tt(d)) * expdec(d, k) * g for f, k, g in
               ((780, 7, 0.35), (2130, 12, 0.18), (3870, 20, 0.08)))
    click = np.concatenate([nes_noise(0.015) * 0.5, np.zeros(T(d - 0.015))])
    return crush(thud * 0.9 + ring + click, 6)


def static(d, vol=1.0):
    s = bp(nes_noise(d, 16000), 800, 7000)
    gate = np.repeat(R.random(int(d * 60) + 1) > 0.25, SR // 60 + 1)[:T(d)]
    return s * gate * env(d, 0.005, 0.05) * vol


def screech(d=1.6):
    f = np.interp(np.linspace(0, 1, T(d)), [0, 0.15, 1], [300, 1600, 900])
    s = square(f, d, 0.25) * 0.4 + square(f * 1.06, d, 0.125) * 0.3
    s += nes_noise(d, 22000) * 0.7
    sub = np.tanh(np.sin(2 * np.pi * phase(np.linspace(70, 30, T(d)), d)) * 4) * 0.9
    return (s + sub) * expdec(d, 1.8) * env(d, 0.002, 0.3)


def heartbeat():
    d = 0.18
    b = np.sin(2 * np.pi * phase(np.linspace(80, 40, T(d)), d)) * expdec(d, 22)
    return np.concatenate([b, np.zeros(T(0.12)), b * 0.7])


def kick():
    d = 0.25
    return np.sin(2 * np.pi * phase(np.linspace(140, 40, T(d)), d)) * expdec(d, 16)


def hat(d=0.04):
    return hp(nes_noise(d, 20000), 6000) * expdec(d, 80)


def crackle(d):
    s = np.zeros(T(d))
    for _ in range(int(d * 14)):
        i = R.integers(0, T(d) - 600)
        s[i:i + 300] += R.normal(0, 1, 300) * np.exp(-np.arange(300) / 40) * R.uniform(0.2, 1)
    return hp(s, 1500) * 0.5 + lp(R.normal(0, 1, T(d)), 400) * 0.25


def crickets(d):
    s = np.sin(2 * np.pi * 4300 * tt(d))
    am = (np.sin(2 * np.pi * 28 * tt(d)) > 0.3) * (np.sin(2 * np.pi * 0.9 * tt(d)) > -0.1)
    return s * am * 0.15


def wind(d):
    n = lp(R.normal(0, 1, T(d)), 500)
    m = 0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * tt(d)) * np.sin(2 * np.pi * 0.07 * tt(d) + 1)
    return n * m * 0.6


def blip(f=880, d=0.06):
    return square(f, d, 0.25) * env(d, 0.002, 0.02) * 0.4


def glitch_sfx(d=0.18):
    out = []
    for _ in range(int(d / 0.02)):
        out.append(square(R.uniform(200, 2000), 0.02, 0.5) * 0.3)
    return np.concatenate(out) + static(len(out) * 0.02, 0.4)


# ---------------------------------------------------------------- music
def seq(bus, t0, t1, bpm, step_div, pattern, voice, vol, pan=0.0, swing=0.0):
    """pattern: list of midi notes or None, played on step grid."""
    step = 60.0 / bpm / step_div
    t, i = t0, 0
    while t < t1 - 1e-3:
        n = pattern[i % len(pattern)]
        if n is not None:
            d = min(step * 0.95, t1 - t)
            bus.add(t, voice(midi(n), d), vol, pan)
        t += step
        i += 1


def v_sq(duty=0.125, dec=8):
    return lambda f, d: square(f, d, duty) * expdec(d, dec) * env(d, 0.003, 0.02)


def v_tri(f, d):
    return tri(f, d) * env(d, 0.005, 0.04)


def v_pad(f, d):
    return (square(f, d, 0.5) * 0.5 + square(f * 1.005, d, 0.25) * 0.5) * env(d, 0.4, 0.5)


def build_music(tl, total):
    m = Bus(total)
    S = {s["name"]: s for s in tl["scenes"]}
    D2, F2, A2, Bb1, G1, A1, Eb2 = 38, 41, 45, 34, 31, 33, 39
    # hook: drone + wind
    hk = S["hook"]
    m.add(0, tri(midi(26), hk["end"]) * env(hk["end"], 0.5, 0.3), 0.35)
    # title stinger
    ti = S["title"]
    for n in (38, 41, 44, 50):
        m.add(ti["start"], v_pad(midi(n), 1.4) * expdec(1.4, 1.5), 0.12)
    m.add(ti["start"], kick(), 0.6)
    # exploration (forest -> circle): 84 bpm
    a, b = S["forest"]["start"], S["circle"]["end"]
    bassline = [D2, None, D2, None, D2, None, D2, None, Bb1, None, Bb1, None, A1, None, A1, None]
    seq(m, a, b, 84, 2, bassline, v_tri, 0.55)
    arp = [62, 65, 69, 65, 62, 65, 69, 74, 58, 62, 65, 62, 57, 61, 64, 69]
    seq(m, a + 60 / 84 * 4, b, 84, 2, arp, v_sq(0.125, 6), 0.09, -0.3)
    seq(m, S["silhouette"]["start"], b, 84, 1, [None, 81, None, None, None, 80, None, None], v_sq(0.5, 3), 0.04, 0.4)
    # camp: sparse pad
    a, b = S["camp"]["start"], S["camp"]["end"]
    for i, n in enumerate([50, 46, 45]):
        t = a + i * (b - a) / 3
        m.add(t, v_pad(midi(n), (b - a) / 3 + 0.3), 0.07)
    seq(m, a, b, 70, 1, [D2, None, None, None], v_tri, 0.45)
    # scream: drone + dissonant tremolo
    a, b = S["scream"]["start"], S["scream"]["end"]
    m.add(a, tri(midi(26), b - a) * env(b - a, 0.2, 0.3), 0.5)
    seq(m, a + 1.0, b, 140, 4, [75, 74], v_sq(0.25, 20), 0.035, 0.5)
    # chase: lantern + circletop, 120 bpm accelerating intensity
    a, b = S["lantern"]["start"], S["circletop"]["end"]
    seq(m, a, b, 120, 2, [D2, D2, D2 + 12, D2, Eb2, Eb2, D2, A1], v_tri, 0.6)
    seq(m, a, b, 120, 4, [62, 65, 68, 65, 63, 66, 69, 66], v_sq(0.125, 14), 0.08, -0.25)
    seq(m, a, b, 120, 4, [None, None, 1, None] * 2, lambda f, d: hat(), 0.25, 0.2)
    seq(m, S["circletop"]["start"], b, 120, 4, [86, None, 85, None, 86, None, 80, None], v_sq(0.25, 10), 0.05, 0.4)
    t = a
    while t < b:
        m.add(t, kick(), 0.5)
        t += 60 / 120 * (1 if t < S["circletop"]["start"] else 0.5)
    # boss: ostinato tritone
    a, b = S["boss"]["start"], S["boss"]["end"]
    seq(m, a, b, 132, 4, [D2, D2 + 12, 44, D2 + 12, D2, D2 + 12, 43, 44], v_sq(0.5, 10), 0.11)
    seq(m, a, b, 132, 1, [D2 - 12, D2 - 12, 32, 32], v_tri, 0.6)
    t = a
    while t < b:
        m.add(t, heartbeat(), 0.8)
        t += 0.62
    # raise: only heartbeat slowing, cuts before end
    a, b = S["raise"]["start"], S["raise"]["end"]
    t = a
    while t < b - 1.0:
        m.add(t, heartbeat(), 0.9)
        t += 0.75
    m.add(a, tri(midi(27), b - a - 1.0) * env(b - a - 1.0, 0.3, 0.05), 0.4)
    # morning: sad triangle melody
    a, b = S["morning"]["start"], S["morning"]["end"]
    mel = [62, None, 65, None, 64, None, 60, None, 62, None, None, None, 57, None, None, None]
    seq(m, a, b, 76, 2, mel, v_tri, 0.35)
    seq(m, a, b, 76, 1, [38, None, 34, None], v_tri, 0.35)
    # game over jingle
    a = S["gameover"]["start"]
    for i, n in enumerate([69, 67, 65, 64, 62, 61, 62]):
        d = 0.22 if i < 6 else 1.2
        m.add(a + i * 0.22, v_sq(0.5, 2 if i == 6 else 6)(midi(n), d), 0.12)
        m.add(a + i * 0.22, v_tri(midi(n - 24), d), 0.4)
    # continue countdown
    a, b = S["continue"]["start"], S["continue"]["end"]
    t = a
    while t < b - 0.3:
        m.add(t, blip(1320, 0.07), 0.6)
        t += 1 / 2.2
    return m


def build_sfx(tl, total):
    s = Bus(total)
    S = {x["name"]: x for x in tl["scenes"]}
    L = {x["id"]: x for x in tl["lines"]}
    # hook
    s.add(0.0, whistle(), 0.9, -0.5)
    s.add(0.0, static(0.25), 0.25)
    s.add(0.0, wind(S["hook"]["end"]), 0.25)
    # transitions glitch
    for sc in tl["scenes"][1:]:
        if sc["name"] not in ("jumpscare",):
            s.add(sc["start"], glitch_sfx(0.12), 0.3)
    s.add(S["title"]["start"], tonk(), 0.9)
    # forest ambience
    a, b = S["forest"]["start"], S["circle"]["end"]
    s.add(a, crickets(b - a), 0.35, 0.3)
    s.add(a, wind(b - a), 0.25)
    t = a
    while t < S["forest"]["end"]:  # footsteps
        s.add(t, hp(nes_noise(0.03), 1500) * expdec(0.03, 60), 0.12)
        t += 1 / 3.5
    sl = S["silhouette"]
    s.add(sl["start"] + 0.6, tonk(), 0.6, 0.4)
    s.add(sl["start"] + 1.4, tonk(), 0.5, 0.45)
    fc = S["footclose"]
    for k in (0.15, 0.9):
        s.add(fc["start"] + k * (fc["end"] - fc["start"]), tonk(), 1.0)
    ci = S["circle"]
    for i in range(12):
        s.add(ci["start"] + i * (ci["end"] - ci["start"]) * 0.7 / 12, tonk(), 0.3, np.sin(i / 12 * 6.28) * 0.8)
    # camp
    a, b = S["camp"]["start"], S["scream"]["end"]
    s.add(a, crackle(b - a), 0.4)
    s.add(a, crickets(b - a), 0.2, -0.3)
    # scream: distant voice is mixed in mix() (narration bus) ; add static
    if "L07B" in L:
        s.add(L["L07B"]["start"] - 0.1, static(0.3), 0.4)
    # lantern: directional whistles
    a, b = S["lantern"]["start"], S["circletop"]["end"]
    s.add(a, wind(b - a), 0.35)
    ln = L.get("L10")
    if ln:
        def wt(txt):
            for w in ln["words"]:
                if txt.lower() in w["w"].lower():
                    return w["s"]
        for txt, pan, dist in (("frente", 0.0, 1), ("Atrás", -0.9, 1.5), ("cima", 0.9, 1)):
            x = wt(txt)
            if x:
                s.add(x - 0.1, whistle(dist), 0.55, pan)
        s.add(ln["start"] - 0.3, whistle(2.5), 0.4, 0.8)
    ct = S["circletop"]
    for i in range(24):
        s.add(ct["start"] + i * (ct["end"] - ct["start"]) * 0.85 / 24, tonk(), 0.35, np.sin(i * 1.7) * 0.9)
    # boss blip
    s.add(S["boss"]["start"], blip(440, 0.3), 0.5)
    # jumpscare
    js = S["jumpscare"]
    s.add(js["start"], screech(1.8), 1.0)
    s.add(js["start"], static(0.6), 0.8)
    # morning
    mo = S["morning"]
    s.add(mo["start"], wind(mo["end"] - mo["start"]), 0.3)
    l14 = L.get("L14")
    if l14:
        s.add(l14["words"][-1]["s"] - 0.1, whistle(3), 0.35, 0.6)
    # loop: whistle tail at end leads back into opening
    co = S["continue"]
    s.add(co["end"] - 0.22, static(0.22), 0.4)
    return s


def read_wav(p):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).astype(np.float64)


def build_vo(tl, total):
    v = Bus(total)
    for ln in tl["lines"]:
        p = TL.line_audio(ln["id"])
        if not p:
            continue
        x = read_wav(p)
        rms = np.sqrt(np.mean(x[np.abs(x) > 0.01 * np.abs(x).max()] ** 2)) + 1e-9
        x = np.tanh(x / rms * 0.12 * 1.6) / 1.6  # RMS-normalize + soft limit
        if ln["id"] == "L07B":  # distant scream: band-limit, echo, pan from left to right
            x = bp(x, 300, 3200)
            x = echo(x, ((0.21, 0.6), (0.43, 0.4), (0.7, 0.25), (1.0, 0.12)))
            v.add(ln["start"], x, 0.55, -0.6)
            v.add(ln["start"] + 0.11, x, 0.35, 0.7)
            continue
        x = hp(x, 70)
        v.add(ln["start"], x, 1.0)
    return v


MUS, SFX = 0.32, 0.4


def mix(out_wav):
    tl = json.load(open(os.path.join(TL.BUILD, "timing.json")))
    total = tl["total"]
    music = build_music(tl, total).a
    sfx = build_sfx(tl, total).a
    vo = build_vo(tl, total).a
    # ducking envelope from narration
    e = np.abs(vo).mean(1)
    e = lp(e, 4)
    e = e / (e.max() + 1e-9)
    duck = 1 - 0.8 * np.clip(e * 5, 0, 1)
    mixd = vo * 1.0 + music * MUS * duck[:, None] + sfx * SFX * (1 - 0.6 * np.clip(e * 5, 0, 1))[:, None]
    mixd = mixd[:T(total)]
    mixd = np.tanh(mixd * 0.9) / 0.9 * 0.7
    raw = os.path.join(TL.BUILD, "mix_raw.wav")
    write_wav(raw, mixd)
    # two-pass loudnorm to -14 LUFS
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-2:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    af = ("loudnorm=I=-14:TP=-2:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
          "measured_thresh={input_thresh}:offset={target_offset}:linear=true").format(**js)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", "48000", out_wav], check=True)
    print("measured", js["input_i"], "->", out_wav)


def write_wav(p, a):
    a = np.clip(a, -1, 1)
    with wave.open(p, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    mix(os.path.join(TL.BUILD, "mix.wav"))
