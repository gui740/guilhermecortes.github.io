# -*- coding: utf-8 -*-
"""Telas 240x160 do sistema: boot, transições, escaneamento, ficha, encerramento."""
import math, random, functools
from .common import *
from .animals import animal, animal_sil, paw
from .script import ANIMALS

def new(color=BLACK):
    im = Image.new("RGB", (W, H), color); return im, draw(im)

def wrap(s, n=27):
    out, cur = [], ""
    for w in s.split(" "):
        if len(cur) + len(w) + (1 if cur else 0) > n: out.append(cur); cur = w
        else: cur = (cur + " " + w) if cur else w
    if cur: out.append(cur)
    return out

def box(d, x0, y0, x1, y1, fill=CREAM, border=DKGREEN, inner=None):
    d.rectangle((x0 + 1, y0, x1 - 1, y1), fill=border); d.rectangle((x0, y0 + 1, x1, y1 - 1), fill=border)
    d.rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2), fill=fill)
    if inner: d.rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2), outline=inner)

# ---------------------------------------------------------------- BOOT
@functools.lru_cache(maxsize=None)
def _logo_pixels():
    m = Image.new("L", (128, 16), 0); d = draw(m); d.text((0, 0), "PANTADEX", font=F16, fill=255)
    a = np.array(m) > 0
    rnd = random.Random(1)
    pts = []
    for y in range(16):
        for x in range(128):
            if a[y, x]: pts.append((x, y, clamp(x / 128 * 0.75 + rnd.random() * 0.25)))
    return pts

def logo(d, ox, oy, p=1.0, t=0.0):
    hi = (255, 232, 112)
    for x, y, r in _logo_pixels():
        if p >= r:
            fall = clamp((p - r) / 0.07)
            yy = oy + y - int((1 - fall) * 12)
            col = WHITE if fall < 1 else (hi if y < 7 else IPE if y < 12 else IPE_D)
            if fall >= 1: d.point((ox + x + 1, oy + y + 1), fill=(88, 56, 16))
            d.point((ox + x, yy), fill=col)
    if p >= 1:   # brilho que passa
        sx = int(((t * 0.9) % 2.2) * 128) - 20
        for x, y, r in _logo_pixels():
            if 0 <= (x + y) - sx < 5: d.point((ox + x, oy + y), fill=WHITE)

