"""CELSO: A VINGANÇA DO PARQUE — render do vídeo vertical 1080x1920 @30fps.

Uso:
  python3 src/render.py --preview          # frames-chave em output/previews/
  python3 src/render.py                    # vídeo final em output/
  python3 src/render.py --frames 0:300     # trecho (frames) para testes

O jogo é desenhado numa tela nativa de 270x480 (pixel art) e ampliada 4x
com nearest-neighbor; depois passa pelo filtro CRT (curvatura, scanlines,
aberração cromática, bloom, ruído) e recebe as legendas nítidas por cima.
"""
import argparse
import math
import os
import random
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fonte  # noqa: E402
import timeline as T  # noqa: E402
from timeline import clamp, ease_io, ease_out, ease_out_bounce, lerp_keys  # noqa: E402

ROOT = T.ROOT
ASSETS = T.ASSETS
GEN = os.path.join(ASSETS, 'gerados')
OUTDIR = os.path.join(ROOT, 'output')
W, H = 270, 480          # mundo (cenário em pixels nativos)
VW, VH = 180, 320        # janela da câmera (tela do "jogo")
VX, VY = 40, 112         # recorte da janela dentro do mundo
S = 6
FW, FH = VW * S, VH * S  # 1080 x 1920
TILE_W = 540

RED = (255, 42, 42)
DRED = (110, 0, 10)
YEL = (255, 214, 64)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (60, 230, 80)


# ======================================================================= assets
def asset_path(name):
    """Usa o PNG do usuário em assets/ se existir; senão o gerado."""
    p = os.path.join(ASSETS, name)
    return (p, True) if os.path.exists(p) else (os.path.join(GEN, name), False)


def key_chroma(a):
    """RGBA uint8 -> alpha 0 onde é verde chroma."""
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    green = (g > 140) & (g - np.maximum(r, b) > 70)
    a = a.copy()
    a[green, 3] = 0
    return a


def load_sheet(name, rows, cols, fw, fh, chroma=True):
    path, user = asset_path(name)
    im = Image.open(path).convert('RGBA')
    cw, ch = im.width / cols, im.height / rows
    frames = []
    for r in range(rows):
        for c in range(cols):
            cell = im.crop((round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch)))
            cell = cell.resize((fw, fh), Image.NEAREST)
            a = np.array(cell)
            if chroma:
                a = key_chroma(a)
            frames.append(a)
    return frames, user


def make_sprite(a):
    return {'rgb': a[..., :3].astype(np.float32), 'mask': a[..., 3] > 127,
            'h': a.shape[0], 'w': a.shape[1], 'raw': a}


class Layers:
    """Camadas de parallax (dia/noite). Usa camadas geradas ou fatia o PNG do usuário."""
    FACT = {'ceu': 0.1, 'predios': 0.25, 'arvores': 0.45, 'lagoa': 0.6, 'chao': 1.0}

    def __init__(self, night):
        name = 'bg_noite.png' if night else 'bg_dia.png'
        user_p = os.path.join(ASSETS, name)
        self.layers = []
        if os.path.exists(user_p):
            im = Image.open(user_p).convert('RGB')
            ar = im.width / im.height
            if ar > 9 / 16:
                nw = int(im.height * 9 / 16)
                im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
            else:
                nh = int(im.width * 16 / 9)
                im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
            a = np.array(im.resize((W, H), Image.NEAREST))
            tile = np.concatenate([a, a[:, ::-1]], 1)           # espelhado = emenda perfeita
            bands = [(0, int(H * 0.36), 0.1), (int(H * 0.36), int(H * 0.55), 0.45), (int(H * 0.55), H, 1.0)]
            for y0, y1, f in bands:
                m = np.zeros((H, TILE_W), bool)
                m[y0:y1] = True
                self.layers.append(('faixa', f, np.concatenate([tile, tile], 1), np.concatenate([m, m], 1)))
            self.user = True
        else:
            d = os.path.join(GEN, 'camadas_' + ('noite' if night else 'dia'))
            for k in ('ceu', 'predios', 'arvores', 'lagoa', 'chao'):
                a = np.array(Image.open(os.path.join(d, k + '.png')).convert('RGBA'))
                if a.shape[0] < H:
                    a = np.concatenate([a, np.zeros((H - a.shape[0], a.shape[1], 4), np.uint8)], 0)
                rgb = np.concatenate([a[..., :3], a[..., :3]], 1)
                m = np.concatenate([a[..., 3] > 0, a[..., 3] > 0], 1)
                self.layers.append((k, self.FACT[k], rgb, m))
            self.user = False

    def draw(self, canvas, cam_x, t, shimmer=True):
        for name, f, rgb, m in self.layers:
            off = int(math.floor(cam_x * f)) % TILE_W
            sl = rgb[:, off:off + W]
            ml = m[:, off:off + W]
            np.copyto(canvas, sl, where=ml[..., None])
            if name == 'lagoa' and shimmer:
                for y in range(200, 262, 2):
                    s = int(round(math.sin(t * 1.7 + y * 0.55)))
                    if s:
                        canvas[y] = np.roll(canvas[y], s, 0)


class Assets:
    def __init__(self):
        cel, self.user_celso = load_sheet('celso_sheet.png', 1, 6, 128, 64)
        self.celso = [make_sprite(a) for a in cel]
        # variante "respirando": metade de cima sobe 1px
        a = cel[0].copy()
        a[:-8] = cel[0][1:-7]
        self.celso_breath = make_sprite(a)
        vis, self.user_vis = load_sheet('visitantes_sheet.png', 2, 11, 32, 48)
        self.visA = [make_sprite(a) for a in vis[:11]]
        self.visB = [make_sprite(a) for a in vis[11:]]
        cap, _ = load_sheet('capivara_sheet.png', 1, 3, 32, 20)
        self.capy = [make_sprite(a) for a in cap]
        js, _ = load_sheet('celso_jumpscare.png', 1, 2, VW, VH, chroma=False)
        self.jump = [make_sprite(a) for a in js]
        self.day = Layers(False)
        self.night = Layers(True)
        self.text_cache = {}
        rng = np.random.RandomState(3)
        # neblina: textura de ruído suave repetível
        n = rng.rand(24, 72)
        n = np.kron(n, np.ones((4, 8)))
        for _ in range(3):
            n = (n + np.roll(n, 1, 0) + np.roll(n, -1, 0) + np.roll(n, 2, 1) + np.roll(n, -2, 1)) / 5
        n = (n - n.min()) / (n.max() - n.min())
        self.fog = np.tile(n, (1, 2))            # 96 x 1152
        self.stars = [(rng.randint(0, W), rng.randint(0, 300), rng.rand()) for _ in range(90)]

    def text(self, s, color=WHITE, scale=1, outline=BLACK, shadow=None):
        k = (s, color, scale, outline, shadow)
        if k not in self.text_cache:
            self.text_cache[k] = fonte.render(s, color, scale, outline, 1, shadow)
        return self.text_cache[k]


