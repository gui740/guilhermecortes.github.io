# Prepara os recortes: máscara (rembg ou limiar), inpainting das placas de fundo,
# tratamento P&B + alto contraste + retícula (halftone) + granulado + borda de papel.
# Uso: python3 -I src/prep.py   (gera public/cut/*.png e public/cut/manifest.json)
import os, json, glob, sys
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = f'{ROOT}/assets/raw'; MASK = f'{ROOT}/assets/masks'; OUT = f'{ROOT}/public/cut'
os.makedirs(OUT, exist_ok=True)
COLOR = '--color' in sys.argv          # versão colorida: mantém cor, mesma textura
rng = np.random.default_rng(7)

def raw(prefix):
    d, p = prefix.split('/')
    return cv2.imread(glob.glob(f'{RAW}/{d}/{p}*')[0], cv2.IMREAD_COLOR)

def largest(mask, keep=1, min_frac=0.02):
    n, lab, st, _ = cv2.connectedComponentsWithStats((mask > 127).astype(np.uint8), 8)
    if n <= 1: return mask
    areas = st[1:, cv2.CC_STAT_AREA]; order = np.argsort(-areas)
    out = np.zeros_like(mask)
    for i in order[:keep]:
        if areas[i] >= min_frac * areas[order[0]]: out[lab == i + 1] = 255
    return out

def clean(m, thr=128, keep=1, close=5):
    m = (m > thr).astype(np.uint8) * 255
    if close: m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    m = largest(m, keep)
    # preenche buracos internos
    inv = 255 - m; n, lab, st, _ = cv2.connectedComponentsWithStats((inv > 0).astype(np.uint8), 4)
    h, w = m.shape
    for i in range(1, n):
        x, y, ww, hh, a = st[i]
        if x > 0 and y > 0 and x + ww < w and y + hh < h and a < 0.02 * h * w: m[lab == i] = 255
    return cv2.GaussianBlur(m, (3, 3), 0)

def halftone_tex(img, cell):
    """img BGR uint8 -> textura de revista: alto contraste, retícula 45°, granulado."""
    if COLOR:
        base = img.astype(np.float32) / 255
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    else:
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if g.mean() < 70:   # still muito escura: equaliza localmente antes do contraste
            g = cv2.createCLAHE(3.0, (8, 8)).apply(g)
        g = g.astype(np.float32) / 255
    # alto contraste: normaliza percentis e curva S
    lo, hi = np.percentile(g, 2), np.percentile(g, 98)
    g = np.clip((g - lo) / max(hi - lo, 1e-3), 0, 1)
    g = 1 / (1 + np.exp(-(g - 0.5) * 7)); g = (g - g.min()) / (g.max() - g.min() + 1e-6)
    h, w = g.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(45); u = xx * np.cos(a) + yy * np.sin(a); v = -xx * np.sin(a) + yy * np.cos(a)
    du = (u / cell) % 1 - 0.5; dv = (v / cell) % 1 - 0.5
    dist = np.sqrt(du ** 2 + dv ** 2) * cell
    dark = cv2.GaussianBlur(1 - g, (0, 0), cell * 0.45)
    r = np.sqrt(np.clip(dark, 0, 1)) * cell * 0.72
    dots = np.clip((dist - r) / 1.2 + 0.5, 0, 1)        # 1 = papel, 0 = tinta
    tone = 0.42 * g + 0.58 * dots
    tone = tone + rng.normal(0, 0.085, tone.shape).astype(np.float32)   # granulado forte
    tone = cv2.GaussianBlur(tone, (0, 0), 0.6)
    tone = np.clip(tone, 0, 1)
    if COLOR:
        out = base * (0.35 + 0.65 * tone[..., None])
        return (np.clip(out, 0, 1) * 255).astype(np.uint8)
    # P&B puxado para o carvão/cinza-claro da paleta (#1C1C1C .. #EDEDED)
    t = 28 + tone * (237 - 28)
    return np.dstack([t, t, t]).astype(np.uint8)

def paper(mask, border):
    """borda de papel recortado (levemente irregular) em volta da máscara."""
    if border <= 0: return mask, None
    m = (mask > 100).astype(np.uint8) * 255
    noise = cv2.GaussianBlur(rng.random(m.shape).astype(np.float32), (0, 0), 6)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    d = cv2.distanceTransform(255 - m, cv2.DIST_L2, 5)
    edge = (d < border * (0.7 + 0.6 * noise)).astype(np.uint8) * 255
    edge = cv2.GaussianBlur(edge, (3, 3), 0)
    return edge, m

