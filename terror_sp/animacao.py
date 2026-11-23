#!/usr/bin/env python3
"""
"E se um assassino de filme de terror atacasse São Paulo?"
Animação vertical 1080x1920 @30fps, toda desenhada com formas vetoriais (Pillow + numpy),
áudio sintetizado em código + narração (Gemini TTS, gerada por narracao.py), exportada com ffmpeg.

Uso:
  python3 animacao.py --preview      # salva PNGs de conferência em previews/
  python3 animacao.py                # renderiza o MP4 final (saida/terror_sp.mp4)
"""
import math, os, random, subprocess, sys, wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
SR = 48000

# ---------------------------------------------------------------- paleta
K = (10, 12, 15)            # contorno
WHITE = (245, 245, 240)
SKY_D = (9, 27, 34)
PET_D = (14, 40, 48)
PET = (24, 66, 78)
PET_L = (44, 98, 110)
PET_XL = (78, 132, 140)
CON_D = (58, 64, 68)
CON = (98, 106, 108)
CON_L = (140, 146, 146)
CON_XL = (178, 182, 180)
RED = (214, 28, 38)
RED_D = (130, 16, 24)
YEL = (222, 186, 38)        # capa de chuva (pedida no briefing)
YEL_D = (166, 128, 18)
YEL_L = (250, 226, 120)
BAG = (212, 200, 172)
BAG_D = (166, 152, 122)
SKIN = (196, 184, 166)
SKIN_D = (150, 138, 122)
DROP = (170, 205, 215)

FONT_PATH = os.path.join(HERE, "fonts", "Anton-Regular.ttf")
if not os.path.exists(FONT_PATH):
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


@lru_cache(None)
def font(size):
    return ImageFont.truetype(FONT_PATH, int(size))


# ---------------------------------------------------------------- utilidades
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def back_out(x):
    x = clamp(x)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def seg(t, a, b):
    """progresso 0..1 de t no intervalo [a,b]"""
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def lerp(a, b, x):
    return a + (b - a) * x


def lerpc(c1, c2, x):
    return tuple(int(lerp(a, b, x)) for a, b in zip(c1, c2))


def rot(pts, ang, cx, cy):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def poly(d, pts, fill, ow=8):
    d.polygon(pts, fill=fill, outline=K if ow else None, width=max(1, int(ow)) if ow else 1)


def limb(d, a, b, w, col, ow):
    w, ow = int(w), int(ow)
    for (ww, cc) in ((w + 2 * ow, K), (w, col)):
        d.line([a, b], fill=cc, width=ww)
        r = ww / 2
        for p in (a, b):
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=cc)


def circle(d, x, y, r, fill, ow=6):
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=K if ow else None, width=int(ow) if ow else 0)


def text(d, xy, s, size, fill=WHITE, anchor="mm", stroke=None, stroke_fill=K, spacing=4):
    f = font(size)
    if stroke is None:
        stroke = max(2, int(size * 0.09))
    d.multiline_text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke,
                     stroke_fill=stroke_fill, align="center", spacing=spacing)


def wrap(s, size, maxw):
    f = font(size)
    out = []
    for para in s.split("\n"):
        words, line = para.split(), ""
        for w_ in words:
            cand = (line + " " + w_).strip()
            if f.getlength(cand) <= maxw or not line:
                line = cand
            else:
                out.append(line)
                line = w_
        out.append(line)
    return "\n".join(out)


def vgrad(img, box, c1, c2):
    x0, y0, x1, y1 = [int(v) for v in box]
    d = ImageDraw.Draw(img)
    hgt = max(1, y1 - y0)
    for y in range(y0, y1, 4):
        d.rectangle([x0, y, x1, y + 4], fill=lerpc(c1, c2, (y - y0) / hgt))


# ---------------------------------------------------------------- personagens
def draw_bag(d, cx, cy, s, ang=0.0, ow=None, eyes=True, squash=1.0):
    """máscara de saco de pão (centro aprox. cx,cy)"""
    ow = ow or max(3, 8 * s)
    def T(pts):
        p = [(cx + x * s, cy - y * s * squash) for x, y in pts]
        return rot(p, ang, cx, cy) if ang else p
    body = [(-58, -75), (58, -75), (62, 55), (48, 82), (30, 62), (12, 86), (-8, 60), (-26, 84), (-44, 60), (-62, 72)]
    poly(d, T(body), BAG, ow)
    d.polygon(T([(26, -73), (56, -73), (60, 52), (48, 74), (30, 56), (22, 50)]), fill=BAG_D)
    poly(d, T(body), None, ow)
    for (a, b) in (((-40, 40), (-30, -60)), ((10, 50), (16, -70)), ((-58, 20), (-20, 30))):
        d.line(T([a, b]), fill=BAG_D, width=max(2, int(3 * s)))
    # carimbo vermelho desbotado
    sx, sy = T([(0, -42)])[0]
    d.text((sx, sy), "PADARIA", font=font(max(8, int(20 * s))), fill=(160, 70, 62), anchor="mm")
    if eyes:
        for ex in (-24, 24):
            ex_, ey_ = T([(ex, 15)])[0]
            d.ellipse([ex_ - 14 * s, ey_ - 11 * s, ex_ + 14 * s, ey_ + 11 * s], fill=K)
    return T


