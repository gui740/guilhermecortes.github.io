"""00:00–00:05 — abertura da fita: tela azul, barras SMPTE, flash da etiqueta."""
import math

import numpy as np
from PIL import Image

import config as C
from config import FPS, H, W

from .comum import bloco_centro, desenho, fonte, fonte_mao, nova, rng_frame, texto

_BARRAS_CACHE = {}


def _barras():
    if "b" in _BARRAS_CACHE:
        return _BARRAS_CACHE["b"].copy()
    img = nova()
    d = desenho(img)
    topo = [(191, 191, 191), (191, 191, 0), (0, 191, 191), (0, 191, 0),
            (191, 0, 191), (191, 0, 0), (0, 0, 191)]
    meio = [(0, 0, 191), (16, 16, 16), (191, 0, 191), (16, 16, 16),
            (0, 191, 191), (16, 16, 16), (191, 191, 191)]
    bw = W / 7
    for i, c in enumerate(topo):
        d.rectangle([int(i * bw), 0, int((i + 1) * bw), 430], fill=c)
    for i, c in enumerate(meio):
        d.rectangle([int(i * bw), 430, int((i + 1) * bw), 478], fill=c)
    base = [(0, 33, 76), (255, 255, 255), (50, 0, 106), (16, 16, 16),
            (0, 0, 0), (16, 16, 16), (26, 26, 26), (16, 16, 16)]
    larg = [1.25, 1.25, 1.25, 1.25, 0.33, 0.34, 0.33, 1.0]
    x = 0.0
    unid = W / sum(larg)
    for c, l in zip(base, larg):
        d.rectangle([int(x), 478, int(x + l * unid), H], fill=c)
        x += l * unid
    _BARRAS_CACHE["b"] = img
    return img.copy()


def _etiqueta(fi):
    rng = np.random.default_rng(C.SEED + 33)
    img = nova((22, 20, 20))
    d = desenho(img)
    # corpo da fita
    d.rectangle([20, 150, 340, 480], fill=(34, 32, 32), outline=(10, 10, 10), width=3)
    d.ellipse([70, 380, 130, 440], fill=(15, 15, 15))
    d.ellipse([230, 380, 290, 440], fill=(15, 15, 15))
    # etiqueta de papel
    d.rectangle([36, 180, 324, 360], fill=(232, 222, 190))
    for y in range(205, 360, 26):
        d.line([40, y, 320, y], fill=(170, 180, 215), width=1)
    d.line([60, 180, 60, 360], fill=(220, 120, 120), width=1)
    # letra "à mão": cada caractere com rotação e baseline irregulares
    y = 196
    for linha in C.ETIQUETA_TXT:
        x = 70
        f = fonte_mao(26)
        for ch in linha:
            if ch == " ":
                x += 12
                continue
            g = Image.new("L", (40, 44), 0)
            gd = desenho(g)
            gd.text((6, 4), ch, font=f, fill=255)
            g = g.rotate(float(rng.uniform(-9, 9)), resample=Image.NEAREST)
            tinta = Image.new("RGB", g.size, (28, 38, 150))
            img.paste(tinta, (int(x), int(y + rng.uniform(-3, 3))), g)
            x += f.getlength(ch) * rng.uniform(0.92, 1.08) + 1
        y += 50
    d.line([70, 345, 300, 340], fill=(28, 38, 150), width=2)
    return img


def cena(t, fi):
    T = fi / FPS
    if T < C.ABERTURA_AZUL_FIM:
        return nova(C.AZUL_VCR)
    if C.ETIQUETA_T <= T < C.ETIQUETA_T + 2.0 / FPS:
        return _etiqueta(fi)
    img = _barras()
    d = desenho(img)
    # letreiro
    d.rectangle([0, 222, W, 336], fill=(0, 0, 0))
    d.rectangle([0, 224, W, 226], fill=(191, 191, 191))
    d.rectangle([0, 332, W, 334], fill=(191, 191, 191))
    y = bloco_centro(d, W // 2, 240, C.CANAL_TXT, 18, (255, 255, 255), maxw=330, entre=6)
    texto(d, (W // 2, y + 8), C.EMISSAO_TXT, 14, (255, 255, 120), anchor="ma")
    return img
