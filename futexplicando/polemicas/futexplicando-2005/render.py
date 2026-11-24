"""@futexplicando — 2005 FOI DO INTER?! — render 9:16.
Mistura o cartoon chibi da série de polêmicas com o estilo de colagem (papel, fotos reais em polaroid,
carimbos de ano) e animação profissional: câmera com paralaxe, molas, carimbos que tremem a tela,
transições whip/crossfade e legenda karaokê sincronizada com a narração."""
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

def bg_court(label="STF"):
    img = Image.new("RGBA", (W, H), (92, 54, 30))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 180):
        d.rectangle([x + 15, 80, x + 165, 1000], fill=(110, 66, 38), outline=(70, 40, 22), width=6)
    d.ellipse([W / 2 - 150, 120, W / 2 + 150, 420], fill=(200, 170, 80), outline=BLK, width=OUT)
    d.text((W / 2, 270), label, font=F(ANTON, 120 if len(label) <= 3 else 96), fill=(90, 60, 20), anchor="mm")
    d.rectangle([60, 1050, W - 60, 1350], fill=(70, 40, 20), outline=BLK, width=OUT)  # bancada
    d.rectangle([0, 1350, W, H], fill=(60, 36, 20))
    return img

# ------------------------------------------------------------------ escudos (placeholder)
CLUBS = {
    "FLA": dict(stripes=[(200, 16, 30), (20, 20, 20)], badge=((200, 16, 30), (20, 20, 20)), txt="CRF"),
    "SPT": dict(stripes=[(210, 20, 30), (20, 20, 20)], badge=((20, 20, 20), (210, 20, 30)), txt="SCR", gold=True),
    "INT": dict(stripes=[(205, 20, 30)], badge=((205, 20, 30), (255, 255, 255)), txt="SCI"),
    "GUA": dict(stripes=[(10, 120, 60)], badge=((10, 120, 60), (255, 255, 255)), txt="GFC"),
    "COR": dict(stripes=[(250, 250, 250)], trim=(18, 18, 18), shorts=(18, 18, 18), sock=(250, 250, 250), txt="SCCP"),
    "ARB": dict(stripes=[(28, 28, 32)], trim=(255, 212, 0), shorts=(28, 28, 32), sock=(28, 28, 32), txt="", nocrest=True),
    "SAN": dict(stripes=[(250, 250, 250)], trim=(18, 18, 18), shorts=(250, 250, 250), txt="SFC"),
    "SAO": dict(stripes=[(250, 250, 250)], trim=(200, 20, 30), shorts=(250, 250, 250), txt="SPFC"),
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

def chibi(club, expr="happy", pose="idle", skin=0, hair=(30, 22, 18), flip=False, prop=None, careca=False):
    """Desenha um personagem chibi num sprite RGBA 600x900. Retorna sprite."""
    S = Image.new("RGBA", (620, 920), (0, 0, 0, 0))
    d = ImageDraw.Draw(S)
    cx = 310
    sk = SKINS[skin]
    c = CLUBS[club]
    # pernas
    for lx in (cx - 55, cx + 15):
        d.rounded_rectangle([lx, 720, lx + 42, 830], 10, fill=sk, outline=BLK, width=OUT)
        d.rounded_rectangle([lx - 4, 770, lx + 46, 830], 8, fill=c.get("sock", c["stripes"][0]), outline=BLK, width=OUT)  # meião
        d.rounded_rectangle([lx - 18, 818, lx + 54, 862], 16, fill=(25, 25, 25), outline=BLK, width=OUT)  # chuteira
    # calção
    shorts = c.get("shorts", (255, 255, 255) if club in ("FLA", "INT", "GUA") else (20, 20, 20))
    d.rounded_rectangle([cx - 92, 650, cx + 92, 745], 22, fill=shorts, outline=BLK, width=OUT)
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
    if "trim" in c:  # detalhes da camisa (faixas laterais)
        for sx in (-1, 1):
            d.line([(cx + sx * 100, 500), (cx + sx * 100, 668)], fill=c["trim"], width=14)
    d.polygon([(cx - 38, 470), (cx, 515), (cx + 38, 470)], fill=c.get("trim", (255, 255, 255)), outline=BLK)  # gola
    if not c.get("nocrest"):
        b = shield(95, club)
        S.alpha_composite(b, (cx + 5, 515))
    # braços
    def arm(x0, y0, x1, y1):
        d.line([(x0, y0), (x1, y1)], fill=BLK, width=50)
        d.line([(x0, y0), (x1, y1)], fill=c["stripes"][0], width=34)
        if "trim" in c:
            mx, my = x0 + (x1 - x0) * .32, y0 + (y1 - y0) * .32
            d.line([(mx, my), (mx + (x1 - x0) * .06, my + (y1 - y0) * .06)], fill=c["trim"], width=34)
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
    if not careca:
        d.chord([hx - R + 2, hy - R + 2, hx + R - 2, hy + R * .4], 180, 360, fill=hair)  # cabelo
    d.arc([hx - R, hy - R, hx + R, hy + R], 180, 360, fill=BLK, width=OUT)
    if club == "SPT":
        for i in range(7):
            x = hx - 150 + i * 50
            d.polygon([(x - 30, hy - R + 70), (x + 10, hy - R - 55), (x + 40, hy - R + 70)], fill=hair, outline=BLK)
    for i in range(0 if careca else 6):  # franja
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
    elif expr == "cry":
        for s in (-1, 1):
            d.arc([hx + s * 70 - 26, ey - 10, hx + s * 70 + 26, ey + 30], 200, 340, fill=BLK, width=12)
            d.line([(hx + s * 40, ey - 50), (hx + s * 105, ey - 34)], fill=BLK, width=12)
            d.rounded_rectangle([hx + s * 70 - 14, ey + 18, hx + s * 70 + 14, ey + 150], 12, fill=(120, 190, 255), outline=BLK, width=4)
        d.chord([hx - 50, ey + 70, hx + 50, ey + 150], 180, 360, fill=(110, 20, 20), outline=BLK, width=OUT)
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
        if not c.get("nocrest"):
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

def newspaper(w, head, ano="1987", foto=None):
    h = int(w * .8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=(238, 232, 214), outline=BLK, width=OUT)
    d.text((w / 2, 50), f"JORNAL DOS SPORTS  •  {ano}", font=F(POP, 30), fill=(60, 60, 60), anchor="mm")
    d.line([(20, 80), (w - 20, 80)], fill=BLK, width=5)
    y = 90
    for ln in head.split("\n"):
        d.text((w / 2, y + 70), ln, font=F(ANTON, 120), fill=BLK, anchor="mm")
        y += 130
    if foto:  # foto real no jornal (meio-tom sépia)
        ph = Image.open(foto).convert("L")
        pw = int(w * .42); ph = ph.resize((pw, int(pw * ph.height / ph.width)), Image.LANCZOS)
        ph = Image.merge("RGB", [ph.point(lambda v: int(v * .95 + 12)), ph.point(lambda v: int(v * .88 + 10)), ph.point(lambda v: int(v * .75 + 8))])
        im.paste(ph, (30, y + 30)); d.rectangle([30, y + 30, 30 + pw, y + 30 + ph.height], outline=BLK, width=4)
        for i in range(5):
            d.line([(60 + pw, y + 50 + i * 34), (w - 30, y + 50 + i * 34)], fill=(140, 140, 140), width=10)
    else:
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

# ------------------------------------------------------------------ estilo colagem (papel, fotos, carimbos)
import numpy as np

def _noise_tex(seed, scale=1):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    n = (np.clip(n * 18 + 128, 0, 255)).astype(np.uint8)
    return Image.fromarray(n, "L").resize((W, H), Image.BILINEAR)

GRAINS = None
def grain_layers():
    """4 texturas de grão (cicladas a cada 2 quadros) + vinheta + leve tom de papel."""
    global GRAINS
    if GRAINS is None:
        g = [_noise_tex(s) for s in range(4)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H * .45) / (H * .62)) ** 2)
        vig = (np.clip((r - .55) / .6, 0, 1) ** 1.6 * 150).astype(np.uint8)
        vign = Image.new("RGBA", (W, H), (20, 10, 0, 0)); vign.putalpha(Image.fromarray(vig, "L"))
        GRAINS = (g, vign)
    return GRAINS