def villain(d, cx, fy, s, t=0.0, walk=None, pose="walk", sx=1.0, sy=1.0, lean=0.0,
            mask=True, umbrella=True, glow=1.0, drips=True, suitcase=False):
    """O Mascarado da Garoa. cx,fy = centro dos pés; s = escala (s=1 -> ~640px)."""
    ow = max(3, 8.5 * s)

    def P(x, y):
        return (cx + (x + y * lean) * s * sx, fy - y * s * sy)

    sw = math.sin(walk * 2 * math.pi) if walk is not None else 0.0
    bob = abs(math.cos(walk * 2 * math.pi)) * 8 if walk is not None else 0.0
    fy0 = fy
    fy = fy - bob * s

    # pernas
    for side, ph in ((-1, sw), (1, -sw)):
        hip = P(side * 24, 200)
        foot = (cx + (side * 26 + 26 * ph) * s * sx, fy0 - 26 * s * sy)
        limb(d, hip, foot, 40 * s * sx, (38, 44, 50), ow)
        bx, by = foot
        d.rounded_rectangle([bx - 30 * s * sx, by - 6 * s, bx + 34 * s * sx, by + 26 * s * sy],
                            radius=10 * s, fill=K)
    # capuz
    hx0, hy0 = P(-84, 625)
    hx1, hy1 = P(84, 432)
    d.ellipse([min(hx0, hx1), hy0, max(hx0, hx1), hy1], fill=YEL_D, outline=K, width=int(ow))

    # braço de trás
    poses = {
        "walk": dict(L=((-108, 365), (-104 - 12 * sw, 268)), R=((112, 372), (112 + 14 * sw, 290)), ua=72),
        "raise": dict(L=((-160, 430), (-215, 520)), R=((140, 565), (150, 690)), ua=-88),
        "squish": dict(L=((-130, 520), (-115, 615)), R=((130, 520), (115, 615)), ua=None),
        "shock": dict(L=((-135, 400), (-62, 520)), R=((135, 400), (62, 520)), ua=None),
        "carry": dict(L=((-112, 360), (-118, 255)), R=((140, 470), (165, 590)), ua=None),
        "drive": dict(L=((-60, 380), (40, 420)), R=((150, 430), (210, 560)), ua=None),
        "shrug": dict(L=((-150, 400), (-190, 470)), R=((150, 400), (190, 470)), ua=None),
    }
    pz = poses[pose]
    shL, shR = P(-78, 456), P(78, 456)
    limb(d, shL, P(*pz["L"][0]), 44 * s * sx, YEL, ow)
    limb(d, P(*pz["L"][0]), P(*pz["L"][1]), 40 * s * sx, YEL, ow)
    circle(d, *P(*pz["L"][1]), 22 * s, K, 0)

    if suitcase:
        hx, hy = P(*pz["L"][1])
        bw, bh = 300 * s, 190 * s
        d.rounded_rectangle([hx - bw / 2, hy + 18 * s, hx + bw / 2, hy + 18 * s + bh], radius=14 * s,
                            fill=(120, 72, 52), outline=K, width=int(ow))
        d.rounded_rectangle([hx - 40 * s, hy - 10 * s, hx + 40 * s, hy + 22 * s], radius=10 * s,
                            outline=K, width=int(ow))
        d.rectangle([hx - bw / 2 + 12 * s, hy + 70 * s, hx + bw / 2 - 12 * s, hy + 150 * s], fill=WHITE,
                    outline=K, width=max(2, int(4 * s)))
        text(d, (hx, hy + 110 * s), "VOLTANDO PRO\nACAMPAMENTO", 28 * s, fill=K, stroke=0, spacing=0)

    # capa
    coat = [(-80, 472), (80, 472), (120, 172), (72, 160), (0, 170), (-72, 160), (-120, 172)]
    poly(d, [P(*p) for p in coat], YEL, ow)
    d.polygon([P(*p) for p in [(22, 470), (80, 470), (118, 174), (72, 162), (34, 167)]], fill=YEL_D)
    poly(d, [P(*p) for p in coat], None, ow)
    d.line([P(0, 466), P(0, 172)], fill=K, width=max(2, int(ow * 0.6)))
    for by in (420, 355, 290, 225):
        circle(d, *P(-14, by), 7 * s, K, 0)
    for (a, b) in (((-60, 430), (-72, 330)), ((-50, 300), (-58, 240)), ((-92, 220), (-98, 190))):
        d.line([P(*a), P(*b)], fill=YEL_L, width=max(2, int(6 * s)))
    # gotas pingando da capa
    if drips:
        for i, dx in enumerate((-95, -30, 50, 104)):
            ph = (t * 1.3 + i * 0.37) % 1.0
            x_, y_ = P(dx, 160)
            y_ += ph * 150 * s
            r = 7 * s
            d.ellipse([x_ - r, y_ - r * 1.4, x_ + r, y_ + r], fill=DROP, outline=K, width=max(1, int(2 * s)))

    # cabeça
    hcx, hcy = P(0, 530)
    if mask:
        draw_bag(d, hcx, hcy, s * min(sx, 1.25), ow=ow, squash=sy if pose == "squish" else 1.0)
        for ex in (-24, 24):
            ex_, ey_ = P(ex, 545)
            r = 4.8 * s * glow
            d.ellipse([ex_ - r, ey_ - r, ex_ + r, ey_ + r], fill=RED)
    else:
        face = [P(x, y) for x, y in [(-50, 455), (50, 455), (56, 560), (40, 600), (-40, 600), (-56, 560)]]
        poly(d, face, SKIN, ow)
        d.polygon([P(x, y) for x, y in [(20, 457), (50, 457), (55, 560), (40, 598), (24, 598)]], fill=SKIN_D)
        poly(d, face, None, ow)
        for ex in (-22, 24):
            circle(d, *P(ex, 545), 19 * s, WHITE, ow * 0.6)
            circle(d, *P(ex + 2, 543), 4.5 * s, K, 0)
            d.line([P(ex - 18, 578), P(ex + 14, 590)], fill=K, width=max(2, int(6 * s)))
        mx, my = P(0, 490)
        d.ellipse([mx - 18 * s, my - 26 * s, mx + 18 * s, my + 22 * s], fill=K)
        for i in range(3):  # cabelos arrepiados
            d.line([P(-20 + i * 20, 600), P(-30 + i * 30, 650)], fill=K, width=max(2, int(6 * s)))
        for k_, (dx, dy) in enumerate(((-70, 590), (72, 570))):
            x_, y_ = P(dx, dy)
            y_ += ((t * 2 + k_ * 0.5) % 1) * 30 * s
            d.ellipse([x_ - 8 * s, y_ - 12 * s, x_ + 8 * s, y_ + 8 * s], fill=DROP, outline=K, width=max(1, int(3 * s)))

    # braço da frente + guarda-chuva quebrado
    limb(d, shR, P(*pz["R"][0]), 44 * s * sx, YEL, ow)
    limb(d, P(*pz["R"][0]), P(*pz["R"][1]), 40 * s * sx, YEL, ow)
    hand = P(*pz["R"][1])
    if umbrella and pz["ua"] is not None:
        broken_umbrella(d, hand, math.radians(pz["ua"]) + 0.05 * sw, s, ow)
    circle(d, *hand, 23 * s, K, 0)


def broken_umbrella(d, hand, ang, s, ow):
    ux, uy = math.cos(ang), math.sin(ang)
    vx, vy = -uy, ux
    hx, hy = hand

    def Q(u, v):
        return (hx + (u * ux + v * vx) * s, hy + (u * uy + v * vy) * s)
    # cabo em J
    pts = [Q(-30 + 22 * math.cos(a), 22 * math.sin(a)) for a in np.linspace(0, math.pi, 8)]
    d.line(pts, fill=K, width=int(12 * s))
    d.line([Q(-10, 0), Q(340, 0)], fill=K, width=int(10 * s))
    canopy = [(320, 0), (120, -66), (150, -34), (100, -26), (128, -4), (96, 22), (140, 38), (110, 72)]
    poly(d, [Q(*p) for p in canopy], (26, 30, 36), ow)
    d.polygon([Q(*p) for p in [(320, 0), (140, 38), (110, 72)]], fill=(50, 56, 64))
    for a, b, c in (((300, -6), (190, -80), (130, -118)), ((300, 6), (170, 74), (150, 118)),
                    ((280, 0), (200, -30), (178, -64))):
        d.line([Q(*a), Q(*b), Q(*c)], fill=K, width=max(2, int(6 * s)))


def person(d, cx, fy, s, body=CON, hat=None, vest=False, arm=None, face="neutral", flip=1, walk=None, t=0.0):
    ow = max(3, 7 * s)
    sw = math.sin(walk * 2 * math.pi) if walk is not None else 0

    def P(x, y):
        return (cx + x * s * flip, fy - y * s)
    for side, ph in ((-1, sw), (1, -sw)):
        limb(d, P(side * 20, 190), P(side * 22 + 22 * ph, 22), 34 * s, CON_D, ow)
        x_, y_ = P(side * 22 + 22 * ph, 22)
        d.rounded_rectangle([x_ - 26 * s, y_ - 6 * s, x_ + 30 * s, y_ + 22 * s], radius=8 * s, fill=K)
    torso = [(-70, 400), (70, 400), (78, 180), (-78, 180)]
    poly(d, [P(*p) for p in torso], body, ow)
    if vest:
        for y in (330, 250):
            d.rectangle([min(P(-74, y)[0], P(74, y)[0]), P(0, y)[1], max(P(-74, y)[0], P(74, y)[0]),
                         P(0, y - 18)[1]], fill=WHITE)
        poly(d, [P(*p) for p in torso], None, ow)
    # braços
    limb(d, P(-68, 385), P(-90, 220), 32 * s, body, ow)
    if arm == "up":
        limb(d, P(68, 385), P(140, 520), 32 * s, body, ow)
        hand = P(140, 520)
    else:
        limb(d, P(68, 385), P(92, 220), 32 * s, body, ow)
        hand = P(92, 220)
    circle(d, *P(-90, 220), 18 * s, SKIN, ow * 0.6)
    circle(d, *hand, 18 * s, SKIN, ow * 0.6)
    # cabeça
    hx, hy = P(0, 470)
    circle(d, hx, hy, 62 * s, SKIN, ow)
    d.chord([hx - 62 * s, hy - 62 * s, hx + 62 * s, hy + 62 * s], -60, 60, fill=SKIN_D) if flip > 0 else \
        d.chord([hx - 62 * s, hy - 62 * s, hx + 62 * s, hy + 62 * s], 120, 240, fill=SKIN_D)
    circle(d, hx, hy, 62 * s, None, ow)
    ex = 22 * flip
    if face == "angry":
        for e in (-1, 1):
            x_, y_ = P(ex + e * 18, 478)
            circle(d, x_, y_, 6 * s, K, 0)
            d.line([(x_ - 12 * s, y_ - 16 * s - e * 5 * s * flip), (x_ + 12 * s, y_ - 16 * s + e * 5 * s * flip)],
                   fill=K, width=max(2, int(6 * s)))
        d.line([P(ex - 14, 440), P(ex + 18, 444)], fill=K, width=max(2, int(6 * s)))
    elif face == "bored":
        for e in (-1, 1):
            x_, y_ = P(ex + e * 18, 478)
            d.line([(x_ - 10 * s, y_), (x_ + 10 * s, y_)], fill=K, width=max(2, int(6 * s)))
        d.line([P(ex - 10, 445), P(ex + 14, 445)], fill=K, width=max(2, int(5 * s)))
    else:
        for e in (-1, 1):
            circle(d, *P(ex + e * 18, 478), 6 * s, K, 0)
        d.arc([P(ex - 14, 460)[0] - 0, P(0, 460)[1], P(ex + 14, 460)[0] + 1, P(0, 430)[1]], 20, 160,
              fill=K, width=max(2, int(5 * s))) if flip > 0 else None
    if hat == "cap":
        d.chord([hx - 64 * s, hy - 74 * s, hx + 64 * s, hy + 30 * s], 180, 360, fill=PET, outline=K, width=int(ow))
        bx = hx + 40 * s * flip
        d.rectangle([min(hx, bx + 45 * s * flip), hy - 30 * s, max(hx, bx + 45 * s * flip), hy - 18 * s], fill=K)
    return hand


