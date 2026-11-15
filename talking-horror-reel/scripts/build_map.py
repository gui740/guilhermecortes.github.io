"""Mapa da Ásia (Natural Earth, domínio público) como recorte de papelão:
- public/tex/map.png: todos os países em cinza claro texturizado, com espessura falsa (extrude) e sombra
- src/geo.json: polígonos de Tailândia e Indonésia em coordenadas do mundo, para extrusão 3D real
- public/tex/paper.png: textura de papel/mapa antigo com retícula (procedural)"""
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LON0, LON1, LAT0, LAT1 = 55.0, 155.0, -15.0, 57.0
KX = 0.97                      # compressão leste-oeste (cos ~15°)
W = 6144; PPD = W / ((LON1 - LON0) * KX); H = int((LAT1 - LAT0) * PPD)
rng = np.random.default_rng(3)

def world(lon, lat):           # coordenadas do mundo 3D (x leste, z sul)
    return ((lon - 105.0) * KX, -(lat - 15.0))
def px(lon, lat):
    return ((lon - LON0) * KX * PPD, (LAT1 - lat) * PPD)

def paper(w, h, base=0.84, amp=0.10):
    n = np.zeros((h, w), np.float32)
    for s, a in ((2, .25), (9, .3), (40, .3), (160, .15)):
        t = rng.normal(0, 1, (h // s + 2, w // s + 2)).astype(np.float32)
        n += a * cv2.resize(t, (w, h), interpolation=cv2.INTER_CUBIC)
    fib = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=12, sigmaY=0.6)
    n += fib * 1.5
    return np.clip(base + amp * n, 0, 1)

def halftone(g, cell=7.0, ang=30):
    h, w = g.shape
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(ang)
    u = (x * np.cos(a) + y * np.sin(a)) * 2 * np.pi / cell
    v = (-x * np.sin(a) + y * np.cos(a)) * 2 * np.pi / cell
    return ((np.cos(u) * np.cos(v) + 1) / 2).astype(np.float32)

feats = json.load(open(os.path.join(ROOT, 'assets/raw/map/ne50.geojson')))['features']
def polys(f):
    g = f['geometry']
    return g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]

mask = Image.new('L', (W, H), 0); d = ImageDraw.Draw(mask)
edges = Image.new('L', (W, H), 0); de = ImageDraw.Draw(edges)
for f in feats:
    b = f.get('bbox')
    for poly in polys(f):
        ring = poly[0]
        lons = [p[0] for p in ring]; lats = [p[1] for p in ring]
        if max(lons) < LON0 - 5 or min(lons) > LON1 + 5 or max(lats) < LAT0 - 5 or min(lats) > LAT1 + 5: continue
        pts = [px(*p[:2]) for p in ring]
        d.polygon(pts, fill=255)
        de.line(pts + [pts[0]], fill=255, width=3)
m = np.asarray(mask).astype(np.float32) / 255
e = np.asarray(edges).astype(np.float32) / 255

EX = 9   # espessura do papelão em px
tex = paper(W, H, 0.80, 0.085)
ht = halftone(tex)
top = np.clip(tex - 0.10 * (ht > 0.72), 0, 1)            # retícula sobre o papel
top = np.clip(top * (1 - 0.55 * e) , 0, 1)               # fronteiras
side = np.roll(m, EX, axis=0); side[:EX] = 0              # lateral do recorte (deslocada p/ baixo)
for k in range(1, EX): side = np.maximum(side, np.roll(m, k, axis=0))
shadow = cv2.GaussianBlur(np.roll(np.roll(m, EX + 14, axis=0), 10, axis=1), (0, 0), 12) * 0.38

rgb = np.zeros((H, W), np.float32); alpha = np.zeros((H, W), np.float32)
alpha = np.maximum(alpha, shadow)                         # sombra preta
rgb = np.where(side > 0.5, 0.36, rgb); alpha = np.maximum(alpha, side)
# borda branca fina estilo adesivo
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
inner = cv2.erode((m > 0.5).astype(np.uint8), k).astype(np.float32)
face = np.where(inner > 0.5, top, 0.97)
rgb = np.where(m > 0.5, face, rgb); alpha = np.maximum(alpha, m)
out = np.dstack([rgb, rgb, rgb, alpha])
Image.fromarray((out * 255).astype(np.uint8)).save(os.path.join(ROOT, 'public/tex/map.png'))

# textura de papel p/ peças 3D e fundos
p = paper(1024, 1024, 0.86, 0.075); p = np.clip(p - 0.09 * (halftone(p, 6, 30) > 0.74), 0, 1)
Image.fromarray((p * 255).astype(np.uint8)).save(os.path.join(ROOT, 'public/tex/paper.png'))

# polígonos para extrusão real
def simplify(ring, tol):
    pts = np.array([world(*q[:2]) for q in ring], np.float32).reshape(-1, 1, 2)
    ap = cv2.approxPolyDP(pts, tol, True).reshape(-1, 2)
    return [[round(float(x), 3), round(float(z), 3)] for x, z in ap]
geo = {}
for name in ('Thailand', 'Indonesia'):
    f = [x for x in feats if x['properties']['ADMIN'] == name][0]
    rings = []
    for poly in polys(f):
        r = simplify(poly[0], 0.035)
        if len(r) >= 4:
            a = cv2.contourArea(np.array(r, np.float32))
            if a > 0.25: rings.append(r)
    geo[name] = rings
    print(name, len(rings), sum(len(r) for r in rings))
geo['bounds'] = {'x0': world(LON0, 0)[0], 'x1': world(LON1, 0)[0], 'z0': world(0, LAT1)[1], 'z1': world(0, LAT0)[1]}
json.dump(geo, open(os.path.join(ROOT, 'src/geo.json'), 'w'))
print('map', W, H, geo['bounds'])
