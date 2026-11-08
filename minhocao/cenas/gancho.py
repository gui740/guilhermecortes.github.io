"""Bloco 0 — gancho (0–4 s): o Minhocão rompe a superfície do rio à noite."""
import numpy as np
from PIL import Image, ImageDraw

import config as C
import criatura
import icones
from .comum import CTX, VT, fonte, desenho, texto, centro, caixa_texto, quebra, rng_frame

Y_HORIZ = 330
Y_AGUA = 452
LUA = (262, 150)
_r0 = np.random.default_rng(C.SEED + 3)
_MATA = [(x, 300 + _r0.integers(-16, 6), _r0.integers(12, 28)) for x in range(-10, C.W + 20, 16)]


def cenario(img, t):
    d = ImageDraw.Draw(img)
    for y in range(Y_HORIZ):
        k = y / Y_HORIZ
        d.line([0, y, C.W, y], fill=(int(8 + 18 * k), int(12 + 26 * k), int(28 + 40 * k)))
    for r, c in [(60, (34, 48, 78)), (40, (52, 70, 104)), (24, (226, 232, 214))]:
        d.ellipse([LUA[0] - r, LUA[1] - r, LUA[0] + r, LUA[1] + r], fill=c)
    for x, y, r in _MATA:
        d.ellipse([x - r, y - r * 0.8, x + r, y + r], fill=(6, 10, 12))
    d.rectangle([0, 312, C.W, Y_HORIZ + 3], fill=(6, 10, 12))
    # rio
    for y in range(Y_HORIZ, C.H):
        k = (y - Y_HORIZ) / (C.H - Y_HORIZ)
        d.line([0, y, C.W, y], fill=(int(16 - 8 * k), int(26 - 12 * k), int(40 - 16 * k)))
    for kk in range(90):
        y = Y_HORIZ + 4 + (kk * 41) % (C.H - Y_HORIZ - 8)
        x = (kk * 89 + t * (10 + kk % 6) * 4) % (C.W + 60) - 30
        ln = 10 + (kk * 17) % 34
        d.line([x, y, x + ln, y], fill=(40, 58, 78))
    for y in range(Y_HORIZ + 3, C.H, 5):
        w = 5 + 16 * (y - Y_HORIZ) / 300 + 5 * np.sin(y * 0.3 + t * 6)
        x = LUA[0] + 5 * np.sin(y * 0.09 + t * 3)
        d.line([x - w, y, x + w, y], fill=(150, 165, 160))


def respingos(d, x, y, t, rng, forca=1.0):
    for _ in range(int(16 * forca)):
        ang = rng.uniform(np.pi * 1.05, np.pi * 1.95)
        r = rng.uniform(4, 34) * forca
        d.point((x + np.cos(ang) * r, y + np.sin(ang) * r), fill=(210, 222, 230))


def cena(t, i):
    rng = rng_frame(i, 51)
    img = Image.new("RGB", (C.W, C.H))
    cenario(img, t)
    d = ImageDraw.Draw(img)
    if t < 2.0:
        # corcova anelada saindo da água, maior que a tela, deslizando
        alt = 230 * min(1.0, t / 0.9) ** 0.7
        esp = criatura.arco(-140, 500, Y_AGUA + 40, alt + 40, deriva=t * 2)
        cam = criatura.desenha(esp, 34, img.size, fase=t * 140, cabeca=False)
        criatura.compoe(img, cam, Y_AGUA, cor_agua=(14, 24, 36))
        if t > 0.3:
            # gotas escorrendo do corpo
            for k in range(14):
                x = 20 + k * 24 + (t * 60) % 24
                yy = Y_AGUA - alt * np.sin(np.pi * (x + 140) / 640) + 30 + ((t * 300 + k * 37) % 80)
                if yy < Y_AGUA:
                    d.line([x, yy, x, yy + 5], fill=(170, 190, 205))
    else:
        tl = t - 2.0
        subida = min(1.0, tl / 1.1)
        yh = Y_AGUA + 40 - 300 * (1 - (1 - subida) ** 2)
        xs = 182 + 18 * np.sin(np.linspace(0, 3, 60) + tl * 2)
        ys = np.linspace(C.H + 60, yh, 60)
        esp = np.stack([xs, ys], 1)
        zoom = 1.0 + 1.6 * max(0.0, tl - 1.55) ** 1.6 / 0.45 ** 1.6 if tl > 1.55 else 1.0
        esp = (esp - esp[-1]) * zoom + esp[-1] + np.array([0, 40 * (zoom - 1)])
        boca = np.clip((tl - 1.1) / 0.5, 0, 1)
        cam = criatura.desenha(esp, lambda u: 30 * zoom * (0.85 + 0.25 * u), img.size,
                               fase=tl * 30, boca=boca, luz=(0.55, -0.8))
        criatura.compoe(img, cam, Y_AGUA if zoom < 1.05 else None, cor_agua=(14, 24, 36))
        if tl < 1.0:
            respingos(d, 182, Y_AGUA, t, rng, 1.0 + 1.5 * (1 - tl))
        if zoom < 1.05:
            for k in range(8):
                x = 160 + k * 6
                yy = yh + 30 + ((tl * 260 + k * 43) % (Y_AGUA - yh))
                d.line([x, yy, x, yy + 6], fill=(170, 190, 205))
    return img


def osd(t, i, img):
    d = desenho(img)
    if t > 0.12 and not (0.5 < t < 0.56):
        d.rectangle([0, C.SAFE_TOP, C.W, C.SAFE_TOP + 34], fill=(190, 20, 20))
        icones.cola_icone(img, "alerta", 22, C.SAFE_TOP + 17, 26)
        texto(d, (C.W // 2 + 12, C.SAFE_TOP + 3), "AVISO AOS PESCADORES", fonte(VT, 30), (255, 255, 255), ancora="ma")
        centro(d, C.SAFE_TOP + 40, "RIO CUIABÁ — BARRA DO PARI", fonte(VT, 22), (255, 230, 120), sombra=(0, 0, 0))
    f = fonte(VT, 26)
    clipes = CTX["voz"].get("gancho", [])
    if clipes:
        ini, fim, _ = clipes[0]
        meio = ini + (fim - ini) * 0.55
        if t >= ini - 0.1:
            linhas = [C.GANCHO[0]] + ([C.GANCHO[1]] if t >= meio else [])
            caixa_texto(d, 462, linhas, f, (255, 255, 255), (0, 0, 0), passo=24, pad=6)


def estilo(t):
    return C.FX_INTENSIDADE["gancho"], "frio"