def car(d, x, y, s, body=CON_L, tail=True, head=True, flip=1, ow=None, driver=None):
    """carro visto de lado; x,y = centro inferior (chão)."""
    ow = ow or max(3, 7 * s)

    def P(px, py):
        return (x + px * s * flip, y - py * s)
    shape = [(-200, 30), (200, 30), (210, 90), (150, 110), (90, 180), (-110, 180), (-160, 110), (-210, 100)]
    poly(d, [P(*p) for p in shape], body, ow)
    d.polygon([P(*p) for p in [(-200, 30), (200, 30), (206, 60), (-206, 60)]], fill=lerpc(body, K, 0.35))
    poly(d, [P(*p) for p in shape], None, ow)
    win = [(-95, 168), (80, 168), (130, 112), (-140, 112)]
    poly(d, [P(*p) for p in win], (40, 70, 80), ow * 0.8)
    d.line([P(-10, 168), P(-10, 112)], fill=K, width=int(ow))
    if driver is not None:
        driver()
    for wx in (-120, 120):
        circle(d, *P(wx, 30), 42 * s, K, 0)
        circle(d, *P(wx, 30), 18 * s, CON, 0)
    if tail:
        tx = -200 if flip > 0 else 200
        d.rectangle([min(P(-206, 95)[0], P(-186, 95)[0]), P(0, 95)[1], max(P(-206, 95)[0], P(-186, 95)[0]),
                     P(0, 72)[1]], fill=RED)
    if head:
        d.rectangle([min(P(196, 88)[0], P(212, 88)[0]), P(0, 88)[1], max(P(196, 88)[0], P(212, 88)[0]),
                     P(0, 70)[1]], fill=WHITE)


def skyline(d, y, rnd, col, hmin, hmax, wmin=60, wmax=160, lights=None, x0=-50, x1=W + 50):
    x = x0
    while x < x1:
        w_ = rnd.randint(wmin, wmax)
        h_ = rnd.randint(hmin, hmax)
        d.rectangle([x, y - h_, x + w_, y + 10], fill=col)
        if rnd.random() < 0.3:
            d.rectangle([x + w_ * 0.4, y - h_ - 40, x + w_ * 0.45, y - h_], fill=col)
        if lights:
            for wy in range(int(y - h_ + 20), int(y - 20), 34):
                for wx in range(int(x + 12), int(x + w_ - 16), 26):
                    if rnd.random() < 0.12:
                        d.rectangle([wx, wy, wx + 10, wy + 14], fill=lights)
        x += w_ + rnd.randint(-10, 20)


# ---------------------------------------------------------------- cenas
# cada cena: função draw(img, d, t, T) -> dict com efeitos (shake, flash)

def scene_intro(img, d, t, T):
    vgrad(img, (0, 0, W, H), SKY_D, PET_D)
    rnd = random.Random(3)
    skyline(d, 1250, rnd, (16, 44, 54), 350, 900, lights=(60, 100, 110))
    rnd = random.Random(8)
    skyline(d, 1450, rnd, (10, 28, 34), 200, 650, 90, 200, lights=(40, 70, 78))
    d.rectangle([0, 1450, W, H], fill=(8, 20, 25))
    # silhueta do vilão na neblina, se aproximando
    s = lerp(0.78, 0.95, ease(t / T))
    villain(d, 540, 1830, s, t=t, walk=t * 0.55, glow=1.0 + 0.4 * math.sin(t * 9))
    fx = {}
    if t < 0.35:
        fx["flash"] = 1 - t / 0.35
    fx["shake"] = 14 * max(0, 1 - t / 0.6)
    return fx


def scene_lake(img, d, t, T):
    vgrad(img, (0, 0, W, 980), SKY_D, PET_D)
    # lua escondida
    circle(d, 820, 280, 70, (150, 170, 172), 0)
    d.ellipse([700, 250, 980, 330], fill=PET_D)
    # árvores do parque
    rnd = random.Random(11)
    for i in range(16):
        x = i * 75 + rnd.randint(-20, 20)
        r = rnd.randint(70, 120)
        circle(d, x, 900 - rnd.randint(0, 60), r, (12, 36, 40), 0)
    skyline(d, 760, random.Random(4), (20, 52, 62), 120, 380, lights=(70, 110, 118))
    for i in range(16):
        x = i * 75 + 30
        circle(d, x, 960, 90, (8, 26, 30), 0)
    d.rectangle([0, 960, W, 1010], fill=(8, 26, 30))
    # postes
    for px in (130, 960):
        d.rectangle([px - 6, 640, px + 6, 1000], fill=K)
        circle(d, px, 640, 20, CON_XL, 4)
    # lago
    vgrad(img, (0, 1000, W, H), (22, 60, 72), (10, 30, 38))
    WL = 1330  # linha d'água onde está o vilão
    for i in range(14):
        y = 1040 + i * 60 + (t * 20 % 60)
        d.line([(80 + (i * 97) % 400, y), (260 + (i * 97) % 400, y)], fill=PET_L, width=4)
        d.line([(600 - (i * 53) % 300, y + 20), (760 - (i * 53) % 300, y + 20)], fill=PET_L, width=4)
    vx = 470
    rise = ease_out(seg(t, 0.9, 2.1))
    fx = {}
    # bolhas
    if t < 2.0:
        rnd = random.Random(int(t * 12))
        for i in range(10):
            bx = vx + rnd.randint(-110, 110)
            by = WL - rnd.randint(0, 40)
            r = rnd.randint(8, 26) * (1 if t < 1.2 else 0.6)
            circle(d, bx, by, r, PET_L, 4)
    # vilão saindo da água (pés abaixo da linha d'água)
    fy = WL + lerp(700, 150, rise)
    shrink = ease(seg(t, 3.3, 3.8))
    villain(d, vx, fy, 0.95, t=t, pose="walk" if t < 3.3 else "shrug", sy=1 - 0.08 * shrink,
            glow=1.2 if t < 3.3 else 0.4)
    # água na frente
    vgrad(img, (0, WL, W, H), (20, 56, 68), (10, 30, 38))
    d.line([(0, WL), (W, WL)], fill=PET_XL, width=5)
    if rise > 0:
        wv = 1 + 0.15 * math.sin(t * 8)
        d.ellipse([vx - 200 * wv, WL - 26, vx + 200 * wv, WL + 26], outline=PET_XL, width=6)
        d.ellipse([vx - 290 * wv, WL - 40, vx + 290 * wv, WL + 40], outline=PET_L, width=4)
        for k_ in range(6):  # respingos
            a = k_ / 6 * math.pi + 0.2
            pr = seg(t, 0.9, 1.6)
            if 0 < pr < 1:
                x_ = vx + math.cos(a) * 260 * pr * (1 if k_ % 2 else -1)
                y_ = WL - math.sin(a) * 300 * (pr - pr * pr) * 2
                circle(d, x_, y_, 14, DROP, 4)
    if 0.9 < t < 1.8:
        fx["shake"] = 16 * (1 - seg(t, 0.9, 1.8))
    # fiscal entra pela direita
    if t > 2.2:
        fxp = lerp(1350, 860, ease_out(seg(t, 2.2, 3.0)))
        hand = person(d, fxp, 1500, 0.92, body=(70, 96, 92), hat="cap", vest=True,
                      arm="up" if t > 2.9 else None, face="angry", flip=-1, walk=t * 1.6 if t < 3.0 else None, t=t)
        d.rectangle([fxp - 40, 1500 - 470 * 0.92 - 60, fxp - 6, 1500 - 470 * 0.92 - 48], fill=RED)  # apito
        if t > 2.9:
            pop = back_out(seg(t, 2.9, 3.25))
            tw, th = 330 * pop, 210 * pop
            tx, ty = hand[0] - 80, hand[1] - 100
            box = [tx - tw / 2, ty - th / 2, tx + tw / 2, ty + th / 2]
            d.rectangle(box, fill=WHITE, outline=K, width=8)
            if pop > 0.5:
                text(d, (tx, ty - 50 * pop), "MULTA", 70 * pop, fill=RED, stroke=0)
                text(d, (tx, ty + 40 * pop), "NADAR NO LAGO\nR$ 130,00", 34 * pop, fill=K, stroke=0, spacing=2)
        if 2.4 < t < 3.2:  # "PRRRIII!" do apito
            text(d, (fxp - 210, 900), "PRIIIII!", 90, fill=WHITE, stroke=8)
    if 2.9 < t < 3.3:
        fx["shake"] = 10
    return fx


