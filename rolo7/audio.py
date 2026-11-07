"""Mixagem final -> saida/audio.wav (48 kHz estéreo) + saida/voz_track.npy (para os medidores)."""
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

import config as C
import voz as V

SR = C.SR
N = int(C.DURACAO * SR) + SR // 2


def seg(t):
    return int(round(t * SR))


def _filt(x, f, tipo, ordem=2):
    sos = butter(ordem, f, btype=tipo, fs=SR, output="sos")
    return sosfilt(sos, x).astype(np.float32)


class Mix:
    def __init__(self):
        self.st = {k: np.zeros((N, 2), np.float32) for k in
                   ("base", "voz", "musica", "festa", "sfx", "ui")}
        self.voz_vis = np.zeros(N, np.float32)

    def por(self, trilha, x, t, ganho=1.0, pan=0.0):
        a = seg(t)
        if a >= N or len(x) == 0:
            return
        x = x[: N - a] * ganho
        if x.ndim == 1:
            l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
            self.st[trilha][a:a + len(x), 0] += x * l
            self.st[trilha][a:a + len(x), 1] += x * r
        else:
            self.st[trilha][a:a + len(x)] += x


# ------------------------------------------------------------------ síntese
def env_adsr(n, a=0.005, r=0.05):
    e = np.ones(n, np.float32)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def tom(f, dur, harm=(1, .5, .3, .2), vib=0.0, decai=0.0, detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fase = 2 * np.pi * np.cumsum(f * (1 + vib * np.sin(2 * np.pi * 5.5 * t))) / SR
    x = sum(a * np.sin((k + 1) * fase * (1 + detune * k)) for k, a in enumerate(harm))
    if decai:
        x = x * np.exp(-t * decai)
    return (x * env_adsr(n)).astype(np.float32)


def nota(nome):
    tab = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    n = tab[nome[0]] + (1 if "#" in nome else 0) - (1 if "b" in nome[1:] else 0)
    oit = int(nome[-1])
    return 440.0 * 2 ** ((n + (oit - 4) * 12) / 12)


def clique(rng, forte=1.0):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 300)
    x = _filt(x, 1500, "high") * 0.8
    x += np.sin(2 * np.pi * 1150 * t) * np.exp(-t * 90) * 0.5
    x += np.sin(2 * np.pi * 95 * t) * np.exp(-t * 40) * 0.6
    return (x * forte).astype(np.float32)


def motor(dur, rng, subindo=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rampa = np.clip(t / (dur * 0.7), 0, 1) if subindo else np.ones(n)
    f = 4 + 46 * rampa ** 1.5
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * fase) / k for k in range(1, 9))
    x += 0.25 * np.sin(fase * 12)  # chiado do motor
    x += _filt(rng.standard_normal(n).astype(np.float32), [200, 1200], "band") * 0.3 * rampa
    return (x * 0.18 * np.clip(t / 0.08, 0, 1)).astype(np.float32)


def bipe(f1=880, f2=1320, corr=False, rng=None):
    out = []
    for f in (f1, f2):
        n = int(0.06 * SR)
        t = np.arange(n) / SR
        ff = f * (1 + (0.03 * np.sin(2 * np.pi * 30 * t) if corr else 0))
        x = np.sign(np.sin(2 * np.pi * np.cumsum(ff) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(ff) / SR) * 0.5
        out.append(_filt(x.astype(np.float32), 3500, "low") * env_adsr(n, 0.002, 0.01))
    return np.concatenate(out) * 0.35


def tecla(rng):
    n = int(0.045 * SR)
    t = np.arange(n) / SR
    x = _filt(rng.standard_normal(n).astype(np.float32), [1800, 6500], "band") * np.exp(-t * 180)
    x += np.sin(2 * np.pi * rng.uniform(160, 220) * t) * np.exp(-t * 70) * 0.5
    return x.astype(np.float32) * rng.uniform(0.5, 0.8)


def tilintar(rng):
    f0 = rng.uniform(1700, 2900)
    dur = rng.uniform(0.4, 0.9)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f0 * p * t + rng.uniform(0, 6)) * np.exp(-t * d)
            for p, a, d in ((1, 1, 6), (2.32, .6, 9), (4.25, .35, 14), (6.63, .2, 20)))
    x *= env_adsr(n, 0.001, 0.05)
    return x.astype(np.float32) * 0.3


