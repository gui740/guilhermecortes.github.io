# -*- coding: utf-8 -*-
import os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 240, 160
FPS = 30

_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", name + ".ttf"), size)
    return _fc[k]
F8 = font("PressStart2P", 8)
F16 = font("PressStart2P", 16)
FT = font("Tiny5", 8)

# paleta de interface
BLACK = (16, 20, 24); WHITE = (248, 248, 240); CREAM = (248, 240, 208)
DKGREEN = (24, 48, 40); MOSS = (72, 104, 56); LEAF = (120, 168, 72)
IPE = (248, 200, 56); IPE_D = (208, 144, 32); RED = (216, 72, 56); SKY = (120, 200, 232)
GREY = (136, 144, 136); NAVY = (24, 40, 56); CYAN = (112, 232, 200)

def draw(im):
    d = ImageDraw.Draw(im); d.fontmode = "1"; return d

def tw(s, f=F8):
    return int(f.getlength(s))

def text(d, x, y, s, f=F8, fill=WHITE, shadow=None, anchor="l"):
    if anchor == "c": x -= tw(s, f) // 2
    elif anchor == "r": x -= tw(s, f)
    if f is FT: y -= 2
    if shadow is not None:
        d.text((x + 1, y + 1), s, font=f, fill=shadow)
    d.text((x, y), s, font=f, fill=fill)

def outline(im, color):
    """contorno de 1px em volta da área opaca (vizinhança-4)"""
    a = np.array(im)
    al = a[..., 3] > 0
    n = np.zeros_like(al)
    n[1:, :] |= al[:-1, :]; n[:-1, :] |= al[1:, :]; n[:, 1:] |= al[:, :-1]; n[:, :-1] |= al[:, 1:]
    edge = n & ~al
    a[edge] = (*color, 255)
    return Image.fromarray(a, "RGBA")

def silhouette(im, color):
    a = np.array(im)
    m = a[..., 3] > 0
    a[m] = (*color, 255)
    return Image.fromarray(a, "RGBA")

class Cv:
    """tela de sprite: primitivas sem anti-aliasing + desenho recortado na máscara"""
    def __init__(s, w, h):
        s.im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def ell(s, box, c): s.d.ellipse(box, fill=c)
    def poly(s, pts, c): s.d.polygon(pts, fill=c)
    def rect(s, box, c): s.d.rectangle(box, fill=c)
    def line(s, pts, c, w=1): s.d.line(pts, fill=c, width=w)
    def px(s, x, y, c):
        if 0 <= x < s.im.width and 0 <= y < s.im.height: s.im.putpixel((x, y), (*c, 255))
    def get(s, x, y):
        if 0 <= x < s.im.width and 0 <= y < s.im.height: return s.im.getpixel((x, y))
        return (0, 0, 0, 0)
    def clip(s, fn, only=None):
        """desenha fn(camada) apenas onde já existe pixel (opcionalmente só sobre cores 'only')"""
        lay = Cv(*s.im.size); fn(lay)
        a = np.array(s.im); b = np.array(lay.im)
        m = (a[..., 3] > 0) & (b[..., 3] > 0)
        if only is not None:
            mm = np.zeros(m.shape, bool)
            for c in only: mm |= (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2])
            m &= mm
        a[m] = b[m]
        s.im = Image.fromarray(a, "RGBA"); s.d = ImageDraw.Draw(s.im)

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
