"""Bloco 4 — Serviço de avisos aos pescadores: as 7 regras."""
import numpy as np

import config as C
import icones
from .comum import VT, fonte, nova, desenho, texto, centro, quebra, rng_frame

MARINHO = (10, 16, 92)
F_REGRA = 20
PASSO = 17
X_TXT = 44
LARG_TXT = C.W - X_TXT - 12


def _layout():
    f = fonte(VT, F_REGRA)
    y = 134
    out = []
    for nome, txt in C.REGRAS:
        linhas = quebra(txt, f, LARG_TXT)
        out.append((nome, linhas, y))
        y += len(linhas) * PASSO + 9
    return out, y


LAYOUT, Y_FIM = _layout()


def inicio_regra(k):
    return C.T_REGRAS0 + k * C.DT_REGRA


def fim_digitacao(k):
    return inicio_regra(k) + len(C.REGRAS[k][1]) / C.CPS_REGRA


def t_1968():
    return fim_digitacao(6) + C.T_1968_ATRASO


def tempos_teclas():
    """Instantes de cada tecla (para o áudio da máquina de escrever)."""
    out = []
    for k, (_, txt) in enumerate(C.REGRAS):
        t0 = inicio_regra(k)
        for c, ch in enumerate(txt):
            if ch != " ":
                out.append(t0 + c / C.CPS_REGRA)
    t0 = t_1968()
    for c, ch in enumerate(C.REGRA_1968):
        if ch != " ":
            out.append(t0 + c / (C.CPS_REGRA * 0.6))
    return out


def tempos_bipes():
    return [inicio_regra(k) for k in range(len(C.REGRAS))]


def cena(t, i):
    rng = rng_frame(i, 11)
    img = nova(MARINHO)
    d = desenho(img)
    fh = fonte(VT, 21)
    centro(d, C.SAFE_TOP + 2, C.CABECALHO_REGRAS[0], fh)
    centro(d, C.SAFE_TOP + 20, C.CABECALHO_REGRAS[1], fh)
    d.line([16, C.SAFE_TOP + 42, C.W - 16, C.SAFE_TOP + 42], fill=(255, 255, 255), width=1)
    if (i // 12) % 2 == 0 or t > 30:
        cor = (255, 220, 60) if (i // 10) % 2 else (255, 90, 70)
        centro(d, C.SAFE_TOP + 48, C.LEIA, fonte(VT, 20), cor)
    f = fonte(VT, F_REGRA)
    for k, (nome, linhas, y) in enumerate(LAYOUT):
        t0 = inicio_regra(k)
        if t < t0:
            break
        n = int((t - t0) * C.CPS_REGRA)
        atual = t < inicio_regra(k + 1) if k < 6 else True
        cor = (255, 255, 255) if atual else (175, 182, 215)
        frames = int((t - t0) * C.FPS)
        # ícone piscando ao lado
        piscando = atual and (frames < 18 or (i // 8) % 2 == 0)
        if not atual or piscando:
            icones.cola_icone(img, nome, 24, y + 10, 26, frames)
        resto = n
        for j, ln in enumerate(linhas):
            if resto <= 0:
                break
            parte = ln[:resto]
            resto -= len(ln) + 1
            texto(d, (X_TXT, y + j * PASSO - 3), parte, f, cor)
            if atual and resto < 0 and (i // 4) % 2 == 0:
                cx = X_TXT + f.getlength(parte) + 1
                d.rectangle([cx, y + j * PASSO + 2, cx + 6, y + j * PASSO + 13], fill=cor)
    # "JÁ DERRUBARAM UMA EM 1968." tremendo embaixo da regra 7
    t68 = t_1968()
    if t >= t68:
        n = int((t - t68) * C.CPS_REGRA * 0.6)
        s = C.REGRA_1968[:n]
        f2 = fonte(VT, 28)
        dx, dy = rng.integers(-2, 3, 2)
        y68 = Y_FIM + 10
        texto(d, (C.W // 2 + dx + 2, y68 + dy), s, f2, (90, 0, 0), ancora="ma")
        texto(d, (C.W // 2 + dx, y68 + dy), s, f2, (255, 50, 40), ancora="ma")
    return img


def estilo(t):
    k = C.FX_INTENSIDADE["regras"]
    if t >= t_1968():
        k = 0.6
    return k, "frio"