def piano(f, dur, rng, desafina=0.0):
    f = f * 2 ** (rng.uniform(-desafina, desafina) / 1200)
    return tom(f, dur, harm=(1, .45, .25, .12, .06), decai=3.2, detune=0.0015) * 0.5


def reverb(x, dur=2.4, rng=None, brilho=3000):
    rng = rng or np.random.default_rng(C.SEED + 9)
    n = int(dur * SR)
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-np.linspace(0, 6.5, n)).astype(np.float32)
    ir = _filt(ir, brilho, "low")
    y = fftconvolve(x, ir)[: len(x) + n].astype(np.float32)
    return y / (np.abs(y).max() + 1e-9) * (np.abs(x).max() + 1e-9)


def variar_velocidade(x, taxa):
    """taxa: array por amostra de saída (1 = normal). Fita desacelerando."""
    pos = np.cumsum(taxa)
    pos = pos[pos < len(x) - 1]
    return np.interp(pos, np.arange(len(x)), x).astype(np.float32)


# ------------------------------------------------------------------ músicas
def tema_programa(rng):
    """Tema alegre de órgão barato, 116 bpm, em Fá maior (~19 s em loop)."""
    bpm = 116
    b = 60 / bpm
    mel = ["C5", "A4", "F4", "A4", "C5", "D5", "C5", "A4", "Bb4", "D5", "F5", "D5", "C5", "A4", "G4", "-",
           "A4", "C5", "F5", "E5", "D5", "C5", "Bb4", "A4", "G4", "Bb4", "D5", "C5", "A4", "G4", "F4", "-"]
    acordes = [["F3", "A3", "C4"], ["F3", "A3", "C4"], ["Bb2", "D3", "F3"], ["C3", "E3", "G3"]] * 2
    dur_total = len(mel) * b * 0.5 * 2
    x = np.zeros(int((dur_total + 1) * SR), np.float32)
    for rep in range(2):
        off = rep * len(mel) * b * 0.5
        for k, nn in enumerate(mel):
            if nn == "-":
                continue
            t0 = off + k * b * 0.5
            s = tom(nota(nn), b * 0.45, harm=(1, .6, .35, .25, .1), vib=0.004)
            a = int(t0 * SR)
            x[a:a + len(s)] += s * 0.5
        for k, ac in enumerate(acordes):
            for nn in ac:
                for bt in range(4):
                    if bt % 2 == 1:
                        t0 = off + (k * 4 + bt) * b * 0.5
                        s = tom(nota(nn), b * 0.4, harm=(1, .5, .2), vib=0.003)
                        a = int(t0 * SR)
                        x[a:a + len(s)] += s * 0.18
            # baixo
            t0 = off + k * 4 * b * 0.5
            s = tom(nota(ac[0]) / 2, b * 0.9, harm=(1, .3), decai=2)
            a = int(t0 * SR)
            x[a:a + len(s)] += s * 0.35
    return x / (np.abs(x).max() + 1e-9)


def valsa(dur, rng):
    """Valsa de piano distante e desafinada, 3/4."""
    bpm = 132
    b = 60 / bpm
    prog = [("A2", ["C4", "E4"]), ("E2", ["B3", "D4"]), ("A2", ["C4", "E4"]), ("D2", ["F3", "A3"]),
            ("A2", ["C4", "E4"]), ("E2", ["G#3", "D4"]), ("A2", ["C4", "E4"]), ("E2", ["G#3", "B3"])]
    mel = ["E5", "C5", "A4", "B4", "G#4", "E4", "C5", "A4", "E4", "D5", "A4", "F4",
           "E5", "C5", "A4", "D5", "B4", "G#4", "C5", "B4", "A4", "B4", "-", "-"]
    x = np.zeros(int((dur + 2) * SR), np.float32)
    compasso = 0
    t = 0.0
    while t < dur:
        bx, ac = prog[compasso % len(prog)]
        for bt in range(3):
            a = int((t + bt * b) * SR)
            if bt == 0:
                s = piano(nota(bx), 1.2, rng, 35)
            else:
                s = sum(piano(nota(n), 0.6, rng, 40) for n in ac) * 0.5
            x[a:a + len(s)] += s[: len(x) - a]
            m = mel[(compasso * 3 + bt) % len(mel)]
            if m != "-":
                s = piano(nota(m), 0.9, rng, 45) * 0.8
                x[a:a + len(s)] += s[: len(x) - a]
        compasso += 1
        t += 3 * b * rng.uniform(0.97, 1.05)  # andamento instável
    x = _filt(x, 2200, "low")
    return x[: int(dur * SR)]


