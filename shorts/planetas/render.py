"""YouTube Short: O TAMANHO REAL DOS PLANETAS
1080x1920, 30 fps, 25 s. Tudo procedural (Python + numpy + PIL + ffmpeg).

Uso:
  python render.py preview 0 1.7 5.2 ...   -> PNGs dos frames-chave em out/preview
  python render.py video                   -> out/video_mudo.mp4
"""
import os, sys, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
CACHE = os.path.join(OUT, "cache")
W, H, FPS = 1080, 1920, 30
DUR = 25.0
NFRAMES = int(DUR * FPS)
SAFE_R = W - 120          # nada importante à direita disto
SAFE_B = H - 300          # nada importante abaixo disto
CX = SAFE_R / 2           # centro horizontal da área segura (480)

YEL = (255, 214, 60)
WHITE = (255, 255, 255)
NAVY = (10, 18, 48)

# ----------------------------------------------------------------- planetas
EARTH_D = 12742.0
PLANETS = [  # nome, diâmetro km, rótulo "Nx"
    ("MERCÚRIO", 4879.0, None),
    ("MARTE", 6779.0, None),
    ("VÊNUS", 12104.0, None),
    ("TERRA", 12742.0, None),
    ("NETUNO", 49244.0, "3,9x"),
    ("URANO", 50724.0, "4x"),
    ("SATURNO", 116460.0, "9,1x"),
    ("JÚPITER", 139820.0, "11x"),
    ("SOL", 109 * EARTH_D, "109x"),
]
RING_OUT = 2.30  # anel de Saturno (raio externo / raio do planeta)
IDX = {p[0]: i for i, p in enumerate(PLANETS)}


def layout():
    xs, x = [], 0.0
    prev_w = None
    for i, (name, d, _) in enumerate(PLANETS):
        r = d / 2
        w = r * RING_OUT if name == "SATURNO" else r
        if prev_w is not None:
            if i <= 3:
                gap = 1600
            elif name == "NETUNO":
                gap = 9000
            elif name == "SOL":
                gap = 260000
            else:
                gap = 20000
            x += prev_w + gap + w
        xs.append(x)
        prev_w = w
    return np.array(xs)


XS = layout()
XS -= XS[IDX["TERRA"]]
R_KM = np.array([p[1] / 2 for p in PLANETS])


# ----------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smoother(x):
    x = clamp(x)
    return x * x * x * (x * (x * 6 - 15) + 10)


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x, k=1.9):
    x = clamp(x)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


def win(t, a, b, fi=0.15, fo=0.15):
    """envelope 0..1 de uma janela [a,b)"""
    if t < a or t >= b:
        return 0.0
    return min(clamp((t - a) / fi) if fi > 0 else 1.0, clamp((b - t) / fo) if fo > 0 else 1.0)


# ----------------------------------------------------------------- câmera
def cam_key(name, d_px, cy=800.0, sx=CX):
    i = IDX[name]
    s = d_px / PLANETS[i][1]
    return s, XS[i] - (sx - CX) / s, cy + d_px / 2


def build_keys():
    keys = []
    s0, x0, b0 = cam_key("TERRA", 640, cy=900)
    keys.append((0.0, s0, x0, b0, "soft"))
    # vizinhos: Mercúrio..Terra enquadrados
    left = XS[0] - R_KM[0]
    right = XS[3] + R_KM[3]
    s1 = 860 / (right - left)
    keys.append((3.5, s1, (left + right) / 2, 1000.0, "soft"))
    for t, n, d, cy in [(5.2, "NETUNO", 520, 790), (7.2, "URANO", 470, 790),
                        (9.2, "SATURNO", 330, 800), (11.2, "JÚPITER", 360, 800)]:
        s, x, b = cam_key(n, d, cy)
        keys.append((t, s, x, b, "soft"))
    s5, x5, b5 = keys[-1][1:4]
    keys.append((12.4, s5 * 0.93, x5 + 40 / s5, b5 + 10, "soft"))
    # revelação do Sol: Sol com 760 px, centro em x=990, base em y=1450
    sS = 760 / PLANETS[IDX["SOL"]][1]
    xS = XS[IDX["SOL"]] - (990 - CX) / sS
    keys.append((15.4, sS, xS, 1450.0, "in"))   # chega rápido -> impacto
    keys.append((19.8, sS * 0.965, xS + 8 / sS, 1440.0, "lin"))
    keys.append((24.0, sS * 0.93, xS + 18 / sS, 1430.0, "lin"))
    keys.append((25.0, s0, x0, b0, "loop"))
    return keys


KEYS = build_keys()


def camera(t):
    t = t % DUR
    for k in range(len(KEYS) - 1):
        ta, sa, xa, ba, _ = KEYS[k]
        tb, sb, xb, bb, mode = KEYS[k + 1]
        if ta <= t < tb or k == len(KEYS) - 2:
            tau = clamp((t - ta) / (tb - ta))
            if mode == "soft":      # nunca para: 25% de componente linear
                u = 0.75 * smoother(tau) + 0.25 * tau
            elif mode == "in":      # acelera até o impacto
                u = 0.35 * tau + 0.65 * tau ** 2.6
            elif mode == "lin":
                u = tau
            else:                   # loop: rápido, aterrissa no frame 0
                u = smoother(tau) ** 0.85
            ls = math.log(sa) + (math.log(sb) - math.log(sa)) * u
            s = math.exp(ls)
            # zoom ancorado no alvo: o deslocamento em tela diminui linearmente
            uo = smoother(tau) if mode != "in" else u
            off0 = (xb - xa) * sa
            x = xb - off0 * (1 - uo) / s
            b = ba + (bb - ba) * smoother(tau)
            return s, x, b
    return KEYS[0][1:4]


def shake(t):
    dt = t - 15.4
    if dt < 0 or dt > 1.0:
        return 0.0, 0.0
    a = 34 * math.exp(-dt * 5.0)
    return (a * math.sin(dt * 71) * math.cos(dt * 13), a * math.sin(dt * 53 + 1.3))


