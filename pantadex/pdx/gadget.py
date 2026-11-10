# -*- coding: utf-8 -*-
"""Corpo do aparelho PANTADEX mk-I (pixel art em grade 540x960, ampliada 2x) + composição do quadro final."""
import math, random
from .common import *

GW, GH = 540, 960
SX, SY = 30, 180            # tela na grade (480x320) -> no quadro: (60,360) 960x640
BODY = (12, 76, 528, 896)
M1 = (92, 118, 64); M0 = (120, 146, 84); M2 = (66, 88, 50); M3 = (44, 60, 38); OLN = (20, 28, 22)
BZ = (26, 30, 34); BT1 = (50, 54, 58); BT0 = (84, 90, 94); BT2 = (24, 26, 30)
Y1 = (244, 196, 52); Y0 = (255, 228, 120); Y2 = (188, 132, 28)
R1 = (204, 92, 56); R0 = (236, 136, 96); R2 = (140, 56, 36)

DPAD = (128, 692); BTN_A = (438, 664); BTN_B = (352, 724); START = (270, 812)
SPK = (364, 800)

def _screw(d, x, y):
    d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=M3); d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(120, 128, 124))
    d.ellipse((x - 4, y - 3, x + 5, y + 5), fill=(88, 96, 96)); d.line((x - 3, y + 3, x + 3, y - 3), fill=(40, 44, 48), width=2)
    d.point((x - 3, y - 3), fill=WHITE)

