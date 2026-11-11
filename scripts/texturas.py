"""Texturas procedurais: granulado de papel (6 variações p/ o 'boil'), pontinhos/manchas e retícula dos cantos."""
import numpy as np, cv2
from PIL import Image
W, H = 1080, 1920; O = "reel/tex"; rng = np.random.default_rng(740)
def grain(i):
    n = rng.normal(0, 1, (H, W)).astype(np.float32)
    n = 0.75 * n + 0.6 * cv2.resize(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    fib = cv2.GaussianBlur(rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32), (0, 0), 3)   # manchas largas de impressão
    n += 1.6 * cv2.resize(fib, (W, H), interpolation=cv2.INTER_CUBIC)
    g = np.clip(128 + n * 20, 0, 255).astype(np.uint8)
    Image.fromarray(g, "L").save(f"{O}/grain{i}.png", optimize=True)
def specks(i):
    a = np.zeros((H * 2, W * 2), np.float32)
    for _ in range(420):
        x, y = rng.integers(0, W * 2), rng.integers(0, H * 2); r = rng.choice([1, 1, 2, 2, 3, 4, 6]); v = rng.uniform(.35, .9)
        cv2.circle(a, (int(x), int(y)), int(r), float(v), -1)
    for _ in range(26):   # respingos em grupo
        cx, cy = rng.integers(0, W * 2), rng.integers(0, H * 2)
        for _ in range(rng.integers(4, 12)):
            cv2.circle(a, (int(cx + rng.normal(0, 26)), int(cy + rng.normal(0, 26))), int(rng.integers(1, 4)), float(rng.uniform(.4, .85)), -1)
    for _ in range(7):    # manchas leves
        m = np.zeros_like(a); cv2.circle(m, (int(rng.integers(0, W * 2)), int(rng.integers(0, H * 2))), int(rng.integers(60, 180)), 0.035, -1)
        a = np.maximum(a, cv2.GaussianBlur(m, (0, 0), 30))
    a = cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgba).save(f"{O}/specks{i}.png", optimize=True)
def halftone(name, blobs, pitch=17, rmax=6.6):
    S = 3; a = np.zeros((H * S, W * S), np.uint8)
    nz = cv2.resize(cv2.GaussianBlur(rng.normal(0, 1, (H // 16, W // 16)).astype(np.float32), (0, 0), 2.2), (W, H)); nz /= np.abs(nz).max()
    row = 0; y = 0.0
    while y < H:
        x = (pitch / 2 if row % 2 else 0.0)
        while x < W:
            f = 0.0
            for bx, by, R in blobs: f = max(f, 1 - np.hypot(x - bx, (y - by) * 0.8) / R)
            f += 0.10 * nz[min(int(y), H - 1), min(int(x), W - 1)]
            r = rmax * np.clip(f, 0, 1) ** 0.9
            if r > 0.9: cv2.circle(a, (int(x * S), int(y * S)), int(r * S), 255, -1, cv2.LINE_AA)
            x += pitch
        y += pitch * 0.866; row += 1
    a = cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., 3] = a
    Image.fromarray(rgba).save(f"{O}/{name}.png", optimize=True)
for i in range(6): grain(i); specks(i)
halftone("halftoneA", [(-20, 40, 230), (1110, 520, 210), (-30, 1240, 200), (1120, 1800, 300)])
halftone("halftoneB", [(1110, 60, 230), (-30, 600, 200), (1120, 1300, 200), (-20, 1850, 300)])