def masp(d, x, y, lit):
    red = lerpc(RED_D, RED, lit)
    redd = lerpc((80, 10, 16), RED_D, lit)
    # vão livre: caixa de vidro suspensa por dois pórticos vermelhos
    box = [x - 330, y - 360, x + 330, y - 170]
    d.rectangle(box, fill=lerpc((26, 40, 46), (70, 96, 104), lit), outline=K, width=8)
    for gx in range(int(box[0]) + 40, int(box[2]), 60):
        d.line([(gx, box[1]), (gx, box[3])], fill=K, width=3)
    d.line([(box[0], y - 265), (box[2], y - 265)], fill=K, width=3)
    for side in (-1, 1):
        px = x + side * 360
        d.rectangle([px - 34, y - 420, px + 34, y], fill=red, outline=K, width=8)
        d.rectangle([px + (6 if side > 0 else -34), y - 420, px + (34 if side > 0 else -6), y], fill=redd)
        d.rectangle([px - 34, y - 420, px + 34, y], outline=K, width=8)
    d.rectangle([x - 394, y - 460, x + 394, y - 400], fill=red, outline=K, width=8)
    d.rectangle([x - 394, y - 420, x + 394, y - 400], fill=redd)
    d.rectangle([x - 394, y - 460, x + 394, y - 400], outline=K, width=8)


def scene_paulista(img, d, t, T):
    flash = 0.0
    for ft in (0.45, 0.62):
        if t >= ft:
            flash = max(flash, 1 - seg(t, ft, ft + 0.3))
    lit = max(0.25, flash, 0.25 + 0.35 * (1 - seg(t, 0.6, 2.0)))
    vgrad(img, (0, 0, W, 1300), lerpc(SKY_D, (120, 140, 145), flash * 0.6), PET_D)
    if 0.42 < t < 0.75:  # raio
        pts = [(700, 0), (650, 160), (720, 230), (620, 420), (680, 470), (600, 640)]
        d.line(pts, fill=WHITE, width=14)
        d.line(pts, fill=(200, 230, 255), width=6)
    # prédios da avenida (perspectiva)
    rnd = random.Random(21)
    skyline(d, 1100, rnd, lerpc((18, 48, 58), (60, 90, 98), flash), 300, 820, lights=(70, 110, 118))
    for side in (-1, 1):
        for i in range(4):
            x0 = 0 if side < 0 else W
            top = 120 + i * 140
            xw = 260 - i * 50
            col = lerpc((12, 32, 40), (40, 64, 72), i / 4 + flash * 0.3)
            pts = [(x0, top - 120), (x0 + side * xw, top + 80), (x0 + side * xw, 1250 - i * 20), (x0, 1350)]
            d.polygon(pts, fill=col, outline=K, width=6)
    # chão da avenida
    d.polygon([(0, 1350), (W, 1350), (W, H), (0, H)], fill=(30, 36, 40))
    d.polygon([(0, 1250), (W, 1250), (W, 1350), (0, 1350)], fill=(46, 54, 58))
    for i in range(6):
        y = 1420 + i * 90 + (t * 140 % 90)
        d.polygon([(530 - 6 - i * 3, y), (550 + 6 + i * 3, y), (556 + i * 4, y + 40), (524 - i * 4, y + 40)],
                  fill=CON_XL)
    # reflexo do MASP no asfalto molhado
    d.rectangle([180, 1360, 900, 1520], fill=lerpc((40, 20, 24), (120, 30, 38), lit * 0.6))
    masp(d, 540, 1250, lit)
    # vilão posando
    jump = 0.0
    spin = 0.0
    if t > 2.55:
        jump = math.sin(math.pi * seg(t, 2.55, 3.15)) * 180
        spin = seg(t, 2.55, 3.15)
    villain(d, 540, 1720 - jump, 1.0, t=t, pose="raise" if t < 2.55 or t > 3.2 else "shock",
            lean=-0.15 * math.sin(spin * math.pi * 2), sx=1 - 0.5 * math.sin(spin * math.pi),
            glow=1.5 if t < 2.4 else 0.6)
    fx = {"flash": flash * 0.9}
    if t < 1.0:
        fx["shake"] = 10 * flash
    # motoboy
    if 2.1 < t < 3.3:
        mx = lerp(-500, W + 600, seg(t, 2.1, 3.1))
        motoboy(d, mx, 1800, 0.95, t)
        if 2.25 < t < 3.0:
            text(d, (380, 1080), "BI-BIIII!", 120, fill=WHITE, stroke=10)
        fx["shake"] = 14 * (1 - seg(t, 2.5, 3.3)) if t > 2.5 else 0
    if t > 3.2:
        text(d, (820, 1060), "?!", 130, fill=WHITE, stroke=10)
    return fx


def motoboy(d, x, y, s, t):
    ow = 7 * s

    def P(px, py):
        return (x + px * s, y - py * s)
    for i in range(6):  # linhas de velocidade
        yy = y - (60 + i * 50) * s
        d.line([(x - (500 + i * 40) * s, yy), (x - 260 * s, yy)], fill=CON_XL, width=6)
    d.polygon([P(230, 140), P(800, 220), P(800, 40)], fill=(230, 230, 210))  # farol
    for wx in (-150, 170):
        circle(d, *P(wx, 60), 62 * s, K, 0)
        circle(d, *P(wx, 60), 26 * s, CON, 0)
    body = [(-190, 110), (-80, 150), (60, 150), (200, 160), (240, 120), (180, 80), (-120, 80)]
    poly(d, [P(*p) for p in body], (36, 60, 70), ow)
    poly(d, [P(*p) for p in [(-60, 150), (60, 150), (40, 175), (-50, 175)]], K, ow * 0.5)
    # baú vermelho
    poly(d, [P(*p) for p in [(-230, 330), (-60, 330), (-60, 170), (-230, 170)]], RED, ow)
    text(d, P(-145, 250), "ENTREGA", 34 * s, fill=WHITE, stroke=4)
    # piloto
    limb(d, P(-20, 175), P(70, 120), 40 * s, (30, 34, 40), ow)
    poly(d, [P(*p) for p in [(-50, 360), (40, 360), (60, 190), (-60, 180)]], (60, 66, 72), ow)
    limb(d, P(30, 330), P(190, 210), 32 * s, (60, 66, 72), ow)
    circle(d, *P(0, 420), 62 * s, CON_XL, ow)
    d.chord([P(0, 482)[0] - 10 * s, P(0, 470)[1], P(66, 470)[0], P(0, 380)[1]], -90, 90, fill=K)


