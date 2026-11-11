"""Recorta as fotos dos slides, remove o fundo (rembg) e reconstrói por inpainting
o que estava coberto por texto/etiquetas/interface do Instagram."""
import numpy as np, cv2, os
from PIL import Image
from rembg import remove, new_session
S = "assets/slides"; O = "assets/recortes"; os.makedirs(O, exist_ok=True)
sess = new_session("isnet-general-use")
PAPER = np.array([234, 231, 220], np.float32)
def slide(n): return cv2.cvtColor(cv2.imread(f"{S}/{n:02d}.jpg"), cv2.COLOR_BGR2RGB)
def inpaint(img, boxes, r=6):
    m = np.zeros(img.shape[:2], np.uint8)
    for b in boxes:
        if len(b) == 3: cv2.circle(m, (b[0], b[1]), b[2], 255, -1)
        else: m[b[1]:b[3], b[0]:b[2]] = 255
    return cv2.inpaint(img, m, r, cv2.INPAINT_TELEA)
def key(img, lo=18, hi=70):
    """alpha por distância ao papel creme (para cenas com mesa/prédio que se fundem ao papel)"""
    lum = img.astype(np.float32).mean(2); a = np.clip((PAPER.mean() - lum - lo) / (hi - lo), 0, 1)
    return a
def rb(img):
    out = np.array(remove(Image.fromarray(img), session=sess, post_process_mask=True))
    return out[..., 3].astype(np.float32) / 255
def save(name, img, a, pad=0):
    a = cv2.GaussianBlur(a, (0, 0), 0.8)
    ys, xs = np.where(a > 0.03); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([img, (a * 255).astype(np.uint8)])[y0:y1, x0:x1]
    Image.fromarray(rgba).save(f"{O}/{name}.png"); print(name, rgba.shape, (x0, y0))
def solid(c, rem=None, thr=0.35, lo=18, hi=70, close=9, min_area=2500, skip=()):
    """máscara sólida: contraste com o papel (+ rembg), fecha buracos e descarta texto/pontinhos soltos"""
    from scipy import ndimage as ndi
    k = key(c, lo, hi)
    for col, tol in skip:   # cores chapadas do layout (círculo verde, tarja amarela) não são foto
        k[np.abs(c.astype(np.float32) - np.array(col, np.float32)).max(2) < tol] = 0
    hard = k > thr
    if rem is not None: hard |= rem > 0.5
    hard = cv2.morphologyEx(hard.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close)))
    hard = ndi.binary_fill_holes(hard)
    lab, n = ndi.label(hard)
    if n:
        area = ndi.sum(hard, lab, range(1, n + 1)); hard = np.isin(lab, [i + 1 for i, v in enumerate(area) if v >= min_area])
    return hard.astype(np.float32)
def cut(n, box, name, mode="both", fix=(), mask_fn=None, erase=(), **kw):
    img = slide(n)
    if fix: img = inpaint(img, fix)
    x0, y0, x1, y1 = box; c = img[y0:y1, x0:x1].copy()
    for e in erase: c[e[1]:e[3], e[0]:e[2]] = PAPER.astype(np.uint8)   # texto do slide: nunca vira imagem
    if mode == "rembg": a = solid(c, rb(c), thr=9, **kw)
    elif mode == "key": a = solid(c, None, **kw)
    else: a = solid(c, rb(c), **kw)
    if mask_fn is not None: a = a * mask_fn(c.shape[0], c.shape[1])
    save(name, c, a)
def poly(pts, inv=False):
    def f(h, w):
        m = np.zeros((h, w), np.float32); cv2.fillPoly(m, [np.array(pts, np.int32)], 1.0)
        m = cv2.GaussianBlur(m, (0, 0), 1.2); return 1 - m if inv else m
    return f
def fix_agente():
    """a tarja amarela passava atrás do topo da cabeça: reconstrói o cabelo por inpainting"""
    p = f"{O}/agente_mpt.png"; im = np.array(Image.open(p)); rgb = im[..., :3].copy()
    m = ((rgb[..., 0].astype(int) - rgb[..., 2] > 45) & (im[..., 3] > 0)).astype(np.uint8) * 255; m[60:] = 0
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    im[..., :3] = cv2.inpaint(rgb, m, 5, cv2.INPAINT_TELEA); Image.fromarray(im).save(p)
GREEN = ((221, 227, 191), 16); YELLOW = ((246, 218, 94), 60); PINK = ((235, 207, 201), 14)
if __name__ == "__main__":
    cut(1, (380, 490, 1179, 1443), "mao_celular", erase=[(620, 190, 700, 400)])
    box = (60, 560, 1179, 1415)
    emp = [(0, 0), (500, 0), (500, 330), (560, 420), (640, 560), (790, 600), (800, 855), (0, 855)]
    txt = [(0, 0, 700, 175), (300, 0, 620, 60)]
    cut(2, box, "funcionario", mask_fn=poly(emp), erase=txt, skip=[PINK])
    cut(2, box, "chefe", mask_fn=poly(emp, inv=True), erase=txt)
    cut(3, (0, 520, 1179, 1414), "celular_mesa", close=15)
    cut(4, (0, 880, 830, 1412), "mao_comprovante", erase=[(100, 0, 330, 40), (640, 0, 830, 75), (745, 0, 830, 95)], lo=6, hi=30, thr=0.3, skip=[GREEN], close=13)
    cut(5, (0, 700, 660, 1441), "celular_audio", erase=[(0, 0, 230, 60)], skip=[GREEN])
    cut(6, (0, 490, 240, 650), "mao_apontando", mode="rembg", min_area=800)
    cut(6, (700, 700, 1179, 1447), "agente_mpt", skip=[YELLOW], erase=[(0, 0, 479, 78)])
    fix_agente()
    cut(7, (560, 40, 1179, 1450), "procuradora", mode="rembg", fix=[(1030, 30, 1145, 120)])
    cut(7, (0, 1080, 700, 1450), "urna", mode="key", fix=[(80, 1387, 46)], close=25, lo=10, hi=50)
    cut(8, (0, 690, 1179, 1425), "predio", mode="key", fix=[(80, 1367, 46), (740, 670, 1080, 790)], lo=8, hi=40, close=31, erase=[(0, 0, 600, 40)])