def finish(img, mask, name, height, cell=None, border=7, pad=48, shadow=True, blur_variant=0, soften=0):
    """recorta pelo bbox, redimensiona para height, aplica textura e salva RGBA."""
    ys, xs = np.where(mask > 60)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    img = img[y0:y1 + 1, x0:x1 + 1]; mask = mask[y0:y1 + 1, x0:x1 + 1]
    s = height / img.shape[0]
    W = max(1, int(img.shape[1] * s))
    img = cv2.resize(img, (W, height), interpolation=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA)
    mask = cv2.resize(mask, (W, height), interpolation=cv2.INTER_LINEAR)
    img = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
    mask = cv2.copyMakeBorder(mask, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    tex = halftone_tex(img, cell or max(7, height / 150))
    edge, core = paper(mask, border)
    rgba = np.zeros((*mask.shape, 4), np.uint8)
    if edge is not None:
        rgba[..., :3] = 237                             # papel #EDEDED
        a = mask.astype(np.float32)[..., None] / 255
        rgba[..., :3] = (tex * a + rgba[..., :3] * (1 - a)).astype(np.uint8)
        rgba[..., 3] = np.maximum(edge, mask)
    else:
        rgba[..., :3] = tex; rgba[..., 3] = mask
    if soften: rgba[..., :3] = cv2.GaussianBlur(rgba[..., :3], (0, 0), soften)   # fundo com blur leve
    if shadow:   # sombra suave de papel recortado sobre a camada de trás (assada no PNG)
        a = rgba[..., 3].astype(np.float32) / 255
        sh = cv2.GaussianBlur(np.roll(a, 16, axis=0), (0, 0), 11) * 0.5
        A = a + sh * (1 - a)
        C = (rgba[..., :3].astype(np.float32) * a[..., None] + 28 * sh[..., None] * (1 - a[..., None])) / np.maximum(A[..., None], 1e-4)
        rgba = np.dstack([np.clip(C, 0, 255), A * 255]).astype(np.uint8)
    out = cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)
    Image.fromarray(out).save(f'{OUT}/{name}.png', optimize=True)
    if blur_variant:   # versão desfocada para primeiro plano (profundidade de campo)
        pre = out.astype(np.float32); al = pre[..., 3:4] / 255
        pm = np.dstack([pre[..., :3] * al, al])
        pm = cv2.GaussianBlur(pm, (0, 0), blur_variant)
        rgb = pm[..., :3] / np.maximum(pm[..., 3:4], 1e-4)
        Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(pm[..., 3:4] * 255, 0, 255)]).astype(np.uint8)).save(f'{OUT}/{name}_b.png', optimize=True)
        MAN[name + '_b'] = {'w': out.shape[1], 'h': out.shape[0]}
    MAN[name] = {'w': out.shape[1], 'h': out.shape[0]}
    print(name, out.shape[1], 'x', out.shape[0])

def torn_rect(shape, x0, y0, x1, y1, jag=18):
    """máscara de papel rasgado retangular-irregular."""
    h, w = shape; m = np.zeros((h, w), np.uint8)
    pts = []
    def edge(p, q, n):
        for t in np.linspace(0, 1, n, endpoint=False):
            x = p[0] + (q[0] - p[0]) * t; y = p[1] + (q[1] - p[1]) * t
            pts.append([x + rng.normal(0, jag * 0.5), y + rng.normal(0, jag * 0.5)])
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i in range(4): edge(c[i], c[(i + 1) % 4], 40)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
    return m

def inpaint(img, hole, r=9):
    hole = cv2.dilate((hole > 60).astype(np.uint8) * 255, np.ones((25, 25), np.uint8))
    # inpainting em escala reduzida (mais estável em buracos grandes) + detalhe
    s = 0.5
    small = cv2.resize(img, None, fx=s, fy=s); hs = cv2.resize(hole, None, fx=s, fy=s)
    fill = cv2.inpaint(small, hs, r, cv2.INPAINT_TELEA)
    fill = cv2.resize(fill, (img.shape[1], img.shape[0]))
    out = img.copy(); out[hole > 0] = fill[hole > 0]
    return out

def m_rembg(key): return cv2.imread(f'{MASK}/{key}.png', cv2.IMREAD_GRAYSCALE)

MAN = {}
# ---------- figuras (rembg) ----------
FIG = {  # nome: (still, máscara, altura final, keep, crop x-frac)
    'e_smith': ('477033/2HnptuDU', 1250, 1, None),
    'e_mask': ('477033/nSCEgpwC', 1150, 1, None),
    'e_girl': ('477033/xhoHM4zE', 1050, 1, None),
    'a_dan': ('424121/xvFwSLv9', 1150, 1, (0, 0.66)),
    'a_hill': ('424121/4BJi7377', 1000, 1, (0.45, 1.0)),
    'a_walkers': ('424121/4BJi7377', 420, 2, (0, 0.45)),
    'a_hood': ('424121/7Y567LQG', 1050, 2, None),
    'a_book': ('424121/58EDJlVN', 1150, 1, None),
    'a_boat': ('424121/tvGTSdLj', 520, 1, None),
    'i_face': ('864370/cEcz50ZF', 1150, 1, None),
    'i_lantern': ('864370/5j3YVzeo', 1100, 1, None),
    'i_hands': ('864370/6d1mHKco', 1050, 1, None),
    'i_woman': ('864370/bfjLErae', 1100, 1, None),
    'i_flash': ('864370/11eJ9OWv', 1000, 1, None),
}
MKEY = {'a_walkers': 'a_hill'}
for name, (src, H, keep, crop) in FIG.items():
    img = raw(src); m = m_rembg(MKEY.get(name, name))
    if m.shape != img.shape[:2]: m = cv2.resize(m, (img.shape[1], img.shape[0]))
    if name == 'i_hands': m[int(m.shape[0] * 0.80):] = 0
    if crop:
        w = img.shape[1]; z = np.zeros_like(m); a, b = int(crop[0] * w), int(crop[1] * w); z[:, a:b] = m[:, a:b]; m = z
    m = clean(m, 110, keep)
    finish(img, m, name, H, border=8)

