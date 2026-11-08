"""Efeitos de fita VHS/CRT aplicados na resolução interna (360x640).

Entrada/saída: numpy float32 HxWx3 em [0, 1].
"""
import numpy as np
from scipy.ndimage import uniform_filter1d

from config import W, H

# ---------------------------------------------------------------------------
# Pré-cálculos: barril de CRT (bilinear) + vinheta
# ---------------------------------------------------------------------------
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_nx = (_xx - W / 2) / (W / 2)
_ny = (_yy - H / 2) / (H / 2)
_r2 = _nx ** 2 + _ny ** 2
_K = 0.035
_sx = (_nx * (1 + _K * _r2)) * (W / 2) + W / 2
_sy = (_ny * (1 + _K * _r2)) * (H / 2) + H / 2
_fora = (_sx < 0) | (_sx > W - 1) | (_sy < 0) | (_sy > H - 1)
_sx = np.clip(_sx, 0, W - 1.001)
_sy = np.clip(_sy, 0, H - 1.001)
_x0 = _sx.astype(np.int32)
_y0 = _sy.astype(np.int32)
_fx = (_sx - _x0)[..., None]
_fy = (_sy - _y0)[..., None]
_VINHETA = np.clip(1.0 - 0.55 * _r2 ** 1.3, 0.0, 1.0).astype(np.float32)[..., None]
_VINHETA[_fora] = 0
_SCAN = np.ones((H, 1, 1), np.float32)
_SCAN[1::2] = 0.84
_COLS = np.arange(W)


def _barril(img):
    a = img[_y0, _x0]
    b = img[_y0, _x0 + 1]
    c = img[_y0 + 1, _x0]
    d = img[_y0 + 1, _x0 + 1]
    top = a + (b - a) * _fx
    bot = c + (d - c) * _fx
    return top + (bot - top) * _fy


def _desloca_linhas(img, offs):
    """Desloca cada linha horizontalmente por offs[y] px (inteiro)."""
    idx = (_COLS[None, :] - offs[:, None].astype(np.int32)) % W
    return np.take_along_axis(img, idx[..., None].repeat(3, 2), axis=1)


def _rgb2yuv(img):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    u = -0.14713 * r - 0.28886 * g + 0.436 * b
    v = 0.615 * r - 0.51499 * g - 0.10001 * b
    return y, u, v


def _yuv2rgb(y, u, v):
    r = y + 1.13983 * v
    g = y - 0.39465 * u - 0.58060 * v
    b = y + 2.03211 * u
    return np.stack([r, g, b], -1)


# ---------------------------------------------------------------------------
# Graduação de cor por modo
# ---------------------------------------------------------------------------
def gradua(img, modo):
    if modo == "quente":  # cor lavada e quente (boletim)
        img = img * 0.86 + 0.07
        lum = img.mean(-1, keepdims=True)
        img = lum + (img - lum) * 0.78
        img = img * np.array([1.06, 1.0, 0.86], np.float32)
    elif modo == "fosforo":
        lum = img.max(-1, keepdims=True)
        img = lum * np.array([0.25, 1.0, 0.35], np.float32) + np.array([0.0, 0.03, 0.01], np.float32)
    elif modo == "noturna":
        lum = img.mean(-1, keepdims=True)
        lum = np.clip((lum - 0.04) * 1.25, 0, 1) ** 0.85
        img = lum * np.array([0.72, 1.0, 0.78], np.float32) + np.array([0.02, 0.05, 0.03], np.float32)
    elif modo == "frio":
        lum = img.mean(-1, keepdims=True)
        img = lum + (img - lum) * 0.85
        img = img * np.array([0.92, 0.98, 1.08], np.float32)
    return img