def make_base():
    im = Image.new("RGB", (GW, GH), (20, 26, 32)); d = draw(im)
    # fundo: mesa escura com padrão discreto
    a = np.array(im)
    yy, xx = np.mgrid[0:GH, 0:GW]
    a[((xx + yy) % 24 == 0)] = (25, 32, 39)
    a[((xx - yy) % 24 == 0) & (yy % 2 == 0)] = (24, 31, 38)
    vig = ((xx - GW / 2) / (GW / 2)) ** 2 + ((yy - GH / 2) / (GH / 2)) ** 2
    a[(vig > 1.0) & ((xx + yy) % 2 == 0)] = (14, 18, 24)
    a[(vig > 1.35)] = (14, 18, 24)
    im = Image.fromarray(a); d = draw(im)
    # alça de pulso (cordão)
    pts = [(52, 884), (44, 912), (60, 938), (120, 950), (200, 946), (236, 928), (214, 910), (150, 914), (96, 908), (70, 890)]
    d.line(pts + [pts[0]], fill=(60, 44, 28), width=9, joint="curve")
    d.line(pts + [pts[0]], fill=(212, 172, 84), width=5, joint="curve")
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        n = int(math.hypot(x1 - x0, y1 - y0) // 6)
        for k in range(n):
            x = x0 + (x1 - x0) * k / n; y = y0 + (y1 - y0) * k / n
            d.rectangle((x - 1, y - 1, x, y), fill=(160, 120, 52))
    d.rectangle((222, 918, 240, 934), fill=Y2, outline=(60, 44, 28)); d.rectangle((226, 922, 236, 930), fill=Y1)
    # antena
    d.rectangle((460, 30, 472, 80), fill=OLN); d.rectangle((462, 30, 470, 80), fill=(72, 78, 82)); d.rectangle((464, 30, 465, 80), fill=(132, 140, 144))
    for y in (44, 58): d.line((462, y, 470, y), fill=OLN)
    d.rectangle((454, 66, 478, 80), fill=OLN); d.rectangle((456, 68, 476, 80), fill=M3)
    d.ellipse((457, 14, 475, 32), fill=OLN); d.ellipse((459, 16, 473, 30), fill=Y1); d.ellipse((461, 18, 466, 23), fill=Y0)
    # sombra + corpo
    x0, y0, x1, y1 = BODY
    d.rounded_rectangle((x0 + 4, y0 + 8, x1 + 6, y1 + 10), radius=44, fill=(10, 13, 17))
    d.rounded_rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), radius=44, fill=OLN)
    d.rounded_rectangle((x0, y0, x1, y1), radius=42, fill=M2)
    d.rounded_rectangle((x0, y0, x1 - 5, y1 - 7), radius=42, fill=M0)
    d.rounded_rectangle((x0 + 4, y0 + 4, x1 - 5, y1 - 7), radius=40, fill=M1)
    # textura de borracha (pontilhado)
    a = np.array(im); rnd = np.random.RandomState(4)
    body = (a[..., 0] == M1[0]) & (a[..., 1] == M1[1]) & (a[..., 2] == M1[2])
    yy, xx = np.mgrid[0:GH, 0:GW]
    a[body & ((xx % 4 == 0) & (yy % 4 == 0))] = (84, 109, 58)
    a[body & ((xx % 4 == 2) & (yy % 4 == 2))] = (99, 126, 70)
    noise = rnd.rand(GH, GW)
    a[body & (noise > 0.992)] = (108, 134, 76); a[body & (noise < 0.008)] = (78, 102, 54)
    im = Image.fromarray(a); d = draw(im)
    # protetores de canto em borracha escura
    msk = Image.new("L", (GW, GH), 0); md = ImageDraw.Draw(msk); md.rounded_rectangle((x0, y0, x1, y1), radius=42, fill=255)
    bump = Image.new("RGB", (GW, GH), M3); bd = ImageDraw.Draw(bump)
    cm = Image.new("L", (GW, GH), 0); cd = ImageDraw.Draw(cm)
    for cx, cy in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        cd.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), fill=255)
    for i in range(-80, 80, 6):
        for cx, cy, s in [(x0, y0, 1), (x1, y0, -1), (x0, y1, -1), (x1, y1, 1)]:
            bd.line((cx - 70, cy + s * (i + 70) - 70 * s + 70 * s, cx + 70, cy + s * (i + 70) - 70 * s - 70 * s + 0), fill=(54, 72, 44), width=2)
    from PIL import ImageChops
    im.paste(bump, (0, 0), ImageChops.multiply(msk, cm)); d = draw(im)
    arcs = Image.new("L", (GW, GH), 0); ad = ImageDraw.Draw(arcs)
    for cx, cy in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        ad.arc((cx - 62, cy - 62, cx + 62, cy + 62), 0, 360, fill=255, width=2)
    im.paste(Image.new("RGB", (GW, GH), OLN), (0, 0), ImageChops.multiply(arcs, msk)); d = draw(im)
    d.rounded_rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), radius=44, outline=OLN, width=3)
    # parafusos
    for sx, sy in [(40, 104), (500, 104), (40, 868), (500, 868)]: _screw(d, sx, sy)
    # faixa amarelo-ipê
    d.rectangle((x0 + 2, 156, x1 - 6, 162), fill=OLN); d.rectangle((x0 + 2, 157, x1 - 6, 161), fill=Y1); d.line((x0 + 2, 161, x1 - 6, 161), fill=Y2)
    # lente do scanner
    lx, ly = 112, 116
    d.ellipse((lx - 37, ly - 37, lx + 37, ly + 37), fill=OLN); d.ellipse((lx - 35, ly - 35, lx + 35, ly + 35), fill=Y1)
    d.ellipse((lx - 35, ly - 31, lx + 31, ly + 35), fill=Y2); d.ellipse((lx - 32, ly - 32, lx + 32, ly + 32), fill=Y1)
    d.ellipse((lx - 28, ly - 28, lx + 28, ly + 28), fill=OLN); d.ellipse((lx - 25, ly - 25, lx + 25, ly + 25), fill=(40, 44, 52))
    for ang in range(0, 360, 30):
        d.point((lx + int(30 * math.cos(math.radians(ang))), ly + int(30 * math.sin(math.radians(ang)))), fill=Y2)
    # LEDs: alojamentos e rótulos
    for cx, lab in [(176, "SCAN"), (214, "REC"), (252, "PWR")]:
        d.ellipse((cx - 9, 96 - 9, cx + 9, 96 + 9), fill=M3); d.ellipse((cx - 7, 96 - 7, cx + 7, 96 + 7), fill=OLN)
        text(d, cx, 112, lab, FT, M3, anchor="c")
    text(d, 176, 128, "LENTE ÓPTICA 4x", FT, M2); 
    # bateria e sinal
    d.rectangle((306, 86, 358, 108), fill=OLN); d.rectangle((358, 92, 362, 102), fill=OLN); d.rectangle((308, 88, 356, 106), fill=(30, 40, 34))
    text(d, 332, 112, "BATERIA", FT, M3, anchor="c")
    d.rectangle((384, 84, 432, 110), fill=OLN); d.rectangle((386, 86, 430, 108), fill=(30, 40, 34))
    text(d, 408, 112, "SINAL", FT, M3, anchor="c")
    # moldura da tela
    d.rounded_rectangle((16, 166, 524, 516), radius=16, fill=OLN)
    d.rounded_rectangle((18, 168, 522, 514), radius=14, fill=Y1); d.rounded_rectangle((18, 170, 522, 514), radius=14, fill=Y2)
    d.rounded_rectangle((20, 170, 520, 512), radius=12, fill=BZ)
    d.rounded_rectangle((20, 170, 520, 512), radius=12, outline=(44, 50, 56))
    d.rectangle((SX - 2, SY - 2, SX + 481, SY + 321), fill=(8, 10, 12))
    text(d, 270, 503, "SCANNER DE CAMPO", FT, (96, 104, 108), anchor="c")
    d.rectangle((40, 504, 44, 508), fill=(60, 66, 70)); d.rectangle((496, 504, 500, 508), fill=(60, 66, 70))
    # adesivo
    d.rectangle((38, 532, 252, 572), fill=(48, 62, 40)); d.rectangle((36, 530, 250, 570), fill=OLN)
    d.rectangle((38, 532, 248, 568), fill=Y1); d.rectangle((38, 564, 248, 568), fill=Y2)
    d.text((46, 541), "PANTADEX", font=F16, fill=(36, 60, 44))
    d.rectangle((182, 540, 242, 558), fill=(36, 60, 44)); d.text((196, 545), "mk-I", font=F8, fill=Y0)
    d.polygon([(248, 532), (240, 532), (248, 540)], fill=M1); d.line((240, 532, 248, 540), fill=Y2)   # canto descolado
    for sx_, sy_, L in [(60, 535, 22), (150, 562, 30), (100, 548, 8)]: d.line((sx_, sy_, sx_ + L, sy_), fill=Y0)
    text(d, 40, 576, "CATALOGADOR DE FAUNA - PANTANAL", FT, M3)
    for k in range(9):
        d.polygon([(300 + k * 14, 548), (308 + k * 14, 548), (300 + k * 14, 536), (292 + k * 14, 536)], fill=Y1 if k % 2 == 0 else M3)
    d.rectangle((290, 534, 420, 535), fill=M3); d.rectangle((290, 549, 420, 550), fill=M3)
    text(d, 292, 556, "MODELO DE CAMPO - À PROVA D'ÁGUA", FT, M3)
    text(d, 292, 566, "Nº DE SÉRIE 0740-MT", FT, M3)
    # nichos dos controles
    cx, cy = DPAD
    d.ellipse((cx - 74, cy - 74, cx + 74, cy + 74), fill=M2); d.ellipse((cx - 72, cy - 70, cx + 74, cy + 74), fill=M3)
    d.ellipse((cx - 70, cy - 68, cx + 70, cy + 70), fill=(58, 78, 46))
    for (bx, by) in (BTN_A, BTN_B):
        d.ellipse((bx - 42, by - 42, bx + 42, by + 44), fill=M3); d.ellipse((bx - 39, by - 38, bx + 39, by + 41), fill=OLN)
    text(d, BTN_A[0] + 36, BTN_A[1] - 54, "A", F8, M3); text(d, BTN_B[0] - 46, BTN_B[1] - 50, "B", F8, M3)
    sx_, sy_ = START
    d.rounded_rectangle((sx_ - 40, sy_ - 14, sx_ + 40, sy_ + 16), radius=14, fill=M3)
    d.rounded_rectangle((sx_ - 37, sy_ - 11, sx_ + 37, sy_ + 14), radius=12, fill=OLN)
    text(d, sx_, sy_ + 22, "START", FT, M3, anchor="c")
    # alto-falante: placa
    gx, gy = SPK
    d.rounded_rectangle((gx - 10, gy - 10, gx + 142, gy + 76), radius=10, fill=M3)
    d.rounded_rectangle((gx - 8, gy - 8, gx + 140, gy + 74), radius=8, fill=M2)
    # ranhuras laterais de pegada
    for y in range(600, 780, 8):
        d.line((x0 + 6, y, x0 + 18, y), fill=M2, width=2); d.line((x0 + 6, y + 2, x0 + 18, y + 2), fill=M0)
        d.line((x1 - 22, y, x1 - 10, y), fill=M2, width=2); d.line((x1 - 22, y + 2, x1 - 10, y + 2), fill=M0)
    # passador da alça
    d.rounded_rectangle((44, 872, 80, 890), radius=6, fill=OLN); d.rounded_rectangle((48, 876, 76, 886), radius=4, fill=(12, 16, 14))
    d.line((56, 880, 56, 896), fill=(212, 172, 84), width=5); d.line((54, 880, 54, 896), fill=(60, 44, 28))
    text(d, 270, 874, "PANTADEX mk-I  -  FEITO NO PANTANAL", FT, M3, anchor="c")
    return im


