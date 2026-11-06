"""Utilidades de desenho compartilhadas entre as cenas."""
import glob
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

import config as C
from config import H, W


def _achar_fonte():
    fontes = sorted(glob.glob(os.path.join(C.BASE_DIR, "assets", "fonts", "*.ttf")) +
                    glob.glob(os.path.join(C.BASE_DIR, "assets", "fonts", "*.otf")))
    if fontes:
        return fontes[0]
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
              "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf",
              "/Library/Fonts/DejaVuSansMono-Bold.ttf",
              "C:/Windows/Fonts/DejaVuSansMono-Bold.ttf"]:
        if os.path.exists(p):
            return p
    return None


FONTE = _achar_fonte()
FONTE_MAO = None
for _p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-BoldOblique.ttf"]:
    if os.path.exists(_p):
        FONTE_MAO = _p
        break


@lru_cache(maxsize=64)
def fonte(size):
    if FONTE:
        return ImageFont.truetype(FONTE, size)
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


@lru_cache(maxsize=16)
def fonte_mao(size):
    if FONTE_MAO:
        return ImageFont.truetype(FONTE_MAO, size)
    return fonte(size)


def nova(cor=(0, 0, 0)):
    return Image.new("RGB", (W, H), cor)


def desenho(img):
    d = ImageDraw.Draw(img)
    d.fontmode = "1"  # sem anti-aliasing: texto serrilhado
    return d


def largura(txt, size):
    return fonte(size).getlength(txt.upper())


def quebrar(txt, size, maxw):
    palavras = txt.upper().split()
    linhas, atual = [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if largura(teste, size) <= maxw or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def texto(d, xy, txt, size, fill, sombra=None, off=(1, 1), anchor="la"):
    txt = txt.upper()
    f = fonte(size)
    if sombra is not None:
        d.text((xy[0] + off[0], xy[1] + off[1]), txt, font=f, fill=sombra, anchor=anchor)
    d.text(xy, txt, font=f, fill=fill, anchor=anchor)


def contorno(d, xy, txt, size, fill, cor=(0, 0, 0), anchor="la"):
    """Texto com contorno de 1 px (estilo OSD)."""
    txt = txt.upper()
    f = fonte(size)
    x, y = xy
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                d.text((x + dx, y + dy), txt, font=f, fill=cor, anchor=anchor)
    d.text(xy, txt, font=f, fill=fill, anchor=anchor)


def bloco_centro(d, cx, y, txt, size, fill, maxw=W - 32, sombra=None, entre=5, off=(1, 1)):
    for linha in quebrar(txt, size, maxw):
        texto(d, (cx, y), linha, size, fill, sombra, off, anchor="ma")
        y += size + entre
    return y


def lerp(a, b, p):
    return a + (b - a) * p


def lerp_cor(c1, c2, p):
    return tuple(int(round(lerp(a, b, p))) for a, b in zip(c1, c2))


def ease(p):
    p = min(1.0, max(0.0, p))
    return 1 - (1 - p) ** 3


def gradiente_v(w, h, c1, c2):
    p = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    a = np.array(c1, np.float32)[None, None]
    b = np.array(c2, np.float32)[None, None]
    arr = a + (b - a) * p
    return Image.fromarray(np.repeat(arr, w, axis=1).astype(np.uint8), "RGB")


def triangulo_play(d, x, y, s, fill, cor=(0, 0, 0)):
    pts = [(x, y), (x + s * 0.85, y + s / 2), (x, y + s)]
    d.polygon([(px + 1, py + 1) for px, py in pts], fill=cor)
    d.polygon(pts, fill=fill)


def quadrado_stop(d, x, y, s, fill, cor=(0, 0, 0)):
    d.rectangle([x + 1, y + 1, x + s + 1, y + s + 1], fill=cor)
    d.rectangle([x, y, x + s, y + s], fill=fill)


@lru_cache(maxsize=8)
def foto(nome, w=W, h=H):
    """Foto opcional do usuário recortada para w x h (ou None)."""
    for ext in (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"):
        p = os.path.join(C.FOTOS_DIR, nome + ext)
        if os.path.exists(p):
            try:
                im = Image.open(p).convert("RGB")
                return ImageOps.fit(im, (w, h), Image.BILINEAR)
            except Exception:
                return None
    return None


def rng_frame(fi, extra=0):
    return np.random.default_rng([C.SEED, fi, extra])
