"""Recortes: remoção de fundo (rembg) ou chave de luminância -> P&B alto contraste + grão + retícula + borda de adesivo.
Gera também sombra e versão desfocada (profundidade de campo) de cada recorte."""
import os, sys, json
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'assets/raw')
OUT = os.path.join(ROOT, 'public/tex')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

# nome: (arquivo, crop frac (l,t,r,b), método, tamanho máx, opções)
CUTS = {
    # --- Tailândia / Quando a Morte Sussurra
    'th_fig':    ('th/still_4.jpg', (0.30, 0.0, 0.80, 1.0), 'rembg', 1300, {}),
    'th_ghost':  ('th/still_2.jpg', (0.28, 0.0, 0.74, 1.0), 'rembg', 1000, {}),
    'th_house':  ('ov/th_house_0.jpg', None, 'rembg', 1024, {}),
    'th_spirit': ('ov/th_spirit_2.jpg', None, 'rembg', 900, {}),
    'th_leaf':   ('ov/th_banana_1.jpg', None, 'rembg', 1024, {}),
    'th_bamboo': ('ov/th_bamboo_5.jpg', (0, 0, 1, 0.8), 'dark', 1024, {'thr': 120}),
    'th_mount':  ('ov/th_mount_2.jpg', (0, 0, 1, 0.6), 'notwhite', 1024, {'thr': 225}),
    'th_lamp':   ('ov/th_lamp_0.jpg', None, 'rembg', 900, {}),
    'moon':      ('ov/moon_0.jpg', None, 'bright', 800, {'thr': 28}),
    # --- Indonésia / Fortuna Maldita
    'fm_fig':    ('fm/still_2.jpg', (0.52, 0.0, 1.0, 1.0), 'rembg', 1300, {}),
    'fm_ghost':  ('fm/still_9.jpg', (0.14, 0.0, 0.52, 1.0), 'rembg', 1000, {}),
    'fm_house':  ('ov/id_villa_6.jpg', None, 'rembg', 1024, {}),
    'fm_candles': ('ov/id_candle_4.jpg', None, 'bright', 1024, {'thr': 40}),
    'fm_palm':   ('ov/id_palm_6.jpg', (0, 0, 1, 0.5), 'dark', 1024, {'thr': 70}),
    'moon2':     ('ov/moon_3.jpg', None, 'bright', 800, {'thr': 28}),
    # --- Indonésia / Impetigore
    'imp_fig':   ('imp/still_9.jpg', (0.12, 0.0, 1.0, 1.0), 'rembg', 1500, {}),
    'imp_woman': ('imp/still_2.jpg', (0.42, 0.0, 0.95, 1.0), 'rembg', 1000, {}),
    'imp_house': ('ov/id_house_1.jpg', (0, 0, 0.93, 0.86), 'notwhite', 1024, {'thr': 200}),
    'imp_wayang': ('ov/id_wayang_7.jpg', (0.0, 0.0, 0.75, 1.0), 'dark', 1024, {'thr': 95}),
    'imp_shadow': ('ov/id_wayang_2.jpg', (0.05, 0.0, 0.95, 1.0), 'dark', 900, {'thr': 70}),
    'imp_gunungan': ('ov/id_gunungan_2.jpg', (0.5, 0.0, 1.0, 1.0), 'dark', 900, {'thr': 110}),
    'imp_frond': ('ov/id_palm_7.jpg', None, 'bright', 1024, {'thr': 60}),
    # --- globais
    'gong':      ('ov/id_gong_5.jpg', (0.0, 0.0, 1.0, 0.86), 'rembg', 1024, {}),
    'cloud':     ('ov/cloud_3.jpg', (0, 0.1, 1, 0.95), 'cloud', 1024, {}),
}
BLUR = {'th_leaf': 10, 'th_bamboo': 9, 'fm_palm': 10, 'fm_candles': 8, 'imp_frond': 10, 'imp_shadow': 6, 'th_lamp': 0}

_sess = None
def rembg_alpha(im):
    global _sess
    from rembg import new_session, remove
    if _sess is None: _sess = new_session('u2net')
    return np.asarray(remove(im, session=_sess, only_mask=True)).astype(np.float32) / 255

def halftone(g, cell=5.0, ang=45):
    h, w = g.shape
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(ang)
    u = (x * np.cos(a) + y * np.sin(a)) * 2 * np.pi / cell
    v = (-x * np.sin(a) + y * np.cos(a)) * 2 * np.pi / cell
    scr = (np.cos(u) * np.cos(v) + 1) / 2
    return (g > scr * 0.9 + 0.05).astype(np.float32)

def treat_gray(rgb, alpha=None):
    g = np.asarray(ImageOps.grayscale(rgb)).astype(np.float32) / 255
    m = alpha > 0.5 if alpha is not None and (alpha > 0.5).sum() > 100 else np.ones_like(g, bool)
    lo, hi = np.percentile(g[m], [3, 97])
    g = np.clip((g - lo) / max(1e-3, hi - lo), 0, 1)
    g = g ** 0.85
    g = 0.5 - 0.5 * np.cos(np.pi * g)          # curva S: alto contraste
    g = np.clip(g + rng.normal(0, 0.085, g.shape), 0, 1)   # grão forte
    ht = halftone(cv2.GaussianBlur(g, (0, 0), 1.2))
    g = 0.42 * g + 0.58 * ht                   # retícula bem visível
    return np.clip(g, 0, 1)