def scene_se(img, d, t, T):
    # parede de azulejo da estação
    d.rectangle([0, 0, W, 1500], fill=(52, 70, 76))
    for y in range(0, 1500, 60):
        d.line([(0, y), (W, y)], fill=(40, 56, 62), width=3)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, 1500)], fill=(40, 56, 62), width=3)
    d.rectangle([0, 0, W, 210], fill=(26, 34, 38))
    for lx in (160, 540, 920):
        d.rectangle([lx - 120, 190, lx + 120, 210], fill=(220, 230, 220))
    # placa
    d.rectangle([250, 330, 830, 470], fill=K, outline=CON_XL, width=6)
    text(d, (540, 400), "ESTAÇÃO SÉ", 84, fill=WHITE, stroke=0)
    # relógio / horário
    d.rectangle([60, 330, 230, 430], fill=K, outline=CON_XL, width=5)
    text(d, (145, 380), "18:07", 52, fill=RED, stroke=0)
    # trilhos / fosso
    d.rectangle([0, 1000, W, 1500], fill=(20, 24, 28))
    d.rectangle([0, 1440, W, 1500], fill=(240, 210, 60))  # faixa de segurança
    for x in range(0, W, 50):
        d.line([(x, 1440), (x + 30, 1500)], fill=K, width=8)
    d.rectangle([0, 1500, W, H], fill=(70, 76, 80))
    # trem
    arrive = ease_out(seg(t, 0.8, 2.0))
    leave = ease_in(seg(t, 3.9, 5.5))
    tx = lerp(1250, 0, arrive) - leave * 1600
    door_open = seg(t, 2.0, 2.3) - seg(t, 2.95, 3.2)
    dcx = tx + 540  # centro da porta
    vx = 520
    inside = t > 2.95
    fx = {}

    def train_body():
        d.rectangle([tx - 1400, 600, tx + 1200, 1440], fill=CON_L, outline=K, width=10)
        d.rectangle([tx - 1400, 1230, tx + 1200, 1300], fill=RED)
        d.rectangle([tx - 1400, 660, tx + 1200, 690], fill=CON)
        for wx in (-1050, -650, 140, 940):
            wxx = tx + wx
            d.rounded_rectangle([wxx - 170, 760, wxx + 170, 1080], radius=20, fill=(34, 52, 58), outline=K, width=8)
            rnd = random.Random(int(wx))
            for i in range(9):  # rostos espremidos
                hx = wxx - 140 + i * 36 + rnd.randint(-8, 8)
                hy = 900 + rnd.randint(-60, 80)
                circle(d, hx, hy, 52, lerpc(SKIN, CON, rnd.random() * 0.5), 5)
                circle(d, hx - 14, hy - 8, 5, K, 0)
                circle(d, hx + 14, hy - 8, 5, K, 0)
                d.line([(hx - 12, hy + 22), (hx + 12, hy + 22)], fill=K, width=5)

    if t > 0.8:
        train_body()
        # porta
        d.rectangle([dcx - 190, 700, dcx + 190, 1440], fill=(30, 44, 50), outline=K, width=8)
        rnd = random.Random(7)
        for i in range(14):  # multidão na porta
            hx = dcx - 170 + (i % 7) * 56 + rnd.randint(-10, 10)
            hy = 820 + (i // 7) * 150 + rnd.randint(-20, 20)
            circle(d, hx, hy, 58, lerpc(SKIN, CON, rnd.random() * 0.6), 5)
            circle(d, hx - 16, hy - 8, 5, K, 0)
            circle(d, hx + 16, hy - 8, 5, K, 0)
            d.ellipse([hx - 8, hy + 16, hx + 8, hy + 30], fill=K)
    if not inside:
        # vilão esperando na plataforma; é sugado pra porta
        pull = ease(seg(t, 2.35, 2.95))
        vx_ = lerp(vx, dcx, pull)
        vy = lerp(1780, 1480, pull)
        villain(d, vx_, vy, lerp(0.85, 0.7, pull), t=t, pose="walk" if t < 2.3 else "shock",
                walk=None if t < 2.3 else t * 3, lean=-0.3 * pull, glow=1.3 if t < 2.0 else 0.5)
        if 2.25 < t < 2.9:
            fx["shake"] = 12
    if t > 0.8:
        # folhas da porta (fecham)
        o = door_open
        for side in (-1, 1):
            x_in = dcx + side * 190 * o
            x_out = dcx + side * 190
            if abs(x_out - x_in) > 2:
                d.rectangle([min(x_in, x_out) - (0 if side > 0 else 0), 700, max(x_in, x_out), 1440],
                            fill=CON_L, outline=K, width=8)
        if inside:
            box = [int(dcx - 180), 760, int(dcx + 180), 1180]
            d.rectangle(box, fill=(34, 52, 58))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            villain(ImageDraw.Draw(lay), dcx, 1500, 0.8, t=t, pose="squish", sx=1.35, sy=0.86, umbrella=False,
                    drips=False, glow=0.6)
            cr = lay.crop((max(0, box[0]), box[1], min(W, box[2]), box[3]))
            img.paste(cr, (max(0, box[0]), box[1]), cr)
        if inside or o < 0.99:
            # vidros da porta
            for side in (-1, 1):
                gx0 = dcx + side * 30 + (0 if side > 0 else -150)
                d.rectangle([gx0, 760, gx0 + 150, 1180], outline=K, width=8)
            if inside:
                for i in range(3):
                    gx = dcx - 120 + i * 90
                    d.line([(gx, 800), (gx + 60, 740)], fill=(220, 235, 240), width=6)
    if 2.95 < t < 3.4:
        fx["shake"] = 18 * (1 - seg(t, 2.95, 3.4))
        text(d, (540, 640), "TUM!", 130, fill=WHITE, stroke=10)
    if 3.4 < t < 3.9:
        text(d, (540, 640), "socorro...", 80, fill=WHITE, stroke=8)
    # luz do túnel antes do trem
    if t < 0.9:
        d.ellipse([1000, 820, 1240, 1060], fill=lerpc((40, 50, 54), WHITE, ease(t / 0.9)))
    return fx


def scene_marginal(img, d, t, T):
    vgrad(img, (0, 0, W, 900), (30, 52, 60), (60, 82, 88))
    skyline(d, 760, random.Random(31), (34, 56, 64), 120, 420, lights=(80, 110, 116))
    # rio Tietê
    d.rectangle([0, 760, W, 880], fill=(30, 58, 60))
    for i in range(8):
        y = 780 + i * 14
        x = (i * 173 + t * 30) % W
        d.line([(x, y), (x + 120, y)], fill=(52, 84, 84), width=3)
    d.rectangle([0, 880, W, 910], fill=CON)
    # pistas
    d.rectangle([0, 910, W, H], fill=(36, 40, 44))
    lanes = [1090, 1330, 1600, 1880]
    for ly in (1210, 1470, 1740):
        for x in range(-60, W, 140):
            d.rectangle([x, ly, x + 70, ly + 10], fill=CON_XL)
    creep = t * 0.83 * 3  # 3 km/h ~ 0,83 m/s -> poucos px
    rnd = random.Random(5)
    cols = [CON_L, (70, 90, 96), CON, (120, 130, 132), PET_L]
    for li, ly in enumerate(lanes):
        if li == 2:
            continue
        sc = 0.55 + li * 0.15
        for i in range(-1, 5):
            cx = i * 470 * sc + rnd.randint(0, 120) + (creep * (li + 1) % 30)
            car(d, cx, ly, sc, body=cols[(i + li) % 5], flip=-1 if li == 0 else 1)
    # faixa do vilão: vítima à frente, vilão atrás
    ly = lanes[2]
    sc = 1.1
    vx = 300 + creep * 2
    victim_x = 860 + creep * 2

    def victim_driver():
        hx, hy = victim_x + (20) * sc, ly - 150 * sc
        circle(d, hx, hy, 32 * sc, SKIN, 5)
        d.line([(hx - 12, hy + 8), (hx + 12, hy + 8)], fill=K, width=4)
        circle(d, hx + 12, hy - 8, 4, K, 0)
    car(d, victim_x, ly, sc, body=(90, 108, 114), driver=victim_driver)

    def villain_driver():
        # vilão dirigindo, cabeça e braço pra fora
        hy = ly - 150 * sc - 58 * 0.8 * sc
        d.ellipse([vx - 60 * sc, hy - 70 * sc, vx + 80 * sc, hy + 60 * sc], fill=YEL_D, outline=K, width=6)
        draw_bag(d, vx + 10 * sc, hy, 0.8 * sc, ow=6)
        for ex in (-24, 24):
            circle(d, vx + 10 * sc + ex * 0.8 * sc, hy - 15 * 0.8 * sc, 4.5, RED, 0)
        shake = math.sin(t * 22) * 10 if t > 1.5 else 0
        limb(d, (vx + 60 * sc, ly - 140 * sc), (vx + 120 * sc, ly - 250 * sc + shake), 26 * sc, YEL, 6)
        circle(d, vx + 120 * sc, ly - 250 * sc + shake, 18, K, 0)
    car(d, vx, ly, sc, body=(48, 52, 58), driver=villain_driver)
    # caracol ultrapassando todo mundo
    sx_ = lerp(-80, 760, seg(t, 0.6, T))
    sy_ = ly + 70
    d.ellipse([sx_ - 70, sy_ - 30, sx_ + 50, sy_ + 4], fill=CON_XL, outline=K, width=6)
    circle(d, sx_ - 20, sy_ - 60, 46, (150, 120, 96), 6)
    d.arc([sx_ - 50, sy_ - 90, sx_ + 10, sy_ - 30], 0, 300, fill=K, width=5)
    d.line([(sx_ + 40, sy_ - 20), (sx_ + 56, sy_ - 70)], fill=K, width=5)
    circle(d, sx_ + 56, sy_ - 74, 7, K, 0)
    if t > 2.7:
        text(d, (sx_ - 10, sy_ - 170), "fui!", 64, fill=WHITE, stroke=7)
    # buzinas
    if 1.5 < t < 2.4:
        text(d, (300, 1250), "BÉÉÉM!", 76, fill=WHITE, stroke=8)
    # placar
    pop = back_out(seg(t, 0.3, 0.7))
    if pop > 0:
        bx0, by0, bx1, by1 = 120, 210, 960, 410
        cx_, cy_ = (bx0 + bx1) / 2, (by0 + by1) / 2
        hw, hh = (bx1 - bx0) / 2 * pop, (by1 - by0) / 2 * pop
        d.rounded_rectangle([cx_ - hw, cy_ - hh, cx_ + hw, cy_ + hh], radius=20, fill=K, outline=CON_XL, width=8)
        if pop > 0.8:
            v = "3" if int(t * 3) % 5 else "2"
            text(d, (cx_, cy_ - 50), "PERSEGUIÇÃO • AO VIVO", 40, fill=CON_XL, stroke=0)
            text(d, (cx_, cy_ + 24), f"VELOCIDADE: {v} km/h", 90, fill=RED, stroke=0)
            if int(t * 2) % 2 == 0:
                circle(d, cx_ - hw + 50, cy_ - 50, 14, RED, 0)
    return {}


def scene_pastel(img, d, t, T):
    d.rectangle([0, 0, W, H], fill=(40, 60, 64))
    for x in range(0, W, 90):  # azulejos
        d.line([(x, 0), (x, 1250)], fill=(32, 50, 54), width=4)
    for y in range(0, 1250, 90):
        d.line([(0, y), (W, y)], fill=(32, 50, 54), width=4)
    # letreiro
    d.rectangle([90, 120, 990, 300], fill=K, outline=CON_XL, width=8)
    text(d, (540, 210), "PASTELARIA DA GAROA", 80, fill=WHITE, stroke=0)
    # cardápio
    zoom = ease(seg(t, 1.6, 2.2))
    d.rectangle([140, 380, 940, 1030], fill=(24, 30, 32), outline=CON_XL, width=10)
    text(d, (540, 450), "CARDÁPIO", 66, fill=CON_XL, stroke=0)
    items = [("CALDO DE CANA", "R$ 12"), ("PASTEL DE FEIRA", None), ("COXINHA", "R$ 11")]
    for i, (name, price) in enumerate(items):
        y = 570 + i * 150
        text(d, (190, y), name, 54, fill=WHITE, stroke=0, anchor="lm")
        if price:
            text(d, (890, y), price, 54, fill=WHITE, stroke=0, anchor="rm")
    y = 720
    pulse = 1 + 0.12 * math.sin(t * 18) * zoom
    text(d, (890 - 10 * zoom, y), "R$ 18", 60 * (1 + 0.9 * zoom) * pulse, fill=RED, stroke=int(4 + 6 * zoom),
         anchor="rm")
    # balcão
    d.rectangle([0, 1250, W, 1400], fill=CON_L, outline=K, width=10)
    d.rectangle([0, 1400, W, H], fill=CON_D)
    for x in range(40, W, 160):
        d.line([(x, 1420), (x + 60, H)], fill=(48, 54, 58), width=8)
    # pastéis na estufa
    d.rectangle([600, 1100, 1040, 1250], fill=(60, 84, 90), outline=K, width=8)
    for i in range(3):
        px = 680 + i * 120
        d.chord([px - 55, 1150, px + 55, 1260], 180, 360, fill=(200, 160, 90), outline=K, width=6)
    # vilão
    shock = t > 2.25
    fly = seg(t, 2.25, 3.4)
    villain(d, 360, 1830, 1.0, t=t, pose="shock" if shock else "walk", walk=None if shock else t * 0.7,
            mask=not shock, sy=1 + 0.06 * math.sin(t * 30) * fly, glow=1.4, umbrella=not shock)
    fx = {}
    if shock:
        mx = 360 + 380 * fly
        my = 1830 - 530 - 900 * math.sin(fly * math.pi * 0.85)
        draw_bag(d, mx, my, 1.0, ang=fly * 7, ow=8)
        if fly < 0.5:
            text(d, (380, 980 + 120), "!!!", 160, fill=WHITE, stroke=12)
        fx["shake"] = 20 * (1 - seg(t, 2.25, 3.0))
    fx["zoom_focus"] = (720, 720, zoom * 0.35 * (1 - seg(t, 2.25, 2.6)))
    return fx


def scene_ponte(img, d, t, T):
    # amanhecer cinza
    vgrad(img, (0, 0, W, 1250), (120, 130, 132), (176, 178, 172))
    circle(d, 300, 820, 110, (214, 212, 200), 0)
    d.rectangle([0, 760, W, 800], fill=(150, 156, 154))
    skyline(d, 1050, random.Random(41), (120, 128, 130), 100, 380, lights=None)
    # ponte estaiada: mastro em X + cabos
    mx, deck = 700, 1180
    top = 260
    for i in range(14):
        k = i / 13
        yA = lerp(top + 60, top + 520, k)
        d.line([(mx - 40 + 30 * k, yA), (-200 + 900 * k * 0.9, deck)], fill=(70, 78, 82), width=4)
        d.line([(mx + 40 - 30 * k, yA), (W + 300 - 600 * k, deck)], fill=(70, 78, 82), width=4)
    d.polygon([(mx - 150, deck + 40), (mx - 110, deck + 40), (mx + 30, top), (mx - 10, top)], fill=CON_XL,
              outline=K, width=8)
    d.polygon([(mx + 150, deck + 40), (mx + 110, deck + 40), (mx - 30, top), (mx + 10, top)], fill=CON_L,
              outline=K, width=8)
    d.rectangle([mx - 26, top - 120, mx + 26, top + 40], fill=CON_XL, outline=K, width=8)
    # tabuleiro curvo
    d.polygon([(-20, deck), (W + 20, deck - 40), (W + 20, deck + 30), (-20, deck + 70)], fill=CON, outline=K,
              width=8)
    d.rectangle([0, deck + 70, W, H], fill=(92, 104, 106))
    for i in range(8):  # rio
        y = deck + 140 + i * 40
        d.line([((i * 211 + t * 25) % W, y), ((i * 211 + t * 25) % W + 160, y)], fill=(124, 136, 138), width=4)
    # rua / ponto de ônibus em primeiro plano
    d.rectangle([0, 1560, W, H], fill=(70, 76, 80))
    d.rectangle([0, 1540, W, 1580], fill=CON_L, outline=K, width=6)
    d.rectangle([60, 1100, 80, 1560], fill=K)
    d.rectangle([20, 1060, 200, 1150], fill=(40, 90, 100), outline=K, width=6)
    text(d, (110, 1105), "BUS", 46, fill=WHITE, stroke=0)
    # ônibus
    bus_in = ease_out(seg(t, 0.0, 1.0))
    bus_out = ease_in(seg(t, 2.6, 4.2))
    bx = lerp(W + 700, 640, bus_in) - bus_out * 1800
    by = 1700
    board = seg(t, 1.2, 2.4)
    # carroceria
    d.rounded_rectangle([bx - 360, by - 520, bx + 520, by], radius=30, fill=(150, 160, 160), outline=K, width=10)
    d.rectangle([bx - 360, by - 200, bx + 520, by - 150], fill=PET)
    d.rectangle([bx - 300, by - 480, bx + 300, by - 420], fill=K)
    text(d, (bx, by - 450), "RODOVIÁRIA", 48, fill=RED, stroke=0)
    for wx in range(-120, 520, 150):
        d.rounded_rectangle([bx + wx, by - 400, bx + wx + 120, by - 250], radius=12, fill=(70, 92, 100), outline=K,
                            width=6)
    d.rectangle([bx - 330, by - 400, bx - 160, by - 20], fill=(70, 92, 100), outline=K, width=8)  # porta
    if board >= 1:
        # vilão sentado na janela, acenando
        wx = bx - 120 + 75
        draw_bag(d, wx, by - 330, 0.5, ow=5)
        for ex in (-12, 12):
            circle(d, wx + ex, by - 337, 3, RED, 0)
        d.text((wx + 60, by - 600), "tchau...", font=font(72), fill=WHITE, anchor="mm", stroke_width=7,
               stroke_fill=K) if t < 3.2 else None
    for wx in (-200, 380):
        circle(d, bx + wx, by, 62, K, 0)
        circle(d, bx + wx, by, 26, CON, 0)
    if board < 1:
        vx = lerp(260, bx - 245, ease(board))
        villain(d, vx, 1850, 0.74 - 0.12 * ease(seg(board, 0.75, 1)), t=t, pose="carry",
                walk=t * 1.1 if t > 1.2 else None, suitcase=True, umbrella=False, glow=0.5)
    # placar final
    fx = {}
    pop = back_out(seg(t, 2.9, 3.3))
    if pop > 0:
        cx_, cy_ = 540, 420
        hw, hh = 470 * pop, 150 * pop
        d.rounded_rectangle([cx_ - hw, cy_ - hh, cx_ + hw, cy_ + hh], radius=26, fill=K, outline=WHITE, width=8)
        if pop > 0.7:
            text(d, (cx_, cy_ - 75), "PLACAR FINAL", 46, fill=CON_XL, stroke=0)
            text(d, (cx_ - 230, cy_ + 30), "SÃO PAULO", 66, fill=WHITE, stroke=0)
            text(d, (cx_ + 70, cy_ + 30), "1 x 0", 92, fill=WHITE, stroke=0)
            text(d, (cx_ + 310, cy_ + 30), "TERROR", 66, fill=RED, stroke=0)
    return fx


# ---------------------------------------------------------------- roteiro
SCENES = [
    # (função, legenda, duração mínima, instante do boing (s rel.), trovões, efeitos extras)
    dict(fn=scene_intro, cap="E se um assassino de filme de terror atacasse São Paulo?", title=True,
         dmin=4.0, boing=None, thunder=[0.0], sfx=[]),
    dict(fn=scene_lake, cap="Primeiro susto: a multa.", cy=1580, dmin=4.2, boing=3.35, thunder=[], sfx=[("splash", 0.9), ("whistle", 2.4)]),
    dict(fn=scene_paulista, cap="Ninguém aqui tem tempo pra ser assustado.", cy=330, dmin=4.2, boing=3.2, thunder=[0.45],
         sfx=[("horn", 2.25), ("whoosh", 2.4)]),
    dict(fn=scene_se, cap="Horário de pico. Ele virou a vítima.", cy=1600, dmin=4.4, boing=3.0, thunder=[],
         sfx=[("train", 0.7), ("thud", 2.95)]),
    dict(fn=scene_marginal, cap="Perseguição em tempo real.", cy=620, dmin=4.2, boing=3.3, thunder=[],
         sfx=[("carhorn", 1.5), ("carhorn", 1.9)]),
    dict(fn=scene_pastel, cap="Agora sim, terror de verdade.", cy=1560, dmin=4.2, boing=3.1, thunder=[2.25],
         sfx=[("sting", 2.25)]),
    dict(fn=scene_ponte, cap="Segue pra mais.", cy=800, cap_at=3.3, dmin=5.2, boing=3.0, thunder=[], sfx=[("bus", 0.0), ("bus", 2.6)]),
]
NARR_DIR = os.path.join(HERE, "narr")
NARR_SPEED = 1.15
NARR_DELAY = 0.2
BLACK_FRAMES = 2


def wav_len(path):
    try:
        with wave.open(path) as w_:
            return w_.getnframes() / w_.getframerate()
    except Exception:
        return 0.0


def prep_narration(i):
    """acelera e corta o silêncio das pontas -> narr/fast_i.wav"""
    src = os.path.join(NARR_DIR, f"linha_{i}.wav")
    out = os.path.join(NARR_DIR, f"fast_{i}.wav")
    if not os.path.exists(src):
        return None
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        trim = "silenceremove=start_periods=1:start_threshold=-45dB"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af",
                        f"{trim},areverse,{trim},areverse,atempo={NARR_SPEED},highpass=f=70,"
                        "acompressor=threshold=-18dB:ratio=3:makeup=2",
                        "-ar", str(SR), "-ac", "1", out], check=True)
    return out


