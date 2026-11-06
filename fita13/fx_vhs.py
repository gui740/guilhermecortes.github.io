"""Pipeline de efeitos VHS. Cada efeito: np.ndarray float32 (H,W,3) -> np.ndarray, k em 0..1."""
import math

import numpy as np

from config import H, W

RGB2YIQ = np.array([[0.299, 0.587, 0.114],
                    [0.596, -0.274, -0.322],
                    [0.211, -0.523, 0.312]], np.float32)
YIQ2RGB = np.linalg.inv(RGB2YIQ).astype(np.float32)

_X = np.arange(W)[None, :]
_ROWS = np.arange(H)[:, None]
_YF = np.arange(H, dtype=np.float32)

# mapa de barril + vinheta pré-calculado
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_u = (_xx - W / 2 + 0.5) / (W / 2)
_v = (_yy - H / 2 + 0.5) / (H / 2)
_R2 = _u * _u + _v * _v
_KB = 0.022
_su = _u * (1 + _KB * _R2)
_sv = _v * (1 + _KB * _R2)
_BX = np.round(_su * W / 2 + W / 2 - 0.5).astype(np.int32)
_BY = np.round(_sv * H / 2 + H / 2 - 0.5).astype(np.int32)
_BFORA = (_BX < 0) | (_BX >= W) | (_BY < 0) | (_BY >= H)
_BX = np.clip(_BX, 0, W - 1)
_BY = np.clip(_BY, 0, H - 1)


# ------------------------------------------------------------------ utilitários
def hblur(a, r):
    """Box blur horizontal de raio r (axis=1)."""
    r = int(r)
    if r <= 0:
        return a
    pads = [(0, 0), (r + 1, r)] + [(0, 0)] * (a.ndim - 2)
    p = np.pad(a, pads, mode="edge")
    c = np.cumsum(p, axis=1, dtype=np.float32)
    return (c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)


def hshift(a, s):
    """Desloca horizontalmente (s>0 para a direita), repetindo a borda."""
    s = int(s)
    if s == 0:
        return a
    out = np.empty_like(a)
    if s > 0:
        out[:, s:] = a[:, :-s]
        out[:, :s] = a[:, :1]
    else:
        out[:, :s] = a[:, -s:]
        out[:, s:] = a[:, -1:]
    return out


def desloc_linhas(img, shifts):
    idx = np.clip(_X - np.round(shifts).astype(np.int32)[:, None], 0, W - 1)
    return img[_ROWS, idx]


def _suave1d(x, r):
    k = np.ones(2 * r + 1, np.float32) / (2 * r + 1)
    return np.convolve(np.pad(x, r, mode="edge"), k, mode="valid")


# ------------------------------------------------------------------ efeitos
def instabilidade_cor(img, k, t):
    """8. Flutuação de saturação/gamma, cores lavadas e quentes, preto levantado."""
    sat = 1.0 - 0.2 * k + 0.07 * k * math.sin(t * 1.7)
    gamma = 1.0 + 0.07 * k * math.sin(t * 0.9 + 1.0)
    y = img.mean(axis=2, keepdims=True)
    img = y + (img - y) * sat
    img = img * np.array([1 + 0.05 * k, 1 + 0.01 * k, 1 - 0.09 * k], np.float32) + 9 * k
    img = np.clip(img / 255.0, 0, 1) ** gamma * 255.0
    return img.astype(np.float32)


def chroma_bleed(img, k):
    """1. Crominância vaza na horizontal; R para a direita, B para a esquerda."""
    yiq = img @ RGB2YIQ.T
    yiq[..., 1] = hshift(hblur(yiq[..., 1], 2 + int(7 * k)), 1 + int(2 * k))
    yiq[..., 2] = hshift(hblur(yiq[..., 2], 3 + int(9 * k)), 1 + int(2 * k))
    rgb = yiq @ YIQ2RGB.T
    s = int(round(2 + 2 * k))
    rgb[..., 0] = hshift(rgb[..., 0], s)
    rgb[..., 2] = hshift(rgb[..., 2], -max(1, s - 1))
    return rgb


def luma_baixa(img, k):
    """2. Luminância de baixa resolução + nitidez exagerada (halo nas bordas)."""
    yiq = img @ RGB2YIQ.T
    y = hblur(yiq[..., 0], 1)
    y = y + (0.7 + 1.5 * k) * (y - hblur(y, 2))
    yiq[..., 0] = y
    return yiq @ YIQ2RGB.T


def scanlines(img, k):
    """3. Escurece linhas alternadas 10–20%."""
    img[1::2] *= (1.0 - (0.10 + 0.10 * k))
    return img


