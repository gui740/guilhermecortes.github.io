"""Perguntas que eu me fiz quando tava chapado — EXPECTATIVA DE VIDA (motion graphics, vertical 1080x1920, 30 fps).
Cada frase da narração tem 2–6 cortes amarrados às palavras faladas.

  python render.py times | preview 3 10.5 ... | video
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "planetas"))
import engine as E
from engine import W, H, FPS, clamp, smoother, ease_out_cubic, ease_out_back, rich_text, paste, rounded_panel, font
import plan as PL

OUT = os.path.join(HERE, "out")
os.environ.setdefault("NARR", os.path.join(OUT, "narr"))
P = PL.load()
S, EN = P["S"], P["E"]
DUR, NFRAMES = P["DUR"], P["NFRAMES"]
CX, CY = 500, 760            # centro da área segura (x 40..960) e do palco visual
NAVY = (10, 14, 38); YEL = (255, 214, 60); CYAN = (60, 210, 255); RED = (255, 64, 72); GREEN = (70, 230, 130)
WHITE = (255, 255, 255); INK = (0, 0, 0)


def wt(line, frag, which="t", nth=0):
    frag = frag.lower(); k = 0
    for w in P["words"]:
        if w["line"] == line and w["w"].lower().startswith(frag):
            if k == nth:
                return w["t"] + (w["d"] if which == "end" else 0.0)
            k += 1
    return S[line]


def pop(t, a, dur=0.22, k=2.4):
    if t < a:
        return 0.0
    x = (t - a) / dur
    return 1.0 if x >= 1 else max(0.0, ease_out_back(x, k))


# ---------------------------------------------------------------- texto e números
_c = {}


def txt(img, s, size, cx, cy, sc=1.0, al=1.0, color=WHITE, hl=YEL, maxw=880, kind="mont", rot=0.0):
    """texto numa linha só; se passar de maxw, encolhe para caber"""
    key = (s, size, color, hl, maxw, kind)
    if key not in _c:
        im = rich_text(s, size, kind, maxw=4000, color=color, hl=hl, stroke=max(6, size // 9))
        if im.width > maxw:
            im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
        _c[key] = im
    paste(img, _c[key], cx, cy, sc, al, rot=rot)


def num(img, s, size, cx, cy, sc=1.0, al=1.0, color=WHITE, glow=CYAN, rot=0.0):
    key = ("n", s, size, color, glow)
    if key not in _c:
        t0_ = rich_text(s, size, "anton", color=color, stroke=max(8, size // 18), maxw=3000)
        pad = int(size * 0.35)
        t_ = Image.new("RGBA", (t0_.width + 2 * pad, t0_.height + 2 * pad), (0, 0, 0, 0)); t_.alpha_composite(t0_, (pad, pad))
        a = t_.getchannel("A").filter(ImageFilter.GaussianBlur(size * 0.1))
        g = Image.new("RGBA", t_.size, glow + (0,)); g.putalpha(a.point(lambda v: int(v * 0.9)))
        both = Image.new("RGBA", t_.size, (0, 0, 0, 0)); both.alpha_composite(g); both.alpha_composite(t_)
        _c[key] = both
    paste(img, _c[key], cx, cy, sc, al, rot=rot)


def pill(img, s, size, cx, cy, sc=1.0, al=1.0, bg=YEL, fg=NAVY):
    key = ("p", s, size, bg, fg)
    if key not in _c:
        f = font("mont", size); tl = int(f.getlength(s))
        im = rounded_panel(tl + 50, size + 34, bg + (255,), (size + 34) // 2, outline=INK + (255,), ow=5)
        ImageDraw.Draw(im).text((25, 14), s, font=f, fill=fg)
        _c[key] = im
    paste(img, _c[key], cx, cy, sc, al)


def stamp(img, s, t, t0, cx, cy, color=RED, size=130, rot=-12):
    """carimbo que bate na tela"""
    if t < t0:
        return
    u = clamp((t - t0) / 0.14)
    sc = 2.4 - 1.4 * ease_out_cubic(u)
    key = ("st", s, size, color)
    if key not in _c:
        f = font("mont", size); tl = int(f.getlength(s))
        im = Image.new("RGBA", (tl + 80, size + 70), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((6, 6, tl + 74, size + 64), 18, outline=color + (255,), width=12)
        d.text((40, 22), s, font=f, fill=color, stroke_width=4, stroke_fill=INK)
        _c[key] = im
    paste(img, _c[key], cx, cy, sc, clamp(u * 3), rot=rot)


# ---------------------------------------------------------------- ícones vetoriais (3x e reduz)
SS = 3


def icon(key, size, draw_fn):
    k = ("ic", key, size)
    if k not in _c:
        s = size * SS
        im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(im), s, im)
        _c[k] = im.resize((size, size), Image.LANCZOS)
    return _c[k]


def outline_poly(d, pts, fill, w):
    d.polygon(pts, fill=fill, outline=INK + (255,), width=w)


def baby(size=300):
    def f(d, s, im):
        w = int(s * 0.03)
        d.rounded_rectangle((s * .22, s * .48, s * .78, s * .95), int(s * .2), fill=(150, 210, 255, 255), outline=INK + (255,), width=w)
        d.ellipse((s * .26, s * .08, s * .74, s * .56), fill=(255, 214, 180, 255), outline=INK + (255,), width=w)
        d.arc((s * .44, s * .02, s * .58, s * .16), 180, 360, fill=INK + (255,), width=w)
        for x in (.4, .6):
            d.ellipse((s * (x - .03), s * .28, s * (x + .03), s * .34), fill=INK + (255,))
        d.ellipse((s * .44, s * .38, s * .56, s * .46), fill=(255, 140, 190, 255), outline=INK + (255,), width=int(w * .7))
    return icon("baby", size, f)


def oldman(size=320):
    def f(d, s, im):
        w = int(s * 0.028)
        d.rounded_rectangle((s * .26, s * .42, s * .7, s * .95), int(s * .12), fill=(90, 120, 200, 255), outline=INK + (255,), width=w)
        d.line((s * .74, s * .55, s * .8, s * .98), fill=(140, 90, 50, 255), width=int(s * .035))
        d.arc((s * .68, s * .48, s * .84, s * .62), 180, 360, fill=(140, 90, 50, 255), width=int(s * .035))
        d.ellipse((s * .28, s * .08, s * .68, s * .46), fill=(245, 205, 170, 255), outline=INK + (255,), width=w)
        d.chord((s * .28, s * .08, s * .68, s * .3), 180, 360, fill=(235, 235, 240, 255), outline=INK + (255,), width=w)
        for x in (.4, .56):
            d.ellipse((s * (x - .05), s * .24, s * (x + .05), s * .32), outline=INK + (255,), width=int(w * .8))
        d.chord((s * .34, s * .3, s * .62, s * .46), 0, 180, fill=(240, 240, 245, 255), outline=INK + (255,), width=int(w * .8))
    return icon("old", size, f)


def grave(size=300):
    def f(d, s, im):
        w = int(s * 0.03)
        d.rounded_rectangle((s * .2, s * .1, s * .8, s * .9), int(s * .28), fill=(150, 155, 170, 255), outline=INK + (255,), width=w)
        d.rectangle((s * .2, s * .5, s * .8, s * .9), fill=(150, 155, 170, 255))
        d.line((s * .2, s * .5, s * .2, s * .9), fill=INK + (255,), width=w); d.line((s * .8, s * .5, s * .8, s * .9), fill=INK + (255,), width=w)
        d.rectangle((s * .08, s * .86, s * .92, s * .96), fill=(70, 160, 80, 255), outline=INK + (255,), width=w)
        d.text((s * .5, s * .45), "RIP", font=font("anton", int(s * .22)), fill=INK, anchor="mm")
    return icon("grave", size, f)


def pave(size=320):
    def f(d, s, im):
        w = int(s * 0.03)
        d.ellipse((s * .05, s * .78, s * .95, s * .96), fill=(240, 240, 240, 255), outline=INK + (255,), width=w)
        layers = [(.66, (110, 70, 40)), (.54, (255, 236, 190)), (.42, (110, 70, 40)), (.3, (255, 236, 190))]
        d.rectangle((s * .15, s * .2, s * .85, s * .82), fill=(255, 236, 190, 255), outline=INK + (255,), width=w)
        for y, c in layers:
            d.rectangle((s * .15, s * y, s * .85, s * (y + .1)), fill=c + (255,))
        d.rectangle((s * .15, s * .2, s * .85, s * .82), outline=INK + (255,), width=w)
        for i in range(6):
            d.ellipse((s * (.2 + i * .11), s * .13, s * (.28 + i * .11), s * .22), fill=(110, 70, 40, 255), outline=INK + (255,), width=int(w * .6))
    return icon("pave", size, f)


def syringe(size=240):
    def f(d, s, im):
        w = int(s * 0.035)
        d.rectangle((s * .3, s * .12, s * .58, s * .7), fill=(220, 240, 255, 255), outline=INK + (255,), width=w)
        d.rectangle((s * .3, s * .4, s * .58, s * .7), fill=(60, 210, 255, 255), outline=INK + (255,), width=w)
        d.rectangle((s * .4, s * .02, s * .48, s * .12), fill=(200, 200, 210, 255), outline=INK + (255,), width=w)
        d.rectangle((s * .26, s * .0, s * .62, s * .05), fill=(200, 200, 210, 255), outline=INK + (255,), width=w)
        d.line((s * .44, s * .7, s * .44, s * .98), fill=INK + (255,), width=int(s * .025))
    return icon("syr", size, f)


def faucet(size=240):
    def f(d, s, im):
        w = int(s * 0.035)
        d.rounded_rectangle((s * .1, s * .3, s * .7, s * .48), int(s * .06), fill=(190, 200, 215, 255), outline=INK + (255,), width=w)
        d.rounded_rectangle((s * .55, s * .3, s * .72, s * .62), int(s * .06), fill=(190, 200, 215, 255), outline=INK + (255,), width=w)
        d.rectangle((s * .3, s * .14, s * .42, s * .3), fill=(190, 200, 215, 255), outline=INK + (255,), width=w)
        d.rounded_rectangle((s * .18, s * .06, s * .54, s * .16), int(s * .04), fill=(255, 64, 72, 255), outline=INK + (255,), width=w)
        for y in (.7, .82, .94):
            d.ellipse((s * .58, s * y, s * .68, s * (y + .08)), fill=(60, 170, 255, 255), outline=INK + (255,), width=int(w * .6))
    return icon("fau", size, f)


def capsule(size=240):
    def f(d, s, im):
        w = int(s * 0.035)
        cap = Image.new("RGBA", (s, s), (0, 0, 0, 0)); dc = ImageDraw.Draw(cap)
        dc.rounded_rectangle((s * .1, s * .36, s * .9, s * .64), int(s * .14), fill=(255, 255, 255, 255), outline=INK + (255,), width=w)
        dc.rounded_rectangle((s * .1, s * .36, s * .5, s * .64), int(s * .14), fill=(255, 64, 72, 255), outline=INK + (255,), width=w)
        dc.rectangle((s * .4, s * .38, s * .5, s * .62), fill=(255, 64, 72, 255))
        dc.line((s * .5, s * .36, s * .5, s * .64), fill=INK + (255,), width=w)
        im.alpha_composite(cap.rotate(35, Image.BICUBIC))
    return icon("cap", size, f)


def heart(size=240, beat=0.0):
    def f(d, s, im):
        pts = []
        sc = 1 + 0.12 * beat
        for k in range(80):
            a = 2 * math.pi * k / 80
            x = 16 * math.sin(a) ** 3; y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((s / 2 + x * s / 38 * sc, s / 2 - y * s / 38 * sc - s * .03))
        d.polygon(pts, fill=RED + (255,), outline=INK + (255,), width=int(s * .035))
        d.ellipse((s * .3, s * .3, s * .42, s * .4), fill=(255, 200, 200, 255))
    return icon(("heart", round(beat, 2)), size, f)


def brain(size=240):
    def f(d, s, im):
        w = int(s * 0.035)
        d.ellipse((s * .1, s * .2, s * .9, s * .82), fill=(255, 160, 190, 255), outline=INK + (255,), width=w)
        d.line((s * .5, s * .22, s * .5, s * .8), fill=INK + (255,), width=w)
        for (x, y) in ((.25, .38), (.32, .6), (.65, .36), (.72, .58), (.4, .3), (.6, .7)):
            d.arc((s * (x - .1), s * (y - .07), s * (x + .1), s * (y + .07)), 200, 340, fill=INK + (255,), width=int(w * .7))
    return icon("brain", size, f)


def drop(size=220):
    def f(d, s, im):
        d.polygon([(s * .5, s * .06), (s * .78, s * .56), (s * .22, s * .56)], fill=(255, 64, 72, 255))
        d.ellipse((s * .2, s * .38, s * .8, s * .94), fill=(255, 64, 72, 255), outline=INK + (255,), width=int(s * .035))
        d.line((s * .5, s * .06, s * .22, s * .56), fill=INK + (255,), width=int(s * .035)); d.line((s * .5, s * .06, s * .78, s * .56), fill=INK + (255,), width=int(s * .035))
        d.text((s * .5, s * .68), "+", font=font("anton", int(s * .3)), fill=WHITE, anchor="mm")
    return icon("drop", size, f)


def lady(size=360):
    def f(d, s, im):
        w = int(s * 0.026)
        d.rounded_rectangle((s * .24, s * .46, s * .7, s * .96), int(s * .12), fill=(120, 80, 160, 255), outline=INK + (255,), width=w)
        d.ellipse((s * .26, s * .14, s * .66, s * .52), fill=(245, 210, 180, 255), outline=INK + (255,), width=w)
        d.chord((s * .2, s * .06, s * .72, s * .3), 180, 360, fill=(30, 30, 40, 255), outline=INK + (255,), width=w)   # boina
        d.ellipse((s * .42, s * .02, s * .5, s * .1), fill=(30, 30, 40, 255))
        for x in (.38, .54):
            d.arc((s * (x - .04), s * .3, s * (x + .04), s * .36), 0, 180, fill=INK + (255,), width=int(w * .8))
        d.line((s * .52, s * .44, s * .8, s * .38), fill=(255, 255, 255, 255), width=int(s * .03))
        d.line((s * .76, s * .39, s * .8, s * .38), fill=(255, 120, 40, 255), width=int(s * .03))
        d.arc((s * .4, s * .38, s * .54, s * .46), 0, 180, fill=INK + (255,), width=int(w * .8))
    return icon("lady", size, f)


def backpain(size=360):
    def f(d, s, im):
        w = int(s * 0.026)
        d.rounded_rectangle((s * .3, s * .38, s * .66, s * .78), int(s * .1), fill=(90, 120, 200, 255), outline=INK + (255,), width=w)
        d.ellipse((s * .48, s * .16, s * .78, s * .44), fill=(245, 205, 170, 255), outline=INK + (255,), width=w)
        d.line((s * .4, s * .78, s * .36, s * .98), fill=INK + (255,), width=int(s * .05)); d.line((s * .56, s * .78, s * .6, s * .98), fill=INK + (255,), width=int(s * .05))
        d.line((s * .3, s * .5, s * .22, s * .66), fill=(245, 205, 170, 255), width=int(s * .05))
        for (x, y) in ((.2, .36), (.14, .5), (.22, .24)):
            d.polygon([(s * x, s * y), (s * (x + .05), s * (y + .06)), (s * (x + .02), s * (y + .07)), (s * (x + .07), s * (y + .14)),
                       (s * (x - .01), s * (y + .07)), (s * (x + .02), s * (y + .06))], fill=YEL + (255,), outline=INK + (255,))
        d.arc((s * .58, s * .3, s * .7, s * .38), 180, 360, fill=INK + (255,), width=int(w * .8))
    return icon("back", size, f)


def bubble(size=300):
    def f(d, s, im):
        w = int(s * 0.035)
        d.rounded_rectangle((s * .06, s * .1, s * .94, s * .7), int(s * .14), fill=WHITE + (255,), outline=INK + (255,), width=w)
        d.polygon([(s * .25, s * .66), (s * .2, s * .9), (s * .45, s * .68)], fill=WHITE + (255,), outline=INK + (255,))
        d.rectangle((s * .26, s * .6, s * .44, s * .72), fill=WHITE + (255,))
        for x in (.32, .5, .68):
            d.ellipse((s * (x - .05), s * .35, s * (x + .05), s * .45), fill=NAVY + (255,))
    return icon("bub", size, f)


def boleto(size=320):
    def f(d, s, im):
        w = int(s * 0.03)
        d.rectangle((s * .1, s * .14, s * .9, s * .86), fill=(250, 250, 245, 255), outline=INK + (255,), width=w)
        d.text((s * .5, s * .26), "BOLETO", font=font("anton", int(s * .13)), fill=INK, anchor="mm")
        r = np.random.default_rng(3)
        x = s * .16
        while x < s * .84:
            bw = s * (0.006 + r.random() * 0.018)
            d.rectangle((x, s * .56, x + bw, s * .78), fill=INK + (255,)); x += bw + s * (0.006 + r.random() * 0.012)
        d.text((s * .5, s * .44), "R$ ????", font=font("anton", int(s * .1)), fill=RED, anchor="mm")
    return icon("bol", size, f)


def clock_rewind(size, ang):
    s = size
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((s * .08, s * .08, s * .92, s * .92), fill=WHITE + (255,), outline=INK + (255,), width=int(s * .04))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        d.line((s / 2 + math.cos(a) * s * .34, s / 2 + math.sin(a) * s * .34, s / 2 + math.cos(a) * s * .4, s / 2 + math.sin(a) * s * .4), fill=INK + (255,), width=int(s * .02))
    for L, wdt, a in ((0.22, .04, ang / 12), (0.32, .03, ang)):
        d.line((s / 2, s / 2, s / 2 + math.cos(a - math.pi / 2) * s * L, s / 2 + math.sin(a - math.pi / 2) * s * L), fill=INK + (255,), width=int(s * wdt))
    d.arc((s * .0, s * .0, s * 1.0, s * 1.0), 200, 320, fill=RED + (255,), width=int(s * .05))
    return im


# ---------------------------------------------------------------- fundo
YY = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
THEMES = {  # (topo, base, brilho)
    "azul": ((8, 12, 40), (20, 40, 110), (60, 140, 255)), "vermelho": ((30, 4, 10), (110, 14, 24), (255, 60, 70)),
    "verde": ((4, 24, 20), (10, 80, 60), (70, 230, 160)), "roxo": ((20, 6, 40), (70, 20, 120), (190, 90, 255)),
    "amarelo": ((40, 26, 4), (120, 80, 10), (255, 200, 60)), "psico": ((10, 30, 10), (60, 10, 90), (120, 255, 120)),
}
STRIPES = None
VIG = None


def build_bg():
    global STRIPES, VIG
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    STRIPES = (((xs + ys) // 90) % 2).astype(np.float32)[..., None] * 0.045
    r = np.sqrt(((xs - W / 2) / (W * 0.75)) ** 2 + ((ys - H / 2) / (H * 0.62)) ** 2)
    VIG = np.clip(1 - 0.75 * np.clip(r - 0.55, 0, 1) ** 1.2, 0, 1)[..., None]


def theme_at(t):
    seq = [(0, "azul"), (S["marca"], "psico"), (S["tio"], "amarelo"), (S["media"], "azul"), (S["bebes"], "roxo"),
           (S["subiu"], "verde"), (wt("pah", "pah") - 0.05, "vermelho"), (S["volta"], "verde"), (S["jeanne"], "roxo"),
           (S["insight"], "azul"), (S["boleto"], "vermelho"), (S["costas"], "amarelo"), (S["cta"], "azul")]
    cur, prev, ts = seq[0][1], seq[0][1], 0
    for a, name in seq:
        if t >= a:
            prev, cur, ts = cur, name, a
    return cur, prev, clamp((t - ts) / 0.25)


def background(t):
    cur, prev, u = theme_at(t)
    def grad(name):
        a, b, g = [np.array(c, np.float32) / 255 for c in THEMES[name]]
        return a + (b - a) * YY, g
    g1, gl1 = grad(cur)
    img = np.broadcast_to(g1, (H, 1, 3))
    if u < 1:
        g0, gl0 = grad(prev)
        img = g0 * (1 - u) + g1 * u
        gl1 = gl0 * (1 - u) + gl1 * u
    img = np.broadcast_to(img, (H, W, 3)).copy()
    sh = int(t * 60) % 180
    img += np.roll(STRIPES, sh, axis=1) * gl1
    ys = np.linspace(-1, 1, H, dtype=np.float32)[:, None]; xs = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
    img += (np.exp(-((xs * 0.9) ** 2 + ((ys + 0.2) * 1.4) ** 2) * 2.2) * 0.22)[..., None] * gl1
    return img * VIG


RNG = np.random.default_rng(4)
PART = dict(x=RNG.random(60), y=RNG.random(60), s=RNG.uniform(1, 3, 60), v=RNG.uniform(0.04, 0.12, 60))


def particles(img, t):
    d = ImageDraw.Draw(img)
    for i in range(60):
        y = ((PART["y"][i] - t * PART["v"][i]) % 1.0) * H
        x = PART["x"][i] * W + 15 * math.sin(t + i)
        r = PART["s"][i]
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 90))


# ---------------------------------------------------------------- cenas (cortes)
SHOTS = []          # (início, função, flash?)


def shot(t0, flash=False):
    def deco(fn):
        SHOTS.append((t0, fn, flash))
        return fn
    return deco


def build_shots():
    SHOTS.clear()
    T45 = wt("hook", "quarenta", nth=1)   # o "quarenta e cinco" (o 1º é de 1940)

    @shot(0.0)
    def s_hook(img, lt, t):
        v = 45 * ease_out_cubic(clamp((t - 0.3) / max(0.4, T45 - 0.3)))
        pill(img, "BRASIL · 1940", 44, CX, 420, pop(t, 0.1), bg=CYAN)
        num(img, f"{int(round(v))}", 520, CX, 760, 1 + 0.03 * math.sin(t * 6), glow=YEL)
        txt(img, "ANOS DE *VIDA*", 90, CX, 1060, pop(t, T45 - 0.1))

    @shot(wt("hook", "então"))
    def s_rip(img, lt, t):
        g = grave(420)
        paste(img, g, CX, 780, pop(t, wt("hook", "então"), 0.3), rot=4 * math.sin(t * 3))
        txt(img, "TODO MUNDO *BATIA AS BOTAS*", 76, CX, 400, pop(t, wt("hook", "batia") - 0.1))
        txt(img, "AOS 45?", 120, CX, 1110, pop(t, wt("hook", "aniversário") - 0.1), color=YEL)

    @shot(wt("hook", "spoiler"), flash=True)
    def s_nao(img, lt, t):
        txt(img, "SPOILER:", 100, CX, 520, pop(t, wt("hook", "spoiler")))
        stamp(img, "NÃO!", t, wt("hook", "não", nth=0) if wt("hook", "não") > wt("hook", "spoiler") else wt("hook", "spoiler") + 0.5, CX, 820, RED, 230)

    @shot(S["marca"], flash=True)
    def s_marca(img, lt, t):
        ws = [("PERGUNTAS", WHITE), ("QUE EU ME FIZ", CYAN), ("QUANDO TAVA", WHITE), ("CHAPADO", GREEN)]
        for i, (w_, c) in enumerate(ws):
            ta = S["marca"] + i * 0.32
            sc = pop(t, ta, 0.18, 3)
            txt(img, w_, 150 if i == 3 else 104, CX, 480 + i * 175, sc, color=c, rot=(-4 if i % 2 else 3) + 2 * math.sin(t * 5 + i))
        for k in range(6):
            a = t * 2.4 + k * 1.05
            x, y = CX + math.cos(a) * 380, 820 + math.sin(a) * 520
            d = ImageDraw.Draw(img)
            r = 26 + 10 * math.sin(t * 4 + k)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 255, 150, 110))

    @shot(S["tio"])
    def s_tio(img, lt, t):
        txt(img, "O *TIO DO PAVÊ*", 110, CX, 420, pop(t, wt("tio", "tio") - 0.1))
        paste(img, pave(460), CX, 820, pop(t, S["tio"], 0.3) * (1 + 0.05 * math.sin(t * 9)), rot=6 * math.sin(t * 4))
        if t >= wt("tio", "nem"):
            u = clamp((t - wt("tio", "nem")) / 0.15)
            d = ImageDraw.Draw(img)
            L = 300 * u
            for sg in (1, -1):
                d.line((CX - L, 820 - L * sg, CX + L, 820 + L * sg), fill=RED + (255,), width=46)
        txt(img, "NEM CHEGAVA NO *CHURRASCO*", 72, CX, 1190, pop(t, wt("tio", "churrasco") - 0.15))

    @shot(S["media"], flash=True)
    def s_golpe(img, lt, t):
        txt(img, "O GOLPE", 150, CX, 640, pop(t, S["media"]), rot=-3)
        txt(img, "TÁ NA *MÉDIA*", 130, CX, 830, pop(t, wt("media", "média") - 0.05), rot=2)

    tb = wt("media", "olha")

    @shot(tb)
    def s_bebes(img, lt, t):
        tm = wt("media", "morre"); to = wt("media", "outro")
        b = baby(300)
        # bebê 1 -> túmulo
        if t < tm + 0.2:
            paste(img, b, CX - 210, 760, pop(t, tb + 0.1, 0.25))
        else:
            paste(img, grave(320), CX - 210, 760, pop(t, tm + 0.2, 0.25))
            pill(img, "1 ANO", 54, CX - 210, 1000, pop(t, tm + 0.3), bg=RED, fg=WHITE)
        # bebê 2 -> velhinho
        if t < to + 0.5:
            paste(img, b, CX + 210, 760, pop(t, tb + 0.25, 0.25))
        else:
            paste(img, oldman(360), CX + 210, 740, pop(t, to + 0.5, 0.25))
            pill(img, "89 ANOS", 54, CX + 210, 1000, pop(t, to + 0.6), bg=GREEN)

    tq = wt("media", "média", nth=1)

    @shot(tq)
    def s_conta(img, lt, t):
        t45 = wt("media", "quarenta")
        txt(img, "( 1 + 89 ) ÷ 2", 110, CX, 640, pop(t, tq), kind="anton")
        if t >= t45 - 0.05:
            num(img, "= 45", 330, CX, 900, pop(t, t45 - 0.05, 0.25) * (1 + 0.04 * math.sin(t * 8)), color=YEL, glow=RED)

    @shot(wt("media", "matemática"), flash=True)
    def s_mente(img, lt, t):
        ta = wt("media", "matemática")
        txt(img, "A MATEMÁTICA", 110, CX, 600, pop(t, ta))
        txt(img, "*MENTE*", 230, CX, 800, pop(t, wt("media", "mente") - 0.05), hl=RED)
        stamp(img, "NA CARA DURA", t, wt("media", "cara"), CX, 1050, YEL, 80, rot=8)

    tmil = wt("bebes", "cada")

    @shot(S["bebes"])
    def s_grid(img, lt, t):
        t150 = wt("bebes", "cento"); thoje = wt("bebes", "hoje")
        now = t >= thoje - 0.05
        pill(img, "HOJE" if now else "1940", 56, CX, 380, 1.0, bg=GREEN if now else CYAN)
        d = ImageDraw.Draw(img)
        rows, cols = 25, 40
        gx0, gy0, step = CX - 19.5 * 21, 480, 21
        appear = clamp((t - tmil) / 0.6)
        nred = 12 if now else int(147 * ease_out_cubic(clamp((t - t150) / 1.0)))
        rng = np.random.default_rng(11)
        order = rng.permutation(1000)
        red = set(order[:nred].tolist())
        for k in range(int(1000 * appear)):
            r, c = divmod(k, cols)
            x, y = gx0 + c * step, gy0 + r * step
            if k in red:
                d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(255, 64, 72, 110))
                d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=RED + (255,))
            else:
                d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(200, 210, 230, 200))
        if t >= t150 - 0.1 and not now:
            num(img, f"{nred}", 220, CX - 120, 1150, pop(t, t150 - 0.1), color=RED, glow=RED)
            txt(img, "DE 1.000", 70, CX + 190, 1170, pop(t, t150))
        if now:
            num(img, "12", 260, CX - 120, 1150, pop(t, thoje), color=GREEN, glow=GREEN)
            txt(img, "DE 1.000", 70, CX + 190, 1170, pop(t, thoje + 0.05))

    @shot(S["subiu"])
    def s_cura(img, lt, t):
        items = [(syringe(230), "VACINA", wt("subiu", "vacina")), (faucet(230), "ÁGUA E ESGOTO", wt("subiu", "saneamento")),
                 (capsule(230), "ANTIBIÓTICO", wt("subiu", "antibiótico"))]
        for i, (im, lab, ta) in enumerate(items):
            x = CX + (i - 1) * 300
            paste(img, im, x, 560, pop(t, ta - 0.05, 0.25), rot=5 * math.sin(t * 4 + i))
            pill(img, lab, 36, x, 720, pop(t, ta), bg=CYAN)
        tm = wt("subiu", "média")
        if t >= tm - 0.1:
            v = 45 + 31.5 * ease_out_cubic(clamp((t - tm) / 1.2))
            num(img, f"{v:.1f}".replace(".", ","), 300, CX, 1000, pop(t, tm - 0.1), color=GREEN, glow=GREEN)
            d = ImageDraw.Draw(img)
            d.polygon([(CX + 330, 960), (CX + 400, 860), (CX + 470, 960)], fill=GREEN + (255,), outline=INK + (255,))

    def chart(img, t, year, color=YEL):
        data = [(2010, 74.4), (2012, 74.9), (2014, 75.4), (2016, 75.8), (2018, 76.2), (2019, 76.4), (2020, 74.8), (2021, 72.8),
                (2022, 75.5), (2023, 76.4), (2024, 76.6)]
        X = lambda y: 110 + (y - 2010) / 14 * 790
        Y = lambda v: 1150 - (v - 72) / 5 * 560
        d = ImageDraw.Draw(img)
        for v in (73, 74, 75, 76, 77):
            d.line((110, Y(v), 900, Y(v)), fill=(255, 255, 255, 50), width=2)
            txt(img, str(v), 34, 70, Y(v), 1.0, kind="anton")
        for y in (2010, 2015, 2021, 2024):
            txt(img, str(y), 34, X(y), 1200, 1.0, kind="anton")
        pts = []
        for i in range(len(data) - 1):
            (y0, v0), (y1, v1) = data[i], data[i + 1]
            for k in range(11):
                yy = y0 + (y1 - y0) * k / 10
                if yy > year:
                    break
                pts.append((X(yy), Y(v0 + (v1 - v0) * k / 10)))
        if len(pts) > 1:
            d.line(pts, fill=color + (90,), width=26, joint="curve")
            d.line(pts, fill=color + (255,), width=12, joint="curve")
            x, y = pts[-1]
            d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=WHITE + (255,), outline=INK + (255,), width=5)
        return X, Y

    tp = wt("pah", "pah")

    @shot(S["pah"])
    def s_chart(img, lt, t):
        crash = clamp((t - tp) / 0.35)
        year = 2010 + 9 * ease_out_cubic(clamp((t - S["pah"]) / max(0.5, tp - S["pah"]))) + 2 * crash
        X, Y = chart(img, t, year, RED if crash > 0 else YEL)
        txt(img, "2021: *PANDEMIA*", 80, CX, 380, pop(t, wt("pah", "pandemia") - 0.1), hl=RED)
        if t >= tp:
            num(img, "-3 ANOS", 150, CX + 120, 560, pop(t, wt("pah", "despencou")), color=RED, glow=RED, rot=-6)

    @shot(wt("pah", "brasil"), flash=True)
    def s_volta_tempo(img, lt, t):
        ta = wt("pah", "brasil")
        paste(img, clock_rewind(420, -t * 9), CX, 760, pop(t, ta, 0.25))
        txt(img, "VOLTOU *+10 ANOS*", 110, CX, 1100, pop(t, wt("pah", "voltou") - 0.1), hl=RED)
        txt(img, "NO TEMPO", 90, CX, 1230, pop(t, wt("pah", "tempo") - 0.1))

    @shot(S["volta"])
    def s_recup(img, lt, t):
        year = 2021 + 3 * ease_out_cubic(clamp((t - S["volta"]) / 1.8))
        chart(img, t, year, GREEN)
        num(img, "76,6", 230, CX, 470, pop(t, wt("volta", "setenta") - 0.05), color=GREEN, glow=GREEN)
        stamp(img, "RECORDE!", t, wt("volta", "recorde"), CX, 760, YEL, 140, rot=-10)

    @shot(S["jeanne"], flash=True)
    def s_122(img, lt, t):
        tc = wt("jeanne", "cento")
        v = 122 * ease_out_cubic(clamp((t - tc + 0.1) / 0.9))
        txt(img, "RECORDE *HUMANO*", 90, CX, 420, pop(t, S["jeanne"]))
        num(img, f"{int(round(v))}", 480, CX, 800, pop(t, tc - 0.1), color=YEL, glow=RED)
        txt(img, "ANOS", 110, CX, 1080, pop(t, wt("jeanne", "anos")))

    @shot(wt("jeanne", "francesa"))
    def s_lady(img, lt, t):
        ta = wt("jeanne", "francesa")
        paste(img, lady(500), CX, 760, pop(t, ta, 0.3), rot=3 * math.sin(t * 3))
        d = ImageDraw.Draw(img)
        for k in range(4):   # fumaça do cigarro
            ph = (t * 0.8 + k * 0.25) % 1
            x, y = CX + 160 + 30 * math.sin(ph * 8 + k), 620 - ph * 240
            r = 14 + ph * 34
            d.ellipse((x - r, y - r, x + r, y + r), fill=(230, 230, 230, int(170 * (1 - ph))))
        pill(img, "JEANNE CALMENT", 52, CX, 400, pop(t, ta + 0.1), bg=CYAN)
        tf = wt("jeanne", "fumou")
        if t >= tf - 0.1:
            txt(img, "FUMOU ATÉ OS *117*", 96, CX, 1110, pop(t, tf - 0.1))
        stamp(img, "NÃO TENTE EM CASA", t, wt("jeanne", "tenta") - 0.1, CX, 1270, RED, 64, rot=-6)

    @shot(S["insight"], flash=True)
    def s_insight(img, lt, t):
        d = ImageDraw.Draw(img)
        x0, x1, y = 90, 910, 760
        d.rounded_rectangle((x0, y - 40, x1, y + 40), 40, fill=(255, 255, 255, 60), outline=WHITE + (255,), width=5)
        tn = wt("insight", "não"); tp2 = wt("insight", "parou")
        txt(img, "NÃO GANHAMOS ANOS", 76, CX, 480, pop(t, tn - 0.1))
        txt(img, "NO *FIM*", 96, CX, 580, pop(t, wt("insight", "fim") - 0.1), hl=RED)
        if t >= wt("insight", "fim"):
            u = clamp((t - wt("insight", "fim")) / 0.25)
            d.rounded_rectangle((x1 - 180, y - 40, x1 - 180 + 180 * u, y + 40), 40, fill=RED + (200,))
            d.line((CX - 260, 580, CX - 260 + 520 * u, 580), fill=RED + (255,), width=14)
        if t >= tp2 - 0.1:
            u = clamp((t - tp2) / 0.4)
            d.rounded_rectangle((x0, y - 40, x0 + 260 * u, y + 40), 40, fill=GREEN + (255,))
            txt(img, "PARAMOS DE MORRER", 86, CX, 980, pop(t, tp2 - 0.1))
            txt(img, "NO *COMEÇO*", 140, CX, 1120, pop(t, wt("insight", "começo") - 0.1), hl=GREEN)

    @shot(S["boleto"])
    def s_boleto(img, lt, t):
        paste(img, boleto(460), CX, 780, pop(t, S["boleto"], 0.3), rot=-8 + 3 * math.sin(t * 5))
        txt(img, "O *BOLETO* CHEGA", 110, CX, 420, pop(t, S["boleto"] + 0.1))

    t3 = wt("boleto", "três")

    @shot(t3, flash=True)
    def s_donut(img, lt, t):
        u = ease_out_cubic(clamp((t - t3) / 1.0))
        d = ImageDraw.Draw(img)
        r = 280
        d.ellipse((CX - r, 760 - r, CX + r, 760 + r), outline=(255, 255, 255, 60), width=70)
        d.arc((CX - r, 760 - r, CX + r, 760 + r), -90, -90 + 270 * u, fill=RED + (255,), width=70)
        num(img, "3 EM 4", 150, CX, 760, pop(t, t3), color=WHITE, glow=RED)
        txt(img, "MORTES: *DOENÇA CRÔNICA*", 66, CX, 1150, pop(t, wt("boleto", "doença") - 0.1), hl=RED)
        for im, ta, (x, y) in ((heart(200, max(0, math.sin(t * 8)) ** 2), wt("boleto", "coração"), (CX - 330, 400)),
                               (brain(200), wt("boleto", "cérebro"), (CX + 330, 400)), (drop(190), wt("boleto", "diabetes"), (CX, 1320))):
            paste(img, im, x, y, pop(t, ta - 0.05, 0.25))

    @shot(S["costas"])
    def s_costas(img, lt, t):
        tq2 = wt("costas", "é")
        txt(img, "QUANTO VOCÊ VAI VIVER?", 80, CX, 520, pop(t, S["costas"]))
        if t >= tq2 - 0.05:
            d = ImageDraw.Draw(img)
            u = clamp((t - tq2) / 0.2)
            d.line((CX - 420, 520, CX - 420 + 840 * u, 520), fill=RED + (255,), width=14)
            txt(img, "QUANTO VOCÊ VIVE", 90, CX, 700, pop(t, tq2))
            txt(img, "*SEM DOR NAS COSTAS?*", 96, CX, 830, pop(t, wt("costas", "sem") - 0.1))
            paste(img, backpain(420), CX, 1150, pop(t, wt("costas", "dor") - 0.1, 0.3), rot=4 * math.sin(t * 7))

    @shot(S["cta"], flash=True)
    def s_cta(img, lt, t):
        b = 1 + 0.06 * abs(math.sin(t * 6))
        paste(img, bubble(380), CX, 650, pop(t, S["cta"], 0.3) * b, rot=-6)
        txt(img, "*COMENTA*", 150, CX, 950, pop(t, S["cta"] + 0.1))
        txt(img, "A PRÓXIMA PERGUNTA CHAPADA", 64, CX, 1090, pop(t, wt("cta", "próxima")))

    SHOTS.sort(key=lambda s: s[0])


# ---------------------------------------------------------------- legendas
NUMS = [("mil novecentos e quarenta", "1940"), ("quarenta e cinco", "45"), ("oitenta e nove", "89"), ("cento e cinquenta", "150"),
        ("doze", "12"), ("setenta e seis anos e meio", "76,5 ANOS"), ("dois mil e vinte e um", "2021"), ("três", "3"),
        ("setenta e seis vírgula seis", "76,6"), ("dois mil e vinte e quatro", "2024"), ("cento e vinte e dois", "122"),
        ("cento e dezessete", "117"), ("quatro", "4"), ("um", "1"), ("mil", "1.000")]
CHUNKS = []


def build_chunks():
    import json, re
    lines = json.load(open(os.path.join(HERE, "narracao.json")))
    by = {}
    for w in P["words"]:
        by.setdefault(w["line"], []).append(dict(w))
    for l in lines:
        ws = by.get(l["id"], [])
        orig = l["text"].split()
        if len(orig) == len(ws):
            for w, o in zip(ws, orig):
                w["w"] = o
        norm = lambda x: re.sub(r"[^\wÀ-ú]", "", x).lower()
        toks, j = [], 0
        while j < len(ws):
            hit = None
            for fr, rep in NUMS:
                fw = fr.split()
                if [norm(x["w"]) for x in ws[j:j + len(fw)]] == fw:
                    hit = (len(fw), rep); break
            if hit and l["id"] != "marca":
                n, rep = hit
                tail = re.sub(r"^[\wÀ-ú]+", "", ws[j + n - 1]["w"])
                toks.append({"w": rep + tail, "t": ws[j]["t"], "d": ws[j + n - 1]["t"] + ws[j + n - 1]["d"] - ws[j]["t"]}); j += n
            else:
                toks.append(ws[j]); j += 1
        cur = []
        for w in toks:
            if cur and (len(cur) >= 3 or sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > 18 or re.search(r"[.?!:…]$", cur[-1]["w"])):
                CHUNKS.append(cur); cur = []
            cur.append(w)
        if cur:
            CHUNKS.append(cur)


def caption(img, t):
    import re
    for i, ch in enumerate(CHUNKS):
        a = ch[0]["t"] - 0.04
        b = CHUNKS[i + 1][0]["t"] - 0.04 if i + 1 < len(CHUNKS) else ch[-1]["t"] + ch[-1]["d"] + 0.3
        b = min(b, ch[-1]["t"] + ch[-1]["d"] + 0.35)
        if a <= t < b:
            parts = []
            for w in ch:
                s_ = re.sub(r"[,.:;]+$", "", w["w"]).upper()
                act = t >= w["t"] - 0.03
                last_act = w is [x for x in ch if t >= x["t"] - 0.03][-1] if any(t >= x["t"] - 0.03 for x in ch) else False
                parts.append(f"*{s_}*" if last_act else s_)
            txt(img, " ".join(parts), 72, CX, 1470, 0.85 + 0.15 * pop(t, a, 0.15), maxw=900)
            return


# ---------------------------------------------------------------- render
def shake(t):
    ox = oy = 0.0
    for t0, amp in ((wt("hook", "spoiler") + 0.5, 22), (wt("pah", "pah"), 40), (wt("media", "mente"), 16), (wt("boleto", "três"), 18)):
        dt = t - t0
        if 0 <= dt < 0.7:
            a = amp * math.exp(-dt * 6)
            ox += a * math.sin(dt * 80); oy += a * math.cos(dt * 63)
    return ox, oy


def render_frame(f):
    t = f / FPS
    bg = background(t)
    img = Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    particles(img, t)
    k = max(i for i, s_ in enumerate(SHOTS) if s_[0] <= t or i == 0)
    t0, fn, fl = SHOTS[k]
    stage = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(stage, t - t0, t)
    # entrada do corte: zoom de impacto + leve zoom contínuo
    lt = t - t0
    # soco de zoom forte no corte + soco leve a cada bloco de legenda (~1 por segundo)
    beats = [c[0]["t"] for c in CHUNKS if t0 < c[0]["t"] <= t]
    lb = t - beats[-1] if beats else 9
    z = 1 + 0.18 * (1 - ease_out_cubic(clamp(lt / 0.2))) + 0.06 * (1 - ease_out_cubic(clamp(lb / 0.18))) + 0.03 * clamp(lt / 3)
    sx, sy = shake(t)
    if abs(z - 1) > 1e-3 or sx or sy:
        stage = stage.transform((W, H), Image.AFFINE, (1 / z, 0, CX - (CX + sx) / z, 0, 1 / z, CY - (CY + sy) / z), Image.BICUBIC)
    img.alpha_composite(stage)
    caption(img, t)
    if fl and lt < 0.12:
        img = Image.blend(img, Image.new("RGBA", img.size, (255, 255, 255, 255)), 0.85 * (1 - lt / 0.12))
    return img.convert("RGB")


def init():
    E.init()
    build_bg()
    build_shots()
    build_chunks()


def render_range(args):
    a, b, path = args
    init()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(render_frame(f).tobytes())
    p.stdin.close(); p.wait()
    return path


def sound_events():
    init()
    return dict(cuts=[(s_[0], s_[2]) for s_ in SHOTS], S=S, E=EN, pah=wt("pah", "pah"), nao=wt("hook", "spoiler") + 0.5,
                recorde=wt("volta", "recorde"), mente=wt("media", "mente"), tres=wt("boleto", "três"), boleto=S["boleto"],
                marca=S["marca"], cta=S["cta"], heart=(wt("boleto", "coração"), S["costas"]), tio=wt("tio", "nem"),
                tenta=wt("jeanne", "tenta") - 0.1, conta=wt("media", "quarenta"))


def main():
    os.makedirs(OUT, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "times":
        init()
        for t0, fn, fl in SHOTS:
            print(f"{t0:6.2f} {fn.__name__}{' (flash)' if fl else ''}")
        print("DUR", DUR)
    elif cmd == "preview":
        init()
        pd = os.path.join(OUT, os.environ.get("PDIR", "preview")); os.makedirs(pd, exist_ok=True)
        for ts in sys.argv[2:]:
            f = min(NFRAMES - 1, int(round(float(ts) * FPS)))
            im = render_frame(f)
            if os.environ.get("GUIDES"):
                d = ImageDraw.Draw(im); d.line((960, 0, 960, H), fill=(255, 0, 0), width=2); d.line((0, 1620, W, 1620), fill=(255, 0, 0), width=2)
            im.save(os.path.join(pd, f"f{f:04d}.png"))
        print("ok")
    elif cmd == "video":
        from multiprocessing import Pool
        nw = int(os.environ.get("WORKERS", 4))
        step = math.ceil(NFRAMES / (nw * 3))
        jobs = [(i, min(NFRAMES, i + step), os.path.join(OUT, f"seg{k:02d}.mp4")) for k, i in enumerate(range(0, NFRAMES, step))]
        with Pool(nw) as pool:
            segs = pool.map(render_range, jobs, chunksize=1)
        open(os.path.join(OUT, "segs.txt"), "w").write("".join(f"file '{s}'\n" for s in segs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "segs.txt"), "-c", "copy",
                        os.path.join(OUT, "video_mudo.mp4")], check=True)
        print("video ok")


if __name__ == "__main__":
    main()
