"""Fumaça (ruído fractal), sprite de partícula e granulado de tela."""
import numpy as np, cv2
from PIL import Image
OUT = "assets/historia/tex"; rng = np.random.default_rng(1961)
def fbm(h, w, oct=6, base=6):
    acc = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(oct):
        s = base * 2 ** o; n = rng.normal(0, 1, (int(h * s / w) + 2, s + 2)).astype(np.float32)
        acc += amp * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC); tot += amp; amp *= 0.55
    return acc / tot
for i in range(4):
    h, w = 512, 1024; n = fbm(h, w); n = (n - n.min()) / (n.max() - n.min())
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    band = np.exp(-((yy - h / 2) / (h * (0.22 + 0.05 * i))) ** 2) * np.clip(np.sin(np.pi * xx / w) * 1.4, 0, 1)
    a = np.clip((n - 0.38) * 2.2, 0, 1) ** 1.4 * band
    a = cv2.GaussianBlur(a, (0, 0), 2.5)
    wisp = np.clip((fbm(h, w, 5, 14) - .1) * 2, 0, 1) * band * .35
    a = np.clip(a + wisp, 0, 1)
    rgba = np.dstack([np.full((h, w), 255, np.uint8)] * 3 + [(a * 255).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").save(f"{OUT}/smoke{i}.png", optimize=True)
s = 64; yy, xx = np.mgrid[0:s, 0:s].astype(np.float32); r = np.hypot(xx - s / 2 + .5, yy - s / 2 + .5) / (s / 2)
a = np.clip(1 - r, 0, 1) ** 2.2
Image.fromarray(np.dstack([np.full((s, s), 255, np.uint8)] * 3 + [(a * 255).astype(np.uint8)]), "RGBA").save(f"{OUT}/dot.png")
for i in range(6):
    n = rng.normal(0, 1, (960, 540)).astype(np.float32) * .8 + cv2.resize(rng.normal(0, 1, (320, 180)).astype(np.float32), (540, 960)) * .5
    g = np.clip(128 + n * 34, 0, 255).astype(np.uint8)
    Image.fromarray(g, "L").save(f"{OUT}/grain{i}.png", optimize=True)
print("ok")
