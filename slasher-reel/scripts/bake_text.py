"""Gera texturas de texto e gráficos (PNG) com as fontes exatas, para planos no mundo 3D."""
import os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "public")
F = os.path.join(PUB, "fonts")
OUT = os.path.join(PUB, "txt")
os.makedirs(OUT, exist_ok=True)
YEL = (0xF2, 0xE6, 0x3A)
RED = (0xF2, 0x3B, 0x3B)
WHT = (0xED, 0xED, 0xED)
CHAR = (0x1C, 0x1C, 0x1C)
BLK = (14, 14, 14)
FONTS = {
    "anton": os.path.join(F, "Anton.ttf"),
    "play": os.path.join(F, "PlayfairItalic900.ttf"),
    "play7": os.path.join(F, "PlayfairItalic700.ttf"),
    "elite": os.path.join(F, "SpecialElite.ttf"),
    "inter": os.path.join(F, "InterBold.ttf"),
}
rng = np.random.default_rng(3)
man = {}


def text_img(text, font="anton", size=200, color=WHT, squeeze=1.0, pad=None, tracking=0, upper=False):
    if upper:
        text = text.upper()
    fnt = ImageFont.truetype(FONTS[font], size)
    pad = pad if pad is not None else int(size * 0.18)
    # mede
    tmp = Image.new("L", (10, 10))
    d = ImageDraw.Draw(tmp)
    if tracking:
        widths = [d.textlength(c, font=fnt) + tracking for c in text]
        w = int(sum(widths))
    else:
        w = int(d.textlength(text, font=fnt))
    asc, desc = fnt.getmetrics()
    h = asc + desc
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for c, cw in zip(text, widths):
            d.text((x, pad), c, font=fnt, fill=color + (255,))
            x += cw
    else:
        d.text((pad, pad), text, font=fnt, fill=color + (255,))
    bb = im.getchannel("A").getbbox()
    im = im.crop((max(0, bb[0] - pad // 2), max(0, bb[1] - pad // 2), min(im.width, bb[2] + pad // 2), min(im.height, bb[3] + pad // 2)))
    if squeeze != 1.0:
        im = im.resize((int(im.width * squeeze), im.height), Image.LANCZOS)
    return im


def save(name, im):
    im.save(os.path.join(OUT, name + ".png"), optimize=True)
    man[name] = {"w": im.width, "h": im.height}


# ---------- palavras/blocos (id, texto, fonte, cor, tamanho, squeeze)
WORDS = [
    # gancho
    ("h_tres", "TRÊS", "anton", YEL, 300, 1),
    ("h_assassinos", "ASSASSINOS", "anton", WHT, 200, 1),
    ("h_mascarados", "MASCARADOS", "anton", WHT, 200, 1),
    ("h_quece", "que cê", "inter", WHT, 70, 1),
    ("h_nunca", "NUNCA VIU", "anton", YEL, 230, 1),
    ("h_eoultimo", "e o último é o mais", "inter", WHT, 64, 1),
    ("h_filho", "FILHO DA MÃE", "anton", RED, 230, 1),
    # filme 3
    ("f3_title_a", "O Palhaço", "play", WHT, 190, 0.8),
    ("f3_title_b", "no Milharal", "play", WHT, 150, 0.8),
    ("f3_virou", "virou", "inter", WHT, 64, 1),
    ("f3_cacador", "CAÇADOR", "anton", YEL, 260, 1),
    ("f3_deadol", "de adolescente", "inter", WHT, 64, 1),
    ("f3_custou", "custou só", "inter", WHT, 64, 1),
    ("f3_milhao", "1 MILHÃO", "anton", YEL, 260, 1),
    ("f3_dolares", "de dólares", "inter", WHT, 64, 1),
    ("tana", "tá na", "inter", WHT, 70, 1),
    ("tano", "tá no", "inter", WHT, 70, 1),
    # ponte
    ("b_insano", "ESSE É INSANO", "anton", WHT, 190, 1),
    ("b_proximo", "mas o próximo…", "inter", YEL, 70, 1),
    # filme 2
    ("f2_title_a", "O Massacre", "play", WHT, 180, 0.8),
    ("f2_title_b", "da Festa do Pijama", "play", WHT, 130, 0.8),
    ("f2_chega", "chega de", "inter", WHT, 64, 1),
    ("f2_furadeira", "FURADEIRA", "anton", YEL, 250, 1),
    ("f2_meninas", "mas essas meninas", "inter", WHT, 64, 1),
    ("f2_viram", "VIRAM O", "anton", WHT, 190, 1),
    ("f2_jogo", "JOGO", "anton", RED, 300, 1),
    # envio
    ("s_manda", "MANDA PRO AMIGO", "anton", WHT, 170, 1),
    ("s_jura", "que jura que já viu todo", "inter", WHT, 64, 1),
    ("s_slasher", "SLASHER", "anton", YEL, 300, 1),
    # filme 1
    ("f1_title_a", "Presos", "play", WHT, 220, 0.8),
    ("f1_title_b", "no Gelo", "play", WHT, 180, 0.8),
    ("f1_hotel", "HOTEL ABANDONADO", "anton", WHT, 170, 1),
    ("f1_neve", "na neve", "inter", WHT, 64, 1),
    ("f1_oculos", "óculos de esqui e uma", "inter", WHT, 64, 1),
    ("f1_picareta", "PICARETA", "anton", YEL, 270, 1),
    ("f1_noruega", "NORUEGA", "anton", WHT, 150, 1),
    # fecho
    ("c_qual", "QUAL desses assassinos", "anton", WHT, 120, 1),
    ("c_ce", "cê", "inter", WHT, 70, 1),
    ("c_nao", "NÃO", "anton", RED, 330, 1),
    ("c_queria", "queria encontrar?", "inter", WHT, 70, 1),
    ("c_segue", "segue a", "inter", WHT, 70, 1),
    ("c_talking", "TALKING", "anton", YEL, 230, 1),
    ("c_horror", "HORROR", "anton", WHT, 230, 1),
    # ganchos alternativos
    ("hb_slasher", "SLASHER?", "anton", YEL, 280, 1),
    ("hb_ceacha", "cê acha que", "inter", WHT, 70, 1),
    ("hb_javiu", "JÁ VIU TODO", "anton", WHT, 220, 1),
    ("hb_duvido", "DUVIDO.", "anton", RED, 280, 1),
    ("hc_cansou", "CANSOU", "anton", WHT, 280, 1),
    ("hc_de", "de", "inter", WHT, 70, 1),
    ("hc_halloween", "HALLOWEEN", "anton", WHT, 220, 1),
    ("hc_panico", "E PÂNICO?", "anton", YEL, 240, 1),
    ("hc_olha", "OLHA ESSES AQUI", "anton", RED, 190, 1),
    # capa
    ("cv_slashers", "SLASHERS", "anton", YEL, 300, 1),
    ("cv_quece", "QUE CÊ", "anton", WHT, 300, 1),
    ("cv_nunca", "NUNCA VIU", "anton", WHT, 300, 1),
]
for n, t, f, c, s, sq in WORDS:
    save(n, text_img(t, f, s, c, sq))


# ---------- placas de evidência numeradas (tenda amarela de perícia)
def placard(num):
    W, H = 520, 600
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # tenda: trapézio com dobra
    d.polygon([(60, 40), (W - 60, 40), (W - 10, H - 20), (10, H - 20)], fill=YEL + (255,))
    d.polygon([(60, 40), (W - 60, 40), (W - 50, 70), (70, 70)], fill=(200, 190, 40, 255))
    d.line([(10, H - 20), (W - 10, H - 20)], fill=BLK + (255,), width=10)
    fnt = ImageFont.truetype(FONTS["play"], 420)
    bb = d.textbbox((0, 0), num, font=fnt)
    cx, cy = W / 2, 80 + (H - 190) / 2
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), num, font=fnt, fill=BLK + (255,))
    fs = ImageFont.truetype(FONTS["elite"], 40)
    d.text((W / 2 - 115, H - 88), "EVIDÊNCIA", font=fs, fill=BLK + (255,))
    # desgaste
    a = np.asarray(im).astype(float)
    a[..., :3] *= (1 - rng.random(a.shape[:2])[..., None] * 0.08)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


for n in "321":
    save(f"placard_{n}", placard(n))


# ---------- etiquetas de evidência (papel com furo, máquina de escrever)
def tag(lines, w=880):
    fs = ImageFont.truetype(FONTS["elite"], 58)
    h = 70 + 74 * len(lines)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(70, 0), (w, 0), (w, h), (70, h), (0, h / 2)], fill=WHT + (255,))
    d.ellipse((34, h / 2 - 16, 66, h / 2 + 16), fill=(0, 0, 0, 0))
    d.ellipse((30, h / 2 - 20, 70, h / 2 + 20), outline=(150, 150, 150, 255), width=5)
    for i, l in enumerate(lines):
        d.text((100, 36 + i * 74), l, font=fs, fill=BLK + (255,))
    a = np.asarray(im).astype(float)
    a[..., :3] -= rng.normal(0, 6, a[..., :3].shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


save("tag_3", tag(["EVIDÊNCIA Nº 3", "2025 · EUA"]))
save("tag_2", tag(["EVIDÊNCIA Nº 2", "2021 · EUA / ÁFR. DO SUL"], w=1000))
save("tag_1", tag(["EVIDÊNCIA Nº 1", "2006 · NORUEGA"]))


# ---------- fita zebrada
def tape(text="CENA DO CRIME  ·  NÃO ULTRAPASSE  ·  ", W=2400, H=150):
    im = Image.new("RGBA", (W, H), YEL + (255,))
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(FONTS["anton"], 96)
    x = 10
    while x < W:
        d.text((x, 10), text, font=fnt, fill=BLK + (255,))
        x += d.textlength(text, font=fnt)
    d.rectangle((0, 0, W, 8), fill=BLK + (255,))
    d.rectangle((0, H - 8, W, H), fill=BLK + (255,))
    a = np.asarray(im).astype(float)
    a[..., :3] *= (1 - rng.random(a.shape[:2])[..., None] * 0.1)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


save("tape", tape())


# ---------- cartaz de desaparecido genérico
def missing(seed):
    r = np.random.default_rng(seed)
    W, H = 600, 820
    im = Image.new("RGBA", (W, H), WHT + (255,))
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(FONTS["anton"], 96)
    d.text((38, 34), "DESAPARECIDO", font=fnt, fill=BLK + (255,))
    # silhueta genérica
    d.rectangle((90, 190, W - 90, 590), fill=(60, 60, 60, 255))
    d.ellipse((W / 2 - 80, 250, W / 2 + 80, 430), fill=(25, 25, 25, 255))
    d.rounded_rectangle((W / 2 - 150, 430, W / 2 + 150, 600), radius=80, fill=(25, 25, 25, 255))
    fs = ImageFont.truetype(FONTS["elite"], 40)
    for i in range(4):
        y = 620 + i * 48
        d.text((60, y), "█" * 0 + ("VISTO PELA ÚLTIMA VEZ" if i == 0 else "_" * int(r.integers(14, 22))), font=fs, fill=BLK + (255,))
    a = np.asarray(im).astype(float)
    a[..., :3] -= r.normal(0, 8, a[..., :3].shape)
    a[..., :3] *= (0.85 + 0.15 * r.random((H, W)))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


save("missing_a", missing(1))
save("missing_b", missing(2))


# ---------- estrela amarela de pontas
def star(n=14, W=1200):
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = W / 2
    pts = []
    for i in range(n * 2):
        a = np.pi * i / n - np.pi / 2
        rr = c * (0.98 if i % 2 == 0 else 0.6) * (0.92 + 0.08 * rng.random())
        pts.append((c + rr * np.cos(a), c + rr * np.sin(a)))
    d.polygon(pts, fill=YEL + (255,))
    return im


save("star", star())


# ---------- fumaça (fbm) e poeira
def smoke(W=1024, seed=0):
    r = np.random.default_rng(seed)
    acc = np.zeros((W, W))
    for o, amp in [(4, 1), (8, .5), (16, .25), (32, .12), (64, .06)]:
        n = r.random((o, o))
        acc += amp * np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, W), Image.BICUBIC)).astype(float) / 255
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    yy, xx = np.mgrid[0:W, 0:W] / W - 0.5
    mask = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) * 2.1, 0, 1) ** 1.5
    a = np.clip((acc - 0.35) * 1.8, 0, 1) * mask
    im = np.zeros((W, W, 4), np.uint8)
    im[..., :3] = 235
    im[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(im, "RGBA")


save("smoke_a", smoke(seed=1))
save("smoke_b", smoke(seed=5))


# ---------- pegadas no chão
def footprints(W=600, H=1600):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(8):
        x = W / 2 + (90 if i % 2 else -90)
        y = H - 120 - i * 190
        d.ellipse((x - 45, y - 80, x + 45, y + 40), fill=(10, 10, 10, 200))
        d.ellipse((x - 35, y + 55, x + 35, y + 120), fill=(10, 10, 10, 200))
    return im.filter(ImageFilter.GaussianBlur(3))


save("footprints", footprints())

json.dump(man, open(os.path.join(ROOT, "src", "txt.json"), "w"), indent=0)
print("ok", len(man))