# ======================================================================= desenho
def blit(canvas, spr, x, y, flip=False, tint=None, glow_eyes=False, alpha=1.0):
    """Desenha sprite (dict de make_sprite) em canvas float32 HxWx3."""
    x, y = int(round(x)), int(round(y))
    rgb, m = spr['rgb'], spr['mask']
    if flip:
        rgb, m = rgb[:, ::-1], m[:, ::-1]
    h, w = m.shape
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.shape[1], x + w), min(canvas.shape[0], y + h)
    if x0 >= x1 or y0 >= y1:
        return
    sr = rgb[y0 - y:y1 - y, x0 - x:x1 - x]
    sm = m[y0 - y:y1 - y, x0 - x:x1 - x]
    if tint is not None:
        out = sr * np.array(tint, np.float32)
        if glow_eyes:
            r, g, b = sr[..., 0], sr[..., 1], sr[..., 2]
            eye = ((r > 190) & (g < 110)) | ((r > 200) & (g > 160) & (b < 90))
            out[eye] = (255, 40, 30)
        sr = out
    reg = canvas[y0:y1, x0:x1]
    if alpha >= 1:
        np.copyto(reg, sr, where=sm[..., None])
    else:
        reg[sm] = reg[sm] * (1 - alpha) + sr[sm] * alpha


def blit_rgba(canvas, a, x, y, alpha=1.0):
    """Desenha imagem RGBA uint8 (texto) em canvas float32."""
    x, y = int(round(x)), int(round(y))
    h, w = a.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.shape[1], x + w), min(canvas.shape[0], y + h)
    if x0 >= x1 or y0 >= y1:
        return
    sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
    m = sub[..., 3] > 0
    reg = canvas[y0:y1, x0:x1]
    if alpha >= 0.999:
        np.copyto(reg, sub[..., :3].astype(canvas.dtype), where=m[..., None])
    else:
        reg[m] = reg[m] * (1 - alpha) + sub[..., :3][m].astype(canvas.dtype) * alpha


def text_center(cv, A, s, y, color=WHITE, scale=1, outline=BLACK, shadow=None, alpha=1.0, cx=W / 2):
    img = A.text(s, color, scale, outline, shadow)
    blit_rgba(cv, img, cx - img.shape[1] / 2, y, alpha)
    return img.shape


def rect(cv, x0, y0, x1, y1, col, alpha=1.0):
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(cv.shape[1], int(x1)), min(cv.shape[0], int(y1))
    if x0 < x1 and y0 < y1:
        if alpha >= 1:
            cv[y0:y1, x0:x1] = col
        else:
            cv[y0:y1, x0:x1] = cv[y0:y1, x0:x1] * (1 - alpha) + np.array(col, np.float32) * alpha


def px(cv, x, y, col, add=False):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < cv.shape[1] and 0 <= y < cv.shape[0]:
        if add:
            cv[y, x] = np.minimum(255, cv[y, x] + np.array(col, np.float32))
        else:
            cv[y, x] = col


