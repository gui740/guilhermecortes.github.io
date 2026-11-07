"""Desenhos procedurais das câmeras de segurança (canvas próprio de 360x640, depois escalado)."""
from PIL import ImageDraw

import config as C

W, H = 360, 640


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
    # vulto de camisola (silhueta, sem rosto: cabelo comprido cobre a cabeça)
    if vulto:
        # luz fraca no fundo do corredor recorta a silhueta
        d.rectangle([fx0, fy0, fx1, fy1], fill=(84, 84, 78))
        d.rectangle([px0, py0, px1, fy1], fill=(110, 108, 100))
        if vulto == "longe":
            cx, base, alt = 180, 352, 64
        else:
            cx, base, alt = 178, 500, 250
        u = alt / 100.0
        pele = (176, 176, 168)
        tecido = (214, 214, 206)
        cabelo = (10, 10, 10)
        topo = base - alt
        # camisola: ombros arredondados, abrindo até o chão
        d.polygon([(cx - 11 * u, topo + 20 * u), (cx + 11 * u, topo + 20 * u), (cx + 15 * u, topo + 30 * u),
                   (cx + 19 * u, base), (cx - 19 * u, base), (cx - 15 * u, topo + 30 * u)], fill=tecido)
        d.ellipse([cx - 15 * u, topo + 17 * u, cx + 15 * u, topo + 31 * u], fill=tecido)
        # dobras
        for k in (-8, -2, 5, 11):
            d.line([(cx + k * u * 0.6, topo + 40 * u), (cx + k * u, base)], fill=(186, 186, 178), width=max(1, int(u)))
        # braços caídos
        for lado in (-1, 1):
            d.polygon([(cx + lado * 14 * u, topo + 22 * u), (cx + lado * 17 * u, topo + 24 * u),
                       (cx + lado * 18 * u, topo + 60 * u), (cx + lado * 15 * u, topo + 60 * u)], fill=pele)
        # cabeça inclinada, coberta pelo cabelo comprido
        d.ellipse([cx - 8 * u, topo, cx + 7 * u, topo + 17 * u], fill=cabelo)
        d.polygon([(cx - 8 * u, topo + 8 * u), (cx + 7 * u, topo + 8 * u), (cx + 9 * u, topo + 34 * u),
                   (cx + 3 * u, topo + 38 * u), (cx - 4 * u, topo + 36 * u), (cx - 10 * u, topo + 30 * u)], fill=cabelo)
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