def build_timeline():
    t0 = 0.0
    for i, sc in enumerate(SCENES):
        f = prep_narration(i)
        nl = wav_len(f) if f else 0.0
        sc["narr_len"] = nl
        sc["dur"] = round(max(sc["dmin"], NARR_DELAY + nl + 0.35) * FPS) / FPS
        sc["t0"] = t0
        t0 += sc["dur"]
    return t0


TOTAL = build_timeline()
NFRAMES = int(round(TOTAL * FPS))

# ---------------------------------------------------------------- pós-processamento (pré-calculado)
_rng = np.random.default_rng(1)
GRAIN = [(_rng.normal(0, 9, (H // 2, W // 2)).astype(np.float32)) for _ in range(6)]
GRAIN = [np.kron(g, np.ones((2, 2), np.float32))[:, :, None] for g in GRAIN]
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.6)) ** 2)
VIGN = np.clip(1.15 - _r ** 2.2 * 0.75, 0.25, 1.0)[:, :, None].astype(np.float32)
del _yy, _xx, _r


def make_fog(seed, alpha, scale, col):
    r = np.random.default_rng(seed)
    small = r.random((int(H / scale) + 2, int(3 * W / scale) + 2)).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((3 * W, H), Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(scale * 0.6))
    a = np.asarray(im).astype(np.float32) / 255.0
    a = np.clip((a - 0.35) * 2.2, 0, 1)
    grad = np.linspace(0.45, 1.0, H, dtype=np.float32)[:, None]
    a = (a * grad * alpha).astype(np.uint8)
    rgba = np.zeros((H, 3 * W, 4), np.uint8)
    rgba[..., :3] = col
    rgba[..., 3] = a
    return Image.fromarray(rgba, "RGBA")


FOGS = [(make_fog(1, 70, 180, (150, 172, 178)), 14.0), (make_fog(2, 55, 110, (170, 186, 190)), -24.0),
        (make_fog(3, 40, 60, (190, 200, 202)), 40.0)]

_rr = random.Random(9)
RAIN = [(_rr.uniform(0, W * 1.4), _rr.uniform(0, H + 300), _rr.uniform(1500, 2300), _rr.uniform(30, 75),
         _rr.uniform(2, 4)) for _ in range(260)]


def rain_layer(t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x0, y0, sp, ln, wd in RAIN:
        y = (y0 + sp * t) % (H + 300) - 150
        x = (x0 - 0.32 * sp * t) % (W * 1.4) - W * 0.2
        d.line([(x, y), (x - 0.32 * ln, y + ln)], fill=(190, 212, 220, 120), width=int(wd))
    return lay


def caption_img(s, title=False):
    size = 96 if title else 84
    maxw = 940
    txt = wrap(s, size, maxw)
    lay = Image.new("RGBA", (W, 700), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.multiline_text((W / 2, 350), txt, font=font(size), fill=WHITE, anchor="mm", align="center",
                     stroke_width=11, stroke_fill=K, spacing=10)
    return lay


CAPS = {}


def render_frame(fi):
    gt = fi / FPS
    idx = 0
    for i, sc in enumerate(SCENES):
        if gt >= sc["t0"]:
            idx = i
    sc = SCENES[idx]
    t = gt - sc["t0"]
    T = sc["dur"]
    local_frame = fi - int(round(sc["t0"] * FPS))
    if local_frame < BLACK_FRAMES and fi > 0:
        return np.zeros((H, W, 3), np.uint8)

    img = Image.new("RGB", (W, H), K)
    d = ImageDraw.Draw(img)
    fx = sc["fn"](img, d, t, T) or {}

    # câmera: zoom-in lento + tremida
    z = 1.0 + 0.07 * ease(t / T)
    fxx, fyy = W / 2, H / 2
    if "zoom_focus" in fx:
        zx, zy, za = fx["zoom_focus"]
        z += za
        fxx, fyy = lerp(W / 2, zx, min(1, za * 3)), lerp(H / 2, zy, min(1, za * 3))
    sh = fx.get("shake", 0)
    rs = random.Random(fi)
    ox, oy = (rs.uniform(-sh, sh), rs.uniform(-sh, sh)) if sh else (0, 0)
    cw, ch = W / z, H / z
    x0 = clamp(fxx - cw / 2 + ox, 0, W - cw)
    y0 = clamp(fyy - ch / 2 + oy, 0, H - ch)
    img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    img = img.convert("RGBA")

    # neblina em camadas + garoa
    for fog, spd in FOGS:
        off = int((gt * spd) % (2 * W))
        img.alpha_composite(fog.crop((off, 0, off + W, H)))
    img.alpha_composite(rain_layer(gt))

    # legenda (fora da câmera)
    key = idx
    if key not in CAPS:
        CAPS[key] = caption_img(sc["cap"], sc.get("title", False))
    cap = CAPS[key]
    if sc.get("title"):
        p = back_out(seg(t, 0.15, 0.55))
        cy = 560
    else:
        ca = sc.get("cap_at", 0.2)
        p = back_out(seg(t, ca, ca + 0.25))
        cy = sc.get("cy", 1500)
    if p > 0:
        sz = 0.6 + 0.4 * p
        cimg = cap.resize((int(W * sz), int(700 * sz)), Image.BILINEAR) if sz != 1 else cap
        img.alpha_composite(cimg, (int(W / 2 - cimg.width / 2), int(cy - cimg.height / 2)))
    if sc.get("title") and t > 0.7:
        tag = caption_small("O MASCARADO DA GAROA", 54, RED)
        img.alpha_composite(tag, (0, 900))

    a = np.asarray(img.convert("RGB")).astype(np.float32)
    fl = fx.get("flash", 0)
    if fl > 0:
        a = a + (255 - a) * min(1.0, fl)
    a = a * VIGN + GRAIN[fi % 6]
    return np.clip(a, 0, 255).astype(np.uint8)


@lru_cache(None)
def caption_small(s, size, col):
    lay = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((W / 2, 80), s, font=font(size), fill=col, anchor="mm", stroke_width=7, stroke_fill=K)
    return lay


# ---------------------------------------------------------------- áudio
def lowpass(x, a):
    """filtro passa-baixa de 1 polo (vetorizado via lfilter manual em blocos)"""
    try:
        from scipy.signal import lfilter
        return lfilter([1 - a], [1, -a], x)
    except Exception:
        y = np.empty_like(x)
        acc = 0.0
        for i in range(len(x)):
            acc = a * acc + (1 - a) * x[i]
            y[i] = acc
        return y


def env(n, att, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(att, 1e-4)) * np.exp(-t / dec)


def sfx(kind, rng):
    if kind == "thunder":
        n = int(SR * 3.5)
        x = rng.normal(0, 1, n)
        x = lowpass(lowpass(x, 0.985), 0.97)
        e = env(n, 0.02, 0.9) * (1 + 0.6 * np.sin(np.arange(n) / SR * 7) ** 2)
        crack = np.zeros(n)
        cn = int(SR * 0.25)
        crack[:cn] = lowpass(rng.normal(0, 1, cn), 0.6) * env(cn, 0.002, 0.06)
        x = x / (np.abs(x).max() + 1e-9) * e * 0.95 + crack * 0.5
        return x
    if kind == "boing":
        n = int(SR * 0.7)
        t = np.arange(n) / SR
        f = 140 + 260 * np.exp(-t * 6) + 18 * np.sin(2 * np.pi * 11 * t)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return 0.55 * np.sin(ph) * env(n, 0.005, 0.25) + 0.15 * np.sin(2 * ph) * env(n, 0.005, 0.15)
    if kind == "whistle":
        n = int(SR * 0.8)
        t = np.arange(n) / SR
        f = 2900 + 250 * np.sign(np.sin(2 * np.pi * 28 * t))
        return 0.22 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.02) * np.minimum(1, (0.8 - t) / 0.05)
    if kind in ("horn", "carhorn"):
        dur = 0.6 if kind == "horn" else 0.45
        n = int(SR * dur)
        t = np.arange(n) / SR
        fr = (520, 650) if kind == "horn" else (330, 415)
        x = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in fr) * 0.12
        if kind == "horn":
            x *= (np.sin(2 * np.pi * 6 * t) > -0.3)
        return lowpass(x, 0.5) * np.minimum(1, (dur - t) / 0.03)
    if kind == "whoosh":
        n = int(SR * 0.9)
        x = rng.normal(0, 1, n)
        t = np.arange(n) / SR
        e = np.exp(-((t - 0.35) / 0.18) ** 2)
        return lowpass(x, 0.7) * e * 0.5
    if kind == "splash":
        n = int(SR * 1.2)
        x = rng.normal(0, 1, n)
        return (lowpass(x, 0.6) * env(n, 0.01, 0.3) * 0.6 +
                lowpass(x, 0.95) * env(n, 0.05, 0.5) * 1.2)
    if kind == "thud":
        n = int(SR * 0.5)
        t = np.arange(n) / SR
        return 0.8 * np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 20)) * t) * env(n, 0.002, 0.12)
    if kind == "train":
        n = int(SR * 3.0)
        t = np.arange(n) / SR
        x = lowpass(rng.normal(0, 1, n), 0.9) * 1.4
        clack = (np.sin(2 * np.pi * 3.2 * t) > 0.95) * lowpass(rng.normal(0, 1, n), 0.5)
        sq = 0.08 * np.sin(2 * np.pi * (1800 - 400 * t / 3) * t) * (t > 1.0) * (t < 1.6)
        e = np.minimum(1, t / 0.8) * np.minimum(1, (3 - t) / 0.8)
        return (x * 0.5 + clack * 0.6 + sq) * e
    if kind == "sting":
        n = int(SR * 1.6)
        t = np.arange(n) / SR
        x = sum(np.sin(2 * np.pi * f * t) for f in (311, 330, 466, 622)) * 0.12
        return x * env(n, 0.01, 0.6)
    if kind == "bus":
        n = int(SR * 1.6)
        t = np.arange(n) / SR
        x = lowpass(rng.normal(0, 1, n), 0.97) * 3 + 0.2 * np.sin(2 * np.pi * 48 * t)
        return x * np.minimum(1, t / 0.3) * np.minimum(1, (1.6 - t) / 0.4) * 0.6
    return np.zeros(1)