BAYER8 = np.array([[0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
                   [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
                   [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
                   [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21]]) / 64.0


def dither_mask(amount, block=3, sweep=None):
    """Máscara de dissolução pixelada (True = mostra o novo). sweep='down' varre de cima p/ baixo."""
    by, bx = np.mgrid[0:VH, 0:VW]
    th = BAYER8[(by // block) % 8, (bx // block) % 8]
    if sweep == 'down':
        th = th * 0.45 + (by / VH) * 0.55
    return th < amount


# ---------------------------------------------------------------- elementos do parque
def night_tint(x_screen, lamps_lit, base=(0.42, 0.40, 0.62)):
    light = 0.0
    for lx, st in lamps_lit:
        if st > 0:
            light += st * clamp(1 - abs(x_screen - lx) / 34)
    light = clamp(light)
    return (base[0] + light * 0.62, base[1] + light * 0.52, base[2] + light * 0.18)


def draw_lamps(cv, cam_x, tb, night, states=None):
    """Postes ao longo da pista. Retorna [(x_tela, estado)] para iluminação."""
    out = []
    k0 = int((cam_x - 30) // T.LAMP_SPACING)
    for k in range(k0, k0 + 6):
        x = T.lamp_x(k) - cam_x
        if x < -30 or x > W + 30:
            continue
        st = 0.0
        if night:
            st = states(k) if states else 1.0
        xi = int(round(x))
        pole = (40, 40, 52) if night else (70, 74, 84)
        rect(cv, xi, 228, xi + 2, 281, pole)
        rect(cv, xi - 1, 279, xi + 3, 282, (30, 30, 40) if night else (60, 60, 70))
        rect(cv, xi, 226, xi + 9, 228, pole)
        head = (255, 244, 190) if st > 0.6 else ((150, 140, 110) if st > 0 else (60, 60, 70) if night else (200, 205, 215))
        rect(cv, xi + 6, 228, xi + 11, 230, head)
        if st > 0:
            cx = xi + 8
            # halo e cone de luz sobre a pista (aditivo)
            for (r, a) in ((7, 0.18), (4, 0.3)):
                y0, y1 = 229 - r, 229 + r
                x0, x1 = cx - r, cx + r
                rect_add(cv, x0, y0, x1, y1, (255 * a * st, 230 * a * st, 150 * a * st))
            for y in range(231, 301):
                u = (y - 231) / 70
                half = 2 + u * 20
                a = (0.22 * (1 - u * 0.4)) * st
                xs0, xs1 = int(cx - half), int(cx + half)
                # dithering nas bordas do cone
                rect_add(cv, xs0 + 2, y, xs1 - 2, y + 1, (255 * a, 225 * a, 140 * a))
                if y % 2 == 0:
                    rect_add(cv, xs0, y, xs0 + 2, y + 1, (255 * a * .5, 225 * a * .5, 140 * a * .5))
                    rect_add(cv, xs1 - 2, y, xs1, y + 1, (255 * a * .5, 225 * a * .5, 140 * a * .5))
        out.append((x + 8, st))
    return out


def rect_add(cv, x0, y0, x1, y1, col):
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(cv.shape[1], int(x1)), min(cv.shape[0], int(y1))
    if x0 < x1 and y0 < y1:
        cv[y0:y1, x0:x1] = np.minimum(255, cv[y0:y1, x0:x1] + np.array(col, np.float32))


SHOW_COLS = [(255, 40, 60), (255, 40, 220), (40, 230, 255), (255, 200, 40), (120, 80, 255)]


def fountain_x(cam_x):
    off = math.floor(cam_x * 0.6) % TILE_W
    return [270 + k * TILE_W - off for k in (-1, 0, 1) if -80 < 270 + k * TILE_W - off < W + 80]


def draw_fountain(cv, cam_x, t, mode='day', show=0.0, red=0.0):
    """mode: day | night. show: 0..1 intensidade do Show das Águas. red: 0..1 tudo vermelho."""
    for fx in fountain_x(cam_x):
        by = 226
        jets = [(0, 34 + 5 * math.sin(t * 2.1), 0), (-1, 16, 1), (1, 16, 2), (-2, 11, 3), (2, 11, 4)]
        if mode == 'night' and show > 0:
            jets = [(0, 44 + 10 * math.sin(t * 3.0), 0), (-1, 22 + 6 * math.sin(t * 2.3), 1), (1, 22 + 6 * math.sin(t * 2.3 + 1), 2),
                    (-2, 15 + 5 * math.sin(t * 4), 3), (2, 15 + 5 * math.sin(t * 4 + 2), 4), (-3, 9, 0), (3, 9, 1)]
        for (side, hgt, ci) in jets:
            if mode == 'night' and show > 0:
                c = SHOW_COLS[(ci + int(t * 1.6)) % len(SHOW_COLS)]
                c = tuple(c[i] * (1 - red) + (255, 30, 25)[i] * red for i in range(3))
                inten = show * (0.75 + 0.25 * math.sin(t * 9 + ci))
                col = tuple(v * inten for v in c)
            elif mode == 'night':
                col = (60, 70, 110)
            else:
                col = (235, 245, 255)
            spread = side * 13
            n = int(10 + hgt * 0.8)
            for i in range(n):
                u = ((i / n) + t * 0.9) % 1.0
                if side == 0:
                    x = fx + math.sin(u * 20 + t * 5) * 0.6
                    y = by - hgt * (1 - (1 - u) ** 2) if u < 0.75 else by - hgt * (1 - (1 - 0.75) ** 2) + (u - 0.75) * hgt * 2.2
                    x += (u > 0.75) * (i % 3 - 1) * (u - 0.75) * 20
                else:
                    x = fx + spread * u
                    y = by - 4 * hgt * u * (1 - u) * 1.0
                if mode == 'night' and show > 0:
                    px(cv, x, y, col, add=True)
                    px(cv, x + 1, y, tuple(v * 0.35 for v in col), add=True)
                    px(cv, x - 1, y, tuple(v * 0.35 for v in col), add=True)
                    px(cv, x, y + 1, tuple(v * 0.25 for v in col), add=True)
                else:
                    px(cv, x, y, col)
        # espuma na base
        for i in range(10):
            ang = i / 10 * math.pi * 2 + t * 2
            px(cv, fx + math.cos(ang) * 10, by + 1 + math.sin(ang) * 1.5,
               (255, 255, 255) if mode == 'day' else (120, 110, 160))
        if mode == 'night' and show > 0:
            # reflexo colorido na água
            for y in range(232, 262):
                if (y + int(t * 8)) % 3 == 0:
                    continue
                c = SHOW_COLS[(y // 4 + int(t * 1.6)) % len(SHOW_COLS)]
                c = tuple(c[i] * (1 - red) + (255, 30, 25)[i] * red for i in range(3))
                a = 0.35 * show * (1 - (y - 232) / 34)
                wv = int(8 + 3 * math.sin(y * 0.8 + t * 4))
                rect_add(cv, fx - wv, y, fx + wv, y + 1, tuple(v * a for v in c))
            # brilho geral na lagoa
            glow = (1 - red) * np.array(SHOW_COLS[int(t * 1.6) % 5], np.float32) + red * np.array((255, 30, 25), np.float32)
            rect_add(cv, fx - 60, 200, fx + 60, 262, tuple(glow * 0.06 * show))


def draw_fog(cv, A, t, amount, y0=196, y1=292, color=(150, 130, 190)):
    if amount <= 0:
        return
    h = y1 - y0
    off = int(t * 10) % 576
    f = A.fog[:h, off:off + W]
    f2 = A.fog[(np.arange(h) + 30) % A.fog.shape[0]][:, (off * 2 + 100) % 576:(off * 2 + 100) % 576 + W]
    if f2.shape[1] < W:
        f2 = A.fog[:h, :W]
    fog = (f * 0.6 + f2 * 0.4)
    prof = np.sin(np.linspace(0, math.pi, h))[:, None]
    a = clamp(amount) * 0.55 * fog * prof
    # quantiza em degraus (visual 16-bit)
    a = np.floor(a * 6) / 6
    cv[y0:y1] = cv[y0:y1] * (1 - a[..., None]) + np.array(color, np.float32) * a[..., None]


def draw_hud(cv, A, tb, patience, heart_n=3, distance=None, blink_red=False):
    """HUD em coordenadas da janela (180x320)."""
    y = 44
    rect(cv, 0, y - 3, VW, y + (36 if distance is not None else 25), (0, 0, 0), 0.6)
    rect(cv, 0, y + (36 if distance is not None else 25), VW, y + (37 if distance is not None else 26), (90, 90, 120), 0.6)
    img = A.text('CELSO', WHITE, 1)
    blit_rgba(cv, img, 5, y)
    hx = 5 + img.shape[1] + 1
    for i in range(3):
        h = A.text('♥', RED if i < heart_n else (70, 70, 70), 1)
        blit_rgba(cv, h, hx + i * 9, y)
    if distance is not None:
        col = RED if distance < 5 else YEL
        on = not (distance < 5 and int(tb * 8) % 2)
        lab = A.text('DISTÂNCIA', WHITE, 1)
        blit_rgba(cv, lab, VW - 5 - lab.shape[1], y)
        val = A.text('%04.1fm' % max(0, distance), col if on else (120, 0, 0), 2)
        blit_rgba(cv, val, VW - 5 - val.shape[1], y + 11)
        lab2 = A.text('PACIÊNCIA 0%', RED if int(tb * 4) % 2 else (140, 20, 20), 1)
        blit_rgba(cv, lab2, 5, y + 13)
        return
    lab = A.text('PACIÊNCIA %d%%' % round(patience * 100), WHITE, 1)
    blit_rgba(cv, lab, VW - 5 - lab.shape[1], y)
    bx0, bx1, by = 92, VW - 6, y + 13
    rect(cv, bx0 - 1, by - 1, bx1 + 1, by + 7, (230, 230, 230))
    rect(cv, bx0, by, bx1, by + 6, (20, 20, 20))
    if patience > 0.6:
        col = (60, 220, 80)
    elif patience > 0.3:
        col = (250, 200, 40)
    else:
        col = (240, 40, 40)
    if blink_red and int(tb * 6) % 2:
        col = (120, 10, 10)
    fill = int((bx1 - bx0) * clamp(patience))
    rect(cv, bx0, by, bx0 + fill, by + 6, col)
    rect(cv, bx0, by, bx0 + fill, by + 2, tuple(min(255, c + 60) for c in col))
    for x in range(bx0 + 7, bx1, 8):
        rect(cv, x, by, x + 1, by + 6, (0, 0, 0), 0.5)


def draw_splash(cv, t0, tb, x, y, n=40, seed=1):
    dt = tb - t0
    if dt < 0 or dt > 1.6:
        return
    rng = random.Random(seed)
    for i in range(n):
        vx = rng.uniform(-45, 45)
        vy = rng.uniform(-110, -40)
        xx = x + vx * dt
        yy = y + vy * dt + 160 * dt * dt
        if yy < y + 4:
            px(cv, xx, yy, (230, 245, 255) if i % 3 else (140, 200, 255))
    for k in range(3):
        r = (dt - k * 0.2) * 40
        if r > 0:
            a = clamp(1 - r / 60)
            for ang in np.linspace(0, math.pi * 2, 48, endpoint=False):
                px(cv, x + math.cos(ang) * r, y + math.sin(ang) * r * 0.22, (200 * a + 40, 230 * a + 20, 255 * a))


def draw_heart(cv, A, x, y, t):
    if t < 0 or t > 1.8:
        return
    yy = y - t * 18
    a = 1 if t < 1.2 else 1 - (t - 1.2) / 0.6
    img = A.text('♥', (255, 90, 140), 2 if int(t * 6) % 2 == 0 or t > 0.4 else 1, BLACK)
    blit_rgba(cv, img, x - img.shape[1] / 2, yy, a)


def draw_zzz(cv, A, x, y, t):
    for k in range(3):
        u = ((t * 0.5) + k / 3) % 1
        img = A.text('z' if k % 2 else 'Z', (220, 230, 255), 1, BLACK)
        blit_rgba(cv, img, x + u * 10 + math.sin(u * 6) * 2, y - u * 22, 1 - u)


def draw_eyes_in_water(cv, A, x, y, tb, scale_glow=1.0):
    spr = A.celso[5]
    blit(cv, spr, x, y, tint=(0.55, 0.5, 0.7), glow_eyes=True)
    # brilho dos olhos (halo aditivo)
    m = spr['mask']
    rgb = spr['rgb']
    eye = m & (rgb[..., 0] > 190) & (rgb[..., 1] < 110)
    ys, xs = np.nonzero(eye)
    pul = 0.6 + 0.4 * math.sin(tb * 6)
    for yy, xx in zip(ys[::2], xs[::2]):
        rect_add(cv, x + xx - 2, y + yy - 2, x + xx + 3, y + yy + 3, (60 * pul * scale_glow, 6, 4))


def park_scene(cv, A, cam_x, tb, night=False, show=0.0, red=0.0, fog=0.0, lamp_fn=None):
    L = A.night if night else A.day
    L.draw(cv, cam_x, tb)
    if night:
        # estrelas piscando
        for (x, y, ph) in A.stars:
            if y < 170 and math.sin(tb * 3 + ph * 20) > 0.6:
                px(cv, x, y, (255, 255, 255))
        if red > 0:
            rect_add(cv, 0, 120, W, 200, (40 * red, 0, 4 * red))
    draw_fountain(cv, cam_x, tb, 'night' if night else 'day', show, red)
    if fog > 0:
        draw_fog(cv, A, tb, fog)
    lamps = draw_lamps(cv, cam_x, tb, night, lamp_fn)
    return lamps


# ======================================================================= cenas
# Coordenadas: o cenário e os personagens são desenhados no MUNDO (270x480)
# e depois recortados pela janela da câmera (VX,VY,180x320). Textos de tela
# (HUD, cartões, GAME OVER) são desenhados direto na janela.
CELSO_GROUND = 280     # y da linha de chão do Celso na margem (frame G=58)
VIS_GROUND = 290       # pés dos visitantes na pista (frame G=46)
CAM_L1_END = 70


def world():
    return np.zeros((H, W, 3), np.float32)


def crop(cv, wc, dy=0):
    cv[:] = wc[VY + dy:VY + dy + VH, VX:VX + VW]


def fit_scale(A, s, max_w, pref):
    for sc in range(pref, 0, -1):
        if fonte.text_width(s) * sc + 2 * sc <= max_w:
            return sc
    return 1


def title_text(cv, A, s, y, color, pref, shadow=DRED, alpha=1.0):
    sc = fit_scale(A, s, VW - 8, pref)
    return text_center(cv, A, s, y, color, sc, BLACK, shadow, alpha, cx=VW / 2)


def walk_cycle(t, fps=8):
    return [0, 1, 2, 1][int(t * fps) % 4]


def scene_title(cv, A, tb, post):
    cv[:] = (4, 2, 10)
    for (x, y, ph) in A.stars:
        if math.sin(tb * 2.5 + ph * 30) > -0.3 and x < VW:
            px(cv, x, y * 0.6 + 20, (180, 170, 230))
    for y in range(200, 236):
        k = (y - 200) / 36
        rect(cv, 0, y, VW, y + 1, (70 * k + 6, 6, 20 * (1 - k) + 6))
    rect(cv, 0, 236, VW, VH, (6, 6, 22))
    for y in range(238, 300, 3):
        for x in range((y * 7) % 11, VW, 13):
            rect(cv, x, y, x + 4, y + 1, (20, 18, 50))
    draw_eyes_in_water(cv, A, 10, 236 - 52 + 2, tb)
    blit_rgba(cv, A.text('1UP 000000', RED, 1), 6, 44)
    hi = A.text('HI 999999', WHITE, 1)
    blit_rgba(cv, hi, VW - 6 - hi.shape[1], 44)
    drop = ease_out_bounce(tb / 0.9)
    y0 = -80 + (74 + 80) * drop
    blink = int(tb * 5) % 2 == 0
    c1 = RED if blink else (190, 10, 20)
    title_text(cv, A, 'CELSO:', y0, c1, 5)
    title_text(cv, A, 'A VINGANÇA', y0 + 60, c1, 3)
    title_text(cv, A, 'DO PARQUE', y0 + 92, c1, 3)
    if tb > 0.9:
        a = clamp((tb - 0.9) / 0.3)
        title_text(cv, A, 'PARQUE DAS ÁGUAS', 206, YEL, 1, None, a)
        title_text(cv, A, '– CUIABÁ/MT –', 218, YEL, 1, None, a)
    on = ((tb % 0.8) < 0.5) if tb < 4.0 else (int(tb * 15) % 2 == 0)
    if on and tb > 1.0:
        title_text(cv, A, 'PRESS START', 186, WHITE, 2, (60, 60, 60))
    credit = 'CREDIT 1' if tb >= 3.6 else 'CREDIT 0'
    title_text(cv, A, credit, 268, (200, 200, 200), 1, None)
    title_text(cv, A, '© 1987 TERROR EM MT', 280, (140, 140, 160), 1, None)
    if tb > 4.6:
        m = dither_mask((tb - 4.6) / 0.4, 4)
        cv[m] = 0


def celso_idle_sprite(A, tb):
    return A.celso_breath if (tb % 2.4) > 1.2 else A.celso[0]


CAPY_STOP = 196        # x no mundo onde a capivara para (na frente do Celso)
CAPY_GROUND = 287


def scene_level1(cv, A, tb, post):
    cam = CAM_L1_END * ease_io((tb - 5.2) / 8.8)
    wc = world()
    park_scene(wc, A, cam, tb)
    cx = 155 - cam
    blit(wc, celso_idle_sprite(A, tb), cx, CELSO_GROUND - 58)
    if tb > 6.0:
        draw_zzz(wc, A, cx + 108, CELSO_GROUND - 26, tb)
    if tb >= 7.0:
        wx = max(CAPY_STOP, 330 - (tb - 7.0) * 34)
        moving = wx > CAPY_STOP
        fr = A.capy[int(tb * 7) % 2] if moving else A.capy[2]
        blit(wc, fr, wx - cam, CAPY_GROUND - 20, flip=True)
        if not moving:
            t_stop = 7.0 + (330 - CAPY_STOP) / 34
            draw_heart(wc, A, CAPY_STOP - cam + 4, CAPY_GROUND - 22, tb - t_stop - 0.2)
    crop(cv, wc)
    if tb > 5.6:
        draw_hud(cv, A, tb, 1.0)
    if 5.3 < tb < 7.6:
        title_text(cv, A, 'LEVEL 1', 80, WHITE, 3, (40, 40, 90))
        title_text(cv, A, '– DIA –', 106, YEL, 2, (90, 60, 0))
    if tb < 5.6:
        m = ~dither_mask((tb - 5.0) / 0.6, 4)
        cv[m] = 0


def scene_puxao(cv, A, tb, post):
    cam = CAM_L1_END
    wc = world()
    park_scene(wc, A, cam, tb)
    cel_x = 155 - cam
    freeze0, freeze1 = 19.5, 20.4
    tf = tb if not (freeze0 <= tb < freeze1) else freeze0
    cel_fr = A.celso[0]
    yank = -2 if 19.25 <= tf <= freeze0 else 0
    if tb >= freeze0:
        cel_fr = A.celso[3]
    if tb >= freeze1:
        cel_fr = A.celso[4] if (tb < 22.0 or 22.6 < tb < 23.2) else A.celso[3]
    celso_gone = tb >= 24.05
    cy = CELSO_GROUND - 58
    if tb >= 23.2 and not celso_gone:
        u = (tb - 23.2) / 0.85
        cel_fr = A.celso[1 + int(tb * 10) % 2]
        cel_x += 10 * u
        cy -= 12 * u
    if not celso_gone:
        if tb < 16.8:
            blit(wc, celso_idle_sprite(A, tb), cel_x, cy)
        else:
            blit(wc, cel_fr, cel_x + yank, cy)
    else:
        draw_eyes_in_water(wc, A, cel_x + 10, 196 + 14, tb)
    draw_splash(wc, 24.0, tb, cel_x + 70, 262, 60, 5)
    if tb < 16.0:
        draw_zzz(wc, A, cel_x + 108, CELSO_GROUND - 26, tb)
    # capivara foge quando os visitantes chegam
    cap_x = CAPY_STOP - cam
    if tb < 16.6:
        blit(wc, A.capy[2], cap_x, CAPY_GROUND - 20, flip=True)
    else:
        u = tb - 16.6
        blit(wc, A.capy[int(tb * 12) % 2], cap_x + u * 75, CAPY_GROUND - 20)
    # visitantes
    stopA, stopB = 67, 44
    speed = 30
    for who, start, stop in (('B', 0, stopB), ('A', 22, stopA)):
        spr_set = A.visA if who == 'A' else A.visB
        t0 = 15.3
        x = min(stop, start + (tf - t0) * speed)
        arrived_t = t0 + (stop - start) / speed
        if tf < arrived_t:
            fr = walk_cycle(tf - t0)
        elif who == 'A' and tf >= 18.85:
            fr = 3
        else:
            fr = 4 + int(tf * 6) % 2
        flip = False
        if tb >= freeze1:
            u = tb - freeze1 - (0.15 if who == 'A' else 0.0)
            if u < 0:
                fr = 9
            else:
                x = stop - u * (85 if who == 'A' else 95)
                fr = [6, 7, 8, 7][int(u * 12) % 4] if (u % 1.0) < 0.7 else 9 + int(u * 8) % 2
                flip = fr < 9
        if who == 'A' and tf >= 19.25 and tb < freeze1:
            x -= 2
        blit(wc, spr_set[fr], x, VIS_GROUND - 46, flip=flip)
        if fr in (4, 5) and tb < freeze0 and int(tf * 3) % 2 == 0:
            img = A.text('HA HA', WHITE, 1, BLACK)
            blit_rgba(wc, img, x + 2 + (0 if who == 'A' else -6), VIS_GROUND - 60 - (0 if who == 'A' else 8))
    if tb >= freeze0 and tb < 22.6:
        pop = ease_out_bounce((tb - freeze0) / 0.35)
        img = A.text('!!', RED, 3, BLACK, (90, 0, 0))
        blit_rgba(wc, img, cel_x + 104 - img.shape[1] / 2, CELSO_GROUND - 40 - img.shape[0] * pop)
    crop(cv, wc)
    pat = 1.0 if tb < freeze0 + 0.1 else 1 - ease_out((tb - (freeze0 + 0.1)) / 1.0)
    draw_hud(cv, A, tb, pat, blink_red=pat <= 0.01)
    if 20.8 <= tb < 24.9:
        msg1, msg2 = 'VOCÊ IRRITOU O', 'MORADOR ERRADO.'
        n = int((tb - 20.8) * 22)
        s1, s2 = msg1[:n], msg2[:max(0, n - len(msg1))]
        col = RED if int(tb * 6) % 3 else (255, 120, 120)
        sc = fit_scale(A, msg2, VW - 6, 2)
        if s1:
            text_center(cv, A, s1, 78, col, sc, BLACK, DRED, cx=VW / 2)
        if s2:
            text_center(cv, A, s2, 78 + 13 * sc, col, sc, BLACK, DRED, cx=VW / 2)
    if freeze0 <= tb < freeze1:
        g = cv.mean(2, keepdims=True)
        cv[:] = cv * 0.35 + g * np.array([0.75, 0.8, 1.05], np.float32) * 0.65
        post['shake'] = 2 if tb < freeze0 + 0.25 else 0
    if freeze1 <= tb < 21.0:
        post['shake'] = 3


def scene_noite(cv, A, tb, post):
    cam = lerp_keys(tb, [(25.0, CAM_L1_END), (34.8, 190)])
    show = clamp((tb - 27.6) / 0.6)
    red = clamp((tb - 31.1) / 0.25)
    if 30.7 < tb < 31.1:
        show *= 0.2 if int(tb * 20) % 2 else 1.0
    fog = clamp((tb - 26.5) / 3.0)

    def lamp_fn(k):
        x = T.lamp_x(k) - cam
        return 1.0 if tb >= 27.0 + clamp(x / W) * 0.8 else 0.0

    wc = world()
    if tb < 27.2:
        day = world()
        park_scene(day, A, cam, tb)
        park_scene(wc, A, cam, tb, night=True, fog=fog, lamp_fn=lamp_fn)
        m = np.zeros((H, W), bool)
        m[VY:VY + VH, VX:VX + VW] = dither_mask((tb - 25.0) / 2.0, 3, 'down')
        wc = np.where(m[..., None], wc, day)
        lamps = [(T.lamp_x(k) - cam + 8, 0) for k in range(10)]
    else:
        lamps = park_scene(wc, A, cam, tb, night=True, show=show, red=red, fog=fog, lamp_fn=lamp_fn)
    if tb >= 31.4:
        u = ease_io((tb - 31.4) / 3.4)
        ex = 60 + 60 * u
        ey = 204 + 42 * u
        draw_eyes_in_water(wc, A, ex - 90, ey - 50, tb, 1.0 + red)
        for k in range(3):
            rr = (tb * 3 + k / 3) % 1
            for ang in np.linspace(math.pi * 0.55, math.pi * 1.45, 12):
                px(wc, ex - 4 + math.cos(ang) * rr * 26, ey + 2 + math.sin(ang) * rr * 5,
                   (90 * (1 - rr), 60 * (1 - rr), 140 * (1 - rr)), add=True)
        draw_fog(wc, A, tb + 3, fog * 0.5, 230, 292)
    if tb >= 32.4:
        x = 20 + (tb - 32.4) * 60
        look = tb > 34.2
        fr = (9 + int(tb * 8) % 2) if look else [6, 7, 8, 7][int(tb * 12) % 4]
        blit(wc, A.visA[fr], x, VIS_GROUND - 46, tint=night_tint(x + 16, lamps))
    crop(cv, wc)
    draw_hud(cv, A, tb, 0.0, blink_red=True)
    if 25.2 < tb < 27.8:
        title_text(cv, A, 'LEVEL 2', 80, WHITE, 3, (40, 40, 90))
        title_text(cv, A, 'A NOITE', 106, RED, 3, DRED)


def scene_chase(cv, A, tb, post):
    cam = T.chase_cam_x(tb)
    wc = world()
    lamps = park_scene(wc, A, cam, tb, night=True, show=1.0, red=1.0, fog=0.7,
                       lamp_fn=lambda k: T.lamp_state(k, tb))
    vis = [(x, st) for x, st in lamps if VX - 20 < x < VX + VW + 20]
    lit = sum(st for _, st in vis)
    dark = clamp(1 - lit / 2.0) * 0.4
    if dark > 0:
        wc[200:] *= (1 - dark)
    hit = T.STICK_HIT
    head_hit = T.celso_world_x(hit) + 124
    bx_world = head_hit + 4
    rx = T.RUNNER_SCREEN_X
    stick_pts = None
    if 42.6 <= tb:
        if tb < hit + 0.35:
            bxs = bx_world - cam
            flipB = True
            if tb < hit - 0.6:
                frB = 0
            else:
                frB = 3
            # mão (sprite virado p/ esquerda): x_espelhado = 31 - x
            hand = (bxs + 31 - 28, VIS_GROUND - 46 + 2 + 39) if frB == 3 else (bxs + 31 - 20, VIS_GROUND - 46 + 2 + 25)
            sw = clamp((tb - (hit - 0.3)) / 0.3)
            ang = math.radians(-115 + 140 * ease_io(sw)) if tb >= hit - 0.6 else math.radians(-100)
            L = 17
            tip = (hand[0] - math.cos(ang) * L, hand[1] + math.sin(ang) * L)
            stick_pts = (hand, tip)
        else:
            u = tb - (hit + 0.35)
            bxs = bx_world - cam + u * 150
            frB, flipB = ([6, 7, 8, 7][int(u * 14) % 4] if u % 1.2 < 0.9 else 9), False
        blit(wc, A.visB[frB], bxs, VIS_GROUND - 46 + 2, flip=flipB, tint=night_tint(bxs + 16, lamps))
        if stick_pts and tb < hit:
            (x0, y0), (x1, y1) = stick_pts
            for i in range(18):
                u = i / 17
                xx, yy = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
                px(wc, xx, yy, (150, 95, 50))
                px(wc, xx, yy + 1, (80, 45, 22))
        if hit <= tb < hit + 1.4:
            rng = random.Random(9)
            dt = tb - hit
            (x0, y0), (x1, y1) = stick_pts if stick_pts else ((bx_world - cam, 280), (bx_world - cam - 16, 290))
            for i in range(18):
                u = i / 17
                sx, sy = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
                vx, vy = rng.uniform(-70, 40), rng.uniform(-120, -30)
                xx, yy = sx + vx * dt, sy + vy * dt + 260 * dt * dt
                if yy < 312:
                    px(wc, xx, yy, (170, 110, 55)); px(wc, xx + 1, yy, (90, 55, 25))
            if dt < 0.6:
                img = A.text('CRACK!', YEL, 2, BLACK, (120, 60, 0))
                blit_rgba(wc, img, x1 - 34, y1 - 46 - max(0, dt - 0.12) * 20, 1 - max(0, dt - 0.12) * 2)
            if dt < 2 / 30:
                post['flash'] = 0.6
    cx = T.celso_world_x(tb) - cam
    rate = 10 + 6 * clamp((tb - 35) / 17)
    fr = 1 + int(tb * rate) % 2
    open_t = [(40.6, 41.1), (hit - 0.05, hit + 0.6), (49.4, 49.9), (51.2, 52.0)]
    if any(a <= tb < b for a, b in open_t):
        fr = 4
    blit(wc, A.celso[fr], cx, VIS_GROUND + 10 - 58, tint=night_tint(cx + 100, lamps, (0.55, 0.5, 0.72)), glow_eyes=True)
    frA, _ = T.runner_frame(tb)
    blit(wc, A.visA[frA], rx, VIS_GROUND - 46, tint=night_tint(rx + 16, lamps))
    if frA >= 9 and int(tb * 4) % 2:
        img = A.text('!', WHITE, 2, BLACK)
        blit_rgba(wc, img, rx + 16, VIS_GROUND - 66)
    crop(cv, wc)
    d = T.distance_m(tb)
    draw_hud(cv, A, tb, 0, distance=d)
    amp = min(3.0, 10.0 / max(1.0, d))
    if hit <= tb < hit + 0.25:
        amp = 4
    post['shake'] = amp
    if d < 8:
        k = (1 - d / 8) * (0.5 + 0.5 * math.sin(tb * 10))
        for i in range(10):
            a = k * 0.07 * (10 - i) / 10
            rect_add(cv, i, 0, i + 1, VH, (255 * a, 0, 0))
            rect_add(cv, VW - 1 - i, 0, VW - i, VH, (255 * a, 0, 0))
            rect_add(cv, 0, VH - 1 - i, VW, VH - i, (255 * a, 0, 0))


def scene_jumpscare(cv, A, tb, post):
    t = tb - 52.0
    if t < 1.4:
        fr = A.jump[0] if t < 0.12 else A.jump[1]
        big = fr['rgb']
        z = 1.0 + 0.12 * ease_out(t / 0.3) + 0.03 * math.sin(t * 40)
        ys = ((np.arange(VH) - VH / 2) / z + VH / 2).astype(int).clip(0, VH - 1)
        xs = ((np.arange(VW) - VW / 2) / z + VW / 2).astype(int).clip(0, VW - 1)
        cv[:] = big[ys][:, xs]
        if int(t * 15) % 2 == 0:
            cv[..., 0] = np.minimum(255, cv[..., 0] * 1.25 + 30)
        post['shake'] = 5 * (1 - t / 1.4) + 1.5
    elif t < 1.4 + 2 / 30:
        cv[:] = 255
    else:
        cv[:] = 0
        u = t - 1.47
        if u < 0.8:
            post['static'] = (1 - u / 0.8) * 0.6
        if 2.6 <= t < 5.95:
            title_text(cv, A, 'CONTINUE?', 120, RED, 2, DRED)
            n = 5 - int((t - 2.6) / 0.6)
            title_text(cv, A, str(max(0, n)), 150, WHITE, 5, DRED)


def scene_gameover(cv, A, tb, post):
    t = tb - 58.0
    cam = CAM_L1_END
    wc = world()
    park_scene(wc, A, cam, tb)
    cx = 155 - cam
    blit(wc, celso_idle_sprite(A, tb), cx, CELSO_GROUND - 58)
    draw_zzz(wc, A, cx + 108, CELSO_GROUND - 26, tb)
    blit(wc, A.capy[2], CAPY_STOP - cam, CAPY_GROUND - 20, flip=True)
    crop(cv, wc)
    pat = ease_io((tb - 59.0) / 3.5)
    draw_hud(cv, A, tb, pat)
    rect(cv, 0, 72, VW, 128, (0, 0, 0), 0.6)
    drop = ease_out_bounce(t / 0.8)
    title_text(cv, A, 'GAME OVER', -50 + 128 * drop, RED if int(tb * 4) % 2 else (230, 20, 30), 3)
    if t > 0.9:
        title_text(cv, A, 'NÃO MEXA COM O CELSO', 110, YEL, 2, (90, 60, 0), clamp((t - 0.9) / 0.3))
    if t > 2.0 and pat < 1 and int(tb * 3) % 2:
        img = A.text('RECARREGANDO...', (180, 255, 180), 1, BLACK)
        blit_rgba(cv, img, VW - 6 - img.shape[1], 131)
    if t < 0.5:
        m = ~dither_mask(t / 0.5, 4)
        cv[m] = 0
    if t > 4.5:
        m = dither_mask((t - 4.5) / 0.5, 4)
        cv[m] = 0


def scene_aviso(cv, A, tb, post):
    cv[:] = 0
    post['aviso'] = tb - 63.0


SCENE_FN = {'titulo': scene_title, 'level1': scene_level1, 'puxao': scene_puxao, 'noite': scene_noite,
            'perseguicao': scene_chase, 'jumpscare': scene_jumpscare, 'gameover': scene_gameover,
            'aviso': scene_aviso}


def scene_at(tb):
    for name, a, b in T.SCENES:
        if a <= tb < b:
            return name
    return T.SCENES[-1][0]


# ======================================================================= glitch VHS (nativo)
def glitch_strength(tb, rng_frame):
    s = 0.0
    for (t0, d, k) in T.GLITCHES:
        if t0 <= tb < t0 + d:
            u = (tb - t0) / d
            s = max(s, k * (1 - u * 0.6))
    # pequenos glitches aleatórios ocasionais (determinísticos)
    slot = int(tb / 3.7)
    r = random.Random(slot * 7919)
    tt = slot * 3.7 + r.uniform(0.5, 3.0)
    if tt <= tb < tt + 0.1 and scene_at(tb) not in ('aviso',):
        s = max(s, 0.3)
    return s


def apply_glitch(cv, s, rng):
    if s <= 0:
        return
    nb = int(2 + 7 * s)
    for _ in range(nb):
        y0 = rng.randint(0, VH - 4)
        h = rng.randint(2, int(6 + 16 * s))
        dx = rng.randint(-int(2 + 15 * s), int(2 + 15 * s))
        cv[y0:y0 + h] = np.roll(cv[y0:y0 + h], dx, 1)
    sh = int(1 + 3 * s)
    if s > 0.45:
        cv[..., 0] = np.roll(cv[..., 0], -sh, 1)
        cv[..., 2] = np.roll(cv[..., 2], sh, 1)
    for _ in range(int(10 * s)):
        y = rng.randint(0, VH - 1)
        cv[y] = rng.randint(120, 255) * (0.5 + 0.5 * rng.rand(VW, 1))
    if s > 0.6:
        y0 = rng.randint(0, VH - 14)
        cv[y0:y0 + 7] = np.minimum(255, cv[y0:y0 + 7] * 1.4 + 40 * rng.rand(7, VW, 1))


def apply_static(cv, a, rng):
    n = rng.rand(VH // 2, VW // 2, 1) * 255
    n = np.repeat(np.repeat(n, 2, 0), 2, 1)
    cv[:] = cv * (1 - a) + n * a


# ======================================================================= CRT (resolução final)
class CRT:
    def __init__(self):
        py, pxx = np.mgrid[0:FH, 0:FW].astype(np.float32)
        u = (pxx + 0.5) / FW * 2 - 1
        v = (py + 0.5) / FH * 2 - 1
        kx, ky = 0.045, 0.032
        uc = u * (1 + kx * v * v)
        vc = v * (1 + ky * u * u)
        self.idx = []
        for ca in (0.0045, 0.0, -0.0045):   # R, G, B (aberração cromática)
            su = uc * (1 + ca)
            sx = ((su + 1) / 2 * VW).clip(0, VW - 1e-3).astype(np.int32)
            sy = ((vc + 1) / 2 * VH).clip(0, VH - 1e-3).astype(np.int32)
            self.idx.append((sy * VW + sx).ravel())
        fy = ((vc + 1) / 2 * VH) % 1.0
        scan = 1 - 0.45 * np.abs(fy * 2 - 1) ** 1.8
        col = np.where((pxx.astype(int) % 3) == 2, 0.94, 1.0)
        r2 = u * u + v * v
        vig = 1 - 0.22 * r2 ** 1.4
        e = np.maximum(np.abs(uc), np.abs(vc))
        edge = np.clip((1.0 - e) / 0.012, 0, 1)
        # cantos arredondados
        cu, cv_ = np.abs(uc), np.abs(vc)
        rc = 0.07
        dx = np.maximum(cu - (1 - rc), 0) / rc
        dy = np.maximum(cv_ - (1 - rc * 9 / 16), 0) / (rc * 9 / 16)
        corner = np.clip((1 - np.sqrt(dx * dx + dy * dy)) / 0.15, 0, 1)
        self.gain = (scan * col * vig * edge * corner * 1.16).astype(np.float32).ravel()
        rng = np.random.RandomState(11)
        self.noise = [(rng.randn(FH * FW).astype(np.float32) * 5.5) for _ in range(6)]

    def process(self, cv, fi, extra_noise=0.0):
        flat = cv.reshape(-1, 3)
        # bloom no nativo
        lum = cv.max(2)
        b = np.clip(lum - 150, 0, None)[..., None] / 105.0 * cv
        for _ in range(2):
            b = (b + np.roll(b, 1, 0) + np.roll(b, -1, 0) + np.roll(b, 2, 1) + np.roll(b, -2, 1)) / 5
        bflat = b.reshape(-1, 3)
        out = np.empty((FH * FW, 3), np.float32)
        nz = self.noise[fi % 6] * (1 + extra_noise * 6)
        flick = 1 + 0.012 * math.sin(fi * 2.1)
        g = self.gain * flick
        for c in range(3):
            ch = flat[:, c][self.idx[c]] + bflat[:, c][self.idx[c]] * 0.55
            out[:, c] = ch * g + nz
        # barra de rolagem suave (60Hz)
        rows = np.arange(FH, dtype=np.float32)
        bar = 1 + 0.035 * np.exp(-((rows - (fi * 9) % (FH + 400) + 200) / 120) ** 2)
        out = out.reshape(FH, FW, 3) * bar[:, None, None]
        return np.clip(out, 0, 255).astype(np.uint8)


# ======================================================================= legendas/overlays nítidos
SUB_SCALE = 5
SUB_MAX_W = 860       # px finais (área segura, longe dos botões do Reels)
SUB_BOTTOM = 1480     # base da legenda (acima da legenda/descrição do Instagram)
SUB_CX = 520


def sub_chunks(text):
    """Divide falas longas em 2 legendas (após as reticências)."""
    if len(text) > 46 and '… ' in text:
        i = text.index('… ') + 1
        return [text[:i], text[i + 1:]]
    return [text]


class Overlay:
    def __init__(self):
        self.cache = {}

    def sub_img(self, text):
        if text not in self.cache:
            lines = fonte.wrap(text, SUB_MAX_W // SUB_SCALE - 4)
            self.cache[text] = fonte.render_lines(lines, WHITE, SUB_SCALE, BLACK, 1, line_gap=3)
        return self.cache[text]

    def aviso_imgs(self):
        if 'aviso' not in self.cache:
            blocks = []
            for para in T.AVISO:
                lines = fonte.wrap(para, 900 // 5 - 2)
                blocks.append(fonte.render_lines(lines, WHITE, 5, BLACK, 1, line_gap=3))
            handle = fonte.render(T.HANDLE, YEL, 5, BLACK, 1, (140, 60, 0))
            self.cache['aviso'] = (blocks, handle)
        return self.cache['aviso']


def comp(frame, img, x, y, alpha=1.0):
    h, w = img.shape[:2]
    x, y = int(x), int(y)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(FW, x + w), min(FH, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    sub = img[y0 - y:y1 - y, x0 - x:x1 - x]
    m = sub[..., 3] > 0
    reg = frame[y0:y1, x0:x1]
    if alpha >= 0.999:
        np.copyto(reg, sub[..., :3], where=m[..., None])
    else:
        r = reg.astype(np.float32)
        r[m] = r[m] * (1 - alpha) + sub[..., :3][m] * alpha
        reg[:] = r.astype(np.uint8)


# ======================================================================= render de um frame
_G = {}


def _init():
    _G['A'] = Assets()
    _G['crt'] = CRT()
    _G['ov'] = Overlay()
    _G['tl'] = T.Timeline()


def render_frame(fi):
    A, crt, ov, tl = _G['A'], _G['crt'], _G['ov'], _G['tl']
    tr = fi / T.FPS
    tb = tl.to_base(tr)
    cv = np.zeros((VH, VW, 3), np.float32)
    post = {}
    SCENE_FN[scene_at(tb)](cv, A, tb, post)
    rng = np.random.RandomState(fi + 1)
    # tremor de tela
    sh = post.get('shake', 0)
    if sh > 0:
        dx = int(round(rng.uniform(-sh, sh)))
        dy = int(round(rng.uniform(-sh, sh) * 0.7))
        cv = np.roll(np.roll(cv, dx, 1), dy, 0)
        if dx > 0:
            cv[:, :dx] = 0
        elif dx < 0:
            cv[:, dx:] = 0
        if dy > 0:
            cv[:dy] = 0
        elif dy < 0:
            cv[dy:] = 0
    gs = glitch_strength(tb, rng)
    apply_glitch(cv, gs, rng)
    if post.get('static'):
        apply_static(cv, post['static'], rng)
    if post.get('flash'):
        cv = cv * (1 - post['flash']) + 255 * post['flash']
    frame = crt.process(cv, fi, extra_noise=gs * 0.5 + post.get('static', 0))
    # legendas
    sub = tl.subtitles_at(tr)
    if sub and scene_at(tb) != 'aviso':
        txt, since, left = sub
        chunks = sub_chunks(txt)
        total = since + left
        acc, k = 0.0, 0
        lens = [len(c) for c in chunks]
        for k, c in enumerate(chunks):
            seg = total * lens[k] / sum(lens)
            if since < acc + seg or k == len(chunks) - 1:
                since, left = since - acc, acc + seg - since
                break
            acc += seg
        img = ov.sub_img(chunks[k])
        a = clamp(since / 0.1) * clamp(left / 0.1)
        comp(frame, img, SUB_CX - img.shape[1] / 2, SUB_BOTTOM - img.shape[0], a)
    if 'aviso' in post:
        t = post['aviso']
        blocks, handle = ov.aviso_imgs()
        total = sum(b.shape[0] for b in blocks) + 34 * (len(blocks) - 1) + 80 + handle.shape[0]
        y = 900 - total / 2
        starts = [0.3, 1.0, 1.9, 2.8, 3.5]
        fade_out = clamp((tl.duration - tr) / 0.35) if tr > tl.duration - 0.4 else 1.0
        for b, st in zip(blocks, starts):
            a = clamp((t - st) / 0.5) * fade_out
            if a > 0:
                comp(frame, b, 540 - b.shape[1] / 2, y, a)
            y += b.shape[0] + 34
        y += 46
        a = clamp((t - 4.4) / 0.5) * fade_out
        if a > 0:
            comp(frame, handle, 540 - handle.shape[1] / 2, y, a)
    return frame


def render_bytes(fi):
    return render_frame(fi).tobytes()


# ======================================================================= main
PREVIEW_TIMES = [('01_titulo', 2.2), ('02_level1_capivara', 11.6), ('03_puxao_rabo', 19.35),
                 ('04_freeze', 20.9), ('05_irritou', 22.4), ('06_noite_show', 29.0), ('07_noite_vermelha', 33.4),
                 ('08_perseguicao', 41.0), ('09_pau_crack', 45.33), ('10_perseguicao_final', 50.0),
                 ('11_jumpscare', 52.5), ('12_gameover', 60.0), ('13_aviso', 69.0)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--frames', default=None)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    ap.add_argument('--out', default=os.path.join(OUTDIR, 'celso_a_vinganca_do_parque.mp4'))
    args = ap.parse_args()
    _init()
    tl = _G['tl']
    print('modo:', tl.mode, '| duração: %.2fs' % tl.duration)
    if args.preview:
        d = os.path.join(OUTDIR, 'previews')
        os.makedirs(d, exist_ok=True)
        thumbs = []
        for name, tb in PREVIEW_TIMES:
            fi = int(round(tl.to_real(tb) * T.FPS))
            im = Image.fromarray(render_frame(fi))
            im.save(os.path.join(d, name + '.png'))
            thumbs.append(im.resize((270, 480), Image.LANCZOS))
            print('preview', name)
        cols = 5
        rows = math.ceil(len(thumbs) / cols)
        sheet = Image.new('RGB', (cols * 280 + 10, rows * 490 + 10), (20, 20, 20))
        for i, th in enumerate(thumbs):
            sheet.paste(th, (10 + (i % cols) * 280, 10 + (i // cols) * 490))
        sheet.save(os.path.join(d, '00_contato.png'))
        return
    nframes = int(round(tl.duration * T.FPS))
    f0, f1 = 0, nframes
    if args.frames:
        a, b = args.frames.split(':')
        f0, f1 = int(a), min(nframes, int(b))
    # áudio
    import audio
    os.makedirs(OUTDIR, exist_ok=True)
    wav = os.path.join(OUTDIR, 'trilha_mix.wav')
    audio.render(tl, wav, os.path.join(OUTDIR, 'trilha_sem_narracao.wav'))
    t0 = time.time()
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (FW, FH),
           '-r', str(T.FPS), '-i', '-', '-ss', '%.4f' % (f0 / T.FPS), '-i', wav,
           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-maxrate', '10M', '-bufsize', '20M',
           '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1', '-g', '60', '-bf', '2',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', args.out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(args.jobs, initializer=_init) as pool:
        for k, buf in enumerate(pool.imap(render_bytes, range(f0, f1), chunksize=4)):
            ff.stdin.write(buf)
            if k % 60 == 0:
                el = time.time() - t0
                print('\rframe %d/%d  %.1f fps' % (f0 + k, f1, (k + 1) / max(el, 1e-6)), end='', flush=True)
    ff.stdin.close()
    ff.wait()
    print('\nok ->', args.out, '(%.0fs)' % (time.time() - t0))


if __name__ == '__main__':
    main()
