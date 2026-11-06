"""01:02–01:10 — o pátio visto pela câmera de segurança (CFTV)."""
import math

import numpy as np
from PIL import Image, ImageDraw

import config as C
import icones
from config import FPS, H, W

from .comum import desenho, foto, fonte, rng_frame, texto

HORIZ = 168
FOCAL = 330.0
CAM_H = 3.6
# vagas dos canhões (X, Z) em metros; ordem de aparição
VAGAS = [(-2.6, 6.5), (-0.85, 6.5), (0.85, 6.5), (2.6, 6.5),   # os 4 "oficiais"
         (0.0, 10.5), (-2.3, 10.5), (2.3, 10.5)]              # os que surgem
# posição da criança por corte (None = ausente): (X, Z) — cada vez mais perto
CRIANCA = [None, (1.25, 27.0), (-1.7, 9.0), (-0.75, 3.1)]


def _proj(X, Z):
    return W / 2 + FOCAL * X / Z, HORIZ + FOCAL * CAM_H / Z, FOCAL / Z


def _canhao(d, X, Z):
    sx, sy, sc = _proj(X, Z)
    L = 1.9 * sc
    r = 0.42 * sc
    # sombra
    d.ellipse([sx - L * 0.55, sy - 0.08 * sc, sx + L * 0.55, sy + 0.1 * sc], fill=28)
    # tubo inclinado
    bx0, by0 = sx - L * 0.5, sy - 0.62 * sc
    bx1, by1 = sx + L * 0.5, sy - 0.85 * sc
    t0, t1 = 0.2 * sc, 0.12 * sc
    d.polygon([(bx0, by0 - t0), (bx1, by1 - t1), (bx1, by1 + t1), (bx0, by0 + t0)], fill=52)
    d.line([(bx0, by0 - t0), (bx1, by1 - t1)], fill=120, width=max(1, int(sc * 0.06)))
    d.ellipse([bx0 - t0, by0 - t0, bx0 + t0 * 0.6, by0 + t0], fill=60)
    # roda
    wx, wy = sx - L * 0.12, sy - r
    d.ellipse([wx - r, wy - r, wx + r, wy + r], fill=40, outline=95, width=max(1, int(sc * 0.05)))
    d.ellipse([wx - r * 0.25, wy - r * 0.25, wx + r * 0.25, wy + r * 0.25], fill=90)


def _crianca(img_l, embers, X, Z):
    d = ImageDraw.Draw(img_l)
    sx, sy, sc = _proj(X, Z)
    h = 1.15 * sc
    cab = h * 0.17
    corpo_w = h * 0.26
    d.ellipse([sx - cab, sy - h, sx + cab, sy - h + 2 * cab], fill=4)
    d.polygon([(sx - corpo_w * 0.55, sy - h + 2 * cab * 0.95), (sx + corpo_w * 0.55, sy - h + 2 * cab * 0.95),
               (sx + corpo_w, sy - h * 0.42), (sx - corpo_w, sy - h * 0.42)], fill=4)
    d.rectangle([sx - corpo_w * 0.7, sy - h * 0.45, sx + corpo_w * 0.7, sy - h * 0.12], fill=4)
    d.rectangle([sx - corpo_w * 0.55, sy - h * 0.14, sx - corpo_w * 0.12, sy], fill=4)
    d.rectangle([sx + corpo_w * 0.12, sy - h * 0.14, sx + corpo_w * 0.55, sy], fill=4)
    # braços caídos, mãos com brasa
    for lado in (-1, 1):
        mx = sx + lado * corpo_w * 1.05
        d.line([sx + lado * corpo_w * 0.8, sy - h * 0.7, mx, sy - h * 0.38], fill=4, width=max(1, int(h * 0.07)))
        embers.append((mx, sy - h * 0.36, max(1.2, h * 0.022)))