# ----------------------------------------------------------------- ruído
class Noise:
    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        self.perm = np.concatenate([rng.permutation(256)] * 2).astype(np.int64)
        self.vals = rng.random(256).astype(np.float32)

    def v3(self, x, y, z):
        xi, yi, zi = np.floor(x), np.floor(y), np.floor(z)
        xf, yf, zf = x - xi, y - yi, z - zi
        xi = xi.astype(np.int64) & 255
        yi = yi.astype(np.int64) & 255
        zi = zi.astype(np.int64) & 255
        u = xf * xf * (3 - 2 * xf)
        v = yf * yf * (3 - 2 * yf)
        w = zf * zf * (3 - 2 * zf)
        p, vals = self.perm, self.vals

        def h(i, j, k):
            return vals[p[p[p[i] + j] + k] & 255]

        x1, y1, z1 = (xi + 1) & 255, (yi + 1) & 255, (zi + 1) & 255
        c000, c100 = h(xi, yi, zi), h(x1, yi, zi)
        c010, c110 = h(xi, y1, zi), h(x1, y1, zi)
        c001, c101 = h(xi, yi, z1), h(x1, yi, z1)
        c011, c111 = h(xi, y1, z1), h(x1, y1, z1)
        a = c000 + (c100 - c000) * u
        b = c010 + (c110 - c010) * u
        c = c001 + (c101 - c001) * u
        d = c011 + (c111 - c011) * u
        e = a + (b - a) * v
        f = c + (d - c) * v
        return e + (f - e) * w

    def fbm(self, x, y, z, octaves=5, lac=2.0, gain=0.5):
        tot, amp, norm = 0.0, 1.0, 0.0
        for o in range(octaves):
            tot = tot + amp * self.v3(x + o * 17.3, y + o * 9.1, z + o * 3.7)
            norm += amp
            amp *= gain
            x, y, z = x * lac, y * lac, z * lac
        return tot / norm


def sphere_grid(tw, th):
    lon = (np.arange(tw) + 0.5) / tw * 2 * np.pi - np.pi
    lat = (0.5 - (np.arange(th) + 0.5) / th) * np.pi
    LON, LAT = np.meshgrid(lon.astype(np.float32), lat.astype(np.float32))
    px = np.cos(LAT) * np.cos(LON)
    py = np.cos(LAT) * np.sin(LON)
    pz = np.sin(LAT)
    return LAT, LON, px, py, pz


def lerp_col(a, b, t):
    a = np.array(a, np.float32) / 255
    b = np.array(b, np.float32) / 255
    t = np.clip(t, 0, 1)[..., None]
    return a + (b - a) * t


def ramp(t, stops):
    """stops: lista (pos, cor)"""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        if m.any():
            out[m] = lerp_col(c0, c1, (t[m] - p0) / max(1e-6, p1 - p0))
    return out


# ----------------------------------------------------------------- texturas
def tex_earth(tw=1536, th=768):
    n = Noise(3)
    LAT, LON, x, y, z = sphere_grid(tw, th)
    wx = n.fbm(x * 2 + 5, y * 2, z * 2, 3)
    c = n.fbm(x * 1.7 + wx * 1.2, y * 1.7 + wx, z * 1.7, 6)
    land = c > 0.53
    coast = np.clip((c - 0.45) / 0.08, 0, 1)
    ocean = lerp_col((6, 30, 95), (25, 95, 170), coast ** 2)
    veg = n.fbm(x * 5, y * 5, z * 5, 4)
    absl = np.abs(LAT) / (np.pi / 2)
    desert = np.clip(1 - np.abs(absl - 0.3) / 0.13, 0, 1) * np.clip((veg - 0.35) * 3, 0, 1)
    landc = lerp_col((40, 105, 45), (95, 120, 55), veg)
    landc = landc * (1 - desert[..., None]) + lerp_col((185, 155, 95), (205, 175, 115), veg) * desert[..., None]
    mount = np.clip((c - 0.62) * 6, 0, 1)[..., None]
    landc = landc * (1 - mount * 0.5) + np.array([0.55, 0.5, 0.45], np.float32) * mount * 0.5
    col = np.where(land[..., None], landc, ocean)
    ice = np.clip((absl - 0.80) / 0.05 + (n.fbm(x * 6, y * 6, z * 6, 3) - 0.5) * 2, 0, 1)[..., None]
    col = col * (1 - ice) + 0.95 * ice
    oc = (~land).astype(np.float32) * (1 - ice[..., 0])
    # nuvens
    cw = n.fbm(x * 3 + 11, y * 3, z * 3, 3)
    cl = n.fbm(x * 3.2 + cw * 2, y * 3.2, z * 6.0 + cw, 6)
    clouds = np.clip((cl - 0.50) * 3.2, 0, 1) * (0.55 + 0.45 * np.clip(1 - np.abs(absl - 0.55) * 1.4, 0, 1))
    return col.astype(np.float32), oc.astype(np.float32), clouds.astype(np.float32)


def tex_jupiter(tw=1536, th=768):
    n = Noise(7)
    LAT, LON, x, y, z = sphere_grid(tw, th)
    turb = n.fbm(x * 4, y * 4, z * 1.5, 5)
    t2 = n.fbm(x * 14, y * 14, z * 5, 4)
    lat = LAT / (np.pi / 2) + (turb - 0.5) * 0.10 + (t2 - 0.5) * 0.025
    band = 0.5 + 0.5 * np.sin(lat * 13.0 + np.sin(lat * 5) * 1.5)
    band2 = 0.5 + 0.5 * np.sin(lat * 31.0 + 1.0)
    tt = np.clip(band * 0.75 + band2 * 0.25, 0, 1)
    col = ramp(tt, [(0, (150, 95, 60)), (0.35, (196, 150, 105)), (0.65, (226, 205, 170)), (1, (245, 236, 218))])
    pole = np.clip((np.abs(LAT) / (np.pi / 2) - 0.7) / 0.3, 0, 1)[..., None]
    col = col * (1 - pole * 0.45) + np.array([0.55, 0.5, 0.5], np.float32) * pole * 0.45
    # Grande Mancha Vermelha
    lat0, lon0 = -22 * np.pi / 180, 0.6
    dlon = np.angle(np.exp(1j * (LON - lon0))).astype(np.float32)
    e = np.sqrt((dlon / 0.30) ** 2 + ((LAT - lat0) / 0.11) ** 2)
    swirl = n.fbm(dlon * 9, (LAT - lat0) * 9, e * 3, 3)
    spot = np.clip(1.15 - e - (swirl - 0.5) * 0.3, 0, 1)
    spot_c = lerp_col((170, 70, 45), (215, 110, 70), np.clip(e * 1.2 + (swirl - 0.5), 0, 1))
    ring = np.clip(1 - np.abs(e - 1.05) / 0.12, 0, 1)[..., None]
    col = col * (1 - ring * 0.35) + np.array([0.95, 0.9, 0.82], np.float32) * ring * 0.35
    s = np.clip(spot * 1.8, 0, 1)[..., None]
    col = col * (1 - s) + spot_c * s
    return col.astype(np.float32)


