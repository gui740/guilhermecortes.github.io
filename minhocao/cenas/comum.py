"""Utilitários compartilhados pelas cenas (fontes, texto, contexto)."""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import config as C

# Contexto preenchido pelo render.py (tempos de voz, forma de onda do áudio)
CTX = {"voz": {}, "onda": None}

VT = "VT323-Regular.ttf"
PLEX = "IBMPlexMono-Bold.ttf"
STM = "ShareTechMono-Regular.ttf"


@lru_cache(maxsize=None)
def fonte(nome, tam):
    return ImageFont.truetype(str(C.FONTES / nome), tam)


def nova(cor=(0, 0, 0)):
    img = Image.new("RGB", (C.W, C.H), cor)
    return img


def desenho(img):
    d = ImageDraw.Draw(img)
    d.fontmode = "1"  # sem antialias: pixel duro, como caractere-gerador
    return d


def quebra(texto, f, largura):
    """Quebra texto em linhas que caibam em `largura` px."""
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if f.getlength(teste) <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def texto(d, xy, s, f, cor=(255, 255, 255), sombra=None, ancora="la", negrito=None):
    # VT323 tem traço de 1 px: engrossa 1 px na horizontal para sobreviver ao VHS
    if negrito is None:
        negrito = VT in str(getattr(f, "path", ""))
    if sombra is not None:
        d.text((xy[0] + 1, xy[1] + 1), s, font=f, fill=sombra, anchor=ancora)
        if negrito:
            d.text((xy[0] + 2, xy[1] + 1), s, font=f, fill=sombra, anchor=ancora)
    d.text(xy, s, font=f, fill=cor, anchor=ancora)
    if negrito:
        d.text((xy[0] + 1, xy[1]), s, font=f, fill=cor, anchor=ancora)


def centro(d, y, s, f, cor=(255, 255, 255), sombra=None, x=None):
    texto(d, ((C.W // 2) if x is None else x, y), s, f, cor, sombra, ancora="ma")


def bloco_centro(d, y, linhas, f, cor=(255, 255, 255), passo=None, sombra=None):
    passo = passo or int(f.size * 0.95)
    for k, ln in enumerate(linhas):
        centro(d, y + k * passo, ln, f, cor, sombra)
    return y + len(linhas) * passo


def caixa_texto(d, y, linhas, f, cor=(255, 255, 255), fundo=(0, 0, 0), passo=None, pad=4):
    passo = passo or int(f.size * 0.95)
    larg = max(f.getlength(ln) for ln in linhas)
    x0 = C.W / 2 - larg / 2 - pad
    d.rectangle([x0, y - pad + 2, C.W - x0, y + passo * len(linhas) + pad - 2], fill=fundo)
    return bloco_centro(d, y, linhas, f, cor, passo)


def triangulo_play(d, x, y, tam, cor=(255, 255, 255)):
    d.polygon([(x, y), (x, y + tam), (x + tam * 0.85, y + tam / 2)], fill=cor)


def quadrado_stop(d, x, y, tam, cor=(255, 255, 255)):
    d.rectangle([x, y, x + tam, y + tam], fill=cor)


def embaralha(s, rng, prob=0.5, chars="#%&?@0123456789$!*"):
    return "".join(
        (chars[rng.integers(len(chars))] if (c != " " and rng.random() < prob) else c)
        for c in s
    )


def rng_frame(i, sal=0):
    return np.random.default_rng(C.SEED * 100003 + i * 7919 + sal)


def tela_vcr(img, rotulo, quadrado=False):
    """Tela azul de videocassete com OSD."""
    d = desenho(img)
    f = fonte(VT, 30)
    if quadrado:
        quadrado_stop(d, 22, C.SAFE_TOP + 10, 16)
    else:
        triangulo_play(d, 22, C.SAFE_TOP + 9, 18)
    texto(d, (46, C.SAFE_TOP + 4), rotulo, f)
    texto(d, (C.W - 22, C.SAFE_TOP + 4), "SP", f, ancora="ra")
    return img


def caminho_rio(n=400, t=0.0):
    """Pontos (x, y) da linha sinuosa do rio no mapa (de cima para baixo)."""
    s = np.linspace(0, 1, n)
    y = 96 + s * 330
    x = 140 + 38 * np.sin(s * 7.2 + 0.4) + 22 * np.sin(s * 15.0 + 1.3) + 10 * s
    return np.stack([x, y], 1)
