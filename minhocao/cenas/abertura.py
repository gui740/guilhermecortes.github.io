"""Bloco 1 — abertura: tela azul PLAY, barras de cor, letreiro, etiqueta."""
import config as C
from .comum import (VT, PLEX, fonte, nova, desenho, texto, centro, tela_vcr,
                    caixa_texto, triangulo_play)

AZUL_VCR = (12, 24, 178)

BARRAS = [(192, 192, 192), (192, 192, 0), (0, 192, 192), (0, 192, 0),
          (192, 0, 192), (192, 0, 0), (0, 0, 192)]
CASTELO = [(0, 0, 192), (19, 19, 19), (192, 0, 192), (19, 19, 19),
           (0, 192, 192), (19, 19, 19), (192, 192, 192)]


def barras(img):
    d = desenho(img)
    bw = C.W / 7
    for k, cor in enumerate(BARRAS):
        d.rectangle([k * bw, 0, (k + 1) * bw, C.H * 0.67], fill=cor)
    for k, cor in enumerate(CASTELO):
        d.rectangle([k * bw, C.H * 0.67, (k + 1) * bw, C.H * 0.75], fill=cor)
    baixo = [(0, 33, 76), (255, 255, 255), (50, 0, 106), (19, 19, 19),
             (9, 9, 9), (19, 19, 19), (29, 29, 29), (19, 19, 19)]
    larg = [1.25, 1.25, 1.25, 1.25, 0.33, 0.34, 0.33, 1.0]
    x = 0
    for cor, l in zip(baixo, larg):
        d.rectangle([x, C.H * 0.75, x + l * bw, C.H], fill=cor)
        x += l * bw
    return d


def etiqueta():
    """Flash da etiqueta da fita (2 frames)."""
    img = nova((14, 12, 12))
    d = desenho(img)
    # corpo da fita
    d.rectangle([20, 200, 340, 440], fill=(28, 26, 26), outline=(60, 58, 58), width=2)
    d.ellipse([70, 330, 130, 390], fill=(8, 8, 8))
    d.ellipse([230, 330, 290, 390], fill=(8, 8, 8))
    # etiqueta de papel
    d.rectangle([40, 222, 320, 312], fill=(228, 220, 190))
    for y in range(240, 310, 14):
        d.line([48, y, 312, y], fill=(170, 180, 205))
    f = fonte(PLEX, 19)
    centro(d, 236, "BOLETIM —", f, (30, 30, 120))
    centro(d, 262, "NÃO EXIBIR", f, (190, 20, 20))
    d.line([70, 290, 290, 286], fill=(190, 20, 20), width=2)
    texto(d, (48, 296), "15/03/74 · CAIXA 9", fonte(VT, 18), (60, 60, 60))
    return img


def cena(t, i):
    if t < C.T_PLAY_FIM:
        return tela_vcr(nova(AZUL_VCR), "PLAY")
    if C.T_ETIQUETA <= t < C.T_ETIQUETA + 2 / C.FPS:
        return etiqueta()
    img = nova()
    d = barras(img)
    f = fonte(VT, 28)
    caixa_texto(d, 150, C.EMISSORA, f, (255, 255, 255), (0, 0, 0), passo=26, pad=8)
    return img


def osd(t, i, img):
    if t < C.T_PLAY_FIM or C.T_ETIQUETA <= t < C.T_ETIQUETA + 2 / C.FPS:
        return
    d = desenho(img)
    f = fonte(VT, 26)
    texto(d, (18, C.SAFE_BOTTOM - 34), C.TIMESTAMP, f, (255, 255, 255), sombra=(0, 0, 0))
    triangulo_play(d, C.W - 40, C.SAFE_TOP + 8, 16)


def estilo(t):
    return C.FX_INTENSIDADE["abertura"], "nenhum"

