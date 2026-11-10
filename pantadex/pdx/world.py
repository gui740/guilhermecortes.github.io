# -*- coding: utf-8 -*-
"""Mapa em tiles (visão de cima) e pesquisadora — tudo desenhado por código."""
import math, random
from .common import *

TS = 16
MW, MH = 34, 16
G0 = (152, 208, 96); G1 = (112, 184, 80); G2 = (80, 152, 64); G3 = (56, 120, 56)
W0 = (40, 104, 168); W1 = (56, 136, 200); W2 = (104, 176, 224); W3 = (184, 224, 240)
P1 = (216, 184, 120); P2 = (184, 152, 96)
WD1 = (184, 128, 72); WD2 = (160, 104, 60); WD3 = (104, 64, 36)
C1 = (64, 136, 56); C2 = (120, 176, 72); C3 = (168, 204, 88); C4 = (224, 208, 112)

def build_map():
    m = [["." for _ in range(MW)] for _ in range(MH)]
    rnd = random.Random(11)
    for y in range(MH):
        cx = 12.4 + 1.3 * math.sin(y * 0.55 + 0.6)
        for x in range(MW):
            if abs(x - cx) < 1.6: m[y][x] = "W"
            if ((x - 27.5) / 4.3) ** 2 + ((y - 11.6) / 2.7) ** 2 < 1: m[y][x] = "W"
    for x in range(19, 27):
        for y in range(3, 9):
            if m[y][x] == "." and not ((x, y) in [(19, 3), (26, 3), (19, 8)]): m[y][x] = "T"
    for x in range(15, 22):
        for y in range(9, 13):
            if m[y][x] == "." and (x, y) not in [(15, 9), (21, 12), (21, 9)]: m[y][x] = "T"
    for x in range(0, MW):
        if m[7][x] == "W" or (x + 1 < MW and m[7][x + 1] == "W") or (x > 0 and m[7][x - 1] == "W"): m[7][x] = "B"
    for x in range(0, 19):
        if m[7][x] in ".T": m[7][x] = ":"
    for y in range(MH):
        for x in range(MW):
            if m[y][x] == "." and rnd.random() < 0.16: m[y][x] = ","
            if m[y][x] == "W" and rnd.random() < 0.2 and (y < 6 or y > 8): m[y][x] = "A"
    return m

MAP = build_map()
TREES = [(4, 4), (8, 11), (17, 2), (29, 5), (23, 13), (1, 12), (31, 1), (6, 1)]   # tile da base do tronco

def at(x, y):
    if 0 <= x < MW and 0 <= y < MH: return MAP[y][x]
    return "."
def is_water(x, y): return at(x, y) in "WA"
def is_wet(x, y): return at(x, y) in "WAB" and (at(x, y) != "B" or is_water(x, y - 1) or is_water(x, y + 1))

def _grass(d, ox, oy, rnd, flowers=False):
    d.rectangle((ox, oy, ox + 15, oy + 15), fill=G1)
    for _ in range(5):
        x = ox + rnd.randint(1, 13); y = oy + rnd.randint(1, 13)
        d.point([(x, y), (x + 1, y - 1), (x + 2, y)], fill=G2)
    for _ in range(2):
        d.point((ox + rnd.randint(0, 15), oy + rnd.randint(0, 15)), fill=G0)
    if flowers:
        for _ in range(3):
            x = ox + rnd.randint(2, 12); y = oy + rnd.randint(2, 12)
            c = rnd.choice([(248, 248, 240), (248, 208, 72), (240, 152, 184)])
            d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=c); d.point((x, y), fill=(232, 144, 40))

