"""Mixagem procedural: chiado, zumbido, tons, órgão, máquina de escrever,
ambiente do rio, sonar, drone do contato e drop-outs sincronizados.

Todos os efeitos são sintetizados aqui (sem amostras externas)."""
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

import config as C
from cenas import regras, sonar, margem

SR = C.SR


def _t(n):
    return np.arange(n) / SR


def _filtro(x, tipo, f, ordem=2):
    sos = butter(ordem, f, btype=tipo, fs=SR, output="sos")
    return sosfilt(sos, x).astype(np.float32)


def _env(n, ataque=0.005, decai=0.1):
    t = _t(n)
    return (np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-t / decai)).astype(np.float32)


class Mix:
    def __init__(self, dur):
        self.n = int(dur * SR)
        self.m = np.zeros(self.n, np.float32)
        self.rng = np.random.default_rng(C.SEED + 99)

    def add(self, t0, x, ganho=1.0):
        a = int(t0 * SR)
        if a >= self.n or a + len(x) <= 0:
            return
        xa = 0
        if a < 0:
            xa, a = -a, 0
        b = min(self.n, a + len(x) - xa)
        self.m[a:b] += x[xa: xa + b - a] * ganho

    def faixa(self, t0, t1):
        return slice(int(t0 * SR), min(self.n, int(t1 * SR)))


# ---------------------------------------------------------------------------
# Instrumentos
# ---------------------------------------------------------------------------
def tom(freq, dur, forma="sin", ataque=0.003, decai=None):
    n = int(dur * SR)
    t = _t(n)
    if forma == "sin":
        x = np.sin(2 * np.pi * freq * t)
    elif forma == "quad":
        x = np.sign(np.sin(2 * np.pi * freq * t)) * 0.6
    else:
        x = 2 * ((t * freq) % 1) - 1
    env = np.ones(n)
    env *= np.minimum(1, t / ataque)
    env *= np.minimum(1, (dur - t) / 0.01)
    if decai:
        env *= np.exp(-t / decai)
    return (x * env).astype(np.float32)


def bipe2(f1=880, f2=1320):
    return np.concatenate([tom(f1, 0.09, "quad"), tom(f2, 0.11, "quad")])


def tecla(rng):
    n = int(0.05 * SR)
    clique = rng.normal(0, 1, n).astype(np.float32) * _env(n, 0.0005, 0.004)
    clique = _filtro(clique, "high", 2500)
    corpo = np.sin(2 * np.pi * rng.uniform(700, 1000) * _t(n)) * _env(n, 0.001, 0.012)
    golpe = rng.normal(0, 1, n) * _env(n, 0.001, 0.02)
    golpe = _filtro(golpe.astype(np.float32), "band", [150, 600])
    return (clique * 0.9 + corpo * 0.35 + golpe * 0.6).astype(np.float32)


def clunk(rng):
    n = int(0.35 * SR)
    t = _t(n)
    baque = np.sin(2 * np.pi * (70 - 30 * t) * t) * _env(n, 0.002, 0.08)
    mec = _filtro(rng.normal(0, 1, n).astype(np.float32), "band", [800, 3000]) * _env(n, 0.001, 0.03)
    return (baque * 0.8 + mec * 0.5).astype(np.float32)


def orgao(t0, t1, notas, baixo, passo, velocidade, ganho_curva, rng):
    """Órgão eletrônico anos 70 com wow; `velocidade(t)` desacelera a fita."""
    n = int((t1 - t0) * SR)
    tt = t0 + _t(n)
    vel = velocidade(tt) * (1 + 0.004 * np.sin(2 * np.pi * 0.7 * tt) + 0.0015 * np.sin(2 * np.pi * 6 * tt))
    tau = np.cumsum(vel) / SR  # tempo de fita
    out = np.zeros(n, np.float32)
    for seq, oit, amp, mult in [(notas, 0, 0.55, 1), (baixo, -24, 0.45, 2)]:
        idx = (tau / (passo * mult)).astype(int) % len(seq)
        frac = (tau / (passo * mult)) % 1
        semis = np.array([s if s is not None else -999 for s in seq])[idx]
        ativo = semis > -900
        f = 523.25 * 2 ** ((semis + oit) / 12) * vel
        fase = np.cumsum(2 * np.pi * f / SR)
        voz = (np.sin(fase) + 0.5 * np.sin(2 * fase) + 0.3 * np.sin(3 * fase) + 0.18 * np.sin(4 * fase)
               + 0.1 * np.sin(6 * fase))
        env = np.minimum(1, frac / 0.04) * np.minimum(1, (1 - frac) / 0.08)
        out += (voz * env * ativo * amp).astype(np.float32)
    # leslie leve
    out *= (1 + 0.15 * np.sin(2 * np.pi * 5.5 * tt)).astype(np.float32)
    out = _filtro(out, "low", 4200)
    return out * ganho_curva(tt).astype(np.float32)


