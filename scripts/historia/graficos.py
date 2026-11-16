"""Bandeiras redesenhadas (vetor simplificado, tons de cinza), documento da postura de 1830 e recorte
da manchete de 1937 — depois passam pelo mesmo tratamento (granulado + retícula + borda de adesivo)."""
import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "scripts/historia"); import tratar
F = "assets/historia/fonts/"
def star(d, cx, cy, r, fill, n=5, rot=-90, inner=0.4):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n); rr = r if i % 2 == 0 else r * inner; pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)
def flag(name, W=900, H=600):
    im = Image.new("L", (W, H), 255); d = ImageDraw.Draw(im)
    if name == "china":
        d.rectangle([0, 0, W, H], fill=95); star(d, 150, 150, 90, 235)
        for (x, y) in [(300, 60), (360, 120), (360, 210), (300, 270)]: star(d, x, y, 30, 235, rot=-90 + math.degrees(math.atan2(150 - y, 150 - x)))
    elif name == "india":
        for i, v in enumerate([150, 245, 110]): d.rectangle([0, i * H / 3, W, (i + 1) * H / 3], fill=v)
        cx, cy, r = W / 2, H / 2, 85; d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=40, width=10)
        for k in range(24):
            a = 2 * math.pi * k / 24; d.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)], fill=40, width=4)
    elif name == "egito":
        for i, v in enumerate([95, 245, 20]): d.rectangle([0, i * H / 3, W, (i + 1) * H / 3], fill=v)
        d.polygon([(450, 240), (500, 280), (480, 360), (420, 360), (400, 280)], fill=170)
    elif name == "portugal":
        d.rectangle([0, 0, W * .4, H], fill=110); d.rectangle([W * .4, 0, W, H], fill=95)
        cx, cy, r = W * .4, H / 2, 150; d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=215, width=22)
        d.rectangle([cx - 70, cy - 85, cx + 70, cy + 75], fill=245); d.rectangle([cx - 52, cy - 65, cx + 52, cy + 55], fill=95)
    elif name == "imperio":
        d.rectangle([0, 0, W, H], fill=110); d.polygon([(70, H / 2), (W / 2, 50), (W - 70, H / 2), (W / 2, H - 50)], fill=215)
        d.ellipse([W / 2 - 120, H / 2 - 120, W / 2 + 120, H / 2 + 120], outline=60, width=14)
        d.polygon([(W / 2 - 60, H / 2 - 70), (W / 2 + 60, H / 2 - 70), (W / 2 + 60, H / 2 + 20), (W / 2, H / 2 + 80), (W / 2 - 60, H / 2 + 20)], fill=95)
        d.rectangle([W / 2 - 45, H / 2 - 150, W / 2 + 45, H / 2 - 105], fill=60)
    elif name == "brasil":
        d.rectangle([0, 0, W, H], fill=110); d.polygon([(60, H / 2), (W / 2, 45), (W - 60, H / 2), (W / 2, H - 45)], fill=215)
        d.ellipse([W / 2 - 150, H / 2 - 150, W / 2 + 150, H / 2 + 150], fill=55)
        d.chord([W / 2 - 420, H / 2 - 120, W / 2 + 150, H / 2 + 520], 228, 300, fill=245, width=26)
        for (x, y) in [(400, 330), (470, 350), (520, 300), (430, 390), (500, 400)]: star(d, x, y, 9, 245)
    elif name == "eua48":
        for i in range(13): d.rectangle([0, i * H / 13, W, (i + 1) * H / 13], fill=95 if i % 2 == 0 else 245)
        d.rectangle([0, 0, W * .4, H * 7 / 13], fill=45)
        for r in range(6):
            for c in range(8): star(d, 24 + c * 43, 26 + r * 51, 13, 245)
    elif name == "israel":
        d.rectangle([0, 60, W, 150], fill=55); d.rectangle([0, H - 150, W, H - 60], fill=55)
        cx, cy, r = W / 2, H / 2, 120
        for rot in (-90, 90):
            pts = [(cx + r * math.cos(math.radians(rot + k * 120)), cy + r * math.sin(math.radians(rot + k * 120))) for k in range(3)]
            d.polygon(pts, outline=55, width=20)
    elif name == "uruguai":
        for i in range(9): d.rectangle([0, i * H / 9, W, (i + 1) * H / 9], fill=245 if i % 2 == 0 else 100)
        d.rectangle([0, 0, H * 5 / 9, H * 5 / 9], fill=245)
        cx = cy = H * 5 / 18
        for k in range(16):
            a = 2 * math.pi * k / 16; d.polygon([(cx + 55 * math.cos(a - .12), cy + 55 * math.sin(a - .12)), (cx + 135 * math.cos(a), cy + 135 * math.sin(a)), (cx + 55 * math.cos(a + .12), cy + 55 * math.sin(a + .12))], fill=190)
        d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=190)
    elif name == "canada":
        d.rectangle([0, 0, W / 4, H], fill=95); d.rectangle([W * 3 / 4, 0, W, H], fill=95)
        cx, cy, s = W / 2, H / 2 + 10, 1.0
        leaf = [(0, -190), (35, -120), (75, -140), (60, -40), (130, -110), (150, -70), (215, -85), (185, -10), (210, 10), (90, 95), (105, 135), (10, 120), (10, 205), (-10, 205), (-10, 120), (-105, 135), (-90, 95), (-210, 10), (-185, -10), (-215, -85), (-150, -70), (-130, -110), (-60, -40), (-75, -140), (-35, -120)]
        d.polygon([(cx + x * s, cy + y * s) for x, y in leaf], fill=95)
    elif name == "alemanha":
        for i, v in enumerate([20, 95, 200]): d.rectangle([0, i * H / 3, W, (i + 1) * H / 3], fill=v)
    return np.array(im).astype(np.float32) / 255
