"""Recorta (rembg), converte para P&B de alto contraste e aplica granulado + retícula (halftone).
Saída: public/cut/<nome>.png (RGBA)."""
import os, sys, json, numpy as np
from PIL import Image, ImageFilter, ImageOps
from rembg import remove, new_session
PICKS = {
    "blair_olhos":  ("assets/raw/blair/backdrop_6.jpg", {}),
    "blair_medo":   ("assets/raw/blair/backdrop_10.jpg", {}),
    "blair_olhos2": ("assets/raw/blair/backdrop_7.jpg", {}),
    "demo_host":    ("assets/raw/demonio/backdrop_2.jpg", {}),
    "demo_camera":  ("assets/raw/demonio/backdrop_6.jpg", {}),
    "demo_grito":   ("assets/raw/demonio/backdrop_4.jpg", {}),
    "demo_menina":  ("assets/raw/demonio/backdrop_5.jpg", {}),
    "gon_medo":     ("assets/raw/gonjiam/backdrop_1.jpg", {}),
    "gon_grupo":    ("assets/raw/gonjiam/backdrop_3.jpg", {}),
    "gon_close":    ("assets/raw/gonjiam/backdrop_4.jpg", {}),
    "gon_predio":   ("assets/raw/gonjiam/backdrop_11.jpg", {}),
}
MAXSIDE = 1500
rng = np.random.default_rng(7)

def halftone(gray, cell=7, angle=45):
    """gray: float 0..1 -> retícula de pontos (0..1)."""
    h, w = gray.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(angle)
    u = (xx * np.cos(a) + yy * np.sin(a)) / cell
    v = (-xx * np.sin(a) + yy * np.cos(a)) / cell
    d = np.sqrt((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2) / 0.7071  # 0 centro .. 1 canto
    dark = 1.0 - gray
    return 1.0 - np.clip((np.sqrt(dark) * 1.02 - d) * cell * 0.9 + 0.5, 0, 1)

def treat(rgba):
    rgba.thumbnail((MAXSIDE, MAXSIDE), Image.LANCZOS)
    a = np.asarray(rgba.split()[3]).astype(np.float32) / 255
    ys, xs = np.where(a > 0.08)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    rgba = rgba.crop(box); a = a[box[1]:box[3], box[0]:box[2]]
    g = ImageOps.grayscale(rgba.convert("RGB"))
    # contraste: equaliza só dentro da máscara, depois curva em S
    g = np.asarray(g).astype(np.float32) / 255
    inside = g[a > 0.5]
    lo, hi = np.percentile(inside, [2, 98])
    g = np.clip((g - lo) / max(hi - lo, 1e-3), 0, 1)
    g = g ** 0.85
    g = 0.5 + 0.5 * np.tanh((g - 0.5) * 3.2) / np.tanh(1.6)   # S-curve
    g = np.clip(g + rng.normal(0, 0.07, g.shape), 0, 1)        # granulado
    ht = halftone(np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32) / 255)
    out = np.clip(0.42 * g + 0.58 * ht, 0, 1)
    out = np.clip((out - 0.08) / 0.84, 0, 1)
    # tons limitados à paleta: preto-carvão (#1C1C1C) -> cinza-claro (#EDEDED)
    lum = 28 + out * (237 - 28)
    alpha = np.clip((a - 0.35) / 0.3, 0, 1)
    arr = np.dstack([lum, lum, lum, alpha * 255]).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

if __name__ == "__main__":
    os.makedirs("public/cut", exist_ok=True)
    only = sys.argv[1:]
    sess = new_session("isnet-general-use")
    meta = {}
    for name, (src, opt) in PICKS.items():
        if only and name not in only: continue
        im = Image.open(src).convert("RGB")
        cut = remove(im, session=sess, post_process_mask=True)
        out = treat(cut)
        out.save(f"public/cut/{name}.png")
        meta[name] = {"w": out.width, "h": out.height, "src": src}
        print(name, out.size)
    if not only: json.dump(meta, open("public/cut/meta.json", "w"), indent=1)
