# -*- coding: utf-8 -*-
"""Sprites grandes dos animais, desenhados por código (originais)."""
import random, functools
from .common import *

OL = (40, 28, 24)

# ---------------------------------------------------------------- ONÇA
def _onca(b, tail, blink):
    O1 = (232, 160, 56); O2 = (196, 116, 40); O3 = (248, 196, 96); CR = (248, 232, 200); SP = (44, 30, 24)
    c = Cv(96, 72)
    # cauda
    tx = tail
    c.line([(15, 34 - b), (8, 40), (5, 49), (8, 56), (15 + tx, 59)], O1, 4)
    c.line([(11 + tx, 58), (16 + tx, 59)], SP, 4)
    # patas de trás (lado distante)
    c.poly([(27, 44), (35, 44), (34, 64), (27, 64)], O2); c.ell((26, 62, 36, 67), O2)
    c.poly([(63, 44), (70, 44), (69, 64), (63, 64)], O2); c.ell((62, 62, 72, 67), O2)
    # tronco
    c.ell((12, 22 - b, 70, 50), O1)
    c.ell((10, 25 - b, 36, 53), O1)       # anca
    c.ell((48, 20 - b, 76, 52), O1)       # ombro / peito
    # pescoço
    c.poly([(58, 22 - b), (70, 12 - b), (84, 26 - b), (72, 40 - b)], O1)
    # sombra inferior e barriga
    c.clip(lambda l: l.ell((8, 40, 78, 60), O2))
    c.clip(lambda l: l.ell((22, 45, 60, 56), CR))
    # luz no dorso
    c.clip(lambda l: l.ell((16, 20 - b, 66, 27 - b), O3))
    # pernas próximas
    c.poly([(13, 42), (25, 42), (23, 53), (24, 64), (15, 64), (16, 54)], O1); c.ell((14, 62, 27, 67), O1)
    c.poly([(54, 44), (65, 44), (64, 64), (55, 64)], O1); c.ell((54, 62, 67, 67), O1)
    c.line([(18, 66), (18, 65)], OL); c.line([(22, 66), (22, 65)], OL)
    c.line([(58, 66), (58, 65)], OL); c.line([(62, 66), (62, 65)], OL)
    # cabeça
    hy = -b
    c.ell((64, 5 + hy, 72, 14 + hy), O2); c.ell((79, 4 + hy, 87, 13 + hy), O1)
    c.ell((62, 8 + hy, 89, 33 + hy), O1)
    c.clip(lambda l: l.ell((66, 8 + hy, 86, 14 + hy), O3))
    c.rect((81, 6 + hy, 84, 9 + hy), CR)                      # interior da orelha
    c.ell((74, 20 + hy, 91, 33 + hy), CR)                     # focinho
    c.rect((87, 21 + hy, 90, 23 + hy), (184, 88, 88))         # nariz
    c.line([(82, 28 + hy), (89, 28 + hy)], OL)                # boca
    c.px(88, 25 + hy, OL); c.px(88, 26 + hy, OL)
    for wx, wy in [(80, 24), (82, 26), (79, 27)]: c.px(wx, wy + hy, SP)
    if blink:
        c.line([(76, 17 + hy), (80, 17 + hy)], OL)
    else:
        c.rect((76, 15 + hy, 80, 17 + hy), (224, 232, 104)); c.rect((78, 16 + hy, 79, 17 + hy), OL)
        c.line([(75, 14 + hy), (80, 14 + hy)], OL)
    # rosetas
    rnd = random.Random(7)
    body = (O1, O2, O3)
    for gy in range(22, 50, 7):
        for gx in range(12, 72, 7):
            x = gx + rnd.randint(-1, 1) + (3 if (gy // 7) % 2 else 0); y = gy + rnd.randint(-1, 1) - b
            if all(c.get(x + dx, y + dy)[:3] in body and c.get(x + dx, y + dy)[3] for dx, dy in [(-1, -1), (2, 2), (2, -1), (-1, 2)]):
                ring = [(0, -1), (1, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (0, 2), (1, 2)]
                rnd.shuffle(ring)
                for dx, dy in ring[:6]: c.px(x + dx, y + dy, SP)
                c.px(x, y, O2); c.px(x + 1, y, O2); c.px(x, y + 1, O2); c.px(x + 1, y + 1, O2)
    # pintas pequenas (pernas, cabeça, pescoço)
    for _ in range(90):
        x = rnd.randint(10, 88); y = rnd.randint(6, 62)
        if y > 50 or x > 66 or y < 20:
            p = c.get(x, y)
            if p[3] and p[:3] in body and c.get(x + 1, y)[:3] in body and c.get(x - 1, y)[:3] in body \
               and c.get(x, y - 1)[:3] in body and not (72 < x < 84 and 12 - b < y < 20 - b):
                c.px(x, y, SP)
    return outline(c.im, OL)

# ---------------------------------------------------------------- TUIUIÚ
def _tuiuiu(b, beak, blink):
    WH = (248, 248, 248); G1 = (208, 216, 232); G2 = (168, 180, 208); BK = (40, 40, 52); BK2 = (80, 80, 96)
    RD = (208, 48, 44); RD2 = (160, 32, 40); LG = (64, 64, 76)
    c = Cv(96, 88)
    # pernas
    c.line([(40, 52), (43, 66), (42, 82)], (40, 40, 48), 2)
    c.line([(43, 82), (49, 83)], (40, 40, 48), 1); c.line([(42, 82), (38, 84)], (40, 40, 48), 1)
    c.line([(33, 52), (34, 66), (33, 82)], LG, 2)
    c.line([(34, 82), (41, 84)], LG, 1); c.line([(33, 83), (29, 84)], LG, 1); c.line([(34, 83), (38, 85)], LG, 1)
    c.rect((33, 65, 35, 67), BK2); c.rect((42, 65, 44, 67), BK2)
    # corpo
    c.poly([(8, 44 - b), (20, 36 - b), (20, 50)], WH)
    c.ell((14, 30 - b, 54, 56), WH)
    c.clip(lambda l: l.ell((12, 44, 56, 62), G1))
    c.clip(lambda l: l.ell((16, 50, 50, 60), G2))
    # asa
    c.clip(lambda l: l.line([(20, 42 - b), (30, 47 - b), (42, 46 - b)], G1, 1))
    c.clip(lambda l: l.line([(16, 46 - b), (26, 51 - b), (38, 50 - b)], G1, 1))
    c.clip(lambda l: l.line([(11, 44 - b), (18, 44 - b)], G2, 1))
    # pescoço (preto) + colar vermelho
    c.line([(47, 38 - b), (52, 26 - b), (51, 14 - b)], BK, 7)
    c.poly([(43, 33 - b), (53, 29 - b), (55, 35 - b), (52, 40 - b), (44, 40 - b)], RD)
    c.clip(lambda l: l.rect((42, 37 - b, 56, 41 - b), RD2), only=[RD])
    # cabeça
    c.ell((45, 4 - b, 59, 18 - b), BK)
    c.px(48, 6 - b, BK2); c.px(49, 5 - b, BK2); c.px(50, 5 - b, BK2)
    # bico grande, levemente curvado para cima
    c.poly([(56, 7 - b), (70, 9 - b), (82, 9 - b), (84, 10 - b), (70, 13 - b), (57, 13 - b)], BK)
    c.poly([(56, 13 - b + beak), (70, 13 - b + beak), (83, 11 - b + beak), (72, 16 - b + beak), (57, 17 - b + beak)], (28, 28, 36))
    c.line([(60, 9 - b), (76, 10 - b)], BK2, 1)
    if blink: c.line([(52, 10 - b), (54, 10 - b)], BK2)
    else:
        c.rect((52, 9 - b, 54, 11 - b), (96, 64, 48)); c.px(53, 10 - b, (16, 16, 16)); c.px(54, 9 - b, WH)
    return outline(c.im, (32, 36, 56))

# ---------------------------------------------------------------- CAPIVARA
def _capivara(b, ear, blink, hop):
    B1 = (184, 124, 76); B2 = (144, 92, 56); B3 = (212, 156, 100); B4 = (112, 68, 44); DK = (56, 36, 28)
    c = Cv(100, 68)
    # pernas distantes
    c.rect((28, 46, 35, 61), B4); c.rect((62, 46, 68, 61), B4)
    # corpo
    c.ell((6, 16 - b, 74, 54), B1)
    c.ell((4, 22 - b, 30, 54), B1)
    # cabeça em bloco
    hy = -b
    c.ell((58, 10 + hy, 84, 40 + hy), B1)
    c.d.rounded_rectangle((70, 12 + hy, 95, 37 + hy), radius=6, fill=B1)
    # luz e sombra
    c.clip(lambda l: l.ell((10, 14 - b, 70, 24 - b), B3))
    c.clip(lambda l: l.d.rounded_rectangle((66, 11 + hy, 93, 16 + hy), radius=3, fill=B3))
    c.clip(lambda l: l.ell((2, 42, 80, 62), B2))
    c.clip(lambda l: l.rect((72, 31 + hy, 96, 40 + hy), B2))
    # pernas próximas
    c.rect((15, 44, 24, 62), B1); c.rect((52, 44, 60, 62), B1)
    c.clip(lambda l: l.rect((15, 52, 60, 62), B2), only=[B1])
    c.rect((14, 61, 26, 64), DK); c.rect((51, 61, 62, 64), DK)
    c.rect((28, 61, 36, 63), DK); c.rect((62, 61, 69, 63), DK)
    # orelha, olho, narina, boca
    ey = hy + (1 if ear else 0)
    c.ell((63, 6 + ey, 70, 13 + ey), B2); c.rect((65, 9 + ey, 67, 11 + ey), B4)
    if blink: c.line([(75, 20 + hy), (78, 20 + hy)], DK)
    else:
        c.rect((75, 19 + hy, 78, 21 + hy), DK); c.px(77, 19 + hy, WHITE)
    c.rect((91, 17 + hy, 92, 19 + hy), DK)
    c.line([(86, 32 + hy), (95, 32 + hy)], DK); c.px(95, 31 + hy, DK)
    # pelagem
    rnd = random.Random(3)
    for _ in range(70):
        x = rnd.randint(6, 90); y = rnd.randint(14, 54)
        p = c.get(x, y); q = c.get(x + 1, y + 1)
        if p[3] and q[3] and p[:3] in (B1, B3):
            c.px(x, y - b if y < 40 else y, B2); c.px(x + 1, y + 1 - (b if y < 40 else 0), B2)
    im = outline(c.im, DK)
    # passarinho de carona
    d = ImageDraw.Draw(im)
    bx, by = 34, 9 - b - hop
    d.rectangle((bx, by, bx + 6, by + 4), fill=(96, 72, 48)); d.rectangle((bx + 1, by + 3, bx + 5, by + 5), fill=(248, 216, 64))
    d.rectangle((bx + 5, by - 2, bx + 8, by + 1), fill=(48, 40, 40)); d.point((bx + 7, by - 1), fill=WHITE)
    d.line([(bx + 9, by), (bx + 10, by)], fill=(232, 152, 40)); d.line([(bx - 2, by + 1), (bx - 1, by + 1)], fill=(96, 72, 48))
    if not hop:
        d.point((bx + 2, by + 6), fill=DK); d.point((bx + 4, by + 6), fill=DK)
    return im

@functools.lru_cache(maxsize=None)
def _frame(kind, *a):
    return {"onca": _onca, "tuiuiu": _tuiuiu, "capivara": _capivara}[kind](*a)

def animal(kind, t):
    """sprite RGBA animado (respiração idle) no tempo t"""
    b = 1 if (t % 1.6) > 0.8 else 0
    blink = 1 if (t % 2.9) > 2.75 else 0
    if kind == "onca":
        ph = int(t / 0.4) % 4
        return _frame(kind, b, (0, 1, 2, 1)[ph], blink)
    if kind == "tuiuiu":
        beak = 1 if 1.9 < (t % 3.4) < 2.3 and int(t * 12) % 2 else 0
        return _frame(kind, b, beak, blink)
    ear = 1 if 1.2 < (t % 2.3) < 1.35 else 0
    hop = 2 if 0.9 < (t % 2.6) < 1.05 else 0
    return _frame(kind, b, ear, blink, hop)

def animal_sil(kind, t, color=(8, 16, 16)):
    return silhouette(animal(kind, t), color)

# ---------------------------------------------------------------- pegadas (ícones 13x13)
PAWS = {
 "onca": ["..##...##....", ".####.####...", ".####.####.#.", "..##...##.###", "#.........###", "###.#####..#.",
          "###.######...", ".#.########..", "...########..", "...########..", "....##..##...", ".............", "............."],
 "tuiuiu": ["......#......", "......#......", "#.....#.....#", ".#....#....#.", "..#...#...#..", "...#..#..#...",
            "....#.#.#....", ".....###.....", "......#......", "......#......", "......#......", ".....#.......", "....#........"],
 "capivara": ["....#...#....", "...##...##...", "...##...##...", ".#..#...#..#.", "##.........##", "##..#####..##",
              ".#.#######.#.", "...#######...", "...#######...", "....#####....", ".....###.....", ".............", "............."],
}
def paw(kind, color):
    im = Image.new("RGBA", (13, 13), (0, 0, 0, 0))
    for y, row in enumerate(PAWS[kind]):
        for x, ch in enumerate(row):
            if ch == "#": im.putpixel((x, y), (*color, 255))
    return im