def _desenhar_cena(corte, fi):
    rng = rng_frame(fi, 6)
    ft = foto("patio")
    if ft is not None:
        img_l = ft.convert("L")
        d = ImageDraw.Draw(img_l)
    else:
        img_l = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(img_l)
        # céu noturno sobre o pátio
        d.rectangle([0, 0, W, HORIZ], fill=22)
        # varanda do outro lado do pátio (arcada)
        _, yb, _ = _proj(0, 30.0)
        d.rectangle([0, HORIZ - 44, W, yb], fill=92)
        d.rectangle([0, HORIZ - 50, W, HORIZ - 44], fill=60)  # telhado
        for i in range(-8, 9):
            ax = W / 2 + i * 26
            d.rectangle([ax - 8, HORIZ - 30, ax + 8, yb], fill=44)
            d.ellipse([ax - 8, HORIZ - 38, ax + 8, HORIZ - 22], fill=44)
        # chão do pátio em perspectiva
        for y in range(int(yb), H):
            d.line([0, y, W, y], fill=int(70 + 70 * (y - yb) / (H - yb)))
        for X in np.arange(-12, 13, 1.5):
            x0, y0, _ = _proj(X, 30.0)
            x1, y1, _ = _proj(X, 1.2)
            d.line([x0, y0, x1, y1], fill=58)
        for Z in [24, 18, 14, 11, 9, 7.5, 6.3, 5.3, 4.5, 3.8, 3.2]:
            _, y, _ = _proj(0, Z)
            d.line([0, y, W, y], fill=60)
    n = C.PATIO_CONTAGEM[corte]
    for X, Z in sorted(VAGAS[:n], key=lambda v: -v[1]):
        _canhao(d, X, Z)
    embers = []
    cri = CRIANCA[corte]
    if cri is not None and cri[1] > 3:
        _crianca(img_l, embers, *cri)
    if ft is None:
        # arco da varanda em primeiro plano (moldura escura)
        mask = Image.new("L", (W, H), 255)
        md = ImageDraw.Draw(mask)
        md.ellipse([34, 40, W - 34, 300], fill=0)
        md.rectangle([34, 170, W - 34, 610], fill=0)
        img_l.paste(12, (0, 0), mask)
        d = ImageDraw.Draw(img_l)
        d.arc([34, 40, W - 34, 300], 180, 360, fill=70, width=3)
        for x in (34, W - 37):
            d.line([x, 170, x, 610], fill=70, width=3)
        for x in (0, W - 34):
            for y in range(60, 610, 14):
                d.line([x + 2, y, x + 31, y], fill=28)
        d.rectangle([0, 606, W, H], fill=30)
        for x in range(0, W, 40):
            d.line([x, 606, x - 30, H], fill=18)
    if cri is not None and cri[1] <= 3:
        _crianca(img_l, embers, *cri)
    # iluminação de CFTV: centro claro, bordas escuras + flicker
    arr = np.asarray(img_l).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    r = ((xx - W / 2) / (W / 1.3)) ** 2 + ((yy - 330) / (H / 1.5)) ** 2
    arr *= np.clip(1.25 - r, 0.25, 1.2) * (0.92 + 0.12 * rng.random())
    rgb = np.stack([arr * 0.38, arr * 1.05, arr * 0.5], axis=2) + np.array([2, 10, 4], np.float32)
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    # brasa nas mãos (único laranja na imagem)
    d = ImageDraw.Draw(img)
    for x, y, rr in embers:
        fl = 0.8 + 0.4 * rng.random()
        for k, cor in ((3.0, (90, 30, 0)), (2.0, (200, 80, 10)), (1.0, (255, 180, 60))):
            rk = rr * k * fl
            d.ellipse([x - rk, y - rk, x + rk, y + rk], fill=cor)
    return img


def _negativo(fi):
    """Rosto (sem rosto) da silhueta colado na câmera, em negativo."""
    rng = rng_frame(fi, 12)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # cabeça: elipse escura com sombreamento suave, ombros embaixo
    cab = ((xx - W / 2) / 150) ** 2 + ((yy - 280) / 215) ** 2
    omb = ((xx - W / 2) / 260) ** 2 + ((yy - 700) / 220) ** 2
    fundo = 70 + 30 * np.clip(1 - ((xx - W / 2) ** 2 + (yy - 300) ** 2) / 160000, 0, 1)
    arr = np.where(cab < 1, 6 + 22 * cab ** 3, fundo)
    arr = np.where(omb < 1, 8, arr)
    # duas cavidades leves onde deveriam estar os olhos
    for ex in (W / 2 - 55, W / 2 + 55):
        cav = ((xx - ex) / 34) ** 2 + ((yy - 260) / 22) ** 2
        arr = np.where(cav < 1, arr + 10 * (1 - cav), arr)
    arr = arr + rng.standard_normal((H, W)).astype(np.float32) * 6
    rgb = np.stack([arr * 0.38, arr * 1.05, arr * 0.5], axis=2) + np.array([2, 10, 4], np.float32)
    rgb = 255 - rgb
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    d = desenho(im)
    texto(d, (W // 2, 500), "APRENDIZ Nº 0", 30, (200, 0, 0), sombra=(0, 0, 0), off=(2, 2), anchor="ma")
    return im


def cena(t, fi):
    T = fi / FPS
    if T >= C.PATIO_NEGATIVO_T:
        return _negativo(fi)
    corte = 0
    for i, tc in enumerate(C.PATIO_CORTES):
        if T >= tc:
            corte = i
    img = _desenhar_cena(corte, fi)
    d = desenho(img)
    verde = (190, 255, 190)
    texto(d, (16, 66), "CAM 04 — PÁTIO", 14, verde, sombra=(0, 0, 0))
    texto(d, (W - 16, 66), C.PATIO_TS, 14, verde, sombra=(0, 0, 0), anchor="ra")
    if (fi // 15) % 2 == 0:
        d.ellipse([16, 88, 26, 98], fill=(230, 30, 30))
        texto(d, (32, 86), "REC", 13, verde, sombra=(0, 0, 0))
    # contagem
    texto(d, (W - 22, 416), "CANHÕES", 12, verde, sombra=(0, 0, 0), anchor="ra")
    texto(d, (W - 22, 432), str(C.PATIO_CONTAGEM[corte]), 56, (230, 255, 230), sombra=(0, 0, 0),
          off=(2, 2), anchor="ra")
    rng = rng_frame(fi, 7)
    for tp, nome, (cx, cy) in C.POPUPS:
        if tp <= T < tp + 1.4:
            icones.colar_animado(img, nome, cx, cy, 3, (T - tp) * FPS, corrompido=True, rng=rng)
    return img