def boot(lt):
    if lt < 0.5: return new((4, 6, 8))[0]
    bg = (10, 22, 20)
    im, d = new(bg)
    p = clamp((lt - 0.7) / 1.9)
    if p >= 1:
        for i, y in enumerate(range(0, H, 4)):
            if (y // 4) % 2 == 0: d.line((0, y, W, y), fill=(14, 30, 26))
        d.rectangle((0, 0, W - 1, 5), fill=MOSS); d.rectangle((0, H - 6, W - 1, H - 1), fill=MOSS)
        d.line((0, 6, W, 6), fill=IPE_D); d.line((0, H - 7, W, H - 7), fill=IPE_D)
    logo(d, 56, 50, p, lt)
    if lt > 2.5:
        pw = paw("onca", IPE)
        k = clamp((lt - 2.5) / 0.3)
        d.line((120 - int(64 * k), 71, 120 + int(64 * k), 71), fill=LEAF)
        if lt > 2.7: im.paste(pw, (113, 30), pw)
    if lt > 2.9:
        s = "SISTEMA DE CAMPO v1.0"; n = int(clamp((lt - 2.9) / 0.9) * len(s))
        text(d, 36, 80, s[:n], F8, CREAM)
        if n < len(s) and int(lt * 12) % 2: d.rectangle((36 + n * 8, 80, 36 + n * 8 + 6, 87), fill=CREAM)
    if lt > 3.9:
        text(d, 120, 97, "FAUNA DO PANTANAL MATO-GROSSENSE", FT, LEAF, anchor="c")
    if lt > 4.1 and (int(lt * 4) % 2 or lt > 4.7):
        text(d, 120, 124, "PRESSIONE START", F8, IPE if lt < 4.7 else WHITE, anchor="c")
    return im

# ---------------------------------------------------------------- transição em faixas
def stripes(a, b, p, n=8):
    """p 0..0.5: faixas pretas cobrem 'a'; 0.5..1: abrem revelando 'b'"""
    src = a if p < 0.5 else b
    im = src.copy(); d = draw(im)
    k = p * 2 if p < 0.5 else (1 - p) * 2
    h = H // n
    wpx = int(round(ease(k) * W / 8)) * 8
    for i in range(n if wpx > 0 else 0):
        if i % 2 == 0: d.rectangle((0, i * h, wpx - 1, i * h + h - 1), fill=BLACK)
        else: d.rectangle((W - wpx, i * h, W, i * h + h - 1), fill=BLACK)
    return im

def white(im, k):
    a = np.array(im).astype(np.int16)
    a = a + (255 - a) * k
    return Image.fromarray(a.astype(np.uint8))

# ---------------------------------------------------------------- ESCANEAMENTO
def scan(i, p, t):
    kind = ANIMALS[i]["key"]
    im, d = new((8, 20, 24))
    off = int(t * 12) % 16
    for x in range(-16, W + 16, 16): d.line((x + off, 0, x + off, H), fill=(14, 36, 38))
    for y in range(0, H, 16): d.line((0, y, W, y), fill=(14, 36, 38))
    x0, y0, x1, y1 = 44, 18, 195, 112
    sp = animal_sil(kind, t, (2, 8, 10))
    rim = animal_sil(kind, t, (24, 88, 80))
    bb = sp.getbbox()
    px = 120 - (bb[0] + bb[2]) // 2; py = (y0 + y1) // 2 - (bb[1] + bb[3]) // 2 + 2
    im.paste(rim, (px - 1, py), rim); im.paste(rim, (px + 1, py), rim); im.paste(rim, (px, py - 1), rim); im.paste(rim, (px, py + 1), rim)
    im.paste(sp, (px, py), sp)
    # linha de varredura (revela uma faixa em ciano)
    ph = (t * 0.9) % 2; ph = ph if ph < 1 else 2 - ph
    ly = int(y0 + 4 + ph * (y1 - y0 - 8))
    band = np.array(animal_sil(kind, t, CYAN)); bandim = Image.fromarray(band, "RGBA").crop((0, ly - py - 2, sp.width, ly - py + 3))
    im.paste(bandim, (px, ly - 2), bandim)
    d = draw(im)
    for x in range(x0 + 2, x1 - 1):
        if (x + int(t * 30)) % 3: d.point((x, ly), fill=CYAN)
    L = 10
    for cx, cy, sx, sy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.line((cx, cy, cx + sx * L, cy), fill=CYAN); d.line((cx, cy, cx, cy + sy * L), fill=CYAN)
        d.line((cx, cy + sy, cx + sx * L, cy + sy), fill=CYAN); d.line((cx + sx, cy, cx + sx, cy + sy * L), fill=CYAN)
    text(d, 6, 5, "ESPÉCIE: ???", FT, CYAN)
    text(d, 234, 5, "Nº " + ANIMALS[i]["num"], FT, CYAN, anchor="r")
    for k, (lab, yy) in enumerate([("DIST", 30), ("TEMP", 46), ("MOV", 62)]):
        text(d, 6, yy, lab, FT, (40, 120, 112))
        v = int(abs(math.sin(t * (3 + k) + k)) * 5) + 1
        for j in range(6): d.rectangle((6 + j * 4, yy + 7, 8 + j * 4, yy + 9), fill=CYAN if j < v else (16, 52, 52))
    done = p >= 0.93
    if done:
        if int(t * 10) % 2: text(d, 120, 119, "IDENTIFICADO!", F8, IPE, anchor="c")
    else:
        text(d, 76, 119, "ESCANEANDO" + "." * (1 + int(t * 5) % 3), F8, CREAM)
    d.rectangle((40, 133, 199, 143), outline=CREAM)
    n = int(clamp(p / 0.93) * 26)
    for j in range(n): d.rectangle((42 + j * 6, 135, 46 + j * 6, 141), fill=IPE if not done else CYAN)
    text(d, 204, 135, f"{int(clamp(p / 0.93) * 100):3d}%", FT, CREAM)
    return im

# ---------------------------------------------------------------- FICHA
@functools.lru_cache(maxsize=None)
def backdrop(kind):
    w, h = 94, 82
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im); rnd = random.Random(hash(kind) % 1000 if False else len(kind))
    if kind == "onca":
        d.rectangle((0, 0, w, h), fill=(40, 96, 64))
        for _ in range(26):
            x = rnd.randint(-8, w); y = rnd.randint(-6, 34); r = rnd.randint(6, 12)
            d.ellipse((x, y, x + r * 2, y + r), fill=rnd.choice([(32, 80, 56), (48, 112, 68), (56, 128, 72)]))
        for x in (8, 30, 70, 86): d.rectangle((x, 20, x + rnd.randint(3, 5), 62), fill=(64, 56, 48))
        d.rectangle((0, 58, w, h), fill=(128, 160, 80)); d.rectangle((0, 58, w, 60), fill=(88, 128, 64))
        for _ in range(30):
            x = rnd.randint(0, w); y = rnd.randint(62, h)
            d.point([(x, y), (x + 1, y - 1)], fill=(96, 136, 64))
        for _ in range(8): d.point((rnd.randint(0, w), rnd.randint(60, h)), fill=(248, 208, 72))
    elif kind == "tuiuiu":
        for y in range(h):
            d.line((0, y, w, y), fill=(136, 208, 232) if y < 30 else (176, 224, 240) if y < 50 else (88, 160, 208))
        d.ellipse((60, 8, 84, 16), fill=WHITE); d.ellipse((70, 5, 88, 14), fill=WHITE); d.ellipse((8, 16, 26, 22), fill=WHITE)
        for x in range(0, w, 3):
            hh = 4 + int(3 * math.sin(x * 0.4) + 2 * math.sin(x * 1.3))
            d.rectangle((x, 50 - hh, x + 3, 52), fill=(64, 128, 80))
        d.rectangle((0, 52, w, 54), fill=(48, 104, 72))
        for _ in range(16):
            x = rnd.randint(0, w - 6); y = rnd.randint(57, h - 1)
            d.line((x, y, x + rnd.randint(3, 7), y), fill=(152, 200, 232))
        for x in (6, 78): 
            for k in range(4): d.line((x + k * 3, 80, x + k * 3 + rnd.randint(-1, 1), 64 - rnd.randint(0, 6)), fill=(72, 144, 72))
    else:
        for y in range(h):
            d.line((0, y, w, y), fill=(160, 216, 232) if y < 26 else (192, 228, 216))
        d.ellipse((66, 6, 80, 20), fill=(255, 236, 160))
        for x in range(0, w, 4):
            hh = 3 + int(3 * math.sin(x * 0.3))
            d.rectangle((x, 34 - hh, x + 4, 40), fill=(72, 136, 80))
        d.rectangle((0, 38, w, 70), fill=(136, 176, 80)); d.rectangle((0, 38, w, 39), fill=(96, 144, 72))
        d.rectangle((0, 70, w, h), fill=(80, 152, 200)); d.rectangle((0, 70, w, 71), fill=(104, 96, 64))
        for _ in range(26):
            x = rnd.randint(0, w); y = rnd.randint(42, 68); d.point([(x, y), (x + 1, y - 1)], fill=(104, 152, 72))
        for _ in range(7):
            x = rnd.randint(0, w - 6); d.line((x, rnd.randint(74, h - 1), x + 5, rnd.randint(74, h - 1)), fill=(152, 200, 232))
    return im

