"""Gera toda a pixel art procedural do projeto em assets/gerados/.

Os arquivos seguem o MESMO formato descrito em assets/prompts_imagens.txt
(frames em linha, fundo chroma #00FF00, upscale 8x nearest), então qualquer
PNG gerado por IA com o mesmo nome em assets/ substitui o daqui.

Uso: python3 src/gerar_assets.py
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'gerados')
CHROMA = (0, 255, 0)
W, H = 270, 480          # resolução nativa do jogo (x4 = 1080x1920)
TILE_W = 540             # largura das camadas de parallax (repetem horizontalmente)


def hexc(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ utilidades
def outline(img, color, diag=False):
    """Contorno de 1px por fora dos pixels opacos (RGBA PIL -> RGBA PIL)."""
    a = np.array(img)
    m = a[..., 3] > 0
    p = np.pad(m, 1)
    n = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    if diag:
        n |= p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:]
    edge = n & ~m
    a[edge] = (*color, 255)
    return Image.fromarray(a)


def paste(dst, src, xy=(0, 0)):
    dst.alpha_composite(src, xy)


def sheet(frames, scale=8, rows=1):
    """Monta sprite sheet com fundo chroma e upscale nearest."""
    cols = math.ceil(len(frames) / rows)
    fw, fh = frames[0].size
    sh = Image.new('RGBA', (fw * cols, fh * rows), (*CHROMA, 255))
    for i, f in enumerate(frames):
        sh.alpha_composite(f, ((i % cols) * fw, (i // cols) * fh))
    sh = sh.convert('RGB')
    return sh.resize((sh.width * scale, sh.height * scale), Image.NEAREST)


def rot(pts, ang, c):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa,
             c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in pts]


def rpts(pts):
    return [(round(x), round(y)) for x, y in pts]


# ================================================================== CELSO
CP = {k: hexc(v) for k, v in dict(
    out='0e150a', dark='23310f', olive='3c4f1a', mid='536a24', light='718a34',
    hi='94aa4a', belly='e6d88a', bshade='bfae5c', eye='f0cc30', lid='2a3612',
    pupil='0a0a0a', tooth='f6f2e2', mouth='b8404e', mouthd='5a1424',
    red='ff2a1a', redglow='ff8a5a', water='9fe3ff', claw='d8d0b0').items()}


def _shade_body(img, region_mask, tail_end_x, head_x0):
    """Colore o corpo coluna a coluna (luz de cima, barriga clara, escamas)."""
    a = np.array(img)
    m = region_mask
    h, w = m.shape
    for x in range(w):
        ys = np.nonzero(m[:, x])[0]
        if len(ys) == 0:
            continue
        top, bot = ys.min(), ys.max()
        span = max(1, bot - top)
        for y in ys:
            t = (y - top) / span
            if x >= head_x0:
                # cabeça: mais escura em cima, mandíbula clara
                if t < 0.15:
                    c = CP['light']
                elif t < 0.55:
                    c = CP['olive'] if (x + y) % 5 else CP['dark']
                elif t < 0.72:
                    c = CP['mid']
                else:
                    c = CP['belly'] if x % 3 else CP['bshade']
            else:
                if t < 0.1:
                    c = CP['hi'] if x % 2 else CP['light']
                elif t < 0.3:
                    c = CP['dark'] if (x % 4 == 0 or (y + x // 4) % 3 == 0) else CP['olive']
                elif t < 0.58:
                    grid = (x % 4 == 0) or ((y - top) % 3 == 0)
                    c = CP['olive'] if grid else CP['mid']
                    if x < tail_end_x and (x // 6) % 2 == 0:
                        c = CP['dark'] if grid else CP['olive']   # faixas escuras da cauda
                elif t < 0.7:
                    c = CP['light']
                else:
                    c = CP['bshade'] if x % 3 == 0 else CP['belly']
            a[y, x, :3] = c
    return Image.fromarray(a)


def celso_frame(kind):
    """kind: idle, walkA, walkB, alert, open."""
    fw, fh = 128, 64
    G = 58
    lift = 0 if kind == 'idle' else 3
    B = G - 1 - lift          # linha da barriga
    body_l = Image.new('RGBA', (fw, fh))
    d = ImageDraw.Draw(body_l)

    def h_of(x):
        if x < 48:
            u = (x - 5) / 43
            return 2 + 10 * u ** 1.1
        if x < 92:
            return 12 + 4 * math.sin(math.pi * (x - 48) / 44)
        return 13

    def bot_of(x):
        if x < 48:
            return B + (48 - x) / 43 * (lift + (1 if kind == 'idle' else 0)) - (48 - x) * 0.02
        return B

    xs = list(range(5, 100))
    top = [(x, bot_of(x) - h_of(x)) for x in xs]
    bot = [(x, bot_of(x)) for x in reversed(xs)]
    d.polygon(rpts(top + bot), fill=(*CP['mid'], 255))

    # cabeça (polígono de perfil, focinho à direita)
    hy = B
    head = [(96, hy - 13), (100, hy - 14), (102, hy - 16), (108, hy - 16), (110, hy - 13),
            (118, hy - 10), (121, hy - 10), (122, hy - 9), (124, hy - 7), (124, hy - 4),
            (121, hy - 2), (110, hy - 1), (98, hy)]
    upper = [(96, hy - 13), (100, hy - 14), (102, hy - 16), (108, hy - 16), (110, hy - 13),
             (118, hy - 10), (121, hy - 10), (122, hy - 9), (124, hy - 7), (124, hy - 5),
             (110, hy - 5), (102, hy - 6)]
    lower = [(102, hy - 6), (110, hy - 5), (123, hy - 4), (121, hy - 2), (110, hy - 1), (98, hy)]
    hinge = (101, hy - 6)
    eye_c = (105, hy - 15)
    jaw_open = None
    if kind == 'alert':
        pivot = (95, hy - 6)
        ang = math.radians(-22)
        head = rot(head, ang, pivot)
        eye_c = rot([eye_c], ang, pivot)[0]
        d.polygon(rpts(head), fill=(*CP['mid'], 255))
        # pescoço levantado
        d.polygon(rpts([(86, hy - 14), (95, hy - 20), (101, hy - 7), (90, hy)]), fill=(*CP['mid'], 255))
    elif kind == 'open':
        au, al = math.radians(-36), math.radians(10)
        up = rot(upper, au, hinge)
        lo = rot(lower, al, hinge)
        eye_c = rot([eye_c], au, hinge)[0]
        tip_u = rot([(123, hy - 5)], au, hinge)[0]
        tip_l = rot([(123, hy - 4)], al, hinge)[0]
        jaw_open = (up, lo, tip_u, tip_l)
        d.polygon(rpts([hinge, tip_u, tip_l]), fill=(*CP['mouth'], 255))
        d.polygon(rpts(up), fill=(*CP['mid'], 255))
        d.polygon(rpts(lo), fill=(*CP['mid'], 255))
    else:
        d.polygon(rpts(head), fill=(*CP['mid'], 255))

    m = np.array(body_l)[..., 3] > 0
    if jaw_open:
        # não sombrear o interior da boca como corpo
        ins = Image.new('L', (fw, fh))
        ImageDraw.Draw(ins).polygon(rpts([hinge, jaw_open[2], jaw_open[3]]), fill=255)
        insm = (np.array(ins) > 0)
        up_m = Image.new('L', (fw, fh)); ImageDraw.Draw(up_m).polygon(rpts(jaw_open[0]), fill=255)
        lo_m = Image.new('L', (fw, fh)); ImageDraw.Draw(lo_m).polygon(rpts(jaw_open[1]), fill=255)
        insm &= ~(np.array(up_m) > 0) & ~(np.array(lo_m) > 0)
        m &= ~insm
    body_l = _shade_body(body_l, m, 48, 97)
    a = np.array(body_l)

    # crista dorsal (escamas serrilhadas) e cauda com crista dupla
    for x in range(8, 96):
        col = np.nonzero(m[:, x])[0]
        if len(col) == 0:
            continue
        t = col.min()
        if x < 48 and x % 3 == 0:
            for k in range(1, 3 if x > 14 else 2):
                if t - k >= 0:
                    a[t - k, x] = (*CP['dark'], 255)
        elif x >= 48 and x % 4 == 1 and t - 1 >= 0:
            a[t - 1, x] = (*CP['olive'], 255)
            a[t, x] = (*CP['dark'], 255)
    # dentes, boca, olho, narina
    if kind in ('idle', 'walkA', 'walkB'):
        for x in range(103, 123):
            y = hy - 5 + (1 if x > 117 else 0) - (1 if x < 106 else 0)
            a[y, x] = (*CP['out'], 255)
            if x % 3 == 0 and x > 105:
                a[y + 1, x] = (*CP['tooth'], 255)
        ex, ey = round(eye_c[0]), round(eye_c[1])
        a[ey - 1, ex - 1:ex + 2] = (*CP['out'], 255)
        a[ey - 2, ex - 1:ex + 2] = (*CP['light'], 255)
        if kind == 'idle':      # olho semicerrado
            a[ey, ex - 1:ex + 2] = (*CP['lid'], 255)
            a[ey + 1, ex - 1:ex + 2] = (*CP['eye'], 255)
            a[ey + 1, ex + 1] = (*CP['pupil'], 255)
        else:
            a[ey:ey + 2, ex - 1:ex + 2] = (*CP['eye'], 255)
            a[ey:ey + 2, ex] = (*CP['pupil'], 255)
        a[hy - 9, 121] = (*CP['out'], 255)
    elif kind == 'alert':
        ex, ey = round(eye_c[0]), round(eye_c[1])
        a[ey - 2, ex - 2:ex + 3] = (*CP['out'], 255)
        a[ey - 1:ey + 2, ex - 1:ex + 2] = (*CP['eye'], 255)
        a[ey - 1:ey + 2, ex] = (*CP['pupil'], 255)
        # linha da boca rotacionada
        pts = rot([(x, hy - 5) for x in range(103, 123)], math.radians(-22), (95, hy - 6))
        for i, (x, y) in enumerate(rpts(pts)):
            if 0 <= y < fh - 1:
                a[y, x] = (*CP['out'], 255)
                if i % 3 == 0 and i > 2:
                    a[y + 1, x] = (*CP['tooth'], 255)
        nx, ny = rpts(rot([(121, hy - 9)], math.radians(-22), (95, hy - 6)))[0]
        a[ny, nx] = (*CP['out'], 255)
    elif kind == 'open':
        up, lo, tu, tl = jaw_open
        # dentes ao longo das duas mandíbulas
        for i in range(2, 21, 2):
            u = i / 21
            px = hinge[0] + (tu[0] - hinge[0]) * u
            py = hinge[1] + (tu[1] - hinge[1]) * u
            for k in range(0, 3 if i % 4 == 0 else 2):
                yy, xx = round(py) + 1 + k, round(px + k * 0.5)
                if 0 <= yy < fh and 0 <= xx < fw and a[yy, xx, 3] and tuple(a[yy, xx, :3]) == CP['mouth']:
                    a[yy, xx] = (*CP['tooth'], 255)
            px = hinge[0] + (tl[0] - hinge[0]) * u
            py = hinge[1] + (tl[1] - hinge[1]) * u
            for k in range(0, 2):
                yy, xx = round(py) - 1 - k, round(px)
                if 0 <= yy < fh and 0 <= xx < fw and a[yy, xx, 3] and tuple(a[yy, xx, :3]) == CP['mouth']:
                    a[yy, xx] = (*CP['tooth'], 255)
        # garganta escura
        hx, hy2 = round(hinge[0]) + 2, round(hinge[1])
        for yy in range(hy2 - 2, hy2 + 2):
            for xx in range(hx, hx + 4):
                if a[yy, xx, 3] and tuple(a[yy, xx, :3]) == CP['mouth']:
                    a[yy, xx] = (*CP['mouthd'], 255)
        ex, ey = round(eye_c[0]), round(eye_c[1])
        a[ey - 2, ex - 2:ex + 2] = (*CP['out'], 255)     # sobrancelha brava
        a[ey - 1:ey + 1, ex - 1:ex + 2] = (*CP['red'], 255)
        a[ey - 1:ey + 1, ex] = (*CP['pupil'], 255)
    body_l = outline(Image.fromarray(a), CP['out'])

    # pernas
    def leg_layer(dark, specs):
        L = Image.new('RGBA', (fw, fh))
        dd = ImageDraw.Draw(L)
        cmain = CP['olive'] if dark else CP['mid']
        cfoot = CP['dark'] if dark else CP['olive']
        for (hx, kx, fx, raised) in specs:
            fy = G - (2 if raised else 0)
            dd.line([(hx, B - 4), (kx, fy - 4)], fill=(*cmain, 255), width=5)
            dd.line([(kx, fy - 4), (fx, fy - 1)], fill=(*cmain, 255), width=4)
            dd.rectangle([fx - 2, fy - 1, fx + 4, fy], fill=(*cfoot, 255))
            for c in (fx + 1, fx + 3, fx + 5):
                if c < fw:
                    L.putpixel((c, fy), (*CP['claw'], 255))
        return outline(L, CP['out'])

    rh, fs = 56, 88  # quadril traseiro / ombro dianteiro
    if kind == 'idle':
        far = [(rh + 2, rh + 4, rh + 5, False), (fs + 2, fs + 4, fs + 6, False)]
        near = [(rh, rh - 2, rh - 4, False), (fs, fs + 1, fs + 2, False)]
    elif kind == 'walkA':
        far = [(rh + 2, rh + 6, rh + 8, False), (fs + 2, fs - 1, fs - 4, True)]
        near = [(rh, rh - 4, rh - 7, True), (fs, fs + 5, fs + 8, False)]
    elif kind == 'walkB':
        far = [(rh + 2, rh - 2, rh - 5, True), (fs + 2, fs + 6, fs + 9, False)]
        near = [(rh, rh + 4, rh + 7, False), (fs, fs - 3, fs - 6, True)]
    else:
        far = [(rh + 2, rh + 3, rh + 4, False), (fs + 2, fs + 4, fs + 6, False)]
        near = [(rh, rh - 2, rh - 3, False), (fs, fs + 2, fs + 3, False)]
    frame = Image.new('RGBA', (fw, fh))
    paste(frame, leg_layer(True, far))
    paste(frame, body_l)
    paste(frame, leg_layer(False, near))
    return frame


def celso_eyes_frame():
    fw, fh = 128, 64
    im = Image.new('RGBA', (fw, fh))
    a = np.array(im)
    wl = 52  # linha d'água
    def px(x, y, c):
        a[y, x] = (*c, 255)
    # focinho (narinas) à direita, olhos à esquerda — só o topo acima da água
    for x in range(108, 118):
        hgt = 2 if 110 <= x <= 115 else 1
        for y in range(wl - hgt, wl):
            px(x, y, CP['olive'] if y > wl - hgt else CP['light'])
    px(111, wl - 2, CP['out']); px(114, wl - 2, CP['out'])
    for ex in (84, 92):
        for x in range(ex - 3, ex + 4):
            hgt = 4 if abs(x - ex) <= 1 else (3 if abs(x - ex) == 2 else 2)
            for y in range(wl - hgt, wl):
                px(x, y, CP['dark'] if y == wl - hgt else CP['olive'])
        px(ex - 1, wl - 3, CP['red']); px(ex, wl - 3, CP['red']); px(ex + 1, wl - 3, CP['redglow'])
        px(ex - 1, wl - 2, CP['red']); px(ex, wl - 2, CP['pupil']); px(ex + 1, wl - 2, CP['red'])
    im = outline(Image.fromarray(a), CP['out'])
    a = np.array(im)
    # ondinhas
    for x0, ln in ((70, 8), (100, 6), (120, 5), (78, 4)):
        for x in range(x0, min(fw, x0 + ln)):
            a[wl + 1 + (x0 % 3 == 0), x] = (*CP['water'], 255)
    for x in range(66, 124):
        if x % 7 in (0, 1, 2):
            a[wl, x] = (*CP['water'], 200 if a[wl, x, 3] == 0 else 255) if a[wl, x, 3] == 0 else a[wl, x]
    return Image.fromarray(a)


def celso_sheet():
    frames = [celso_frame('idle'), celso_frame('walkA'), celso_frame('walkB'),
              celso_frame('alert'), celso_frame('open'), celso_eyes_frame()]
    return sheet(frames, 8)


# ================================================================== VISITANTES
VA = dict(skin='d9a066', skind='a86f3e', shirt='c83a3a', shirtd='8a2424', shorts='3a5fa8',
          shortsd='243f73', hair='3a2410', shoe='ececec', shoed='9a9a9a', cap=None)
VB = dict(skin='8d5a3b', skind='5e3923', shirt='2fa39a', shirtd='1b6b65', shorts='b09a62',
          shortsd='7a6a40', hair='15100c', shoe='c03434', shoed='7a1c1c', cap='e07a2a')
OUTC = hexc('120e14')


def person_frame(P, pose):
    P = {k: (hexc(v) if v else None) for k, v in P.items()}
    fw, fh = 32, 48
    bob = pose.get('bob', 0)

    def sh(p):
        return (p[0], p[1] + bob)

    hip, shoulder, head = sh(pose['hip']), sh(pose['shoulder']), sh(pose['head'])

    def limb(L, a, b, c, wid, col):
        d = ImageDraw.Draw(L)
        d.line([a, b], fill=(*col, 255), width=wid)
        d.line([b, c], fill=(*col, 255), width=wid)
        for p in (a, b):
            d.rectangle([p[0] - wid // 2, p[1] - wid // 2, p[0] + (wid - 1) // 2, p[1] + (wid - 1) // 2], fill=(*col, 255))

    def leg(dark, knee, foot):
        L = Image.new('RGBA', (fw, fh))
        knee, foot = sh(knee), sh(foot)
        skin = P['skind'] if dark else P['skin']
        limb(L, hip, knee, foot, 3, skin)
        d = ImageDraw.Draw(L)
        # bermuda cobre a coxa
        d.line([hip, ((hip[0] * 2 + knee[0]) / 3, (hip[1] * 2 + knee[1]) / 3 + 1)],
               fill=(*(P['shortsd'] if dark else P['shorts']), 255), width=4)
        d.rectangle([foot[0] - 1, foot[1] - 1, foot[0] + 2, foot[1]],
                    fill=(*(P['shoed'] if dark else P['shoe']), 255))
        return outline(L, OUTC)

    def arm(dark, elbow, hand):
        L = Image.new('RGBA', (fw, fh))
        elbow, hand = sh(elbow), sh(hand)
        s = (shoulder[0], shoulder[1] + 1)
        limb(L, s, elbow, hand, 2, P['skind'] if dark else P['skin'])
        d = ImageDraw.Draw(L)
        d.line([s, ((s[0] + elbow[0]) / 2, (s[1] + elbow[1]) / 2)],
               fill=(*(P['shirtd'] if dark else P['shirt']), 255), width=3)
        d.rectangle([hand[0] - 1, hand[1] - 1, hand[0], hand[1]], fill=(*(P['skind'] if dark else P['skin']), 255))
        return outline(L, OUTC)

    frame = Image.new('RGBA', (fw, fh))
    paste(frame, arm(True, *pose['farm']))
    paste(frame, leg(True, *pose['fleg']))
    # tronco
    T = Image.new('RGBA', (fw, fh))
    d = ImageDraw.Draw(T)
    vx, vy = hip[0] - shoulder[0], hip[1] - shoulder[1]
    ln = math.hypot(vx, vy)
    nx, ny = -vy / ln, vx / ln   # normal
    half = 3.6
    poly = [(shoulder[0] + nx * half, shoulder[1] + ny * half), (shoulder[0] - nx * half, shoulder[1] - ny * half),
            (hip[0] - nx * half, hip[1] - ny * half), (hip[0] + nx * half, hip[1] + ny * half)]
    d.polygon(rpts(poly), fill=(*P['shirt'], 255))
    # sombra nas costas (lado esquerdo)
    back = [(shoulder[0] + nx * half, shoulder[1] + ny * half), (shoulder[0] + nx * (half - 2), shoulder[1] + ny * (half - 2)),
            (hip[0] + nx * (half - 2), hip[1] + ny * (half - 2)), (hip[0] + nx * half, hip[1] + ny * half)]
    d.polygon(rpts(back), fill=(*P['shirtd'], 255))
    # bermuda
    d.rectangle([hip[0] - 4, hip[1] - 1, hip[0] + 3, hip[1] + 3], fill=(*P['shorts'], 255))
    d.line([(hip[0] - 4, hip[1] + 3), (hip[0] + 3, hip[1] + 3)], fill=(*P['shortsd'], 255))
    # pescoço
    d.line([shoulder, ((shoulder[0] + head[0]) / 2, (shoulder[1] + head[1]) / 2 + 2)], fill=(*P['skin'], 255), width=3)
    T = outline(T, OUTC)
    paste(frame, T)
    # cabeça
    Hh = Image.new('RGBA', (fw, fh))
    a = np.array(Hh)
    cx, cy = round(head[0]), round(head[1])
    face = pose.get('face', 'r')
    sgn = 1 if face == 'r' else -1
    for y in range(cy - 4, cy + 5):
        for x in range(cx - 4, cx + 4):
            corner = (y in (cy - 4, cy + 4)) and (x in (cx - 4, cx + 3))
            if not corner:
                a[y, x] = (*P['skin'], 255)
    # nariz e queixo
    nxp = cx + 4 if face == 'r' else cx - 5
    a[cy, nxp] = (*P['skin'], 255)
    # cabelo (topo e nuca)
    backx = range(cx - 4, cx - 1) if face == 'r' else range(cx + 1, cx + 4)
    for x in range(cx - 4, cx + 4):
        a[cy - 4, x] = (*P['hair'], 255)
        if x in backx or (face == 'r' and x < cx + 2) or (face == 'l' and x > cx - 3):
            a[cy - 3, x] = (*P['hair'], 255)
    for y in range(cy - 2, cy + 1):
        for x in backx:
            if (face == 'r' and x == cx - 4) or (face == 'l' and x == cx + 3):
                a[y, x] = (*P['hair'], 255)
    # orelha
    ex = cx - 1 if face == 'r' else cx
    a[cy, ex] = (*P['skind'], 255)
    a[cy + 1, ex] = (*P['skind'], 255)
    # olho e boca
    expr = pose.get('expr', 'neutral')
    ox = cx + 2 if face == 'r' else cx - 3
    if expr in ('scared', 'terror'):
        a[cy - 1, ox] = (255, 255, 255, 255)
        a[cy - 1, ox + sgn] = (255, 255, 255, 255) if expr == 'terror' else (20, 20, 20, 255)
        a[cy - 1, ox + (sgn if expr == 'terror' else 0)] = (20, 20, 20, 255) if expr == 'terror' else a[cy - 1, ox]
        a[cy - 2, ox - sgn: ox + 2] = (*P['skind'], 255) if face == 'r' else a[cy - 2, ox - sgn: ox + 2]
        mo = 2 if expr == 'terror' else 1
        for yy in range(cy + 2, cy + 2 + mo):
            a[yy, ox] = (90, 20, 30, 255)
            a[yy, ox + sgn] = (90, 20, 30, 255)
    elif expr == 'laugh':
        a[cy - 1, ox] = (20, 20, 20, 255)
        a[cy - 1, ox + sgn] = (20, 20, 20, 255)
        a[cy + 1, ox:ox + 2 * sgn:sgn] = (255, 255, 255, 255)
        a[cy + 2, ox] = (150, 30, 40, 255)
        a[cy + 2, ox + sgn] = (150, 30, 40, 255)
    else:
        a[cy - 1, ox] = (20, 20, 20, 255)
        a[cy + 2, ox] = (120, 60, 50, 255)
        a[cy + 2, ox + sgn] = (120, 60, 50, 255)
    Hh = Image.fromarray(a)
    if P['cap']:
        d = ImageDraw.Draw(Hh)
        d.rectangle([cx - 4, cy - 5, cx + 3, cy - 3], fill=(*P['cap'], 255))
        if face == 'r':
            d.line([(cx + 3, cy - 3), (cx + 5, cy - 3)], fill=(*P['cap'], 255))
        else:
            d.line([(cx - 6, cy - 3), (cx - 4, cy - 3)], fill=(*P['cap'], 255))
    Hh = outline(Hh, OUTC)
    paste(frame, Hh)
    paste(frame, leg(False, *pose['nleg']))
    paste(frame, arm(False, *pose['narm']))
    return frame


def poses():
    G = 46
    base = dict(hip=(16, 30), shoulder=(16, 17), head=(17, 9))
    P = []
    # walk 1..3
    P.append(dict(base, nleg=((19, 38), (21, G - 1)), fleg=((14, 38), (11, G - 1)),
                  narm=((14, 22), (12, 26)), farm=((18, 22), (20, 25))))
    P.append(dict(base, bob=-1, nleg=((17, 38), (16, G - 1)), fleg=((16, 37), (15, G - 2)),
                  narm=((16, 23), (16, 27)), farm=((16, 23), (17, 27))))
    P.append(dict(base, nleg=((14, 38), (11, G - 1)), fleg=((19, 38), (21, G - 1)),
                  narm=((18, 22), (20, 25)), farm=((14, 22), (12, 26))))
    # reach down
    P.append(dict(hip=(13, 33), shoulder=(20, 23), head=(24, 17), expr='laugh',
                  nleg=((19, 38), (18, G - 1)), fleg=((16, 40), (11, G - 1)),
                  narm=((24, 30), (28, 39)), farm=((22, 29), (24, 34))))
    # laugh 1-2
    P.append(dict(hip=(16, 30), shoulder=(15, 17), head=(15, 9), expr='laugh',
                  nleg=((17, 38), (18, G - 1)), fleg=((14, 38), (12, G - 1)),
                  narm=((19, 23), (17, 27)), farm=((19, 19), (23, 15))))
    P.append(dict(hip=(16, 31), shoulder=(15, 18), head=(14, 11), expr='laugh',
                  nleg=((18, 39), (18, G - 1)), fleg=((14, 39), (12, G - 1)),
                  narm=((19, 24), (17, 28)), farm=((18, 23), (16, 28))))
    # run 1-3 (inclinado, assustado)
    R = dict(hip=(15, 29), shoulder=(18, 17), head=(20, 9), expr='scared')
    P.append(dict(R, nleg=((22, 36), (25, G - 2)), fleg=((10, 35), (6, 40)),
                  narm=((14, 22), (11, 19)), farm=((22, 22), (25, 18))))
    P.append(dict(R, bob=-2, nleg=((21, 33), (18, 41)), fleg=((15, 38), (14, G - 1)),
                  narm=((17, 23), (20, 25)), farm=((18, 23), (16, 26))))
    P.append(dict(R, nleg=((11, 36), (6, 41)), fleg=((21, 37), (24, G - 1)),
                  narm=((22, 22), (25, 18)), farm=((14, 22), (11, 19))))
    # look back 1-2 (cabeça virada para trás, pavor)
    P.append(dict(R, face='l', expr='terror', head=(19, 9), nleg=((22, 36), (25, G - 2)), fleg=((10, 35), (6, 40)),
                  narm=((14, 23), (10, 22)), farm=((22, 21), (25, 15))))
    P.append(dict(R, face='l', expr='terror', bob=-1, head=(19, 9), nleg=((11, 36), (6, 41)), fleg=((21, 37), (24, G - 1)),
                  narm=((22, 21), (26, 16)), farm=((14, 23), (10, 22))))
    return P


def visitantes_sheet():
    ps = poses()
    frames = [person_frame(VA, p) for p in ps] + [person_frame(VB, p) for p in ps]
    return sheet(frames, 8, rows=2)


# ================================================================== CAPIVARA
def capivara_frame(step):
    fw, fh = 32, 20
    C = {k: hexc(v) for k, v in dict(b='8a5a32', d='5e3a1e', l='b07a45', n='3a2414', e='0a0a0a').items()}
    L = Image.new('RGBA', (fw, fh))
    d = ImageDraw.Draw(L)
    G = 19
    legs = {0: [(9, 0), (12, 1), (20, 1), (23, 0)], 1: [(10, 1), (12, 0), (20, 0), (22, 1)],
            2: [(10, 0), (12, 0), (20, 0), (22, 0)]}[step]
    for i, (lx, up) in enumerate(legs):
        col = C['d'] if i % 2 == 0 else C['b']
        d.rectangle([lx, G - 5 - up, lx + 2, G - up], fill=(*col, 255))
    d.ellipse([4, 5, 25, 16], fill=(*C['b'], 255))
    d.rectangle([20, 4, 29, 11], fill=(*C['b'], 255))   # cabeça quadradona
    d.rectangle([27, 6, 30, 11], fill=(*C['b'], 255))   # focinho
    d.rectangle([21, 2, 22, 4], fill=(*C['d'], 255))    # orelha
    a = np.array(L)
    m = a[..., 3] > 0
    for y in range(fh):
        for x in range(fw):
            if m[y, x]:
                if y <= 6 and x < 26:
                    a[y, x, :3] = C['l']
                elif y >= 14:
                    a[y, x, :3] = C['d']
                elif (x + y * 2) % 7 == 0:
                    a[y, x, :3] = C['d']
    a[6, 25] = (*C['e'], 255)
    a[7, 29] = (*C['n'], 255)
    a[10, 27:30] = (*C['d'], 255)
    return outline(Image.fromarray(a), hexc('1a120a'))


def capivara_sheet():
    return sheet([capivara_frame(0), capivara_frame(1), capivara_frame(2)], 8)


# ================================================================== JUMPSCARE
def jumpscare_frame(open_amt):
    fw, fh = 180, 320
    k = fw / 135.0
    rng = random.Random(7)
    im = Image.new('RGBA', (fw, fh), (0, 0, 0, 255))
    a = np.array(im)
    # garganta: gradiente vermelho escuro -> preto no centro
    cy = fh // 2 + 6
    for y in range(fh):
        for x in range(fw):
            r = math.hypot((x - fw / 2) / fw, (y - cy) / fh * 1.3)
            v = max(0, 1 - r * 2.6)
            bay = ((x % 4) * 4 + (y % 4)) / 16
            lvl = v * 3 + bay * 0.9
            col = [(10, 0, 4), (60, 6, 14), (110, 14, 26), (160, 30, 44)][min(3, int(lvl))]
            a[y, x, :3] = col
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    gap = int((40 + 26 * open_amt) * k)
    ujaw_y = cy - gap      # borda da mandíbula superior (centro)
    ljaw_y = cy + gap
    pal = {k: hexc(v) for k, v in dict(o='0e150a', d='23310f', m='3c4f1a', l='536a24', h='718a34',
                                       g='b8404e', gd='7a2030', t='f6f2e2', ts='c8c0a8', y='e6d88a').items()}
    # mandíbula superior (forma de U invertido)
    J1, J2 = 30 * k, 34 * k
    up = [(0, 0), (fw, 0), (fw, ujaw_y + J1)]
    for i in range(21):
        u = i / 20
        x = fw - u * fw
        y = ujaw_y + J1 * (abs(u - 0.5) * 2) ** 1.6
        up.append((x, y))
    up.append((0, ujaw_y + J1))
    d.polygon(rpts(up), fill=(*pal['l'], 255))
    lo = [(0, fh), (fw, fh), (fw, ljaw_y - J2)]
    for i in range(21):
        u = i / 20
        x = fw - u * fw
        y = ljaw_y - J2 * (abs(u - 0.5) * 2) ** 1.6
        lo.append((x, y))
    lo.append((0, ljaw_y - J2))
    d.polygon(rpts(lo), fill=(*pal['l'], 255))
    a = np.array(im)
    # textura de escamas + gengiva rosa na borda
    upm = np.zeros((fh, fw), bool); lom = np.zeros((fh, fw), bool)
    t1 = Image.new('L', (fw, fh)); ImageDraw.Draw(t1).polygon(rpts(up), fill=255); upm = np.array(t1) > 0
    t2 = Image.new('L', (fw, fh)); ImageDraw.Draw(t2).polygon(rpts(lo), fill=255); lom = np.array(t2) > 0
    for msk, is_up in ((upm, True), (lom, False)):
        for x in range(fw):
            ys = np.nonzero(msk[:, x])[0]
            if not len(ys):
                continue
            edge = ys.max() if is_up else ys.min()
            for y in ys:
                dist = abs(edge - y)
                if dist < 5 * k:
                    c = pal['g'] if dist > 1 else pal['gd']
                elif dist < 7 * k:
                    c = pal['o']
                else:
                    sc = ((x // 6) + (y // 5)) % 2
                    c = pal['m'] if sc else pal['l']
                    if (x % 6 == 0) or (y % 5 == 0):
                        c = pal['d']
                    if not is_up and dist > 40 * k:
                        c = pal['y'] if (x + y) % 9 else hexc('bfae5c')
                    if is_up and y < 12 * k:
                        c = pal['h'] if (x // 3) % 2 else pal['l']
                a[y, x, :3] = c
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    # dentes
    def teeth(is_up):
        n = 13
        for i in range(n):
            u = (i + 0.5) / n
            x = fw - u * fw
            if is_up:
                ey = ujaw_y + J1 * (abs(u - 0.5) * 2) ** 1.6 - 4 * k
                ln = (rng.randint(9, 16) + (6 if i in (2, 10) else 0)) * k
                tri = [(x - 5, ey), (x + 5, ey), (x, ey + ln)]
            else:
                ey = ljaw_y - J2 * (abs(u - 0.5) * 2) ** 1.6 + 4 * k
                ln = (rng.randint(8, 14) + (6 if i in (3, 9) else 0)) * k
                tri = [(x - 5, ey), (x + 5, ey), (x, ey - ln)]
            d.polygon(rpts(tri), fill=(*pal['t'], 255), outline=(*pal['o'], 255))
            d.line(rpts([(x + 2, ey), (x + 1, ey + (ln - 3) * (1 if is_up else -1))]), fill=(*pal['ts'], 255))
    teeth(True)
    teeth(False)
    # língua
    d.ellipse([fw / 2 - 35, ljaw_y - 40, fw / 2 + 35, ljaw_y + 5], fill=(*hexc('a83848'), 255), outline=(*pal['gd'], 255))
    d.line([(fw / 2, ljaw_y - 35), (fw / 2, ljaw_y - 8)], fill=(*pal['gd'], 255))
    # olhos vermelhos em cima
    for ex in (43, fw - 44):
        d.ellipse([ex - 17, 10, ex + 17, 45], fill=(*pal['m'], 255), outline=(*pal['o'], 255))
        d.ellipse([ex - 12, 17, ex + 12, 39], fill=(255, 40, 20, 255), outline=(120, 0, 0, 255))
        d.ellipse([ex - 7, 20, ex + 7, 33], fill=(255, 140, 90, 255))
        d.rectangle([ex - 1, 17, ex + 1, 39], fill=(10, 0, 0, 255))
        d.line([(ex - 18, 8 + (5 if ex < fw / 2 else 0)), (ex + 16, 8 + (0 if ex < fw / 2 else 5))],
               fill=(*pal['o'], 255), width=4)
    # narinas
    for nx in (fw / 2 - 11, fw / 2 + 8):
        d.ellipse([nx - 3, 54, nx + 4, 59], fill=(*pal['o'], 255))
    return im


def jumpscare_sheet():
    f1, f2 = jumpscare_frame(0.0), jumpscare_frame(1.0)
    sh = Image.new('RGB', (f1.width * 2, f1.height))
    sh.paste(f1.convert('RGB'), (0, 0))
    sh.paste(f2.convert('RGB'), (f1.width, 0))
    return sh.resize((sh.width * 6, sh.height * 6), Image.NEAREST)


# ================================================================== CENÁRIOS
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def gradient(h, w, stops):
    """stops: [(y, (r,g,b)), ...] — degradê em faixas com dithering ordenado."""
    out = np.zeros((h, w, 3), np.uint8)
    ys = [s[0] for s in stops]
    for y in range(h):
        i = max(0, min(len(stops) - 2, np.searchsorted(ys, y, side='right') - 1))
        y0, c0 = stops[i]
        y1, c1 = stops[i + 1]
        t = min(1, max(0, (y - y0) / max(1, (y1 - y0))))
        for x in range(w):
            out[y, x] = c1 if t > BAYER4[y % 4, x % 4] else c0
    return out


def blob(d, cx, cy, r, col):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*col, 255))


def make_layers(night):
    rng = random.Random(42)
    L = {}
    # ---------------- céu
    if not night:
        sky = gradient(190, TILE_W, [(0, hexc('10206a')), (70, hexc('1f3f9e')), (112, hexc('2f5cc0')),
                                     (132, hexc('6f86d0')), (148, hexc('c88aa0')), (162, hexc('ee9a58')),
                                     (176, hexc('f8c060')), (189, hexc('fde08a'))])
    else:
        sky = gradient(190, TILE_W, [(0, hexc('05030f')), (60, hexc('120a30')), (115, hexc('231348')),
                                     (155, hexc('3a1c5c')), (182, hexc('52286a')), (189, hexc('52286a'))])
    im = Image.fromarray(sky).convert('RGBA')
    d = ImageDraw.Draw(im)
    if not night:
        # sol
        sx, sy = 205, 160
        blob(d, sx, sy, 17, hexc('ffd27a'))
        blob(d, sx, sy, 13, hexc('fff0b8'))
        # nuvens
        for (cx, cy, s) in ((80, 128, 0.9), (300, 120, 0.8), (470, 136, 1.0), (390, 150, 0.6)):
            for k in range(6):
                ox = (k - 2.5) * 9 * s
                r = (8 - abs(k - 2.5) * 1.6) * s
                blob(d, cx + ox, cy, r, hexc('f2c6a6'))
            for k in range(6):
                ox = (k - 2.5) * 9 * s
                r = (8 - abs(k - 2.5) * 1.6) * s
                d.rectangle([cx + ox - r, cy + r * 0.3, cx + ox + r, cy + r], fill=(*hexc('c98a7e'), 255))
            d.rectangle([cx - 30 * s, cy + 5 * s, cx + 30 * s, cy + 8 * s], fill=(*hexc('c98a7e'), 255))
    else:
        a = np.array(im)
        for _ in range(170):
            x, y = rng.randrange(TILE_W), rng.randrange(100, 172)
            a[y, x, :3] = rng.choice([(255, 255, 255), (200, 190, 255), (255, 230, 200), (140, 130, 200)])
        im = Image.fromarray(a)
        d = ImageDraw.Draw(im)
        blob(d, 196, 136, 9, hexc('f4ecd0'))
        blob(d, 200, 133, 8, hexc('1c1040'))
    L['ceu'] = im

    # ---------------- prédios do Centro Político Administrativo (genéricos)
    im = Image.new('RGBA', (TILE_W, H))
    d = ImageDraw.Draw(im)
    if not night:
        wall, wsh, win, glass, roof = hexc('a3acd0'), hexc('7e86b0'), hexc('5c6494'), hexc('d6e0f6'), hexc('6a7099')
    else:
        wall, wsh, win, glass, roof = hexc('211c40'), hexc('171330'), hexc('2c2654'), hexc('f2d070'), hexc('110e24')
    base_y = 182
    x = 0
    bl = []
    while x < TILE_W:
        bw = rng.randint(26, 64)
        bh = rng.randint(18, 46)
        if rng.random() < 0.18:
            bh = rng.randint(60, 74)    # torre
        bl.append((x, bw, bh))
        x += bw + rng.randint(2, 12)
    for (bx, bw, bh) in bl:
        top = base_y - bh
        d.rectangle([bx, top, bx + bw, base_y], fill=(*wall, 255))
        d.rectangle([bx + bw - 4, top, bx + bw, base_y], fill=(*wsh, 255))
        d.rectangle([bx - 1, top - 2, bx + bw + 1, top], fill=(*roof, 255))
        horiz = rng.random() < 0.5
        for wy in range(top + 4, base_y - 3, 4):
            if horiz:
                d.line([(bx + 2, wy), (bx + bw - 6, wy)], fill=(*win, 255))
                if night:
                    for wx in range(bx + 2, bx + bw - 6, 3):
                        if rng.random() < 0.3:
                            d.point((wx, wy), fill=(*glass, 255))
            else:
                for wx in range(bx + 3, bx + bw - 6, 4):
                    lit = night and rng.random() < 0.35
                    c = glass if (lit or (not night and rng.random() < 0.15)) else win
                    d.rectangle([wx, wy, wx + 1, wy + 1], fill=(*c, 255))
        if bh > 58:
            d.line([(bx + bw // 2, top - 12), (bx + bw // 2, top - 2)], fill=(*roof, 255))
            d.point((bx + bw // 2, top - 13), fill=(255, 40, 40, 255) if night else (*roof, 255))
    L['predios'] = im

    # ---------------- árvores do cerrado + palmeiras + gramado distante com capivaras
    im = Image.new('RGBA', (TILE_W, H))
    d = ImageDraw.Draw(im)
    if not night:
        gr, grd, gl, trunk, palm, palmd, capy = hexc('5a9632'), hexc('3f7426'), hexc('7cb444'), hexc('5a3a1e'), hexc('3e8a34'), hexc('2a6224'), hexc('7a4e2c')
        greens = [hexc('22561f'), hexc('357a2a'), hexc('4f9636'), hexc('78b448')]
    else:
        gr, grd, gl, trunk, palm, palmd, capy = hexc('122a24'), hexc('0b1c18'), hexc('1c3a32'), hexc('140e0c'), hexc('163430'), hexc('0c2220'), hexc('2a1c18')
        greens = [hexc('07150f'), hexc('0e241e'), hexc('15302a'), hexc('1f4038')]
    d.rectangle([0, 186, TILE_W, 200], fill=(*gr, 255))
    for xx in range(0, TILE_W, 2):
        if rng.random() < 0.5:
            d.point((xx, 186 + rng.randint(0, 13)), fill=(*rng.choice([grd, gl]), 255))
    items = []
    x = 6
    while x < TILE_W - 6:
        items.append((x, 'palm' if rng.random() < 0.3 else 'tree', rng.randint(0, 999)))
        x += rng.randint(22, 46)
    for (tx, kind, seed) in items:
        r2 = random.Random(seed)
        gy = 190 + r2.randint(-2, 4)
        if kind == 'tree':
            h = r2.randint(20, 34)
            pts = [(tx, gy)]
            cx = tx
            for k in range(3):
                cx += r2.randint(-3, 3)
                pts.append((cx, gy - h * (k + 1) / 3))
            d.line(pts, fill=(*trunk, 255), width=2)
            top = pts[-1]
            for k in range(7):
                ox, oy = r2.randint(-11, 11), r2.randint(-6, 4)
                r = r2.randint(5, 8)
                blob(d, top[0] + ox, top[1] + oy, r, greens[1])
            for k in range(5):
                ox, oy = r2.randint(-9, 7), r2.randint(-7, 1)
                blob(d, top[0] + ox - 1, top[1] + oy - 1, r2.randint(3, 5), greens[2])
            for k in range(4):
                ox, oy = r2.randint(-8, 4), r2.randint(-8, -3)
                blob(d, top[0] + ox - 2, top[1] + oy, 2, greens[3])
            # sombra embaixo da copa
            d.line([(top[0] - 9, top[1] + 6), (top[0] + 9, top[1] + 6)], fill=(*greens[0], 255), width=2)
        else:
            h = r2.randint(40, 56)
            bend = r2.choice([-1, 1]) * r2.randint(2, 6)
            pts = [(tx + bend * (k / 6) ** 2, gy - h * k / 6) for k in range(7)]
            d.line(pts, fill=(*trunk, 255), width=2)
            topx, topy = pts[-1]
            for ang in range(0, 360, 36):
                ra = math.radians(ang)
                ln = r2.randint(10, 15)
                ex = topx + math.cos(ra) * ln
                ey = topy + math.sin(ra) * ln * 0.55 + (abs(math.cos(ra)) * 4)
                d.line([(topx, topy), ((topx + ex) / 2, min(topy, ey) - 2), (ex, ey)], fill=(*palm, 255), width=2)
                d.point((round(ex), round(ey) + 1), fill=(*palmd, 255))
            blob(d, topx, topy, 2, palmd)
    # capivaras pequenas no gramado
    for cxp in (60, 210, 230, 400):
        d.rectangle([cxp, 193, cxp + 6, 196], fill=(*capy, 255))
        d.rectangle([cxp + 5, 192, cxp + 8, 195], fill=(*capy, 255))
        d.point((cxp + 1, 197), fill=(*capy, 255)); d.point((cxp + 5, 197), fill=(*capy, 255))
    L['arvores'] = im

    # ---------------- lagoa (com base do chafariz no centro do tile)
    im = Image.new('RGBA', (TILE_W, H))
    if not night:
        water = gradient(66, TILE_W, [(0, hexc('8fb4e8')), (10, hexc('5d8ad0')), (40, hexc('3b68b0')), (65, hexc('2b528f'))])
        sh1, sh2 = hexc('c4dcf8'), hexc('f6c27a')
    else:
        water = gradient(66, TILE_W, [(0, hexc('1c1240')), (20, hexc('110c30')), (65, hexc('080820'))])
        sh1, sh2 = hexc('3a2e70'), hexc('4a2a5a')
    a = np.zeros((H, TILE_W, 4), np.uint8)
    a[198:264, :, :3] = water
    a[198:264, :, 3] = 255
    for _ in range(260):
        x, y = rng.randrange(TILE_W - 8), rng.randrange(200, 262)
        ln = rng.randint(2, 7)
        a[y, x:x + ln, :3] = sh1
    if not night:   # reflexo do sol
        for y in range(200, 250, 2):
            w = rng.randint(3, 10)
            x = 210 - w // 2 + rng.randint(-2, 2)
            a[y, x:x + w, :3] = sh2
    a[198, :, :3] = hexc('2a4a2a') if not night else hexc('0a1410')
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    fx, fy = TILE_W // 2, 230
    stone, stoned = (hexc('b8b8c4'), hexc('6a6a7a')) if not night else (hexc('3a3850'), hexc('1e1c30'))
    d.ellipse([fx - 22, fy - 3, fx + 22, fy + 5], fill=(*stoned, 255))
    d.ellipse([fx - 21, fy - 4, fx + 21, fy + 3], fill=(*stone, 255))
    d.ellipse([fx - 17, fy - 3, fx + 17, fy + 2], fill=(*(hexc('5d8ad0') if not night else hexc('141040')), 255))
    d.rectangle([fx - 2, fy - 6, fx + 2, fy], fill=(*stoned, 255))
    L['lagoa'] = im

    # ---------------- chão: margem, pista, ciclofaixa, gramado da frente
    im = Image.new('RGBA', (TILE_W, H))
    a = np.zeros((H, TILE_W, 4), np.uint8)
    if not night:
        C = dict(mud='6e5a3a', grass='4f9030', grassd='2f6a1e', grassl='78b444', curb='d2cabb', curbd='8a8478',
                 track='a64a2a', trackd='8a3820', trackl='c0603a', line='efe6d6', bike='b33a32', biked='8e2a26',
                 fg='3a7a26', fgd='275a1a', fgl='5e9c38', flower='f6d34a', rock='8a8a80')
    else:
        C = dict(mud='1a140e', grass='10261a', grassd='081810', grassl='183428', curb='3a3848', curbd='22202e',
                 track='3a1a1a', trackd='2a1212', trackl='4a2222', line='5a5866', bike='3a1620', biked='2a0e16',
                 fg='0c2016', fgd='06140c', fgl='14301e', flower='4a4020', rock='2a2a30')
    C = {k: hexc(v) for k, v in C.items()}
    a[262:480, :, 3] = 255

    def band(y0, y1, base, others, p):
        a[y0:y1, :, :3] = base
        n = rng
        for y in range(y0, y1):
            for x in range(TILE_W):
                if n.random() < p:
                    a[y, x, :3] = n.choice(others)
    band(262, 265, C['mud'], [C['grassd']], 0.2)
    band(265, 280, C['grass'], [C['grassd'], C['grassl']], 0.18)
    a[280:282, :, :3] = C['curb']
    a[282, :, :3] = C['curbd']
    band(283, 300, C['track'], [C['trackd'], C['trackl']], 0.22)
    a[300, :, :3] = C['line']
    band(301, 316, C['bike'], [C['biked']], 0.12)
    for x in range(0, TILE_W, 12):
        a[308, x:x + 6, :3] = C['line']
    a[316:318, :, :3] = C['curb']
    a[318, :, :3] = C['curbd']
    band(319, 480, C['fg'], [C['fgd'], C['fgl']], 0.16)
    # escurece a base (vinheta do chão)
    for y in range(400, 480):
        k = 1 - (y - 400) / 80 * 0.45
        a[y, :, :3] = (a[y, :, :3] * k).astype(np.uint8)
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    # juncos/capim na margem
    for x in range(0, TILE_W, 3):
        if rng.random() < 0.45:
            h = rng.randint(2, 7)
            d.line([(x, 266), (x + rng.randint(-1, 1), 266 - h)], fill=(*rng.choice([C['grassl'], C['grassd']]), 255))
            if h > 5 and rng.random() < 0.3:
                d.rectangle([x, 266 - h - 2, x, 266 - h], fill=(*hexc('6a4020' if not night else '1a120c'), 255))
    # pedras
    for _ in range(10):
        x = rng.randrange(TILE_W)
        d.ellipse([x, 268, x + 5, 272], fill=(*C['rock'], 255))
    # símbolo de bicicleta na ciclofaixa
    for bx in (60, 330):
        for cx in (bx, bx + 9):
            d.ellipse([cx - 3, 304, cx + 3, 310], outline=(*C['line'], 255))
        d.line([(bx, 307), (bx + 4, 303), (bx + 9, 307)], fill=(*C['line'], 255))
    # gramado da frente: arbustos, flores, banco, ipê amarelo
    for _ in range(26):
        x, y = rng.randrange(TILE_W), rng.randrange(326, 470)
        for k in range(4):
            blob(d, x + rng.randint(-6, 6), y + rng.randint(-2, 2), rng.randint(3, 6), C['fgd'])
        for k in range(3):
            blob(d, x + rng.randint(-5, 4), y + rng.randint(-3, 0), rng.randint(2, 3), C['fgl'])
    for _ in range(90):
        x, y = rng.randrange(TILE_W), rng.randrange(322, 470)
        d.point((x, y), fill=(*C['flower'], 255))
    # banco
    bench = C['curbd'] if night else hexc('7a4a28')
    d.rectangle([130, 332, 156, 334], fill=(*bench, 255))
    d.rectangle([130, 327, 156, 328], fill=(*bench, 255))
    d.line([(132, 334), (132, 339)], fill=(*C['curbd'], 255)); d.line([(154, 334), (154, 339)], fill=(*C['curbd'], 255))
    # ipê amarelo
    ix, iy = 440, 420
    tcol = hexc('4a2e18') if not night else hexc('120c08')
    d.line([(ix, 480), (ix - 3, iy), (ix - 10, iy - 30)], fill=(*tcol, 255), width=4)
    d.line([(ix - 3, iy), (ix + 10, iy - 26)], fill=(*tcol, 255), width=3)
    ipe = [hexc('c89a10'), hexc('f2c418'), hexc('ffe25a')] if not night else [hexc('2a220a'), hexc('3a3010'), hexc('4a3e16')]
    for k, col in enumerate(ipe):
        for _ in range(16 - k * 4):
            blob(d, ix + rng.randint(-26, 22), iy - 36 + rng.randint(-14, 10) - k * 2, rng.randint(5, 9) - k * 2, col)
    L['chao'] = im
    return L


def composite(L, x=0):
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for name, f in (('ceu', 0.1), ('predios', 0.25), ('arvores', 0.45), ('lagoa', 0.6), ('chao', 1.0)):
        lay = L[name]
        off = int(x * f) % TILE_W
        tile = Image.new('RGBA', (TILE_W * 2, lay.height))
        tile.paste(lay, (0, 0)); tile.paste(lay, (TILE_W, 0))
        out.alpha_composite(tile.crop((off, 0, off + W, lay.height)), (0, 0))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    celso_sheet().save(os.path.join(OUT, 'celso_sheet.png'))
    visitantes_sheet().save(os.path.join(OUT, 'visitantes_sheet.png'))
    capivara_sheet().save(os.path.join(OUT, 'capivara_sheet.png'))
    jumpscare_sheet().save(os.path.join(OUT, 'celso_jumpscare.png'))
    for night, name in ((False, 'dia'), (True, 'noite')):
        L = make_layers(night)
        d = os.path.join(OUT, 'camadas_' + name)
        os.makedirs(d, exist_ok=True)
        for k, im in L.items():
            im.save(os.path.join(d, k + '.png'))
        comp = composite(L, 0).convert('RGB')
        comp.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(OUT, 'bg_%s.png' % name))
    print('assets gerados em', OUT)


if __name__ == '__main__':
    main()