# ---------------------------------------------------------------------------
def aplica(img, k, modo, i, rng):
    """Aplica a cadeia VHS. k = intensidade 0..1, i = índice do frame."""
    if modo == "preto":
        return np.zeros_like(img)
    img = gradua(img, modo)

    # 1. chroma bleed + deslocamento R/B
    y, u, v = _rgb2yuv(img)
    larg = int(3 + 6 * k)
    u = np.roll(uniform_filter1d(u, larg, axis=1), 2, axis=1)
    v = np.roll(uniform_filter1d(v, larg, axis=1), 2, axis=1)
    # 2. blur horizontal na luminância + unsharp exagerado (halo)
    yb = uniform_filter1d(y, 2, axis=1)
    yb2 = uniform_filter1d(yb, 7, axis=1)
    y = yb + (0.3 + 0.5 * k) * (yb - yb2)
    img = _yuv2rgb(y, u * (0.9 + 0.1 * k), v * (0.9 + 0.1 * k))
    s = int(round(0.4 + 1.6 * k))
    if s:
        img[..., 0] = np.roll(img[..., 0], s, axis=1)
        img[..., 2] = np.roll(img[..., 2], -s, axis=1)

    # 5. jitter horizontal por linha (com picos)
    offs = rng.normal(0, 0.5 + 1.6 * k, H)
    offs = uniform_filter1d(offs, 9)
    if rng.random() < 0.08 + 0.25 * k:
        y0 = rng.integers(0, H - 20)
        hgt = rng.integers(3, 18)
        offs[y0:y0 + hgt] += rng.normal(0, 4 + 10 * k)
    # 6. barra de tracking rolando
    yb = int((i * (2.3 + 2 * k)) % (H + 120)) - 60
    banda = np.exp(-((np.arange(H) - yb) / (6 + 10 * k)) ** 2)
    offs += banda * (3 + 10 * k) * np.sin(np.arange(H) * 0.9 + i)
    # 7. head-switching nas últimas ~8 linhas
    offs[-9:] += np.linspace(4, 18, 9) * (0.6 + k)
    img = _desloca_linhas(img, np.round(offs))

    vis_banda = (0.15 + 0.6 * k) * banda[:, None]
    img = img * (1 - 0.25 * vis_banda[..., None]) + \
        vis_banda[..., None] * rng.random((H, W, 1), dtype=np.float32) * 0.7
    img[-9:] = img[-9:] * 0.6 + rng.random((9, W, 1), dtype=np.float32) * 0.35

    # 4. grão + neve
    img = img + rng.normal(0, 0.02 + 0.07 * k, (H, W, 1)).astype(np.float32)
    neve = rng.random((H, W)) < (0.0008 + 0.006 * k)
    img[neve] = 0.95

    # 10. drop-outs (riscos brancos)
    for _ in range(rng.poisson(0.4 + 2.5 * k)):
        yy = rng.integers(0, H)
        xx = rng.integers(0, W)
        ln = rng.integers(8, 70)
        img[yy, xx:xx + ln] = 0.9 + 0.1 * rng.random()

    # 3. scanlines + 9. vinheta e barril
    img = np.clip(img, 0, 1) * _SCAN
    img = _barril(img) * _VINHETA
    return np.clip(img, 0, 1).astype(np.float32)


def leve(img, rng):
    """Tratamento leve para OSD e cartões limpos."""
    y, u, v = _rgb2yuv(img)
    u = uniform_filter1d(u, 3, axis=1)
    v = uniform_filter1d(v, 3, axis=1)
    img = _yuv2rgb(y, u, v)
    img = img + rng.normal(0, 0.012, (H, W, 1)).astype(np.float32)
    return np.clip(img, 0, 1).astype(np.float32)


# ---------------------------------------------------------------------------
# 11. Glitch forte pontual
# ---------------------------------------------------------------------------
def glitch(img, rng, tipo=None):
    tipo = tipo or rng.choice(["blocos", "inverte", "rola", "blocos"])
    out = img.copy()
    if tipo == "blocos":
        for _ in range(rng.integers(4, 10)):
            y0 = rng.integers(0, H - 10)
            hh = rng.integers(6, 60)
            out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], rng.integers(-80, 80), axis=1)
            if rng.random() < 0.4:
                out[y0:y0 + hh, :, rng.integers(0, 3)] *= 0.2
    elif tipo == "inverte":
        out = 1.0 - out
    elif tipo == "rola":
        out = np.roll(out, rng.integers(H // 6, H // 2), axis=0)
        out[: rng.integers(4, 12)] = 0
    return out


# ---------------------------------------------------------------------------
# 12. Estática total
# ---------------------------------------------------------------------------
def estatica(rng, i):
    base = rng.random((H, W // 2), dtype=np.float32)
    base = np.repeat(base, 2, axis=1)
    linhas = rng.random((H, 1), dtype=np.float32) * 0.35
    img = np.clip(base * 0.85 + linhas, 0, 1)
    yb = int((i * 37) % H)
    img[max(0, yb - 14):yb + 14] = img[max(0, yb - 14):yb + 14] * 0.4 + 0.5
    img = np.repeat(img[..., None], 3, axis=2)
    img = img * np.array([0.95, 0.97, 1.0], np.float32)
    return _barril(img * _SCAN) * _VINHETA
