"""Efeitos de VHS / fita. Cada função: np.ndarray float32 (H,W,3) 0..1 -> mesmo formato."""
import numpy as np
from scipy.ndimage import uniform_filter1d, map_coordinates

import config as C

H, W = C.H, C.W
_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)


def _barril_coords(k=0.06):
    nx = (_XX - W / 2) / (W / 2)
    ny = (_YY - H / 2) / (H / 2)
    r2 = nx * nx * 0.6 + ny * ny * 0.4
    f = 1 + k * r2
    sx = nx * f / (1 + k * 0.5) * (W / 2) + W / 2
    sy = ny * f / (1 + k * 0.5) * (H / 2) + H / 2
    return np.stack([sy, sx])


_BARRIL = _barril_coords()
_VIN = np.clip(1.0 - 0.55 * (((_XX - W / 2) / (W * 0.62)) ** 2 + ((_YY - H / 2) / (H * 0.66)) ** 2) ** 1.4,
               0, 1)[..., None].astype(np.float32)


def rgb2yuv(a):
    y = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    u = (a[..., 2] - y) * 0.492
    v = (a[..., 0] - y) * 0.877
    return y, u, v


def yuv2rgb(y, u, v):
    r = y + v / 0.877
    b = y + u / 0.492
    g = (y - 0.299 * r - 0.114 * b) / 0.587
    return np.stack([r, g, b], -1)


# 1 + 2: croma vazando, luma borrada com halo, desalinhamento R/B
def chroma_luma(a, i, rng):
    y, u, v = rgb2yuv(a)
    k = int(3 + 10 * i)
    u = uniform_filter1d(u, k, axis=1)
    v = uniform_filter1d(v, k, axis=1)
    u = np.roll(u, int(1 + 2 * i), axis=1)
    v = np.roll(v, int(1 + 2 * i), axis=1)
    yb = uniform_filter1d(y, 2, axis=1)
    larga = uniform_filter1d(yb, int(5 + 4 * i), axis=1)
    y = yb + (0.6 + 0.9 * i) * (yb - larga)        # halo de unsharp
    out = yuv2rgb(y, u, v)
    d = int(round(2 + 2 * i))
    out[..., 0] = np.roll(out[..., 0], d, axis=1)
    out[..., 2] = np.roll(out[..., 2], -d, axis=1)
    return out


# 3
def scanlines(a, i):
    a = a.copy()
    a[1::2] *= (0.88 - 0.08 * i)
    return a


# 4
def grao(a, i, rng):
    n = rng.standard_normal((H, W, 1)).astype(np.float32) * (0.012 + 0.04 * i)
    a = a + n
    neve = rng.random((H, W)) < (0.0002 + 0.0018 * i)
    a[neve] = 0.95
    return a


# 5
def jitter(a, i, rng, t):
    desloc = rng.standard_normal(H) * (0.25 + 1.0 * i)
    desloc += np.sin(_YY[:, 0] * 0.05 + t * 7) * 0.6 * i
    if rng.random() < 0.08 * i:  # pico ocasional
        y0 = rng.integers(0, H - 20)
        desloc[y0:y0 + rng.integers(3, 18)] += rng.uniform(-12, 12) * i
    return deslocar_linhas(a, desloc)


def deslocar_linhas(a, desloc):
    idx = (np.arange(W)[None, :] - np.round(desloc).astype(int)[:, None]) % W
    return a[np.arange(H)[:, None], idx]


# 6
def tracking(a, i, rng, t, forca=1.0):
    if i <= 0.05 and forca <= 1.0:
        return a
    alt = int(14 + 26 * i * forca)
    pos = int(H - ((t * 95) % (H + alt * 3)))
    y0, y1 = max(0, pos), min(H, pos + alt)
    if y1 <= y0:
        return a
    a = a.copy()
    faixa = a[y0:y1]
    sh = rng.integers(-8, 9, size=(y1 - y0)) * i * forca
    faixa = deslocar_linhas_parcial(faixa, sh)
    ruido = rng.random(faixa.shape[:2])[..., None]
    faixa = faixa * (0.75 + 0.2 * ruido) + (ruido > 0.92) * 0.6 * forca * i
    a[y0:y1] = faixa
    return a


def deslocar_linhas_parcial(a, desloc):
    h, w = a.shape[:2]
    idx = (np.arange(w)[None, :] - np.round(desloc).astype(int)[:, None]) % w
    return a[np.arange(h)[:, None], idx]


# 7
def head_switch(a, i, rng):
    a = a.copy()
    n = 8
    sh = (np.linspace(4, 22, n) * (0.5 + i) + rng.integers(-3, 4, n)).astype(int)
    a[H - n:] = deslocar_linhas_parcial(a[H - n:], sh)
    a[H - n:] = a[H - n:] * 0.8 + rng.random((n, W, 1)) * 0.25
    return a


