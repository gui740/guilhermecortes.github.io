"""Tratamento dos recortes: alpha (rembg ou papel), erosão 1-2px + feather, P&B alto contraste,
granulado forte + retícula visível, borda branca de adesivo (só informação), sombra suave e
'bleed' de cor nas áreas transparentes (evita halo escuro no mipmap/desfoque do 3D)."""
import numpy as np, cv2, sys, os, json
from PIL import Image
RAW, OUT = "assets/historia/raw", "assets/historia/tex"
_sess = None
def rembg_alpha(rgb):
    global _sess
    from rembg import remove, new_session
    if _sess is None: _sess = new_session("isnet-general-use")
    return np.array(remove(Image.fromarray(rgb), session=_sess, post_process_mask=True))[..., 3].astype(np.float32) / 255
def paper_alpha(rgb, thr=38, close=5, fill=True):
    """fundo claro/uniforme (pranchas botânicas, fundo branco): distância à cor da borda"""
    b = np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)])
    bg = np.median(b, 0).astype(np.float32)
    d = np.abs(rgb.astype(np.float32) - bg).max(2)
    m = (d > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close)))
    from scipy import ndimage as ndi
    if fill: m = ndi.binary_fill_holes(m)
    lab, n = ndi.label(m)
    if n:
        area = ndi.sum(m, lab, range(1, n + 1)); keep = [i + 1 for i, a in enumerate(area) if a > max(400, area.max() * 0.04)]
        m = np.isin(lab, keep)
    return m.astype(np.float32)
def clean_edge(a, erode=2, feather=1.2):
    """binariza, erode 1-2px (tira halo de fundo) e aplica feather leve"""
    m = (a > 0.5).astype(np.uint8)
    if erode: m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * erode + 1, 2 * erode + 1)))
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), feather)
def bw(rgb, contrast=1.0):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    g = cv2.createCLAHE(clipLimit=2.2 + contrast, tileGridSize=(8, 8)).apply(g).astype(np.float32) / 255
    lo, hi = np.percentile(g, 3), np.percentile(g, 97); g = np.clip((g - lo) / max(1e-3, hi - lo), 0, 1)
    return np.clip((g - .5) * (1.25 + .25 * contrast) + .5, 0, 1)
def texture(g, seed, pitch=6.0, grain=0.16, ht=0.55):
    """granulado + retícula (pontos pretos a 45°, raio pela tinta)"""
    rng = np.random.default_rng(seed); h, w = g.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); c, s = np.cos(np.pi / 4), np.sin(np.pi / 4)
    u, v = (xx * c - yy * s) / pitch, (xx * s + yy * c) / pitch
    du, dv = u - np.round(u), v - np.round(v); dist = np.sqrt(du * du + dv * dv)          # 0..0.707
    ink = 1 - g; r = np.sqrt(np.clip(ink, 0, 1)) * 0.62
    dots = np.clip((r - dist) * pitch * 0.9 + 0.5, 0, 1)                                  # antialias
    out = g * (1 - ht) + (1 - dots) * ht
    n = rng.normal(0, 1, (h, w)).astype(np.float32); n2 = cv2.resize(rng.normal(0, 1, (h // 3 + 1, w // 3 + 1)).astype(np.float32), (w, h))
    out = out + (0.7 * n + 0.5 * n2) * grain
    return np.clip(out, 0, 1)
def finish(g, a, name, border=0, shadow=True, maxside=1024, green=False):
    h, w = a.shape; pad = int(max(h, w) * 0.06) + border + 8
    g = np.pad(g, pad, constant_values=1); a = np.pad(a, pad)
    if border:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * border + 1, 2 * border + 1))
        ab = cv2.GaussianBlur(cv2.dilate((a > .5).astype(np.uint8), k).astype(np.float32), (0, 0), 1.0)
        g = g * a + 1.0 * (1 - a); a = np.maximum(a, ab)                                      # branco do adesivo
    if shadow:
        off = int(max(h, w) * 0.018) + 2; sh = np.zeros_like(a); sh[off:, off:] = a[:-off, :-off]
        sh = cv2.GaussianBlur(sh, (0, 0), max(h, w) * 0.012 + 2) * 0.42
        A = a + sh * (1 - a); G = (g * a + 0.0 * sh * (1 - a)) / np.maximum(A, 1e-4)
    else: A, G = a, g
    # bleed: área transparente recebe a cor da borda mais próxima
    m = (A > 0.02).astype(np.uint8); G8 = (np.clip(G, 0, 1) * 255).astype(np.uint8)
    if (m == 0).any():
        _, lab = cv2.distanceTransformWithLabels(1 - m, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
        ys, xs = np.nonzero(m); idx = np.zeros(lab.max() + 1, np.int64)
        lab_on = lab[ys, xs]; idx[lab_on] = ys * G8.shape[1] + xs
        G8 = G8.reshape(-1)[idx[lab]].reshape(G8.shape) * (1 - m) + G8 * m
    ys, xs = np.nonzero(A > 0.01); y0, y1, x0, x1 = max(0, ys.min() - 4), ys.max() + 5, max(0, xs.min() - 4), xs.max() + 5
    rgba = np.dstack([G8, G8, G8, (np.clip(A, 0, 1) * 255).astype(np.uint8)])[y0:y1, x0:x1]
    im = Image.fromarray(rgba, "RGBA"); im.thumbnail((maxside, maxside), Image.LANCZOS)
    im.save(f"{OUT}/{name}.png", optimize=True); return im.size
def load(name, maxside=1400):
    p = [f for f in os.listdir(RAW) if os.path.splitext(f)[0] == name][0]
    im = Image.open(f"{RAW}/{p}").convert("RGB"); im.thumbnail((maxside, maxside), Image.LANCZOS); return np.array(im)
def crop(rgb, box):
    if not box: return rgb
    h, w = rgb.shape[:2]; x0, y0, x1, y1 = box; return rgb[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
def make(spec, seed):
    rgb = crop(load(spec["src"]), spec.get("box"))
    mode = spec.get("mode", "rembg")
    if mode == "rect": a = np.ones(rgb.shape[:2], np.float32)
    elif mode == "paper": a = paper_alpha(rgb, spec.get("thr", 38), spec.get("close", 5), spec.get("fill", True))
    elif mode == "both": a = np.maximum(rembg_alpha(rgb) > .5, paper_alpha(rgb, spec.get("thr", 38)) > .5).astype(np.float32)
    else: a = rembg_alpha(rgb)
    if mode != "rect": a = clean_edge(a, spec.get("erode", 2))
    else: a = np.pad(np.ones((rgb.shape[0] - 4, rgb.shape[1] - 4), np.float32), 2)
    g = texture(bw(rgb, spec.get("contrast", 1.0)), seed, pitch=spec.get("pitch", 6.0) * max(rgb.shape[:2]) / 1000)
    return finish(g, a, spec["name"], border=spec.get("border", 0), shadow=spec.get("shadow", True))
if __name__ == "__main__":
    specs = json.load(open(sys.argv[1])); only = set(sys.argv[2:])
    for i, s in enumerate(specs):
        if only and s["name"] not in only: continue
        try: print(s["name"], make(s, i))
        except Exception as e: print("ERRO", s["name"], repr(e)[:200])