def tex_saturn(tw=1024, th=512):
    n = Noise(11)
    LAT, LON, x, y, z = sphere_grid(tw, th)
    turb = n.fbm(x * 4, y * 4, z * 1.5, 4)
    lat = LAT / (np.pi / 2) + (turb - 0.5) * 0.05
    tt = 0.5 + 0.35 * np.sin(lat * 11) + 0.15 * np.sin(lat * 27 + 2)
    col = ramp(tt, [(0, (176, 140, 85)), (0.5, (222, 192, 135)), (1, (240, 222, 175))])
    pole = np.clip((np.abs(LAT) / (np.pi / 2) - 0.75) / 0.25, 0, 1)[..., None]
    col = col * (1 - pole * 0.4) + np.array([0.55, 0.6, 0.55], np.float32) * pole * 0.4
    return col.astype(np.float32)


def tex_simple(kind, tw=768, th=384):
    LAT, LON, x, y, z = sphere_grid(tw, th)
    absl = np.abs(LAT) / (np.pi / 2)
    if kind == "MERCÚRIO":
        n = Noise(21)
        b = n.fbm(x * 4, y * 4, z * 4, 6)
        col = lerp_col((95, 90, 86), (175, 168, 160), b)
        rng = np.random.default_rng(5)
        for _ in range(90):
            v = rng.normal(size=3); v /= np.linalg.norm(v)
            rad = rng.uniform(0.03, 0.18) ** 1.4 * 1.2
            d = np.arccos(np.clip(x * v[0] + y * v[1] + z * v[2], -1, 1))
            inner = np.clip(1 - d / rad, 0, 1)
            rim = np.clip(1 - np.abs(d - rad) / (rad * 0.18), 0, 1)
            col = col * (1 - 0.25 * (inner > 0)[..., None] * (0.6 + 0.4 * inner[..., None])) + 0.22 * rim[..., None]
        return np.clip(col, 0, 1).astype(np.float32)
    if kind == "MARTE":
        n = Noise(31)
        b = n.fbm(x * 3, y * 3, z * 3, 6)
        col = ramp(b, [(0, (110, 50, 30)), (0.45, (170, 80, 45)), (0.6, (205, 115, 65)), (1, (225, 150, 100))])
        cap = np.clip((absl - 0.86) / 0.04, 0, 1)[..., None]
        return (col * (1 - cap) + 0.95 * cap).astype(np.float32)
    if kind == "VÊNUS":
        n = Noise(41)
        w = n.fbm(x * 2, y * 2, z * 2, 3)
        b = n.fbm(x * 2.5 + w * 2, y * 2.5, z * 5 + w, 5)
        return ramp(b, [(0, (190, 150, 90)), (0.5, (228, 200, 145)), (1, (250, 235, 200))]).astype(np.float32)
    if kind == "NETUNO":
        n = Noise(51)
        t = n.fbm(x * 3, y * 3, z * 1.5, 4)
        lat = LAT / (np.pi / 2) + (t - 0.5) * 0.08
        tt = 0.5 + 0.3 * np.sin(lat * 9) + 0.2 * (t - 0.5)
        col = ramp(tt, [(0, (25, 55, 160)), (0.5, (45, 95, 210)), (1, (90, 140, 235))])
        lat0, lon0 = -20 * np.pi / 180, 1.4
        dlon = np.angle(np.exp(1j * (LON - lon0))).astype(np.float32)
        e = np.sqrt((dlon / 0.22) ** 2 + ((LAT - lat0) / 0.09) ** 2)
        col = col * (1 - 0.55 * np.clip(1.1 - e, 0, 1)[..., None])
        st = np.clip((n.fbm(x * 8, y * 8, z * 30, 3) - 0.62) * 5, 0, 1) * np.clip(1 - np.abs(LAT + 0.5) * 3, 0, 1)
        col = col * (1 - st[..., None]) + 0.95 * st[..., None]
        return col.astype(np.float32)
    if kind == "URANO":
        n = Noise(61)
        t = n.fbm(x * 3, y * 3, z * 1.5, 3)
        lat = LAT / (np.pi / 2)
        tt = 0.5 + 0.15 * np.sin(lat * 8 + t) + 0.1 * (t - 0.5)
        return ramp(tt, [(0, (120, 190, 205)), (1, (185, 232, 238))]).astype(np.float32)
    raise ValueError(kind)


def tex_sun(tw=2048, th=1024):
    n = Noise(77)
    LAT, LON, x, y, z = sphere_grid(tw, th)
    g = n.fbm(x * 70, y * 70, z * 70, 3)
    g2 = n.fbm(x * 9, y * 9, z * 9, 4)
    cells = 1 - np.abs(g - 0.5) * 2
    v = np.clip(0.55 * cells ** 2 + 0.45 * g2, 0, 1)
    col = ramp(v, [(0, (230, 95, 10)), (0.5, (255, 165, 35)), (0.8, (255, 215, 90)), (1, (255, 245, 170))])
    rng = np.random.default_rng(3)
    for _ in range(4):
        la, lo = rng.uniform(-0.5, 0.5), rng.uniform(-np.pi, np.pi)
        dlon = np.angle(np.exp(1j * (LON - lo))).astype(np.float32)
        d = np.sqrt((dlon * np.cos(la)) ** 2 + (LAT - la) ** 2)
        r = rng.uniform(0.02, 0.045)
        um = np.clip(1 - d / r, 0, 1)
        pen = np.clip(1 - d / (r * 2.2), 0, 1)
        col = col * (1 - 0.45 * pen[..., None]) * (1 - 0.5 * um[..., None])
    return col.astype(np.float32)