def read_wav_mono(path, speed=1.0):
    with wave.open(path) as w_:
        sr = w_.getframerate()
        a = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768
        if w_.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
    n_out = int(len(a) * SR / sr / speed)
    # reamostragem simples; a mudança de tom de 8% é corrigida via ffmpeg (atempo) se disponível
    return np.interp(np.linspace(0, len(a) - 1, n_out), np.arange(len(a)), a)


def narration_track(i):
    f = prep_narration(i)
    return read_wav_mono(f) if f else None


def build_audio(path):
    n = int(TOTAL * SR) + SR
    rng = np.random.default_rng(4)
    mix = np.zeros(n, np.float32)
    # garoa: ruído rosado-ish filtrado, constante
    rain = rng.normal(0, 1, n).astype(np.float32)
    rain = lowpass(rain, 0.55) - lowpass(rain, 0.97)
    rain = rain / np.abs(rain).max() * 0.12
    drops = (rng.random(n) > 0.9993) * rng.normal(0, 0.35, n)
    rain = rain + lowpass(drops, 0.3).astype(np.float32)
    # drone grave de terror
    t = np.arange(n) / SR
    drone = 0.05 * np.sin(2 * np.pi * 55 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * t)) + \
        0.03 * np.sin(2 * np.pi * 58.3 * t)
    mix += rain + drone.astype(np.float32)

    def add(x, at, g=1.0):
        a = int(at * SR)
        x = np.asarray(x, np.float32)[: max(0, n - a)]
        mix[a:a + len(x)] += x * g

    voice = np.zeros(n, np.float32)
    for i, sc in enumerate(SCENES):
        for th in sc["thunder"]:
            add(sfx("thunder", rng), sc["t0"] + th, 0.9)
        for k, at in sc["sfx"]:
            add(sfx(k, rng), sc["t0"] + at, 0.8)
        if sc["boing"] is not None:
            add(sfx("boing", rng), sc["t0"] + sc["boing"], 0.75)
        nv = narration_track(i)
        if nv is not None:
            a = int((sc["t0"] + NARR_DELAY) * SR)
            nv = nv[: n - a]
            voice[a:a + len(nv)] += nv.astype(np.float32)
    # ducking: abaixa o resto quando a voz fala
    venv = lowpass(np.abs(voice), 0.9995)
    duck = 1 - np.clip(venv / (venv.max() + 1e-9) * 2.5, 0, 0.55)
    out = mix * duck + voice * 1.15
    out = out[: int(TOTAL * SR)]
    out = np.tanh(out * 1.1) / np.tanh(1.1)
    out = (out / max(1e-6, np.abs(out).max()) * 0.92 * 32767).astype(np.int16)
    with wave.open(path, "wb") as w_:
        w_.setnchannels(1)
        w_.setsampwidth(2)
        w_.setframerate(SR)
        w_.writeframes(out.tobytes())


