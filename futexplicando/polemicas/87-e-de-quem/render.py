"""@futexplicando — 87 É DE QUEM?! — render 9:16 com personagens chibi desenhados em código."""
import math, random, subprocess, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
import os
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
ANTON = os.path.join(HERE, "fonts", "Anton-Regular.ttf")
POP = os.path.join(HERE, "fonts", "Poppins-Bold.ttf")
YEL = (255, 212, 0)
BLK = (12, 12, 16)
OUT = 9  # contorno dos desenhos

def F(path, size):
    return ImageFont.truetype(path, size)

# ---------------------------------------------------------------- cenários
def sky(d, top=(8, 20, 70), bot=(30, 62, 160), y0=0, y1=1000):
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0)
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))

def floodlight(img, cx, cy):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([cx - 260, cy - 200, cx + 260, cy + 200], fill=(255, 250, 210, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([cx - 130, cy - 75, cx + 130, cy + 75], 14, fill=(40, 44, 60), outline=BLK, width=6)
    for r in range(3):
        for c in range(5):
            x, y = cx - 100 + c * 50, cy - 48 + r * 48
            d.ellipse([x - 19, y - 19, x + 19, y + 19], fill=(255, 255, 235), outline=(255, 230, 140), width=3)
    # brilho em estrela
    for a in range(8):
        ang = a * math.pi / 4
        L = 190 if a % 2 == 0 else 110
        d.line([(cx, cy), (cx + L * math.cos(ang), cy + L * math.sin(ang))], fill=(255, 255, 220), width=5)

def sparkles(d, n=55, ymax=760, seed=3):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.randint(0, W), rnd.randint(40, ymax)
        s = rnd.randint(5, 13)
        col = YEL if rnd.random() < .7 else (255, 255, 255)
        if rnd.random() < .5:
            d.polygon([(x, y - s), (x + s * .3, y - s * .3), (x + s, y), (x + s * .3, y + s * .3),
                       (x, y + s), (x - s * .3, y + s * .3), (x - s, y), (x - s * .3, y - s * .3)], fill=col)
        else:
            d.line([(x, y), (x + s * 1.4, y - s * .7)], fill=col, width=5)

def crowd(d, y0=760, y1=1060, seed=7):
    rnd = random.Random(seed)
    d.rectangle([0, y0, W, y1], fill=(22, 26, 48))
    cols = [(220, 40, 40), (250, 250, 250), (20, 20, 20), (255, 210, 0), (40, 90, 200), (230, 120, 40), (40, 160, 70)]
    y = y0 + 14
    row = 0
    while y < y1 - 8:
        x = (row % 2) * 11
        while x < W:
            d.ellipse([x, y, x + 15, y + 15], fill=rnd.choice(cols))
            x += 22
        y += 20; row += 1
    d.rectangle([0, y1 - 26, W, y1], fill=(235, 235, 240), outline=BLK, width=4)  # placa de publicidade
    for i in range(0, W, 270):
        d.rectangle([i + 20, y1 - 21, i + 230, y1 - 5], fill=(30, 120, 60))

def field(d, y0=1060):
    for i, y in enumerate(range(y0, H, 95)):
        d.rectangle([0, y, W, y + 95], fill=(46, 160, 64) if i % 2 == 0 else (58, 178, 76))
    d.line([(0, y0 + 300), (W, y0 + 300)], fill=(240, 255, 240), width=8)
    d.arc([W / 2 - 330, y0 + 140, W / 2 + 330, y0 + 460], 0, 360, fill=(240, 255, 240), width=8)

def bg_stadium(seed=3):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    sky(d, y1=780)
    sparkles(d, seed=seed)
    floodlight(img, 120, 150)
    floodlight(img, W - 120, 150)
    d = ImageDraw.Draw(img)
    crowd(d)
    field(d)
    return img

def bg_newsroom():
    img = Image.new("RGBA", (W, H), (226, 206, 160))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 120):
        d.rectangle([x, 0, x + 60, 1150], fill=(214, 192, 144))
    # estantes de arquivo
    for x in (40, 790):
        d.rectangle([x, 300, x + 250, 1150], fill=(120, 84, 52), outline=BLK, width=6)
        for y in range(330, 1130, 110):
            d.rectangle([x + 20, y, x + 230, y + 80], fill=(150, 108, 70), outline=BLK, width=4)
            d.rectangle([x + 105, y + 30, x + 145, y + 45], fill=(60, 50, 40))
    d.rectangle([0, 1150, W, H], fill=(142, 98, 60))
    for y in range(1150, H, 70):
        d.line([(0, y), (W, y)], fill=(120, 82, 50), width=5)
    return img

def bg_split():
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    sky(d, y1=H)
    sparkles(d, n=40, ymax=H - 100, seed=11)
    d.polygon([(0, 380), (W / 2 + 60, 380), (W / 2 - 60, 1700), (0, 1700)], fill=(40, 170, 80), outline=BLK, width=OUT)
    d.polygon([(W / 2 + 80, 380), (W, 380), (W, 1700), (W / 2 - 40, 1700)], fill=(255, 205, 20), outline=BLK, width=OUT)
    return img

def bg_court():
    img = Image.new("RGBA", (W, H), (92, 54, 30))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 180):
        d.rectangle([x + 15, 80, x + 165, 1000], fill=(110, 66, 38), outline=(70, 40, 22), width=6)
    d.ellipse([W / 2 - 150, 120, W / 2 + 150, 420], fill=(200, 170, 80), outline=BLK, width=OUT)
    d.text((W / 2, 270), "STF", font=F(ANTON, 120), fill=(90, 60, 20), anchor="mm")
    d.rectangle([60, 1050, W - 60, 1350], fill=(70, 40, 20), outline=BLK, width=OUT)  # bancada
    d.rectangle([0, 1350, W, H], fill=(60, 36, 20))
    return img

