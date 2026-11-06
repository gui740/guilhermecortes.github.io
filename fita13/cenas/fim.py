"""01:10–01:15 — fim da transmissão."""
import numpy as np
from PIL import Image

import config as C
from config import FPS, H, W

from .comum import bloco_centro, desenho, fonte, largura, nova, rng_frame, texto


def cena(t, fi):
    T = fi / FPS
    if T < C.FIM_PRETO:
        return nova((0, 0, 0))
    if T >= C.FIM_AZUL:
        return nova(C.AZUL_VCR)
    if T >= C.FIM_CARTAO:
        img = nova((8, 8, 10))
        d = desenho(img)
        y = bloco_centro(d, W // 2, 150, C.FICCAO_TXT, 16, (240, 240, 240), maxw=320, entre=8)
        if C.HANDLE:
            texto(d, (W // 2, y + 26), C.HANDLE, 20, (255, 255, 255), anchor="ma")
            y += 60
        y += 22
        for ln in C.CREDITOS_FOTOS:
            y = bloco_centro(d, W // 2, y, ln, 13, (175, 175, 175), maxw=340, entre=4)
        return img
    rng = rng_frame(fi, 8)
    n = rng.random((H, W)).astype(np.float32) * 55 * (0.7 + 0.3 * rng.random((H, 1)))
    img = Image.fromarray(np.repeat(n[..., None], 3, axis=2).astype(np.uint8))
    d = desenho(img)
    texto(d, (W // 2, 238), "FIM DA TRANSMISSÃO", 22, (255, 255, 255), sombra=(0, 0, 0), anchor="ma")
    texto(d, (W // 2, 284), "BOA NOITE, CUIABÁ.", 17, (230, 230, 230), sombra=(0, 0, 0), anchor="ma")
    if T >= C.FIM_APRENDIZ_T:
        frase = "ATÉ AMANHÃ, APRENDIZ."
        if rng.random() < 0.3:
            frase = "".join(ch if rng.random() > 0.2 else "#%?@"[int(rng.integers(0, 4))] for ch in frase)
        dx = int(rng.integers(-4, 5))
        y = 318 + int(rng.integers(-1, 2))
        texto(d, (W // 2 + dx - 3, y), frase, 17, (255, 0, 0), anchor="ma")
        texto(d, (W // 2 + dx + 3, y), frase, 17, (0, 220, 255), anchor="ma")
        texto(d, (W // 2 + dx, y), frase, 17, (255, 255, 255), anchor="ma")
    return img
