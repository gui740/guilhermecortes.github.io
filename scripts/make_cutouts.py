"""Recorta (rembg), converte para P&B de alto contraste e aplica granulado + retícula (halftone).
Saída: public/cut/<nome>.png (RGBA)."""
import os, sys, json, numpy as np
from PIL import Image, ImageFilter, ImageOps
import subprocess
from scipy import ndimage as ndi
PICKS = {
    "blair_olhos":  ("assets/raw/blair/backdrop_6.jpg", {}),
    "blair_medo":   ("assets/raw/blair/backdrop_9.jpg", {"crop_left": 0.375}),  # tira o galho solto à esquerda
    "blair_lanterna": ("assets/raw/blair/backdrop_10.jpg", {}),
    "demo_palco":   ("assets/raw/demonio/backdrop_3.jpg", {}),
    "gon_camera":   ("assets/raw/gonjiam/backdrop_10.jpg", {}),
    "gon_escuro":   ("assets/raw/gonjiam/backdrop_6.jpg", {}),
    "demo_host":    ("assets/raw/demonio/backdrop_2.jpg", {}),
    "demo_grito":   ("assets/raw/demonio/backdrop_4.jpg", {}),
    "demo_menina":  ("assets/raw/demonio/backdrop_5.jpg", {}),
    "gon_medo":     ("assets/raw/gonjiam/backdrop_1.jpg", {}),
    "gon_grupo":    ("assets/raw/gonjiam/backdrop_3.jpg", {}),
    "gon_close":    ("assets/raw/gonjiam/backdrop_4.jpg", {}),
    "gon_predio":   ("assets/raw/gonjiam/backdrop_2.jpg", {}),
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

def clean_mask(a):
    """Limpa a máscara: remove pedaços soltos, fecha furinhos e suaviza o contorno."""
    m = a > 0.5
    lab, n = ndi.label(m)
    if n > 1:
        sizes = ndi.sum(m, lab, range(1, n + 1))
        keep = [i + 1 for i, sz in enumerate(sizes) if sz >= 0.06 * sizes.max()]
        m = np.isin(lab, keep)
    holes = ndi.binary_fill_holes(m) & ~m
    hl, hn = ndi.label(holes)
    if hn:
        hs = ndi.sum(holes, hl, range(1, hn + 1))
        small = [i + 1 for i, sz in enumerate(hs) if sz < 0.004 * m.sum()]
        m |= np.isin(hl, small)
    # contorno suave; as bordas do quadro original continuam retas (padding por replicação)
    sm = ndi.gaussian_filter(np.pad(m.astype(np.float32), 12, mode="edge"), 2.2)[12:-12, 12:-12]
    return np.clip((sm - 0.5) * 3.0 + 0.5, 0, 1) * np.maximum(a, m)

def treat(rgba):
    rgba.thumbnail((MAXSIDE, MAXSIDE), Image.LANCZOS)
    a = clean_mask(np.asarray(rgba.split()[3]).astype(np.float32) / 255)
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
    alpha = a
    arr = np.dstack([lum, lum, lum, alpha * 255]).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

if __name__ == "__main__":
    os.makedirs("public/cut", exist_ok=True); os.makedirs("build/cut_raw", exist_ok=True)
    meta = {}
    for name, (src, opt) in PICKS.items():
        raw = f"build/cut_raw/{name}.png"
        if not os.path.exists(raw):   # BiRefNet, um processo por imagem (memória)
            subprocess.run([sys.executable, "scripts/rembg_one.py", src, raw], check=True, stderr=subprocess.DEVNULL)
        rgba = Image.open(raw).convert("RGBA")
        if "crop_left" in opt: rgba = rgba.crop((int(rgba.width * opt["crop_left"]), 0, rgba.width, rgba.height))
        out = treat(rgba)
        out.save(f"public/cut/{name}.png")
        meta[name] = {"w": out.width, "h": out.height, "src": src}
        print(name, out.size)
    json.dump(meta, open("public/cut/meta.json", "w"), indent=1)