def ruido_rosa(n, rng):
    b = rng.normal(0, 1, n).astype(np.float32)
    b = _filtro(b, "low", 1200, 1) * 0.6 + b * 0.08
    return b


# ---------------------------------------------------------------------------
def gera_mix(voz, eventos):
    dur = C.DURACAO
    M = Mix(dur)
    rng = M.rng
    n = M.n
    T = _t(n)

    # --- base: chiado de fita + zumbido 60 Hz --------------------------------
    chiado = _filtro(rng.normal(0, 1, n).astype(np.float32), "high", 1800) * 0.018
    zumbido = (np.sin(2 * np.pi * 60 * T) * 0.008 + np.sin(2 * np.pi * 120 * T) * 0.004
               + np.sin(2 * np.pi * 180 * T) * 0.002).astype(np.float32)
    nivel_base = np.ones(n, np.float32)
    nivel_base[M.faixa(C.T_CARTAO_REAL, C.T_STOP)] = 0.35
    M.m += (chiado + zumbido) * nivel_base

    # --- abertura --------------------------------------------------------------
    M.add(0.0, clunk(rng), 0.6)
    M.add(C.T_PLAY_FIM, tom(1000, C.BLOCOS[0][2] - C.T_PLAY_FIM, ataque=0.002), 0.22)
    s = M.faixa(C.T_ETIQUETA, C.T_ETIQUETA + 2 / C.FPS)
    M.m[s] = rng.normal(0, 0.3, M.m[s].shape).astype(np.float32)

    # --- vinheta + cama de órgão; desafina e desacelera no bloco 3 --------------
    notas = [0, 4, 7, 4, 5, 9, 7, None, 4, 7, 12, 7, 9, 5, 7, None]
    baixo = [-12, -5, -7, -5]
    vel = lambda tt: np.where(tt < 20.0, 1.0, np.clip(1 - (tt - 20.0) / 3.2, 0.25, 1.0))
    def ganho(tt):
        g = np.where(tt < 9.0, 0.45, 0.10)
        g = np.where(tt < 6.15, 0.45 * np.clip((tt - 6.0) / 0.15, 0, 1), g)
        g = np.where(tt >= 20.0, 0.22, g)
        return g
    M.add(6.0, orgao(6.0, 22.6, notas, baixo, 0.2, vel, ganho, rng), 1.0)
    # desafino: segunda voz fora do tom no bloco 3
    M.add(20.0, orgao(20.0, 22.6, notas, baixo, 0.2,
                      lambda tt: vel(tt) * 0.97, lambda tt: np.full_like(tt, 0.12), rng), 1.0)

    # --- ícones com bipe -------------------------------------------------------
    from cenas.comum import CTX
    for j, (ini, fim, _) in enumerate(CTX["voz"].get("boletim", [])):
        if C.FALAS_BOLETIM[j][1] != "gota":
            M.add(ini, tom(1250, 0.08, "quad"), 0.12)
    for tt, v in C.T_REGUA:
        M.add(tt, tom(620 if v else 210, 0.25, "quad", decai=0.2), 0.14)

    # --- voz -----------------------------------------------------------------
    M.m += voz * 0.62

    # --- regras: máquina de escrever + bipe de 2 tons -------------------------
    for tt in regras.tempos_teclas():
        M.add(tt + rng.uniform(-0.004, 0.004), tecla(rng), 0.22 * rng.uniform(0.7, 1.0))
    for tt in regras.tempos_bipes():
        M.add(tt - 0.22, bipe2(), 0.13)
    # golpe grave quando aparece "1968"
    t68 = regras.t_1968()
    nn = int(2.5 * SR)
    golpe = (np.sin(2 * np.pi * 41 * _t(nn)) + 0.4 * np.sin(2 * np.pi * 61.5 * _t(nn))) * _env(nn, 0.01, 0.9)
    M.add(t68, golpe.astype(np.float32), 0.5)

    # --- sonar ---------------------------------------------------------------
    for p in sonar.PINGS:
        ping = tom(1850, 0.35, ataque=0.002, decai=0.07)
        M.add(p, ping, 0.22)
        if p < C.T_CRIATURA_SONAR + 1.0:
            M.add(p + 0.11, ping, 0.06)
    tc0 = C.T_CRIATURA_SONAR
    nn = int((59.0 - tc0) * SR)
    tt = _t(nn)
    eco = (np.sin(2 * np.pi * 55 * tt) + 0.6 * np.sin(2 * np.pi * 56.3 * tt) + 0.3 * np.sin(2 * np.pi * 110.5 * tt))
    eco *= np.clip(tt / 3.0, 0, 1) ** 1.5 * np.minimum(1, (tt[-1] - tt) / 0.05)
    M.add(tc0, eco.astype(np.float32), 0.38)

    # --- margem: ambiente do rio ----------------------------------------------
    c0, c1, c2, c3 = C.T_CORTES_MARGEM
    t_fim_m = 66.0
    nn = int((t_fim_m - c0) * SR)
    tt = _t(nn)
    agua = ruido_rosa(nn, rng)
    agua = _filtro(agua, "band", [120, 1600]) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.3 * tt))
    M.add(c0, agua.astype(np.float32), 0.35)
    # sapos e grilos (corte total na canoa virada)
    vivos = (c0 + tt) < c2
    grilo = np.sin(2 * np.pi * 4600 * tt) * (np.sin(2 * np.pi * 32 * tt) > 0.2) * \
        (np.sin(2 * np.pi * 2.1 * tt) > 0.3)
    grilo2 = np.sin(2 * np.pi * 5200 * tt) * (np.sin(2 * np.pi * 28 * tt + 1) > 0.3) * \
        (np.sin(2 * np.pi * 1.6 * tt + 2) > 0.5)
    sapo = np.zeros(nn, np.float32)
    for k in range(18):
        ts = rng.uniform(0, c2 - c0 - 0.2)
        f = rng.uniform(260, 460)
        nc = int(rng.uniform(0.15, 0.35) * SR)
        tc = _t(nc)
        cro = np.sign(np.sin(2 * np.pi * f * tc)) * (np.sin(2 * np.pi * rng.uniform(11, 16) * tc) > 0)
        cro = _filtro(cro.astype(np.float32), "band", [200, 1400]) * np.minimum(1, (tc[-1] - tc) / 0.02)
        a = int(ts * SR)
        sapo[a:a + nc] += cro[: len(sapo[a:a + nc])] * rng.uniform(0.5, 1.0)
    noite = (grilo * 0.05 + grilo2 * 0.035 + sapo * 0.16) * vivos
    M.add(c0, noite.astype(np.float32), 1.0)
    # motor de rabeta distante (corte 1)
    nn1 = int((c1 - c0) * SR)
    t1 = _t(nn1)
    rabeta = np.sign(np.sin(2 * np.pi * (29 + 1.5 * np.sin(2 * np.pi * 0.4 * t1)) * t1))
    rabeta = _filtro(rabeta.astype(np.float32), "low", 320) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * t1))
    M.add(c0, rabeta * np.minimum(1, (t1[-1] - t1) / 0.03), 0.05)
    # canoa batendo na madeira da estaca (remo / casco)
    for ts in (c0 + 0.4, c0 + 1.25, c1 + 0.3, c1 + 1.1, c1 + 1.25, c1 + 1.45):
        nk = int(0.2 * SR)
        k = np.sin(2 * np.pi * 210 * _t(nk)) * _env(nk, 0.001, 0.04) + \
            _filtro(rng.normal(0, 1, nk).astype(np.float32), "band", [300, 1200]) * _env(nk, 0.001, 0.02)
        M.add(ts, k.astype(np.float32), 0.25)
    # corte 2: corcova passando — ronco grave, onda batendo, madeira rangendo
    nn2 = int(1.75 * SR)
    t2 = _t(nn2)
    ronco = (np.sin(2 * np.pi * 38 * t2) + _filtro(rng.normal(0, 1, nn2).astype(np.float32), "low", 140) * 2.0)
    ronco *= np.sin(np.pi * t2 / 1.75) * np.minimum(1, (t2[-1] - t2) / 0.02)
    M.add(c1, ronco.astype(np.float32), 0.3)
    no = int(0.9 * SR)
    onda = _filtro(rng.normal(0, 1, no).astype(np.float32), "low", 900) * \
        np.sin(np.pi * np.clip(_t(no) / 0.9, 0, 1)) ** 2
    M.add(c1 + 0.75, onda * np.minimum(1, (c2 - c1 - 0.75 - _t(no)) * 50).clip(0, 1), 0.5)
    nr = int(0.7 * SR)
    tr = _t(nr)
    ranger = 2 * ((np.cumsum(40 + 35 * np.sin(2 * np.pi * 1.3 * tr)) / SR) % 1) - 1
    ranger = _filtro(ranger.astype(np.float32), "band", [500, 1800]) * np.sin(np.pi * tr / 0.7)
    M.add(c1 + 0.95, ranger, 0.22)
    # corte 4: barranco desmoronando (estrondo grave + terra caindo na água)
    nb = int(1.75 * SR)
    tb = _t(nb)
    estrondo = np.sin(2 * np.pi * (48 - 14 * tb) * tb) * _env(nb, 0.01, 0.7) + \
        _filtro(rng.normal(0, 1, nb).astype(np.float32), "low", 220) * _env(nb, 0.02, 0.9) * 2
    M.add(c3 + 0.12, (estrondo * np.minimum(1, (tb[-1] - tb) / 0.02)).astype(np.float32), 0.45)
    for (x, y, w, h, atraso) in margem._PEDACOS:
        timpacto = c3 + atraso + np.sqrt(2 * (margem.Y_AGUA1 - 8 - y) / 900)
        ns = int(0.3 * SR)
        sp = _filtro(rng.normal(0, 1, ns).astype(np.float32), "band", [300, 2800]) * _env(ns, 0.003, 0.08)
        M.add(timpacto, sp, 0.35 * min(1, (66.0 - timpacto) * 5))
    terra = _filtro(rng.normal(0, 1, nb).astype(np.float32), "band", [1500, 6000]) * \
        (rng.random(nb) < 0.02) * _env(nb, 0.3, 0.6)
    M.add(c3 + 0.2, terra.astype(np.float32) * np.minimum(1, (tb[-1] - tb) / 0.02), 0.5)

    # --- contato: órgão de tubos debaixo d'água --------------------------------
    t0c, t1c = 66.0, C.T_PRETO
    nc = int((t1c - t0c) * SR)
    tc = _t(nc)
    f0 = 36.7 * (1 + 0.01 * np.sin(2 * np.pi * 0.07 * tc))
    fase = np.cumsum(2 * np.pi * f0 / SR)
    drone = np.zeros(nc)
    for k in range(1, 9):
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * (0.05 + 0.03 * k) * tc + k * 1.7)
        drone += np.sin(k * fase + k) / k * lfo
    resp = 0.55 + 0.45 * np.sin(2 * np.pi * tc / 3.4 - np.pi / 2) ** 2  # "respiração" do rio
    drone = _filtro((drone * resp).astype(np.float32), "low", 380)
    drone *= np.clip(tc / 0.8, 0, 1)
    M.add(t0c, drone.astype(np.float32), 0.55)

    # --- fim -----------------------------------------------------------------
    M.add(C.T_FIM_TEXTO + 0.1, orgao(0, 1.4, [7, 4, 0, None], [-12], 0.25,
                                     lambda tt: 1 - tt * 0.35, lambda tt: np.full_like(tt, 0.15), rng), 1.0)
    M.add(C.T_STOP, clunk(rng), 0.6)

    # --- eventos sincronizados com o vídeo ------------------------------------
    for ev in eventos:
        s = M.faixa(ev["t"], ev["t"] + ev["dur"])
        ln = len(range(*s.indices(n)))
        if ln <= 0:
            continue
        if ev["tipo"] == "estatica":
            M.m[s] = M.m[s] * 0.15 + rng.normal(0, 0.28, ln).astype(np.float32)
        elif ev["tipo"] == "glitch":
            bloco = M.m[s].copy()
            pedaco = bloco[: max(1, int(0.025 * SR))]
            rep = np.tile(pedaco, ln // len(pedaco) + 1)[:ln]
            buzz = np.sign(np.sin(2 * np.pi * 118 * _t(ln))) * 0.12
            M.m[s] = rep * 0.7 + buzz.astype(np.float32)
        elif ev["tipo"] == "dropout":
            M.m[s] *= 0.05
        elif ev["tipo"] == "subliminar":
            M.m[s] = rng.normal(0, 0.5, ln).astype(np.float32) + \
                np.sin(2 * np.pi * 55 * _t(ln)).astype(np.float32) * 0.4

    # --- silêncio absoluto no corte para preto ---------------------------------
    sil = M.faixa(C.T_PRETO, C.BLOCOS[-2][2])

    # estéreo: chiado descorrelacionado nas laterais
    lat = _filtro(rng.normal(0, 1, n).astype(np.float32), "high", 3000) * 0.006
    L = M.m + lat
    R = M.m - lat
    st = np.stack([L, R], 1)
    st[sil] = 0.0
    pico = np.abs(st).max()
    st *= 10 ** (-1 / 20) / pico  # pico em -1 dBFS
    st[sil] = 0.0
    return st.astype(np.float32), M.m * (10 ** (-1 / 20) / pico)


def salva(st, caminho):
    sf.write(str(caminho), st, SR, subtype="PCM_16")
