"""PERA, OI? — SE A HISTÓRIA DA TERRA FOSSE UM DIA DE 24 HORAS (v2)
1080x1920, 30 fps, ~58,5 s. Abre no fim (23:59:54), rebobina 4,5 bilhões de anos e volta ao mesmo frame = loop.
A Terra 3D muda junto com o relógio (lava -> Lua -> oceanos -> oxigênio -> continentes -> plantas -> asteroide -> cidades).

  python render.py times | preview 0 5.2 ... | video
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "planetas"))
import engine as E   # textos, fontes, easing, ruído
from engine import (W, H, FPS, clamp, smoother, ease_out_cubic, ease_out_back, rich_text, paste, pop,
                    rounded_panel, font, Noise, sample, sphere_grid, ramp)
import plan as PL

OUT = os.path.join(HERE, "out")
os.environ.setdefault("NARR", os.path.join(OUT, "narr"))
P = PL.load()
S, EN = P["S"], P["E"]
DUR, NFRAMES, T_LOOP = P["DUR"], P["NFRAMES"], P["T_LOOP"]

CX = W / 2               # tudo centrado no meio real da tela
MAXW = 840               # texto cabe em 120..960 (fora da faixa da direita)
NAVY = (10, 14, 38)
YEL = (255, 214, 60)
CYAN = (60, 210, 255)
WHITE = (255, 255, 255)
DAY = 86400.0


def PF(w):
    """frequência arredondada para ciclos inteiros em DUR (loop perfeito)"""
    return 2 * math.pi * max(1, round(w * DUR / (2 * math.pi))) / DUR


def osc(t, w, ph=0.0):
    return math.sin(t * PF(w) + ph)


def word_t(line, frag, which="t"):
    frag = frag.lower()
    for w in P["words"]:
        if w["line"] == line and frag in w["w"].lower():
            return w["t"] + (w["d"] if which == "end" else 0.0)
    return (S[line] + EN[line]) / 2


def hms(h, m, s=0.0):
    return h * 3600 + m * 60 + s


# ---------------------------------------------------------------- momentos
T_RW_A, T_RW_B = S["rewind"] + 0.15, S["lava"] - 0.05        # rebobinar
T_THEIA = word_t("lua", "bate") + 0.15
T_VIDA = S["vida"] + 0.05
T_OXI = word_t("oxigenio", "meio")
T_ANI = S["animais"] + 0.05
T_PLANT = S["plantas"] + 0.05
T_DINO = S["dinos"] + 0.05
T_REIGN = word_t("dinos", "reinam")
T_BOOM = EN["asteroide"] + 0.25
T_SLOW = T_BOOM + 0.9
T_SAP = word_t("sapiens", "últimos")
T_PIR = S["historia"] + 0.05
T_ROMA = word_t("historia", "roma")
T_NET = word_t("historia", "internet")
T_DEC = word_t("historia", "décimo") + 0.25
T_CARD = S["suavida"]
T_YOU = word_t("suavida", "milésimo")
T_CTA = S["cta"]

C0 = hms(23, 59, 54)
CKEYS = [  # (tempo do vídeo, relógio, modo)
    (0.0, C0, None),
    (T_RW_A, hms(23, 59, 57.6), "lin"),
    (T_RW_B, 0.0, "rew"),
    (T_THEIA, hms(0, 9, 30), "soft"),
    (T_VIDA, hms(3, 55), "soft"),
    (EN["so"] - 0.2, hms(10, 35), "soft"),
    (T_OXI + 0.1, hms(11, 19), "soft"),
    (T_ANI, hms(21, 9), "soft"),
    (T_PLANT, hms(21, 31), "soft"),
    (T_DINO, hms(22, 47), "soft"),
    (EN["dinos"], hms(23, 33), "soft"),
    (T_BOOM, hms(23, 39), "soft"),
    (T_SAP, hms(23, 59, 54), "out4"),
    (T_DEC, hms(23, 59, 59.9), "soft"),
    (T_YOU + 0.3, hms(23, 59, 59.9985), "out2"),
    (T_LOOP, hms(23, 59, 59.9995), "lin"),
    (DUR, C0, "rew"),
]


def clock(t):
    for k in range(len(CKEYS) - 1):
        ta, ca, _ = CKEYS[k]
        tb, cb, mode = CKEYS[k + 1]
        if ta <= t < tb:
            u = (t - ta) / (tb - ta)
            if mode == "soft":
                e = 0.78 * smoother(u) + 0.22 * u
            elif mode == "out4":
                e = 1 - (1 - u) ** 4
            elif mode == "out2":
                e = 1 - (1 - u) ** 2
            elif mode == "rew":
                e = smoother(u)
            else:
                e = u
            return ca + (cb - ca) * e
    return C0


def clock_speed(t):
    dt = 1 / 120
    return (clock(t + dt) - clock(t - dt)) / (2 * dt)


def rewind_amt(t):
    """intensidade do efeito VHS de rebobinar"""
    a = 0.0
    for ta, tb in ((T_RW_A, T_RW_B), (T_LOOP, DUR)):
        if ta <= t < tb:
            u = (t - ta) / (tb - ta)
            a = max(a, math.sin(math.pi * u) ** 0.6)
    return a


# ---------------------------------------------------------------- eras (em função do relógio -> rebobina junto)
STOPS = [  # (relógio, topo, base, brilho, partícula)
    (0, (42, 8, 0), (190, 55, 10), (255, 120, 30), "brasa"),
    (hms(2, 0), (8, 28, 36), (28, 96, 104), (90, 210, 190), "bolha"),
    (hms(11, 19), (3, 20, 46), (11, 90, 140), (60, 210, 255), "bolha"),
    (hms(21, 9), (2, 26, 56), (16, 112, 158), (90, 225, 255), "bolha"),
    (hms(21, 31), (4, 34, 15), (31, 122, 58), (140, 230, 120), "esporo"),
    (hms(22, 47), (12, 36, 14), (90, 120, 30), (210, 230, 90), "folha"),
    (hms(23, 39), NAVY, (58, 22, 96), (150, 90, 255), "estrela"),
]


def era_mix(c):
    """(i, j, w): cor = mistura de STOPS[i] e STOPS[j] com peso w em j"""
    i = 0
    for k, s in enumerate(STOPS):
        if c >= s[0]:
            i = k
    if i + 1 < len(STOPS):
        nxt = STOPS[i + 1][0]
        win = 0.06 * (nxt - STOPS[i][0])
        w = smoother((c - (nxt - win)) / win)
        return i, i + 1, w
    return i, i, 0.0


YY = np.linspace(0, 1, H, dtype=np.float32)[:, None]
XX = np.linspace(0, 1, W, dtype=np.float32)[None, :]
GLOBE_C = (CX, 1090.0)
GLOBE_R = 290.0
RADG = np.sqrt(((XX - GLOBE_C[0] / W) * W / H) ** 2 + (YY - GLOBE_C[1] / H) ** 2)
VIG = np.clip(1 - 0.75 * np.clip(np.sqrt((XX - 0.5) ** 2 * 1.2 + (YY - 0.5) ** 2) - 0.32, 0, 1) ** 1.3, 0, 1)[..., None]


def background(t):
    c = clock(t)
    i, j, w = era_mix(c)
    col = lambda k, idx: np.array(STOPS[k][idx], np.float32) / 255
    top = col(i, 1) * (1 - w) + col(j, 1) * w
    bot = col(i, 2) * (1 - w) + col(j, 2) * w
    gl = col(i, 3) * (1 - w) + col(j, 3) * w
    img = top + (bot - top) * (YY ** 1.2)[..., None]
    pulse = 0.85 + 0.15 * osc(t, 2.2)
    img = img + gl * (np.exp(-(RADG / 0.30) ** 2) * 0.28 * pulse)[..., None]
    return np.broadcast_to(img, (H, W, 3)).astype(np.float32)


RNG = np.random.default_rng(7)
NP_ = 80
PART = dict(x=RNG.random(NP_), y=RNG.random(NP_), s=RNG.uniform(0.6, 1.6, NP_), ph=RNG.uniform(0, 6.28, NP_),
            v=RNG.uniform(0.6, 1.4, NP_))


def particles(img, t):
    i, j, w = era_mix(clock(t))
    d = ImageDraw.Draw(img)
    for k, alpha in ((i, 1 - w), (j, w)):
        if alpha <= 0.02:
            continue
        kind, col = STOPS[k][4], STOPS[k][3]
        for n in range(NP_):
            sz, ph, v = PART["s"][n], PART["ph"][n], PART["v"][n]
            per = DUR / max(1, round(DUR / (7 / v)))
            ft = (t / per + PART["y"][n]) % 1.0
            x = PART["x"][n] * W
            if kind in ("brasa", "bolha"):
                y = H * (1.05 - ft * 1.1); x += 25 * math.sin(2 * math.pi * ft * 2 + ph)
            elif kind in ("esporo", "folha"):
                y = H * (ft * 1.1 - 0.05); x += 40 * math.sin(2 * math.pi * ft * 3 + ph)
            else:
                y = PART["y"][n] * H
            a = int(255 * alpha * (0.3 + 0.6 * (0.5 + 0.5 * math.sin(2 * math.pi * ft * 4 + ph))))
            r = 2.4 * sz if kind != "bolha" else 6 * sz
            if kind == "bolha":
                d.ellipse((x - r, y - r, x + r, y + r), outline=col + (a,), width=2)
            elif kind == "folha":
                d.ellipse((x - r * 2, y - r, x + r * 2, y + r), fill=col + (a // 2,))
            else:
                d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))


# ---------------------------------------------------------------- Terra 3D
GT = {}


def build_globe_tex():
    f = os.path.join(OUT, "globe_tex_v2.npz")
    if os.path.exists(f):
        GT.update(dict(np.load(f)))
        return
    print("gerando texturas da Terra...", flush=True)
    n = Noise(3)
    LAT, LON, x, y, z = sphere_grid(1024, 512)
    wx = n.fbm(x * 2 + 5, y * 2, z * 2, 3)
    elev = n.fbm(x * 1.7 + wx * 1.2, y * 1.7 + wx, z * 1.7, 6)
    veg = n.fbm(x * 5, y * 5, z * 5, 4)
    cw = n.fbm(x * 3 + 11, y * 3, z * 3, 3)
    cl = n.fbm(x * 3.2 + cw * 2, y * 3.2, z * 6.0 + cw, 6)
    clouds = np.clip((cl - 0.5) * 3.2, 0, 1)
    a = n.fbm(x * 3, y * 3, z * 3, 5)
    rid = 1 - np.abs(n.fbm(x * 5 + a, y * 5, z * 5, 4) - 0.5) * 2
    lava = np.clip((rid - 0.78) / 0.12, 0, 1)
    city = n.fbm(x * 40, y * 40, z * 40, 3)
    GT.update(elev=elev, veg=veg, clouds=clouds, lava=lava, crust=a, city=city,
              absl=(np.abs(LAT) / (np.pi / 2)).astype(np.float32))
    np.savez(f, **GT)


def C_(c):
    return np.array(c, np.float32) / 255


def lerp(a, b, w):
    return a + (b - a) * w


def globe_albedo(c):
    """textura da Terra no instante c do relógio"""
    elev, veg, absl = GT["elev"], GT["veg"], GT["absl"]
    # nível do mar: quase sem terra no começo, continentes crescem até o atual
    thr = 0.66 - 0.125 * smoother((c - hms(11, 0)) / (hms(21, 0) - hms(11, 0)))
    land = np.clip((elev - thr) / 0.012, 0, 1)
    oxy = smoother((c - hms(11, 0)) / hms(0, 40))
    ocean = lerp(lerp(C_((24, 100, 104)), C_((44, 135, 135)), np.clip((elev - 0.4) * 3, 0, 1)[..., None]),
                 lerp(C_((6, 32, 96)), C_((25, 95, 170)), np.clip((elev - thr + 0.08) / 0.08, 0, 1)[..., None] ** 2), oxy)
    barren = lerp(C_((110, 88, 70)), C_((165, 140, 112)), veg[..., None])
    green = lerp(C_((40, 105, 45)), C_((105, 125, 60)), veg[..., None])
    desert = np.clip(1 - np.abs(absl - 0.3) / 0.13, 0, 1) * np.clip((veg - 0.35) * 3, 0, 1)
    green = green * (1 - desert[..., None]) + C_((195, 165, 105)) * desert[..., None]
    plants = smoother((c - hms(21, 31)) / hms(0, 18))
    landc = lerp(barren, green, plants)
    col = ocean * (1 - land[..., None]) + landc * land[..., None]
    ice = np.clip((absl - 0.82) / 0.05, 0, 1)[..., None] * oxy
    col = col * (1 - ice) + 0.93 * ice
    return col.astype(np.float32), land


def globe_state(c, t):
    lava_w = 1 - smoother((c - hms(0, 25)) / hms(1, 30))
    if T_THEIA <= t < T_THEIA + 2.5:                  # impacto re-derrete
        lava_w = max(lava_w, 1.0)
    oxy = smoother((c - hms(11, 0)) / hms(0, 40))
    cities = smoother((c - hms(23, 59, 48)) / 6.0) * (0.6 + 0.4 * smoother((c - C0) / 5.9))
    if rewind_amt(t) > 0 and t < T_RW_B:
        cities *= clamp(1 - (t - T_RW_A) / 0.6)
    atm = lerp(lerp(C_((255, 120, 40)), C_((230, 150, 90)), smoother(c / hms(2, 0))), C_((90, 160, 255)), oxy)
    return lava_w, oxy, cities, atm


def globe_spin(t):
    rw1 = smoother(clamp((t - T_RW_A) / (T_RW_B - T_RW_A)))
    rw2 = smoother(clamp((t - T_LOOP) / (DUR - T_LOOP)))
    return 2.0 * t / DUR - 0.5 * rw1 - 0.5 * rw2      # 2 voltas - 1 de rebobinar = inteiro -> loop


LIGHT = np.array([-0.62, 0.38, 0.69], np.float32)
LIGHT /= np.linalg.norm(LIGHT)
ASH = {}


def draw_globe(canvas, t, cx, cy, R):
    c = clock(t)
    lava_w, oxy, cities, atm = globe_state(c, t)
    alb, land = globe_albedo(c)
    ext = R * 1.25
    x0, x1 = int(max(0, cx - ext)), int(min(W, cx + ext))
    y0, y1 = int(max(0, cy - ext)), int(min(H, cy + ext))
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    X, Y = (xs + 0.5 - cx) / R, (ys + 0.5 - cy) / R
    d = np.sqrt(X * X + Y * Y)
    reg = canvas[y0:y1, x0:x1]
    # atmosfera externa
    halo = np.clip(1 - (d - 1) / 0.12, 0, 1) ** 2 * (d >= 1)
    lit2 = np.clip(0.25 + 0.9 * (X * LIGHT[0] - Y * LIGHT[1]) / np.maximum(d, 1e-3), 0, 1)
    reg += (halo * lit2 * 0.7)[..., None] * atm
    if lava_w > 0:
        reg += (np.exp(-np.maximum(d - 1, 0) * 6) * (d > 0.98) * 0.5 * lava_w)[..., None] * C_((255, 110, 25))
    iy, ix = np.nonzero(d < 1 + 1.5 / R)
    Xi, Yi = X[iy, ix], Y[iy, ix]
    Zi = np.sqrt(np.clip(1 - Xi * Xi - Yi * Yi, 0, 1))
    tilt = 0.32
    ct, st = math.cos(tilt), math.sin(tilt)
    bx = Xi * ct + Yi * st
    by = -(-Xi * st + Yi * ct)
    lat = np.arcsin(np.clip(by, -1, 1))
    lon = np.arctan2(bx, Zi)
    spin = globe_spin(t)
    u = (lon / (2 * np.pi) + 0.5 + spin) % 1.0
    v = 0.5 - lat / np.pi
    col = sample(alb, u, v)
    ndl = Xi * LIGHT[0] - Yi * LIGHT[1] + Zi * LIGHT[2]
    shade = 0.03 + 0.97 * np.clip(ndl, 0, 1) ** 0.85 * (0.6 + 0.4 * np.clip((ndl + 0.12) / 0.24, 0, 1))
    # nuvens: névoa laranja (sem oxigênio) -> nuvens brancas
    cl = sample(GT["clouds"], (u + t / DUR) % 1.0, v)
    haze = (1 - oxy) * 0.32
    col = col * (1 - haze) + C_((210, 130, 70)) * haze
    cw = cl[:, None] * (0.25 + 0.65 * oxy)
    col = col * (1 - cw) + 0.96 * cw
    col = col * shade[:, None]
    # oceano: brilho especular
    lm = sample(land.astype(np.float32), u, v)
    hv = np.array([LIGHT[0], LIGHT[1], LIGHT[2] + 1]); hv /= np.linalg.norm(hv)
    spec = np.clip(Xi * hv[0] - Yi * hv[1] + Zi * hv[2], 0, 1) ** 70 * (1 - lm) * (1 - cl) * 0.6 * oxy
    col += spec[:, None]
    # lava
    if lava_w > 0:
        lv = sample(GT["lava"], u, v)
        cr = sample(GT["crust"], u, v)
        crust = ramp(cr, [(0, (35, 14, 10)), (0.6, (70, 30, 18)), (1, (110, 50, 25))]) * (0.25 + 0.9 * np.clip(ndl, 0, 1))[:, None]
        flick = 1 + 0.12 * np.sin(t * 7 + Xi * 9) * np.sin(t * 5 + Yi * 11)
        hot = ramp(lv, [(0, (255, 90, 10)), (0.6, (255, 170, 40)), (1, (255, 240, 150))]) * (lv * flick)[:, None]
        lavac = crust * (1 - lv[:, None]) + hot + ((1 - Zi) ** 3 * 0.5)[:, None] * C_((255, 120, 30))
        col = col * (1 - lava_w) + lavac * lava_w
    # luzes das cidades no lado noturno
    if cities > 0:
        cn = sample(GT["city"], u, v)
        night = np.clip((0.12 - ndl) / 0.3, 0, 1)
        lights = np.clip((cn - 0.56) * 6, 0, 1) * lm * night * cities
        col += lights[:, None] * C_((255, 200, 110)) * 1.4
    # cinzas do asteroide
    dtb = t - T_BOOM
    if 0 <= dtb < 4.5:
        ix0, iy0 = ASH["pt"]
        dist = np.sqrt(((xs[iy, ix] - ix0) / R) ** 2 + ((ys[iy, ix] - iy0) / R) ** 2)
        front = clamp(dtb / 1.2) * 2.4
        dark = np.clip((front - dist) / 0.3, 0, 1) * (0.78 * clamp((4.5 - dtb) / 3.0))
        col = col * (1 - dark[:, None]) + C_((40, 32, 36)) * dark[:, None]
        glow = np.exp(-(dist / max(0.05, 0.25 * (1 + dtb))) ** 2) * clamp(1 - dtb / 1.5) * 1.5
        col += glow[:, None] * C_((255, 160, 60))
    # borda iluminada (rim)
    col += ((1 - Zi) ** 2.5 * 0.35 * np.clip(ndl + 0.35, 0, 1))[:, None] * atm
    a = np.clip((1 - d[iy, ix]) * R + 0.5, 0, 1)[:, None]
    reg[iy, ix] = reg[iy, ix] * (1 - a) + np.clip(col, 0, 2) * a


def small_sphere(canvas, cx, cy, R, base, emissive=None, t=0.0):
    if R < 0.8:
        return
    x0, x1 = int(max(0, cx - R - 2)), int(min(W, cx + R + 2))
    y0, y1 = int(max(0, cy - R - 2)), int(min(H, cy + R + 2))
    if x0 >= x1 or y0 >= y1:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    X, Y = (xs + 0.5 - cx) / R, (ys + 0.5 - cy) / R
    d = np.sqrt(X * X + Y * Y)
    Z = np.sqrt(np.clip(1 - d * d, 0, 1))
    ndl = np.clip(X * LIGHT[0] - Y * LIGHT[1] + Z * LIGHT[2], 0, 1)
    tex = GT["crust"][((Y * 0.5 + 0.5) * 300).astype(int) % 512, ((X * 0.5 + 0.5 + t * 0.01) * 300).astype(int) % 1024]
    col = C_(base) * (0.7 + 0.5 * tex)[..., None] * (0.06 + 0.94 * ndl)[..., None]
    if emissive is not None:
        col += C_(emissive) * (np.clip((tex - 0.55) * 4, 0, 1) * 1.2)[..., None]
    a = np.clip((1 - d) * R + 0.5, 0, 1)[..., None]
    reg = canvas[y0:y1, x0:x1]
    reg[:] = reg * (1 - a) + col * a


ORB = dict(rx=420, ry=105, tilt=-0.18)


def moon_pos(t):
    th = t * PF(2 * math.pi * 3 / DUR) + 0.9
    x, y = ORB["rx"] * math.cos(th), ORB["ry"] * math.sin(th)
    ct, st = math.cos(ORB["tilt"]), math.sin(ORB["tilt"])
    return GLOBE_C[0] + x * ct - y * st, GLOBE_C[1] - 60 + x * st + y * ct, math.sin(th)


def moon_alpha(t):
    c = clock(t)
    if T_THEIA <= t < T_THEIA + 1.6:
        return smoother((t - T_THEIA - 0.8) / 0.8)
    return 1.0 if c >= hms(0, 12) else 0.0


def theia(canvas, t, shake_xy):
    a, b = T_THEIA - 1.4, T_THEIA
    if not (a <= t < b):
        return
    u = ((t - a) / (b - a)) ** 1.5
    tx = GLOBE_C[0] - GLOBE_R * 0.62 - 100
    ty = GLOBE_C[1] - GLOBE_R * 0.58 - 100
    sx, sy = -260, 760
    small_sphere(canvas, sx + (tx - sx) * u + shake_xy[0], sy + (ty - sy) * u + shake_xy[1], 120, (120, 50, 30), (255, 140, 40), t)


def debris(img, t):
    dt = t - T_THEIA
    if not (0 <= dt < 1.8):
        return
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(9)
    mx, my, _ = moon_pos(T_THEIA + 1.6)
    for i in range(70):
        ang = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0.8, 1.2)
        ox = GLOBE_C[0] - GLOBE_R * 0.6 + math.cos(ang) * GLOBE_R * 1.3 * rr * ease_out_cubic(dt / 0.8)
        oy = GLOBE_C[1] - GLOBE_R * 0.55 + math.sin(ang) * GLOBE_R * 0.5 * rr * ease_out_cubic(dt / 0.8)
        k = smoother((dt - 0.6) / 1.0)
        x, y = ox + (mx - ox) * k, oy + (my - oy) * k
        r = rng.uniform(3, 9) * (1 - 0.5 * k)
        al = int(255 * clamp((1.8 - dt) / 0.5))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, int(150 + 80 * k), 60, al))


def asteroid(img, t, sxy):
    a, b = S["asteroide"] - 0.1, T_BOOM
    if not (a <= t < b):
        return
    u = (t - a) / (b - a)
    e = u ** 1.7
    x1, y1 = ASH["pt"]
    x0, y0 = 1180, 620
    x, y = x0 + (x1 - x0) * e + sxy[0], y0 + (y1 - y0) * e + sxy[1]
    d = ImageDraw.Draw(img)
    ang = math.atan2(y1 - y0, x1 - x0)
    for k in range(30, 0, -1):
        tx, ty = x - math.cos(ang) * k * 13 * (0.5 + e), y - math.sin(ang) * k * 13 * (0.5 + e)
        r = 32 * (1 - k / 34) * (0.6 + 0.4 * e)
        d.ellipse((tx - r, ty - r, tx + r, ty + r), fill=(255, int(120 + 110 * (1 - k / 30)), 40, int(210 * (1 - k / 30))))
    r = 20 + 12 * e
    pts = [(x + r * (1 + 0.2 * math.sin(i * 2.3)) * math.cos(i * 0.785), y + r * (1 + 0.2 * math.sin(i * 2.3)) * math.sin(i * 0.785))
           for i in range(8)]
    d.polygon(pts, fill=(105, 88, 80, 255), outline=(0, 0, 0, 255), width=4)


def shockwave(img, t):
    dt = t - T_BOOM
    if not (0 <= dt < 1.2):
        return
    d = ImageDraw.Draw(img)
    x, y = ASH["pt"]
    for k, sp in enumerate((1.0, 0.7)):
        r = 20 + 520 * ease_out_cubic(dt / 1.0) * sp
        a = int(230 * clamp(1 - dt / 1.0))
        d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), outline=(255, 225, 160, a), width=10 - 4 * k)


# ---------------------------------------------------------------- selos com silhuetas suaves
def chaikin(pts, it=3):
    for _ in range(it):
        new = []
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            new += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        pts = new
    return pts


TREX = [(0.02, 0.42), (0.20, 0.36), (0.40, 0.30), (0.55, 0.28), (0.64, 0.24), (0.70, 0.15), (0.80, 0.11), (0.92, 0.12),
        (0.99, 0.17), (0.98, 0.23), (0.87, 0.25), (0.96, 0.28), (0.89, 0.33), (0.77, 0.33), (0.71, 0.40), (0.69, 0.47),
        (0.76, 0.53), (0.80, 0.58), (0.75, 0.58), (0.68, 0.55), (0.62, 0.62), (0.61, 0.70), (0.64, 0.82), (0.63, 0.89),
        (0.72, 0.94), (0.72, 0.98), (0.56, 0.98), (0.55, 0.86), (0.52, 0.74), (0.48, 0.71), (0.45, 0.79), (0.47, 0.89),
        (0.54, 0.94), (0.54, 0.98), (0.40, 0.98), (0.38, 0.85), (0.34, 0.67), (0.28, 0.57), (0.16, 0.49), (0.03, 0.45)]
HUMAN = [(0.50, 0.08), (0.58, 0.12), (0.59, 0.21), (0.55, 0.26), (0.63, 0.30), (0.70, 0.46), (0.74, 0.56), (0.69, 0.58),
         (0.62, 0.45), (0.60, 0.58), (0.68, 0.74), (0.74, 0.92), (0.66, 0.94), (0.57, 0.76), (0.50, 0.66), (0.44, 0.78),
         (0.36, 0.94), (0.28, 0.92), (0.38, 0.72), (0.42, 0.56), (0.41, 0.44), (0.33, 0.55), (0.27, 0.53), (0.35, 0.36),
         (0.45, 0.28), (0.42, 0.21), (0.43, 0.12)]


def badge(kind, size=210):
    """círculo com degradê + silhueta preta suavizada, renderizado em 4x"""
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cols = {"vida": ((40, 120, 140), (120, 230, 210)), "oxi": ((20, 70, 140), (120, 210, 255)),
            "ani": ((10, 60, 110), (60, 170, 220)), "plant": ((30, 90, 40), (150, 220, 120)),
            "dino": ((200, 80, 30), (255, 190, 90)), "sap": ((70, 40, 140), (200, 140, 255)),
            "pir": ((190, 110, 40), (255, 210, 120))}[kind]
    for k in range(60):
        r = s / 2 - 8 - k * (s / 2 - 8) / 60
        cc = tuple(int(cols[1][i] + (cols[0][i] - cols[1][i]) * (k / 60) ** 0.7) for i in range(3))
        cc = tuple(int(cols[0][i] + (cols[1][i] - cols[0][i]) * (k / 60)) for i in range(3))
        d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), fill=cc + (255,))
    ink = (12, 10, 20, 255)
    S_ = lambda pts, sc=0.70, ox=0.15, oy=0.17: [(s * (ox + x * sc), s * (oy + y * sc)) for x, y in pts]
    if kind == "dino":
        d.ellipse((s * 0.52, s * 0.18, s * 0.80, s * 0.46), fill=(255, 230, 150, 255))   # sol poente
        d.polygon(S_(chaikin(TREX), 0.74, 0.12, 0.16), fill=ink)
        d.rectangle((s * 0.05, s * 0.86, s * 0.95, s), fill=ink)
    elif kind == "sap":
        d.polygon(S_(chaikin(HUMAN), 0.78, 0.11, 0.08), fill=ink)
        d.ellipse((s * 0.43, s * 0.12, s * 0.59, s * 0.28), fill=ink)
    elif kind == "pir":
        d.ellipse((s * 0.58, s * 0.16, s * 0.80, s * 0.38), fill=(255, 245, 200, 255))
        for (a, b, c) in [((0.10, 0.78), (0.34, 0.44), (0.58, 0.78)), ((0.30, 0.78), (0.58, 0.30), (0.88, 0.78)),
                          ((0.62, 0.78), (0.78, 0.55), (0.94, 0.78))]:
            d.polygon([(s * a[0], s * a[1]), (s * b[0], s * b[1]), (s * c[0], s * c[1])], fill=ink)
        d.rectangle((0, s * 0.77, s, s), fill=ink)
    elif kind == "plant":
        stem = [(0.5 + 0.06 * math.sin(k / 6), 0.88 - k * 0.7 / 20) for k in range(21)]
        d.line([(s * x, s * y) for x, y in stem], fill=ink, width=int(s * 0.03), joint="curve")
        for k in range(2, 20, 2):
            x, y = stem[k]
            L = 0.22 * (1 - k / 26)
            for sgn in (-1, 1):
                leaf = chaikin([(x, y), (x + sgn * L * 0.5, y - 0.05), (x + sgn * L, y - 0.02), (x + sgn * L * 0.5, y + 0.02)], 2)
                d.polygon([(s * a, s * b) for a, b in leaf], fill=ink)
        d.rectangle((0, s * 0.86, s, s), fill=ink)
    elif kind == "ani":   # trilobita
        body = chaikin([(0.5, 0.14), (0.70, 0.22), (0.80, 0.42), (0.74, 0.70), (0.58, 0.88), (0.5, 0.92), (0.42, 0.88),
                        (0.26, 0.70), (0.20, 0.42), (0.30, 0.22)], 3)
        d.polygon([(s * x, s * y) for x, y in body], fill=ink)
        for k in range(8):
            y = 0.40 + k * 0.06
            d.line((s * 0.27, s * y, s * 0.73, s * y), fill=cols[0] + (255,), width=int(s * 0.012))
        d.line((s * 0.5, s * 0.36, s * 0.5, s * 0.86), fill=cols[0] + (255,), width=int(s * 0.012))
        d.ellipse((s * 0.36, s * 0.22, s * 0.44, s * 0.30), fill=cols[1] + (255,))
        d.ellipse((s * 0.56, s * 0.22, s * 0.64, s * 0.30), fill=cols[1] + (255,))
    elif kind == "vida":
        rng = np.random.default_rng(2)
        for cx_, cy_, r in [(0.5, 0.5, 0.17), (0.28, 0.34, 0.09), (0.72, 0.33, 0.1), (0.3, 0.72, 0.08), (0.7, 0.7, 0.11)]:
            pts = [(cx_ + r * (1 + 0.1 * math.sin(3 * a + rng.random())) * math.cos(a) * 1.2,
                    cy_ + r * (1 + 0.1 * math.sin(3 * a)) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30, endpoint=False)]
            d.polygon([(s * x, s * y) for x, y in pts], fill=(220, 255, 240, 230), outline=ink, width=10)
            d.ellipse((s * (cx_ - r * 0.3), s * (cy_ - r * 0.3), s * (cx_ + r * 0.3), s * (cy_ + r * 0.3)), fill=(30, 110, 110, 255))
    elif kind == "oxi":
        for cx_, cy_, r in [(0.30, 0.66, 0.08), (0.62, 0.74, 0.06), (0.72, 0.42, 0.07), (0.40, 0.36, 0.05)]:
            d.ellipse((s * (cx_ - r), s * (cy_ - r), s * (cx_ + r), s * (cy_ + r)), outline=(255, 255, 255, 230), width=12)
        f = font("anton", int(s * 0.36))
        d.text((s * 0.5, s * 0.52), "O₂", font=f, fill=WHITE + (255,), anchor="mm", stroke_width=14, stroke_fill=ink)
    # aro
    d.ellipse((6, 6, s - 6, s - 6), outline=(255, 255, 255, 255), width=int(s * 0.03))
    d.ellipse((0, 0, s - 1, s - 1), outline=(0, 0, 0, 255), width=int(s * 0.012))
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse((0, 0, s - 1, s - 1), fill=255)
    img.putalpha(Image.fromarray(np.minimum(np.asarray(img.getchannel("A")), np.asarray(m))))
    return img.resize((size, size), Image.LANCZOS)


BADGES = {}
BADGE_T = []   # (tipo, início, fim)


def build_badges():
    for k in ("vida", "oxi", "ani", "plant", "dino", "sap", "pir"):
        BADGES[k] = badge(k)
    BADGE_T[:] = [("vida", T_VIDA, T_OXI - 0.1), ("oxi", T_OXI, T_ANI - 0.1), ("ani", T_ANI, T_PLANT - 0.1),
                  ("plant", T_PLANT, T_DINO - 0.1), ("dino", T_DINO, T_BOOM), ("sap", T_SAP, T_PIR - 0.05),
                  ("pir", T_PIR, T_CARD - 0.1)]


BADGE_XY = (825, 845)


def draw_badges(frame, t, sxy):
    for k, a, b in BADGE_T:
        if a <= t < b:
            sc = ease_out_back(clamp((t - a) / 0.4), 1.8) * (0.3 + 0.7 * clamp((b - t) / 0.2))
            if k == "dino" and t > b - 0.25:      # estilhaça no impacto
                sc *= 1 + (t - (b - 0.25)) * 2
            fl = 6 * osc(t, 3.0)
            paste(frame, BADGES[k], BADGE_XY[0] + sxy[0], BADGE_XY[1] + fl + sxy[1], sc, rot=4 * osc(t, 1.7))


# ---------------------------------------------------------------- relógio
CLOCK_Y = 470
_dig = {}


def glyph(ch, size, color):
    k = (ch, size, color)
    if k not in _dig:
        _dig[k] = rich_text(ch, size, "anton", color=color, stroke=max(6, size // 22))
    return _dig[k]


def draw_digits(frame, txt, cx, cy, size, color, alpha=1.0, glow=CYAN):
    if alpha <= 0.01:
        return 0
    dw = glyph("0", size, color).width - size * 0.06
    cw = glyph(":", size, color).width - size * 0.08
    widths = [cw if c in ":," else dw for c in txt]
    total = sum(widths)
    layer = Image.new("RGBA", (int(total + size), int(size * 1.6)), (0, 0, 0, 0))
    lx = size / 2
    for c, w in zip(txt, widths):
        g = glyph(c, size, color)
        layer.alpha_composite(g, (int(lx + w / 2 - g.width / 2), int(size * 0.8 - g.height / 2)))
        lx += w
    if glow:
        a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(size * 0.12))
        gl = Image.new("RGBA", layer.size, glow + (0,))
        gl.putalpha(a.point(lambda v: int(v * 0.85)))
        paste(frame, gl, cx, cy, 1.0, alpha)
    paste(frame, layer, cx, cy, 1.0, alpha)
    return total


def fmt_clock(c, decimals=0):
    c = max(0.0, min(c, DAY - 1e-6))
    h, m, s = int(c // 3600), int((c % 3600) // 60), c % 60
    if decimals == 0:
        return f"{h:02d}:{m:02d}:{int(s):02d}"
    sec = int(s)
    frac = int(round((s - sec) * 10 ** decimals))
    if frac >= 10 ** decimals:
        frac = 10 ** decimals - 1
    return f"{h:02d}:{m:02d}:", f"{sec:02d}", f",{frac:0{decimals}d}"


def slowmo(t):
    """1 = layout câmera lenta (zoom nos segundos): no gancho e depois do asteroide"""
    if t < T_RW_A + 0.4:
        return 1 - smoother((t - T_RW_A) / 0.4)
    return smoother((t - T_SLOW) / 0.45)


def draw_clock(frame, t, sxy):
    c = clock(t)
    z = slowmo(t)
    sx, sy = sxy
    beat = 1 + 0.02 * osc(t, 4 * math.pi)
    red = rewind_amt(t) > 0.05
    if z < 0.999:
        draw_digits(frame, fmt_clock(c), CX + sx, CLOCK_Y + sy, int(210 * (1 - 0.35 * z) * beat),
                    (255, 120, 120) if red else WHITE, clamp(1 - z * 2.2), glow=(255, 60, 60) if red else CYAN)
    if z <= 0.01:
        return
    zi = clamp((z - 0.35) / 0.65)
    dec = 3 if (T_DEC <= t < T_LOOP) else 2
    pre, sec, frac = fmt_clock(c, dec)
    draw_digits(frame, pre, CX + sx, 330 + sy, 80, (205, 215, 235), zi, glow=None)
    big = int(250 * beat)
    fsz = int(big * 0.42)
    wsec = glyph("0", big, YEL).width * 2 - big * 0.12
    wfr = (glyph("0", fsz, WHITE).width - fsz * 0.06) * (dec + 0.5)
    x0 = CX - (wsec + wfr) / 2
    draw_digits(frame, sec, x0 + wsec / 2 + sx, CLOCK_Y + 10 + sy, big, YEL, zi)
    draw_digits(frame, frac, x0 + wsec + wfr / 2 + sx, CLOCK_Y + 10 + big * 0.22 + sy, fsz, WHITE, zi)


# ---------------------------------------------------------------- barra do dia (com zoom)
BAR_Y, BAR_X0, BAR_X1 = 680, 130, 950
SEGS = [(0, hms(3, 55), (255, 110, 30)), (hms(3, 55), hms(21, 9), (60, 170, 255)), (hms(21, 9), hms(21, 31), (90, 225, 255)),
        (hms(21, 31), hms(22, 47), (110, 210, 90)), (hms(22, 47), hms(23, 39), (200, 230, 80)), (hms(23, 39), DAY, (170, 110, 255))]
SPANS = [(DAY, "O DIA INTEIRO"), (3600, "ÚLTIMA HORA"), (60, "ÚLTIMO MINUTO"), (1, "ÚLTIMO SEGUNDO")]


def bar_span(t):
    keys = [(0.0, 60.0), (T_RW_A, 60.0), (T_RW_A + 0.7, DAY), (T_SLOW, DAY), (T_SLOW + 0.8, 3600), (T_SAP - 0.3, 60),
            (T_PIR, 60), (T_DEC - 0.6, 1.0), (T_LOOP, 1.0), (DUR, 60.0)]
    for (ta, a), (tb, b) in zip(keys, keys[1:]):
        if ta <= t < tb:
            u = smoother((t - ta) / (tb - ta))
            return math.exp(math.log(a) + (math.log(b) - math.log(a)) * u)
    return 60.0


def draw_bar(frame, t):
    d = ImageDraw.Draw(frame)
    span = bar_span(t)
    L = DAY - span
    c = clock(t)
    X = lambda v: BAR_X0 + (BAR_X1 - BAR_X0) * clamp((v - L) / span)
    h = 30
    d.rounded_rectangle((BAR_X0 - 6, BAR_Y - h / 2 - 6, BAR_X1 + 6, BAR_Y + h / 2 + 6), 22, fill=(0, 0, 0, 200))
    d.rounded_rectangle((BAR_X0, BAR_Y - h / 2, BAR_X1, BAR_Y + h / 2), 16, fill=(255, 255, 255, 40))
    for a, b, col in SEGS:
        if b <= L or a >= c:
            continue
        xa, xb = X(max(a, L)), X(min(b, c))
        if xb - xa >= 1:
            d.rectangle((xa, BAR_Y - h / 2 + 3, xb, BAR_Y + h / 2 - 3), fill=col + (255,))
    if T_DEC - 0.3 <= t < T_LOOP:
        xa = X(DAY - 0.095)
        a = int(255 * clamp((t - T_DEC + 0.3) / 0.3))
        d.rectangle((xa, BAR_Y - h / 2 - 4, BAR_X1, BAR_Y + h / 2 + 4), outline=YEL + (a,), width=5)
    ph = X(c)
    d.ellipse((ph - 16, BAR_Y - 16, ph + 16, BAR_Y + 16), fill=WHITE + (255,), outline=(0, 0, 0, 255), width=4)
    lab = SPANS[0][1]
    for sp, name in SPANS:
        if span <= sp * 1.4:
            lab = name
    if T_RW_A <= t < DUR - 0.45:     # no gancho o selo amarelo ocupa esse lugar
        paste(frame, rich_text(lab, 32, color=CYAN), CX, BAR_Y - 48)
    if span > 2:
        paste(frame, rich_text(fmt_clock(L), 26), BAR_X0 + 64, BAR_Y + 42)
    else:
        paste(frame, rich_text("23:59:59", 26), BAR_X0 + 64, BAR_Y + 42)
    if not (T_YOU - 0.1 <= t < T_LOOP):
        paste(frame, rich_text("24:00:00", 26), BAR_X1 - 64, BAR_Y + 42)


# ---------------------------------------------------------------- textos
_cache = {}


def pill(text, size=40, fg=NAVY, bg=CYAN):
    k = ("pill", text, size, bg, fg)
    if k not in _cache:
        f = font("mont", size)
        tl = int(f.getlength(text))
        img = rounded_panel(tl + 44, size + 30, bg + (255,), (size + 30) // 2, outline=(0, 0, 0, 255), ow=4)
        ImageDraw.Draw(img).text((22, 12), text, font=f, fill=fg)
        _cache[k] = img
    return _cache[k]


ERA_LABELS = []


def build_labels():
    ERA_LABELS[:] = [
        ("A TERRA *NASCE*", "4,5 BILHÕES DE ANOS ATRÁS", S["lava"] + 0.1, word_t("lua", "minutos") - 0.05),
        ("NASCE A *LUA*", "IMPACTO COM THEIA", T_THEIA + 0.2, T_VIDA - 0.05),
        ("PRIMEIRA *VIDA*", "3,8 BILHÕES DE ANOS ATRÁS", T_VIDA + 0.1, S["so"] + 0.1),
        ("SÓ *MICRÓBIOS*", "POR MAIS DE 15 HORAS", S["so"] + 0.15, T_OXI - 0.05),
        ("O AR GANHA *OXIGÊNIO*", "2,4 BILHÕES DE ANOS ATRÁS", T_OXI + 0.1, T_ANI - 0.05),
        ("EXPLOSÃO DE *ANIMAIS*", "538 MILHÕES DE ANOS ATRÁS", T_ANI + 0.1, T_PLANT - 0.05),
        ("PLANTAS EM *TERRA FIRME*", "470 MILHÕES DE ANOS ATRÁS", T_PLANT + 0.1, T_DINO - 0.05),
        ("*DINOSSAUROS*", "230 MILHÕES DE ANOS ATRÁS", T_DINO + 0.1, T_REIGN - 0.05),
        ("REINAM POR *52 MINUTOS*", "164 MILHÕES DE ANOS", T_REIGN, S["asteroide"] - 0.05),
        ("O *ASTEROIDE*", "66 MILHÕES DE ANOS ATRÁS", S["asteroide"], T_SLOW + 0.4),
        ("*HOMO SAPIENS*", "300 MIL ANOS ATRÁS", T_SAP + 0.1, T_PIR - 0.05),
        ("TODA A *HISTÓRIA ESCRITA*", "5 MIL ANOS = 0,1 SEGUNDO", T_PIR + 0.1, T_CARD - 0.05),
    ]


def era_labels(frame, t):
    for title, years, a, b in ERA_LABELS:
        if a <= t < b:
            al = clamp((b - t) / 0.15)
            paste(frame, rich_text(title, 56, maxw=MAXW), CX, 1428, pop(t, a), al)
            paste(frame, pill(years, 34), CX, 1494, pop(t, a + 0.08), al)


def final_card():
    if "card" not in _cache:
        a = rich_text("A SUA VIDA INTEIRA DURA", 52, maxw=780)
        b = rich_text("0,0015 SEGUNDO", 124, "anton", color=YEL, stroke=10)
        c = rich_text("NESSE RELÓGIO", 52, maxw=780)
        pw, ph = 820, a.height + b.height + c.height + 40
        img = rounded_panel(pw, ph, NAVY + (230,), 44, outline=YEL + (255,), ow=6)
        y = 18
        for im in (a, b, c):
            img.alpha_composite(im, ((pw - im.width) // 2, y))
            y += im.height
        _cache["card"] = img
    return _cache["card"]


def rewind_icon(frame, cx, cy, al):
    d = ImageDraw.Draw(frame)
    for k in (0, 1):
        x = cx - 10 + k * 46
        d.polygon([(x + 40, cy - 32), (x + 40, cy + 32), (x - 8, cy)], fill=WHITE + (int(255 * al),), outline=(0, 0, 0, 255))


def ui(frame, t, sxy):
    d = ImageDraw.Draw(frame)
    draw_badges(frame, t, sxy)
    era_labels(frame, t)
    # gancho (frame 0) — volta no fim do loop
    hook = rich_text("TODA A HUMANIDADE CABE EM *6 SEGUNDOS*", 62, maxw=800)
    if t < T_RW_A:
        paste(frame, hook, CX, 168, 1 + 0.02 * osc(t, 5.0), clamp((T_RW_A - t) / 0.15))
        # seta "VOCÊ ESTÁ AQUI" apontando para os segundos
        if t >= 0.0:
            bob = 8 * osc(t, 6.0)
            paste(frame, pill("A HUMANIDADE ESTÁ AQUI", 30, bg=YEL), CX, 612 + bob, 1.0, clamp((T_RW_A - t) / 0.15))
    if t >= DUR - 0.45:
        u = clamp((t - (DUR - 0.45)) / 0.35)
        sc = 0.6 + 0.4 * ease_out_back(u, 2.0) if u < 1 else 1.0
        paste(frame, hook, CX, 168, sc, clamp(u * 3))
        paste(frame, pill("A HUMANIDADE ESTÁ AQUI", 30, bg=YEL), CX, 612 + 8 * osc(t, 6.0), sc, clamp(u * 3))
    ra = rewind_amt(t)
    if T_RW_A <= t < T_RW_B:
        al = clamp((t - T_RW_A) / 0.15) * clamp((T_RW_B - t) / 0.15)
        paste(frame, rich_text("VOLTANDO *4,5 BILHÕES* DE ANOS", 62, maxw=MAXW), CX + 30, 190, 1.0, al)
        rewind_icon(frame, 160, 190, al * (0.6 + 0.4 * osc(t, 12.0)))
    if S["humanos"] - 0.1 <= t < T_SAP + 0.1:
        paste(frame, rich_text("E A *GENTE?*", 100, maxw=MAXW), CX, 190, pop(t, S["humanos"] - 0.1), clamp((T_SAP + 0.1 - t) / 0.12))
    if T_SLOW <= t < T_CARD:
        al = clamp((t - T_SLOW) / 0.3) * clamp((T_CARD - t) / 0.2)
        paste(frame, pill("CÂMERA LENTA", 30, bg=YEL), CX, 262, 1 + 0.04 * osc(t, 8.0), al)
    # "Pirâmides, Roma, a internet"
    for txt, ta in (("PIRÂMIDES", T_PIR), ("ROMA", T_ROMA), ("INTERNET", T_NET)):
        if ta <= t < T_CARD - 0.1:
            k = ["PIRÂMIDES", "ROMA", "INTERNET"].index(txt)
            paste(frame, pill(txt, 34, bg=WHITE), 250 + k * 0 if False else 230, 900 + k * 78, pop(t, ta),
                  clamp((T_CARD - 0.1 - t) / 0.15))
    # cartão final + CTA
    if T_CARD <= t < T_LOOP:
        al = clamp((T_LOOP - t) / 0.12)
        e2 = ease_out_back(clamp((t - T_CARD) / 0.35), 1.8)
        paste(frame, final_card(), CX, 1100, (0.8 + 0.2 * e2) * (1 + 0.012 * osc(t, 5.0)), al)
        if t >= T_YOU - 0.1:
            sc = pop(t, T_YOU - 0.1)
            paste(frame, rich_text("*VOCÊ*", 46, maxw=300), BAR_X1 - 50, BAR_Y + 92, sc, al)
            d.polygon([(BAR_X1 - 12, BAR_Y + 26), (BAR_X1 + 2, BAR_Y + 52), (BAR_X1 - 26, BAR_Y + 52)],
                      fill=YEL + (int(255 * al),), outline=(0, 0, 0, 255))
    if T_CTA <= t < T_LOOP:
        al = clamp((T_LOOP - t) / 0.12)
        paste(frame, rich_text("PERA, OI?", 120, "anton", color=YEL, stroke=10), CX, 190, pop(t, T_CTA) * (1 + 0.03 * osc(t, 7.0)), al)
        tq = word_t("cta", "comenta") - 0.05
        if t >= tq:
            paste(frame, rich_text("COMENTA: QUAL *ESCALA* AGORA?", 50, maxw=MAXW), CX, 1440, pop(t, tq), al)
    caption(frame, t)


# ---------------------------------------------------------------- legendas
CHUNKS = []


def build_chunks():
    CHUNKS.clear()
    cur, line = [], None
    for w in P["words"]:
        if w["line"] in ("cta",):
            continue
        if cur and (w["line"] != line or len(cur) >= 3 or sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > 16):
            CHUNKS.append(cur); cur = []
        cur.append(w); line = w["line"]
    if cur:
        CHUNKS.append(cur)


def caption(frame, t):
    for ci, ch in enumerate(CHUNKS):
        a = max(0.04, ch[0]["t"] - 0.05)
        b = ch[-1]["t"] + ch[-1]["d"] + 0.15
        if ci + 1 < len(CHUNKS) and CHUNKS[ci + 1][0]["line"] == ch[0]["line"]:
            b = min(b, CHUNKS[ci + 1][0]["t"] - 0.05)
        if a <= t < b:
            parts = []
            for w in ch:
                txt = w["w"].upper().strip(",.!?:;…")
                act = w["t"] - 0.03 <= t < w["t"] + w["d"] + 0.03 or (w is ch[-1] and t >= w["t"])
                parts.append(f"*{txt}*" if act else txt)
            paste(frame, rich_text(" ".join(parts), 58, maxw=MAXW + 60), CX, 1568,
                  0.82 + 0.18 * ease_out_back(clamp((t - a) / 0.16), 2.0))
            return


# ---------------------------------------------------------------- efeitos de tela
def shake(t):
    ox = oy = 0.0
    for t0, amp in ((T_BOOM, 40), (T_THEIA, 26)):
        dt = t - t0
        if 0 <= dt < 1.1:
            a = amp * math.exp(-dt * 4.5)
            ox += a * math.sin(dt * 73) * math.cos(dt * 11)
            oy += a * math.sin(dt * 51 + 1.1)
    return ox, oy


def flash(t):
    f = 0.0
    for t0, pk in ((T_BOOM, 1.0), (T_THEIA, 0.7)):
        if t0 - 0.03 <= t < t0 + 0.55:
            f = max(f, pk * (1.0 if t < t0 + 0.06 else 1 - smoother((t - t0 - 0.06) / 0.5)))
    return f


def vhs(arr, t, amt):
    """rebobinar: faixas deslocadas, separação RGB, linhas de varredura"""
    if amt <= 0.01:
        return arr
    rng = np.random.default_rng(int(t * FPS) + 5)
    out = arr.copy()
    sh = int(10 * amt)
    out[:, :, 0] = np.roll(arr[:, :, 0], sh, axis=1)
    out[:, :, 2] = np.roll(arr[:, :, 2], -sh, axis=1)
    for _ in range(int(6 * amt) + 1):
        y = rng.integers(0, H - 80)
        hgt = rng.integers(10, 70)
        out[y:y + hgt] = np.roll(out[y:y + hgt], int(rng.integers(-60, 60) * amt), axis=1)
    out[::4] = (out[::4] * (1 - 0.25 * amt)).astype(out.dtype)
    yb = int((t * 900) % H)
    out[yb:yb + 24] = np.clip(out[yb:yb + 24].astype(np.int16) + int(90 * amt), 0, 255).astype(np.uint8)
    return out


# ---------------------------------------------------------------- render
def init():
    E.init()
    build_globe_tex()
    build_badges()
    build_labels()
    build_chunks()
    gx, gy = GLOBE_C
    ASH["pt"] = (gx + GLOBE_R * 0.40, gy - GLOBE_R * 0.36)


def render_frame(f):
    t = f / FPS
    sxy = shake(t)
    bg = background(t)
    gx, gy = GLOBE_C[0] + sxy[0], GLOBE_C[1] + sxy[1]
    push = 1 + 0.03 * osc(t, 0.9)                      # respiração lenta da câmera
    R = GLOBE_R * push
    mx, my, mz = moon_pos(t)
    ma = moon_alpha(t)
    if ma > 0 and mz < 0:
        small_sphere(bg, mx + sxy[0], my + sxy[1], 40 * ma, (175, 172, 168))
    theia(bg, t, sxy)
    draw_globe(bg, t, gx, gy, R)
    if ma > 0 and mz >= 0:
        small_sphere(bg, mx + sxy[0], my + sxy[1], 40 * ma, (175, 172, 168))
    bg = bg * VIG
    img = Image.fromarray((np.clip(bg, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    particles(img, t)
    debris(img, t)
    asteroid(img, t, sxy)
    shockwave(img, t)
    draw_clock(img, t, sxy)
    draw_bar(img, t)
    ui(img, t, sxy)
    fl = flash(t)
    if fl > 0:
        img = Image.blend(img, Image.new("RGBA", img.size, (255, 255, 255, 255)), fl)
    arr = np.asarray(img.convert("RGB"))
    arr = vhs(arr, t, rewind_amt(t))
    return Image.fromarray(arr)


def render_range(args):
    a, b, path = args
    init()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(render_frame(f).tobytes())
    p.stdin.close()
    p.wait()
    return path


def sound_events():
    return dict(eras=[T_VIDA, T_OXI, T_ANI, T_PLANT, T_DINO], boom=T_BOOM, theia=T_THEIA, slow=T_SLOW, sap=T_SAP,
                pir=T_PIR, dec=T_DEC, you=T_YOU, card=T_CARD, cta=T_CTA, loop=T_LOOP, rw=(T_RW_A, T_RW_B),
                ast=S["asteroide"] - 0.1,
                pops=[T_VIDA, T_OXI, T_ANI, T_PLANT, T_DINO, T_SAP, T_PIR, T_ROMA, T_NET, T_YOU - 0.1, T_CTA])


def main():
    os.makedirs(OUT, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "times":
        for k, v in sorted(dict(T_RW_A=T_RW_A, T_RW_B=T_RW_B, T_THEIA=T_THEIA, T_VIDA=T_VIDA, T_OXI=T_OXI, T_ANI=T_ANI,
                                T_PLANT=T_PLANT, T_DINO=T_DINO, T_REIGN=T_REIGN, T_BOOM=T_BOOM, T_SAP=T_SAP, T_PIR=T_PIR,
                                T_DEC=T_DEC, T_CARD=T_CARD, T_YOU=T_YOU, T_CTA=T_CTA, T_LOOP=T_LOOP, DUR=DUR).items(),
                           key=lambda x: x[1]):
            print(f"{v:6.2f} {k}")
    elif cmd == "preview":
        init()
        pd = os.path.join(OUT, os.environ.get("PDIR", "preview"))
        os.makedirs(pd, exist_ok=True)
        for ts in sys.argv[2:]:
            f = min(NFRAMES - 1, int(round(float(ts) * FPS)))
            im = render_frame(f)
            if os.environ.get("GUIDES"):
                dd = ImageDraw.Draw(im)
                dd.line((W - 120, 0, W - 120, H), fill=(255, 0, 0), width=2)
                dd.line((0, H - 300, W, H - 300), fill=(255, 0, 0), width=2)
                dd.line((W / 2, 0, W / 2, H), fill=(0, 255, 0), width=1)
            im.save(os.path.join(pd, f"f{f:04d}.png"))
        print("ok")
    elif cmd == "video":
        from multiprocessing import Pool
        init()
        nw = int(os.environ.get("WORKERS", os.cpu_count() or 4))
        step = math.ceil(NFRAMES / (nw * 3))
        jobs = [(i, min(NFRAMES, i + step), os.path.join(OUT, f"seg{k:02d}.mp4")) for k, i in enumerate(range(0, NFRAMES, step))]
        with Pool(nw) as pool:
            segs = pool.map(render_range, jobs, chunksize=1)
        open(os.path.join(OUT, "segs.txt"), "w").write("".join(f"file '{s}'\n" for s in segs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "segs.txt"),
                        "-c", "copy", os.path.join(OUT, "video_mudo.mp4")], check=True)
        print("video ok")


if __name__ == "__main__":
    main()
