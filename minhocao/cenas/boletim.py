"""Blocos 2 e 3 — Boletim do Rio (normal) e o boletim saindo do script."""
import numpy as np
from PIL import Image, ImageDraw

import config as C
import icones
from .comum import (CTX, VT, fonte, nova, desenho, texto, centro, quebra,
                    caixa_texto, embaralha, rng_frame, caminho_rio)

PETROLEO = (22, 84, 96)
MUSGO = (78, 98, 52)
MUSGO_ESC = (60, 78, 40)
AZUL_RIO = (70, 140, 210)


# ---------------------------------------------------------------------------
def peixinho(img, x, y, t, escala=3, nome="peixe"):
    ic = icones.icone_escalado(nome, 16 * escala)
    yy = int(y + 4 * np.sin(t * 6))
    img.paste(ic, (int(x), yy), ic)


def vinheta(t, i):
    img = nova(PETROLEO)
    d = desenho(img)
    # faixas de sol estilo anos 70
    for k, cor in enumerate([(240, 170, 40), (230, 120, 40), (200, 70, 50)]):
        y0 = 120 + k * 14
        d.rectangle([0, y0, C.W, y0 + 8], fill=cor)
    # ondinhas
    for k in range(6):
        y0 = 380 + k * 18
        pts = [(x, y0 + 4 * np.sin(x * 0.08 + t * 3 + k)) for x in range(0, C.W + 4, 4)]
        d.line(pts, fill=(120, 200, 210) if k % 2 == 0 else (60, 150, 170), width=3)
    # título deslizando
    dt = t - 6.0
    x_off = int(max(0, 1 - dt / 0.6) * -C.W)
    f1 = fonte(VT, 56)
    f2 = fonte(VT, 26)
    texto(d, (C.W // 2 + x_off + 3, 196 + 3), "BOLETIM", f1, (10, 30, 40), ancora="ma")
    texto(d, (C.W // 2 + x_off, 196), "BOLETIM", f1, (255, 220, 60), ancora="ma")
    texto(d, (C.W // 2 - x_off + 3, 246 + 3), "DO RIO", f1, (10, 30, 40), ancora="ma")
    texto(d, (C.W // 2 - x_off, 246), "DO RIO", f1, (255, 220, 60), ancora="ma")
    if dt > 0.8:
        d.rectangle([40, 316, C.W - 40, 346], fill=(250, 245, 230))
        centro(d, 318, "— " + C.SUBTITULO + " —", f2, (22, 84, 96))
    # peixinho atravessando
    px = -60 + (dt / 3.0) * (C.W + 120)
    peixinho(img, px, 440, t)
    peixinho(img, C.W - px * 0.7, 490, t + 1, escala=2)
    return img


# ---------------------------------------------------------------------------
def desenha_mapa(img, t, i, corrupcao=0.0):
    d = desenho(img)
    x0, y0, x1, y1 = 12, 92, 268, 430
    d.rectangle([x0, y0, x1, y1], fill=MUSGO)
    # textura de mapa (quadriculado de TV)
    for gx in range(x0, x1, 32):
        d.line([gx, y0, gx, y1], fill=MUSGO_ESC)
    for gy in range(y0, y1, 32):
        d.line([x0, gy, x1, gy], fill=MUSGO_ESC)
    pts = caminho_rio()
    # traço escuro da criatura (bloco 3): maior que o rio, segue as curvas
    if corrupcao > 0:
        rng = rng_frame(i, 5)
        n = len(pts)
        prog = np.clip((t - 21.4) / 4.0, 0, 1)
        a = int(n * (0.5 - 0.6 * prog))
        b = int(n * (0.5 + 0.6 * prog))
        a, b = max(0, a), min(n, b)
        if b - a > 2:
            seg = pts[a:b].copy()
            seg[:, 0] += 5 * np.sin(np.linspace(0, 9, len(seg)) + t * 4)
            seg[:, 1] += 3
            lw = 22 + int(3 * np.sin(t * 3))
            d.line([tuple(p) for p in seg], fill=(14, 16, 12), width=lw, joint="curve")
            # o traço continua para fora do mapa
            if prog > 0.6:
                d.line([(seg[0][0], seg[0][1]), (seg[0][0] - 10, y0 - 4)], fill=(14, 16, 12), width=lw)
                d.line([(seg[-1][0], seg[-1][1]), (seg[-1][0] + 6, y1 + 4)], fill=(14, 16, 12), width=lw)
    # o rio
    cor_rio = AZUL_RIO if corrupcao < 0.5 else (60, 90, 120)
    d.line([tuple(p) for p in pts], fill=cor_rio, width=9, joint="curve")
    d.line([tuple(p) for p in pts], fill=(150, 200, 240), width=2)
    # córrego do Pari entrando pela margem esquerda (oeste)... e lugares
    lugares = [
        ("GUIA", 0.06, +1, "igreja"),
        ("BARRA DO PARI", 0.36, +1, "canoa"),
        ("PORTO", 0.62, +1, "gota"),
        ("VÁRZEA GRANDE", 0.80, -1, "igreja"),
    ]
    f = fonte(VT, 18)
    rng = rng_frame(i, 9)
    for nome, s, lado, ic in lugares:
        px, py = pts[int(s * (len(pts) - 1))]
        mx = px + lado * 16
        d.ellipse([mx - 3, py - 3, mx + 3, py + 3], fill=(250, 230, 80), outline=(0, 0, 0))
        lbl = nome
        if corrupcao > 0.5 and rng.random() < 0.15:
            lbl = embaralha(nome, rng, 0.4)
        if lado > 0:
            tx = mx + 6
            larg = f.getlength(lbl)
            if tx + larg > x1 - 2:
                tx = x1 - 2 - larg
            ty = py - 6
        else:
            tx = mx - 6 - f.getlength(lbl)
            tx = max(x0 + 2, tx)
            ty = py + 6
        d.rectangle([tx - 2, ty + 2, tx + f.getlength(lbl) + 2, ty + 16], fill=(20, 26, 14))
        texto(d, (tx, ty), lbl, f, (250, 250, 235))
    texto(d, (x0 + 4, y1 - 20), "RIO CUIABÁ", f, (190, 220, 245))
    d.rectangle([x0, y0, x1, y1], outline=(230, 230, 200), width=2)
    return pts


def regua(img, t, i, nivel_txt, nivel_val, alerta=False):
    d = desenho(img)
    x0, y0, x1, y1 = 286, 92, 348, 430
    d.rectangle([x0, y0, x1, y1], fill=(16, 30, 40))
    rx0, rx1 = 300, 322
    topo, base = y0 + 10, y1 - 40
    # escala: 0 m na base, 14 m no topo
    m2y = lambda m: base - (m / 14.0) * (base - topo)
    for m in range(0, 14):
        ya, yb = m2y(m + 1), m2y(m)
        cor = (250, 205, 30) if m % 2 == 0 else (20, 20, 20)
        d.rectangle([rx0, ya, rx1, yb], fill=cor)
    # água
    yl = m2y(min(nivel_val, 14.5))
    d.rectangle([x0 + 2, max(y0 + 2, yl), x1 - 2, base], fill=(40, 90, 150))
    d.line([x0 + 2, yl, x1 - 2, yl], fill=(255, 60, 40) if alerta else (180, 220, 255), width=2)
    for m in range(0, 14):
        ya, yb = m2y(m + 1), m2y(m)
        if yb > yl:
            cor = (150, 125, 40) if m % 2 == 0 else (14, 20, 40)
            d.rectangle([rx0, max(ya, yl), rx1, yb], fill=cor)
    for m in range(2, 14, 4):
        texto(d, (rx1 + 3, m2y(m) - 9), str(m), fonte(VT, 18), (240, 240, 220), sombra=(0, 0, 0))
    f = fonte(VT, 20)
    texto(d, ((x0 + x1) // 2, base + 4), "NÍVEL", f, (240, 240, 220), ancora="ma")
    cor = (255, 70, 50) if alerta and (i // 4) % 2 else (255, 230, 80)
    texto(d, ((x0 + x1) // 2, base + 18), nivel_txt, f, cor, ancora="ma")
    d.rectangle([x0, y0, x1, y1], outline=(230, 230, 200), width=2)


def cabecalho(img, t, corrompido=False):
    d = desenho(img)
    d.rectangle([0, C.SAFE_TOP, C.W, C.SAFE_TOP + 24], fill=(250, 245, 230))
    f = fonte(VT, 22)
    txt = "BOLETIM DO RIO — AVISO AOS PESCADORES"
    if corrompido:
        txt = "BOLETIM DO RIO — RIO FECHADO"
    centro(d, C.SAFE_TOP + 2, txt, f, (22, 84, 96) if not corrompido else (150, 20, 20))


def legenda(img, s, cor=(255, 255, 255)):
    d = desenho(img)
    f = fonte(VT, 22)
    linhas = quebra(s.upper(), f, 320)
    caixa_texto(d, 482, linhas, f, cor, (0, 0, 0), passo=20, pad=5)


def fala_atual(chave_lista, t):
    """Retorna (índice, texto) da frase falada em t, ou (None, None)."""
    for k, (ini, fim, txt) in enumerate(CTX["voz"].get(chave_lista, [])):
        if ini - 0.05 <= t <= fim + 0.25:
            return k, txt
    return None, None


def icones_boletim(img, t, i, corrompido=False):
    """Ícones que pipocam em sincronia com as frases do locutor."""
    falas = CTX["voz"].get("boletim", [])
    rng = rng_frame(i, 3)
    xs = [52, 128, 204, 280]
    k = 0
    for j, (ini, fim, txt) in enumerate(falas):
        nome = C.FALAS_BOLETIM[j][1]
        if nome == "gota":
            continue
        frames = int((t - ini) * C.FPS)
        if frames >= 0 and k < len(xs):
            inv = corrompido and rng.random() < 0.08
            icones.cola_icone(img, nome, xs[k], 452, 36, frames,
                              corrompido=corrompido and rng.random() < 0.5,
                              invertido=inv, tremer=2 if corrompido else 0, rng=rng)
        k += 1


def mapa(t, i):
    img = nova(PETROLEO)
    cabecalho(img, t)
    desenha_mapa(img, t, i)
    nivel = 5.6 + 0.6 * np.clip((t - C.T_VINHETA_FIM) / 9.0, 0, 1)
    regua(img, t, i, f"{nivel:.1f}".replace(".", ",") + " M", nivel)
    icones_boletim(img, t, i)
    _, s = fala_atual("boletim", t)
    if s:
        legenda(img, s)
    peixinho(img, ((t - 9) * 40) % (C.W + 60) - 50, 504, t, escala=1)
    return img


def cena_boletim(t, i):
    if t < C.T_VINHETA_FIM:
        return vinheta(t, i)
    return mapa(t, i)


# ---------------------------------------------------------------------------
def cena_fora_script(t, i):
    rng = rng_frame(i, 1)
    img = nova((18, 60, 70))
    cabecalho(img, t, corrompido=t > C.T_VOZ_CORRECAO)
    desenha_mapa(img, t, i, corrupcao=0.4 + 0.6 * np.clip((t - 21) / 3, 0, 1))
    # régua disparando
    txt, val = "8,4 M", 8.4
    for tt, v in C.T_REGUA:
        if t >= tt:
            if v is None:
                txt = embaralha("00,0", rng, 1.0, "0123456789?") + " M"
                if rng.random() < 0.3:
                    txt = "??,? M"
                val = 13.5 + rng.random() * 2
            else:
                txt, val = v + " M", float(v.replace(",", "."))
    regua(img, t, i, txt, val, alerta=True)
    icones_boletim(img, t, i, corrompido=True)
    # serpente piscando sobre a Barra do Pari
    if t > 23.0 and (i // 5) % 2 == 0:
        px, py = caminho_rio()[int(0.36 * 399)]
        icones.cola_icone(img, "serpente", px - 2, py - 22, 34, rng=rng, tremer=1)
    _, s = fala_atual("lenta", t)
    if s:
        legenda(img, s, (230, 230, 230))
    _, s = fala_atual("correcao", t)
    if s:
        legenda(img, s, (255, 90, 70))
    return img


def estilo_boletim(t):
    return C.FX_INTENSIDADE["boletim"], "quente"


def estilo_fora(t):
    return C.FX_INTENSIDADE["fora_script"], "quente"
