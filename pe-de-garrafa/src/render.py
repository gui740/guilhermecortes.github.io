"""Pixel-art renderer for PÉ DE GARRAFA. Everything is drawn in code.

Low-res canvas 270x480 -> palette quantized with ordered dither -> 4x nearest
upscale -> captions -> CRT post (scanlines, grain, vignette) -> ffmpeg.
"""
import json, math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import timeline as TL

W, H = 270, 480
S = 4
FW, FH = W * S, H * S
FONT = os.path.join(TL.ROOT, "assets", "fonts", "PressStart2P-Regular.ttf")
_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size)
    return _fonts[size]


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


PAL_HEX = ["#07060b", "#120e1c", "#1f1630", "#33224a", "#4e3168", "#74468f", "#a46cb8",
           "#0c1a12", "#163222", "#234a2e", "#3a6b3a", "#6a9a48",
           "#2a1c14", "#4a3222", "#6e4b30", "#9a7048", "#c9b48a", "#ece4cc",
           "#5a0a14", "#9c1424", "#e0303a", "#f2862a", "#ffd35a",
           "#3c4a6a", "#6d84a8", "#9aa6a0", "#c8d0c4", "#53625a", "#2e3a36"]
PAL = np.array([hx(h) for h in PAL_HEX], np.float32)
C = {n: hx(PAL_HEX[i]) for i, n in enumerate(
    ["k", "k1", "p0", "p1", "p2", "p3", "p4", "g0", "g1", "g2", "g3", "g4",
     "m0", "m1", "m2", "m3", "straw", "bone", "b0", "b1", "red", "orange", "yellow",
     "s0", "s1", "grey", "lgrey", "fog0", "fog1"])}

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16.0 - 0.5)
BAYER_FULL = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W, None]


def quantize(img, strength=34.0, pal=PAL):
    a = np.asarray(img, np.float32)[..., :3] + BAYER_FULL * strength
    flat = a.reshape(-1, 3)
    d = ((flat[:, None, :] - pal[None, :, :]) ** 2 * np.array([0.3, 0.59, 0.11], np.float32) * 3).sum(-1)
    idx = d.argmin(1)
    return pal[idx].reshape(H, W, 3).astype(np.uint8)


def rng(seed):
    return np.random.default_rng(seed)


