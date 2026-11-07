"""Mixagem final -> saida/audio.wav (48 kHz estéreo), seguindo o roteiro montado pelas falas."""
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

import config as C
import voz as V

SR = C.SR


def _filt(x, f, tipo, ordem=2):
    return sosfilt(butter(ordem, f, btype=tipo, fs=SR, output="sos"), x).astype(np.float32)


def seg_(t):
    return int(round(t * SR))


def env_adsr(n, a=0.005, r=0.05):
    e = np.ones(n, np.float32)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def tom(f, dur, harm=(1,), decai=0.0, detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * (k + 1) * (1 + detune * k) * t) for k, a in enumerate(harm))
    if decai:
        x = x * np.exp(-t * decai)
    return (x * env_adsr(n)).astype(np.float32)


def nota(nome):
    tab = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    n = tab[nome[0]] + (1 if "#" in nome else 0) - (1 if "b" in nome[1:] else 0)
    return 440.0 * 2 ** ((n + (int(nome[-1]) - 4) * 12) / 12)


def tilintar(rng):
    f0 = rng.uniform(1700, 2900)
    n = int(rng.uniform(0.4, 0.9) * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f0 * p * t + rng.uniform(0, 6)) * np.exp(-t * d)
            for p, a, d in ((1, 1, 6), (2.32, .6, 9), (4.25, .35, 14), (6.63, .2, 20)))
    return (x * env_adsr(n, 0.001, 0.05)).astype(np.float32) * 0.3


def piano(f, dur, rng, desafina=0.0):
    f = f * 2 ** (rng.uniform(-desafina, desafina) / 1200)
    return tom(f, dur, harm=(1, .45, .25, .12, .06), decai=3.2, detune=0.0015) * 0.5


def valsa(dur, rng):
    """Valsa de piano distante e desafinada (3/4)."""
    b = 60 / 132
    prog = [("A2", ["C4", "E4"]), ("E2", ["B3", "D4"]), ("A2", ["C4", "E4"]), ("D2", ["F3", "A3"]),
            ("A2", ["C4", "E4"]), ("E2", ["G#3", "D4"]), ("A2", ["C4", "E4"]), ("E2", ["G#3", "B3"])]
    mel = ["E5", "C5", "A4", "B4", "G#4", "E4", "C5", "A4", "E4", "D5", "A4", "F4",
           "E5", "C5", "A4", "D5", "B4", "G#4", "C5", "B4", "A4", "B4", "-", "-"]
    x = np.zeros(int((dur + 2) * SR), np.float32)
    c, t = 0, 0.0
    while t < dur:
        bx, ac = prog[c % len(prog)]
        for bt in range(3):
            a = int((t + bt * b) * SR)
            s = piano(nota(bx), 1.2, rng, 35) if bt == 0 else sum(piano(nota(n), 0.6, rng, 40) for n in ac) * 0.5
            x[a:a + len(s)] += s[: len(x) - a]
            m = mel[(c * 3 + bt) % len(mel)]
            if m != "-":
                s = piano(nota(m), 0.9, rng, 45) * 0.8
                x[a:a + len(s)] += s[: len(x) - a]
        c += 1
        t += 3 * b * rng.uniform(0.97, 1.05)
    return _filt(x, 2200, "low")[: int(dur * SR)]


def reverb(x, dur=2.4, rng=None, brilho=3000):
    rng = rng or np.random.default_rng(C.SEED + 9)
    n = int(dur * SR)
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-np.linspace(0, 6.5, n)).astype(np.float32)
    ir = _filt(ir, brilho, "low")
    y = fftconvolve(x, ir).astype(np.float32)
    return y / (np.abs(y).max() + 1e-9) * (np.abs(x).max() + 1e-9)


def gota():
    n = int(0.05 * SR)
    tt = np.arange(n) / SR
    f = 2100 * np.exp(-tt * 28) + 700
    x = (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 70)).astype(np.float32)
    out = np.zeros(int(1.8 * SR), np.float32)
    g, d = 1.0, int(0.29 * SR)
    for k in range(6):
        s = x if k == 0 else _filt(x, 3000 / (k + 0.5), "low")
        out[k * d:k * d + n] += s * g
        g *= 0.5
    return out