def load_textures():
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, "tex_v3.npz")
    if os.path.exists(f):
        d = np.load(f)
        return {k: d[k] for k in d.files}
    print("gerando texturas...", flush=True)
    t = {}
    t["TERRA"], t["TERRA_oc"], t["TERRA_cl"] = tex_earth()
    t["JÚPITER"] = tex_jupiter()
    t["SATURNO"] = tex_saturn()
    for k in ["MERCÚRIO", "MARTE", "VÊNUS", "NETUNO", "URANO"]:
        t[k] = tex_simple(k)
    t["SOL"] = tex_sun()
    np.savez(f, **t)
    return t


TEX = None
ATM = {"TERRA": ((0.35, 0.65, 1.0), 0.55, 0.10), "VÊNUS": ((1.0, 0.9, 0.65), 0.35, 0.07),
       "NETUNO": ((0.45, 0.65, 1.0), 0.45, 0.07), "URANO": ((0.6, 0.95, 1.0), 0.40, 0.07),
       "JÚPITER": ((1.0, 0.9, 0.75), 0.18, 0.04), "SATURNO": ((1.0, 0.92, 0.7), 0.18, 0.04),
       "MARTE": ((1.0, 0.65, 0.45), 0.18, 0.04), "MERCÚRIO": ((0.8, 0.8, 0.8), 0.05, 0.02)}
ROT_SPEED = {"TERRA": 1 / 25.0, "MERCÚRIO": 0.004, "MARTE": 0.01, "VÊNUS": 0.004, "NETUNO": 0.016,
             "URANO": 0.014, "SATURNO": 0.02, "JÚPITER": 0.022, "SOL": 0.004}
TILT = {"TERRA": 0.30, "URANO": 0.25, "SATURNO": -0.18, "NETUNO": 0.12, "MARTE": 0.25}
LIGHT = np.array([0.55, 0.42, 0.72], np.float32)
LIGHT /= np.linalg.norm(LIGHT)


def sample(tex, u, v):
    th, tw = tex.shape[:2]
    fu = u * tw - 0.5
    fv = np.clip(v * th - 0.5, 0, th - 1.001)
    i0 = np.floor(fu).astype(np.int64)
    j0 = np.floor(fv).astype(np.int64)
    du = (fu - i0)[..., None] if tex.ndim == 3 else fu - i0
    dv = (fv - j0)[..., None] if tex.ndim == 3 else fv - j0
    i0 %= tw
    i1 = (i0 + 1) % tw
    j1 = np.minimum(j0 + 1, th - 1)
    a = tex[j0, i0] * (1 - du) + tex[j0, i1] * du
    b = tex[j1, i0] * (1 - du) + tex[j1, i1] * du
    return a * (1 - dv) + b * dv


def bbox(cx, cy, r):
    x0, x1 = int(max(0, math.floor(cx - r))), int(min(W, math.ceil(cx + r + 1)))
    y0, y1 = int(max(0, math.floor(cy - r))), int(min(H, math.ceil(cy + r + 1)))
    return x0, x1, y0, y1


def draw_ring(canvas, cx, cy, R, part):
    a = R * RING_OUT
    x0, x1, y0, y1 = bbox(cx, cy, a + 2)
    if x0 >= x1 or y0 >= y1:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xs - cx, ys - cy
    ang = TILT["SATURNO"]
    ca, sa = math.cos(ang), math.sin(ang)
    rx = dx * ca + dy * sa
    ry = -dx * sa + dy * ca
    ratio = 0.30
    rr = np.sqrt(rx ** 2 + (ry / ratio) ** 2) / max(R, 1e-3)
    front = ry > 0
    m = front if part == "front" else ~front
    op = np.zeros_like(rr)
    op += 0.25 * ((rr > 1.24) & (rr < 1.53))
    op += 0.85 * ((rr >= 1.53) & (rr < 1.95))
    op += 0.65 * ((rr >= 2.03) & (rr < RING_OUT))
    op *= 1 - 0.8 * ((rr > 2.20) & (rr < 2.23))
    op *= 0.85 + 0.15 * np.sin(rr * 90)
    edge = np.clip((RING_OUT - rr) * R + 0.5, 0, 1) * np.clip((rr - 1.24) * R + 0.5, 0, 1)
    op = op * edge * m
    col = lerp_col((150, 125, 90), (235, 215, 170), np.clip((rr - 1.2) / 1.0, 0, 1))
    # sombra do planeta no anel (lado oposto à luz, atrás)
    sh = np.clip(((rx + R * 0.35) ** 2 + (ry / 1.0) ** 2) ** 0.5 / R - 0.0, 0, 1)
    shadow = ((~front) & (rx < 0) & (np.abs(ry) < R) & (rr < 1.0 / ratio)).astype(np.float32)
    col = col * (1 - 0.0 * shadow[..., None])
    a3 = op[..., None]
    reg = canvas[y0:y1, x0:x1]
    reg[:] = reg * (1 - a3) + col * a3


