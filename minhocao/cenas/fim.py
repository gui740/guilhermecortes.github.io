"""Bloco 7 — fim do boletim, cartão do aviso real, cartão de ficção, STOP."""
import config as C
from .comum import (VT, PLEX, fonte, nova, desenho, centro, quebra, bloco_centro,
                    tela_vcr, rng_frame)
from .abertura import AZUL_VCR
from .regras import MARINHO


def glitch_frame(t, i):
    """Frames em que 'ELE CONTA AS CANOAS.' rompe a tela."""
    if not (C.T_FIM_TEXTO + 0.5 <= t < C.T_CARTAO_REAL):
        return False
    k = i % 14
    return k in (0, 1, 7) or t > C.T_CARTAO_REAL - 0.25


def cena(t, i):
    if t < C.T_CARTAO_REAL:
        img = nova(MARINHO)
        d = desenho(img)
        f = fonte(VT, 30)
        centro(d, 220, C.FIM[0], f)
        centro(d, 256, C.FIM[1], f)
        if glitch_frame(t, i):
            rng = rng_frame(i, 41)
            fg = fonte(VT, 34)
            dx = int(rng.integers(-12, 12))
            y = 330 + int(rng.integers(-6, 6))
            centro(d, y, C.FIM_GLITCH, fg, (0, 255, 255), x=C.W // 2 + dx - 3)
            centro(d, y, C.FIM_GLITCH, fg, (255, 30, 30), x=C.W // 2 + dx)
        return img
    if t < C.T_CARTAO_FICCAO:
        img = nova((12, 12, 16))
        d = desenho(img)
        f = fonte(PLEX, 15)
        y = 170
        for par in C.CARTAO_REAL:
            linhas = quebra(par, f, 316)
            y = bloco_centro(d, y, linhas, f, (245, 245, 240), passo=20) + 18
        d.line([60, y, C.W - 60, y], fill=(120, 120, 120))
        return img
    if t < C.T_STOP:
        img = nova((0, 0, 0))
        d = desenho(img)
        centro(d, 250, C.CARTAO_FICCAO, fonte(PLEX, 22), (240, 240, 240))
        centro(d, 300, C.HANDLE, fonte(PLEX, 18), (200, 200, 200))
        return img
    return tela_vcr(nova(AZUL_VCR), "STOP", quadrado=True)


def estilo(t):
    if t < C.T_CARTAO_REAL:
        return C.FX_INTENSIDADE["fim"], "frio"
    if t < C.T_STOP:
        return C.FX_INTENSIDADE["cartao"], "limpo"
    return 0.3, "nenhum"