# ------------------------------------------------------------------ mixagem
def mixar(eventos, falas=None):
    rng = np.random.default_rng(C.SEED)
    falas = falas or V.gerar_todas()
    M = Mix()
    t_all = np.arange(N) / SR

    # base contínua: chiado + 60 Hz
    hiss = _filt(rng.standard_normal((N, 2)).astype(np.float32).T, [1500, 12000], "band").T * 0.020
    hum = (np.sin(2 * np.pi * 60 * t_all) * 0.010 + np.sin(2 * np.pi * 120 * t_all) * 0.004
           + np.sin(2 * np.pi * 180 * t_all) * 0.002).astype(np.float32)
    M.st["base"] += hiss + hum[:, None]

    # ---------------- bloco 1: o rolo
    M.por("sfx", clique(rng, 1.3), 0.15)
    M.por("sfx", clique(rng, 0.9), 0.32)
    M.por("sfx", motor(5.9, rng), 0.3, 0.5)
    M.por("sfx", motor(13.8, rng, subindo=False) * 0.25, 6.2, 0.3)

    # ---------------- bloco 2: programa
    tema = tema_programa(rng)
    tema = V.wow_flutter(tema, 0.002, 0.0006, rng)
    trecho = np.tile(tema, 2)[: seg(C.T_RETA - C.B2[0])]
    # na corrupção (a partir de 20 s) a fita desacelera e desafina
    n_ok = seg(C.B3[0] - C.B2[0])
    ini = trecho[:n_ok]
    resto = trecho[n_ok:]
    n_corr = seg(C.T_RETA - C.B3[0])
    taxa = np.linspace(1.0, 0.45, n_corr) + 0.05 * np.sin(np.linspace(0, 40, n_corr))
    corr = variar_velocidade(resto, taxa)
    musica = np.concatenate([ini, corr]).astype(np.float32)
    musica = V.passa_banda(musica, 200, 5000)
    gm = np.ones(len(musica), np.float32) * 0.22
    gm[: seg(C.T_VINHETA_FIM - C.B2[0])] = 0.55       # vinheta mais alta
    nr = seg(0.4)
    gm[seg(C.T_VINHETA_FIM - C.B2[0]):seg(C.T_VINHETA_FIM - C.B2[0]) + nr] = np.linspace(0.55, 0.22, nr)
    musica *= gm
    musica[-seg(0.05):] *= np.linspace(1, 0, seg(0.05))
    M.por("musica", musica, C.B2[0])

    def falar(nome, t, ganho=1.0, corr=0.0, semi=0.0, seed=0, reverb=True, trilha="voz", vis=True):
        x = V.tratar_fita(falas[nome], corr, semi, seed, reverb)
        M.por(trilha, x, t, ganho)
        if vis:
            a = seg(t)
            M.voz_vis[a:a + len(x)] += x[: max(0, N - a)] * ganho
        return t + len(x) / SR

    fim_a = falar("fala_a", C.T_FALA_A, 0.9, 0.0, 0, 1)
    falar("fala_b", fim_a - 0.25, 0.9, 0.0, 0, 2)

    for t0, _, _ in C.ICONES_B2:
        M.por("ui", bipe(), t0, 0.7)

    # ---------------- bloco 3: a fita fala com quem escuta
    M.por("sfx", clique(rng, 1.4), C.B3[0])
    t = falar("fala_b", C.T_REPETE, 0.95, 0.4, 1.5, 3, reverb=True) - 0.32
    t = falar("voltar", t, 0.95, 0.6, 3, 4) - 0.3
    t = falar("voltar", t, 0.95, 0.85, 5, 5)
    falar("quem", C.T_QUEM, 1.1, 0.0, 0.5, 6, reverb=False)
    for t0, _, _ in C.CARTOES_B3:
        M.por("ui", bipe(660, 990, True), t0, 0.6)
        M.por("sfx", clique(rng, 0.5), t0)
    for ts in C.SUBLIMINAR_T:
        M.por("sfx", _filt(rng.standard_normal(int(0.04 * SR)).astype(np.float32), 3000, "high") * 0.25, ts)

    # ---------------- bloco 4: regras (teclas + bipes) e festa entrando
    for k, (_, texto) in enumerate(C.REGRAS):
        t0 = C.B4[0] + k * C.REGRA_DUR
        M.por("ui", bipe(), t0, 0.6)
        txt = f"{k + 1}. {texto}"
        for j, ch in enumerate(txt):
            if ch != " ":
                M.por("ui", tecla(rng), t0 + 0.25 + j / len(txt) * C.REGRA_DIGITA, 0.75,
                      pan=rng.uniform(-0.3, 0.3))
        M.por("ui", tecla(rng) * 1.5, t0 + 0.3 + C.REGRA_DIGITA, 0.4)
    M.por("ui", bipe(440, 330, True), C.T_REGRA7_EXTRA, 0.8)
    M.por("sfx", motor(0.8, rng, False) * 0.6, C.T_REGRA7_EXTRA, 0.5)

    # festa: valsa distante + copos, crescendo de 30 s até 66 s
    t_fe0, t_fe1 = C.B4[0], C.B5[1]
    dur_f = t_fe1 - t_fe0
    v = valsa(dur_f, rng)
    v = V.wow_flutter(v, 0.004, 0.001, rng)
    copos = np.zeros(len(v), np.float32)
    tc = 0.5
    while tc < dur_f - 0.5:
        taxa_c = 0.5 + 2.8 * (tc / dur_f) ** 1.5
        s = tilintar(rng)
        a = seg(tc)
        copos[a:a + len(s)] += s[: len(copos) - a]
        if rng.random() < 0.35:  # brinde: dois copos
            s2 = tilintar(rng)
            b2 = a + seg(rng.uniform(0.03, 0.09))
            copos[b2:b2 + len(s2)] += s2[: max(0, len(copos) - b2)]
        tc += rng.exponential(1 / taxa_c)
    # regra 3: um brinde a mais
    t3 = C.B4[0] + 2 * C.REGRA_DUR - t_fe0
    for j in range(5):
        s = tilintar(rng)
        a = seg(t3 + 0.6 + j * 0.32)
        copos[a:a + len(s)] += s * 1.6
    festa = v * 0.6 + copos * 0.7
    wet = reverb(festa, 2.8, rng)[: len(festa)]
    festa = festa * 0.3 + wet * 0.9
    curva = (0.04 + 0.96 * (np.linspace(0, 1, len(festa)) ** 2.2)).astype(np.float32)
    festa *= curva * 0.42 * (1.8 - 0.8 * np.linspace(0, 1, len(festa)))
    festa[-seg(0.1):] *= np.linspace(1, 0, seg(0.1))
    st = np.stack([festa, np.roll(festa, 900)], -1)
    M.por("festa", st, t_fe0)

    # ---------------- bloco 5: CFTV
    # voz do discurso abafada (outro cômodo)
    abaf = np.concatenate([V.tratar_fita(falas["fala_a"], 0.3, 0.7, 7),
                           V.tratar_fita(falas["fala_b"], 0.4, 1.0, 8)])
    abaf = _filt(abaf, 650, "low", 4)
    abaf = reverb(abaf, 1.2, rng, 1500)[: len(abaf) + seg(1.0)] * 0.9
    abaf = abaf[: seg(C.B5[1] - 52.4)]
    abaf[-seg(0.2):] *= np.linspace(1, 0, seg(0.2))
    M.por("voz", abaf, 52.4, 0.55)
    a = seg(52.4)
    M.voz_vis[a:a + len(abaf)] += abaf[: N - a] * 1.4

    # goteira com eco
    def gota():
        n = int(0.05 * SR)
        tt = np.arange(n) / SR
        f = 2100 * np.exp(-tt * 28) + 700
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 70)
        x = x.astype(np.float32)
        out = np.zeros(int(1.6 * SR), np.float32)
        g, d = 1.0, int(0.29 * SR)
        for k in range(6):
            s = x if k == 0 else _filt(x, 3000 / (k + 0.5), "low")
            out[k * d:k * d + n] += s * g
            g *= 0.5
        return out

    gt = C.GOTA_FASE
    while gt < C.B5[1] - 0.3:
        ncam = max(c for c in C.CORTES_CFTV if c[0] <= gt)[1]
        M.por("sfx", gota(), gt, 0.5 if ncam == 3 else 0.18, pan=0.25)
        gt += C.GOTA_PERIODO

    # porta batendo
    n = int(1.2 * SR)
    tt = np.arange(n) / SR
    porta = (np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 7) * 1.0
             + _filt(rng.standard_normal(n).astype(np.float32), 900, "low") * np.exp(-tt * 14) * 1.4
             + _filt(rng.standard_normal(n).astype(np.float32), 2500, "high") * np.exp(-tt * 60) * 0.4)
    porta = reverb(porta.astype(np.float32), 1.0, rng)[:n] * 0.6 + porta * 0.6
    M.por("sfx", porta, C.T_PORTA, 0.7)

    # drone grave crescendo
    d0, d1 = C.B5
    n = seg(d1 - d0)
    tt = np.arange(n) / SR
    cres = (np.linspace(0, 1, n) ** 1.6).astype(np.float32)
    drone = (np.sin(2 * np.pi * (42 + 6 * tt / (d1 - d0)) * tt) + 0.7 * np.sin(2 * np.pi * 55.3 * tt)
             + 0.4 * np.sin(2 * np.pi * 84.5 * tt))
    drone += _filt(rng.standard_normal(n).astype(np.float32), 120, "low") * 2.0
    drone = drone.astype(np.float32) * cres * 0.16
    drone[-seg(0.05):] *= np.linspace(1, 0, seg(0.05))
    M.por("sfx", drone, d0)
    for t0, _, _ in C.ICONES_B5:
        M.por("ui", bipe(990, 740, True), t0, 0.4)

    # ---------------- bloco 6: lado B (fala invertida e mais lenta)
    rev = np.concatenate([V.tratar_fita(V.lado_b(falas[f"ladob_{i}"]), 0.5, 0.5, 10 + i) for i in (3, 2, 1, 0)])
    rev = rev[: seg(C.T_FITA_ARREBENTA - 66.3)]
    M.por("voz", rev, 66.3, 0.95)
    a = seg(66.3)
    M.voz_vis[a:a + len(rev)] += rev * 0.95
    M.por("sfx", motor(C.T_FITA_ARREBENTA - 66.0, rng, False) * 0.3, 66.0)
    # fita arrebenta: estalo + flap-flap
    M.por("sfx", clique(rng, 2.0), C.T_FITA_ARREBENTA)
    tf = C.T_FITA_ARREBENTA + 0.04
    per = 1 / 15
    while tf < C.T_CONGELA:
        n = int(0.025 * SR)
        x = _filt(rng.standard_normal(n).astype(np.float32), [300, 3000], "band") * np.exp(-np.arange(n) / SR * 160)
        M.por("sfx", x * 1.2, tf)
        tf += per
        per *= 1.05
    # zumbido do congelamento
    n = seg(C.T_PRETO - C.T_CONGELA)
    zz = np.sign(np.sin(2 * np.pi * 120 * np.arange(n) / SR)).astype(np.float32) * 0.12
    M.por("sfx", zz, C.T_CONGELA)

    # ---------------- bloco 7: fim, rebobinar, cartões
    n = seg(0.95)
    tt = np.arange(n) / SR
    f = 250 + 2400 * (tt / 0.95) ** 1.3
    reb = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    reb += _filt(rng.standard_normal(n).astype(np.float32), [800, 6000], "band") * (0.5 + 0.5 * np.sin(2 * np.pi * 37 * tt)) * 0.6
    reb = reb.astype(np.float32) * np.clip(tt / 0.1, 0, 1) * 0.6
    M.por("sfx", reb, C.T_REBOBINANDO)
    M.por("sfx", clique(rng, 1.5), C.T_REBOBINANDO + 0.97)
    M.por("sfx", clique(rng, 1.2), C.B7[1])        # STOP
    M.por("sfx", clique(rng, 0.8), C.B7[1] + 0.06)

    # ---------------- soma por trilhas
    mix = sum(M.st[k] for k in ("voz", "musica", "festa", "sfx", "ui"))
    base = M.st["base"].copy()

    # cartão da verdade e ficção: só um chiado muito baixo
    calmo = (t_all >= C.T_VERDADE) & (t_all < C.B7[1])
    base[calmo] *= 0.35

    # drop-outs e glitches sincronizados com o vídeo
    for ev in eventos:
        a, b = seg(ev["f0"] / C.FPS), seg((ev["f0"] + ev["nf"]) / C.FPS)
        b = min(b, N)
        if b <= a:
            continue
        rampa = np.ones(b - a, np.float32)
        k = min(240, (b - a) // 3)
        if ev["tipo"] == "dropout":
            g = 0.12
        else:
            g = 0.35
        env = 1 - (1 - g) * rampa
        if k:
            env[:k] = np.linspace(1, g, k)
            env[-k:] = np.linspace(g, 1, k)
        mix[a:b] *= env[:, None]
        M.voz_vis[a:b] *= env
        ruido = rng.standard_normal((b - a, 2)).astype(np.float32)
        ruido *= (rng.random((b - a, 1)) < 0.02) * 0.4 + 0.03
        mix[a:b] += ruido * (0.6 if ev["tipo"] != "dropout" else 0.4)

    mix += base

    # estática nas transições
    for t0, fa, fd in C.TRANSICOES:
        if fa + fd == 0:
            continue
        a, b = seg(t0 - fa / C.FPS), seg(t0 + fd / C.FPS)
        b = min(b, N)
        ru = _filt(rng.standard_normal((b - a, 2)).astype(np.float32).T, [400, 9000], "band").T * 0.35
        mix[a:b] = mix[a:b] * 0.25 + ru

    # tela azul: só o clique do STOP
    azul = seg(C.B7[1] + 0.25)
    mix[azul:] *= np.linspace(1, 0, N - azul)[:, None] ** 3

    # silêncio absoluto no preto do bloco 6
    a, b = seg(C.T_PRETO), seg(C.B6[1])
    mix[a:b] = 0.0
    M.voz_vis[a:b] = 0.0

    mix = mix[: int(C.DURACAO * SR)]
    # nivelamento: leva o corpo do som a um nível bom e limita os picos (sem clipping)
    ref = np.percentile(np.abs(mix[np.abs(mix) > 1e-6]), 99.0)
    mix = mix / (ref + 1e-9) * 0.55
    lim = 0.7
    acima = np.abs(mix) > lim
    mix[acima] = np.sign(mix[acima]) * (lim + (1 - lim) * np.tanh((np.abs(mix[acima]) - lim) / (1 - lim)))
    pico = np.abs(mix).max()
    mix = mix / pico * (10 ** (-1 / 20))     # -1 dBFS
    C.SAIDA.mkdir(parents=True, exist_ok=True)
    sf.write(C.SAIDA / "audio.wav", mix, SR, subtype="PCM_16")
    np.save(C.SAIDA / "voz_track.npy", (M.voz_vis / (np.abs(M.voz_vis).max() + 1e-9)).astype(np.float16))
    return C.SAIDA / "audio.wav"


# ------------------------------------------------------------------ leitura p/ cenas
_VT = None


def voz_track():
    global _VT
    if _VT is None:
        p = C.SAIDA / "voz_track.npy"
        _VT = np.load(p).astype(np.float32) if p.exists() else np.zeros(N, np.float32)
    return _VT


def voz_env(t, janela=0.05):
    v = voz_track()
    a = seg(t)
    b = a + int(janela * SR)
    if a < 0 or a >= len(v):
        return 0.0
    return float(np.sqrt(np.mean(v[a:b] ** 2)) * 3.2)


def voz_amostras(t, n=180, janela=0.04):
    v = voz_track()
    a = seg(t)
    b = a + int(janela * SR)
    if a < 0 or b >= len(v):
        return np.zeros(n, np.float32)
    x = v[a:b]
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