def draw_body(canvas, name, cx, cy, R, t, scale=1.0):
    R = R * scale
    if R <= 0.05:
        return
    if name == "SATURNO":
        draw_ring(canvas, cx, cy, R, "back")
    atm = ATM.get(name)
    halo_h = atm[2] if atm else 0.0
    ext = R * (1 + halo_h) + 2 if name != "SOL" else R * 2.6
    x0, x1, y0, y1 = bbox(cx, cy, ext)
    if x0 < x1 and y0 < y1:
        ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        X = (xs + 0.5 - cx) / R
        Y = (ys + 0.5 - cy) / R
        d2 = X * X + Y * Y
        d = np.sqrt(d2)
        reg = canvas[y0:y1, x0:x1]
        inside = d < 1 + 1.5 / R
        if name == "SOL":
            # brilho/corona aditivo
            dd = np.maximum(d - 1, 0)
            pulse = 1 + 0.06 * math.sin(t * 2.3)
            glow = (0.85 * np.exp(-dd * 7) + 0.45 * np.exp(-dd * 2.2)) * pulse
            glow *= (d > 0.98)
            reg += glow[..., None] * np.array([1.0, 0.62, 0.18], np.float32)
        if inside.any():
            iy, ix = np.nonzero(inside)
            Xi, Yi = X[iy, ix], Y[iy, ix]
            Zi = np.sqrt(np.clip(1 - Xi * Xi - Yi * Yi, 0, 1))
            alpha = np.clip((1 - d[iy, ix]) * R + 0.5, 0, 1)
            tilt = TILT.get(name, 0.0)
            ct, st = math.cos(tilt), math.sin(tilt)
            bx = Xi * ct + Yi * st
            by = -(-Xi * st + Yi * ct)
            lat = np.arcsin(np.clip(by, -1, 1))
            lon = np.arctan2(bx, np.maximum(Zi, 1e-4) * np.sqrt(np.maximum(1 - by * by, 1e-6)) / np.sqrt(np.maximum(1 - by * by, 1e-6)))
            lon = np.arctan2(bx, Zi)
            u = (lon / (2 * np.pi) + 0.5 + t * ROT_SPEED[name]) % 1.0
            v = 0.5 - lat / np.pi
            col = sample(TEX[name], u, v)
            ndl = Xi * LIGHT[0] + (-Yi) * LIGHT[1] + Zi * LIGHT[2]
            if name == "SOL":
                limb = 0.42 + 0.58 * Zi ** 0.55
                warm = np.stack([np.ones_like(Zi), 0.75 + 0.25 * Zi, 0.55 + 0.45 * Zi], -1)
                boil = 1 + 0.05 * np.sin(t * 5 + Xi * 40 + Yi * 31) * np.sin(t * 3.1 + Yi * 47)
                col = col * limb[..., None] * warm * boil[..., None] * 1.12
            else:
                if name == "TERRA":
                    oc = sample(TEX["TERRA_oc"], u, v)
                    cl = sample(TEX["TERRA_cl"], (u + t / 25.0) % 1.0, v)
                    hx, hy, hz = LIGHT[0], LIGHT[1], LIGHT[2] + 1
                    hn = math.sqrt(hx * hx + hy * hy + hz * hz)
                    ndh = np.clip((Xi * hx - Yi * hy + Zi * hz) / hn, 0, 1)
                    spec = oc * ndh ** 80 * 0.35
                    col = col * (1 - cl[..., None]) + cl[..., None] * 0.97
                    col = col + spec[..., None] * (1 - cl[..., None])
                diff = np.clip(ndl, 0, 1) ** 0.85
                term = np.clip((ndl + 0.12) / 0.24, 0, 1)
                shade = 0.035 + 0.965 * diff * (0.6 + 0.4 * term)
                col = col * shade[..., None]
                if atm:
                    ac = np.array(atm[0], np.float32)
                    rim = (1 - Zi) ** 2.5 * atm[1] * np.clip(ndl + 0.35, 0, 1)
                    col = col + rim[..., None] * ac
            col = np.clip(col, 0, 3)
            a3 = alpha[..., None]
            reg[iy, ix] = reg[iy, ix] * (1 - a3) + col * a3
        if atm and name != "SOL" and halo_h > 0:
            out = (d >= 1) & (d < 1 + halo_h)
            if out.any():
                oy, ox = np.nonzero(out)
                k = 1 - (d[oy, ox] - 1) / halo_h
                lit = np.clip(0.25 + 0.9 * (X[oy, ox] * LIGHT[0] - Y[oy, ox] * LIGHT[1]) / np.maximum(d[oy, ox], 1e-3), 0, 1)
                hcol = np.array(atm[0], np.float32) * (k ** 2.2 * atm[1] * 1.3 * lit)[..., None]
                reg[oy, ox] += hcol
    if name == "SATURNO":
        draw_ring(canvas, cx, cy, R, "front")


# ----------------------------------------------------------------- fundo
BG = None
VIGNETTE = None
TWINKLE = None
BGW, BGH = 1500, 2600


def make_background():
    f = os.path.join(CACHE, "bg_v2.npy")
    if os.path.exists(f):
        return np.load(f)
    print("gerando fundo...", flush=True)
    n = Noise(99)
    ys, xs = np.mgrid[0:BGH, 0:BGW].astype(np.float32)
    x, y = xs / 520, ys / 520
    w = n.fbm(x, y, 0.5, 4)
    a = n.fbm(x * 1.2 + w * 1.5, y * 1.2 + w, 2.0, 6)
    b = n.fbm(x * 0.9 + 4, y * 0.9 - w, 5.0, 6)
    base = np.array([5, 9, 28], np.float32) / 255
    img = np.ones((BGH, BGW, 3), np.float32) * base
    neb1 = np.clip((a - 0.45) * 2.2, 0, 1) ** 1.6
    neb2 = np.clip((b - 0.5) * 2.4, 0, 1) ** 1.6
    img += neb1[..., None] * np.array([0.30, 0.10, 0.42], np.float32) * 0.55
    img += neb2[..., None] * np.array([0.05, 0.28, 0.45], np.float32) * 0.5
    dust = np.clip((n.fbm(x * 4, y * 4, 9.0, 4) - 0.5) * 3, 0, 1)
    img *= (1 - 0.35 * dust[..., None])
    rng = np.random.default_rng(1)
    N = 5200
    sx, sy = rng.uniform(0, BGW, N), rng.uniform(0, BGH, N)
    br = rng.uniform(0.15, 0.9, N) ** 2.2
    tint = rng.choice([0, 1, 2], N, p=[0.7, 0.18, 0.12])
    cols = np.array([[1, 1, 1], [0.75, 0.85, 1], [1, 0.9, 0.7]], np.float32)
    ix, iy = sx.astype(int), sy.astype(int)
    np.add.at(img, (iy, ix), cols[tint] * br[:, None])
    img = np.clip(img, 0, 1)
    np.save(f, img)
    return img


