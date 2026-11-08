"""Bloco 6 — contato: forma de onda do som do leito do rio + legendas."""
import numpy as np

import config as C
import criatura
from .comum import CTX, VT, fonte, nova, desenho, caixa_texto, quebra


def cena(t, i):
    img = nova((0, 0, 0))
    if t >= C.T_PRETO:
        return img
    # nos últimos segundos, a cabeça dele se aproxima no escuro, atrás da onda
    tl = t - (C.T_CONTATO + 3.6)
    if tl > 0:
        z = 1 + tl * 0.45
        u = np.linspace(0, 1, 50)
        esp = np.stack([180 + 12 * np.sin(u * 3 + t), C.H + 80 - (C.H + 80 - 250) * u], 1)
        esp = (esp - esp[-1]) * z + esp[-1]
        cam = criatura.desenha(esp, lambda v: 40 * z * (0.8 + 0.3 * v), img.size, fase=t * 10,
                               boca=min(1, tl / 2), escuro=min(0.35, tl * 0.25), luz=(0, -1))
        img.paste(cam, (0, 0), cam)
    d = desenho(img)
    onda = CTX.get("onda")
    yc = 300
    xs = np.arange(16, C.W - 16)
    if onda is not None:
        c = int(t * C.SR)
        janela = onda[max(0, c - 2400): c + 2400]
        if len(janela) < 10:
            janela = np.zeros(4800)
        idx = np.linspace(0, len(janela) - 1, len(xs)).astype(int)
        amos = janela[idx]
        pico = max(np.abs(onda[max(0, c - 48000): c + 4800]).max(), 1e-4)
        ys = yc - amos / pico * 70
    else:
        ys = yc + 20 * np.sin(xs * 0.05 + t * 3)
    for gx in range(16, C.W - 16, 24):
        d.line([gx, yc - 90, gx, yc + 90], fill=(0, 34, 0))
    d.line([16, yc, C.W - 16, yc], fill=(0, 70, 0))
    pts = list(zip(xs.tolist(), ys.tolist()))
    d.line(pts, fill=(60, 255, 120), width=2)
    d.line(pts, fill=(220, 255, 230), width=1)
    d.rectangle([14, yc - 92, C.W - 14, yc + 92], outline=(0, 110, 40))
    f = fonte(VT, 22)
    y = 418
    for tt, s in C.T_LEGENDAS:
        if t >= tt:
            linhas = quebra(s, f, 324)
            y = caixa_texto(d, y, linhas, f, (255, 225, 40), (0, 0, 0), passo=20, pad=4) + 10
    return img


def estilo(t):
    if t >= C.T_PRETO:
        return 0.0, "preto"
    return C.FX_INTENSIDADE["contato"], "nenhum"