def save_graphic(g, name, border=10, pitch=5.0, seed=0, alpha=None):
    a = np.ones(g.shape, np.float32) if alpha is None else alpha
    a = np.pad(a[2:-2, 2:-2], 2)
    tratar.finish(tratar.texture(g, seed, pitch=pitch, grain=0.12, ht=0.45), a, name, border=border, shadow=True, maxside=900)
def torn(W, H, seed, amp=10):
    rng = np.random.default_rng(seed); m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    pts = []
    for x in range(0, W + 1, 14): pts.append((x, amp + rng.uniform(-amp, amp)))
    for y in range(0, H + 1, 14): pts.append((W - amp + rng.uniform(-amp, amp), y))
    for x in range(W, -1, -14): pts.append((x, H - amp + rng.uniform(-amp, amp)))
    for y in range(H, -1, -14): pts.append((amp + rng.uniform(-amp, amp), y))
    d.polygon(pts, fill=255); return np.array(m).astype(np.float32) / 255
def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    return lines + [cur]
def postura():
    W, H = 900, 760; im = Image.new("L", (W, H), 232); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(F + "PlayfairDisplay-italic-900.ttf", 52); f2 = ImageFont.truetype(F + "PlayfairDisplay-italic-700.ttf", 40); f3 = ImageFont.truetype(F + "Inter-normal-700.ttf", 22)
    d.text((W / 2, 70), "Posturas da Câmara Municipal", font=f1, fill=25, anchor="mm"); d.text((W / 2, 128), "Rio de Janeiro · 1830", font=f2, fill=60, anchor="mm")
    d.line([90, 170, W - 90, 170], fill=40, width=3)
    y = 210
    for ln in wrap(d, "§ 7º É prohibida a venda e uso do pito do pango.", f2, W - 170):
        d.text((85, y), ln, font=f2, fill=20); y += 56
    y += 16
    for ln in wrap(d, "Pena: o vendedor, multa de 20$000; os escravos e mais pessoas que dele usarem, 3 dias de cadeia.", f2, W - 170):
        d.text((85, y), ln, font=f2, fill=20); y += 56
    d.text((W / 2, H - 45), "trecho adaptado · Código de Posturas, Biblioteca Brasiliana / USP", font=f3, fill=90, anchor="mm")
    save_graphic(np.array(im).astype(np.float32) / 255, "g_postura1830", border=0, pitch=4.5, seed=3, alpha=torn(W, H, 5))
def manchete():
    W, H = 900, 640; im = Image.new("L", (W, H), 228); d = ImageDraw.Draw(im)
    fa = ImageFont.truetype(F + "Anton-normal-400.ttf", 150); fb = ImageFont.truetype(F + "PlayfairDisplay-italic-900.ttf", 64); fc = ImageFont.truetype(F + "Inter-normal-700.ttf", 26)
    d.text((W / 2, 46), "THE AMERICAN MAGAZINE · JULY 1937", font=fc, fill=40, anchor="mm"); d.line([50, 74, W - 50, 74], fill=30, width=4)
    d.text((W / 2, 175), "MARIJUANA", font=fa, fill=15, anchor="mm"); d.text((W / 2, 310), "Assassin of Youth", font=fb, fill=20, anchor="mm")
    d.text((W / 2, 372), "by H. J. ANSLINGER", font=fc, fill=40, anchor="mm"); d.line([50, 400, W - 50, 400], fill=30, width=2)
    rng = np.random.default_rng(2)
    for col in range(3):
        x0 = 60 + col * 270
        for k in range(9):
            w = 240 if k < 8 else rng.integers(80, 200); d.rectangle([x0, 425 + k * 22, x0 + w, 433 + k * 22], fill=120)
    save_graphic(np.array(im).astype(np.float32) / 255, "g_manchete1937", border=0, pitch=4.5, seed=4, alpha=torn(W, H, 9))
if __name__ == "__main__":
    for i, n in enumerate(["china", "india", "egito", "portugal", "imperio", "brasil", "eua48", "israel", "uruguai", "canada", "alemanha"]):
        save_graphic(flag(n), "flag_" + n, seed=10 + i)
    postura(); manchete(); print("ok")