def make_vignette():
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xs - W / 2) / (W / 2)
    dy = (ys - H / 2) / (H / 2)
    r = np.sqrt(dx * dx * 0.8 + dy * dy * 0.9)
    return np.clip(1 - 0.55 * np.clip(r - 0.55, 0, 1) ** 1.4, 0, 1).astype(np.float32)[..., None]


def make_twinkle():
    rng = np.random.default_rng(8)
    N = 140
    return dict(x=rng.uniform(0, BGW, N), y=rng.uniform(0, BGH, N), ph=rng.uniform(0, 6.28, N),
                fr=rng.integers(6, 20, N) * 2 * np.pi / DUR, b=rng.uniform(0.5, 1.0, N), sz=rng.choice([1, 1, 2, 2, 3], N))


def background(t, s):
    # zoom-out lento do fundo (paralaxe) + deriva
    s0 = KEYS[0][1]
    z = clamp(math.log(s0 / s) / math.log(s0 / 0.0004), 0, 1.2)
    scale = 1.0 - 0.16 * z
    cw, ch = W / scale * 1.0, H / scale * 1.0
    cw, ch = min(cw, BGW), min(ch, BGH)
    ox = (BGW - cw) / 2 + 60 * math.sin(2 * math.pi * t / DUR)
    oy = (BGH - ch) / 2 + 40 * math.cos(2 * math.pi * t / DUR)
    box = (ox, oy, ox + cw, oy + ch)
    return box


def render_bg(t, s):
    global BG_IMG
    box = background(t, s)
    img = BG_IMG.resize((W, H), Image.BILINEAR, box=box)
    arr = np.asarray(img, np.float32) / 255.0
    arr = arr.copy()
    # estrelas cintilantes
    sx = W / (box[2] - box[0])
    tw = TWINKLE
    px = (tw["x"] - box[0]) * sx
    py = (tw["y"] - box[1]) * sx
    br = tw["b"] * (0.35 + 0.65 * (0.5 + 0.5 * np.sin(t * tw["fr"] + tw["ph"]))) ** 2
    for i in range(len(px)):
        x, y = int(px[i]), int(py[i])
        if 3 <= x < W - 3 and 3 <= y < H - 3:
            b = br[i]
            sz = tw["sz"][i]
            arr[y, x] += b
            if sz >= 2:
                arr[y, x - 1:x + 2] += b * 0.45
                arr[y - 1:y + 2, x] += b * 0.45
            if sz >= 3:
                arr[y, x - 3:x + 4] += b * 0.18
                arr[y - 3:y + 4, x] += b * 0.18
    return arr


# ----------------------------------------------------------------- texto
FONT_DIR = os.path.join(HERE, "fonts")
_fc = {}


def font(kind, size):
    k = (kind, size)
    if k not in _fc:
        if kind == "anton":
            f = ImageFont.truetype(os.path.join(FONT_DIR, "Anton-Regular.ttf"), size)
        else:
            f = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat.ttf"), size)
            f.set_variation_by_name("Black")
        _fc[k] = f
    return _fc[k]


_tc = {}


def rich_text(text, size, kind="mont", maxw=880, color=WHITE, hl=YEL, stroke=None, spacing=1.05):
    """'*palavra*' fica amarela. Retorna RGBA."""
    key = (text, size, kind, maxw, color, hl, stroke)
    if key in _tc:
        return _tc[key]
    f = font(kind, size)
    stroke = stroke if stroke is not None else max(4, size // 9)
    words = []
    on = False
    for wd in text.split(" "):
        st = wd.startswith("*")
        en = wd.endswith("*")
        if st:
            on = True
        words.append((wd.strip("*"), hl if on else color))
        if en:
            on = False
    space = f.getlength(" ")
    lines, cur, cw = [], [], 0
    for wd, c in words:
        wl = f.getlength(wd)
        if cur and cw + space + wl > maxw:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (space if cur else 0) + wl
        cur.append((wd, c, wl))
    if cur:
        lines.append((cur, cw))
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * spacing)
    tw = int(max(l[1] for l in lines) + stroke * 2 + 8)
    th = int(lh * len(lines) + stroke * 2 + 8)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for li, (ws, lw) in enumerate(lines):
        x = (tw - lw) / 2
        y = stroke + 4 + li * lh
        for wd, c, wl in ws:
            d.text((x, y), wd, font=f, fill=c, stroke_width=stroke, stroke_fill=(0, 0, 0))
            x += wl + space
    _tc[key] = img
    return img


def paste(frame, img, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.003 or scale <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BICUBIC)
    if rot:
        img = img.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy(); img.putalpha(a)
    frame.alpha_composite(img, (int(round(cx - img.width / 2)), int(round(cy - img.height / 2))))


def pop(t, a, dur=0.28):
    """escala de entrada com overshoot"""
    if t < a:
        return 0.0
    x = (t - a) / dur
    return 1.0 if x >= 1 else 0.55 + 0.45 * ease_out_back(x, 2.2)


def rounded_panel(w, h, fill, r=36, outline=None, ow=6):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=outline, width=ow if outline else 0)
    return img


def fmt_km(v):
    return f"{int(round(v)):,}".replace(",", ".") + " KM"


_card_cache = {}