def _water(d, ox, oy, tx, ty, fr):
    d.rectangle((ox, oy, ox + 15, oy + 15), fill=W1)
    rnd = random.Random(tx * 131 + ty * 17)
    for i in range(3):
        x = rnd.randint(0, 11); y = rnd.randint(2, 14)
        x = (x + fr * 3 + (i % 2) * fr) % 12
        d.line((ox + x, oy + y, ox + x + 3, oy + y), fill=W2)
        if i == 0 and fr == 1: d.point((ox + x + 1, oy + y - 1), fill=W3)
    if not is_wet(tx, ty - 1):
        d.rectangle((ox, oy, ox + 15, oy + 1), fill=(72, 96, 56)); d.rectangle((ox, oy + 2, ox + 15, oy + 3), fill=W0)
        for x in range(0, 16, 4): d.point((ox + x + (fr % 2), oy + 4), fill=W0)
    if not is_wet(tx - 1, ty):
        d.line((ox, oy, ox, oy + 15), fill=(72, 96, 56)); d.line((ox + 1, oy, ox + 1, oy + 15), fill=W0)
    if not is_wet(tx + 1, ty):
        d.line((ox + 15, oy, ox + 15, oy + 15), fill=G3); d.line((ox + 14, oy, ox + 14, oy + 15), fill=W0)
    if not is_wet(tx, ty + 1):
        d.line((ox, oy + 15, ox + 15, oy + 15), fill=G3)
        for x in range(fr, 16, 3): d.point((ox + x, oy + 14), fill=W3)

def _aguape(d, ox, oy, tx, ty, fr):
    rnd = random.Random(tx * 7 + ty * 29)
    bob = 1 if (fr + tx) % 3 == 0 else 0
    for i in range(rnd.randint(2, 3)):
        x = ox + 2 + i * 4 + rnd.randint(0, 1); y = oy + 4 + rnd.randint(0, 6) + bob
        d.ellipse((x, y, x + 5, y + 4), fill=(40, 120, 64)); d.ellipse((x, y, x + 4, y + 3), fill=(88, 184, 88))
        d.point((x + 1, y + 1), fill=(160, 224, 120))
    x = ox + rnd.randint(4, 9); y = oy + rnd.randint(4, 8) + bob
    d.rectangle((x, y, x + 2, y + 2), fill=(176, 136, 232)); d.point((x + 1, y + 1), fill=(248, 224, 96))
    d.point([(x + 1, y - 1), (x - 1, y + 1)], fill=(208, 184, 248))

