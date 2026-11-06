"""00:50–01:02 — alerta de emergência (entidade fictícia)."""
import numpy as np
from PIL import Image

import config as C
import icones
from config import FPS, H, W

from .comum import desenho, fonte, largura, quebrar, rng_frame, texto

VERMELHO = (178, 0, 0)


def cena(t, fi):
    T = fi / FPS
    rng = rng_frame(fi, 4)
    tom = C.alerta_tom_ligado(T)
    img = Image.new("RGB", (W, H), (70, 0, 0) if tom else (0, 0, 0))
    d = desenho(img)

    # faixa do cabeçalho
    linhas = quebrar(C.ALERTA_CAB, 14, 330)
    d.rectangle([0, 62, W, 70 + len(linhas) * 19 + 6], fill=VERMELHO)
    y = 70
    for ln in linhas:
        texto(d, (W // 2, y), ln, 14, (255, 255, 255), sombra=(60, 0, 0), anchor="ma")
        y += 19

    # ⚠ grande piscando
    fr = (T - C.ALERTA_ICONE_T) * FPS
    if (fi // 10) % 2 == 0 or fr < 14:
        icones.colar_animado(img, "aviso", W // 2, 182, 6, fr)
    else:
        icones.colar_animado(img, "aviso", W // 2, 182, 6, 99,
                             paleta={"#": (200, 0, 0), "o": (0, 0, 0), "x": (255, 210, 0)})

    # texto central
    y = 252
    for ti, frase in C.ALERTA_LINHAS:
        if T < ti:
            break
        for ln in quebrar(frase, 16, 330):
            texto(d, (W // 2, y), ln, 16, (255, 255, 255), anchor="ma")
            y += 22
        y += 12

    # crawl na base
    d.rectangle([0, 488, W, 522], fill=VERMELHO)
    d.line([0, 488, W, 488], fill=(255, 255, 255))
    d.line([0, 522, W, 522], fill=(255, 255, 255))
    larg = largura(C.ALERTA_CRAWL, 16)
    x = W - ((T - C.T_ALERTA - 0.4) * 78) % (larg + W)
    texto(d, (x, 496), C.ALERTA_CRAWL, 16, (255, 255, 255))

    # pop-ups de canto
    for tp, nome, (cx, cy) in C.POPUPS:
        if tp <= T < tp + 1.4:
            icones.colar_animado(img, nome, cx, cy, 3, (T - tp) * FPS, corrompido=True, rng=rng)
    return img