def planet_card(name, km_val, label, count_u):
    """cartão: nome grande + km contando + selo 'Nx A TERRA'"""
    pw, ph = 820, 400
    km_txt = fmt_km(km_val * ease_out_cubic(count_u))
    key = (name, km_txt, label)
    if key in _card_cache:
        return _card_cache[key]
    img = rounded_panel(pw, ph, (8, 16, 46, 200), 40, outline=(255, 214, 60, 255), ow=5)
    nm = rich_text(name, 92, "mont", maxw=800)
    img.alpha_composite(nm, ((pw - nm.width) // 2, 8))
    km = rich_text(km_txt, 104, "anton", color=WHITE, stroke=8)
    img.alpha_composite(km, ((pw - km.width) // 2, 112))
    if label:
        f = font("mont", 50)
        txt = f"{label} A TERRA"
        tl = int(f.getlength(txt))
        bw, bh = tl + 60, 74
        badge = rounded_panel(bw, bh, YEL + (255,), 37)
        ImageDraw.Draw(badge).text((30, 8), txt, font=f, fill=NAVY)
        img.alpha_composite(badge, ((pw - bw) // 2, ph - bh - 24))
    if len(_card_cache) > 400:
        _card_cache.clear()
    _card_cache[key] = img
    return img


def arrow_img(length=170, color=YEL):
    w = 90
    img = Image.new("RGBA", (w + 20, length + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = (w + 20) / 2
    pts = [(cx - 14, 10), (cx + 14, 10), (cx + 14, length - 40), (cx + 40, length - 40),
           (cx, length + 8), (cx - 40, length - 40), (cx - 14, length - 40)]
    d.polygon(pts, fill=color, outline=(0, 0, 0))
    d.line(pts + [pts[0]], fill=(0, 0, 0), width=7, joint="curve")
    return img


def counter_img(n):
    key = ("cnt", n)
    if key in _tc:
        return _tc[key]
    a = rich_text("1x", 120, "anton", color=WHITE, stroke=9)
    b = rich_text(f"{n}x", 230, "anton", color=YEL, stroke=12)
    aw = 110
    arr = Image.new("RGBA", (aw, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(arr)
    p = [(4, 30), (60, 30), (60, 8), (104, 45), (60, 82), (60, 60), (4, 60)]
    d.polygon(p, fill=WHITE)
    d.line(p + [p[0]], fill=(0, 0, 0), width=6, joint="curve")
    bw = rich_text("109x", 230, "anton", stroke=12).width  # largura fixa
    tw = a.width + aw + 20 + bw
    th = max(a.height, b.height)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    img.alpha_composite(a, (0, th - a.height - 18))
    img.alpha_composite(arr, (a.width + 4, th - a.height + 8))
    img.alpha_composite(b, (a.width + aw + 20 + (bw - b.width) // 2, 0))
    _tc[key] = img
    return img


# ----------------------------------------------------------------- linha do tempo
NEIGHBOR_POP = {"VÊNUS": 1.70, "MARTE": 1.85, "MERCÚRIO": 2.00}
CARDS = [("NETUNO", 4.9, 6.35), ("URANO", 6.9, 8.35), ("SATURNO", 8.9, 10.35), ("JÚPITER", 10.9, 12.35)]
T_SUN = 15.4
T_ARROW = 17.6
T_FINAL = 19.8
T_Q = 22.4
T_LOOP = 24.0


def neighbor_scale(name, t):
    a = NEIGHBOR_POP[name]
    if t < a:
        return 0.0
    if t > T_LOOP + 0.15:   # encolhem durante o loop para o frame 0 bater
        return 1 - smoother((t - T_LOOP - 0.15) / 0.55)
    x = (t - a) / 0.35
    return 1.0 if x >= 1 else max(0.0, ease_out_back(x, 2.0))


def world_layer(t):
    s, xc, B = camera(t)
    canvas = render_bg(t, s)
    shx, shy = shake(t)
    # Sol primeiro (está atrás de tudo à direita), depois os demais
    order = [IDX["SOL"]] + [i for i in range(len(PLANETS)) if PLANETS[i][0] != "SOL"]
    pos = {}
    for i in order:
        name, d, _ = PLANETS[i]
        R = d / 2 * s
        cx = CX + (XS[i] - xc) * s + shx
        cy = B - R + shy
        pos[name] = (cx, cy, R)
        ext = R * (RING_OUT if name == "SATURNO" else (2.6 if name == "SOL" else 1.2))
        if cx + ext < 0 or cx - ext > W or cy + ext < 0 or cy - ext > H:
            continue
        sc = neighbor_scale(name, t) if name in NEIGHBOR_POP else 1.0
        if sc <= 0:
            continue
        if sc != 1.0:  # escala ancorada na base
            cy = B - R * sc + shy
        draw_body(canvas, name, cx, cy, R, t, sc)
    canvas *= VIGNETTE
    # flash branco na revelação
    fl = 0.0
    if T_SUN - 0.04 <= t < T_SUN + 0.5:
        fl = 1.0 if t < T_SUN + 0.06 else 1 - smoother((t - T_SUN - 0.06) / 0.44)
    if fl > 0:
        canvas = canvas * (1 - fl) + fl
    return np.clip(canvas, 0, 1), pos


def ui_layer(frame, t, pos):
    # textos do topo
    TOP_Y = 250
    def top(text, a, b, size=84, grow=0.0, keep0=False):
        if not (a <= t < b):
            return
        sc = 1.0 if keep0 and t < a + 1e-6 else pop(t, a)
        if keep0:
            sc = 1.0
        al = clamp((b - t) / 0.12)
        sc *= 1 + grow * (t - a)
        img = rich_text(text, size, maxw=860)
        paste(frame, img, CX, TOP_Y, sc, al)

    # gancho: totalmente visível já no frame 0 (e volta no fim do loop)
    if t < 1.7:
        sc = 1 + 0.03 * math.sin(t * 5)
        paste(frame, rich_text("A TERRA PARECE *GRANDE?*", 92, maxw=860), CX, TOP_Y, sc, clamp((1.7 - t) / 0.12))
    if t >= T_LOOP + 0.55:
        u = (t - T_LOOP - 0.55) / 0.42
        sc = (0.55 + 0.45 * ease_out_back(clamp(u), 2.0)) if u < 1 else 1.0
        paste(frame, rich_text("A TERRA PARECE *GRANDE?*", 92, maxw=860), CX, TOP_Y, sc * 1.0, clamp(u * 3))
    top("PERTO DOS VIZINHOS, *ATÉ QUE SIM...*", 1.75, 3.85)
    top("MAS AÍ CHEGAM OS *GIGANTES*", 3.9, 12.35, size=88)
    top("AGORA OLHA O *SOL...*", 12.4, T_SUN - 0.03, size=96, grow=0.05)

    # nomes pequenos dos vizinhos (abaixo da base)
    if 2.1 <= t < 4.1:
        for k, nm in enumerate(["MERCÚRIO", "MARTE", "VÊNUS", "TERRA"]):
            cx, cy, R = pos[nm]
            a = win(t, NEIGHBOR_POP.get(nm, 1.9) + 0.3, 4.1, 0.2, 0.2)
            img = rich_text(nm, 38, maxw=400)
            paste(frame, img, cx, cy + R + 42 + (k % 2 == 0) * 52 * (k < 2), 1.0, a)

    # cartões dos gigantes
    for nm, a, b in CARDS:
        if a <= t < b:
            i = IDX[nm]
            u = (t - a) / 0.9
            card = planet_card(nm, PLANETS[i][1], PLANETS[i][2], u)
            e = ease_out_back(clamp((t - a) / 0.3), 1.6)
            al = min(clamp((t - a) / 0.15), clamp((b - t) / 0.18))
            paste(frame, card, CX, 1330 + (1 - e) * 120, 0.9 + 0.1 * e, al)

    # contador do Sol
    if T_SUN <= t < T_FINAL + 0.2:
        u = clamp((t - T_SUN - 0.1) / 1.5)
        n = 1 + int(round(108 * (1 - (1 - u) ** 2.2)))
        img = counter_img(n)
        sc = pop(t, T_SUN, 0.3) * (1 + 0.05 * math.sin((t - T_SUN) * 7) * (u >= 1))
        al = clamp((T_FINAL + 0.2 - t) / 0.2)
        paste(frame, img, CX, 330, sc * 0.95, al)
        sub = rich_text("MAIOR QUE A *TERRA*", 70, maxw=860)
        paste(frame, sub, CX, 500, pop(t, T_SUN + 0.25), al)

    # seta VOCÊ ESTÁ AQUI
    if T_ARROW <= t < T_FINAL + 0.25:
        ex, ey, er = pos["TERRA"]
        al = clamp((T_FINAL + 0.25 - t) / 0.25)
        bob = 10 * math.sin((t - T_ARROW) * 7)
        sc = pop(t, T_ARROW, 0.3)
        ar = arrow_img(230)
        paste(frame, ar, ex, ey - er - 16 - ar.height / 2 + bob, sc, al)
        lab = rich_text("*VOCÊ ESTÁ AQUI*", 74, maxw=700)
        lx = clamp(ex + 120, lab.width / 2 + 30, SAFE_R - lab.width / 2 - 10)
        paste(frame, lab, lx, ey - er - 320 + bob * 0.5, sc, al)
        # anel pulsante na Terra
        d = ImageDraw.Draw(frame)
        rr = er + 14 + 10 * ((t - T_ARROW) * 1.6 % 1)
        aa = int(255 * al * (1 - ((t - T_ARROW) * 1.6 % 1)))
        d.ellipse((ex - rr, ey - rr, ex + rr, ey + rr), outline=(255, 214, 60, aa), width=5)

    # cartão final
    if T_FINAL <= t < T_LOOP + 0.2:
        al = min(clamp((t - T_FINAL) / 0.2), clamp((T_LOOP + 0.2 - t) / 0.2))
        e = ease_out_back(clamp((t - T_FINAL) / 0.35), 1.5)
        breathe = 1 + 0.015 * math.sin((t - T_FINAL) * 4)
        panel = _final_panel()
        paste(frame, panel, CX, 740, (0.85 + 0.15 * e) * breathe, al)
        if t >= T_Q:
            q = rich_text("QUAL A PRÓXIMA *COMPARAÇÃO?*", 70, maxw=820)
            paste(frame, q, CX, 1215, pop(t, T_Q) * (1 + 0.02 * math.sin(t * 6)), al)


_fp = None


def _final_panel():
    global _fp
    if _fp is None:
        a = rich_text("DENTRO DELE CABEM", 64, maxw=820)
        b = rich_text("1,3 MILHÃO", 190, "anton", color=YEL, stroke=12)
        c = rich_text("DE TERRAS", 92, maxw=820)
        pw, ph = 860, 40 + a.height + b.height + c.height + 10
        img = rounded_panel(pw, ph, (8, 16, 46, 215), 44, outline=(255, 214, 60, 255), ow=6)
        y = 24
        for im in (a, b, c):
            img.alpha_composite(im, ((pw - im.width) // 2, y))
            y += im.height
        _fp = img
    return _fp


def init():
    global TEX, BG_IMG, VIGNETTE, TWINKLE
    TEX = load_textures()
    bg = make_background()
    BG_IMG = Image.fromarray((bg * 255).astype(np.uint8))
    VIGNETTE = make_vignette()
    TWINKLE = make_twinkle()


def render_frame(f):
    t = f / FPS
    canvas, pos = world_layer(t)
    img = Image.fromarray((canvas * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    ui_layer(img, t, pos)
    return img.convert("RGB")


def render_range(args):
    a, b, path = args
    init()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                          "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", path],
                         stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(render_frame(f).tobytes())
        if f % 30 == 0:
            print(f"frame {f}", flush=True)
    p.stdin.close()
    p.wait()
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "preview":
        init()
        pd = os.path.join(OUT, os.environ.get("PDIR", "preview"))
        os.makedirs(pd, exist_ok=True)
        for ts in sys.argv[2:]:
            f = int(round(float(ts) * FPS))
            im = render_frame(f)
            # guias da área segura
            if os.environ.get("GUIDES"):
                d = ImageDraw.Draw(im)
                d.line((SAFE_R, 0, SAFE_R, H), fill=(255, 0, 0), width=2)
                d.line((0, SAFE_B, W, SAFE_B), fill=(255, 0, 0), width=2)
            im.save(os.path.join(pd, f"f{f:04d}.png"))
            print("ok", f)
    elif cmd == "video":
        from multiprocessing import Pool
        init()  # gera caches uma vez
        nw = int(os.environ.get("WORKERS", os.cpu_count() or 4))
        step = math.ceil(NFRAMES / nw)
        jobs = [(i, min(NFRAMES, i + step), os.path.join(OUT, f"seg{k}.mp4")) for k, i in enumerate(range(0, NFRAMES, step))]
        with Pool(len(jobs)) as pool:
            segs = pool.map(render_range, jobs)
        lst = os.path.join(OUT, "segs.txt")
        open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                        os.path.join(OUT, "video_mudo.mp4")], check=True)
        print("video ok")


if __name__ == "__main__":
    main()