def _round_btn(d, c, r, col, hi, lo, pressed, label=None):
    cx, cy = c
    if pressed:
        cy += 5
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=lo); d.ellipse((cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), fill=tuple(int(v * 0.86) for v in col))
    else:
        d.ellipse((cx - r, cy - r + 6, cx + r, cy + r + 6), fill=lo)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        d.arc((cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), 180, 290, fill=hi, width=3)
        d.ellipse((cx - r + 9, cy - r + 9, cx - r + 14, cy - r + 14), fill=hi)
    if label:
        d.text((cx - 7, cy - 7), label, font=F16, fill=lo)

def draw_dynamic(im, hud, t):
    d = draw(im)
    pr = hud.get("buttons", ())
    # direcional
    cx, cy = DPAD; hw, L = 21, 60
    arms = {"up": (cx - hw, cy - L, cx + hw, cy - hw), "down": (cx - hw, cy + hw, cx + hw, cy + L),
            "left": (cx - L, cy - hw, cx - hw, cy + hw), "right": (cx + hw, cy - hw, cx + L, cy + hw)}
    for nm, (a0, b0, a1, b1) in arms.items():
        if nm not in pr: d.rounded_rectangle((a0 - 2, b0 + 4, a1 + 2, b1 + 8), radius=5, fill=BT2)
    d.rectangle((cx - hw - 2, cy - hw + 4, cx + hw + 2, cy + hw + 8), fill=BT2)
    for nm, (a0, b0, a1, b1) in arms.items():
        p = nm in pr; oy = 5 if p else 0
        col = (36, 40, 44) if p else BT1
        d.rounded_rectangle((a0 - 2, b0 + oy - 2, a1 + 2, b1 + oy + 2), radius=5, fill=BT2 if p else (30, 33, 37))
        d.rounded_rectangle((a0, b0 + oy, a1, b1 + oy), radius=4, fill=col)
        if not p:
            if nm == "up": d.line((a0 + 3, b0 + 1, a1 - 3, b0 + 1), fill=BT0)
            if nm == "left": d.line((a0 + 1, b0 + 3, a0 + 1, b1 - 3), fill=BT0)
            if nm in ("left", "right"): d.line((a0 + 3, b0 + 1, a1 - 1, b0 + 1), fill=BT0)
        mx, my = (a0 + a1) // 2, (b0 + b1) // 2 + oy
        ac = Y1 if p else (104, 110, 114)
        tri = {"up": [(mx, my - 8), (mx - 8, my + 4), (mx + 8, my + 4)], "down": [(mx, my + 8), (mx - 8, my - 4), (mx + 8, my - 4)],
               "left": [(mx - 8, my), (mx + 4, my - 8), (mx + 4, my + 8)], "right": [(mx + 8, my), (mx - 4, my - 8), (mx - 4, my + 8)]}[nm]
        d.polygon(tri, fill=ac)
    d.rectangle((cx - hw, cy - hw, cx + hw, cy + hw), fill=BT1)
    d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(40, 44, 48)); d.ellipse((cx - 7, cy - 6, cx + 8, cy + 8), fill=(58, 62, 66))
    # botões de ação e START
    _round_btn(d, BTN_A, 34, Y1, Y0, Y2, "A" in pr, "A")
    _round_btn(d, BTN_B, 34, R1, R0, R2, "B" in pr, "B")
    sx, sy = START; p = "START" in pr; oy = 5 if p else 0
    if not p: d.rounded_rectangle((sx - 34, sy - 8 + 5, sx + 34, sy + 8 + 5), radius=9, fill=BT2)
    d.rounded_rectangle((sx - 34, sy - 8 + oy, sx + 34, sy + 8 + oy), radius=9, fill=(40, 44, 48) if p else BT1)
    if not p: d.line((sx - 26, sy - 6, sx + 26, sy - 6), fill=BT0)
    # alto-falante (vibra com a narração)
    gx, gy = SPK; lv = hud.get("speaker", 0.0)
    for r in range(6):
        for c in range(11):
            if (r in (0, 5)) and c in (0, 10): continue
            jx = jy = 0
            if lv > 0.06:
                ph = int(t * 30)
                if (r + c + ph) % 2 == 0: jy = 1 if lv < 0.4 else (1 if ph % 2 else -1)
                if lv > 0.5 and (r * 3 + c + ph) % 5 == 0: jx = 1
            x = gx + 6 + c * 12 + jx; y = gy + 4 + r * 12 + jy
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=OLN)
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(14, 18, 16) if lv <= 0.06 else (30, 40, 30))
            d.point((x + 2, y + 3), fill=M0 if lv <= 0.06 else Y0 if (lv > 0.45 and (r + c + int(t * 30)) % 3 == 0) else M0)
    # LEDs
    def led(cx, col_on, level, r=6):
        off = (36, 44, 40)
        col = tuple(int(off[i] + (col_on[i] - off[i]) * level) for i in range(3))
        d.ellipse((cx - r, 96 - r, cx + r, 96 + r), fill=col)
        if level > 0.3: d.rectangle((cx - 3, 96 - 4, cx - 1, 96 - 2), fill=WHITE)
        if level > 0.6:
            for ang in range(0, 360, 30):
                d.point((cx + int((r + 5) * math.cos(math.radians(ang))), 96 + int((r + 5) * math.sin(math.radians(ang)))), fill=col_on)
    sc = hud.get("scan", 0.0)
    led(176, (112, 255, 208), sc)
    led(214, (255, 64, 56), 1.0 if hud.get("rec") else 0.0)
    led(252, (136, 232, 88), 0.85 if hud.get("power") else 0.0)
    # lente
    lx, ly = 112, 116
    g0 = (20, 32, 60); g1 = (72, 232, 200)
    gl = tuple(int(g0[i] + (g1[i] - g0[i]) * sc * 0.8) for i in range(3))
    d.ellipse((lx - 22, ly - 22, lx + 22, ly + 22), fill=gl)
    d.ellipse((lx - 14, ly - 14, lx + 14, ly + 14), fill=tuple(int(v * 0.7) for v in gl))
    d.ellipse((lx - 7, ly - 7, lx + 7, ly + 7), fill=(8, 10, 20) if sc < 0.5 else (200, 255, 240))
    d.arc((lx - 20, ly - 20, lx + 20, ly + 20), 200, 260, fill=(150, 190, 230), width=3)
    d.ellipse((lx - 13, ly - 15, lx - 8, ly - 10), fill=WHITE)
    if sc > 0.6:
        for ang in range(0, 360, 20):
            d.point((lx + int(41 * math.cos(math.radians(ang + t * 90))), ly + int(41 * math.sin(math.radians(ang + t * 90)))), fill=g1)
    # bateria / sinal / antena
    if hud.get("power"):
        nb = hud.get("battery", 3)
        for k in range(3):
            if k < nb: d.rectangle((311 + k * 15, 91, 322 + k * 15, 103), fill=(136, 232, 88) if nb > 1 else Y1)
        sg = hud.get("signal", 1)
        for k in range(4):
            h = 5 + k * 4
            d.rectangle((390 + k * 10, 105 - h, 396 + k * 10, 105), fill=(112, 255, 208) if k < sg else (44, 60, 52))
        if sg >= 3 and int(t * 6) % 2 == 0:
            for rr in (16, 24):
                d.arc((466 - rr, 23 - rr, 466 + rr, 23 + rr), 200, 250, fill=(112, 255, 208), width=2)
                d.arc((466 - rr, 23 - rr, 466 + rr, 23 + rr), 290, 340, fill=(112, 255, 208), width=2)

def make_glass():
    ov = Image.new("RGBA", (960, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.polygon([(500, 0), (700, 0), (400, 640), (200, 640)], fill=(255, 255, 255, 10))
    d.polygon([(740, 0), (790, 0), (490, 640), (440, 640)], fill=(255, 255, 255, 8))
    a = np.array(ov)
    a[3::4, :, :3] = 0; a[3::4, :, 3] = 44          # scanlines
    a[:2, :, :3] = 0; a[:2, :, 3] = 110; a[:, :2, :3] = 0; a[:, :2, 3] = 110   # sombra interna
    return Image.fromarray(a, "RGBA")

BASE = None; GLASS = None
def compose(screen, hud, t):
    global BASE, GLASS
    if BASE is None: BASE = make_base(); GLASS = make_glass()
    g = BASE.copy()
    draw_dynamic(g, hud, t)
    fr = g.resize((1080, 1920), Image.NEAREST)
    sc = screen.resize((960, 640), Image.NEAREST).convert("RGBA")
    sc.alpha_composite(GLASS)
    fr.paste(sc.convert("RGB"), (SX * 2, SY * 2))
    return fr
