"""PERA, OI? — O QUE ACONTECE COM VOCÊ NOS PRÓXIMOS 60 SEGUNDOS
1080x1920, 30 fps, exatamente 60 s (cronômetro real), loop perfeito.

  python render.py times | preview 0 5.2 ... | video
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "planetas"))
import engine as E
from engine import (W, H, FPS, clamp, smoother, ease_out_cubic, ease_out_back, rich_text, paste, pop,
                    rounded_panel, font, sample)
import plan as PL

OUT = os.path.join(HERE, "out")
NARR = os.environ.get("NARR", os.path.join(OUT, "narr"))
P = PL.build_fixed(NARR, 60.0, 59.25)
S, EN = P["S"], P["E"]
DUR, NFRAMES, T_LOOP = P["DUR"], P["NFRAMES"], P["T_LOOP"]

CX = W / 2
MAXW = 840
NAVY = (10, 14, 38)
YEL = (255, 214, 60)
CYAN = (60, 210, 255)
RED = (255, 64, 88)
WHITE = (255, 255, 255)


def PF(w):
    return 2 * math.pi * max(1, round(w * DUR / (2 * math.pi))) / DUR


def osc(t, w, ph=0.0):
    return math.sin(t * PF(w) + ph)


def word_t(line, frag, which="t"):
    frag = frag.lower()
    for w in P["words"]:
        if w["line"] == line and frag in w["w"].lower():
            return w["t"] + (w["d"] if which == "end" else 0.0)
    return (S[line] + EN[line]) / 2


# ---------------------------------------------------------------- eventos "reais"
def beat_times():
    """coração ~68 -> 77 bpm (acelerando)"""
    out, t = [], 0.35
    while t < DUR + 1:
        out.append(t)
        bpm = 68 + 9 * min(t, 55) / 55
        t += 60 / bpm
    return out


BEATS = beat_times()
BEATS_X = [b - DUR for b in BEATS if DUR - 3.5 < b < DUR] + BEATS   # continua do fim -> loop
BLINKS = [1.9, 5.2, 8.1, 11.6, 15.0, 18.3, 21.2, 25.0, 28.7, 31.9, 35.2, 39.0, 42.4, 45.9, 49.1, 52.8]
BREATH_P = 4.0
T_BOOM = word_t("sofa", "sofá") + 0.1
T_CTA = S["cta"]


def count_events(ev, t):
    tt = min(t, T_BOOM)
    return sum(1 for e in ev if e <= tt)


def beat_env(t):
    """pulso do coração (0..1) no instante t"""
    v = 0.0
    for b in BEATS_X:
        dt = t - b
        if -0.05 < dt < 0.6:
            v = max(v, math.exp(-max(dt, 0) * 9) + 0.55 * math.exp(-max(dt - 0.18, 0) * 11) * (dt > 0.18))
    return min(v, 1.0)


def ft(t):
    return min(t, T_BOOM)


ORDER = ["coracao", "piscadas", "respira", "celulas", "raios", "bebes", "rotacao", "orbita", "sol", "galaxia"]
STATS = {
    "coracao": dict(head="SEU CORAÇÃO *BATEU*", row="BATIMENTOS", col=RED, val=lambda t: count_events(BEATS, t),
                    fmt="int", pill="~70 POR MINUTO"),
    "piscadas": dict(head="VOCÊ *PISCOU*", row="PISCADAS", col=CYAN, val=lambda t: count_events(BLINKS, t),
                     fmt="int", pill="~16 POR MINUTO"),
    "respira": dict(head="VOCÊ *RESPIROU*", row="RESPIRAÇÕES", col=(120, 200, 255),
                    val=lambda t: int((ft(t) + 1.0) // BREATH_P), fmt="int", pill="~15 POR MINUTO"),
    "celulas": dict(head="CÉLULAS *TROCADAS*", row="CÉLULAS NOVAS", col=(90, 230, 140), val=lambda t: 3.8e6 * ft(t),
                    fmt="int", pill="3,8 MILHÕES POR SEGUNDO"),
    "raios": dict(head="RAIOS NO *MUNDO*", row="RAIOS NA TERRA", col=YEL, val=lambda t: 44 * ft(t), fmt="int",
                  pill="44 POR SEGUNDO"),
    "bebes": dict(head="BEBÊS *NASCERAM*", row="BEBÊS NASCIDOS", col=(255, 140, 200), val=lambda t: 4.3 * ft(t),
                  fmt="int", pill="4,3 POR SEGUNDO"),
    "rotacao": dict(head="A TERRA *TE GIROU*", row="GIRO DA TERRA", col=(60, 230, 200), val=lambda t: 0.426 * ft(t),
                    fmt="km1", pill="1.530 KM/H NO BRASIL"),
    "orbita": dict(head="VOLTA *EM TORNO DO SOL*", row="ÓRBITA DO SOL", col=(80, 160, 255),
                   val=lambda t: 29.8 * ft(t), fmt="km", pill="30 KM POR SEGUNDO"),
    "sol": dict(head="VIAGEM *PELA GALÁXIA*", row="VIAGEM NA GALÁXIA", col=(255, 160, 60),
                val=lambda t: 230 * ft(t), fmt="km", pill="230 KM POR SEGUNDO"),
    "galaxia": dict(head="A VIA LÁCTEA *VOOU*", row="VIA LÁCTEA", col=(190, 120, 255), val=lambda t: 600 * ft(t),
                    fmt="km", pill="600 KM POR SEGUNDO"),
}


def fmt_val(v, fmt):
    if fmt == "km1":
        return f"{v:.1f}".replace(".", ",") + " KM"
    s = f"{int(v):,}".replace(",", ".")
    return s + (" KM" if fmt == "km" else "")


def hero_window(k):
    i = ORDER.index(k)
    a = S[k] - 0.15
    b = S[ORDER[i + 1]] - 0.15 if i + 1 < len(ORDER) else S["sofa"] - 0.1
    return a, b


# ---------------------------------------------------------------- fundo HUD
YY = np.linspace(0, 1, H, dtype=np.float32)[:, None]
XX = np.linspace(0, 1, W, dtype=np.float32)[None, :]
BASE = None
VIG = np.clip(1 - 0.8 * np.clip(np.sqrt((XX - 0.5) ** 2 * 1.2 + (YY - 0.5) ** 2) - 0.3, 0, 1) ** 1.3, 0, 1)[..., None]


def build_base():
    global BASE
    top, bot = np.array(NAVY, np.float32) / 255, np.array((18, 30, 78), np.float32) / 255
    img = top + (bot - top) * YY[..., None]
    img = np.broadcast_to(img, (H, W, 3)).copy()
    grid = ((np.arange(W) % 60) == 0)[None, :] | ((np.arange(H) % 60) == 0)[:, None]
    img[grid] += np.array([0.05, 0.12, 0.18], np.float32)
    BASE = img


RNG = np.random.default_rng(3)
NP_ = 70
PART = dict(x=RNG.random(NP_), y=RNG.random(NP_), s=RNG.uniform(0.6, 1.8, NP_), ph=RNG.uniform(0, 6.28, NP_),
            v=RNG.uniform(0.5, 1.5, NP_))


def background(t):
    img = BASE.copy()
    hue = np.array([0.25, 0.05, 0.12], np.float32) * beat_env(t) * 0.35     # pulso vermelho sutil
    rad = np.exp(-(((XX - 0.5) * 1.3) ** 2 + ((YY - 0.33) * 1.6) ** 2) / 0.08)
    img += (rad[..., None] * (np.array([0.05, 0.18, 0.30], np.float32) * (0.8 + 0.2 * osc(t, 1.3)) + hue))
    sy = int((t / DUR * 4 % 1) * H)                                          # linha de varredura
    img[max(0, sy - 3):sy + 3] += np.array([0.05, 0.15, 0.2], np.float32)
    return img * VIG


def particles(frame, t):
    d = ImageDraw.Draw(frame)
    for n in range(NP_):
        per = DUR / max(1, round(DUR / (9 / PART["v"][n])))
        f = (t / per + PART["y"][n]) % 1.0
        x = PART["x"][n] * W + 20 * math.sin(2 * math.pi * f * 2 + PART["ph"][n])
        y = H * (1.05 - f * 1.1)
        r = 2.2 * PART["s"][n]
        a = int(160 * (0.4 + 0.6 * abs(math.sin(2 * math.pi * f * 3 + PART["ph"][n]))))
        d.ellipse((x - r, y - r, x + r, y + r), fill=CYAN + (a,))


# ---------------------------------------------------------------- ícones vetoriais (supersample 3x)
SS = 3


def canvas(size):
    s = size * SS
    return Image.new("RGBA", (s, s), (0, 0, 0, 0)), s


def finish(img, size):
    return img.resize((size, size), Image.LANCZOS)


def heart_pts(s, sc=1.0):
    pts = []
    for k in range(80):
        a = 2 * math.pi * k / 80
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((s / 2 + x * s / 38 * sc, s / 2 - y * s / 38 * sc - s * 0.03))
    return pts


def icon_heart(size, pulse=0.0):
    img, s = canvas(size)
    d = ImageDraw.Draw(img)
    sc = 1 + 0.16 * pulse
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon(heart_pts(s, sc * 1.08), fill=RED + (int(140 + 100 * pulse),))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(s * 0.05)))
    d.polygon(heart_pts(s, sc), fill=(0, 0, 0, 255))
    d.polygon(heart_pts(s, sc * 0.93), fill=(220, 30, 60, 255))
    d.polygon(heart_pts(s, sc * 0.72), fill=(255, 70, 95, 255))
    d.ellipse((s * 0.30, s * 0.28, s * 0.42, s * 0.38), fill=(255, 200, 210, 200))
    return finish(img, size)


def icon_eye(size, lid=0.0, look=0.0):
    img, s = canvas(size)
    d = ImageDraw.Draw(img)
    top = [(s * (0.08 + 0.84 * k / 30), s * 0.5 - s * 0.30 * math.sin(math.pi * k / 30)) for k in range(31)]
    bot = [(s * (0.92 - 0.84 * k / 30), s * 0.5 + s * 0.26 * math.sin(math.pi * k / 30)) for k in range(31)]
    d.polygon(top + bot, fill=(0, 0, 0, 255))
    inner = [(x, s * 0.5 + (y - s * 0.5) * 0.88) for x, y in top + bot]
    d.polygon(inner, fill=(240, 248, 255, 255))
    ix = s * (0.5 + 0.08 * look)
    d.ellipse((ix - s * 0.17, s * 0.33, ix + s * 0.17, s * 0.67), fill=(30, 140, 200, 255), outline=(0, 0, 0, 255), width=SS * 3)
    d.ellipse((ix - s * 0.08, s * 0.42, ix + s * 0.08, s * 0.58), fill=(5, 10, 20, 255))
    d.ellipse((ix - s * 0.11, s * 0.37, ix - s * 0.04, s * 0.44), fill=(255, 255, 255, 230))
    if lid > 0:   # pálpebra descendo
        ly = s * (0.18 + 0.36 * lid)
        lidp = [(x, min(y + (ly - s * 0.18) * 1.2, s * 0.5 + (y - s * 0.5) * (1 - lid))) for x, y in top]
        d.polygon(top + lidp[::-1], fill=(60, 120, 170, 255))
        d.line(lidp, fill=(0, 0, 0, 255), width=SS * 4)
    d.line(top, fill=(0, 0, 0, 255), width=SS * 5)
    return finish(img, size)


def icon_lungs(size, breath=0.0):
    img, s = canvas(size)
    d = ImageDraw.Draw(img)
    sc = 0.9 + 0.12 * breath
    for sgn in (-1, 1):
        cx = s / 2 + sgn * s * 0.17
        pts = []
        for k in range(40):
            a = 2 * math.pi * k / 40
            rx, ry = s * 0.17 * sc, s * 0.30 * sc
            x = math.cos(a) * rx * (1 + 0.25 * math.sin(a) * sgn * -1)
            y = math.sin(a) * ry
            pts.append((cx + x, s * 0.56 + y))
        d.polygon(pts, fill=(0, 0, 0, 255))
        d.polygon([(cx + (x - cx) * 0.9, s * 0.56 + (y - s * 0.56) * 0.92) for x, y in pts], fill=(255, 130, 150, 255))
        d.polygon([(cx + (x - cx) * 0.6 - sgn * s * 0.02, s * 0.52 + (y - s * 0.56) * 0.6) for x, y in pts], fill=(255, 175, 185, 255))
    d.line((s / 2, s * 0.10, s / 2, s * 0.42), fill=(0, 0, 0, 255), width=SS * 14)
    d.line((s / 2, s * 0.10, s / 2, s * 0.42), fill=(230, 230, 240, 255), width=SS * 7)
    for sgn in (-1, 1):
        d.line((s / 2, s * 0.40, s / 2 + sgn * s * 0.13, s * 0.52), fill=(0, 0, 0, 255), width=SS * 11)
        d.line((s / 2, s * 0.40, s / 2 + sgn * s * 0.13, s * 0.52), fill=(230, 230, 240, 255), width=SS * 5)
    return finish(img, size)


def icon_cell(size, ph=0.0):
    """célula em mitose: alonga e divide (ph 0..1 cíclico)"""
    img, s = canvas(size)
    d = ImageDraw.Draw(img)
    split = smoother(clamp((ph - 0.35) / 0.5))
    stretch = math.sin(math.pi * clamp(ph / 0.85)) * 0.25
    for sgn in ((-1, 1) if split > 0.02 else (0,)):
        off = sgn * s * (0.05 + 0.16 * split)
        rx = s * (0.30 + stretch * 0.3) * (1 - 0.32 * split)
        ry = s * 0.30 * (1 - 0.25 * split)
        cx = s / 2 + off
        d.ellipse((cx - rx, s / 2 - ry, cx + rx, s / 2 + ry), fill=(0, 0, 0, 255))
        d.ellipse((cx - rx * 0.92, s / 2 - ry * 0.92, cx + rx * 0.92, s / 2 + ry * 0.92), fill=(90, 230, 140, 200))
        d.ellipse((cx - rx * 0.35, s / 2 - ry * 0.35, cx + rx * 0.35, s / 2 + ry * 0.35), fill=(20, 110, 70, 255), outline=(0, 0, 0, 255), width=SS * 3)
        for k in range(6):
            a = k * 1.05 + ph * 6
            d.ellipse((cx + math.cos(a) * rx * 0.6 - s * 0.02, s / 2 + math.sin(a) * ry * 0.6 - s * 0.02,
                       cx + math.cos(a) * rx * 0.6 + s * 0.02, s / 2 + math.sin(a) * ry * 0.6 + s * 0.02), fill=(200, 255, 220, 220))
    return finish(img, size)


def icon_bolt(size, flick=1.0):
    img, s = canvas(size)
    pts = [(0.58, 0.04), (0.22, 0.56), (0.46, 0.56), (0.36, 0.96), (0.80, 0.40), (0.54, 0.40), (0.68, 0.04)]
    P_ = [(x * s, y * s) for x, y in pts]
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon(P_, fill=YEL + (int(220 * flick),))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(s * 0.06)))
    d = ImageDraw.Draw(img)
    d.polygon(P_, fill=(255, 235, 120, 255), outline=(0, 0, 0, 255), width=SS * 5)
    return finish(img, size)


def icon_baby(size, wob=0.0):
    img, s = canvas(size)
    d = ImageDraw.Draw(img)
    a = wob * 6
    body = [(s * 0.5 + s * 0.24 * math.cos(k / 20 * 2 * math.pi) * (1 - 0.25 * math.sin(k / 20 * 2 * math.pi)),
             s * 0.68 + s * 0.26 * math.sin(k / 20 * 2 * math.pi)) for k in range(20)]
    d.polygon(body, fill=(255, 170, 210, 255), outline=(0, 0, 0, 255), width=SS * 5)
    d.arc((s * 0.30, s * 0.48, s * 0.70, s * 0.80), 200, 340, fill=(255, 230, 240, 255), width=SS * 6)
    d.ellipse((s * 0.31, s * 0.14, s * 0.69, s * 0.52), fill=(255, 215, 180, 255), outline=(0, 0, 0, 255), width=SS * 5)
    d.arc((s * 0.44, s * 0.08, s * 0.58, s * 0.24), 180 + a, 360 + a, fill=(0, 0, 0, 255), width=SS * 5)
    d.arc((s * 0.38, s * 0.30, s * 0.47, s * 0.36), 0, 180, fill=(0, 0, 0, 255), width=SS * 4)
    d.arc((s * 0.53, s * 0.30, s * 0.62, s * 0.36), 0, 180, fill=(0, 0, 0, 255), width=SS * 4)
    d.ellipse((s * 0.45, s * 0.39, s * 0.55, s * 0.46), fill=(255, 140, 200, 255), outline=(0, 0, 0, 255), width=SS * 3)
    return finish(img, size)


def globe_rgba(R, t, pin=False):
    """Terra 3D (textura do motor dos planetas), com pino 'VOCÊ' no Brasil"""
    n = int(2 * R + 4)
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    X, Y = (xs + 0.5 - n / 2) / R, (ys + 0.5 - n / 2) / R
    d = np.sqrt(X * X + Y * Y)
    Z = np.sqrt(np.clip(1 - d * d, 0, 1))
    tilt = 0.4
    bx = X * math.cos(tilt) + Y * math.sin(tilt)
    by = -(-X * math.sin(tilt) + Y * math.cos(tilt))
    lat = np.arcsin(np.clip(by, -1, 1))
    lon = np.arctan2(bx, np.maximum(Z, 1e-4))
    spin = 3 * t / DUR
    u = (lon / (2 * np.pi) + 0.5 + spin) % 1.0
    v = 0.5 - lat / np.pi
    col = sample(E.TEX["TERRA"], u, v)
    cl = sample(E.TEX["TERRA_cl"], (u + 0.02) % 1, v)
    col = col * (1 - cl[..., None]) + 0.96 * cl[..., None]
    L = np.array([-0.5, 0.45, 0.74], np.float32)
    ndl = np.clip(X * L[0] - Y * L[1] + Z * L[2], 0, 1)
    col = col * (0.12 + 0.88 * ndl)[..., None] + ((1 - Z) ** 3 * 0.6)[..., None] * np.array([0.3, 0.6, 1.0], np.float32)
    a = np.clip((1 - d) * R + 0.5, 0, 1)
    rgba = np.dstack([np.clip(col, 0, 1) * 255, a * 255]).astype(np.uint8)
    img = Image.fromarray(rgba, "RGBA")
    if pin:    # um ponto fixo da superfície (Brasil-ish) girando junto
        plon = (-0.12 - spin) * 2 * math.pi
        plat = -0.3
        px, py, pz = math.cos(plat) * math.sin(plon), math.sin(plat), math.cos(plat) * math.cos(plon)
        if pz > 0:
            sx = px * math.cos(tilt) - (-py) * math.sin(tilt)
            sy = px * math.sin(tilt) + (-py) * math.cos(tilt)
            gx, gy = n / 2 + sx * R, n / 2 + sy * R
            dd = ImageDraw.Draw(img)
            dd.ellipse((gx - 9, gy - 9, gx + 9, gy + 9), fill=YEL + (255,), outline=(0, 0, 0, 255), width=3)
    return img


def icon_orbit(size, t):
    img, s = canvas(size)
    d = ImageDraw.Draw(img)
    cx, cy = s / 2, s / 2
    rx, ry = s * 0.42, s * 0.20
    for k in range(48):
        if k % 2 == 0:
            a0, a1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 1) / 48
            d.line((cx + rx * math.cos(a0), cy + ry * math.sin(a0), cx + rx * math.cos(a1), cy + ry * math.sin(a1)),
                   fill=(150, 200, 255, 200), width=SS * 3)
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - s * 0.16, cy - s * 0.16, cx + s * 0.16, cy + s * 0.16), fill=(255, 180, 60, 230))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(s * 0.05)))
    d.ellipse((cx - s * 0.10, cy - s * 0.10, cx + s * 0.10, cy + s * 0.10), fill=(255, 220, 90, 255), outline=(0, 0, 0, 255), width=SS * 3)
    a = t * PF(2 * math.pi / 6)
    for k in range(12, 0, -1):   # rastro
        aa = a - k * 0.06
        x, y = cx + rx * math.cos(aa), cy + ry * math.sin(aa)
        r = s * 0.03 * (1 - k / 14)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(80, 160, 255, int(200 * (1 - k / 12))))
    x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
    d.ellipse((x - s * 0.05, y - s * 0.05, x + s * 0.05, y + s * 0.05), fill=(60, 140, 255, 255), outline=(0, 0, 0, 255), width=SS * 3)
    return finish(img, size)


GALAXY = None


def build_galaxy(size=300):
    global GALAXY
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(5)
    for arm in range(2):
        for k in range(900):
            th = rng.random() * 4.2
            r = s * 0.04 * math.exp(0.42 * th) + rng.normal() * s * 0.015
            a = th + arm * math.pi + rng.normal() * 0.18
            x, y = s / 2 + r * math.cos(a), s / 2 + r * math.sin(a) * 0.55
            rr = rng.uniform(1, 3.5) * SS
            c = (200, 170, 255, int(rng.uniform(80, 220))) if rng.random() < 0.7 else (255, 230, 200, 230)
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=c)
    core = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse((s * 0.40, s * 0.44, s * 0.60, s * 0.56), fill=(255, 240, 210, 255))
    img.alpha_composite(core.filter(ImageFilter.GaussianBlur(s * 0.04)))
    GALAXY = img.resize((size, size), Image.LANCZOS)


def icon_galaxy(size, t, sun=True, streak=False):
    rot = (t / DUR) * 360 * 1
    g = GALAXY.rotate(rot, Image.BICUBIC).resize((size, size), Image.LANCZOS)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if streak:   # galáxia voando: rastros
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(1)
        for k in range(26):
            y = rng.uniform(0.1, 0.9) * size
            L = rng.uniform(0.15, 0.4) * size
            x = (rng.random() * size + t * PF(2.0) * 40) % (size * 1.4) - size * 0.2
            d.line((x, y, x - L, y), fill=(200, 180, 255, 120), width=2)
    img.alpha_composite(g)
    if sun:
        a = t * PF(2 * math.pi / 8)
        r0 = size * 0.30
        x, y = size / 2 + r0 * math.cos(a), size / 2 + r0 * math.sin(a) * 0.55
        d = ImageDraw.Draw(img)
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=YEL + (255,), outline=(0, 0, 0, 255), width=2)
    return img


def icon_sofa(size):
    img, s = canvas(size)
    d = ImageDraw.Draw(img)
    k = (0, 0, 0, 255)
    c1, c2 = (255, 214, 60, 255), (230, 170, 30, 255)
    d.rounded_rectangle((s * 0.14, s * 0.22, s * 0.86, s * 0.62), int(s * 0.08), fill=c2, outline=k, width=SS * 6)
    d.rounded_rectangle((s * 0.06, s * 0.44, s * 0.94, s * 0.76), int(s * 0.08), fill=c1, outline=k, width=SS * 6)
    d.rounded_rectangle((s * 0.02, s * 0.36, s * 0.20, s * 0.78), int(s * 0.07), fill=c2, outline=k, width=SS * 6)
    d.rounded_rectangle((s * 0.80, s * 0.36, s * 0.98, s * 0.78), int(s * 0.07), fill=c2, outline=k, width=SS * 6)
    for x in (0.12, 0.82):
        d.rectangle((s * x, s * 0.76, s * (x + 0.06), s * 0.88), fill=k)
    return finish(img, size)


def hero_icon(k, t, size=230):
    if k == "coracao":
        return icon_heart(size, beat_env(t))
    if k == "piscadas":
        lid = 0.0
        for b in BLINKS:
            if 0 <= t - b < 0.22:
                lid = math.sin(math.pi * (t - b) / 0.22)
        return icon_eye(size, lid, osc(t, 1.4))
    if k == "respira":
        return icon_lungs(size, 0.5 - 0.5 * math.cos(2 * math.pi * (t + 1.0) / BREATH_P))
    if k == "celulas":
        return icon_cell(size, (t / 1.6) % 1.0)
    if k == "raios":
        return icon_bolt(size, 0.6 + 0.4 * abs(osc(t, 9.0)))
    if k == "bebes":
        return icon_baby(size, osc(t, 3.0))
    if k == "rotacao":
        return globe_rgba(size * 0.45, t, pin=True)
    if k == "orbita":
        return icon_orbit(size + 40, t)
    if k == "sol":
        return icon_galaxy(size + 50, t)
    if k == "galaxia":
        return icon_galaxy(size + 30, t, sun=False, streak=True)


ROW_ICON = {}


def build_row_icons():
    sz = 46
    ROW_ICON.update(coracao=icon_heart(sz), piscadas=icon_eye(sz), respira=icon_lungs(sz), celulas=icon_cell(sz),
                    raios=icon_bolt(sz), bebes=icon_baby(sz), orbita=icon_orbit(sz, 1.0),
                    sol=icon_galaxy(sz, 0.0), galaxia=icon_galaxy(sz, 0.0, sun=False))


# ---------------------------------------------------------------- cronômetro + ECG
_g = {}


def glyph(ch, size, color):
    k = (ch, size, color)
    if k not in _g:
        _g[k] = rich_text(ch, size, "anton", color=color, stroke=max(6, size // 22))
    return _g[k]


def draw_digits(frame, txt, cx, cy, size, color, glow=CYAN, alpha=1.0, scale=1.0):
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
        paste(frame, gl, cx, cy, scale, alpha)
    paste(frame, layer, cx, cy, scale, alpha)


def num_text(frame, txt, size, color, glow, cx, cy, sc=1.0, al=1.0):
    img = rich_text(txt, size, "anton", color=color, stroke=max(6, size // 20), maxw=3000)
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(size * 0.12))
    gl = Image.new("RGBA", img.size, glow + (0,))
    gl.putalpha(a.point(lambda v: int(v * 0.8)))
    paste(frame, gl, cx, cy, sc, al)
    paste(frame, img, cx, cy, sc, al)


def remaining(t):
    if t < T_LOOP:
        return max(0.0, 60.0 - t)
    u = smoother(clamp((t - T_LOOP) / (DUR - T_LOOP - 0.2)))   # volta para 01:00 e segura
    return (60.0 - T_LOOP) + (60.0 - (60.0 - T_LOOP)) * u


def draw_timer(frame, t, sxy):
    r = remaining(t)
    m, s = int(r // 60), r % 60
    cs = int((s - int(s)) * 100)
    txt = f"{m:02d}:{int(s):02d},{cs:02d}"
    urgent = r < 10 and t < T_LOOP
    col = (255, 120, 120) if urgent else WHITE
    sc = 1.0 + (0.05 * beat_env(t) if urgent else 0.0)
    paste(frame, rich_text("TEMPO RESTANTE", 30, color=CYAN), CX, 82)
    draw_digits(frame, txt, CX + sxy[0], 168 + sxy[1], 128, col, glow=RED if urgent else CYAN, scale=sc)
    d = ImageDraw.Draw(frame)
    x0, x1, y = 120, 960, 258
    d.rounded_rectangle((x0, y - 7, x1, y + 7), 7, fill=(255, 255, 255, 40))
    f = r / 60.0
    d.rounded_rectangle((x0, y - 7, x0 + (x1 - x0) * f, y + 7), 7, fill=(RED if urgent else CYAN) + (255,))


def ecg_value(tt):
    """forma de onda de ECG em função do tempo"""
    v = 0.0
    for b in BEATS_X:
        dt = tt - b
        if -0.3 < dt < 0.5:
            v += 0.12 * math.exp(-((dt + 0.16) / 0.03) ** 2)          # P
            v -= 0.15 * math.exp(-((dt + 0.02) / 0.008) ** 2)         # Q
            v += 1.0 * math.exp(-((dt) / 0.012) ** 2)                  # R
            v -= 0.25 * math.exp(-((dt - 0.03) / 0.012) ** 2)         # S
            v += 0.22 * math.exp(-((dt - 0.25) / 0.05) ** 2)          # T
    return v


def draw_ecg(frame, t, y=312, alpha=1.0):
    d = ImageDraw.Draw(frame)
    pts = []
    span = 2.6
    for k in range(0, 841, 4):
        x = 120 + k
        tt = t - span * (1 - k / 840)
        pts.append((x, y - 46 * ecg_value(tt)))
    a = int(255 * alpha)
    d.line(pts, fill=RED + (int(70 * alpha),), width=12, joint="curve")
    d.line(pts, fill=(255, 120, 140, a), width=4, joint="curve")
    x, yy = pts[-1]
    d.ellipse((x - 7, yy - 7, x + 7, yy + 7), fill=WHITE + (a,))
    bpm = 68 + 9 * min(t, 55) / 55
    if t >= T_LOOP:
        bpm = 77 - 9 * smoother((t - T_LOOP) / (DUR - T_LOOP))
    paste(frame, rich_text(f"{int(round(bpm))} BPM", 26, color=(255, 150, 160)), 900, y - 36, 1.0, alpha)


# ---------------------------------------------------------------- cartões
HERO_C = (CX, 640)
ROW_Y0, ROW_H = 1004, 61
_c = {}


def hud_panel(w, h, col, alpha=200):
    k = ("panel", w, h, col, alpha)
    if k not in _c:
        img = rounded_panel(w, h, (12, 20, 52, alpha), 26, outline=col + (220,), ow=3)
        d = ImageDraw.Draw(img)
        L = 34
        for (x, y, dx, dy) in ((8, 8, 1, 1), (w - 9, 8, -1, 1), (8, h - 9, 1, -1), (w - 9, h - 9, -1, -1)):
            d.line((x, y, x + dx * L, y), fill=col + (255,), width=6)
            d.line((x, y, x, y + dy * L), fill=col + (255,), width=6)
        _c[k] = img
    return _c[k]


def pill(text, size=34, fg=NAVY, bg=CYAN):
    k = ("pill", text, size, bg, fg)
    if k not in _c:
        f = font("mont", size)
        tl = int(f.getlength(text))
        img = rounded_panel(tl + 40, size + 28, bg + (255,), (size + 28) // 2, outline=(0, 0, 0, 255), ow=4)
        ImageDraw.Draw(img).text((20, 11), text, font=f, fill=fg)
        _c[k] = img
    return _c[k]


def draw_hero(frame, k, t, a, b, sxy):
    st = STATS[k]
    col = st["col"]
    e_in = ease_out_back(clamp((t - a) / 0.4), 1.6)
    out = clamp((t - (b - 0.35)) / 0.35)
    if out > 0:          # encolhe em direção à linha do painel
        i = ORDER.index(k)
        ty = ROW_Y0 + i * ROW_H
        cy = HERO_C[1] + (ty - HERO_C[1]) * smoother(out)
        sc = 1 - 0.85 * smoother(out)
        al = 1 - smoother(out) * 0.9
    else:
        cy, sc, al = HERO_C[1], 0.7 + 0.3 * e_in, clamp((t - a) / 0.2)
    cx = CX + sxy[0]
    cy += sxy[1]
    panel = hud_panel(840, 550, col)
    paste(frame, panel, cx, cy, sc, al * 0.95)
    off = lambda dy: cy + dy * sc
    paste(frame, rich_text(st["head"], 48, maxw=800, hl=col if col != RED else (255, 120, 140)), cx, off(-218), sc, al)
    ic = hero_icon(k, t, 270)
    bob = 6 * osc(t, 2.5)
    paste(frame, ic, cx, off(-50 + bob), sc, al)
    v = st["val"](t)
    txt = fmt_val(v, st["fmt"])
    size = 150 if len(txt) <= 9 else 128
    numc = YEL if t >= T_BOOM else WHITE
    num_text(frame, txt, size, numc, col, cx, off(118), sc, al)
    paste(frame, pill(st["pill"], 30, bg=col if col != RED else (255, 120, 140)), cx, off(232), sc, al)


def draw_rows(frame, t, sxy):
    d = ImageDraw.Draw(frame)
    for i, k in enumerate(ORDER):
        a, b = hero_window(k)
        if t < b - 0.05:
            continue
        st = STATS[k]
        y = ROW_Y0 + i * ROW_H + sxy[1]
        e = ease_out_back(clamp((t - (b - 0.05)) / 0.3), 1.6)
        al = 1.0
        if t >= T_LOOP:     # recolhe no loop
            al = clamp(1 - (t - T_LOOP - i * 0.03) / 0.25)
            if al <= 0:
                continue
        frozen = t >= T_BOOM
        col = YEL if frozen else st["col"]
        panel = hud_panel(840, 54, col, 170)
        flash_ = clamp(1 - (t - T_BOOM) / 0.6) if frozen else 0.0
        paste(frame, panel, CX + sxy[0], y, 0.85 + 0.15 * e, al)
        if k == "rotacao":
            ic = globe_rgba(21, t)
        else:
            ic = ROW_ICON[k]
        paste(frame, ic, 168 + sxy[0], y, e, al)
        lab = rich_text(st["row"], 30)
        paste(frame, lab, 205 + lab.width / 2 + sxy[0], y, e, al)
        v = st["val"](t)
        num = rich_text(fmt_val(v, st["fmt"]), 42, "anton", color=YEL if frozen else WHITE, stroke=5)
        paste(frame, num, 935 - num.width / 2 + sxy[0], y, e * (1 + 0.1 * flash_), al)


def sofa_card():
    if "sofa" not in _c:
        a = rich_text("E VOCÊ NEM SAIU", 84, maxw=MAXW)
        b = rich_text("DO *SOFÁ*", 150, maxw=MAXW)
        pw = 860
        ic = icon_sofa(200)
        ph = a.height + b.height + ic.height + 30
        img = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        img.alpha_composite(a, ((pw - a.width) // 2, 0))
        img.alpha_composite(b, ((pw - b.width) // 2, a.height - 10))
        img.alpha_composite(ic, ((pw - ic.width) // 2, a.height + b.height + 10))
        _c["sofa"] = img
    return _c["sofa"]


def ui(frame, t, sxy):
    draw_ecg(frame, t)
    # gancho (frame 0 e volta no fim do loop)
    hook_a = 1.0 if t < S["coracao"] - 0.3 else clamp((S["coracao"] - 0.1 - t) / 0.2)
    if t >= T_LOOP + 0.25:
        hook_a = clamp((t - T_LOOP - 0.25) / 0.3)
    if hook_a > 0:
        sc = 1 + 0.02 * osc(t, 4.0)
        if t >= T_LOOP:
            u = clamp((t - T_LOOP - 0.25) / 0.4)
            sc = 0.6 + 0.4 * ease_out_back(u, 2.0) if u < 1 else sc
        paste(frame, rich_text("NOS PRÓXIMOS", 80, maxw=MAXW), CX, 520, sc, hook_a)
        num_text(frame, "60 SEGUNDOS", 165, YEL, RED, CX, 680, sc, hook_a)
        paste(frame, rich_text("VOCÊ VAI…", 80, maxw=MAXW), CX, 850, sc, hook_a)
        paste(frame, icon_heart(140, beat_env(t)), CX, 1010, sc, hook_a)
        paste(frame, pill("SEM SAIR DO LUGAR", 34, bg=YEL), CX, 1150, sc, hook_a)
    # cartão em destaque
    for k in ORDER:
        a, b = hero_window(k)
        if a <= t < b:
            draw_hero(frame, k, t, a, b, sxy)
    draw_rows(frame, t, sxy)
    # final: sofá + CTA
    if S["sofa"] - 0.1 <= t < T_LOOP:
        al = clamp((t - S["sofa"] + 0.1) / 0.2) * clamp((T_LOOP - t) / 0.15)
        if t < T_BOOM:
            paste(frame, rich_text("TUDO ISSO...", 110, maxw=MAXW), CX + sxy[0], 640, pop(t, S["sofa"] - 0.1), al)
        elif t < T_CTA:
            paste(frame, sofa_card(), CX + sxy[0], 640 + sxy[1], ease_out_back(clamp((t - T_BOOM) / 0.3), 2.2), al)
    if T_CTA <= t < T_LOOP:
        al = clamp((T_LOOP - t) / 0.15)
        paste(frame, rich_text("PERA, OI?", 170, "anton", color=YEL, stroke=12), CX, 540,
              pop(t, T_CTA) * (1 + 0.03 * osc(t, 7.0)), al)
        tq = word_t("cta", "assiste") - 0.05
        if t >= tq:
            sc = pop(t, tq)
            paste(frame, rich_text("ASSISTE DE NOVO E", 62, maxw=MAXW), CX, 700, sc, al)
            paste(frame, rich_text("*CONTA AS PISCADAS*", 66, maxw=MAXW), CX, 775, sc, al)
            lid = 0.0
            ph = (t - tq) % 1.2
            if ph < 0.22:
                lid = math.sin(math.pi * ph / 0.22)
            paste(frame, icon_eye(130, lid), CX, 890, sc, al)
    caption(frame, t)


# ---------------------------------------------------------------- legendas
CHUNKS = []


def build_chunks():
    CHUNKS.clear()
    cur, line = [], None
    for w in P["words"]:
        if w["line"] in ("hook", "sofa", "cta"):
            continue
        if cur and (w["line"] != line or len(cur) >= 3 or sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > 18):
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
            paste(frame, rich_text(" ".join(parts), 50, maxw=MAXW + 60), CX, 950,
                  0.85 + 0.15 * ease_out_back(clamp((t - a) / 0.16), 2.0))
            return


# ---------------------------------------------------------------- efeitos
def shake(t):
    dt = t - T_BOOM
    if 0 <= dt < 1.0:
        a = 34 * math.exp(-dt * 5)
        return a * math.sin(dt * 73) * math.cos(dt * 11), a * math.sin(dt * 51 + 1.1)
    return 0.0, 0.0


def flash(t):
    f = 0.0
    if T_BOOM - 0.03 <= t < T_BOOM + 0.5:
        f = 1.0 if t < T_BOOM + 0.06 else 1 - smoother((t - T_BOOM - 0.06) / 0.44)
    if T_LOOP <= t < T_LOOP + 0.4:
        f = max(f, 0.6 * (1 - smoother((t - T_LOOP) / 0.4)))
    return f


def init():
    E.init()
    build_base()
    build_galaxy()
    build_row_icons()
    build_chunks()


def render_frame(f):
    t = f / FPS
    sxy = shake(t)
    bg = background(t)
    img = Image.fromarray((np.clip(bg, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    particles(img, t)
    draw_timer(img, t, sxy)
    ui(img, t, sxy)
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
    return dict(beats=[b for b in BEATS if b < DUR], blinks=[b for b in BLINKS if b < T_BOOM], cards=[S[k] - 0.15 for k in ORDER],
                order=ORDER, S=S, boom=T_BOOM, cta=T_CTA, loop=T_LOOP, sofa=S["sofa"],
                breaths=[k * BREATH_P - 1.0 + BREATH_P for k in range(int(DUR / BREATH_P) + 1)])


def main():
    os.makedirs(OUT, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "times":
        for k in ORDER + ["sofa", "cta"]:
            print(f"{S[k]:6.2f} {k}")
        print(f"{T_BOOM:6.2f} BOOM  {T_LOOP:6.2f} LOOP  {DUR} DUR")
        for k in ORDER:
            print(k, fmt_val(STATS[k]["val"](DUR), STATS[k]["fmt"]))
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