def _board(d, ox, oy, tx):
    d.rectangle((ox, oy + 14, ox + 15, oy + 15), fill=W0 if True else 0)
    d.rectangle((ox, oy + 2, ox + 15, oy + 13), fill=WD1)
    for x in range(0, 16, 4):
        d.line((ox + x, oy + 2, ox + x, oy + 13), fill=WD3)
        if (x // 4 + tx) % 2: d.rectangle((ox + x + 1, oy + 3, ox + x + 3, oy + 12), fill=WD2)
        d.point((ox + x + 2, oy + 4), fill=(216, 168, 104)); d.point((ox + x + 2, oy + 11), fill=WD3)
    d.line((ox, oy + 2, ox + 15, oy + 2), fill=WD3); d.line((ox, oy + 13, ox + 15, oy + 13), fill=WD3)
    d.line((ox, oy + 3, ox + 15, oy + 3), fill=(216, 168, 104))
    if tx % 2 == 0:
        d.rectangle((ox + 6, oy, ox + 9, oy + 2), fill=WD3); d.rectangle((ox + 6, oy + 13, ox + 9, oy + 15), fill=WD3)
        d.point((ox + 7, oy), fill=WD1); d.point((ox + 7, oy + 13), fill=WD1)

def _path(d, ox, oy, tx, ty, rnd):
    d.rectangle((ox, oy, ox + 15, oy + 15), fill=P1)
    for _ in range(5): d.point((ox + rnd.randint(0, 15), oy + rnd.randint(2, 13)), fill=P2)
    d.point((ox + rnd.randint(2, 13), oy + rnd.randint(4, 11)), fill=(240, 216, 160))
    for x in range(16):
        if at(tx, ty - 1) != ":": d.line((ox + x, oy, ox + x, oy + rnd.randint(0, 2)), fill=G1 if rnd.random() < .7 else G2)
        if at(tx, ty + 1) != ":": d.line((ox + x, oy + 15 - rnd.randint(0, 2), ox + x, oy + 15), fill=G1 if rnd.random() < .7 else G2)

def capim_tile(fr, tx, ty, front=False):
    """tile de capim alto (RGBA); fr = quadro de balanço; front = só a metade de baixo (cobre as pernas)"""
    im = Image.new("RGBA", (16, 18), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rnd = random.Random(tx * 53 + ty * 97)
    d.rectangle((0, 2, 15, 17), fill=C1)
    for row, by in enumerate((8, 13, 17)):
        for i in range(4):
            x = i * 4 + (row % 2) * 2 + rnd.randint(0, 1); h = rnd.randint(6, 8)
            sway = (fr if fr < 2 else -1) if (i + row) % 2 == 0 else (0 if fr < 2 else 1)
            x0 = x % 16
            d.line((x0, by, x0, by - h + 3), fill=C2); d.line(((x0 + 1) % 16, by, (x0 + 1) % 16, by - h + 4), fill=G3)
            xt = (x0 + sway) % 16
            d.line((xt, by - h + 2, xt, by - h), fill=C3)
            if rnd.random() < 0.45: d.point((xt, max(0, by - h - 1)), fill=C4)
    if front:
        a = np.array(im); a[:9, :, 3] = 0
        # borda superior irregular
        for x in range(16):
            if (x + tx) % 3 == 0: a[9, x, 3] = 0
        im = Image.fromarray(a, "RGBA")
    return im

_CAP = {}
def capim(fr, tx, ty, front=False):
    k = (fr, tx, ty, front)
    if k not in _CAP: _CAP[k] = capim_tile(fr, tx, ty, front)
    return _CAP[k]

def make_tree():
    Y1 = (248, 204, 56); Y2 = (216, 152, 32); Y3 = (255, 236, 136); TR = (104, 72, 56); TR2 = (72, 48, 40)
    c = Cv(44, 56)
    c.poly([(19, 30), (25, 30), (26, 52), (18, 52)], TR); c.line([(22, 34), (14, 24)], TR, 3); c.line([(22, 34), (31, 24)], TR, 3)
    c.line([(24, 32), (24, 51)], TR2, 2)
    rnd = random.Random(5)
    blobs = [(12, 20, 9), (22, 12, 10), (32, 20, 9), (16, 12, 7), (29, 11, 7), (22, 24, 8), (8, 14, 5), (36, 13, 5), (22, 5, 6)]
    for x, y, r in blobs: c.ell((x - r, y - r, x + r, y + r), Y1)
    for x, y, r in blobs: c.clip(lambda l: l.ell((x - r + 3, y + 1, x + r, y + r), Y2), only=[Y1])
    for x, y, r in blobs[:6]: c.clip(lambda l: l.ell((x - r + 1, y - r + 1, x - 1, y - 2), Y3), only=[Y1])
    for _ in range(40):
        x = rnd.randint(4, 40); y = rnd.randint(2, 30)
        if c.get(x, y)[:3] == Y1: c.px(x, y, Y3 if rnd.random() < .5 else Y2)
        elif c.get(x, y)[:3] == Y2 and rnd.random() < .4: c.px(x, y, (176, 112, 24))
    return outline(c.im, (112, 72, 24))
TREE = make_tree()

def make_ground(fr):
    im = Image.new("RGB", (MW * TS, MH * TS)); d = ImageDraw.Draw(im)
    for ty in range(MH):
        for tx in range(MW):
            ch = MAP[ty][tx]; ox, oy = tx * TS, ty * TS
            rnd = random.Random(tx * 1009 + ty * 9176)
            if ch in ".,T": _grass(d, ox, oy, rnd, ch == ",")
            elif ch == ":": _path(d, ox, oy, tx, ty, rnd)
            elif ch in "WA":
                _water(d, ox, oy, tx, ty, fr)
                if ch == "A": _aguape(d, ox, oy, tx, ty, fr)
            elif ch == "B":
                if is_wet(tx, ty): _water(d, ox, oy, tx, ty, fr)
                else: _grass(d, ox, oy, rnd)
                _board(d, ox, oy, tx)
    # sombras e pétalas caídas dos ipês
    rnd = random.Random(2)
    for tx, ty in TREES:
        bx, by = tx * TS + 8, ty * TS + 12
        for yy in range(-4, 5):
            for xx in range(-16, 17):
                if (xx / 16) ** 2 + (yy / 4.5) ** 2 < 1 and (xx + yy) % 2 == 0:
                    X, Y = bx + xx, by + yy
                    if 0 <= X < im.width and 0 <= Y < im.height and im.getpixel((X, Y)) in (G1, G0): im.putpixel((X, Y), G2)
        for _ in range(14):
            X = bx + rnd.randint(-22, 22); Y = by + rnd.randint(-6, 12)
            if 0 <= X < im.width and 0 <= Y < im.height and im.getpixel((X, Y)) in (G1, G2, P1):
                im.putpixel((X, Y), (248, 208, 64))
    return im
GROUND = [make_ground(f) for f in range(3)]

# ---------------------------------------------------------------- pesquisadora
def make_player(dr, fr):
    HT = (236, 212, 140); HT2 = (196, 164, 96); BD = (128, 56, 40); SK = (236, 180, 132); HR = (72, 44, 32)
    VS = (88, 128, 80); VS2 = (64, 96, 64); SH = (240, 228, 196); PT = (72, 92, 136); BT = (96, 60, 44); BP = (192, 108, 56)
    c = Cv(18, 26)
    bob = 1 if fr in (1, 3) else 0
    o = 1
    def R(x0, y0, x1, y1, col): c.rect((x0 + o, y0 + bob + 1, x1 + o, y1 + bob + 1), col)
    # pernas (sem bob)
    def L(x0, x1, short):
        y1 = 22 - (2 if short else 0)
        c.rect((x0 + o, 18, x1 + o, y1), PT); c.rect((x0 + o, y1 + 1, x1 + o, y1 + 2), BT)
    if dr in ("down", "up"):
        L(4, 7, fr == 1); L(8, 11, fr == 3)
        R(3, 11, 12, 17, VS)
        if dr == "down":
            R(7, 11, 8, 17, SH); R(3, 16, 12, 17, VS2)
            R(2, 12, 2, 15 + (fr == 1), SH); R(13, 12, 13, 15 + (fr == 3), SH)
            R(2, 16 + (fr == 1), 2, 16 + (fr == 1), SK); R(13, 16 + (fr == 3), 13, 16 + (fr == 3), SK)
            R(13, 15 + (fr == 3), 14, 17 + (fr == 3), (64, 104, 56)); R(14, 15 + (fr == 3), 14, 15 + (fr == 3), IPE)
            R(4, 7, 11, 11, SK); R(3, 7, 3, 12, HR); R(12, 7, 12, 10, HR)
            R(5, 9, 5, 9, (40, 32, 32)); R(10, 9, 10, 9, (40, 32, 32)); R(7, 11, 8, 11, (208, 136, 104))
        else:
            R(2, 12, 2, 16, SH); R(13, 12, 13, 16, SH)
            R(4, 12, 11, 17, BP); R(5, 13, 10, 13, (224, 144, 80)); R(7, 15, 8, 16, (144, 76, 40))
            R(4, 7, 11, 11, HR); R(7, 10, 8, 13, HR)
    else:
        if fr in (1, 3): L(3, 6, False); L(9, 12, fr == 1)
        else: L(6, 9, False)
        R(5, 11, 10, 17, VS); R(5, 16, 10, 17, VS2)
        R(3, 12, 4, 16, BP)
        ax = 7 + (1 if fr == 1 else -1 if fr == 3 else 0)
        R(ax, 12, ax + 1, 15, SH); R(ax, 16, ax + 1, 16, SK)
        R(11, 13, 12, 15, (64, 104, 56)); R(12, 13, 12, 13, IPE)
        R(6, 7, 11, 11, SK); R(4, 7, 5, 12, HR); R(10, 9, 10, 9, (40, 32, 32))
    # chapéu pantaneiro (aba larga)
    c.ell((0 + o, 4 + bob, 15 + o, 9 + bob), HT)
    c.clip(lambda l: l.rect((0, 8 + bob, 18, 10 + bob), HT2), only=[HT])
    R(4, 0, 11, 4, HT); R(5, -1, 10, -1, HT); R(4, 4, 11, 4, BD); R(5, 0, 7, 0, (255, 240, 184))
    im = outline(c.im, (40, 32, 32))
    if dr == "left": im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im
PLAYER = {(d_, f): make_player(d_, f) for d_ in ("down", "up", "left", "right") for f in range(4)}

def route_state(route, dist):
    """route: lista de pontos (tile x,y); devolve (px, py, dir, fim?) após andar 'dist' pixels"""
    for (x0, y0), (x1, y1) in zip(route, route[1:]):
        seg = (abs(x1 - x0) + abs(y1 - y0)) * TS
        dr = "right" if x1 > x0 else "left" if x1 < x0 else "down" if y1 > y0 else "up"
        if dist <= seg:
            f = dist / seg
            return (x0 + (x1 - x0) * f) * TS + 8, (y0 + (y1 - y0) * f) * TS + 12, dr, False
        dist -= seg
    return route[-1][0] * TS + 8, route[-1][1] * TS + 12, dr, True
def route_len(route):
    return sum((abs(x1 - x0) + abs(y1 - y0)) * TS for (x0, y0), (x1, y1) in zip(route, route[1:]))

def render(t, px, py, dr, moving, excl=0.0, walk_dist=0.0):
    """quadro 240x160 do mundo. (px,py) = pés da personagem em pixels do mapa; excl>0 mostra '!'"""
    px = int(round(px)); py = int(round(py))
    cx = int(clamp(px - W // 2, 0, MW * TS - W)); cy = int(clamp(py - 8 - H // 2, 0, MH * TS - H))
    fr = int(t * 3.5) % 3
    im = GROUND[fr].crop((cx, cy, cx + W, cy + H)).convert("RGB")
    ptx, pty = px // TS, (py - 2) // TS
    # capim alto
    for ty in range(cy // TS - 1, (cy + H) // TS + 2):
        for tx in range(cx // TS, (cx + W) // TS + 1):
            if at(tx, ty) == "T" and 0 <= ty < MH:
                near = (tx, ty) == (ptx, pty)
                f = (int(t * 10) % 2 + 1 if moving else 0) if near else (int(t * 1.2 + tx * 0.37 + ty * 0.61) % 3 if True else 0)
                if near and moving: f = 1 + int(t * 10) % 2
                tl = capim(f, tx, ty)
                im.paste(tl, (tx * TS - cx, ty * TS - cy - 2), tl)
    objs = []
    for tx, ty in TREES:
        objs.append((ty * TS + 14, "tree", tx, ty))
    objs.append((py, "player", 0, 0))
    d = ImageDraw.Draw(im)
    for yk, kind, tx, ty in sorted(objs):
        if kind == "tree":
            im.paste(TREE, (tx * TS + 8 - 22 - cx, ty * TS + 14 - 52 - cy), TREE)
        else:
            f = int(walk_dist / 7) % 4 if moving else 0
            sp = PLAYER[(dr, f)]
            sx, sy = px - 9 - cx, py - 25 - cy
            if at(ptx, pty) not in "T":
                for xx in range(-5, 6):
                    for yy in range(-1, 2):
                        if abs(xx) + abs(yy) * 3 < 7 and (xx + yy) % 2 == 0:
                            X, Y = px + xx - cx, py + yy - cy
                            if 0 <= X < W and 0 <= Y < H:
                                r, g, b = im.getpixel((X, Y)); im.putpixel((X, Y), (r * 2 // 3, g * 2 // 3, b * 2 // 3))
            im.paste(sp, (sx, sy), sp)
            if at(ptx, pty) == "T":
                f2 = 1 + int(t * 10) % 2 if moving else 0
                tl = capim(f2, ptx, pty, True)
                im.paste(tl, (ptx * TS - cx, pty * TS - cy - 2), tl)
                if moving:   # folhinhas voando
                    for i in range(3):
                        ph = (t * 3 + i / 3) % 1
                        d.point((px - cx - 6 + i * 6 + int(ph * 4 * (-1) ** i), py - cy - 6 - int(ph * 8)), fill=C3)
            if excl > 0:
                by = sy - 15 - (2 if excl < 0.08 else 0)
                bx = sx + 3
                d.rectangle((bx, by + 1, bx + 11, by + 12), fill=WHITE); d.rectangle((bx + 1, by, bx + 10, by + 13), fill=WHITE)
                d.rectangle((bx + 4, by + 13, bx + 7, by + 14), fill=WHITE); d.rectangle((bx + 5, by + 15, bx + 6, by + 15), fill=WHITE)
                d.rectangle((bx + 5, by + 2, bx + 6, by + 8), fill=RED); d.rectangle((bx + 5, by + 10, bx + 6, by + 11), fill=RED)
    # pétalas de ipê caindo
    for i, (tx, ty) in enumerate(TREES):
        for k in range(3):
            ph = (t * 0.45 + k / 3 + i * 0.17) % 1
            X = tx * TS + 8 - 14 + k * 12 + int(math.sin(ph * 9 + k) * 3) - cx
            Y = ty * TS - 30 + int(ph * 44) - cy
            if 0 <= X < W and 0 <= Y < H: d.point((X, Y), fill=(255, 228, 96))
    return im