# ---------- figuras por limiar ----------
# Apóstolo: figura de braços abertos contra o fogo (silhueta) — o fogo vira chama chapada no React
img = raw('424121/a3qsXYK0'); g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
from rembg import new_session, remove
m = np.array(remove(Image.fromarray(img[..., ::-1]), session=new_session('isnet-general-use'), only_mask=True))
fire = cv2.dilate((g > 120).astype(np.uint8), np.ones((1, 1), np.uint8))
m = clean(m, 120, 1, 7); finish(img, m, 'a_robed', 1100, border=8)

# ---------- primeiro plano por limiar ----------
# cerca de cruzes de madeira (Errementari) — escura contra a neblina
img = raw('477033/cq5f3HHi'); g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
bgl = cv2.GaussianBlur(g, (0, 0), 40)
m = ((bgl.astype(int) - g.astype(int)) > 22).astype(np.uint8) * 255
m[int(g.shape[0] * 0.62):] = 0          # só o alto da cerca (cruzes)
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
m = largest(m, 40, 0.001); m = cv2.GaussianBlur(m, (3, 3), 0)
finish(img, m, 'fg_fence', 900, border=0, cell=8, shadow=False, blur_variant=7)

# galhos (arte do pôster de Apóstolo): traço preto em fundo claro, sem a figura
img = raw('424121/73iZGJA2'); g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
b, gg, r = cv2.split(img.astype(int))
m = ((g < 80) & ~((r - gg) > 60)).astype(np.uint8) * 255
m[:, int(g.shape[1] * 0.56):] = 0
m = largest(m, 30, 0.002); m = cv2.dilate(m, np.ones((3, 3), np.uint8))
finish(img, m, 'fg_branches', 1500, border=0, cell=9, shadow=False, blur_variant=7)

# árvores na neblina (Errementari) — tronco/galho escuro
img = raw('477033/ffS9VpJL'); g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
bgl = cv2.GaussianBlur(g, (0, 0), 60)
m = ((bgl.astype(int) - g.astype(int)) > 26).astype(np.uint8) * 255
m[int(g.shape[0] * 0.55):] = 0
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); m = largest(m, 12, 0.01)
m = cv2.GaussianBlur(m, (3, 3), 0)
finish(img, m, 'fg_trees', 1400, border=0, cell=9)

# ---------- placas de fundo (com inpainting do que ficou atrás do recorte) ----------
def plate(src, name, holes_key, box, H, crop_hole_frac=None):
    img = raw(src)
    if holes_key:
        hm = m_rembg(holes_key)
        if hm.shape != img.shape[:2]: hm = cv2.resize(hm, (img.shape[1], img.shape[0]))
        img = inpaint(img, (hm > 90).astype(np.uint8) * 255)
        cv2.imwrite(f'{ROOT}/assets/masks/{name}_inpainted.jpg', img)
    h, w = img.shape[:2]
    x0, y0, x1, y1 = [int(v) for v in (box[0] * w, box[1] * h, box[2] * w, box[3] * h)]
    m = torn_rect((h, w), x0, y0, x1, y1, jag=14)
    finish(img, m, name, H, border=9, soften=1.1)

plate('424121/4BJi7377', 'p_moor', 'a_hill', (0.0, 0.05, 1.0, 0.95), 760)       # montanhas + navio (sem o homem)
plate('477033/xhoHM4zE', 'p_forest', 'e_girl', (0.02, 0.0, 0.98, 1.0), 820)      # floresta (sem a menina)
plate('477033/lv3mfeaQ', 'p_village', None, (0.0, 0.05, 1.0, 0.95), 700)        # vila basca
plate('864370/9ak0EWYG', 'p_temple', None, (0.1, 0.0, 0.9, 1.0), 900)           # templo
plate('424121/dnU1fJ53', 'p_church', None, (0.0, 0.1, 1.0, 0.95), 700)          # congregação (grupo)
plate('864370/5j3YVzeo', 'p_lanterns', 'i_lantern', (0.0, 0.0, 1.0, 0.8), 760) # lanternas (sem a mulher)
plate('477033/cq5f3HHi', 'p_fence', None, (0.05, 0.0, 0.95, 1.0), 760)          # cerca inteira (meio)

# pôsteres (para a linha tracejada até o logo)
for src, name in [('477033/poster', 'poster_e'), ('424121/poster', 'poster_a'), ('864370/poster', 'poster_i')]:
    img = raw(src); h, w = img.shape[:2]
    finish(img, np.full((h, w), 255, np.uint8), name, 620, border=10)

json.dump(MAN, open(f'{OUT}/manifest.json', 'w'), indent=1)
