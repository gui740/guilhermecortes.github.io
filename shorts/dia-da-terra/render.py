"""PERA, OI? — SE A HISTÓRIA DA TERRA FOSSE UM DIA DE 24 HORAS
1080x1920, 30 fps, ~28,7 s, loop perfeito. Linha do tempo derivada da narração (plan.py).

  python render.py times | preview 0 5.2 ... | video
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "planetas"))
import engine as E   # textos, fontes, easing, ruído (motor do Short dos planetas)
from engine import (W, H, FPS, SAFE_R, clamp, smoother, ease_out_cubic, ease_out_back, rich_text, paste, pop,
                    rounded_panel, font, Noise, sample, sphere_grid, ramp)
import plan as PL

OUT = os.path.join(HERE, "out")
os.environ.setdefault("NARR", os.path.join(OUT, "narr"))
P = PL.load()
S, EN = P["S"], P["E"]
DUR, NFRAMES, T_LOOP = P["DUR"], P["NFRAMES"], P["T_LOOP"]

CX = SAFE_R / 2          # 480: centro da área segura
NAVY = (10, 14, 38)
YEL = (255, 214, 60)
CYAN = (60, 210, 255)
WHITE = (255, 255, 255)
DAY = 86400.0


def PF(w):
    """frequência angular arredondada para ciclos inteiros em DUR (loop perfeito)"""
    return 2 * math.pi * max(1, round(w * DUR / (2 * math.pi))) / DUR


def word_t(line, frag, which="t"):
    frag = frag.lower()
    for w in P["words"]:
        if w["line"] == line and frag in w["w"].lower():
            return w["t"] + (w["d"] if which == "end" else 0.0)
    return (S[line] + EN[line]) / 2


def hms(h, m, s=0.0):
    return h * 3600 + m * 60 + s


# ---------------------------------------------------------------- momentos
T_VIDA = word_t("vida", "quatro")
T_PLANT = word_t("plantas", "nove")
T_DINO = word_t("dinos", "quase")
T_BOOM = EN["asteroide"] + 0.25
T_SLOW = T_BOOM + 0.9                       # entra a câmera lenta
T_SAP = S["sapiens"] + 0.2
T_PIR = word_t("historia", "pirâmides")
T_DEC = word_t("historia", "décimo")
T_YOU = word_t("suavida", "milésimo")
T_CARD = S["suavida"]
T_CTA = S["cta"]
T_FLIP = T_LOOP + 0.12                      # relógio vira 00:00:00

CKEYS = [  # (tempo do vídeo, segundos do relógio, modo)
    (0.0, 0.0, None),
    (S["lava"] + 0.3, hms(0, 1, 30), "soft"),
    (T_VIDA + 0.05, hms(3, 55), "soft"),
    (T_PLANT + 0.05, hms(21, 31), "soft"),
    (T_DINO + 0.05, hms(22, 47), "soft"),
    (T_BOOM, hms(23, 39), "soft"),
    (T_SAP, hms(23, 59, 54), "out4"),       # desacelera forte
    (T_DEC + 0.25, hms(23, 59, 59.9), "soft"),
    (T_YOU + 0.3, hms(23, 59, 59.9985), "out2"),
    (T_FLIP, hms(23, 59, 59.9995), "lin"),
]


def clock(t):
    """segundos do dia mostrados no relógio"""
    if t >= T_FLIP:
        return 0.0
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
            else:
                e = u
            return ca + (cb - ca) * e
    return CKEYS[-1][1]


def clock_speed(t):
    dt = 1 / 120
    return max(0.0, (clock(t + dt) - clock(t - dt)) / (2 * dt))


# ---------------------------------------------------------------- eras e fundo
ERAS = [  # (início em tempo de vídeo, topo, base, glow, tipo de partícula)
    (-1, (42, 8, 0), (190, 55, 10), (255, 120, 30), "brasa"),
    (T_VIDA, (3, 20, 46), (11, 90, 140), (60, 210, 255), "bolha"),
    (T_PLANT, (4, 34, 15), (31, 122, 58), (140, 230, 120), "esporo"),
    (T_DINO, (12, 36, 14), (90, 120, 30), (210, 230, 90), "folha"),
    (T_BOOM, NAVY, (58, 22, 96), (150, 90, 255), "estrela"),
]


def era_index(t):
    if t >= T_FLIP:
        return 0
    k = 0
    for i, e in enumerate(ERAS):
        if t >= e[0]:
            k = i
    return k


def era_blend(t):
    """(índice atual, índice anterior, mistura 0..1)"""
    k = era_index(t)
    start = T_FLIP if (t >= T_FLIP) else ERAS[k][0]
    prev = len(ERAS) - 1 if t >= T_FLIP else max(0, k - 1)
    u = clamp((t - start) / 0.45) if start > 0 else 1.0
    return k, prev, smoother(u)


YY = np.linspace(0, 1, H, dtype=np.float32)[:, None]
XX = np.linspace(0, 1, W, dtype=np.float32)[None, :]
RAD = np.sqrt(((XX - CX / W) * W / H) ** 2 + (YY - 0.45) ** 2)
VIG = np.clip(1 - 0.75 * np.clip(np.sqrt((XX - 0.5) ** 2 * 1.2 + (YY - 0.5) ** 2) - 0.32, 0, 1) ** 1.3, 0, 1)[..., None]


def era_bg(k, t):
    _, top, bot, glow, _ = ERAS[k]
    top = np.array(top, np.float32) / 255
    bot = np.array(bot, np.float32) / 255
    g = np.array(glow, np.float32) / 255
    img = top + (bot - top) * (YY ** 1.2)[..., None]
    pulse = 0.85 + 0.15 * math.sin(t * PF(2.2))
    img = img + g * (np.exp(-(RAD / 0.33) ** 2) * 0.22 * pulse)[..., None]
    return np.broadcast_to(img, (H, W, 3)).copy() if img.shape[1] == 1 else img


def background(t):
    k, prev, u = era_blend(t)
    bg = era_bg(k, t)
    if u < 1:
        bg = era_bg(prev, t) * (1 - u) + bg * u
    return bg


RNG = np.random.default_rng(7)
PART = dict(x=RNG.random(90), y=RNG.random(90), s=RNG.uniform(0.6, 1.6, 90), ph=RNG.uniform(0, 6.28, 90),
            v=RNG.uniform(0.6, 1.4, 90))


def particles(img, t):
    k, prev, u = era_blend(t)
    d = ImageDraw.Draw(img)
    for kind_i, alpha in ((k, u), (prev, 1 - u)):
        if alpha <= 0.02:
            continue
        kind = ERAS[kind_i][4]
        col = ERAS[kind_i][3]
        for i in range(len(PART["x"])):
            sz, ph, v = PART["s"][i], PART["ph"][i], PART["v"][i]
            # relógio de partícula periódico em DUR -> loop perfeito
            per = DUR / max(1, round(DUR / (6 / v)))
            ft = (t / per + PART["y"][i]) % 1.0
            x = PART["x"][i] * W
            if kind in ("brasa", "bolha"):
                y = H * (1.05 - ft * 1.1)
                x += 25 * math.sin(2 * math.pi * ft * 2 + ph)
            elif kind in ("esporo", "folha"):
                y = H * (ft * 1.1 - 0.05)
                x += 40 * math.sin(2 * math.pi * ft * 3 + ph)
            else:
                y = PART["y"][i] * H
            a = int(255 * alpha * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(2 * math.pi * ft * 4 + ph))))
            r = 2.5 * sz if kind != "bolha" else 6 * sz
            if kind == "bolha":
                d.ellipse((x - r, y - r, x + r, y + r), outline=col + (a,), width=2)
            elif kind == "folha":
                d.ellipse((x - r * 2, y - r, x + r * 2, y + r), fill=col + (a // 2,))
            else:
                d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))


# ---------------------------------------------------------------- ícones (silhuetas com contorno preto)
def silhouette(draw_fn, size, fill, outline=10, shade=None):
    """draw_fn(draw, s) desenha a forma em branco num canvas 2x; devolve RGBA com contorno preto"""
    s2 = size * 2
    m = Image.new("L", (s2, s2), 0)
    draw_fn(ImageDraw.Draw(m), s2)
    edge = m.filter(ImageFilter.MaxFilter(outline * 2 + 1))
    img = Image.new("RGBA", (s2, s2), (0, 0, 0, 0))
    img.paste((0, 0, 0, 255), (0, 0), edge)
    img.paste(fill + (255,), (0, 0), m)
    if shade is not None:
        sm = Image.new("L", (s2, s2), 0)
        shade(ImageDraw.Draw(sm), s2)
        sm = Image.fromarray((np.asarray(sm) * (np.asarray(m) > 0)).astype(np.uint8))
        img.paste(tuple(int(c * 0.72) for c in fill) + (255,), (0, 0), sm)
    return img.resize((size, size), Image.LANCZOS)


def P_(s, pts):
    return [(x * s, y * s) for x, y in pts]


def dino_shape(d, s):
    e = lambda cx, cy, rx, ry: d.ellipse(((cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s), fill=255)
    e(0.47, 0.60, 0.22, 0.12)                                         # corpo
    d.polygon(P_(s, [(0.58, 0.56), (0.66, 0.50), (0.76, 0.30), (0.80, 0.22), (0.86, 0.22), (0.84, 0.30),
                     (0.74, 0.55), (0.66, 0.66)]), fill=255)           # pescoço
    e(0.86, 0.22, 0.06, 0.04)                                         # cabeça
    d.polygon(P_(s, [(0.30, 0.56), (0.12, 0.66), (0.02, 0.74), (0.14, 0.70), (0.32, 0.66)]), fill=255)  # cauda
    for x in (0.33, 0.42, 0.53, 0.62):
        d.rounded_rectangle(((x - 0.035) * s, 0.62 * s, (x + 0.035) * s, 0.86 * s), int(0.02 * s), fill=255)


def human_shape(d, s):
    d.ellipse((0.42 * s, 0.10 * s, 0.58 * s, 0.26 * s), fill=255)
    d.rounded_rectangle((0.38 * s, 0.29 * s, 0.62 * s, 0.60 * s), int(0.06 * s), fill=255)
    d.rounded_rectangle((0.29 * s, 0.30 * s, 0.36 * s, 0.56 * s), int(0.035 * s), fill=255)
    d.rounded_rectangle((0.64 * s, 0.30 * s, 0.71 * s, 0.56 * s), int(0.035 * s), fill=255)
    d.rounded_rectangle((0.40 * s, 0.56 * s, 0.49 * s, 0.90 * s), int(0.04 * s), fill=255)
    d.rounded_rectangle((0.51 * s, 0.56 * s, 0.60 * s, 0.90 * s), int(0.04 * s), fill=255)


def pyr_shape(d, s):
    d.polygon(P_(s, [(0.08, 0.80), (0.30, 0.48), (0.52, 0.80)]), fill=255)
    d.polygon(P_(s, [(0.26, 0.80), (0.56, 0.30), (0.86, 0.80)]), fill=255)
    d.polygon(P_(s, [(0.62, 0.80), (0.78, 0.56), (0.94, 0.80)]), fill=255)


def pyr_shade(d, s):
    d.polygon(P_(s, [(0.30, 0.48), (0.52, 0.80), (0.30, 0.80)]), fill=255)
    d.polygon(P_(s, [(0.56, 0.30), (0.86, 0.80), (0.56, 0.80)]), fill=255)
    d.polygon(P_(s, [(0.78, 0.56), (0.94, 0.80), (0.78, 0.80)]), fill=255)


def plant_shape(d, s):
    d.rounded_rectangle((0.05 * s, 0.82 * s, 0.95 * s, 0.92 * s), int(0.04 * s), fill=255)       # chão
    d.line(P_(s, [(0.5, 0.84), (0.49, 0.6), (0.52, 0.4), (0.5, 0.18)]), fill=255, width=int(0.045 * s), joint="curve")
    for (cx, cy, ang) in [(0.36, 0.62, -30), (0.65, 0.50, 30), (0.37, 0.38, -35), (0.63, 0.26, 35), (0.5, 0.13, 0)]:
        leaf = Image.new("L", (s, s), 0)
        ImageDraw.Draw(leaf).ellipse((0.5 * s - 0.12 * s, 0.5 * s - 0.05 * s, 0.5 * s + 0.12 * s, 0.5 * s + 0.05 * s), fill=255)
        leaf = leaf.rotate(ang, Image.BICUBIC)
        d.bitmap(((cx - 0.5) * s, (cy - 0.5) * s), leaf, fill=255)


ICONS = {}


def build_icons():
    ICONS["dino"] = silhouette(dino_shape, 420, (120, 200, 80))
    ICONS["human"] = silhouette(human_shape, 360, YEL)
    ICONS["pyr"] = silhouette(pyr_shape, 420, (232, 176, 74), shade=pyr_shade)
    ICONS["plant"] = silhouette(plant_shape, 380, (110, 210, 90))


def microbes(t, size=440):
    s2 = size * 2
    img = Image.new("RGBA", (s2, s2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cells = [(0.5, 0.5, 0.17, 0.0), (0.24, 0.36, 0.10, 1.3), (0.78, 0.34, 0.11, 2.1), (0.27, 0.74, 0.09, 3.0),
             (0.75, 0.72, 0.12, 4.2), (0.52, 0.18, 0.07, 5.1)]
    for cx, cy, r, ph in cells:
        cx += 0.015 * math.sin(t * PF(2.0) + ph)
        cy += 0.015 * math.cos(t * PF(1.7) + ph)
        pts, rim = [], []
        for k in range(40):
            th = 2 * math.pi * k / 40
            rr = r * (1 + 0.10 * math.sin(3 * th + t * 4 + ph) + 0.05 * math.sin(5 * th - t * 3))
            pts.append(((cx + rr * math.cos(th) * 1.25) * s2, (cy + rr * math.sin(th)) * s2))
        for k in range(0, 40, 4):          # cílios
            th = 2 * math.pi * k / 40
            x0, y0 = pts[k]
            l = r * 0.35 * s2
            d.line((x0, y0, x0 + math.cos(th + 0.3 * math.sin(t * PF(6) + k)) * l * 1.25,
                    y0 + math.sin(th + 0.3 * math.sin(t * PF(6) + k)) * l), fill=(0, 0, 0, 255), width=10)
            d.line((x0, y0, x0 + math.cos(th + 0.3 * math.sin(t * PF(6) + k)) * l * 1.25,
                    y0 + math.sin(th + 0.3 * math.sin(t * PF(6) + k)) * l), fill=(120, 240, 210, 255), width=5)
        d.polygon(pts, fill=(70, 220, 190, 230), outline=(0, 0, 0, 255), width=12)
        d.ellipse(((cx - r * 0.35) * s2, (cy - r * 0.3) * s2, (cx + r * 0.25) * s2, (cy + r * 0.3) * s2),
                  fill=(20, 110, 120, 255), outline=(0, 0, 0, 255), width=6)
    return img.resize((size, size), Image.LANCZOS)


LAVA_TEX = None


def build_lava():
    global LAVA_TEX
    f = os.path.join(OUT, "lava_tex.npy")
    if os.path.exists(f):
        LAVA_TEX = np.load(f)
        return
    n = Noise(5)
    LAT, LON, x, y, z = sphere_grid(1024, 512)
    a = n.fbm(x * 3, y * 3, z * 3, 5)
    rid = 1 - np.abs(n.fbm(x * 5 + a, y * 5, z * 5, 4) - 0.5) * 2
    lava = np.clip((rid - 0.78) / 0.12, 0, 1)
    crust = ramp(a, [(0, (35, 14, 10)), (0.6, (70, 30, 18)), (1, (110, 50, 25))])
    hot = ramp(lava, [(0, (255, 90, 10)), (0.6, (255, 170, 40)), (1, (255, 240, 150))])
    LAVA_TEX = np.concatenate([crust * (1 - lava[..., None]), (hot * lava[..., None])], -1).astype(np.float32)
    np.save(f, LAVA_TEX)


def lava_planet(canvas, cx, cy, R, t):
    if R < 1:
        return
    ext = R * 1.6
    x0, x1 = int(max(0, cx - ext)), int(min(W, cx + ext))
    y0, y1 = int(max(0, cy - ext)), int(min(H, cy + ext))
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    X, Y = (xs + 0.5 - cx) / R, (ys + 0.5 - cy) / R
    d = np.sqrt(X * X + Y * Y)
    reg = canvas[y0:y1, x0:x1]
    glow = np.exp(-np.maximum(d - 1, 0) * 5) * (d > 0.98) * (0.55 + 0.1 * math.sin(t * PF(3)))
    reg += glow[..., None] * np.array([1.0, 0.45, 0.1], np.float32)
    inside = d < 1 + 1.5 / R
    iy, ix = np.nonzero(inside)
    Xi, Yi = X[iy, ix], Y[iy, ix]
    Zi = np.sqrt(np.clip(1 - Xi * Xi - Yi * Yi, 0, 1))
    lat = np.arcsin(np.clip(-Yi, -1, 1))
    lon = np.arctan2(Xi, Zi)
    u = (lon / (2 * np.pi) + 0.5 + t / DUR) % 1.0
    v = 0.5 - lat / np.pi
    tex = sample(LAVA_TEX, u, v)
    crust, hot = tex[:, :3], tex[:, 3:]
    L = np.array([-0.5, 0.45, 0.74], np.float32)
    ndl = np.clip(Xi * L[0] - Yi * L[1] + Zi * L[2], 0, 1)
    flick = 1 + 0.12 * np.sin(t * 7 + Xi * 9) * np.sin(t * 5 + Yi * 11)
    col = crust * (0.25 + 0.9 * ndl)[:, None] + hot * flick[:, None] * (0.75 + 0.25 * Zi)[:, None]
    col += ((1 - Zi) ** 3 * 0.5)[:, None] * np.array([1.0, 0.5, 0.1], np.float32)
    a = np.clip((1 - d[iy, ix]) * R + 0.5, 0, 1)[:, None]
    reg[iy, ix] = reg[iy, ix] * (1 - a) + np.clip(col, 0, 2) * a


# ---------------------------------------------------------------- relógio
CLOCK_Y = 560
_dig = {}


def glyph(ch, size, color):
    k = (ch, size, color)
    if k not in _dig:
        _dig[k] = rich_text(ch, size, "anton", color=color, stroke=max(6, size // 22))
    return _dig[k]


def draw_digits(frame, txt, cx, cy, size, color, alpha=1.0, glow=True):
    """dígitos com largura fixa (sem tremer)"""
    dw = glyph("0", size, color).width - size * 0.06
    cw = glyph(":", size, color).width - size * 0.08
    widths = [cw if c in ":," else dw for c in txt]
    total = sum(widths)
    x = cx - total / 2
    layer = Image.new("RGBA", (int(total + size), int(size * 1.6)), (0, 0, 0, 0))
    lx = size / 2
    for c, w in zip(txt, widths):
        g = glyph(c, size, color)
        layer.alpha_composite(g, (int(lx + w / 2 - g.width / 2), int(size * 0.8 - g.height / 2)))
        lx += w
    if glow:
        a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(size * 0.12))
        gl = Image.new("RGBA", layer.size, CYAN + (0,))
        gl.putalpha(a.point(lambda v: int(v * 0.85)))
        paste(frame, gl, cx, cy, 1.0, alpha)
    paste(frame, layer, cx, cy, 1.0, alpha)
    return total


def fmt_clock(c, decimals=0):
    c = max(0.0, min(c, DAY - 1e-6))
    h = int(c // 3600)
    m = int((c % 3600) // 60)
    s = c % 60
    if decimals == 0:
        return f"{h:02d}:{m:02d}:{int(s):02d}"
    sec = int(s)
    frac = int((s - sec) * 10 ** decimals)
    return f"{h:02d}:{m:02d}:", f"{sec:02d}", f",{frac:0{decimals}d}"


def slowmo(t):
    """0 = relógio normal, 1 = câmera lenta (zoom nos segundos)"""
    if t >= T_FLIP:
        return 0.0
    return smoother((t - T_SLOW) / 0.45)


def draw_clock(frame, t, shake):
    c = clock(t)
    z = slowmo(t)
    sx, sy = shake
    beat = 1 + 0.025 * math.sin(t * PF(4 * math.pi))
    if T_FLIP <= t < T_FLIP + 0.35:
        beat *= 1 + 0.12 * (1 - (t - T_FLIP) / 0.35)
    if z < 0.02:
        draw_digits(frame, fmt_clock(c), CX + sx, CLOCK_Y + sy, int(236 * beat), WHITE)
        return
    dec = 3 if t >= T_DEC else 2
    pre, sec, frac = fmt_clock(c, dec)
    # HH:MM: encolhe e sobe; segundos crescem
    if z < 1:
        draw_digits(frame, fmt_clock(c), CX + sx, CLOCK_Y - 120 * z + sy, int(236 * (1 - 0.4 * z)), WHITE, clamp(1 - z * 2.2))
    zi = clamp((z - 0.35) / 0.65)
    draw_digits(frame, pre, CX + sx, 425 + sy, 88, (205, 215, 235), zi, glow=False)
    big = int((200 + 80 * zi) * beat)
    fsz = int(big * 0.42)
    wsec = glyph("0", big, YEL).width * 2 - big * 0.12
    wfr = (glyph("0", fsz, WHITE).width - fsz * 0.06) * (dec + 0.5)
    x0 = CX - (wsec + wfr) / 2
    draw_digits(frame, sec, x0 + wsec / 2 + sx, CLOCK_Y + 15 + sy, big, YEL, zi)
    draw_digits(frame, frac, x0 + wsec + wfr / 2 + sx, CLOCK_Y + 15 + big * 0.22 + sy, fsz, WHITE, zi)


# ---------------------------------------------------------------- barra do dia (com zoom)
BAR_Y, BAR_X0, BAR_X1 = 790, 60, 900
SEGS = [(0, hms(3, 55), (255, 110, 30)), (hms(3, 55), hms(21, 31), (60, 170, 255)),
        (hms(21, 31), hms(22, 47), (110, 210, 90)), (hms(22, 47), hms(23, 39), (190, 220, 80)),
        (hms(23, 39), DAY, (170, 110, 255))]
SPANS = [(DAY, "O DIA INTEIRO"), (3600, "ÚLTIMA HORA"), (60, "ÚLTIMO MINUTO"), (1, "ÚLTIMO SEGUNDO")]


def bar_span(t):
    """quanto do fim do dia a barra mostra"""
    if t >= T_FLIP:
        return DAY
    keys = [(T_SLOW, DAY), (T_SLOW + 0.8, 3600), (T_SAP - 0.3, 60), (T_PIR, 60), (T_PIR + 0.6, 1.0)]
    if t <= keys[0][0]:
        return DAY
    for (ta, a), (tb, b) in zip(keys, keys[1:]):
        if t < tb:
            u = smoother((t - ta) / (tb - ta))
            return math.exp(math.log(a) + (math.log(b) - math.log(a)) * u)
    return 1.0


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
    # trecho "história escrita" e "você" no último segundo
    if t >= T_DEC - 0.2 and t < T_FLIP:
        xa = X(DAY - 0.095)
        a = int(255 * clamp((t - T_DEC + 0.2) / 0.3))
        d.rectangle((xa, BAR_Y - h / 2 - 4, BAR_X1, BAR_Y + h / 2 + 4), outline=YEL + (a,), width=5)
    ph = X(c)
    d.ellipse((ph - 16, BAR_Y - 16, ph + 16, BAR_Y + 16), fill=WHITE + (255,), outline=(0, 0, 0, 255), width=4)
    # rótulos
    lab = SPANS[0][1]
    for sp, name in SPANS:
        if span <= sp * 1.4:
            lab = name
    paste(frame, rich_text(lab, 34, color=CYAN), CX, BAR_Y - 52)
    ltxt = fmt_clock(L) if span > 59 else fmt_clock(L) if span > 2 else "23:59:59"
    paste(frame, rich_text(ltxt, 28), BAR_X0 + 70, BAR_Y + 44)
    if not (T_YOU - 0.1 <= t < T_FLIP):
        paste(frame, rich_text("24:00:00", 28), BAR_X1 - 70, BAR_Y + 44)


# ---------------------------------------------------------------- cena
ICON_Y = 1150


def shake(t):
    dt = t - T_BOOM
    if 0 <= dt < 1.1:
        a = 40 * math.exp(-dt * 4.5)
        return a * math.sin(dt * 73) * math.cos(dt * 11), a * math.sin(dt * 51 + 1.1)
    return 0.0, 0.0


def flash(t):
    f = 0.0
    if T_BOOM - 0.03 <= t < T_BOOM + 0.55:
        f = 1.0 if t < T_BOOM + 0.06 else 1 - smoother((t - T_BOOM - 0.06) / 0.5)
    if T_FLIP - 0.03 <= t < T_FLIP + 0.5:
        f = max(f, 0.95 if t < T_FLIP + 0.05 else 0.95 * (1 - smoother((t - T_FLIP - 0.05) / 0.45)))
    return f


def icon_env(t, a, b, d_in=0.35, d_out=0.25):
    """escala de entrada/saída de um ícone"""
    if t < a or t >= b:
        return 0.0
    sc = ease_out_back(clamp((t - a) / d_in), 2.0)
    out = clamp((b - t) / d_out)
    return sc * (0.4 + 0.6 * out) if out < 1 else sc


def lava_scale(t):
    if t < T_VIDA - 0.2:
        return 1.0
    if t >= T_FLIP:
        return ease_out_back(clamp((t - T_FLIP - 0.05) / 0.4), 2.0)
    return clamp((T_VIDA - t) / 0.2) if t < T_VIDA else 0.0


def world(t):
    bg = background(t)
    sx, sy = shake(t)
    ls = lava_scale(t)
    if ls > 0:
        bob = 8 * math.sin(t * 2 * math.pi / DUR * 6)
        lava_planet(bg, CX + sx, ICON_Y + sy + bob, 190 * ls, t)
    return bg


def asteroid(frame, t, sx, sy):
    a, b = S["asteroide"] - 0.1, T_BOOM
    if not (a <= t < b):
        return
    u = (t - a) / (b - a)
    e = u ** 1.6
    x0, y0, x1, y1 = 1130, 880, CX + 30, ICON_Y - 20
    x, y = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    d = ImageDraw.Draw(frame)
    ang = math.atan2(y1 - y0, x1 - x0)
    for k in range(26, 0, -1):          # rastro de fogo
        tx, ty = x - math.cos(ang) * k * 16 * (0.4 + e), y - math.sin(ang) * k * 16 * (0.4 + e)
        r = 46 * (1 - k / 30) * (0.6 + 0.4 * e)
        col = (255, int(120 + 100 * (1 - k / 26)), 40, int(200 * (1 - k / 26)))
        d.ellipse((tx - r, ty - r, tx + r, ty + r), fill=col)
    r = 34 + 22 * e
    pts = [(x + r * (1 + 0.18 * math.sin(i * 2.3)) * math.cos(i * 0.785), y + r * (1 + 0.18 * math.sin(i * 2.3)) * math.sin(i * 0.785))
           for i in range(8)]
    d.polygon(pts, fill=(110, 90, 80, 255), outline=(0, 0, 0, 255), width=6)


def impact(frame, t):
    dt = t - T_BOOM
    if not (0 <= dt < 1.1):
        return
    d = ImageDraw.Draw(frame)
    r = 60 + 900 * ease_out_cubic(dt / 1.0)
    a = int(255 * clamp(1 - dt / 1.0))
    d.ellipse((CX - r, ICON_Y - r * 0.55, CX + r, ICON_Y + r * 0.55), outline=(255, 220, 140, a), width=14)
    rng = np.random.default_rng(3)
    for i in range(22):           # poeira
        ang = rng.uniform(math.pi, 2 * math.pi)
        sp = rng.uniform(150, 520)
        x = CX + math.cos(ang) * sp * ease_out_cubic(dt / 1.4) * 1.3
        y = ICON_Y + 120 + math.sin(ang) * sp * ease_out_cubic(dt / 1.4) * 0.7
        rr = rng.uniform(12, 30) * (1 + dt)
        al = int(120 * clamp(1 - dt / 1.1))
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(120, 100, 110, al))


def era_label(frame, t, title, years, a, b):
    if not (a <= t < b):
        return
    al = clamp((b - t) / 0.15)
    paste(frame, rich_text(title, 54, maxw=920), CX, 1385, pop(t, a), al)
    paste(frame, pill(years, 36), CX, 1462, pop(t, a + 0.08), al)


_cache = {}


def pill(text, size=40, fg=NAVY, bg=CYAN):
    k = ("pill", text, size, bg)
    if k not in _cache:
        f = font("mont", size)
        tl = int(f.getlength(text))
        img = rounded_panel(tl + 44, size + 30, bg + (255,), (size + 30) // 2, outline=(0, 0, 0, 255), ow=4)
        ImageDraw.Draw(img).text((22, 12), text, font=f, fill=fg)
        _cache[k] = img
    return _cache[k]


def final_card():
    if "card" not in _cache:
        a = rich_text("A SUA VIDA INTEIRA DURA", 54, maxw=820)
        b = rich_text("0,0015 SEGUNDO", 128, "anton", color=YEL, stroke=10)
        c = rich_text("NESSE RELÓGIO", 54, maxw=820)
        pw, ph = 860, a.height + b.height + c.height + 40
        img = rounded_panel(pw, ph, NAVY + (225,), 44, outline=YEL + (255,), ow=6)
        y = 18
        for im in (a, b, c):
            img.alpha_composite(im, ((pw - im.width) // 2, y))
            y += im.height
        _cache["card"] = img
    return _cache["card"]


def ui(frame, t):
    sx, sy = shake(t)
    d = ImageDraw.Draw(frame)
    # ícones
    e = icon_env(t, T_VIDA, T_PLANT)
    if e > 0:
        paste(frame, microbes(t), CX + sx, ICON_Y + sy, e)
    e = icon_env(t, T_PLANT, T_DINO)
    if e > 0:
        paste(frame, ICONS["plant"], CX + sx, ICON_Y + sy - 10, e * (1 + 0.03 * math.sin(t * PF(5))), rot=3 * math.sin(t * PF(3)))
    if T_DINO <= t < T_BOOM:
        e = icon_env(t, T_DINO, T_BOOM + 1, 0.35)
        walk = 18 * math.sin(t * PF(6))
        paste(frame, ICONS["dino"], CX - 30 + sx + walk, ICON_Y + sy, e, rot=2 * math.sin(t * PF(6)))
        paste(frame, ICONS["dino"].transpose(Image.FLIP_LEFT_RIGHT), CX + 230 + sx - walk * 0.6, ICON_Y + 70 + sy, e * 0.5)
    asteroid(frame, t, sx, sy)
    impact(frame, t)
    e = icon_env(t, T_SAP, T_CARD)
    if e > 0:
        bob = 6 * math.sin(t * PF(4))
        paste(frame, ICONS["human"], CX - (110 if t >= T_PIR else 0) + sx, ICON_Y + sy + bob, e)
    e = icon_env(t, T_PIR, T_CARD)
    if e > 0:
        paste(frame, ICONS["pyr"], CX + 150, ICON_Y + 40, e * 0.8)
    # rótulos de era
    era_label(frame, t, "TERRA EM *LAVA*", "4,5 BILHÕES DE ANOS ATRÁS", S["lava"] + 0.2, T_VIDA - 0.05)
    era_label(frame, t, "PRIMEIRA *VIDA*", "3,8 BILHÕES DE ANOS ATRÁS", T_VIDA + 0.15, T_PLANT - 0.05)
    era_label(frame, t, "PLANTAS EM *TERRA FIRME*", "470 MILHÕES DE ANOS ATRÁS", T_PLANT + 0.15, T_DINO - 0.05)
    era_label(frame, t, "*DINOSSAUROS*", "230 MILHÕES DE ANOS ATRÁS", T_DINO + 0.15, S["asteroide"] - 0.05)
    era_label(frame, t, "O *ASTEROIDE*", "66 MILHÕES DE ANOS ATRÁS", S["asteroide"], T_SLOW + 0.4)
    era_label(frame, t, "*HOMO SAPIENS*", "300 MIL ANOS ATRÁS", T_SAP + 0.15, T_PIR - 0.05)
    era_label(frame, t, "TODA A *HISTÓRIA ESCRITA*", "5 MIL ANOS = 0,1 SEGUNDO", T_PIR + 0.1, T_CARD - 0.05)
    # textos do topo
    if t < S["lava"] + 0.1:
        paste(frame, rich_text("VOCÊ SÓ APARECE NOS *ÚLTIMOS SEGUNDOS*", 76, maxw=880), CX, 215,
              1 + 0.02 * math.sin(t * PF(5)), clamp((S["lava"] + 0.1 - t) / 0.12))
    if t >= T_FLIP + 0.3:
        u = clamp((t - T_FLIP - 0.3) / 0.4)
        sc = 0.55 + 0.45 * ease_out_back(u, 2.0) if u < 1 else 1.0
        paste(frame, rich_text("VOCÊ SÓ APARECE NOS *ÚLTIMOS SEGUNDOS*", 76, maxw=880), CX, 215, sc, clamp(u * 3))
    if S["humanos"] - 0.1 <= t < T_SAP + 0.1:
        paste(frame, rich_text("E OS *HUMANOS?*", 96, maxw=880), CX, 215, pop(t, S["humanos"] - 0.1),
              clamp((T_SAP + 0.1 - t) / 0.12))
    if T_SLOW <= t < T_CARD:
        al = clamp((t - T_SLOW) / 0.3) * clamp((T_CARD - t) / 0.2)
        paste(frame, pill("CÂMERA LENTA", 32, bg=YEL), CX, 318, 1 + 0.04 * math.sin(t * PF(8)), al)
    # cartão final + CTA
    if T_CARD <= t < T_FLIP:
        al = clamp((T_FLIP - t) / 0.1)
        e2 = ease_out_back(clamp((t - T_CARD) / 0.35), 1.8)
        paste(frame, final_card(), CX, 1160, (0.8 + 0.2 * e2) * (1 + 0.012 * math.sin(t * PF(5))), al)
        # "VOCÊ" na ponta da barra
        if t >= T_YOU - 0.1:
            sc = pop(t, T_YOU - 0.1)
            paste(frame, rich_text("*VOCÊ*", 48, maxw=300), BAR_X1 - 50, BAR_Y + 100, sc, al)
            d.polygon([(BAR_X1 - 12, BAR_Y + 26), (BAR_X1 + 2, BAR_Y + 54), (BAR_X1 - 26, BAR_Y + 54)],
                      fill=YEL + (int(255 * al),), outline=(0, 0, 0, 255))
    if T_CTA <= t < T_FLIP:
        al = clamp((T_FLIP - t) / 0.1)
        paste(frame, rich_text("PERA, OI?", 120, "anton", color=YEL, stroke=10), CX, 215,
              pop(t, T_CTA) * (1 + 0.03 * math.sin(t * PF(7))), al)
        tq = word_t("cta", "qual") - 0.05
        if t >= tq:
            paste(frame, rich_text("QUAL OUTRA *ESCALA* EU FAÇO?", 48, maxw=940), CX, 1450, pop(t, tq), al)
    caption(frame, t)


# ---------------------------------------------------------------- legendas
CHUNKS = []


def build_chunks():
    CHUNKS.clear()
    cur, line = [], None
    for w in P["words"]:
        if w["line"] in ("hook", "cta"):
            continue
        if cur and (w["line"] != line or len(cur) >= 3 or sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > 16):
            CHUNKS.append(cur); cur = []
        cur.append(w); line = w["line"]
    if cur:
        CHUNKS.append(cur)


def caption(frame, t):
    for ci, ch in enumerate(CHUNKS):
        a = ch[0]["t"] - 0.05
        b = ch[-1]["t"] + ch[-1]["d"] + 0.15
        if ci + 1 < len(CHUNKS) and CHUNKS[ci + 1][0]["line"] == ch[0]["line"]:
            b = min(b, CHUNKS[ci + 1][0]["t"] - 0.05)
        if a <= t < b:
            parts = []
            for w in ch:
                txt = w["w"].upper().strip(",.!?:;…")
                act = w["t"] - 0.03 <= t < w["t"] + w["d"] + 0.03 or (w is ch[-1] and t >= w["t"])
                parts.append(f"*{txt}*" if act else txt)
            img = rich_text(" ".join(parts), 60, maxw=900)
            paste(frame, img, CX, 1550, 0.82 + 0.18 * ease_out_back(clamp((t - a) / 0.16), 2.0))
            return


# ---------------------------------------------------------------- render
def init():
    E.init()
    build_lava()
    build_icons()
    build_chunks()


def render_frame(f):
    t = f / FPS
    bg = world(t) * VIG
    if slowmo(t) > 0:   # câmera lenta: menos saturação, tom frio
        z = slowmo(t) * 0.35
        g = bg.mean(2, keepdims=True)
        bg = bg * (1 - z) + (g * np.array([0.85, 0.95, 1.15], np.float32)) * z
    img = Image.fromarray((np.clip(bg, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    particles(img, t)
    draw_clock(img, t, shake(t))
    draw_bar(img, t)
    ui(img, t)
    fl = flash(t)
    if fl > 0:
        img = Image.blend(img, Image.new("RGBA", img.size, (255, 255, 255, 255)), fl)
    return img.convert("RGB")


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
    return dict(eras=[T_VIDA, T_PLANT, T_DINO], boom=T_BOOM, slow=T_SLOW, sap=T_SAP, pir=T_PIR, dec=T_DEC,
                you=T_YOU, card=T_CARD, cta=T_CTA, flip=T_FLIP, ast=S["asteroide"] - 0.1,
                pops=[T_VIDA, T_PLANT, T_DINO, T_SAP, T_PIR, T_YOU - 0.1, word_t("cta", "qual") - 0.05])


def main():
    os.makedirs(OUT, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "times":
        for k, v in sorted(dict(T_VIDA=T_VIDA, T_PLANT=T_PLANT, T_DINO=T_DINO, T_BOOM=T_BOOM, T_SLOW=T_SLOW,
                                T_SAP=T_SAP, T_PIR=T_PIR, T_DEC=T_DEC, T_YOU=T_YOU, T_CARD=T_CARD, T_CTA=T_CTA,
                                T_FLIP=T_FLIP, DUR=DUR).items(), key=lambda x: x[1]):
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
                dd.line((SAFE_R, 0, SAFE_R, H), fill=(255, 0, 0), width=2)
                dd.line((0, H - 300, W, H - 300), fill=(255, 0, 0), width=2)
            im.save(os.path.join(pd, f"f{f:04d}.png"))
        print("ok")
    elif cmd == "video":
        from multiprocessing import Pool
        init()
        nw = int(os.environ.get("WORKERS", os.cpu_count() or 4))
        step = math.ceil(NFRAMES / (nw * 3))
        jobs = [(i, min(NFRAMES, i + step), os.path.join(OUT, f"seg{k:02d}.mp4"))
                for k, i in enumerate(range(0, NFRAMES, step))]
        with Pool(nw) as pool:
            segs = pool.map(render_range, jobs, chunksize=1)
        open(os.path.join(OUT, "segs.txt"), "w").write("".join(f"file '{s}'\n" for s in segs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "segs.txt"),
                        "-c", "copy", os.path.join(OUT, "video_mudo.mp4")], check=True)
        print("video ok")


if __name__ == "__main__":
    main()
