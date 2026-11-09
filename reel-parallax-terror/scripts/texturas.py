#!/usr/bin/env python3
"""Gera os quadros de granulação de filme (ruído) usados pelo FilmGrain: assets/textura/grao_0..7.png"""
import numpy as np, pathlib
from PIL import Image, ImageFilter
ROOT = pathlib.Path(__file__).resolve().parent.parent
out = ROOT / "assets" / "textura"; out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)
for i in range(8):
    n = rng.normal(128, 52, (960, 540)).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(n, "L").filter(ImageFilter.GaussianBlur(0.6))
    # alguns riscos/poeira de película
    a = np.array(im)
    for _ in range(rng.integers(2, 6)):
        x, y, r = rng.integers(0, 540), rng.integers(0, 960), rng.integers(1, 3)
        a[max(y - r, 0):y + r, max(x - r, 0):x + r] = 255 if rng.random() < .5 else 0
    if rng.random() < .5:
        x = rng.integers(0, 540); a[:, x:x + 1] = np.clip(a[:, x:x + 1].astype(int) + 60, 0, 255)
    Image.fromarray(a).save(out / f"grao_{i}.png", optimize=True)
print("ok")

# ---- papel envelhecido (fundo das polaroides, fichas, impressos) ----
def _ruido(h, w, escalas, seed):
    r = np.random.default_rng(seed); o = np.zeros((h, w), np.float32)
    for s, a in escalas:
        n = r.standard_normal((h // s + 2, w // s + 2)).astype(np.float32)
        o += a * np.array(Image.fromarray(n).resize((w, h), Image.BICUBIC))
    return o / np.abs(o).max()
H = W = 1024
fib = _ruido(H, W, ((1, .35), (3, .35), (12, .3)), 11)
man = _ruido(H, W, ((90, .7), (220, .3)), 12)
base = np.array([238, 230, 212], np.float32)
img = base[None, None, :] * (1 + 0.045 * fib[..., None]) - np.clip(man, 0, 1)[..., None] * np.array([18, 24, 40], np.float32)
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out / "papel.jpg", quality=90)
print("ok papel")
