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