# ------------------------------------------------------------------ escudos (placeholder)
CLUBS = {
    "FLA": dict(stripes=[(200, 16, 30), (20, 20, 20)], badge=((200, 16, 30), (20, 20, 20)), txt="CRF"),
    "SPT": dict(stripes=[(210, 20, 30), (20, 20, 20)], badge=((20, 20, 20), (210, 20, 30)), txt="SCR", gold=True),
    "INT": dict(stripes=[(205, 20, 30)], badge=((205, 20, 30), (255, 255, 255)), txt="SCI"),
    "GUA": dict(stripes=[(10, 120, 60)], badge=((10, 120, 60), (255, 255, 255)), txt="GFC"),
}

_CREST = {}
def shield(size, club):
    """Escudo oficial (PNG em escudos/) cabendo numa caixa size x size*1.18, com sombra."""
    key = (size, club)
    if key in _CREST:
        return _CREST[key]
    src = Image.open(f"escudos/{club}.png").convert("RGBA")
    src.thumbnail((size, int(size * 1.18)), Image.LANCZOS)
    pad = max(4, size // 20)
    im = Image.new("RGBA", (src.width + pad * 2, src.height + pad * 2), (0, 0, 0, 0))
    a = src.split()[3].point(lambda v: 255 if v > 20 else 0)
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    glow.paste((255, 255, 255, 255), (pad, pad), a)
    glow = glow.filter(ImageFilter.MaxFilter(pad * 2 - 1 if pad * 2 % 2 == 0 else pad * 2))
    im.alpha_composite(glow)
    im.alpha_composite(src, (pad, pad))
    _CREST[key] = im
    return im

# ------------------------------------------------------------------ chibi
SKINS = [(242, 196, 158), (196, 136, 92), (140, 92, 60), (228, 176, 132)]

def chibi(club, expr="happy", pose="idle", skin=0, hair=(30, 22, 18), flip=False, prop=None):
    """Desenha um personagem chibi num sprite RGBA 600x900. Retorna sprite."""
    S = Image.new("RGBA", (620, 920), (0, 0, 0, 0))
    d = ImageDraw.Draw(S)
    cx = 310
    sk = SKINS[skin]
    c = CLUBS[club]
    # pernas
    for lx in (cx - 55, cx + 15):
        d.rounded_rectangle([lx, 720, lx + 42, 830], 10, fill=sk, outline=BLK, width=OUT)
        d.rounded_rectangle([lx - 4, 770, lx + 46, 830], 8, fill=c["stripes"][0], outline=BLK, width=OUT)  # meião
        d.rounded_rectangle([lx - 18, 818, lx + 54, 862], 16, fill=(25, 25, 25), outline=BLK, width=OUT)  # chuteira
    # calção
    d.rounded_rectangle([cx - 92, 650, cx + 92, 745], 22, fill=(255, 255, 255) if club in ("FLA", "INT", "GUA") else (20, 20, 20),
                        outline=BLK, width=OUT)
    # tronco com listras
    body = Image.new("RGBA", S.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle([cx - 115, 470, cx + 115, 680], 48, fill=c["stripes"][0])
    if len(c["stripes"]) > 1:
        for i, y in enumerate(range(470, 680, 34)):
            if i % 2:
                bd.rectangle([cx - 120, y, cx + 120, y + 34], fill=c["stripes"][1])
    mask = Image.new("L", S.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([cx - 115, 470, cx + 115, 680], 48, fill=255)
    S.paste(body, (0, 0), mask)
    d.rounded_rectangle([cx - 115, 470, cx + 115, 680], 48, outline=BLK, width=OUT)
    d.polygon([(cx - 38, 470), (cx, 515), (cx + 38, 470)], fill=(255, 255, 255), outline=BLK)  # gola
    b = shield(95, club)
    S.alpha_composite(b, (cx + 5, 515))
    # braços
    def arm(x0, y0, x1, y1):
        d.line([(x0, y0), (x1, y1)], fill=BLK, width=50)
        d.line([(x0, y0), (x1, y1)], fill=c["stripes"][0], width=34)
        d.ellipse([x1 - 30, y1 - 30, x1 + 30, y1 + 30], fill=sk, outline=BLK, width=OUT)
    if pose == "up":          # erguendo taça
        arm(cx - 100, 510, cx - 75, 55); arm(cx + 100, 510, cx + 75, 55)
    elif pose == "point":     # apontando pra frente (direita do sprite)
        arm(cx - 100, 520, cx - 150, 640); arm(cx + 100, 520, cx + 245, 470)
    elif pose == "cross":     # braços cruzados
        d.rounded_rectangle([cx - 120, 540, cx + 120, 610], 30, fill=c["stripes"][0], outline=BLK, width=OUT)
        d.ellipse([cx - 135, 545, cx - 80, 600], fill=sk, outline=BLK, width=OUT)
        d.ellipse([cx + 80, 545, cx + 135, 600], fill=sk, outline=BLK, width=OUT)
    elif pose == "hold":      # segurando objeto na frente
        arm(cx - 100, 520, cx - 40, 600); arm(cx + 100, 520, cx + 40, 600)
    elif pose == "chin":      # mão no queixo
        arm(cx - 100, 520, cx - 150, 640); arm(cx + 100, 520, cx + 30, 420)
    else:
        arm(cx - 100, 520, cx - 150, 650); arm(cx + 100, 520, cx + 150, 650)
    # cabeça
    hx, hy, R = cx, 290, 185
    d.ellipse([hx - R, hy - R, hx + R, hy + R], fill=sk, outline=BLK, width=OUT)
    d.ellipse([hx - R - 22, hy - 10, hx - R + 22, hy + 50], fill=sk, outline=BLK, width=OUT)  # orelhas
    d.ellipse([hx + R - 22, hy - 10, hx + R + 22, hy + 50], fill=sk, outline=BLK, width=OUT)
    d.chord([hx - R + 2, hy - R + 2, hx + R - 2, hy + R * .4], 180, 360, fill=hair)  # cabelo
    d.arc([hx - R, hy - R, hx + R, hy + R], 180, 360, fill=BLK, width=OUT)
    if club == "SPT":
        for i in range(7):
            x = hx - 150 + i * 50
            d.polygon([(x - 30, hy - R + 70), (x + 10, hy - R - 55), (x + 40, hy - R + 70)], fill=hair, outline=BLK)
    for i in range(6):  # franja
        x = hx - 150 + i * 60
        d.polygon([(x, hy - 60), (x + 60, hy - 60), (x + 30, hy - 5)], fill=hair)
    if pose == "chin":  # mão por cima da cabeça já desenhada
        d.ellipse([cx + 0, 420, cx + 60, 480], fill=sk, outline=BLK, width=OUT)
    # rosto
    ey = hy + 30
    if expr == "angry":
        for s in (-1, 1):
            d.ellipse([hx + s * 70 - 20, ey - 20, hx + s * 70 + 20, ey + 26], fill=BLK)
            d.line([(hx + s * 30, ey - 34), (hx + s * 110, ey - 62)], fill=BLK, width=16)
        d.ellipse([hx - 60, ey + 50, hx + 60, ey + 140], fill=(110, 20, 20), outline=BLK, width=OUT)
        d.ellipse([hx - 30, ey + 100, hx + 30, ey + 135], fill=(230, 90, 90))
        d.rectangle([hx - 40, ey + 56, hx + 40, ey + 72], fill=(255, 255, 255))
    elif expr == "smug":
        for s in (-1, 1):
            d.chord([hx + s * 70 - 26, ey - 18, hx + s * 70 + 26, ey + 22], 0, 180, fill=BLK)
            d.line([(hx + s * 40, ey - 40), (hx + s * 105, ey - 46)], fill=BLK, width=12)
        d.arc([hx - 40, ey + 40, hx + 70, ey + 110], 10, 120, fill=BLK, width=12)
    elif expr == "sad":
        for s in (-1, 1):
            d.ellipse([hx + s * 70 - 18, ey - 18, hx + s * 70 + 18, ey + 22], fill=BLK)
            d.line([(hx + s * 40, ey - 50), (hx + s * 105, ey - 34)], fill=BLK, width=12)
        d.arc([hx - 45, ey + 80, hx + 45, ey + 140], 200, 340, fill=BLK, width=12)
        d.ellipse([hx + 82, ey + 25, hx + 112, ey + 75], fill=(120, 190, 255), outline=BLK, width=4)
    elif expr == "shock":
        for s in (-1, 1):
            d.ellipse([hx + s * 70 - 26, ey - 30, hx + s * 70 + 26, ey + 30], fill=(255, 255, 255), outline=BLK, width=8)
            d.ellipse([hx + s * 70 - 10, ey - 10, hx + s * 70 + 10, ey + 10], fill=BLK)
        d.ellipse([hx - 30, ey + 60, hx + 30, ey + 130], fill=(110, 20, 20), outline=BLK, width=OUT)
    else:  # happy
        for s in (-1, 1):
            d.arc([hx + s * 70 - 26, ey - 22, hx + s * 70 + 26, ey + 22], 200, 340, fill=BLK, width=12)
        d.chord([hx - 70, ey + 30, hx + 70, ey + 140], 0, 180, fill=(110, 20, 20), outline=BLK, width=OUT)
        d.rectangle([hx - 55, ey + 86, hx + 55, ey + 100], fill=(255, 255, 255))
        for s in (-1, 1):
            d.ellipse([hx + s * 120 - 25, ey + 30, hx + s * 120 + 25, ey + 60], fill=(255, 140, 140))
    if prop == "trophy":
        t = trophy(260)
        S.alpha_composite(t, (cx - 130, 120 - 230 + 40)) if False else None
    if flip:
        S = S.transpose(Image.FLIP_LEFT_RIGHT)
        # o escudo vira espelhado; redesenha por cima
        S.alpha_composite(shield(95, club), (620 - (cx + 5) - shield(95, club).width, 515))
    return S

# ------------------------------------------------------------------ objetos
def trophy(size):
    im = Image.new("RGBA", (size, int(size * 1.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w, h = im.size
    gold, dark = (250, 200, 40), (200, 140, 20)
    for s in (-1, 1):
        d.arc([w / 2 + s * w * .32 - w * .18, h * .12, w / 2 + s * w * .32 + w * .18, h * .45], 0, 360, fill=BLK, width=OUT + 12)
        d.arc([w / 2 + s * w * .32 - w * .18, h * .12, w / 2 + s * w * .32 + w * .18, h * .45], 0, 360, fill=gold, width=12)
    d.polygon([(w * .18, h * .08), (w * .82, h * .08), (w * .7, h * .5), (w * .3, h * .5)], fill=gold, outline=BLK, width=OUT)
    d.rectangle([w * .44, h * .5, w * .56, h * .7], fill=dark, outline=BLK, width=OUT)
    d.rounded_rectangle([w * .25, h * .7, w * .75, h * .92], 10, fill=(70, 40, 20), outline=BLK, width=OUT)
    d.ellipse([w * .18, h * .03, w * .82, h * .14], fill=(255, 230, 120), outline=BLK, width=OUT)
    d.line([(w * .32, h * .18), (w * .38, h * .42)], fill=(255, 250, 210), width=10)
    im.info["kind"] = "trophy"
    return im

def paper(size, title="REGULAMENTO", lines=6):
    w, h = size, int(size * 1.3)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, w, h], fill=(250, 248, 238), outline=BLK, width=OUT)
    d.text((w / 2 + 5, 60), title, font=F(ANTON, int(size * .13)), fill=BLK, anchor="mm")
    for i in range(lines):
        d.line([(40, 120 + i * (h - 170) / lines), (w - 40, 120 + i * (h - 170) / lines)], fill=(120, 120, 130), width=8)
    return im.rotate(-8, expand=True, resample=Image.BICUBIC)

def newspaper(w, head):
    h = int(w * .8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=(238, 232, 214), outline=BLK, width=OUT)
    d.text((w / 2, 50), "JORNAL DOS SPORTS  •  1987", font=F(POP, 30), fill=(60, 60, 60), anchor="mm")
    d.line([(20, 80), (w - 20, 80)], fill=BLK, width=5)
    y = 90
    for ln in head.split("\n"):
        d.text((w / 2, y + 70), ln, font=F(ANTON, 120), fill=BLK, anchor="mm")
        y += 130
    for i in range(5):
        d.line([(30, y + 50 + i * 34), (w - 30, y + 50 + i * 34)], fill=(140, 140, 140), width=10)
    return im.rotate(4, expand=True, resample=Image.BICUBIC)

def gavel(size):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = size
    d.line([(s * .3, s * .3), (s * .85, s * .85)], fill=BLK, width=int(s * .1))
    d.line([(s * .3, s * .3), (s * .85, s * .85)], fill=(150, 90, 40), width=int(s * .07))
    head = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    hd = ImageDraw.Draw(head)
    hd.rounded_rectangle([s * .1, s * .2, s * .55, s * .4], 12, fill=(120, 70, 30), outline=BLK, width=OUT)
    head = head.rotate(45, center=(s * .32, s * .3), resample=Image.BICUBIC)
    im.alpha_composite(head)
    im.info["kind"] = "gavel"
    return im

def stamp(text, color=(220, 30, 30), size=110, rot=-12):
    f = F(ANTON, size)
    tw = int(f.getlength(text)) + 80
    im = Image.new("RGBA", (tw, size + 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, tw - 6, size + 64], 18, outline=color, width=14, fill=(255, 255, 255, 230))
    d.text((tw / 2, (size + 70) / 2), text, font=f, fill=color, anchor="mm")
    out = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    out.info["kind"] = "stamp"
    return out

def scoreboard(a, sa, b, sb):
    im = Image.new("RGBA", (860, 240), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 859, 239], 30, fill=(15, 18, 30), outline=YEL, width=10)
    im.alpha_composite(shield(120, a), (40, 45))
    im.alpha_composite(shield(120, b), (700, 45))
    d.text((430, 120), f"{sa}  x  {sb}", font=F(ANTON, 150), fill=(255, 255, 255), anchor="mm")
    return im

def textbox(txt, size=96, fill=(255, 255, 255), stroke=10, font=ANTON):
    f = F(font, size)
    l, t, r, b = f.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (r - l + 40, b - t + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20 - l, 20 - t), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=BLK)
    return im

def title(l1, l2):
    f = F(ANTON, 210)
    im = Image.new("RGBA", (W, 560), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    for layer, off, c1, c2 in ((sh, 14, (0, 0, 0, 200), (0, 0, 0, 200)), (im, 0, (255, 255, 255), YEL)):
        dd = ImageDraw.Draw(layer)
        dd.text((W / 2 + off, 140 + off), l1, font=f, fill=c1, anchor="mm", stroke_width=14, stroke_fill=BLK)
        dd.text((W / 2 + off, 380 + off), l2, font=f, fill=c2, anchor="mm", stroke_width=14, stroke_fill=BLK)
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    sh.alpha_composite(im)
    sk = 0.16  # itálico
    return sh.transform(sh.size, Image.AFFINE, (1, sk, -sk * sh.size[1] / 2, 0, 1, 0), resample=Image.BICUBIC)

def tag(txt, col):
    f = F(ANTON, 64)
    tw = int(f.getlength(txt)) + 60
    im = Image.new("RGBA", (tw, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, tw - 4, 96], 40, fill=col, outline=BLK, width=7)
    d.text((tw / 2, 50), txt, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=BLK)
    return im

def logo():
    im = Image.new("RGBA", (430, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 429, 89], 45, fill=(255, 255, 255, 235), outline=(20, 110, 50), width=6)
    d.ellipse([12, 12, 78, 78], fill=(255, 255, 255), outline=BLK, width=4)
    d.regular_polygon((45, 45, 14), 5, fill=BLK)
    d.text((250, 45), "@futexplicando", font=F(POP, 38), fill=(20, 110, 50), anchor="mm")
    return im

# ------------------------------------------------------------------ cenas
SCENES = [
    dict(id="gancho", bg="stadium", text="O Flamengo ganhou a final, levantou a taça... e a Justiça diz que o campeão é OUTRO. 87 é de quem?"),
    dict(id="contexto", bg="newsroom", text="1987. A CBF tá sem dinheiro pra organizar o Brasileirão. Aí os grandes criam o Clube dos 13 e fazem o próprio campeonato: a Copa União."),
    dict(id="modulos", bg="split", text="A CBF aceita, mas divide tudo em dois módulos. O Verde, com os grandes, e o Amarelo."),
    dict(id="final", bg="stadium", text="No Verde, o Flamengo de Zico, Bebeto e Renato bate o Inter na final."),
    dict(id="recusa", bg="stadium", text="Só que o regulamento mandava fazer um quadrangular com os dois melhores do Amarelo: Sport e Guarani. Flamengo e Inter se recusam a jogar."),
    dict(id="sport", bg="stadium", text="O Sport bate o Guarani por 1 a 0, em fevereiro de 88... e a CBF declara: campeão é o SPORT."),
    dict(id="ladoA", bg="stadium", text="O Flamengo diz: a Copa União era a elite de verdade. Os maiores do país tavam ali, e ele venceu TODOS."),
    dict(id="ladoB", bg="stadium", text="O Sport diz: regra é regra. O cruzamento tava no regulamento, e quem não entra em campo... perde."),
    dict(id="desfecho", bg="court", text="Em 2011, a CBF tentou dividir o título. Em 2017, o STF bateu o martelo: o Sport é o ÚNICO campeão. E em 2026 a Justiça do Rio negou de novo o pedido do Flamengo."),
    dict(id="cta", bg="stadium", text="E aí: 87 é do Fla ou do Sport? Comenta aí. Segue o @futexplicando pra próxima."),
]
WPS = 3.3  # palavras por segundo (ritmo de narração rápida)

class Sp:
    def __init__(s, img, x, y, t0=0.0, pop=True, bob=0, shake=0, slide=None, zoom=0, t_end=None):
        s.img, s.x, s.y, s.t0, s.pop, s.bob, s.shake, s.slide, s.zoom, s.t_end = img, x, y, t0, pop, bob, shake, slide, zoom, t_end

def build(sc, dur):
    """Retorna (bg, [sprites]) para a cena. Coordenadas = centro do sprite."""
    i = sc["id"]
    sp = []
    if sc["bg"] == "stadium":
        bg = bg_stadium(seed=len(i))
    else:
        bg = {"newsroom": bg_newsroom, "split": bg_split, "court": bg_court}[sc["bg"]]()
    if i == "gancho":
        fla = chibi("FLA", "smug", "up", skin=1)
        spt = chibi("SPT", "angry", "point", skin=0, flip=True)
        sp += [Sp(fla, 290, 1330, 0.0, bob=10), Sp(trophy(240), 290, 815, 0.15, bob=10),
               Sp(spt, 790, 1330, 0.25, shake=4), Sp(paper(200), 600, 1210, 0.5, bob=6),
               Sp(tag("FLA", (200, 16, 30)), 290, 1760, 0.3), Sp(tag("SPORT", (20, 20, 20)), 790, 1760, 0.4),
               Sp(title("87 É", "DE QUEM?!"), W / 2, 330, 0.0)]
    elif i == "contexto":
        sp += [Sp(textbox("1987", 260, YEL, 14), W / 2, 260, 0.0),
               Sp(newspaper(860, "CBF SEM\nDINHEIRO!"), W / 2, 760, 0.6, zoom=0.04),
               Sp(chibi("FLA", "shock", "idle", skin=2).resize((372, 552)), 260, 1500, dur * .45, bob=8),
               Sp(chibi("INT", "smug", "cross", skin=3).resize((372, 552)), 820, 1500, dur * .5, bob=8),
               Sp(stamp("CLUBE DOS 13", (20, 110, 50), 100, 8), W / 2, 1190, dur * .55),
               Sp(stamp("COPA UNIÃO", (200, 16, 30), 120, -6), W / 2, 1400, dur * .78)]
    elif i == "modulos":
        sp += [Sp(textbox("2 MÓDULOS", 150, (255, 255, 255), 12), W / 2, 220, 0.0),
               Sp(textbox("VERDE", 130, (255, 255, 255), 12), 290, 520, dur * .45),
               Sp(textbox("AMARELO", 120, (255, 255, 255), 12), 800, 520, dur * .75)]
        for k, cl in enumerate(["FLA", "INT"]):
            sp.append(Sp(shield(170, cl), 210 + k * 190, 900, dur * .5 + k * .15, bob=6))
        for k, cl in enumerate(["SPT", "GUA"]):
            sp.append(Sp(shield(170, cl), 760 + k * 190, 1100, dur * .8 + k * .15, bob=6))
        sp.append(Sp(textbox("+ os grandes", 70, (255, 255, 255), 8, POP), 300, 1180, dur * .55))
    elif i == "final":
        sp += [Sp(textbox("FINAL DA COPA UNIÃO", 110, YEL, 12), W / 2, 230, 0.0),
               Sp(chibi("FLA", "happy", "up", skin=1), 300, 1330, 0.2, bob=14),
               Sp(chibi("INT", "sad", "idle", skin=0, flip=True), 790, 1350, 0.4),
               Sp(stamp("FLA CAMPEÃO!", (200, 16, 30), 100, -8), W / 2, 560, dur * .6)]
    elif i == "recusa":
        sp += [Sp(textbox("QUADRANGULAR", 130, YEL, 12), W / 2, 220, 0.0),
               Sp(paper(300), 260, 600, 0.3, bob=6)]
        for k, cl in enumerate(["FLA", "INT", "SPT", "GUA"]):
            sp.append(Sp(shield(130, cl), 560 + (k % 2) * 220, 560 + (k // 2) * 180, 0.6 + k * .2, bob=5))
        sp += [Sp(chibi("FLA", "smug", "cross", skin=1), 300, 1350, dur * .6, shake=0),
               Sp(chibi("INT", "smug", "cross", skin=0, flip=True), 790, 1350, dur * .68),
               Sp(stamp("NÃO VAMOS!", (220, 30, 30), 110, 10), W / 2, 1000, dur * .75)]
    elif i == "sport":
        sp += [Sp(scoreboard("SPT", 1, "GUA", 0), W / 2, 280, 0.0),
               Sp(textbox("FEV/1988", 90, (255, 255, 255), 10), W / 2, 470, 0.4),
               Sp(chibi("GUA", "sad", "idle", skin=2), 800, 1350, 0.3),
               Sp(chibi("SPT", "happy", "up", skin=0), 300, 1330, dur * .5, bob=14),
               Sp(trophy(240), 300, 815, dur * .55, bob=14),
               Sp(stamp("CAMPEÃO: SPORT", (20, 20, 20), 100, -10), W / 2, 720, dur * .75)]
    elif i == "ladoA":
        sp += [Sp(textbox("LADO DO FLA", 140, YEL, 12), W / 2, 250, 0.0),
               Sp(chibi("FLA", "smug", "chin", skin=1), W / 2, 1300, 0.2, bob=8),
               Sp(stamp("ELITE DE VERDADE", (200, 16, 30), 90, 6), W / 2, 560, dur * .3),
               Sp(stamp("VENCEU TODOS", (20, 20, 20), 100, -6), W / 2, 760, dur * .75)]
    elif i == "ladoB":
        sp += [Sp(textbox("LADO DO SPORT", 140, YEL, 12), W / 2, 250, 0.0),
               Sp(chibi("SPT", "angry", "point", skin=0), 380, 1300, 0.2, shake=3),
               Sp(paper(300), 830, 1080, 0.4, bob=6),
               Sp(stamp("REGRA É REGRA", (20, 20, 20), 100, -6), W / 2, 560, dur * .25),
               Sp(stamp("W.O. = PERDE", (220, 30, 30), 100, 8), W / 2, 780, dur * .8)]
    elif i == "desfecho":
        sp += [Sp(stamp("2011: CBF DIVIDE", (40, 90, 200), 90, -5), W / 2, 560, 0.2),
               Sp(gavel(380), W / 2 + 180, 1200, dur * .3, shake=10, t_end=None),
               Sp(stamp("2017 STF: SÓ O SPORT", (220, 30, 30), 95, 6), W / 2, 780, dur * .35),
               Sp(stamp("2026: NEGADO DE NOVO", (20, 20, 20), 90, -4), W / 2, 1000, dur * .72),
               Sp(chibi("FLA", "sad", "idle", skin=1).resize((434, 644)), 270, 1600, dur * .75)]
    elif i == "cta":
        sp += [Sp(chibi("FLA", "angry", "point", skin=1), 300, 1330, 0.0, shake=3),
               Sp(chibi("SPT", "angry", "point", skin=0, flip=True), 780, 1330, 0.1, shake=3),
               Sp(trophy(200), W / 2, 1080, 0.3, bob=12),
               Sp(title("E AÍ, 87 É", "DE QUEM?!"), W / 2, 340, 0.0),
               Sp(textbox("COMENTA AÍ 👇".replace(" 👇", ""), 110, YEL, 12), W / 2, 700, dur * .35),
               Sp(logo().resize((645, 135)), W / 2, 860, dur * .55)]
    return bg, sp

# ------------------------------------------------------------------ legendas
def chunks(text, n=4):
    w = text.split()
    out, cur = [], []
    for x in w:
        cur.append(x)
        if len(cur) >= n or x.endswith((".", "?", ":", ",")) and len(cur) >= 2:
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out

def caption(txt):
    words = txt.split()
    size = 92
    while True:  # encolhe a fonte se a frase não couber na largura (margem de 50 px de cada lado)
        f = F(ANTON, size)
        tw = sum(f.getlength(x.upper() + " ") for x in words)
        if tw <= W - 100 or size <= 56:
            break
        size -= 4
    im = Image.new("RGBA", (W, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = (W - tw) / 2
    for wd in words:
        key = wd.strip(".,?:!").isupper() or any(ch.isdigit() for ch in wd) or wd.strip(".,?:!").lower() in (
            "flamengo", "sport", "stf", "justiça", "campeão", "verde", "amarelo", "regulamento", "todos", "único", "perde", "cbf")
        d.text((x, 85), wd.upper(), font=f, fill=YEL if key else (255, 255, 255), anchor="lm", stroke_width=10, stroke_fill=BLK)
        x += f.getlength(wd.upper() + " ")
    return im

# ------------------------------------------------------------------ render
def ease_pop(p):
    if p >= 1:
        return 1.0
    return 1 + 0.25 * math.sin(p * math.pi) * (1 - p) * 2 if p > .5 else (p / .5) * 1.15

def main(out="fut87.mp4", timings=None):
    durs = []
    for k, sc in enumerate(SCENES):
        n = len(sc["text"].split())
        durs.append(timings[k] if timings else round(n / WPS + 0.35, 2))
    total = sum(durs)
    json.dump(dict(durations=durs, total=total), open("timings.json", "w"), indent=1)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    lg = logo()
    for k, sc in enumerate(SCENES):
        dur = durs[k]
        bg, sprites = build(sc, dur)
        bg.alpha_composite(lg, (W - 450, H - 110)) if sc["id"] != "cta" else None
        caps = chunks(sc["text"])
        wc = [len(c.split()) for c in caps]
        tot = sum(wc)
        bounds, acc = [], 0
        for c in wc:
            bounds.append(acc / tot * dur); acc += c
        cap_imgs = [caption(c) for c in caps]
        nfr = int(round(dur * FPS))
        for fi in range(nfr):
            t = fi / FPS
            # leve zoom de câmera no fundo
            z = 1 + 0.025 * (t / dur)
            frame = bg.resize((int(W * z), int(H * z)), Image.BILINEAR).crop(
                (int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W, int((H * z - H) / 2) + H)) if fi % 2 == 0 or fi == 0 else frame_bg
            frame_bg = frame
            fr = frame.copy()
            for s in sprites:
                if t < s.t0:
                    continue
                p = (t - s.t0) / 0.35
                sc_ = ease_pop(p) if s.pop else 1
                sc_ *= 1 + s.zoom * (t - s.t0)
                img = s.img
                if abs(sc_ - 1) > 0.01:
                    img = img.resize((max(1, int(img.width * sc_)), max(1, int(img.height * sc_))), Image.BILINEAR)
                dx = s.shake * math.sin(t * 40) if s.shake else 0
                dy = -abs(s.bob * math.sin(t * 6)) if s.bob else 0
                fr.alpha_composite(img, (int(s.x - img.width / 2 + dx), int(s.y - img.height / 2 + dy)))
            ci = max(j for j, b in enumerate(bounds) if t >= b)
            fr.alpha_composite(cap_imgs[ci], (0, 1560))
            # flash de corte no início de cada cena
            if fi < 3 and k > 0:
                fr = Image.blend(fr, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.5 - fi * .16)
            ff.stdin.write(fr.convert("RGB").tobytes())
        print(f"cena {k+1}/{len(SCENES)} {sc['id']} {dur:.1f}s", flush=True)
    ff.stdin.close(); ff.wait()
    print("total", total)

if __name__ == "__main__":
    main(*(sys.argv[1:2] or ["fut87.mp4"]))