# ---------------------------------------------------------------- main
def preview():
    os.makedirs(os.path.join(HERE, "previews"), exist_ok=True)
    picks = []
    for i, sc in enumerate(SCENES):
        for frac in (0.15, 0.5, 0.8):
            picks.append((i, frac, int(round((sc["t0"] + sc["dur"] * frac) * FPS))))
    for i, frac, fi in picks:
        Image.fromarray(render_frame(fi)).save(os.path.join(HERE, "previews", f"cena{i}_{int(frac*100):02d}.png"))
    print("previews ok:", len(picks))


def main():
    print(f"duração total {TOTAL:.2f}s, {NFRAMES} frames")
    for i, sc in enumerate(SCENES):
        print(f"  cena {i}: início {sc['t0']:.2f}s, dur {sc['dur']:.2f}s, narração {sc['narr_len']:.2f}s")
    if "--preview" in sys.argv:
        frames = [int(a) for a in sys.argv[2:]] if len(sys.argv) > 2 else None
        if frames:
            os.makedirs(os.path.join(HERE, "previews"), exist_ok=True)
            for fi in frames:
                Image.fromarray(render_frame(fi)).save(os.path.join(HERE, "previews", f"f{fi:04d}.png"))
        else:
            preview()
        return
    out_dir = os.path.join(HERE, "saida")
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, "audio.wav")
    build_audio(wav)
    print("áudio ok")
    mp4 = os.path.join(out_dir, "terror_sp.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(NFRAMES), chunksize=4)):
            ff.stdin.write(fr.tobytes())
            if k % 60 == 0:
                print(f"  frame {k}/{NFRAMES}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("MP4:", mp4)


if __name__ == "__main__":
    main()