def film(fr, fi):
    """Acabamento: grão de filme, vinheta quente e leve 'papel'."""
    g, vign = grain_layers()
    fr.alpha_composite(vign)
    rgb = fr.convert("RGB")
    noise = g[(fi // 2) % 4]
    rgb = Image.blend(rgb, Image.merge("RGB", (noise, noise, noise)), 0.055)  # grão de filme
    return rgb

def polaroid(path, w, h, legenda=None, credito=None, rot=-4, sepia=0.0):
    """Foto real em polaroid com fita adesiva, legenda manuscrita e crédito."""
    ph = Image.open(path).convert("RGB")
    sc = max(w / ph.width, h / ph.height)
    ph = ph.resize((int(ph.width * sc) + 1, int(ph.height * sc) + 1), Image.LANCZOS)
    ph = ph.crop(((ph.width - w) // 2, (ph.height - h) // 2, (ph.width - w) // 2 + w, (ph.height - h) // 2 + h))
    if sepia:
        g = ph.convert("L")
        sep = Image.merge("RGB", [g.point(lambda v: min(255, int(v * 1.07 + 20))), g.point(lambda v: int(v * .95 + 10)), g.point(lambda v: int(v * .78))])
        ph = Image.blend(ph, sep, sepia)
    pad, bottom = 26, (110 if legenda else 40)
    card = Image.new("RGBA", (w + pad * 2, h + pad + bottom), (252, 250, 243, 255))
    card.paste(ph, (pad, pad))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, card.width - 1, card.height - 1], outline=BLK, width=5)
    if credito:
        d.text((pad + w - 10, pad + h - 10), credito, font=F(POP, 22), fill=(255, 255, 255), anchor="rs", stroke_width=3, stroke_fill=(0, 0, 0))
    if legenda:
        fs = 64
        while F(ANTON, fs).getlength(legenda) > card.width - 40 and fs > 30:
            fs -= 2
        d.text((card.width / 2, pad + h + bottom / 2 + 4), legenda, font=F(ANTON, fs), fill=BLK, anchor="mm")
    # fita adesiva
    tape = Image.new("RGBA", (200, 60), (245, 232, 180, 190))
    card.alpha_composite(tape.rotate(6, expand=True), (card.width // 2 - 110, -18 if False else 0))
    out = Image.new("RGBA", (card.width + 40, card.height + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([28, 28, card.width + 22, card.height + 22], fill=(0, 0, 0, 150))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    out.alpha_composite(card, (10, 10))
    return out.rotate(rot, expand=True, resample=Image.BICUBIC)

def tv(path, w=760, credito=None, tag_txt="AO VIVO"):
    """Foto em TV de tubo (para imagem de baixa resolução de arquivo)."""
    ph = Image.open(path).convert("RGB")
    h = int(w * .62)
    sc = max(w / ph.width, h / ph.height)
    ph = ph.resize((int(ph.width * sc) + 1, int(ph.height * sc) + 1), Image.BICUBIC).crop((0, 0, w, h))
    scan = Image.new("RGB", (w, h), (0, 0, 0)); sd = ImageDraw.Draw(scan)
    for y in range(0, h, 4):
        sd.line([(0, y), (w, y)], fill=(255, 255, 255))
    ph = Image.composite(ph, Image.blend(ph, Image.new("RGB", (w, h), (0, 0, 0)), .35), scan.convert("L"))
    box = Image.new("RGBA", (w + 120, h + 150), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
    d.rounded_rectangle([0, 0, w + 119, h + 119], 46, fill=(110, 72, 40), outline=BLK, width=8)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 40, fill=255)
    box.paste(ph, (60, 60), m)
    d.rounded_rectangle([60, 60, 60 + w, 60 + h], 40, outline=BLK, width=7)
    for x in (w * .25, w * .75):
        d.rectangle([x, h + 118, x + 60, h + 148], fill=(60, 40, 20), outline=BLK, width=5)
    tg = tag(tag_txt, (210, 25, 30)); box.alpha_composite(tg.resize((tg.width * 2 // 3, tg.height * 2 // 3)), (90, 80))
    if credito:
        d.text((40 + w, 40 + h), credito, font=F(POP, 22), fill=(255, 255, 255), anchor="rs", stroke_width=3, stroke_fill=(0, 0, 0))
    return box

def yearstamp(txt, color=(205, 25, 35), size=230, sub=None, rot=-8):
    """Carimbo grunge de ano (borda dupla + textura de tinta falhada)."""
    f = F(ANTON, size)
    tw = int(f.getlength(txt)) + 120
    hh = size + (90 if sub else 60)
    im = Image.new("RGBA", (tw, hh + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, tw - 8, hh + 10], 22, outline=color, width=16)
    d.text((tw / 2, size * .58 + 18), txt, font=f, fill=color, anchor="mm")
    if sub:
        d.text((tw / 2, hh - 20), sub, font=F(ANTON, 52), fill=color, anchor="mm")
    rng = np.random.default_rng(len(txt) * 7)
    m = np.array(im.split()[3]).astype(np.float32)
    holes = rng.random(m.shape) < .09
    m[holes] *= .1
    blot = Image.fromarray(m.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(blot.point(lambda v: 235 if v > 110 else int(v * 2)))
    out = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    out.info["kind"] = "stamp"
    return out

def etiqueta(txt, cor=(18, 18, 18), size=78, txtcor=(255, 255, 255), rot=-2):
    """Faixa de papel rasgado (estilo colagem)."""
    f = F(ANTON, size)
    tw = int(f.getlength(txt)) + 90; th = size + 50
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    pts = []
    for i in range(0, 23):
        pts.append((tw * i / 22, (math.sin(i * 7.3) * .5 + .5) * 9))
    for i in range(22, -1, -1):
        pts.append((tw * i / 22, th - (math.sin(i * 5.1 + 3) * .5 + .5) * 9))
    d = ImageDraw.Draw(im); d.polygon(pts, fill=cor)
    d.text((tw / 2, th / 2), txt, font=f, fill=txtcor, anchor="mm")
    out = Image.new("RGBA", (tw + 24, th + 24), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 130), (14, 14), im.split()[3])
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3))); out.alpha_composite(im)
    return out.rotate(rot, expand=True, resample=Image.BICUBIC)

def redcard(size=220):
    im = Image.new("RGBA", (size, int(size * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, size - 6, int(size * 1.4) - 6], 18, fill=(225, 25, 30), outline=BLK, width=OUT)
    d.line([(30, 40), (60, 120)], fill=(255, 150, 150), width=10)
    im.info["kind"] = "card"
    return im

def whistle(size=160):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([20, 50, 110, 140], fill=(200, 200, 210), outline=BLK, width=7)
    d.rounded_rectangle([80, 60, 150, 100], 10, fill=(200, 200, 210), outline=BLK, width=7)
    im.info["kind"] = "whistle"
    return im

def pointsboard(a, pa, b, pb):
    im = Image.new("RGBA", (920, 330), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 919, 329], 34, fill=(15, 18, 30), outline=YEL, width=10)
    d.text((460, 46), "PONTOS FINAIS · 2005", font=F(ANTON, 52), fill=YEL, anchor="mm")
    im.alpha_composite(shield(150, a), (40, 100)); im.alpha_composite(shield(150, b), (735, 100))
    d.text((460, 205), f"{pa}  x  {pb}", font=F(ANTON, 170), fill=(255, 255, 255), anchor="mm")
    return im

def question(size=420):
    im = textbox("?", size, YEL, 18)
    im.info["kind"] = "stamp"
    return im

def cbf_plate():
    im = Image.new("RGBA", (520, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 519, 149], 20, fill=(240, 200, 60), outline=BLK, width=8)
    d.text((260, 75), "CBF · RIO", font=F(ANTON, 90), fill=BLK, anchor="mm")
    return im

# ------------------------------------------------------------------ cenas
TITLE = ("2005 FOI", "DO INTER?!")
SCENES = [
    dict(id="gancho", bg="stadium", cam=(1.03, 1.0, 0, 20), text="O próprio juiz confessou: ele mudou o campeão brasileiro. 2005 foi do Inter?"),
    dict(id="contexto", bg="newsroom", cam=(1.0, 1.08, -20, 0), text="2005. Estoura a Máfia do Apito: o árbitro Edílson Pereira de Carvalho manipulava jogos pra apostadores."),
    dict(id="decisao", bg="court", label="STJD", cam=(1.08, 1.0, 0, -20), text="O STJD anula os 11 jogos que ele apitou e manda jogar tudo de novo."),
    dict(id="virada", bg="stadium", cam=(1.0, 1.07, 20, 0), text="Nos jogos refeitos, o Corinthians soma quatro pontos: vence o Santos e empata com o São Paulo."),
    dict(id="lance", bg="stadium", cam=(1.0, 1.12, 0, 40), text="E no confronto direto, o Tinga cai na área, o juiz não dá pênalti e ainda expulsa o Tinga."),
    dict(id="resultado", bg="stadium", cam=(1.08, 1.0, -20, 0), text="No fim, Corinthians campeão, três pontos na frente do Inter."),
    dict(id="ladoA", bg="stadium", cam=(1.0, 1.06, 0, -30), text="O Inter diz: sem a máfia, o campeão era ele. O próprio Edílson admitiu isso em documentário, e até o ex-presidente corintiano Alberto Dualib aparece num áudio dizendo o mesmo."),
    dict(id="ladoB", bg="stadium", cam=(1.0, 1.06, 0, 30), text="O Corinthians diz: os jogos foram refeitos e ele ganhou dentro de campo. E especialista em direito desportivo lembra: título não se divide."),
    dict(id="desfecho", bg="court", label="CBF", cam=(1.1, 1.0, 0, 0), text="Em maio de 2026 o Inter pediu à CBF pra dividir o título, sem tirar a taça do Corinthians. E até agora... nada de decisão."),
    dict(id="cta", bg="stadium", cam=(1.0, 1.03, 0, 0), text="E aí: 2005 é do Corinthians ou do Inter? Comenta aí. Segue o @futexplicando pra próxima."),
]
WPS = 3.3
PAD_ANTES = 0.15  # mesmo respiro usado no finalizar.py

# ------------------------------------------------------------------ sincronia palavra a palavra
import unicodedata, difflib
def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(ch for ch in w if ch.isalnum())

_ASR = None
def word_times(k, dur):
    """Tempo (s, dentro da cena) de cada palavra do texto da cena, alinhado ao Whisper da narração."""
    global _ASR
    words = SCENES[k]["text"].split()
    if _ASR is None:
        try:
            _ASR = json.load(open("narracao/palavras_asr.json"))
        except Exception:
            _ASR = []
    if k >= len(_ASR) or not _ASR[k]:
        return [i / len(words) * dur for i in range(len(words))]
    asr = _ASR[k]
    a = [_norm(w) for w in words]; b = [_norm(q["w"]) for q in asr]
    t = [None] * len(words)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for j in range(blk.size):
            t[blk.a + j] = asr[blk.b + j]["s"] + PAD_ANTES
    t[0] = PAD_ANTES if t[0] is None else t[0]
    last = asr[-1]["s"] + PAD_ANTES + .3
    for i in range(len(t)):  # interpola os que não casaram
        if t[i] is None:
            j = next((x for x in range(i + 1, len(t)) if t[x] is not None), None)
            nxt = t[j] if j is not None else last
            t[i] = t[i - 1] + (nxt - t[i - 1]) / ((j if j is not None else len(t)) - i + 1)
    return t

def when(sc_words, times, key, default):
    """Tempo da primeira palavra que contém `key`."""
    k = _norm(key)
    for w, t in zip(sc_words, times):
        if k in _norm(w):
            return t
    return default

# ------------------------------------------------------------------ animação
def ease_out_back(p, s=1.7):
    p = min(1, max(0, p)) - 1
    return p * p * ((s + 1) * p + s) + 1
def ease_in_out(p):
    p = min(1, max(0, p)); return p * p * (3 - 2 * p)
def spring(t, f=2.6, z=0.38):
    """Mola amortecida: 0 → 1 com overshoot."""
    if t <= 0: return 0.0
    w = 2 * math.pi * f
    return 1 - math.exp(-z * w * t) * math.cos(w * math.sqrt(1 - z * z) * t)

class Sp:
    """Sprite animado. anim: pop | slide | slam | drop | fade | fly | none."""
    def __init__(s, img, x, y, t0=0.0, anim="pop", bob=0, shake=0, frm=(0, 0), zoom=0, breathe=False, rot=0, fly_to=None, shadow=False, t_out=None, layer=1):
        s.img, s.x, s.y, s.t0, s.anim, s.bob, s.shake, s.frm, s.zoom = img, x, y, t0, anim, bob, shake, frm, zoom
        s.breathe, s.rot, s.fly_to, s.shadow, s.t_out, s.layer = breathe, rot, fly_to, shadow, t_out, layer
        s._cache = {}

    def state(s, t):
        """(dx, dy, escala, rotação, alpha) no tempo t."""
        u = t - s.t0
        if u < 0: return None
        dx = dy = r = 0.0; k = 1.0; a = 1.0
        if s.anim == "pop":
            k = spring(u, 2.4, .42)
        elif s.anim == "slide":
            p = ease_out_back(u / .45, 1.4); dx = s.frm[0] * (1 - p); dy = s.frm[1] * (1 - p)
        elif s.anim == "slam":
            p = min(1, u / .16); k = 2.3 - 1.3 * (p * p) if p < 1 else 1 + .06 * math.exp(-(u - .16) * 14) * math.cos((u - .16) * 50)
            a = min(1, u / .06)
        elif s.anim == "drop":
            p = min(1, u / .5); dy = -900 * (1 - ease_out_back(p, 1.2))
        elif s.anim == "fade":
            a = min(1, u / .35)
        elif s.anim == "fly" and s.fly_to:
            p = ease_in_out(u / .7); dx = (s.fly_to[0] - s.x) * p; dy = (s.fly_to[1] - s.y) * p - 260 * math.sin(math.pi * min(1, p)); r = 540 * p
            k = .5 + .5 * min(1, p * 1.4)
        if s.zoom: k *= 1 + s.zoom * u
        if s.breathe: k *= 1 + .012 * math.sin(t * 3.1 + s.x)
        if s.bob: dy -= abs(s.bob * math.sin(t * 5.5 + s.x * .01))
        if s.shake: dx += s.shake * math.sin(t * 38) * max(.3, math.exp(-u * 1.5))
        r += s.rot * math.sin(t * 2.2 + s.y) if s.rot else 0
        if s.t_out is not None and t > s.t_out:
            a *= max(0, 1 - (t - s.t_out) / .25)
        return dx, dy, k, r, a

    def render(s, fr, t):
        st = s.state(t)
        if st is None: return
        dx, dy, k, r, a = st
        if a <= 0.01: return
        key = (round(k, 2), round(r, 1))
        img = s._cache.get(key)
        if img is None:
            img = s.img
            if abs(k - 1) > .005:
                img = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.BILINEAR)
            if abs(r) > .3:
                img = img.rotate(r, expand=True, resample=Image.BILINEAR)
            if len(s._cache) < 90: s._cache[key] = img
        if s.shadow:
            sw = int(s.img.width * .55); shd = Image.new("RGBA", (sw, 50), (0, 0, 0, 0))
            ImageDraw.Draw(shd).ellipse([0, 0, sw - 1, 49], fill=(0, 0, 0, 90))
            fr.alpha_composite(shd, (int(s.x + dx - sw / 2), int(s.y + s.img.height * .46)))
        if a < .99:
            img = img.copy(); img.putalpha(img.split()[3].point(lambda v: int(v * a)))
        fr.alpha_composite(img, (int(s.x + dx - img.width / 2), int(s.y + dy - img.height / 2)))

def impulses(sprites):
    """Momentos em que carimbos batem (geram tremor de câmera)."""
    return [s.t0 + .16 for s in sprites if s.anim == "slam"]

def camshake(t, imps):
    x = y = 0.0
    for t0 in imps:
        u = t - t0
        if 0 <= u < .45:
            e = math.exp(-u * 9) * 22
            x += e * math.sin(u * 95); y += e * math.cos(u * 77)
    return x, y

# ------------------------------------------------------------------ montagem das cenas
CH_S = (0.62)  # escala padrão dos chibis em cena média
def ch(img, s=1.0):
    return img if s == 1 else img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)

def build(sc, dur, times=None):
    """Retorna (bg, [sprites]) para a cena. Coordenadas = centro do sprite."""
    i = sc["id"]
    words = sc["text"].split()
    times = times or [j / len(words) * dur for j in range(len(words))]
    T = lambda key, d: when(words, times, key, d)
    sp = []
    if sc["bg"] == "stadium":
        bg = bg_stadium(seed=len(i))
    elif sc["bg"] == "court":
        bg = bg_court(sc.get("label", "STF"))
    else:
        bg = bg_newsroom()
    if i == "gancho":
        sp += [Sp(title(*TITLE), W / 2, 330, 0.0, "slam"),
               Sp(chibi("COR", "smug", "up", skin=0), 760, 1330, 0.1, "slide", frm=(500, 0), bob=8, breathe=True, shadow=True),
               Sp(trophy(240), 760, 815, 0.35, "drop", bob=8),
               Sp(chibi("INT", "cry", "idle", skin=2, flip=True), 300, 1350, 0.25, "slide", frm=(-500, 0), breathe=True, shadow=True),
               Sp(tag("INTER", (205, 20, 30)), 300, 1765, 0.4), Sp(tag("CORINTHIANS", (20, 20, 20)), 760, 1765, 0.5),
               Sp(stamp("O JUIZ CONFESSOU", (220, 30, 30), 84, 7), W / 2, 650, T("confessou", 1.3), "slam"),
               Sp(etiqueta("MUDOU O CAMPEÃO?", (18, 18, 18), 58), 320, 850, T("mudou", 2.6), "slide", frm=(-600, 0))]
    elif i == "contexto":
        sp += [Sp(yearstamp("2005", sub="BRASILEIRÃO"), W / 2, 230, 0.05, "slam"),
               Sp(newspaper(840, "MÁFIA DO\nAPITO!", "2005"), W / 2, 790, T("Máfia", 1.2), "slide", frm=(0, 1200), zoom=.02),
               Sp(tv("fotos/edilson-2005.jpg", 640, "Reprodução/SporTV", "ÁRBITRO"), 330, 1390, T("Edílson", 3.4), "pop", rot=1.2),
               Sp(chibi("ARB", "smug", "point", skin=0, hair=(60, 40, 25)).resize((400, 594)), 840, 1480, T("manipulava", 5.2), "slide", frm=(400, 0), breathe=True),
               Sp(etiqueta("JOGOS PRA APOSTADORES", (205, 25, 35), 62, rot=3), W / 2, 1100, T("apostadores", 7.0), "slam")]
    elif i == "decisao":
        sp += [Sp(chibi("ARB", "sad", "idle", skin=0, hair=(60, 40, 25)).resize((360, 534)), 220, 1500, 0.1, "slide", frm=(-300, 0), breathe=True),
               Sp(gavel(380), W / 2 + 200, 1180, T("anula", .6), "drop", shake=6),
               Sp(stamp("11 JOGOS ANULADOS", (220, 30, 30), 96, -6), W / 2, 640, T("11", 1.2), "slam"),
               Sp(etiqueta("JOGAR TUDO DE NOVO", (18, 18, 18), 72, rot=2), W / 2, 880, T("jogar", 3.4), "slide", frm=(700, 0))]
    elif i == "virada":
        sp += [Sp(textbox("JOGOS REFEITOS", 120, YEL, 12), W / 2, 220, 0.0, "pop"),
               Sp(scoreboard("COR", 3, "SAN", 2), W / 2, 470, T("Santos", 2.6), "slide", frm=(-1100, 0)),
               Sp(scoreboard("COR", 1, "SAO", 1), W / 2, 760, T("empata", 3.6), "slide", frm=(1100, 0)),
               Sp(chibi("COR", "happy", "up", skin=0), W / 2, 1360, T("soma", 1.4), "pop", bob=14, breathe=True, shadow=True),
               Sp(stamp("+4 PONTOS", (20, 130, 60), 110, -8), 690, 1000, T("quatro", 1.8), "slam")]
    elif i == "lance":
        tq = T("cai", 1.6); tp = T("pênalti", 3.2); te = T("expulsa", 4.4)
        sp += [Sp(polaroid("fotos/pacaembu.jpg", 600, 340, "PACAEMBU · 20/11/2005", "Reprodução/Metrópoles", rot=-4, sepia=.35), W / 2, 300, 0.05, "slide", frm=(-900, 0)),
               Sp(textbox("CONFRONTO DIRETO", 92, YEL, 10), W / 2, 590, 0.3, "pop"),
               Sp(chibi("COR", "smug", "cross", skin=0), 800, 1340, 0.4, "slide", frm=(500, 0), breathe=True, shadow=True),
               Sp(chibi("INT", "shock", "idle", skin=2, careca=True, flip=True), 300, 1360, tq, "drop", shake=4, shadow=True),
               Sp(etiqueta("PÊNALTI? NÃO DEU", (18, 18, 18), 70), W / 2, 760, tp, "slam"),
               Sp(chibi("ARB", "angry", "point", skin=0, hair=(60, 40, 25), flip=True).resize((380, 564)), 560, 1500, tp - .2, "slide", frm=(0, 600)),
               Sp(redcard(170), 640, 1250, te - .1, "fly", fly_to=(170, 880)),
               Sp(stamp("EXPULSO!", (220, 30, 30), 110, 8), 600, 925, te + .5, "slam")]
    elif i == "resultado":
        sp += [Sp(pointsboard("COR", 81, "INT", 78), W / 2, 300, 0.05, "slide", frm=(0, -700)),
               Sp(polaroid("fotos/tevez-2005.jpg", 500, 316, "TEVEZ · 2005", "Reprodução/Lance!", rot=4), 760, 790, T("campeão", 1.0), "slide", frm=(700, 0)),
               Sp(chibi("COR", "happy", "up", skin=0), 320, 1340, T("Corinthians", .7), "pop", bob=14, breathe=True, shadow=True),
               Sp(trophy(240), 320, 825, T("campeão", 1.0) + .1, "drop", bob=14),
               Sp(chibi("INT", "sad", "idle", skin=2, flip=True).resize((434, 644)), 800, 1500, T("três", 2.0), "slide", frm=(500, 0), breathe=True),
               Sp(etiqueta("3 PONTOS DE DIFERENÇA", (205, 25, 35), 60, rot=-3), W / 2, 530, T("três", 2.0), "slam")]
    elif i == "ladoA":
        sp += [Sp(textbox("LADO DO INTER", 140, YEL, 12), W / 2, 230, 0.0, "slam"),
               Sp(chibi("INT", "angry", "point", skin=2, careca=True), 250, 1360, 0.15, "slide", frm=(-500, 0), breathe=True, shadow=True),
               Sp(stamp("SEM A MÁFIA, ERA O INTER", (205, 20, 30), 70, 5), W / 2, 470, T("máfia", 1.0), "slam"),
               Sp(polaroid("fotos/edilson-documentario.jpg", 520, 325, "EDÍLSON · DOCUMENTÁRIO", "Reprodução/SporTV", rot=-4), 730, 830, T("Edílson", 3.6), "slide", frm=(700, 0)),
               Sp(stamp("O JUIZ CONFESSOU", (20, 20, 20), 76, -6), 720, 1160, T("admitiu", 4.2), "slam"),
               Sp(stamp("ÁUDIO DO DUALIB", (205, 20, 30), 76, 6), 720, 1360, T("Dualib", 7.6), "slam")]
    elif i == "ladoB":
        sp += [Sp(textbox("LADO DO CORINTHIANS", 118, YEL, 12), W / 2, 230, 0.0, "slam"),
               Sp(chibi("COR", "smug", "point", skin=0), 360, 1340, 0.15, "slide", frm=(-500, 0), shake=2, breathe=True, shadow=True),
               Sp(trophy(200), 830, 1180, 0.4, "pop", bob=8),
               Sp(stamp("GANHOU EM CAMPO", (20, 20, 20), 96, -6), W / 2, 520, T("ganhou", 2.6), "slam"),
               Sp(etiqueta("JOGOS REFEITOS = JOGO LIMPO", (18, 18, 18), 58, rot=2), W / 2, 700, T("refeitos", 1.6), "slide", frm=(-900, 0)),
               Sp(stamp("TÍTULO É ÚNICO", (205, 20, 30), 100, 7), W / 2, 880, T("título", 6.4), "slam")]
    elif i == "desfecho":
        sp += [Sp(cbf_plate(), W / 2, 560, 0.05, "drop"),
               Sp(yearstamp("26/05/2026", (40, 90, 200), 120, rot=-5), W / 2, 760, T("maio", .4), "slam"),
               Sp(paper(260, "PEDIDO"), 280, 1190, T("pediu", 1.6), "slide", frm=(-600, 0), bob=6),
               Sp(stamp("PEDIDO NA CBF", (205, 20, 30), 96, 6), W / 2, 980, T("CBF", 2.0), "slam"),
               Sp(etiqueta("SEM TIRAR A TAÇA DO CORINTHIANS", (18, 18, 18), 54, rot=-2), W / 2, 1140, T("tirar", 4.4), "slide", frm=(900, 0)),
               Sp(chibi("INT", "shock", "chin", skin=2, careca=True).resize((434, 644)), 790, 1560, T("agora", 6.8), "slide", frm=(400, 0), breathe=True),
               Sp(question(380), W / 2, 1360, T("decisão", 8.2), "slam")]
    elif i == "cta":
        sp += [Sp(title("E AÍ, 2005 É", "DE QUEM?!"), W / 2, 330, 0.0, "slam"),
               Sp(chibi("INT", "angry", "point", skin=2, careca=True), 300, 1330, 0.05, "slide", frm=(-500, 0), shake=3, shadow=True),
               Sp(chibi("COR", "angry", "point", skin=0, flip=True), 780, 1330, 0.1, "slide", frm=(500, 0), shake=3, shadow=True),
               Sp(trophy(200), W / 2, 1080, 0.3, "drop", bob=12),
               Sp(textbox("E AÍ? COMENTA", 110, YEL, 12), W / 2, 700, T("Comenta", 3.2), "slam"),
               Sp(logo().resize((645, 135)), W / 2, 860, T("Segue", 4.4), "pop")]
    return bg, sp

# ------------------------------------------------------------------ legenda karaokê
def chunks(text, n=4):
    w = text.split()
    out, cur = [], []
    for x in w:
        cur.append(x)
        if len(cur) >= n or x.endswith((".", "?", ":", ",")) and len(cur) >= 2:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out

KEYS = ("inter", "corinthians", "stjd", "cbf", "máfia", "apito", "edílson", "tinga", "dualib", "campeão", "pênalti", "anula", "expulsa", "título")
def caption_img(words, active, pop=1.0):
    """Linha de legenda: palavra falada em amarelo e um pouco maior; números e nomes destacados."""
    size = 90
    while True:
        f = F(ANTON, size)
        tw = sum(f.getlength(x.upper() + " ") for x in words)
        if tw <= W - 110 or size <= 56: break
        size -= 4
    im = Image.new("RGBA", (W, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = (W - tw) / 2
    for j, wd in enumerate(words):
        clean = wd.strip(".,?:!")
        hot = j == active
        key = clean.isupper() or any(ch.isdigit() for ch in clean) or clean.lower() in KEYS
        col = YEL if hot else ((255, 236, 150) if key else (255, 255, 255))
        if hot and pop != 1.0:
            fb = F(ANTON, int(size * pop))
            d.text((x + f.getlength(wd.upper()) / 2, 95), wd.upper(), font=fb, fill=col, anchor="mm", stroke_width=11, stroke_fill=BLK)
        else:
            d.text((x, 95), wd.upper(), font=f, fill=col, anchor="lm", stroke_width=10, stroke_fill=BLK)
        x += f.getlength(wd.upper() + " ")
    return im

_BAND = None
def caption_band():
    global _BAND
    if _BAND is None:
        a = np.zeros((420, W), np.uint8)
        for y in range(420):
            a[y, :] = int(150 * (y / 420) ** 1.5)
        _BAND = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); _BAND.putalpha(Image.fromarray(a, "L"))
    return _BAND

# ------------------------------------------------------------------ render
TRANS = 9  # quadros de transição entre cenas

def compose(bg, sprites, t, dur, cam, imps):
    """Quadro da cena no tempo t: fundo com paralaxe + sprites, câmera com zoom/pan e tremor."""
    z0, z1, px, py = cam
    p = ease_in_out(t / dur)
    z = z0 + (z1 - z0) * p
    sx, sy = camshake(t, imps)
    ox, oy = px * (p - .5) * 2 + sx, py * (p - .5) * 2 + sy
    # fundo: paralaxe (move 60% da câmera)
    zb = 1 + (z - 1) * .6
    fr = bg.transform((W, H), Image.AFFINE, (1 / zb, 0, (W - W / zb) / 2 - ox * .6 / zb, 0, 1 / zb, (H - H / zb) / 2 - oy * .6 / zb), Image.BILINEAR)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for s in sorted(sprites, key=lambda q: q.layer):
        s.render(lay, t)
    lay = lay.transform((W, H), Image.AFFINE, (1 / z, 0, (W - W / z) / 2 - ox / z, 0, 1 / z, (H - H / z) / 2 - oy / z), Image.BILINEAR)
    fr.alpha_composite(lay)
    return fr

def main(out="fut2005.mp4", timings=None):
    durs = []
    for k, sc in enumerate(SCENES):
        n = len(sc["text"].split())
        durs.append(timings[k] if timings else round(n / WPS + 0.35, 2))
    total = sum(durs)
    json.dump(dict(durations=durs, total=total), open("timings.json", "w"), indent=1)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    lg = logo()
    band = caption_band()
    prev_last = None
    fi_global = 0
    for k, sc in enumerate(SCENES):
        dur = durs[k]
        times = word_times(k, dur)
        bg, sprites = build(sc, dur, times)
        if sc["id"] != "cta":
            bg.alpha_composite(lg, (W - 450, H - 110))
        imps = impulses(sprites)
        words = sc["text"].split()
        groups = chunks(sc["text"])
        gidx, acc = [], 0
        for g in groups:
            gidx.append(list(range(acc, acc + len(g)))); acc += len(g)
        nfr = int(round(dur * FPS))
        whip = k % 2 == 1
        for fi in range(nfr):
            t = fi / FPS
            fr = compose(bg, sprites, t, dur, sc["cam"], imps)
            # legenda karaokê
            wi = max([j for j, tt in enumerate(times) if t >= tt - .02] or [0])
            g = next(n for n, ids in enumerate(gidx) if wi in ids)
            fr.alpha_composite(band, (0, H - 420))
            pop = 1 + .14 * max(0, 1 - (t - times[wi]) / .18)
            fr.alpha_composite(caption_img(groups[g], wi - gidx[g][0], pop), (0, 1530))
            # transição de entrada
            if prev_last is not None and fi < TRANS:
                p = ease_in_out((fi + 1) / (TRANS + 1))
                if whip:  # whip pan: cena anterior sai pra esquerda, nova entra da direita, com borrão
                    off = int(W * p)
                    canvas = Image.new("RGBA", (W, H))
                    canvas.alpha_composite(prev_last, (-off, 0)); canvas.alpha_composite(fr, (W - off, 0))
                    fr = canvas.filter(ImageFilter.BoxBlur(int(14 * math.sin(math.pi * p)) + 0)) if fi < TRANS - 1 else canvas
                else:
                    fr = Image.blend(prev_last, fr, p)
            out_rgb = film(fr, fi_global)
            ff.stdin.write(out_rgb.tobytes())
            if fi == nfr - 1:
                prev_last = fr
            fi_global += 1
        print(f"cena {k+1}/{len(SCENES)} {sc['id']} {dur:.1f}s", flush=True)
    ff.stdin.close(); ff.wait()
    print("total", total)

if __name__ == "__main__":
    main(*(sys.argv[1:2] or ["fut2005.mp4"]))