SPR_Y = {"onca": 74, "tuiuiu": 80, "capivara": 70}   # linha do chão dentro da janela

def ficha(i, lt, st):
    """st: dict(page, chars, done, bars=[0..1]*3, selo=None|0..1, rows=n)"""
    a = ANIMALS[i]; kind = a["key"]
    im, d = new((216, 224, 176))
    for y in range(12, 113, 2): d.line((0, y, W, y), fill=(208, 216, 168))
    # cabeçalho
    d.rectangle((0, 0, W, 11), fill=DKGREEN); d.line((0, 11, W, 11), fill=IPE_D)
    text(d, 5, 3, "PANTADEX", FT, IPE); text(d, 50, 3, "FICHA DE CAMPO", FT, LEAF)
    text(d, 222, 3, f"{i + 1}/3", FT, CREAM, anchor="r")
    if int(lt * 2) % 2 == 0: d.rectangle((227, 4, 231, 8), fill=RED)
    # janela do sprite
    box(d, 3, 14, 100, 99, fill=BLACK, border=DKGREEN)
    bg = backdrop(kind)
    im.paste(bg, (5, 16))
    sp = animal(kind, lt)
    bb = animal(kind, 0).getbbox()
    sx = 5 + 47 - (bb[0] + bb[2]) // 2; sy = 16 + SPR_Y[kind] - bb[3]
    win = Image.new("RGBA", (94, 82), (0, 0, 0, 0)); win.paste(sp, (sx - 5, sy - 16), sp)
    # sombra no chão
    wd = ImageDraw.Draw(im)
    for xx in range(bb[0] + 6, bb[2] - 6):
        for yy in range(0, 3):
            if (xx + yy) % 2 == 0:
                X, Y = sx + xx, 16 + SPR_Y[kind] - 2 + yy
                if 5 <= X < 99 and 16 <= Y < 98:
                    r, g, b = im.getpixel((X, Y)); im.putpixel((X, Y), (r * 2 // 3, g * 2 // 3, b * 2 // 3))
    if lt < 0.35:
        win = silhouette(win, WHITE if lt < 0.18 else (255, 240, 160))
    im.paste(win, (5, 16), win)
    d = draw(im)
    rows = st.get("rows", 99)
    X0 = 105
    if rows > 0:
        text(d, X0, 16, "Nº " + a["num"], FT, IPE_D)
        box(d, 219, 14, 236, 31, fill=CREAM, border=DKGREEN)
        pw = paw(kind, DKGREEN); im.paste(pw, (221, 16), pw); d = draw(im)
    if rows > 1: text(d, X0, 24, a["name"], F8, DKGREEN, shadow=(176, 192, 136))
    if rows > 2: text(d, X0, 36, a["sci"], FT, (96, 112, 72))
    if rows > 3:
        x = X0
        text(d, x, 47, "TIPO", FT, DKGREEN); x += 22
        for ty_, col in zip(a["types"], [(184, 96, 56), (72, 120, 136)]):
            wd_ = tw(ty_, FT) + 7
            d.rectangle((x + 1, 45, x + wd_ - 1, 54), fill=col); d.rectangle((x, 46, x + wd_, 53), fill=col)
            text(d, x + 4, 47, ty_, FT, WHITE); x += wd_ + 3
    if rows > 4:
        text(d, X0, 58, "ALT.", FT, DKGREEN); text(d, X0 + 22, 58, a["alt"], FT, (64, 72, 48))
        text(d, X0 + 62, 58, "PESO", FT, DKGREEN); text(d, X0 + 86, 58, a["peso"], FT, (64, 72, 48))
    if rows > 5:
        text(d, X0, 67, "HABITAT", FT, DKGREEN)
        text(d, X0 + 38, 67, a["habitat"][0], FT, (64, 72, 48)); text(d, X0 + 38, 74, a["habitat"][1], FT, (64, 72, 48))
    if rows > 6:
        d.line((X0, 83, 235, 83), fill=(168, 184, 128))
        for k, (lab, val) in enumerate(a["stats"]):
            y = 87 + k * 9
            text(d, X0, y, lab, FT, DKGREEN)
            f = st["bars"][k] * val
            for j in range(10):
                on = j < int(f + 0.001)
                col = (IPE if val >= 7 else LEAF) if on else (176, 188, 144)
                if on and j == int(f + 0.001) - 1 and st["bars"][k] < 1: col = WHITE
                d.rectangle((X0 + 42 + j * 7, y, X0 + 47 + j * 7, y + 5), fill=col)
                if on: d.line((X0 + 42 + j * 7, y + 5, X0 + 47 + j * 7, y + 5), fill=IPE_D if val >= 7 else MOSS)
            if st["bars"][k] >= 1: text(d, 233, y, str(val), FT, DKGREEN, anchor="r")
    # selo de status de conservação
    s = st.get("selo")
    if s is not None:
        col = (48, 128, 72) if a["status_ok"] else (200, 56, 40)
        g = 3 if s < 0.06 else 1 if s < 0.12 else 0
        d.rectangle((3 - g, 101 - g, 100 + g, 111 + g), fill=WHITE if g else CREAM, outline=col)
        if not g:
            d.rectangle((4, 102, 99, 110), outline=col); d.rectangle((5, 103, 98, 109), fill=CREAM)
            text(d, 52, 103, a["status"], FT, col, anchor="c")
            d.rectangle((7, 105, 9, 107), fill=col); d.rectangle((94, 105, 96, 107), fill=col)
    else:
        text(d, 52, 103, "STATUS: ANALISANDO", FT, (152, 164, 120), anchor="c")
    # caixa de texto
    box(d, 3, 114, 236, 157, fill=WHITE, border=DKGREEN, inner=IPE)
    pg = st.get("page", -1)
    if pg >= 0:
        lines = wrap(a["pages"][pg]); n = st["chars"]
        for li, ln in enumerate(lines):
            if n <= 0: break
            text(d, 12, 121 + li * 11, ln[:n], F8, (32, 40, 40)); n -= len(ln) + 1
        if st["done"] and int(lt * 4) % 2:
            d.polygon([(224, 148), (230, 148), (227, 152)], fill=RED)
    return im

# ---------------------------------------------------------------- ENCERRAMENTO
def check(d, x, y, col):
    d.line((x, y + 3, x + 2, y + 5), fill=col); d.line((x + 2, y + 5, x + 7, y), fill=col)
    d.line((x, y + 4, x + 2, y + 6), fill=col); d.line((x + 2, y + 6, x + 7, y + 1), fill=col)

def end(lt):
    if lt >= 7.55: return new((4, 6, 8))[0]
    if lt < 5.3:
        im, d = new((16, 40, 36))
        for y in range(0, H, 4): d.line((0, y, W, y), fill=(20, 46, 40))
        d.rectangle((0, 0, W, 11), fill=DKGREEN); d.line((0, 11, W, 11), fill=IPE_D)
        text(d, 5, 3, "PANTADEX", FT, IPE); text(d, 50, 3, "REGISTRO DE CAMPO", FT, LEAF)
        for k, a in enumerate(ANIMALS):
            t0 = 0.4 + k * 0.5
            if lt < t0: continue
            y = 17 + k * 26
            slide = int((1 - ease((lt - t0) / 0.2)) * 40)
            box(d, 14 + slide, y, 225 + slide, y + 22, fill=CREAM, border=BLACK)
            pw = paw(a["key"], DKGREEN); im.paste(pw, (19 + slide, y + 5), pw); d = draw(im)
            text(d, 38 + slide, y + 8, a["num"], FT, IPE_D)
            text(d, 60 + slide, y + 4, a["name"], F8, DKGREEN); text(d, 60 + slide, y + 14, a["sci"], FT, (112, 128, 88))
            if lt > t0 + 0.25: check(d, 208 + slide, y + 8, (48, 144, 72))
        if lt > 2.1:
            text(d, 120, 100, "3 ESPÉCIES CATALOGADAS", F8, IPE, shadow=BLACK, anchor="c")
        if 3.3 <= lt < 4.5:
            text(d, 120, 118, "SALVANDO REGISTRO...", FT, CREAM, anchor="c")
            d.rectangle((60, 130, 179, 138), outline=CREAM)
            n = int(clamp((lt - 3.3) / 1.1) * 19)
            for j in range(n): d.rectangle((62 + j * 6, 132, 66 + j * 6, 136), fill=IPE)
        elif lt >= 4.5:
            text(d, 120, 124, "REGISTRO SALVO!", F8, WHITE, shadow=BLACK, anchor="c")
        elif lt > 2.6 and int(lt * 4) % 2:
            text(d, 120, 124, "START: SALVAR", FT, CREAM, anchor="c")
        return im
    im, d = new((10, 22, 20))
    for y in range(0, H, 8): d.line((0, y, W, y), fill=(14, 30, 26))
    d.rectangle((0, 0, W - 1, 5), fill=MOSS); d.rectangle((0, H - 6, W - 1, H - 1), fill=MOSS)
    d.line((0, 6, W, 6), fill=IPE_D); d.line((0, H - 7, W, H - 7), fill=IPE_D)
    logo(d, 56, 26, 1.0, lt)
    d.line((56, 47, 184, 47), fill=LEAF)
    k = lt - 5.3
    if k > 0.2: text(d, 120, 62, "CONHECER PARA", F8, CREAM, anchor="c")
    if k > 0.45: text(d, 120, 76, "PROTEGER", F8, IPE, anchor="c")
    if k > 0.7:
        for j, a in enumerate(ANIMALS):
            pw = paw(a["key"], LEAF); im.paste(pw, (88 + j * 26, 96), pw)
        d = draw(im)
        text(d, 120, 122, "PANTANAL MATO-GROSSENSE - BRASIL", FT, LEAF, anchor="c")
    if lt >= 7.1:    # desligar: colapso tipo CRT
        q = clamp((lt - 7.1) / 0.4)
        out, d2 = new((4, 6, 8))
        if q < 0.6:
            hh = max(2, int(H * (1 - q / 0.6)))
            out.paste(white(im.resize((W, hh), Image.NEAREST), q), (0, (H - hh) // 2))
        else:
            ww = max(2, int(W * (1 - (q - 0.6) / 0.4)))
            d2.rectangle(((W - ww) // 2, H // 2 - 1, (W + ww) // 2, H // 2), fill=WHITE)
        return out
    return im