def ruido(img, k, rng):
    """4. Grão gaussiano + neve esparsa."""
    g = rng.standard_normal((H, W, 1), dtype=np.float32) * (3 + 10 * k)
    c = rng.standard_normal((H // 2, W // 4, 3), dtype=np.float32) * (2 + 5 * k)
    c = np.repeat(np.repeat(c, 2, axis=0), 4, axis=1)
    img = img + g + c
    n = int(500 * k * k)
    if n:
        ys = rng.integers(0, H, n)
        xs = rng.integers(0, W - 2, n)
        img[ys, xs] = 255
        img[ys, xs + 1] = 210
    return img


def jitter(img, k, t, rng):
    """5. Cada linha deslocada por onda + ruído suave, com picos ocasionais."""
    s = (0.9 * k * np.sin(_YF * 0.045 + t * 9.0)
         + 0.5 * k * np.sin(_YF * 0.31 + t * 23.0)
         + 1.6 * k * _suave1d(rng.standard_normal(H).astype(np.float32), 4))
    if rng.random() < 0.07 * k:
        y0 = int(rng.integers(0, H - 20))
        s[y0:y0 + int(rng.integers(3, 18))] += rng.uniform(5, 16) * (1 if rng.random() < .5 else -1)
    return desloc_linhas(img, s)


def barra_tracking(img, prog, k, rng):
    """6. Faixa de distorção que rola de baixo para cima."""
    alt = int(26 + 34 * k)
    centro = H + alt - prog * (H + 2 * alt)
    y0, y1 = int(max(0, centro - alt)), int(min(H, centro + alt))
    if y1 <= y0:
        return img
    ys = np.arange(y0, y1)
    w = np.clip(1 - np.abs(ys - centro) / alt, 0, 1) ** 1.5
    shifts = np.zeros(H, np.float32)
    shifts[y0:y1] = w * rng.uniform(6, 34, y1 - y0)
    img = desloc_linhas(img, shifts)
    linhas_ruido = (rng.random(y1 - y0) > 0.35).astype(np.float32)
    nz = rng.random((y1 - y0, W, 1)).astype(np.float32) ** 3 * 255
    img[y0:y1] = img[y0:y1] * (1 - 0.6 * w[:, None, None]) + nz * (w * linhas_ruido)[:, None, None]
    yc = int(centro)
    if 0 <= yc < H:
        img[yc] = np.maximum(img[yc], 230)
    return img


def head_switching(img, k, rng, n=8):
    """7. Últimas ~8 linhas tortas para a direita, com ruído."""
    shifts = np.zeros(H, np.float32)
    shifts[H - n:] = np.linspace(4, 26, n) + rng.integers(0, 7, n)
    img = desloc_linhas(img, shifts)
    nz = rng.random((n, W, 1)).astype(np.float32) * 120
    img[H - n:] = img[H - n:] * 0.7 + nz
    img[H - n:, :, 1] *= 0.85  # leve erro de cor (magenta)
    return img


def barril_vinheta(img, k):
    """9. Distorção de barril (CRT) + vinheta."""
    out = img[_BY, _BX]
    out[_BFORA] = 0
    m = 1.0 - (0.15 + 0.4 * k) * np.clip(_R2 / 2.0, 0, 1) ** 1.3
    return out * m[..., None]


def dropouts(img, lista, rng):
    """10. Riscos brancos horizontais curtos."""
    for y, x, l in lista:
        img[y, x:x + l] = 255 - rng.random((min(l, W - x), 1)) * 40
        if y + 1 < H:
            img[y + 1, x:x + l // 2] = np.maximum(img[y + 1, x:x + l // 2], 200)
    return img


def glitch_forte(img, tipo, prog, rng):
    """11. Blocos deslocados, inversão, pulo de sincronia vertical. (congelar é no render)"""
    if tipo == "inverter":
        return 255.0 - img
    if tipo == "blocos":
        img = img.copy()
        for _ in range(int(rng.integers(3, 8))):
            y0 = int(rng.integers(0, H - 10))
            h = int(rng.integers(6, 60))
            dx = int(rng.integers(-80, 80))
            img[y0:y0 + h] = hshift(img[y0:y0 + h], dx)
            if rng.random() < 0.4:
                ys = int(rng.integers(0, H - h))
                img[y0:y0 + h] = img[ys:ys + h][:, :, ::-1] if rng.random() < .3 else img[ys:ys + h]
        return img
    if tipo == "vsync":
        off = int(prog * H * 0.9)
        img = np.roll(img, off, axis=0)
        barra = int(18)
        y = off % H
        img[max(0, y - barra):y] = 0
        return img
    return img


def estatica(rng, k=1.0):
    """12. Estática total para as transições."""
    n = rng.random((H, W), dtype=np.float32)
    n = 0.55 * n + 0.45 * hblur(n, 2)
    linha = rng.random((H, 1)).astype(np.float32) * 0.6 + 0.55
    n = n * linha
    y0 = int(rng.integers(0, H))
    n[y0:y0 + 40] *= 1.35
    img = np.repeat(n[..., None], 3, axis=2) * 255 * k
    img[..., 2] *= 1.05
    return img


# ------------------------------------------------------------------ pipeline
def aplicar(img, k, t, rng, track_prog=None, drops=None):
    """Aplica todo o pipeline (1–10) num frame float32. OSD vem depois, por fora."""
    if k <= 0:
        return img
    img = instabilidade_cor(img, k, t)
    img = luma_baixa(img, k)
    img = chroma_bleed(img, k)
    img = jitter(img, k, t, rng)
    if track_prog is not None:
        img = barra_tracking(img, track_prog, max(k, 0.5), rng)
    img = head_switching(img, k, rng)
    img = scanlines(img, k)
    img = ruido(img, k, rng)
    if drops:
        img = dropouts(img, drops, rng)
    img = barril_vinheta(img, k)
    return np.clip(img, 0, 255)
