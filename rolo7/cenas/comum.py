"""Utilitários de desenho compartilhados pelas cenas (360x640)."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import config as C

W, H = C.W, C.H


@lru_cache(None)
def fonte(nome, tam):
    arq = {"vt": "VT323-Regular.ttf", "se": "SpecialElite-Regular.ttf",
           "plex": "IBMPlexMono-Regular.ttf", "plexb": "IBMPlexMono-Bold.ttf"}[nome]
    return ImageFont.truetype(str(C.FONTES / arq), tam)


def nova(cor=(0, 0, 0), modo="RGB"):
    return Image.new(modo, (W, H), cor)


def draw_serrilhado(img):
    d = ImageDraw.Draw(img)
    d.fontmode = "1"   # sem antialias: serrilhado de VHS
    return d


def quebrar(texto, fnt, largura):
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if fnt.getlength(teste) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def texto_bloco(d, linhas, cx, y, fnt, cor, entre=4, sombra=None, alinhar="centro", x0=None):
    """Desenha linhas centralizadas (ou à esquerda em x0). Retorna y final."""
    asc = fnt.getbbox("ÁHgy")
    alt = asc[3] - asc[1]
    for ln in linhas:
        w = fnt.getlength(ln)
        x = cx - w / 2 if alinhar == "centro" else x0
        if sombra:
            d.text((x + sombra[0], y + sombra[1]), ln, font=fnt, fill=sombra[2])
        d.text((x, y), ln, font=fnt, fill=cor)
        y += alt + entre
    return y


def contorno(d, xy, s, fnt, cor, borda=(0, 0, 0), r=1, anchor="la"):
    x, y = xy
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx or dy:
                d.text((x + dx, y + dy), s, font=fnt, fill=borda, anchor=anchor)
    d.text((x, y), s, font=fnt, fill=cor, anchor=anchor)


# ------------------------------------------------------------------ OSD de VCR
def hora_str(h, m, s):
    return f"{h:02d}:{m:02d}:{s:02d}"


def osd_vcr(modo="play", t=0.0, data=True, extra=None):
    """Camada RGBA do OSD (desenhada sobre os efeitos)."""
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_serrilhado(o)
    f = fonte("vt", 24)
    y0 = C.SEGURO_TOPO + 6
    branco = (235, 240, 235, 255)
    sombra = (0, 0, 0, 200)

    def txt(x, y, s, anchor="la"):
        d.text((x + 2, y + 2), s, font=f, fill=sombra, anchor=anchor)
        d.text((x, y), s, font=f, fill=branco, anchor=anchor)

    if modo == "play":
        d.polygon([(20, y0 + 3), (20, y0 + 19), (33, y0 + 11)], fill=branco)
        txt(40, y0, "PLAY")
        txt(W - 20, y0, "SP", "ra")
    elif modo == "stop":
        d.rectangle([20, y0 + 4, 33, y0 + 17], fill=branco)
        txt(40, y0, "STOP")
    elif modo == "rew":
        for k in (0, 12):
            d.polygon([(33 + k, y0 + 3), (33 + k, y0 + 19), (21 + k, y0 + 11)], fill=branco)
        txt(52, y0, "REW")
    if data:
        h, m, s = C.HORA_OSD_INICIO
        tot = h * 3600 + m * 60 + s + int(t)
        yb = C.SEGURO_BASE - 30
        txt(20, yb, C.DATA_OSD)
        txt(W - 20, yb, hora_str(tot // 3600 % 24, tot // 60 % 60, tot % 60), "ra")
    if extra:
        extra(d, f, txt)
    return o


def osd_cftv(cam, nome, t, rec_on=True):
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_serrilhado(o)
    f = fonte("vt", 24)
    branco = (225, 235, 225, 255)
    y0 = C.SEGURO_TOPO + 6

    def txt(x, y, s, anchor="la", cor=branco):
        d.text((x + 1, y + 1), s, font=f, fill=(0, 0, 0, 220), anchor=anchor)
        d.text((x, y), s, font=f, fill=cor, anchor=anchor)

    txt(16, y0, f"CAM {cam:02d} — {nome}")
    if rec_on and int(t * 2) % 2 == 0:
        d.ellipse([W - 76, y0 + 5, W - 64, y0 + 17], fill=(230, 30, 30, 255))
    txt(W - 16, y0, "REC", "ra")
    h, m, s = C.CFTV_HORA
    tot = h * 3600 + m * 60 + s + int(t - C.B5[0])
    yb = C.SEGURO_BASE - 30
    txt(16, yb, hora_str(tot // 3600, tot // 60 % 60, tot % 60))
    txt(W - 16, yb, "16-11-1974", "ra")
    return o


# ------------------------------------------------------------------ objetos
def carretel(d, cx, cy, r, ang, cor_fita=(92, 52, 28), raio_fita=0.75, metal=(170, 170, 165)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=metal, outline=(40, 40, 40))
    rf = r * raio_fita
    d.ellipse([cx - rf, cy - rf, cx + rf, cy + rf], fill=cor_fita)
    # janelas do carretel (3 recortes que giram)
    for k in range(3):
        a = ang + k * 2 * math.pi / 3
        pts = []
        for s in np.linspace(-0.45, 0.45, 6):
            pts.append((cx + math.cos(a + s) * r * 0.92, cy + math.sin(a + s) * r * 0.92))
        for s in np.linspace(0.45, -0.45, 6):
            pts.append((cx + math.cos(a + s) * r * 0.42, cy + math.sin(a + s) * r * 0.42))
        d.polygon(pts, fill=(25, 22, 20))
    rh = r * 0.22
    d.ellipse([cx - rh, cy - rh, cx + rh, cy + rh], fill=(200, 200, 195), outline=(60, 60, 60))
    for k in range(3):
        a = ang + k * 2 * math.pi / 3 + math.pi / 3
        d.line([(cx, cy), (cx + math.cos(a) * rh, cy + math.sin(a) * rh)], fill=(60, 60, 60), width=2)


def gravador(img, cx, cy, esc, ang, vu, quebrada=False, flap=0.0, etiqueta=True):
    """Gravador de rolo visto de frente. esc=1 -> 300 px de largura."""
    d = draw_serrilhado(img)
    w, h = 300 * esc, 330 * esc
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(10 * esc), fill=(58, 50, 44), outline=(20, 18, 16), width=2)
    d.rectangle([x0 + 8 * esc, y0 + 8 * esc, x0 + w - 8 * esc, y0 + 205 * esc], fill=(42, 38, 34))
    r = 62 * esc
    c1 = (x0 + 78 * esc, y0 + 92 * esc)
    c2 = (x0 + w - 78 * esc, y0 + 92 * esc)
    carretel(d, *c1, r, ang, raio_fita=0.8 if not quebrada else 0.3)
    carretel(d, *c2, r, ang * 1.15, raio_fita=0.55 if not quebrada else 0.85)
    # cabeça
    hx, hy = cx, y0 + 175 * esc
    d.rectangle([hx - 30 * esc, hy - 10 * esc, hx + 30 * esc, hy + 12 * esc], fill=(120, 120, 118), outline=(30, 30, 30))
    d.rectangle([hx - 6 * esc, hy - 8 * esc, hx + 6 * esc, hy + 6 * esc], fill=(200, 190, 120))
    fita = (110, 62, 32)
    if not quebrada:
        d.line([(c1[0] - r * 0.78, c1[1]), (c1[0] - r * 0.78, hy), (hx - 30 * esc, hy - 10 * esc)], fill=fita, width=max(1, int(3 * esc)))
        d.line([(hx - 30 * esc, hy - 10 * esc), (hx + 30 * esc, hy - 10 * esc)], fill=fita, width=max(1, int(3 * esc)))
        d.line([(hx + 30 * esc, hy - 10 * esc), (c2[0] + r * 0.55, hy), (c2[0] + r * 0.55, c2[1])], fill=fita, width=max(1, int(3 * esc)))
    else:
        # ponta solta batendo
        a = math.sin(flap) * 1.2
        L = r * 1.1
        px, py = c2[0] - r * 0.85, c2[1] + 6
        pts = [(px, py)]
        for k in range(1, 6):
            s = k / 5
            pts.append((px - math.cos(a * s + 0.4) * L * s, py + math.sin(a * s + 0.4) * L * s))
        d.line(pts, fill=fita, width=max(1, int(3 * esc)))
    # VU meter
    vx, vy = x0 + 18 * esc, y0 + 222 * esc
    vw, vh = 120 * esc, 70 * esc
    d.rectangle([vx, vy, vx + vw, vy + vh], fill=(225, 205, 140), outline=(20, 20, 20), width=2)
    pcx, pcy = vx + vw / 2, vy + vh - 6 * esc
    for k in range(9):
        a = math.radians(-140 + k * 12.5)
        d.line([(pcx + math.cos(a) * vh * 0.75, pcy + math.sin(a) * vh * 0.75),
                (pcx + math.cos(a) * vh * 0.85, pcy + math.sin(a) * vh * 0.85)],
               fill=(150, 20, 20) if k > 6 else (40, 30, 20), width=1)
    a = math.radians(-140 + min(1.0, vu) * 100)
    d.line([(pcx, pcy), (pcx + math.cos(a) * vh * 0.82, pcy + math.sin(a) * vh * 0.82)], fill=(20, 15, 10), width=2)
    if esc >= 0.8:
        d.text((vx + 4, vy + 2), "VU", font=fonte("vt", 16), fill=(60, 40, 20))
    # botões
    for k in range(4):
        bx = x0 + 160 * esc + k * 30 * esc
        d.rectangle([bx, y0 + 260 * esc, bx + 22 * esc, y0 + 285 * esc], fill=(30, 28, 26), outline=(90, 85, 80))
    d.ellipse([x0 + 160 * esc, y0 + 228 * esc, x0 + 172 * esc, y0 + 240 * esc], fill=(230, 40, 30) if vu > 0.02 else (90, 20, 20))
    return c1, c2, r


def etiqueta(texto, tam=14, larg=None):
    f = fonte("se", tam)
    larg = larg or int(f.getlength(texto) + 16)
    linhas = quebrar(texto, f, larg - 12)
    alt = len(linhas) * (tam + 4) + 10
    img = Image.new("RGBA", (larg, alt), (232, 222, 190, 255))
    d = ImageDraw.Draw(img)   # papel: tinta com antialias, mais grossa
    d.rectangle([0, 0, larg - 1, alt - 1], outline=(150, 130, 90, 255))
    texto_bloco(d, linhas, larg / 2 + 1, 6, f, (40, 30, 70, 255), entre=4)
    texto_bloco(d, linhas, larg / 2, 6, f, (20, 15, 45, 255), entre=4)
    return img


def silhueta_radialista(d, cx, cy, esc, cor):
    """Mulher anos 60 ao microfone, só contorno escuro (perfil, sem rosto)."""
    s = esc
    # ombros/tronco
    d.polygon([(cx - 80 * s, cy + 190 * s), (cx - 70 * s, cy + 95 * s), (cx - 35 * s, cy + 70 * s),
               (cx + 30 * s, cy + 72 * s), (cx + 62 * s, cy + 100 * s), (cx + 72 * s, cy + 190 * s)], fill=cor)
    d.rectangle([cx - 12 * s, cy + 30 * s, cx + 14 * s, cy + 78 * s], fill=cor)   # pescoço
    d.ellipse([cx - 32 * s, cy - 30 * s, cx + 30 * s, cy + 45 * s], fill=cor)      # cabeça
    d.polygon([(cx + 24 * s, cy - 4 * s), (cx + 37 * s, cy + 12 * s), (cx + 26 * s, cy + 16 * s),
               (cx + 30 * s, cy + 24 * s), (cx + 24 * s, cy + 34 * s)], fill=cor)  # perfil
    d.ellipse([cx - 58 * s, cy - 78 * s, cx + 40 * s, cy + 12 * s], fill=cor)      # cabelo armado (bufante)
    d.ellipse([cx - 40 * s, cy - 92 * s, cx + 22 * s, cy - 40 * s], fill=cor)      # topo do bufante
    d.ellipse([cx - 66 * s, cy - 30 * s, cx - 8 * s, cy + 40 * s], fill=cor)       # volume da nuca
    d.ellipse([cx - 74 * s, cy + 18 * s, cx - 34 * s, cy + 52 * s], fill=cor)      # cacho virado (flip)
    d.ellipse([cx + 10 * s, cy - 30 * s, cx + 44 * s, cy - 6 * s], fill=cor)       # franja
    # microfone de rádio antigo (cápsula com grade) no pedestal
    mx, my = cx + 78 * s, cy + 18 * s
    d.line([(mx, my + 40 * s), (mx, cy + 190 * s)], fill=cor, width=max(2, int(5 * s)))
    d.rounded_rectangle([mx - 16 * s, my - 30 * s, mx + 16 * s, my + 34 * s], radius=int(14 * s), fill=cor)
    d.rectangle([mx - 22 * s, my + 30 * s, mx + 22 * s, my + 38 * s], fill=cor)


def casa_fachada(img, todas_acesas=False, vulto=False, t=0.0):
    """Casarão térreo de esquina numa bifurcação, à noite, visto da rua (câmera alta)."""
    d = ImageDraw.Draw(img)
    # céu e chão
    d.rectangle([0, 0, W, H], fill=(18, 20, 22))
    d.rectangle([0, 360, W, H], fill=(30, 31, 30))
    # bifurcação: duas ruas abrindo em V a partir da esquina
    d.polygon([(180, 395), (-40, 640), (60, 640), (180, 420)], fill=(44, 44, 42))
    d.polygon([(180, 395), (400, 640), (300, 640), (180, 420)], fill=(44, 44, 42))
    d.polygon([(180, 420), (60, 640), (300, 640)], fill=(36, 37, 35))   # calçada/canteiro da ponta
    for k in range(5):
        y = 470 + k * 34
        d.line([(180 - (y - 400) * 0.62, y), (180 - (y - 400) * 0.62 - 12, y + 14)], fill=(70, 70, 64), width=2)
        d.line([(180 + (y - 400) * 0.62, y), (180 + (y - 400) * 0.62 + 12, y + 14)], fill=(70, 70, 64), width=2)
    # telhado (quatro águas)
    d.polygon([(28, 270), (332, 270), (300, 215), (60, 215)], fill=(40, 30, 28))
    for k in range(10):
        x = 60 + k * 26
        d.line([(x, 215), (28 + k * 33.7, 270)], fill=(30, 22, 20))
    # corpo da casa
    d.rectangle([40, 270, 320, 372], fill=(78, 74, 66))
    # varanda comprida com pilares
    d.rectangle([34, 300, 326, 306], fill=(55, 52, 46))
    d.rectangle([34, 366, 326, 374], fill=(60, 57, 50))
    for x in range(44, 330, 40):
        d.rectangle([x, 300, x + 6, 366], fill=(110, 104, 92))
    # janelas altas de madeira
    luz = (255, 205, 90)
    apagada = (14, 14, 16)
    for k, x in enumerate(range(58, 316, 40)):
        acesa = todas_acesas
        cor = luz if acesa else apagada
        d.rectangle([x, 312, x + 22, 360], fill=cor, outline=(50, 34, 22), width=2)
        d.line([(x + 11, 312), (x + 11, 360)], fill=(50, 34, 22), width=1)
        if not acesa:
            d.rectangle([x - 5, 312, x - 1, 360], fill=(70, 46, 28))
            d.rectangle([x + 23, 312, x + 27, 360], fill=(70, 46, 28))
    # ala dos fundos com a janela da cozinha
    d.polygon([(255, 215), (300, 215), (320, 200), (290, 190)], fill=(48, 36, 32))
    d.rectangle([296, 228, 330, 270], fill=(66, 62, 56))
    d.rectangle([304, 238, 318, 258], fill=luz, outline=(40, 30, 20))
    # muro baixo com grade
    d.rectangle([10, 384, 350, 398], fill=(92, 88, 80))
    for x in range(14, 350, 7):
        d.line([(x, 368), (x, 384)], fill=(26, 26, 26), width=1)
    d.line([(10, 368), (350, 368)], fill=(26, 26, 26), width=2)
    # árvore escura
    d.rectangle([2, 250, 14, 390], fill=(12, 12, 12))
    for (x, y, r) in ((8, 200, 44), (36, 228, 36), (-14, 240, 40), (20, 170, 30)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=(10, 12, 10))
    # poste
    d.rectangle([346, 230, 350, 395], fill=(20, 20, 20))
    if vulto:
        vx, vy = 204, 306
        cor = (250, 250, 244)
        d.rectangle([vx - 16, 308, vx + 16, 366], fill=(8, 8, 8))           # porta aberta escura atrás
        d.ellipse([vx - 5, vy + 2, vx + 5, vy + 13], fill=(30, 28, 26))     # cabeça (cabelo escuro, sem rosto)
        d.polygon([(vx - 5, vy + 12), (vx + 5, vy + 12), (vx + 11, vy + 60), (vx - 11, vy + 60)], fill=cor)
        d.line([(vx - 5, vy + 16), (vx - 8, vy + 38)], fill=cor, width=2)
        d.line([(vx + 5, vy + 16), (vx + 8, vy + 38)], fill=cor, width=2)
    return img


def corredor(img, porta_aberta=0.0, vulto=None, t=0.0):
    """Corredor comprido em perspectiva de um ponto. vulto: None, 'longe' ou 'perto'."""
    d = ImageDraw.Draw(img)
    vx, vy = 180, 300
    d.rectangle([0, 0, W, H], fill=(28, 28, 26))
    fx0, fy0, fx1, fy1 = 152, 262, 208, 352    # parede do fundo
    d.polygon([(0, 0), (W, 0), (fx1, fy0), (fx0, fy0)], fill=(40, 40, 38))      # teto
    d.polygon([(0, H), (W, H), (fx1, fy1), (fx0, fy1)], fill=(52, 50, 46))      # chão
    d.polygon([(0, 0), (fx0, fy0), (fx0, fy1), (0, H)], fill=(66, 64, 58))      # parede esq
    d.polygon([(W, 0), (fx1, fy0), (fx1, fy1), (W, H)], fill=(60, 58, 52))      # parede dir
    d.rectangle([fx0, fy0, fx1, fy1], fill=(34, 33, 30))
    # tábuas do chão
    for k in range(-6, 7):
        d.line([(vx + k * 4.6, fy1), (vx + k * 70, H)], fill=(44, 42, 38))
    # portas laterais
    for z in (0.25, 0.55):
        for lado in (-1, 1):
            xa = vx + lado * (180 - 152) * (1 - z) + lado * 0
            x_ext = vx + lado * 180 * (1 - z * 0.9)
            x_int = vx + lado * 180 * (1 - (z + 0.12) * 0.9)
            ytop = lambda xx: vy - (abs(xx - vx) / 180) * 300 * 0.62
            ybot = lambda xx: vy + (abs(xx - vx) / 180) * 340 * 0.95
            d.polygon([(x_ext, ytop(x_ext)), (x_int, ytop(x_int)), (x_int, ybot(x_int)), (x_ext, ybot(x_ext))],
                      fill=(30, 22, 16))
    # porta do fundo
    px0, px1, py0 = 168, 192, 300
    d.rectangle([px0, py0, px1, fy1], fill=(70, 50, 34))
    if porta_aberta > 0:
        d.rectangle([px0, py0, px0 + (px1 - px0) * porta_aberta, fy1], fill=(4, 4, 4))
    # luminária apagada
    d.ellipse([vx - 14, 70, vx + 14, 84], fill=(80, 80, 76))
    # vulto de camisola
    if vulto:
        if vulto == "longe":
            cx, base, alt = 180, 350, 52
        else:
            cx, base, alt = 176, 470, 190
        cor = (200, 200, 192)
        cab = alt * 0.13
        d.ellipse([cx - cab * 0.7, base - alt, cx + cab * 0.7, base - alt + cab * 1.3], fill=(26, 24, 22))
        d.polygon([(cx - cab * 0.9, base - alt + cab * 0.9), (cx - cab * 0.4, base - alt + cab * 2.2),
                   (cx + cab * 0.4, base - alt + cab * 2.2), (cx + cab * 0.9, base - alt + cab * 0.9)], fill=(26, 24, 22))
        d.polygon([(cx - alt * 0.08, base - alt + cab * 1.25), (cx + alt * 0.08, base - alt + cab * 1.25),
                   (cx + alt * 0.17, base), (cx - alt * 0.17, base)], fill=cor)
        d.line([(cx - alt * 0.09, base - alt + cab * 1.6), (cx - alt * 0.12, base - alt * 0.45)], fill=cor, width=max(1, int(alt * 0.04)))
        d.line([(cx + alt * 0.09, base - alt + cab * 1.6), (cx + alt * 0.12, base - alt * 0.45)], fill=cor, width=max(1, int(alt * 0.04)))
    # goteira: gota caindo do teto até o chão, com anel
    per, fase = C.GOTA_PERIODO, C.GOTA_FASE
    tq = 0.45   # tempo de queda
    gx, gy_teto, gy_chao = 236, 130, 520
    ph = (t - fase) % per
    if per - tq <= ph:  # caindo
        s = (ph - (per - tq)) / tq
        y = gy_teto + (gy_chao - gy_teto) * s * s
        d.ellipse([gx - 2, y - 4, gx + 2, y + 3], fill=(190, 200, 210))
    else:
        if ph < 0.6:
            r = 4 + ph * 50
            d.ellipse([gx - r, gy_chao - r * 0.25, gx + r, gy_chao + r * 0.25], outline=(150, 160, 165), width=1)
        if ph > per - tq - 0.3:  # gota se formando
            d.ellipse([gx - 2, gy_teto - 1, gx + 2, gy_teto + 4], fill=(170, 180, 190))
    d.ellipse([gx - 22, gy_chao - 5, gx + 22, gy_chao + 5], fill=(46, 46, 44))  # mancha de água
    d.ellipse([gx - 10, gy_teto - 6, gx + 10, gy_teto + 2], fill=(52, 50, 44))   # infiltração no teto
    return img


def sala(img, t, ang, vu):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(46, 44, 40))
    d.rectangle([0, 430, W, H], fill=(36, 33, 30))
    d.rectangle([250, 120, 330, 260], fill=(14, 15, 18), outline=(70, 60, 50), width=3)   # janela escura
    d.line([(290, 120), (290, 260)], fill=(70, 60, 50), width=2)
    d.rectangle([20, 140, 90, 230], outline=(70, 66, 58), width=3)                          # quadro
    # mesa
    d.polygon([(30, 400), (330, 400), (350, 440), (10, 440)], fill=(70, 48, 30))
    d.rectangle([24, 440, 36, 540], fill=(50, 34, 22))
    d.rectangle([324, 440, 336, 540], fill=(50, 34, 22))
    # cadeira vazia
    d.rectangle([250, 380, 300, 470], fill=(40, 28, 18))
    d.rectangle([245, 330, 255, 470], fill=(40, 28, 18))
    gravador(img, 150, 330, 0.42, ang, vu)
    return img