def sticker(g, alpha, border):
    a = (alpha > 0.5).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border * 2 + 1, border * 2 + 1))
    out_a = cv2.dilate(a, k)
    inner = cv2.GaussianBlur(a.astype(np.float32), (0, 0), 1.0)
    outer = cv2.GaussianBlur(out_a.astype(np.float32), (0, 0), 1.0)
    col = g * inner + 1.0 * (1 - inner)        # borda branca
    rgba = np.dstack([col, col, col, outer])
    return (rgba * 255).astype(np.uint8)

def bbox_crop(arr, pad=4):
    a = arr[..., 3] > 8
    ys, xs = np.where(a)
    if len(ys) == 0: return arr
    return arr[max(0, ys.min() - pad):ys.max() + pad + 1, max(0, xs.min() - pad):xs.max() + pad + 1]

def keep_big(alpha, frac=0.02):
    a = (alpha > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(a)
    if n <= 1: return alpha
    big = st[1:, cv2.CC_STAT_AREA].max()
    keep = np.zeros_like(a)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= big * frac: keep[lab == i] = 1
    return alpha * keep

meta = {}
only = sys.argv[1:]
for name, (src, crop, method, size, opt) in CUTS.items():
    if only and name not in only: continue
    im = Image.open(os.path.join(RAW, src)).convert('RGB')
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    sc = size / max(im.size)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    lum = np.asarray(ImageOps.grayscale(im)).astype(np.float32)
    if method == 'rembg': alpha = keep_big(rembg_alpha(im), 0.05)
    elif method == 'dark': alpha = (cv2.GaussianBlur(lum, (0, 0), 1) < opt['thr']).astype(np.float32)
    elif method == 'bright': alpha = keep_big((cv2.GaussianBlur(lum, (0, 0), 1.5) > opt['thr']).astype(np.float32), 0.01)
    elif method == 'notwhite':
        a = (cv2.GaussianBlur(lum, (0, 0), 2) < opt['thr']).astype(np.uint8)
        # só o que está ligado à base (montanha), sem buracos
        a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)); alpha = keep_big(a.astype(np.float32), 0.3)
    elif method == 'cloud':
        rgb = np.asarray(im).astype(np.float32)
        whiteness = rgb.min(axis=2) - 0.5 * (rgb[..., 2] - rgb[..., 0])
        alpha = keep_big((cv2.GaussianBlur(whiteness, (0, 0), 3) > 150).astype(np.float32), 0.15)
    g = treat_gray(im, alpha)
    if method == 'dark': g = g * 0.35           # silhuetas ficam escuras, com retícula
    rgba = bbox_crop(sticker(g, alpha, border=max(4, size // 170)))
    Image.fromarray(rgba).save(os.path.join(OUT, name + '.png'))
    # sombra (alpha desfocado, baixa resolução)
    sh = Image.fromarray(rgba[..., 3]).resize((max(8, rgba.shape[1] // 4), max(8, rgba.shape[0] // 4)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    z = np.zeros((sh.height, sh.width, 4), np.uint8); z[..., 3] = (np.asarray(sh) * 0.55).astype(np.uint8)
    Image.fromarray(z).save(os.path.join(OUT, name + '_sh.png'))
    if name in BLUR and BLUR[name] > 0:
        pad = BLUR[name] * 3
        p = np.pad(rgba, ((pad, pad), (pad, pad), (0, 0)))
        pre = p.astype(np.float32); pre[..., :3] *= pre[..., 3:4] / 255
        pre = cv2.GaussianBlur(pre, (0, 0), BLUR[name])
        a = np.maximum(pre[..., 3:4], 1e-3); pre[..., :3] = pre[..., :3] / a * 255
        Image.fromarray(np.clip(pre, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name + '_blur.png'))
    meta[name] = {'w': int(rgba.shape[1]), 'h': int(rgba.shape[0]), 'blur': name in BLUR and BLUR[name] > 0}
    print(name, rgba.shape)

mp = os.path.join(ROOT, 'src/cutouts.json')
old = json.load(open(mp)) if os.path.exists(mp) else {}
old.update(meta); json.dump(old, open(mp, 'w'), indent=1)

# folha de conferência
names = sorted(old)
tiles = []
for n in names:
    im = Image.open(os.path.join(OUT, n + '.png')); im.thumbnail((300, 300))
    t = Image.new('RGB', (310, 310), (242, 59, 59)); t.paste(im, (5, 5), im); tiles.append(t)
cols = 6
sheet = Image.new('RGB', (310 * cols, 310 * ((len(tiles) + cols - 1) // cols)), 'white')
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * 310, (i // cols) * 310))
sheet.save(os.path.join(ROOT, 'out/_cutouts_sheet.jpg'), quality=82)