# 8
def grade(a, tipo, t, i):
    g = 1.0 + 0.05 * np.sin(t * 0.9) * i
    s = 0.85 + 0.1 * np.sin(t * 0.37)
    y = a.mean(-1, keepdims=True)
    if tipo == "tv":       # lavado e quente
        a = y + (a - y) * (s * 0.8)
        a = a * np.array([1.06, 1.0, 0.86], np.float32) + np.array([0.04, 0.025, 0.0], np.float32)
        a = 0.06 + a * 0.9
    elif tipo == "cftv":   # verde-cinza
        mono = y * np.array([0.78, 1.0, 0.82], np.float32)
        a = mono * 0.86 + a * 0.14
        a = 0.03 + a * 0.97
    elif tipo == "aviso":    # azul de transmissão, levemente lavado
        a = y + (a - y) * (0.9 + 0.05 * np.sin(t * 0.4))
        a = 0.03 + a * 0.95
    elif tipo == "fria":
        a = y + (a - y) * s * 0.9
        a = a * np.array([0.92, 0.98, 1.08], np.float32)
    elif tipo == "limpa":
        return a
    a = np.clip(a, 0, 1.5) ** g
    return a


# 9
def crt(a, i):
    a = np.stack([map_coordinates(a[..., c], _BARRIL, order=1, mode="constant", cval=0.0)
                  for c in range(3)], -1)
    return a * (_VIN * (0.55 + 0.45 * (1 - i * 0.5)) + (1 - (0.55 + 0.45 * (1 - i * 0.5))))


# 10
def dropouts(a, i, rng, extra=0):
    n = rng.poisson(0.15 * i) + extra
    if n == 0:
        return a
    a = a.copy()
    for _ in range(n):
        y = rng.integers(0, H)
        x = rng.integers(-20, W)
        comp = rng.integers(8, 70)
        a[y, max(0, x):max(0, min(W, x + comp))] = rng.uniform(0.8, 1.0)
        if rng.random() < 0.5 and y + 1 < H:
            a[y + 1, max(0, x + 3):max(0, min(W, x + comp - 5))] = 0.85
    return a


# 11
def glitch_forte(a, rng, tipo="blocos"):
    a = a.copy()
    if tipo in ("blocos", "misto"):
        for _ in range(rng.integers(4, 10)):
            bh, bw = rng.integers(6, 40), rng.integers(30, W)
            y, x = rng.integers(0, H - bh), rng.integers(0, W - bw)
            dx = rng.integers(-40, 40)
            bloco = a[y:y + bh, x:x + bw].copy()
            x2 = int(np.clip(x + dx, 0, W - bw))
            a[y:y + bh, x2:x2 + bw] = bloco[..., rng.permutation(3)] if rng.random() < 0.4 else bloco
    if tipo in ("inverte", "misto"):
        a = 1.0 - np.clip(a, 0, 1)
    if tipo == "rola":
        a = np.roll(a, int(rng.integers(H // 5, H // 2)), axis=0)
        a[: int(rng.integers(4, 10))] = 0.0
    return a


# 12
def estatica(rng, forca=1.0, t=0.0):
    n = rng.random((H, W // 3)).astype(np.float32)
    n = np.repeat(n, 3, axis=1)[..., None].repeat(3, -1)
    linhas = (rng.random((H, 1, 1)) * 0.5 + 0.5).astype(np.float32)
    n = n * linhas
    pos = int(H - ((t * 400) % H))
    n[max(0, pos - 18):pos] *= 0.25   # barra de tracking na estática
    return n * forca


def aplicar(img_u8, i, t, rng, tipo="tv", eventos=(), estat=0.0):
    """Pipeline completo. img_u8: np.uint8 (H,W,3)."""
    a = img_u8.astype(np.float32) / 255.0
    if i > 0.02:
        a = chroma_luma(a, i, rng)
        a = grade(a, tipo, t, i)
        a = jitter(a, i, rng, t)
        a = tracking(a, i, rng, t)
        extra = 0
        for ev in eventos:
            if ev["tipo"] == "dropout":
                extra += 3
            elif ev["tipo"] in ("blocos", "inverte", "rola", "misto"):
                a = glitch_forte(a, rng, ev["tipo"])
        a = dropouts(a, i, rng, extra)
        a = grao(a, i, rng)
        a = scanlines(a, i)
        a = head_switch(a, i, rng)
        a = crt(a, i)
    else:
        a = grade(a, "limpa", t, i)
        a = grao(a, 0.02, rng) if i > 0 else a
    if estat > 0:
        e = estatica(rng, 1.0, t)
        a = a * (1 - estat) + e * estat
    return (np.clip(a, 0, 1) * 255).astype(np.uint8)


def compor_texto(arr, camada, rng, i):
    """Texto/OSD por cima dos efeitos, com tratamento leve para continuar legível:
    croma desalinhado 1-2 px, leve borrão horizontal, scanlines e tremor mínimo por linha."""
    o = np.asarray(camada).astype(np.float32) / 255.0
    a = o[..., 3:4]
    cor = o[..., :3]
    a = uniform_filter1d(a, 2, axis=1)
    cor = uniform_filter1d(cor, 2, axis=1)
    d = 1 + int(i > 0.6)
    cor[..., 0] = np.roll(cor[..., 0], d, axis=1)
    cor[..., 2] = np.roll(cor[..., 2], -d, axis=1)
    desloc = np.where(rng.random(H) < 0.03 + 0.1 * i, rng.integers(-2, 3, H), 0)
    cor = deslocar_linhas(cor, desloc)
    a = deslocar_linhas(a, desloc)
    cor[1::2] *= 0.9
    cor = cor + rng.standard_normal((H, W, 1)).astype(np.float32) * 0.03
    base = arr.astype(np.float32) / 255.0
    out = base * (1 - a) + np.clip(cor, 0, 1) * a
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