def impacto(rng, dur=1.2, grave=48):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * grave * tt) * np.exp(-tt * 6)
         + _filt(rng.standard_normal(n).astype(np.float32), 700, "low") * np.exp(-tt * 10) * 1.2
         + _filt(rng.standard_normal(n).astype(np.float32), 2500, "high") * np.exp(-tt * 40) * 0.3)
    return x.astype(np.float32)


def ruido_estatica(rng, dur):
    n = int(dur * SR)
    return _filt(rng.standard_normal((n, 2)).astype(np.float32).T, [300, 9000], "band").T * 0.5


def mixar(roteiro, total, eventos, falas):
    rng = np.random.default_rng(C.SEED)
    N = int(total * SR) + SR
    st = {k: np.zeros((N, 2), np.float32) for k in ("voz", "festa", "sfx", "ui", "drone")}

    def por(trilha, x, t, g=1.0, pan=0.0):
        a = seg_(t)
        if a >= N or len(x) == 0:
            return
        x = x[: N - a] * g
        if x.ndim == 1:
            st[trilha][a:a + len(x), 0] += x * np.sqrt(0.5 * (1 - pan))
            st[trilha][a:a + len(x), 1] += x * np.sqrt(0.5 * (1 + pan))
        else:
            st[trilha][a:a + len(x)] += x

    t_all = np.arange(N) / SR
    base = (_filt(rng.standard_normal((N, 2)).astype(np.float32).T, [1500, 12000], "band").T * 0.010
            + (np.sin(2 * np.pi * 60 * t_all) * 0.006 + np.sin(2 * np.pi * 120 * t_all) * 0.002)[:, None])

    seg = {s["tipo"]: s for s in roteiro}
    regras = [s for s in roteiro if s["tipo"] == "regra"]
    cftv = [s for s in roteiro if s["tipo"] == "cftv"]

    # abertura: estática e tom de alerta de dois tons
    por("sfx", ruido_estatica(rng, 0.35), 0.0, 0.8)
    cab = seg["fita"]
    n = seg_(0.85)
    tt = np.arange(n) / SR
    alerta = (np.sin(2 * np.pi * 853 * tt) + np.sin(2 * np.pi * 960 * tt)) * 0.5 * env_adsr(n, 0.01, 0.05)
    por("ui", np.tanh(alerta * 1.5).astype(np.float32), cab["t0"] + 0.05, 0.22)
    por("voz", V.transmissao(falas["intro1"], 1), cab["t_voz"], 1.0)
    al = seg["alvo"]
    por("sfx", ruido_estatica(rng, 2 / C.FPS + 0.03), al["t0"] - 0.02, 0.7)
    por("sfx", impacto(rng, 1.6, 44), al["t0"], 0.55)
    por("voz", V.transmissao(falas["intro2"], 2), al["t_voz"], 1.0)
    # bipe de "objetivo" quando o marcador aparece
    por("ui", np.concatenate([tom(660, 0.08, harm=(1, .3)), tom(990, 0.12, harm=(1, .3))]) * 0.4, al["t0"] + 0.45, 0.6)

    # regras
    for s in regras:
        k = s["n"]
        bip = tom(1000, 0.16, harm=(1, .2)) * 0.4
        por("ui", bip, s["t0"] + 0.02, 0.5)
        por("voz", V.transmissao(falas[f"regra{k}"], 10 + k), s["t_voz"], 1.0)
        if k == 3:   # um brinde a mais, ao fundo
            for j in range(6):
                por("festa", tilintar(rng) * 1.5, s["t_voz"] + 3.6 + j * 0.3, 1.0, pan=0.4)
        if k == 7:
            x = V.corrompida(falas["extra"], -3, 77)
            por("voz", x, s["t_voz_extra"], 1.05)
            zz = np.sign(np.sin(2 * np.pi * 60 * np.arange(seg_(s["t1"] - s["t_extra"])) / SR)).astype(np.float32)
            zz = _filt(zz, 400, "low") * np.linspace(0, 1, len(zz)) ** 2
            por("sfx", zz, s["t_extra"], 0.25)
            por("sfx", impacto(rng, 1.0, 40), s["t_extra"], 0.6)

    # festa distante: valsa + copos, de regra 2 até o fim da regra 7, crescendo
    f0, f1 = regras[1]["t0"], cftv[-1]["t1"]
    dur = f1 - f0
    v = V.wow(valsa(dur, rng), 0.004, 3)
    copos = np.zeros(len(v), np.float32)
    tc = 0.6
    while tc < dur - 0.5:
        s_ = tilintar(rng)
        a = seg_(tc)
        copos[a:a + len(s_)] += s_[: len(copos) - a]
        tc += rng.exponential(1 / (0.4 + 2.2 * (tc / dur) ** 1.5))
    festa = v * 0.6 + copos * 0.7
    festa = festa * 0.25 + reverb(festa, 2.8, rng)[: len(festa)] * 0.9
    festa *= (0.05 + 0.95 * np.linspace(0, 1, len(festa)) ** 1.8).astype(np.float32) * 0.5
    festa[-seg_(0.05):] *= np.linspace(1, 0, seg_(0.05))
    por("festa", np.stack([festa, np.roll(festa, 900)], -1), f0)

    # drone grave crescendo do começo ao fim
    d0, d1 = cab["t0"], cftv[-1]["t1"]
    n = seg_(d1 - d0)
    tt = np.arange(n) / SR
    drone = (np.sin(2 * np.pi * (41 + 5 * tt / (d1 - d0)) * tt) + 0.6 * np.sin(2 * np.pi * 55.3 * tt)
             + 0.3 * np.sin(2 * np.pi * 82.7 * tt))
    drone += _filt(rng.standard_normal(n).astype(np.float32), 110, "low") * 1.6
    drone = drone.astype(np.float32) * (0.15 + 0.85 * (tt / (d1 - d0)) ** 2) * 0.14
    drone[-seg_(0.03):] *= np.linspace(1, 0, seg_(0.03))
    por("drone", drone, d0)

    # cortes de CFTV
    for s in cftv:
        por("sfx", ruido_estatica(rng, 2 / C.FPS + 0.03), s["t0"] - 0.02, 0.7)
        if s["var"] in ("festa", "varanda"):
            por("sfx", impacto(rng, 1.4, 45), s["t0"], 0.7)
            if s["var"] == "festa":   # a festa fica alta por um instante
                for j in range(5):
                    por("festa", tilintar(rng) * 2.0, s["t0"] + 0.1 + j * 0.16, 1.0, pan=rng.uniform(-.5, .5))
        else:
            tg = s["t0"] + 0.30
            while tg < s["t1"]:
                por("sfx", gota(), tg, 0.55, pan=0.3)
                tg += C.GOTA_PERIODO
        if s["var"] == "perto":
            por("sfx", impacto(rng, 1.6, 36), s["t0"], 0.9)
            por("voz", V.corrompida(falas["quem"], -4, 99), s["t_voz"], 1.2)

    # soma
    mix = sum(st.values())
    for ev in eventos:
        a, b = seg_(ev["f0"] / C.FPS), min(N, seg_((ev["f0"] + ev["nf"]) / C.FPS))
        if b <= a:
            continue
        g = 0.15 if ev["tipo"] == "dropout" else 0.4
        mix[a:b] *= g
        ru = rng.standard_normal((b - a, 2)).astype(np.float32) * ((rng.random((b - a, 1)) < 0.03) * 0.4 + 0.02)
        mix[a:b] += ru * 0.5
    mix += base

    # corte seco: estática no fim do último CFTV, depois silêncio absoluto
    fim = cftv[-1]["t1"]
    por_estat = ruido_estatica(rng, 0.12)
    a = seg_(fim - 0.12)
    mix[a:a + len(por_estat)] = por_estat * 1.2
    p = seg["preto"]
    mix[seg_(p["t0"]):seg_(p["t1"])] = 0.0
    if "cartao" in seg:
        c = seg["cartao"]
        mix[seg_(c["t0"]):] = base[seg_(c["t0"]):] * 0.25

    mix = mix[: int(total * SR)]
    nz = np.abs(mix[np.abs(mix) > 1e-6])
    mix = mix / (np.percentile(nz, 99.0) + 1e-9) * 0.55
    lim = 0.7
    ac = np.abs(mix) > lim
    mix[ac] = np.sign(mix[ac]) * (lim + (1 - lim) * np.tanh((np.abs(mix[ac]) - lim) / (1 - lim)))
    mix = mix / np.abs(mix).max() * (10 ** (-1 / 20))
    C.SAIDA.mkdir(parents=True, exist_ok=True)
    sf.write(C.SAIDA / "audio.wav", mix, SR, subtype="PCM_16")
    return C.SAIDA / "audio.wav"