def noise(w, h, cell, seed, octaves=3):
    r = rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(1, cell // (2 ** o))
        g = r.random((h // c + 3, w // c + 3)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize(((w // c + 3) * c, (h // c + 3) * c), Image.BICUBIC)
        out += np.asarray(im, np.float32)[:h, :w] / 255 * amp
        tot += amp
        amp *= 0.5
    return out / tot


def ease(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- layers
class Cache:
    pass


K = Cache()


def make_sky(top, bot, seed=1, stars=True):
    a = np.zeros((H, W, 3), np.float32)
    y = np.linspace(0, 1, H)[:, None, None]
    a[:] = np.array(top, np.float32) * (1 - y) + np.array(bot, np.float32) * y
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    if stars:
        r = rng(seed)
        d = ImageDraw.Draw(im)
        for _ in range(90):
            x, yy = int(r.integers(0, W)), int(r.integers(0, H * 0.55))
            d.point((x, yy), fill=C["lgrey"] if r.random() < 0.3 else C["s1"])
    return im


def draw_moon(im, cx, cy, r):
    d = ImageDraw.Draw(im)
    for i, (rr, col) in enumerate([(r + 9, C["p1"]), (r + 5, C["p2"]), (r + 2, C["p3"])]):
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C["bone"])
    for ox, oy, rr in [(-4, -3, 3), (3, 4, 2), (5, -5, 2), (-2, 6, 1)]:
        d.ellipse((cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr), fill=C["straw"])


def draw_tree(d, x, base, h, r, trunk, leaf, flower=None, lw=1.0):
    pts = [(x, base)]
    cx, cy = x, base
    segs = 6
    for i in range(segs):
        cx += r.integers(-4, 5)
        cy -= h * 0.6 / segs
        pts.append((cx, cy))
    for i in range(len(pts) - 1):
        wdt = max(1, int((5 - i * 0.7) * lw))
        d.line([pts[i], pts[i + 1]], fill=trunk, width=wdt)
    tips = []
    for b in range(int(r.integers(3, 6))):
        sx, sy = pts[int(r.integers(2, len(pts)))]
        ang = r.uniform(-2.6, -0.5)
        ln = h * r.uniform(0.18, 0.38)
        ex, ey = sx + math.cos(ang) * ln, sy + math.sin(ang) * ln
        mx, my = (sx + ex) / 2 + r.integers(-4, 5), (sy + ey) / 2 + r.integers(-3, 3)
        d.line([(sx, sy), (mx, my), (ex, ey)], fill=trunk, width=max(1, int(2 * lw)))
        tips.append((ex, ey))
    tips.append(pts[-1])
    for ex, ey in tips:
        for _ in range(int(r.integers(3, 6))):
            ox, oy = r.integers(-9, 10), r.integers(-6, 4)
            rx, ry = r.integers(5, 11), r.integers(3, 7)
            d.ellipse((ex + ox - rx, ey + oy - ry, ex + ox + rx, ey + oy + ry), fill=leaf)
            if flower is not None:
                for _ in range(4):
                    fx, fy = ex + ox + r.integers(-rx, rx + 1), ey + oy + r.integers(-ry, ry + 1)
                    d.point((fx, fy), fill=flower)


def make_tree_layer(width, height, seed, n, base_y, hmin, hmax, trunk, leaf, flower=None, lw=1.0, grass=None):
    im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = rng(seed)
    xs = np.sort(r.uniform(0, width, n))
    for x in xs:
        h = r.uniform(hmin, hmax)
        for off in (0, -width, width):
            rr = rng(int(x * 1000) + seed)
            draw_tree(d, x + off, base_y + r.integers(-3, 4) * 0, h, rr, trunk, leaf, flower, lw)
    if grass:
        d.rectangle((0, base_y, width, height), fill=grass)
        for x in range(0, width, 2):
            gh = int(r.integers(2, 8))
            d.line([(x, base_y), (x + r.integers(-1, 2), base_y - gh)], fill=grass)
    return im


def make_hills(width, seed, base, amp, col):
    im = Image.new("RGBA", (width, H), (0, 0, 0, 0))
    n = noise(width, 1, 60, seed, 3)[0]
    # make seamless
    n = (n + n[::-1]) / 2
    d = ImageDraw.Draw(im)
    for x in range(width):
        top = int(base - n[x] * amp)
        d.line([(x, top), (x, H)], fill=col)
    return im


def scroll(dst, layer, ox, oy=0):
    w = layer.width
    ox = int(ox) % w
    dst.alpha_composite(layer, (-ox, int(oy)))
    if w - ox < W:
        dst.alpha_composite(layer, (w - ox, int(oy)))


def init_layers():
    if hasattr(K, "ready"):
        return
    K.sky = make_sky(C["k1"], C["p2"], 3)
    draw_moon(K.sky, 205, 150, 16)
    K.hills = make_hills(1080, 5, 300, 50, C["p1"])
    K.trees_far = make_tree_layer(1080, H, 7, 22, 318, 50, 90, C["p2"], C["p2"])
    K.trees_mid = make_tree_layer(1080, H, 11, 12, 345, 90, 150, C["g1"], C["g2"], C["p4"], 1.2)
    K.trees_near = make_tree_layer(1620, H, 13, 7, 400, 170, 260, C["k1"], C["g0"], None, 2.0,
                                   grass=C["g0"])
    K.river = Image.new("RGBA", (1080, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(K.river)
    d.rectangle((0, 330, 1080, 352), fill=C["s0"])
    r = rng(3)
    for _ in range(140):
        x, y = r.integers(0, 1080), r.integers(332, 352)
        d.line([(x, y), (x + r.integers(3, 10), y)], fill=C["s1"] if r.random() < .4 else C["p2"])
    K.grass_fg = Image.new("RGBA", (1080, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(K.grass_fg)
    for x in range(0, 1080, 3):
        gh = int(r.integers(10, 40))
        d.polygon([(x - 2, H), (x + 2, H), (x + r.integers(-6, 7), H - 40 - gh)], fill=C["k"])
    K.fog = noise(W * 2, H, 40, 21, 3)
    K.mud = noise(W, H, 24, 31, 4)
    K.ready = True


def fog_overlay(base, t, amount=0.5, y0=250, y1=480, col=(110, 100, 140), speed=6):
    a = np.asarray(base, np.float32)
    off = int(t * speed) % W
    f = np.roll(K.fog, -off, axis=1)[:, :W]
    yy = np.linspace(0, 1, H)[:, None]
    band = np.clip((np.arange(H)[:, None] - y0) / max(1, (y1 - y0)), 0, 1) * (np.arange(H)[:, None] <= y1 + 60)
    m = np.clip((f - 0.35) * 2.2, 0, 1) * band * amount
    a[..., :3] = a[..., :3] * (1 - m[..., None]) + np.array(col, np.float32) * m[..., None]
    return Image.fromarray(a.astype(np.uint8))


def light(base, lights, ambient=0.25, warm=(255, 170, 80)):
    """lights: list of (x, y, radius, intensity)."""
    a = np.asarray(base, np.float32)
    rgb = a[..., :3]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    L = np.full((H, W), ambient, np.float32)
    tint = np.zeros((H, W), np.float32)
    for (x, y, r, k) in lights:
        dd = np.sqrt((xx - x) ** 2 + (yy - y) ** 2) / r
        f = np.clip(1 - dd, 0, 1) ** 1.6 * k
        L += f
        tint += f
    L = np.clip(L, 0, 1.5)
    tint = np.clip(tint, 0, 1)[..., None]
    out = rgb * L[..., None]
    out = out * (1 - 0.35 * tint) + np.array(warm, np.float32) * 0.35 * tint * L[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def darken(img, k):
    a = np.asarray(img, np.float32)[..., :3] * k
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


# ---------------------------------------------------------------- sprites
def man_side(d, x, y, frame, face=1, shirt=None, lantern=False, sitting=False, gun=False, raise_arm=0.0):
    shirt = shirt or C["s1"]
    skin, pants, hat, beard = C["m2"], C["m1"], C["straw"], C["lgrey"]
    bob = 1 if frame % 2 == 1 else 0
    y = y + bob
    lo = [(-2, 2), (0, 0), (2, -2), (0, 0)][frame % 4]
    if sitting:
        d.rectangle((x - 3, y - 4, x + 5 * face, y - 2), fill=pants)
        d.rectangle((x + 4 * face - 1, y - 4, x + 4 * face + 1, y), fill=pants)
        top = y - 4
    else:
        d.line([(x - 1, y - 8), (x - 1 + lo[0], y)], fill=pants, width=2)
        d.line([(x + 1, y - 8), (x + 1 + lo[1], y)], fill=C["m0"], width=2)
        top = y - 8
    # sack on back
    d.rectangle((x - 5 * face - (2 if face > 0 else 0), top - 9, x - 5 * face + (2 if face < 0 else 0), top - 2), fill=C["m3"])
    d.rectangle((x - 3, top - 9, x + 3, top), fill=shirt)
    # head
    d.rectangle((x - 2, top - 14, x + 2, top - 10), fill=skin)
    d.rectangle((x - 2 + face, top - 11, x + 2, top - 9), fill=beard)
    d.point((x + face * 1, top - 13), fill=C["k"])
    # hat
    d.rectangle((x - 5, top - 15, x + 5, top - 14), fill=hat)
    d.rectangle((x - 2, top - 18, x + 2, top - 15), fill=hat)
    d.line([(x - 2, top - 16), (x + 2, top - 16)], fill=C["m2"])
    # arm
    sw = [1, 0, -1, 0][frame % 4] if not lantern else 0
    if lantern:
        ax, ay = x + 5 * face, top - 7 - int(raise_arm * 8)
        d.line([(x + 2 * face, top - 7), (ax, ay)], fill=shirt, width=2)
        d.rectangle((ax - 1, ay, ax + 1, ay + 4), fill=C["yellow"])
        d.point((ax, ay - 1), fill=C["m1"])
    elif gun:
        d.line([(x, top - 7), (x + 3 * face, top - 3)], fill=shirt, width=2)
        d.line([(x - 4 * face, top - 10), (x + 7 * face, top - 1)], fill=C["m0"], width=1)
    else:
        d.line([(x, top - 7), (x + sw * 2, top - 1)], fill=shirt, width=2)


def man2(im, x, y, frame, face=1, scale=2, **kw):
    """draw side man at 2x pixel scale; (x, y) = feet position on im."""
    sp = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    man_side(ImageDraw.Draw(sp), 20, 36, frame, face, **kw)
    sp = sp.resize((40 * scale, 40 * scale), Image.NEAREST)
    im.alpha_composite(sp, (int(x - 20 * scale), int(y - 36 * scale)))
    return (x + 5 * face * scale, y - (15 + 7) * scale)


def man_top(d, x, y, frame, shirt=None, lantern=False):
    shirt = shirt or C["s1"]
    sw = [1, 0, -1, 0][frame % 4]
    d.ellipse((x - 5, y - 3, x + 5, y + 3), fill=shirt)
    d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=C["straw"])
    d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=C["m3"])
    if lantern:
        d.rectangle((x + 5, y + 2, x + 7, y + 4), fill=C["yellow"])


def creature(im, cx, base, h, t, eye=1.0, rim=C["p3"], body=C["k"], seed=77, navel=False):
    r = rng(seed)
    d = ImageDraw.Draw(im)
    sway = math.sin(t * 1.3) * h * 0.01

    def hairy(cx_, cy_, rx, ry, n=46, jag=0.18):
        pts = []
        for i in range(n):
            a = i / n * math.tau
            k = 1 + (jag if i % 2 else -jag * 0.3) * (0.6 + 0.4 * math.sin(i * 1.7 + t * 2))
            pts.append((cx_ + math.cos(a) * rx * k, cy_ + math.sin(a) * ry * k))
        return pts

    def shape(dx, col):
        legw = h * 0.07
        hip = base - h * 0.42
        d.polygon([(cx - legw + dx, hip), (cx + legw + dx, hip), (cx + legw * 0.8 + dx, base - h * 0.04),
                   (cx - legw * 0.8 + dx, base - h * 0.04)], fill=col)
        fr = h * 0.08
        d.ellipse((cx - fr + dx, base - fr * 0.9, cx + fr + dx, base + fr * 0.2), fill=col)
        tx, ty = cx + sway + dx, base - h * 0.62
        d.polygon(hairy(tx, ty, h * 0.2, h * 0.26), fill=col)
        hx_, hy = cx + sway * 1.6 + dx, base - h * 0.9
        d.polygon(hairy(hx_, hy, h * 0.1, h * 0.1, 30, 0.25), fill=col)
        for s in (-1, 1):
            sx, sy = tx + s * h * 0.16, ty - h * 0.15
            ex, ey = tx + s * h * 0.27, base - h * 0.3 + math.sin(t * 2 + s) * 2
            d.line([(sx, sy), (ex, ey)], fill=col, width=max(1, int(h * 0.05)))
            for c in (-1, 0, 1):
                d.line([(ex, ey), (ex + c * h * 0.02, ey + h * 0.05)], fill=col, width=1)
        return hx_, hy, tx, ty

    shape(-1, rim)
    shape(1, C["p1"])
    hx_, hy, tx, ty = shape(0, body)
    if eye > 0:
        ew = max(1, h * 0.05)
        eh = max(1, h * 0.03 * eye)
        d.ellipse((hx_ - ew - 2, hy - eh - 2, hx_ + ew + 2, hy + eh + 2), fill=C["b0"])
        d.ellipse((hx_ - ew, hy - eh, hx_ + ew, hy + eh), fill=C["red"])
        d.point((hx_, hy), fill=C["yellow"])
    if navel:
        nr = max(2, h * 0.025)
        d.ellipse((tx - nr, ty + h * 0.06 - nr, tx + nr, ty + h * 0.06 + nr), fill=C["bone"])
    return hx_, hy, tx, ty


def footprint(d, x, y, r, water=True, t=0.0):
    d.ellipse((x - r - 1, y - r - 1, x + r + 1, y + r + 1), fill=C["m3"])
    d.ellipse((x - r, y - r + 1, x + r, y + r + 1), fill=C["m0"])
    d.ellipse((x - r + 1, y - r + 2, x + r - 1, y + r), fill=C["k1"] if not water else C["s0"])


def glyph_text(d, xy, text, size, fill, shadow=C["k"], anchor="mm", stroke=0):
    f = font(size)
    x, y = xy
    if shadow is not None:
        d.text((x + max(1, size // 8), y + max(1, size // 8)), text, font=f, fill=shadow, anchor=anchor)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=C["k"])


# ---------------------------------------------------------------- scenes
def forest_base(cam, t, river=True, moon=True):
    im = K.sky.copy() if moon else make_sky(C["k1"], C["p1"], 3)
    scroll(im, K.hills, cam * 0.1)
    scroll(im, K.trees_far, cam * 0.2)
    if river:
        scroll(im, K.river, cam * 0.35)
    scroll(im, K.trees_mid, cam * 0.5)
    return im


def fireflies(d, t, n=14, seed=5, area=(0, 200, W, 420), fade=1.0):
    r = rng(seed)
    for i in range(n):
        if r.random() > fade:
            continue
        bx, by = r.uniform(area[0], area[2]), r.uniform(area[1], area[3])
        ph = r.uniform(0, 6.28)
        x = bx + math.sin(t * 0.7 + ph) * 12
        y = by + math.cos(t * 0.5 + ph * 2) * 8
        if math.sin(t * 3 + ph * 3) > 0.1:
            d.point((x, y), fill=C["yellow"])
            if math.sin(t * 3 + ph * 3) > 0.7:
                d.point((x + 1, y), fill=C["g4"])


def sc_hook(lt, dur, g):
    # top-down mud close-up with round footprint filling with water
    m = K.mud
    z = 1.0 + 0.09 * lt
    a = np.zeros((H, W, 3), np.float32)
    cols = np.array([C["m0"], C["m1"], C["m2"], C["m1"]], np.float32)
    idx = np.clip((m * 1.4 - 0.15) * 3.99, 0, 3.99)
    lo = np.floor(idx).astype(int)
    fr = (idx - lo)[..., None]
    a = cols[lo] * (1 - fr) + cols[np.minimum(lo + 1, 3)] * fr
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    r = rng(9)
    for _ in range(60):  # grass bits / twigs
        x, y = r.integers(0, W), r.integers(0, H)
        d.line([(x, y), (x + r.integers(-6, 7), y + r.integers(-6, 7))], fill=C["g1"] if r.random() < .6 else C["m3"])
    cx, cy, R = 135, 228, 50
    # second print far
    d.ellipse((150 - 22, 70 - 18, 150 + 22, 70 + 18), fill=C["m3"])
    d.ellipse((150 - 20, 70 - 15, 150 + 20, 70 + 17), fill=C["k1"])
    d.ellipse((cx - R - 4, cy - R - 4, cx + R + 4, cy + R + 4), fill=C["m3"])
    d.ellipse((cx - R - 1, cy - R + 2, cx + R + 1, cy + R + 3), fill=C["m0"])
    d.ellipse((cx - R + 2, cy - R + 5, cx + R - 2, cy + R), fill=C["k1"])
    # water rising
    wl = ease(lt / max(dur, 0.1) * 1.4)
    rr = (R - 4) * (0.35 + 0.65 * wl)
    d.ellipse((cx - rr, cy - rr * 0.95 + 3, cx + rr, cy + rr * 0.95 + 3), fill=C["s0"])
    # moon reflection + ripple
    d.ellipse((cx + 8, cy - 14, cx + 18, cy - 4), fill=C["s1"])
    d.ellipse((cx + 10, cy - 12, cx + 16, cy - 6), fill=C["bone"])
    for k in range(3):
        ph = (lt * 0.8 + k / 3) % 1
        rp = rr * ph
        d.ellipse((cx - rp, cy - rp * 0.9 + 3, cx + rp, cy + rp * 0.9 + 3), outline=C["s1"])
    # red eye reflected in the puddle (someone is standing over you)
    if lt > 0.6:
        op = ease((lt - 0.6) / 0.25)
        blink = 0 if (1.7 < lt < 1.82) else 1
        ex, ey = cx - 10, cy + 4
        eh = int(5 * op * blink)
        if eh > 0:
            d.ellipse((ex - 13, ey - eh - 2, ex + 13, ey + eh + 2), fill=C["b0"])
            d.ellipse((ex - 10, ey - eh, ex + 10, ey + eh), fill=C["red"])
            d.line([(ex, ey - eh + 1), (ex, ey + eh - 1)], fill=C["k"], width=2)
        # dark silhouette of the head reflected
        d.arc((ex - 26, ey - 22, ex + 26, ey + 26), 200, 340, fill=C["k1"], width=3)
    fireflies(d, lt, 10, 3, (0, 0, W, H), fade=max(0.0, 1 - lt / max(dur, .1)))
    # zoom
    im = im.resize((int(W * z), int(H * z)), Image.NEAREST)
    ox, oy = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((ox, oy, ox + W, oy + H))
    im = light(im, [(cx, cy, 160, 0.6)], ambient=0.55, warm=(120, 140, 200))
    return im


def sc_title(lt, dur, g):
    im = make_sky(C["k"], C["p1"], 4)
    draw_moon(im, 135, 120, 22)
    scroll(im, K.hills, 0)
    scroll(im, K.trees_far, 40)
    d = ImageDraw.Draw(im)
    r = rng(int(lt * 15))
    p = ease(lt / 0.4)
    y = 205
    for i, line in enumerate(["PÉ DE", "GARRAFA"]):
        glyph_text(d, (135 + (r.integers(-2, 3) if lt < 0.3 else 0), y + i * 30), line, 24, C["red"], C["b0"])
    # drips
    for k in range(9):
        x = 40 + k * 23 + (k * 7) % 5
        L = int(min(1, lt / dur * 1.3) * (8 + (k * 13) % 17))
        d.line([(x, 242), (x, 242 + L)], fill=C["b1"], width=2)
    if lt > 0.35:
        glyph_text(d, (135, 300), "FASE 1", 8, C["yellow"])
        glyph_text(d, (135, 316), "BEIRA DO RIO PARAGUAI", 8, C["bone"])
        glyph_text(d, (135, 330), "1874", 8, C["bone"])
    return im


def sc_forest(lt, dur, g):
    cam = lt * 22
    im = forest_base(cam, lt)
    d = ImageDraw.Draw(im)
    scroll(im, K.trees_near, cam)
    d = ImageDraw.Draw(im)
    man2(im, 110, 404, int(lt * 7), 1)
    d = ImageDraw.Draw(im)
    fireflies(d, lt, 16, 8, (0, 220, W, 400))
    scroll(im, K.grass_fg, cam * 1.5, 30)
    im = fog_overlay(im, lt, 0.45, 300, 420)
    im = light(im, [(205, 150, 150, 0.35)], ambient=0.75, warm=(170, 160, 220))
    return im


def sc_silhouette(lt, dur, g):
    cam = 300 + lt * 6
    im = forest_base(cam, lt)
    p = ease(lt / (dur * 0.6))
    cr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    eye = ease((lt - dur * 0.25) / 0.4)
    creature(cr, 150, 362, 250 + p * 8, lt, eye=eye, rim=C["p4"])
    # fade-in silhouette
    a = np.asarray(cr).copy()
    a[..., 3] = (a[..., 3] * min(1, 0.45 + p)).astype(np.uint8)
    im.alpha_composite(Image.fromarray(a))
    scroll(im, K.trees_near, cam)
    d = ImageDraw.Draw(im)
    man2(im, 60, 404, 1, 1)
    scroll(im, K.grass_fg, cam * 1.5, 30)
    im = fog_overlay(im, lt, 0.6, 260, 420)
    im = light(im, [(205, 150, 150, 0.35)], ambient=0.68, warm=(170, 160, 220))
    return im


def sc_footclose(lt, dur, g):
    # low side close-up: the bottle-bottom foot stomps twice, leaving round prints
    im = forest_base(500, lt, river=False)
    im = darken(im, 0.8)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 370, W, H), fill=C["m1"])
    r = rng(5)
    for _ in range(140):
        x, y = r.integers(0, W), r.integers(372, H)
        d.point((x, y), fill=C["m2"] if r.random() < .5 else C["m0"])
    for x in range(0, W, 3):
        d.line([(x, 371), (x + 1, 364 - (x * 7) % 8)], fill=C["g2"])
    for i, k in enumerate((0.15, 0.9)):
        st = k * dur
        fx = 95 if i == 0 else 185
        lift = ease((lt - (0.62 * dur)) / 0.4) if i == 0 else 0.0
        drop = ease((lt - st + 0.3) / 0.3)
        if lt > st:  # print left behind
            footprint(d, fx, 392, 22, water=True)
            d.ellipse((fx - 18, 388, fx + 18, 398), fill=C["s1"])
        if lt > st - 0.3 and lift < 1:
            fy = lerp(60, 392, drop) - lift * 400
            hw = 30
            # hairy leg
            d.polygon([(fx - hw - 3, -20), (fx + hw + 3, -20), (fx + hw, fy - 20), (fx - hw, fy - 20)], fill=C["p3"])
            d.polygon([(fx - hw, -20), (fx + hw, -20), (fx + hw - 3, fy - 20), (fx - hw + 3, fy - 20)], fill=C["p1"])
            for j in range(int(max(0, fy) // 6)):
                yy = j * 6 + (j * 3) % 5
                for sgn in (-1, 1):
                    d.line([(fx + sgn * (hw - 2), yy), (fx + sgn * (hw + 5), yy + 4)], fill=C["p3"] if sgn < 0 else C["p0"])
            # bottle-bottom foot
            d.ellipse((fx - 30, fy - 30, fx + 30, fy + 6), fill=C["k1"])
            d.ellipse((fx - 30, fy - 6, fx + 30, fy + 8), fill=C["s0"])
            d.ellipse((fx - 20, fy - 3, fx + 20, fy + 5), fill=C["s1"])
            d.ellipse((fx - 8, fy, fx + 8, fy + 3), fill=C["lgrey"])
            if lt > st:  # mud splash
                for kk in range(10):
                    ang = kk / 9 * math.pi
                    dist = (lt - st) * 70
                    d.point((fx + math.cos(ang) * (30 + dist), 380 - math.sin(ang) * dist * 0.7 + (lt - st) ** 2 * 120), fill=C["m2"])
    im = light(im, [(W // 2, 300, 260, 0.5)], ambient=0.75, warm=(150, 150, 210))
    return im


def sc_circle(lt, dur, g):
    # top-down ground, footprints making a loop, spinning "?"
    m = K.mud
    a = (np.array(C["g2"], np.float32) * (1 - m[..., None]) + np.array(C["m2"], np.float32) * m[..., None])
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    r = rng(4)
    for _ in range(300):
        x, y = r.integers(0, W), r.integers(0, H)
        d.point((x, y), fill=C["g2"])
    n = int(min(1, lt / (dur * 0.7)) * 12)
    for i in range(n):
        ang = i / 12 * math.tau
        footprint(d, 135 + math.cos(ang) * 80, 200 + math.sin(ang) * 80, 9, water=False)
    # spinning arrow
    ang = lt * 9
    ax, ay = 135 + math.cos(ang) * 22, 200 + math.sin(ang) * 22
    d.line([(135, 200), (ax, ay)], fill=C["yellow"], width=2)
    glyph_text(d, (135, 200), "?", 24, C["red"])
    im = light(im, [(135, 200, 190, 0.6)], ambient=0.5, warm=(140, 150, 210))
    return im


def fire(d, x, y, t, k=1.0):
    r = rng(int(t * 12))
    for i in range(int(16 * k)):
        h = r.uniform(6, 22) * k
        wx = r.uniform(-7, 7) * k
        col = [C["red"], C["orange"], C["yellow"]][min(2, int(r.random() * 3 * (1 - abs(wx) / 10)))]
        d.polygon([(x + wx - 3, y), (x + wx + 3, y), (x + wx * 0.5 + r.uniform(-2, 2), y - h)], fill=col)
    d.line([(x - 9, y + 1), (x + 9, y - 1)], fill=C["m1"], width=2)
    d.line([(x - 9, y - 1), (x + 9, y + 1)], fill=C["m0"], width=2)
    for i in range(3):
        ph = (t * 0.7 + i / 3) % 1
        d.point((x + math.sin(t * 5 + i) * 6, y - 20 - ph * 50), fill=C["orange"])


def sc_camp(lt, dur, g, bento=True, k_fire=None):
    im = forest_base(800, lt, river=False)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 395, W, H), fill=C["g0"])
    # trees with hammocks
    for tx in (30, 240):
        d.rectangle((tx - 4, 210, tx + 4, 400), fill=C["k1"])
        d.ellipse((tx - 30, 170, tx + 30, 230), fill=C["g0"])
    d.arc((30, 280, 120, 330), 0, 180, fill=C["m3"], width=3)
    d.line([(30, 300), (120, 300)], fill=C["m2"])
    # horse silhouette
    hx_ = 220
    d.ellipse((hx_ - 20, 345, hx_ + 14, 368), fill=C["k"])
    d.polygon([(hx_ + 8, 350), (hx_ + 22, 330), (hx_ + 28, 336), (hx_ + 16, 356)], fill=C["k"])
    for lx in (-16, -10, 6, 11):
        d.line([(hx_ + lx, 362), (hx_ + lx, 396)], fill=C["k"], width=2)
    kf = k_fire if k_fire is not None else lerp(1.0, 0.55, ease(lt / dur))
    fire(d, 135, 398, lt, kf)
    man2(im, 100, 402, 0, 1, sitting=True)
    if bento:
        bx = 165 + max(0, lt - 0.4) * 38
        if bx < W + 10:
            man2(im, int(bx), 404, int(lt * 7), 1, shirt=C["b1"], gun=True)
    flick = 1 + 0.08 * math.sin(lt * 23) + 0.05 * math.sin(lt * 37)
    im = light(im, [(135, 385, 130 * kf * flick, 1.0)], ambient=0.5)
    return im


def sc_scream(lt, dur, g):
    lines = g["lines"]
    im = sc_camp(lt + 3, dur, g, bento=False, k_fire=0.35)
    im = darken(im, 0.75)
    d = ImageDraw.Draw(im)
    sl = g["line_at"]("L07B")
    if sl and sl["start"] - 0.05 <= g["t"] <= sl["start"] + sl["dur"] + 0.6:
        r = rng(int(g["t"] * 30))
        lt2 = g["t"] - sl["start"]
        for i, wd in enumerate(["Ô,", "COMPADREEE!"]):
            glyph_text(d, (135 + r.integers(-3, 4), 170 + i * 28 + r.integers(-3, 4)), wd, 16 if i else 24, C["red"], C["b0"])
    return im


def sc_lantern(lt, dur, g):
    cam = 1200 + lt * 26
    im = forest_base(cam, lt, river=False, moon=False)
    scroll(im, K.trees_near, cam)
    d = ImageDraw.Draw(im)
    fr = int(lt * 6)
    mx = 120
    lx, ly = man2(im, mx, 404, fr, 1, lantern=True)
    scroll(im, K.grass_fg, cam * 1.5, 30)
    im = fog_overlay(im, lt, 0.7, 240, 430, col=(70, 60, 100), speed=14)
    flick = 1 + 0.1 * math.sin(lt * 19) + 0.06 * math.sin(lt * 41)
    im = light(im, [(lx, ly + 4, 115 * flick, 1.15)], ambient=0.3)
    d = ImageDraw.Draw(im)
    # directional scream icons on "frente/atrás/em cima"
    for wtxt, pos in (("frente", (232, 300)), ("Atrás", (38, 300)), ("cima", (135, 150))):
        w = g["word_at"]("L10", wtxt)
        if w and w["s"] - 0.05 <= g["t"] <= w["s"] + 0.9:
            ph = g["t"] - w["s"]
            r = rng(int(g["t"] * 40))
            x, y = pos[0] + r.integers(-2, 3), pos[1] + r.integers(-2, 3)
            glyph_text(d, (x, y), "!", 24, C["red"], C["b0"])
            for k in range(3):
                rr = 10 + ((ph * 40 + k * 8) % 24)
                d.arc((x - rr, y - rr, x + rr, y + rr), 0, 360, fill=C["b1"])
    return im


def sc_circletop(lt, dur, g):
    m = K.mud
    a = (np.array(C["g0"], np.float32) * (1 - m[..., None]) + np.array(C["m0"], np.float32) * m[..., None])
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    r = rng(12)
    for _ in range(200):
        x, y = r.integers(0, W), r.integers(0, H)
        d.line([(x, y), (x + 1, y - 2)], fill=C["g1"])
    p = min(1, lt / (dur * 0.85))
    n = int(p * 48)
    pts = []
    for i in range(48):
        ring = i // 16
        ang = (i % 16) / 16 * math.tau + ring * 0.2
        rad = 45 + ring * 26
        pts.append((135 + math.cos(ang) * rad, 215 + math.sin(ang) * rad * 1.0))
    order = rng(2).permutation(48)
    for i in order[:n]:
        footprint(d, pts[i][0], pts[i][1], 7, water=False)
    man_top(d, 135, 215, int(lt * 4), lantern=True)
    flick = 1 + 0.1 * math.sin(lt * 21)
    im = light(im, [(141, 218, 130 * flick, 1.1)], ambient=0.22)
    g["fcount"] = 1 + n
    return im


def sc_boss(lt, dur, g):
    im = Image.new("RGBA", (W, H), C["k"])
    d = ImageDraw.Draw(im)
    # frame
    d.rectangle((14, 104, W - 15, 340), outline=C["bone"], width=2)
    d.rectangle((18, 108, W - 19, 336), outline=C["b1"], width=1)
    glyph_text(d, (135, 120), "BOSS", 8, C["yellow"])
    glyph_text(d, (135, 138), "PÉ DE GARRAFA", 16, C["red"], C["b0"])
    creature(im, 135, 312, 150, lt, eye=1.0, rim=C["p4"], body=C["p0"], navel=True)
    d = ImageDraw.Draw(im)
    # navel marker blinking
    nx, ny = 135 + math.sin(lt * 1.3) * 1.5, 312 - 150 * 0.62 + 150 * 0.06
    if (lt * 4) % 1 < 0.6:
        d.rectangle((nx - 9, ny - 9, nx + 9, ny + 9), outline=C["yellow"])
        d.line([(nx + 10, ny), (205, ny)], fill=C["yellow"])
    glyph_text(d, (135, 312), "PONTO FRACO:", 8, C["bone"])
    w = g["word_at"]("L12", "umbigo")
    if w and g["t"] >= w["s"]:
        glyph_text(d, (135, 326), "UMBIGO BRANCO", 8, C["yellow"])
    return im


def sc_raise(lt, dur, g):
    # POV: lantern rises slowly revealing hair, then silence
    speech = g["line_at"]("L13")["dur"] + 0.1
    p = ease(lt / dur)
    im = Image.new("RGBA", (W, H), C["k"])
    d = ImageDraw.Draw(im)
    r = rng(44)
    # hairy wall (creature body) close
    for i in range(500):
        x = r.integers(-10, W + 10)
        y = r.integers(0, H)
        L = r.integers(10, 40)
        d.line([(x, y), (x + r.integers(-4, 5), y + L)], fill=[C["p1"], C["p2"], C["p0"], C["p3"]][i % 4], width=2)
    # foot/leg base at bottom
    ly = lerp(420, 300, p)
    hand_y = lerp(470, 280, p)
    im = light(im, [(158, hand_y - 12, 150, 1.25)], ambient=0.1)
    d = ImageDraw.Draw(im)
    d.line([(190, H), (160, hand_y)], fill=C["s1"], width=6)
    d.rectangle((150, hand_y - 20, 166, hand_y - 2), fill=C["yellow"])
    d.rectangle((152, hand_y - 18, 164, hand_y - 4), fill=C["orange"])
    d.rectangle((154, hand_y - 24, 162, hand_y - 21), fill=C["m1"])
    return im


def sc_jumpscare(lt, dur, g):
    open_ = ease(lt / 0.12)
    im = Image.new("RGBA", (W, H), C["k"])
    d = ImageDraw.Draw(im)
    r = rng(91)
    for i in range(900):
        x = r.integers(-10, W + 10)
        y = r.integers(-20, H)
        L = r.integers(15, 60)
        d.line([(x, y), (x + r.integers(-8, 9), y + L)], fill=[C["p0"], C["k1"], C["p1"], C["b0"]][i % 4], width=2)
    cx, cy = 135, 205
    ew, eh = 110, int(70 * open_)
    if eh > 1:
        d.ellipse((cx - ew - 6, cy - eh - 6, cx + ew + 6, cy + eh + 6), fill=C["b0"])
        d.ellipse((cx - ew, cy - eh, cx + ew, cy + eh), fill=C["straw"])
        for k in range(14):
            a = r.uniform(0, math.tau)
            x0, y0 = cx + math.cos(a) * ew * 0.95, cy + math.sin(a) * eh * 0.95
            d.line([(x0, y0), (lerp(x0, cx, 0.4) + r.integers(-6, 6), lerp(y0, cy, 0.4))], fill=C["b1"])
        look = math.sin(lt * 40) * 3
        d.ellipse((cx - 44 + look, cy - min(44, eh), cx + 44 + look, cy + min(44, eh)), fill=C["red"])
        d.ellipse((cx - 30 + look, cy - min(30, eh), cx + 30 + look, cy + min(30, eh)), fill=C["b1"])
        d.ellipse((cx - 5 + look, cy - min(34, eh), cx + 5 + look, cy + min(34, eh)), fill=C["k"])
        d.rectangle((cx + 14 + look, cy - 18, cx + 19 + look, cy - 13), fill=C["bone"])
    # mouth
    my = 360
    mo = ease((lt - 0.05) / 0.2)
    mh = int(55 * mo)
    d.ellipse((50, my - mh, 220, my + mh), fill=C["k"])
    for k in range(9):
        x = 62 + k * 18
        d.polygon([(x, my - mh + 2), (x + 10, my - mh + 2), (x + 5, my - mh + 20 * mo)], fill=C["bone"])
        d.polygon([(x + 4, my + mh - 2), (x + 14, my + mh - 2), (x + 9, my + mh - 18 * mo)], fill=C["straw"])
    zoom = 1 + 0.25 * ease(lt / dur)
    im = im.resize((int(W * zoom), int(H * zoom)), Image.NEAREST)
    ox, oy = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((ox, oy, ox + W, oy + H))


def sc_morning(lt, dur, g):
    m = K.mud
    a = (np.array(C["fog0"], np.float32) * (1 - m[..., None]) + np.array(C["fog1"], np.float32) * m[..., None])
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    r = rng(15)
    for _ in range(250):
        x, y = r.integers(0, W), r.integers(0, H)
        d.line([(x, y), (x, y - 2)], fill=C["fog0"])
    cx, cy, R = 135, 205, 66
    for i in range(32):
        a2 = i / 32 * math.tau
        if i % 2:
            footprint(d, cx + math.cos(a2) * (R + 14), cy + math.sin(a2) * (R + 14), 5, water=False)
        else:
            px, py = cx + math.cos(a2) * R, cy + math.sin(a2) * R
            d.ellipse((px - 2, py - 3, px + 2, py + 3), fill=C["fog1"])
    ang = lt * 1.6
    bx, by = cx + math.cos(ang) * R, cy + math.sin(ang) * R
    sp = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    man_top(ImageDraw.Draw(sp), 10, 10, int(lt * 5), shirt=C["b1"])
    im.alpha_composite(sp.resize((40, 40), Image.NEAREST), (int(bx - 20), int(by - 20)))
    im = fog_overlay(im, lt, 0.6, 0, 480, col=C["lgrey"], speed=8)
    return im


def sc_gameover(lt, dur, g):
    im = Image.new("RGBA", (W, H), C["k"])
    d = ImageDraw.Draw(im)
    p = ease(lt / 0.6)
    glyph_text(d, (135, 200), "GAME", 32, C["red"], C["b0"])
    glyph_text(d, (135, 240), "OVER", 32, C["red"], C["b0"])
    for k in range(14):
        x = 24 + k * 16 + (k * 5) % 7
        L = int(min(1, lt / dur * 1.2) * (10 + (k * 17) % 50))
        d.line([(x, 258), (x, 258 + L)], fill=C["b1"], width=3)
        d.point((x, 259 + L), fill=C["red"])
    # dropped lantern dying
    kk = max(0.0, 1 - lt / dur)
    d.rectangle((120, 400, 140, 410), fill=C["m1"])
    fire(d, 130, 400, lt, 0.3 * kk + 0.05)
    im = light(im, [(130, 395, 60 * kk + 10, 1.0)], ambient=0.9)
    return im


def sc_continue(lt, dur, g):
    im = Image.new("RGBA", (W, H), C["k"])
    d = ImageDraw.Draw(im)
    glyph_text(d, (135, 170), "CONTINUE?", 24, C["bone"])
    n = max(1, 9 - int(lt * 2.2))
    glyph_text(d, (135, 215), str(n), 24, C["red"])
    sel = int(lt * 2.5) % 2
    for i, opt in enumerate(["SIM", "NÃO"]):
        x = 85 + i * 100
        glyph_text(d, (x, 265), opt, 16, C["yellow"] if i == sel else C["grey"])
        if i == sel and (lt * 4) % 1 < 0.7:
            glyph_text(d, (x - 34, 265), ">", 16, C["red"], None)
    glyph_text(d, (135, 312), "VOCÊ RESPONDERIA?", 8, C["bone"])
    glyph_text(d, (135, 328), "COMENTA AÍ", 8, C["yellow"])
    return im


SCENE_FN = {"hook": sc_hook, "title": sc_title, "forest": sc_forest, "silhouette": sc_silhouette,
            "footclose": sc_footclose, "circle": sc_circle, "camp": sc_camp, "scream": sc_scream,
            "lantern": sc_lantern, "circletop": sc_circletop, "boss": sc_boss, "raise": sc_raise,
            "jumpscare": sc_jumpscare, "morning": sc_morning, "gameover": sc_gameover,
            "continue": sc_continue}
HUD_SCENES = {"forest", "silhouette", "footclose", "circle", "camp", "scream", "lantern", "circletop", "raise"}


# ---------------------------------------------------------------- HUD / captions / post
HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]


def draw_hud(d, sanity, steps, t):
    y = 66
    for j, row in enumerate(HEART):
        for i, ch in enumerate(row):
            if ch == "1":
                d.point((16 + i, y + j), fill=C["red"])
    d.rectangle((26, y, 106, y + 6), outline=C["bone"])
    wbar = int(78 * max(0, sanity))
    col = C["g4"] if sanity > 0.5 else (C["yellow"] if sanity > 0.25 else C["red"])
    if sanity < 0.25 and (t * 6) % 1 < 0.5:
        col = C["b1"]
    if wbar > 0:
        d.rectangle((27, y + 1, 27 + wbar, y + 5), fill=col)
    d.text((112, y), "SANIDADE", font=font(8), fill=C["bone"])
    # footprint counter
    d.ellipse((180 + 30, y, 186 + 30, y + 6), fill=C["m3"])
    d.text((222, y), "x%02d" % min(99, steps), font=font(8), fill=C["bone"])


def draw_handle(d):
    d.text((135, 84), "@terroremmatogrosso", font=font(8), fill=C["p4"], anchor="mt")


def caption_chunks(line, maxc=13):
    """group words into on-screen chunks (<= 2 lines of maxc chars)."""
    chunks, cur, curlen = [], [], 0
    for w in line["words"]:
        L = len(w["w"]) + (1 if cur else 0)
        brk = cur and (curlen + L > maxc * 2 - 2 or len(cur) >= 4)
        if brk:
            chunks.append(cur)
            cur, curlen = [], 0
            L = len(w["w"])
        cur.append(w)
        curlen += L
        if w["w"].endswith((".", "!", "?", "...", "…")) and len(cur) >= 1 and curlen > 6:
            chunks.append(cur)
            cur, curlen = [], 0
    if cur:
        chunks.append(cur)
    return chunks


def wrap(words, maxc):
    lines, cur = [], []
    for w in words:
        test = " ".join([x["w"] for x in cur + [w]])
        if cur and len(test) > maxc:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def norm_w(w):
    import unicodedata, re
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def draw_captions(img, t, tl, ycenter):
    if ycenter is None:
        return
    active = None
    for ln in tl["lines"]:
        if ln["id"] == "L07B":
            continue
        if ln["start"] - 0.05 <= t <= ln["start"] + ln["dur"] + 0.35:
            active = ln
    if not active:
        return
    chunks = caption_chunks(active)
    cur = None
    for ch in chunks:
        if t >= ch[0]["s"] - 0.08:
            cur = ch
    if cur is None:
        return
    if t > cur[-1]["e"] + 0.6 and cur is chunks[-1]:
        return
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    f = font(56)
    rows = wrap(cur, 15)
    lh = 84
    y0 = ycenter - (len(rows) - 1) * lh / 2
    for ri, row in enumerate(rows):
        text = " ".join(w["w"] for w in row)
        tw = d.textlength(text, font=f)
        x = (FW - tw) / 2
        y = y0 + ri * lh
        for w in row:
            seg = w["w"]
            on = t >= w["s"] - 0.03
            now = w["s"] - 0.03 <= t < w["e"] + 0.05
            col = C["yellow"] if now else (C["bone"] if on else (120, 110, 140))
            pop = -6 if now else 0
            d.text((x + 6, y + 8 + pop), seg, font=f, fill=C["k"], anchor="ls")
            d.text((x, y + pop), seg, font=f, fill=col, anchor="ls", stroke_width=6, stroke_fill=C["k"])
            x += d.textlength(seg + " ", font=f)


_post = {}


def post(frame, t, glitch=0.0, flash=0.0, chroma=0):
    if not _post:
        yy, xx = np.mgrid[0:FH, 0:FW].astype(np.float32)
        v = ((xx - FW / 2) / (FW / 2)) ** 2 + ((yy - FH / 2) / (FH / 2)) ** 2
        _post["vig"] = np.clip(1 - 0.32 * v ** 1.4, 0.35, 1)[..., None].astype(np.float32)
        scan = np.ones((FH, 1, 1), np.float32)
        scan[3::4] = 0.8
        scan[2::4] = 0.93
        _post["scan"] = scan
        r = rng(1)
        _post["grain"] = [(r.normal(0, 7, (FH // 2, FW // 2, 1))).astype(np.float32).repeat(2, 0).repeat(2, 1) for _ in range(6)]
    a = frame.astype(np.float32)
    if chroma:
        a[..., 0] = np.roll(a[..., 0], chroma, axis=1)
        a[..., 2] = np.roll(a[..., 2], -chroma, axis=1)
    a = a * _post["scan"] * _post["vig"] + _post["grain"][int(t * 30) % 6]
    if flash:
        a = a * (1 - flash) + np.array([230, 40, 50], np.float32) * flash
    return np.clip(a, 0, 255).astype(np.uint8)


def glitch_lowres(arr, t, amt):
    r = rng(int(t * 1000))
    out = arr.copy()
    n = int(4 + amt * 16)
    for _ in range(n):
        y = int(r.integers(0, H - 8))
        h = int(r.integers(2, 14))
        dx = int(r.integers(-30, 31) * amt)
        out[y:y + h] = np.roll(out[y:y + h], dx, axis=1)
    if amt > 0.4:
        for _ in range(int(amt * 6)):
            x, y = int(r.integers(0, W - 20)), int(r.integers(0, H - 10))
            out[y:y + int(r.integers(2, 8)), x:x + int(r.integers(8, 40))] = PAL[[0, 20, 24, 17][int(r.integers(0, 4))]]
    return out


# ---------------------------------------------------------------- frame assembly
class Ctx:
    def __init__(self, tl):
        self.tl = tl
        self.lines = {l["id"]: l for l in tl["lines"]}
        self.scene_by = {s["name"]: s for s in tl["scenes"]}

    def line_at(self, lid):
        return self.lines.get(lid)

    def word_at(self, lid, txt):
        ln = self.lines.get(lid)
        if not ln:
            return None
        for w in ln["words"]:
            if txt.lower() in w["w"].lower():
                return w
        return None


def sanity_at(t, cx):
    s = cx.scene_by
    pts = [(0, 1.0), (s["camp"]["start"], 1.0), (s["scream"]["start"], 0.85), (s["lantern"]["start"], 0.7),
           (s["lantern"]["end"], 0.35), (s["circletop"]["end"], 0.15), (s["raise"]["end"], 0.1),
           (s["jumpscare"]["start"] + 0.1, 0.0)]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return lerp(v0, v1, (t - t0) / max(1e-3, t1 - t0))
    return 0.0


def steps_at(t, cx, g):
    s = cx.scene_by
    if t < s["silhouette"]["start"]:
        return 0
    if t < s["footclose"]["start"]:
        return 1
    if t < s["circle"]["start"]:
        return 1 + int(t > s["footclose"]["start"] + 0.15 * (s["footclose"]["end"] - s["footclose"]["start"])) + int(
            t > s["footclose"]["start"] + 0.9 * (s["footclose"]["end"] - s["footclose"]["start"]))
    if t < s["camp"]["start"]:
        sc = s["circle"]
        return 3 + int(min(1, (t - sc["start"]) / ((sc["end"] - sc["start"]) * 0.7)) * 12)
    if t < s["circletop"]["start"]:
        return 15
    if t < s["circletop"]["end"]:
        return 15 + g.get("fcount", 0)
    return 64


def shake_at(t, cx):
    s = cx.scene_by
    amp = 0.0
    js = s["jumpscare"]
    if js["start"] <= t < js["end"]:
        amp = 9 * (1 - (t - js["start"]) / (js["end"] - js["start"])) + 2
    fc = s["footclose"]
    for k in (0.15, 0.9):
        st = fc["start"] + k * (fc["end"] - fc["start"])
        if st <= t < st + 0.35:
            amp = max(amp, 6 * (1 - (t - st) / 0.35))
    sl = cx.line_at("L07B")
    if sl and sl["start"] <= t < sl["start"] + sl["dur"]:
        amp = max(amp, 2.5)
    wn = cx.word_at("L00", "não")
    if wn and wn["s"] - 0.05 <= t < wn["s"] + 0.3:
        amp = max(amp, 5 * (1 - (t - wn["s"] + 0.05) / 0.35))
    lt = s["lantern"]
    if lt["start"] <= t < lt["end"]:
        amp = max(amp, 0.8)
    return amp


def render_frame(t, tl, cx):
    sc = None
    for s in tl["scenes"]:
        if s["start"] <= t < s["end"]:
            sc = s
    if sc is None:
        sc = tl["scenes"][-1]
    lt, dur = t - sc["start"], sc["end"] - sc["start"]
    g = {"t": t, "lines": tl["lines"], "line_at": cx.line_at, "word_at": cx.word_at}
    name = sc["name"]
    # loop: last 0.2s of 'continue' glitches into the hook frame
    if name == "continue" and dur - lt < 0.22:
        im = sc_hook(0.0, 2.0, g)
        name_eff = "hook"
    else:
        im = SCENE_FN[name](lt, dur, g)
        name_eff = name
    arr = quantize(im.convert("RGB"))
    # glitch transitions
    gl = 0.0
    if lt < 0.14 and name not in ("hook",):
        gl = 1 - lt / 0.14
    if name == "continue" and dur - lt < 0.3:
        gl = max(gl, 0.9)
    js = cx.scene_by["jumpscare"]
    if js["start"] <= t < js["start"] + 0.35:
        gl = max(gl, 0.8)
    if name == "scream" and cx.line_at("L07B") and abs(t - cx.line_at("L07B")["start"]) < 0.25:
        gl = max(gl, 0.6)
    if gl > 0:
        arr = glitch_lowres(arr, t, gl)
    amp = shake_at(t, cx)
    if amp > 0:
        r = rng(int(t * 997))
        arr = np.roll(arr, (int(r.integers(-amp, amp + 1)), int(r.integers(-amp, amp + 1))), axis=(0, 1))
    pim = Image.fromarray(arr)
    d = ImageDraw.Draw(pim)
    d.fontmode = "1"
    if name_eff in HUD_SCENES:
        draw_hud(d, sanity_at(t, cx), steps_at(t, cx, g), t)
    if name_eff not in ("title", "continue", "gameover", "jumpscare"):
        draw_handle(d)
    big = pim.resize((FW, FH), Image.NEAREST)
    capy = {"hook": 1290, "boss": 1880 - 200, "gameover": 1290, "continue": None, "title": None,
            "jumpscare": None}.get(name_eff, 1170)
    if name_eff == "boss":
        capy = 1520
    if name_eff == "gameover":
        capy = 1420
    if name_eff == "hook":
        # giant hook text
        d2 = ImageDraw.Draw(big)
        d2.fontmode = "1"
        wn = cx.word_at("L00", "não")
        if name != "continue":
            ln0 = cx.line_at("L00")
            top = [w for w in ln0["words"] if norm_w(w["w"]) not in ("nao", "responde")]
            rows = [top[:3], top[3:4], top[4:]]
            for ri, row in enumerate(rows):
                xs = " ".join(w["w"] for w in row)
                f = font(64)
                x = FW / 2 - d2.textlength(xs, font=f) / 2
                for w in row:
                    if t >= w["s"] - 0.12 or t < 0.02:
                        on = w["s"] - 0.12 <= t < w["e"] + 0.1
                        col = C["yellow"] if on else C["bone"]
                        d2.text((x + 6, 480 + ri * 96 + 6), w["w"], font=f, fill=C["k"], anchor="ls")
                        d2.text((x, 480 + ri * 96), w["w"], font=f, fill=col, anchor="ls", stroke_width=7, stroke_fill=C["k"])
                    x += d2.textlength(w["w"] + " ", font=f)
        if name != "continue" and wn and t >= wn["s"] - 0.05:
            r = rng(int(t * 20))
            jx, jy = r.integers(-4, 5), r.integers(-4, 5)
            d2.text((FW / 2 + jx + 8, 1400 + jy + 8), "NÃO", font=font(160), fill=C["k"], anchor="mm")
            d2.text((FW / 2 + jx, 1400 + jy), "NÃO", font=font(160), fill=C["red"], anchor="mm", stroke_width=10, stroke_fill=C["k"])
            d2.text((FW / 2 + jx, 1570 + jy), "RESPONDE", font=font(96), fill=C["red"], anchor="mm", stroke_width=10, stroke_fill=C["k"])
        capy = None
    if name != "continue" or dur - lt >= 0.22:
        draw_captions(big, t, tl, capy)
    flash = 0.0
    if js["start"] <= t < js["start"] + 0.25:
        flash = 0.55 * (1 - (t - js["start"]) / 0.25)
    out = post(np.asarray(big), t, flash=flash, chroma=int(gl * 6) * S // 2 if gl > 0 else (2 if amp > 3 else 0))
    return out


_TL = None


def _init():
    global _TL, _CX
    init_layers()
    _TL = json.load(open(os.path.join(TL.BUILD, "timing.json")))
    _CX = Ctx(_TL)


def _work(i):
    if _TL is None:
        _init()
    return render_frame(i / TL.FPS, _TL, _CX).tobytes()


def render(out, t0=0.0, t1=None, workers=4, audio=None, crf=20):
    from multiprocessing import Pool
    tl = json.load(open(os.path.join(TL.BUILD, "timing.json")))
    t1 = t1 if t1 is not None else tl["total"]
    frames = range(int(round(t0 * TL.FPS)), int(round(t1 * TL.FPS)))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{FW}x{FH}",
           "-r", str(TL.FPS), "-i", "-"]
    if audio:
        cmd += ["-ss", str(t0), "-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-maxrate", "16M", "-bufsize", "32M", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers, initializer=_init) as pool:
        for k, buf in enumerate(pool.imap(_work, frames, chunksize=4)):
            p.stdin.write(buf)
            if k % 150 == 0:
                print("frame", k, "/", len(frames), flush=True)
    p.stdin.close()
    p.wait()


def still(t, path):
    _init()
    Image.fromarray(render_frame(t, _TL, _CX)).save(path)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--t0", type=float, default=0)
    ap.add_argument("--t1", type=float)
    ap.add_argument("--audio")
    a = ap.parse_args()
    if a.still is not None:
        for t in a.still:
            still(t, os.path.join(TL.BUILD, "still_%05.2f.png" % t))
    else:
        render(a.out, a.t0, a.t1, audio=a.audio)


def thumbnail(path):
    init_layers()
    im = forest_base(300, 0)
    creature(im, 140, 372, 220, 0.5, eye=1.0, rim=C["p4"])
    scroll(im, K.trees_near, 300)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 380, W, H), fill=C["m0"])
    footprint(d, 70, 430, 26, water=True)
    d.ellipse((52, 424, 88, 436), fill=C["s1"])
    footprint(d, 200, 400, 14, water=True)
    man2(im, 230, 452, 0, -1, lantern=True)
    im = fog_overlay(im, 0, 0.6, 260, 440)
    im = light(im, [(205, 150, 150, 0.35), (140, 372 - 220 * 0.9, 40, 0.9)], ambient=0.75, warm=(220, 60, 70))
    arr = quantize(im.convert("RGB"))
    big = Image.fromarray(arr).resize((FW, FH), Image.NEAREST)
    d = ImageDraw.Draw(big)
    d.fontmode = "1"
    def t(y, s, size, col, stroke=10):
        d.text((FW / 2 + 10, y + 10), s, font=font(size), fill=C["k"], anchor="mm")
        d.text((FW / 2, y), s, font=font(size), fill=col, anchor="mm", stroke_width=stroke, stroke_fill=C["k"])
    t(300, "SE OUVIR ESSE", 56, C["bone"], 8)
    t(390, "ASSOBIO...", 80, C["bone"], 8)
    t(1380, "NÃO", 160, C["red"])
    t(1540, "RESPONDE", 96, C["red"])
    t(1680, "A LENDA DO PÉ DE GARRAFA", 32, C["yellow"], 6)
    d.text((FW / 2, 210), "@terroremmatogrosso", font=font(32), fill=C["p4"], anchor="mm")
    Image.fromarray(post(np.asarray(big), 0.0)).save(path)
