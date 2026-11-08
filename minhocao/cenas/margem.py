"""Bloco 5b — câmera noturna na margem da Barra do Pari (4 cortes)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import config as C
import icones
import criatura
from .comum import VT, fonte, desenho, texto, rng_frame

Y_AGUA0, Y_AGUA1 = 262, 472     # faixa do rio
LUA = (252, 118)
X_BARR = 286                    # barranco à direita
HORAS = ["03:40:12", "03:41:37", "03:43:05", "03:44:51", "03:46:20"]

_rng0 = np.random.default_rng(C.SEED)
_ARVORES = [(x, 228 + _rng0.integers(-14, 10), _rng0.integers(10, 26)) for x in range(-10, C.W + 20, 14)]
_CAPIM = [(x, _rng0.integers(8, 34), _rng0.normal(0, 3)) for x in range(0, C.W, 3)]
_ESTRELAS = [(_rng0.integers(0, C.W), _rng0.integers(0, 200)) for _ in range(40)]
_PEDACOS = []  # pedaços do barranco: (x, y, w, h, atraso)
for k in range(9):
    _PEDACOS.append((X_BARR + 6 + (k % 3) * 22 + _rng0.integers(-4, 4),
                     332 + (k // 3) * 36 + _rng0.integers(-4, 4),
                     _rng0.integers(16, 26), _rng0.integers(16, 30),
                     0.15 + 0.11 * k + _rng0.random() * 0.1))


def g(v):
    v = int(np.clip(v, 0, 255))
    return (v, v, v)


def corte_atual(t):
    c = 0
    for k, tc in enumerate(C.T_CORTES_MARGEM):
        if t >= tc:
            c = k
    return c, t - C.T_CORTES_MARGEM[c]


def fundo(img, d, t, rng):
    # céu
    for y in range(0, Y_AGUA0):
        d.line([0, y, C.W, y], fill=g(52 - y * 0.08))
    for x, y in _ESTRELAS:
        if rng.random() > 0.1:
            d.point((x, y), fill=g(120))
    # lua + halo
    for r, v in [(34, 62), (24, 80), (15, 230)]:
        d.ellipse([LUA[0] - r, LUA[1] - r, LUA[0] + r, LUA[1] + r], fill=g(v))
    # mata da margem oposta (silhuetas: sarãs, capim alto)
    pts = [(0, Y_AGUA0 + 4)]
    for x, y, r in _ARVORES:
        pts.append((x, y + r * 0.2))
        d.ellipse([x - r, y - r * 0.8, x + r, y + r], fill=g(12))
    pts.append((C.W, Y_AGUA0 + 4))
    d.rectangle([0, 236, C.W, Y_AGUA0 + 4], fill=g(12))
    # rio
    d.rectangle([0, Y_AGUA0, C.W, Y_AGUA1], fill=g(26))


def ondulacoes(d, t, rng, agitacao=1.0):
    # reflexos em linhas horizontais
    for k in range(70):
        y = Y_AGUA0 + 6 + (k * 37) % (Y_AGUA1 - Y_AGUA0 - 8)
        x = (k * 97 + t * (14 + k % 5) * 3) % (C.W + 60) - 30
        ln = 8 + (k * 13) % 26
        d.line([x, y, x + ln, y], fill=g(44 + (k % 3) * 8))
    # reflexo da lua (coluna de traços quebrados)
    for y in range(Y_AGUA0 + 4, Y_AGUA1, 5):
        w = 6 + 10 * (1 - (y - Y_AGUA0) / 260) + 6 * np.sin(y * 0.3 + t * 5) * agitacao
        x = LUA[0] + 4 * np.sin(y * 0.11 + t * 2.5) * agitacao
        d.line([x - w, y, x + w, y], fill=g(150 + 60 * np.sin(y * 0.7 + t * 9)))


def barranco(d, t, faltando=0.0):
    # parede de terra à direita
    topo = 318
    poly = [(X_BARR, Y_AGUA1), (X_BARR + 8, topo + 30), (X_BARR + 4, topo), (C.W, topo - 8), (C.W, Y_AGUA1)]
    d.polygon(poly, fill=g(40))
    for k in range(22):
        x = X_BARR + 8 + k * 3.3
        d.line([x, topo + 4 + (k * 7) % 11, x - 3 + (k % 3), Y_AGUA1], fill=g(30 + (k * 13) % 18))
    for k in range(12):
        y = topo + 14 + k * 12
        d.line([X_BARR + 6, y, C.W, y + (k % 3) - 1], fill=g(33))
    for k in range(0, 76, 3):
        d.line([X_BARR + 4 + k, topo, X_BARR + 2 + k, topo - 6 - (k * 7) % 9], fill=g(16))


def margem_perto(d, t, rng):
    # chão da margem de cá
    d.polygon([(0, 486), (120, 474), (250, 480), (C.W, 470), (C.W, C.H), (0, C.H)], fill=g(9))
    for x, h, inc in _CAPIM:
        y0 = 478 + (x % 7)
        d.line([x, y0, x + inc + 2 * np.sin(t * 2 + x), y0 - h], fill=g(4))
    # árvore grande torta à esquerda
    d.polygon([(0, C.H), (0, 300), (18, 210), (40, 120), (30, 60), (48, 0), (70, 0), (60, 80),
               (66, 160), (44, 260), (40, 360), (54, 500), (64, C.H)], fill=g(3))
    for (x0, y0, x1, y1, w) in [(42, 140, 130, 90, 7), (100, 108, 168, 112, 4), (52, 210, 150, 196, 5),
                                (36, 60, 120, 18, 5), (60, 300, 110, 280, 4)]:
        d.line([x0, y0, x1, y1], fill=g(3), width=w)
    for cx, cy, r in [(130, 84, 26), (170, 108, 18), (150, 190, 22), (110, 20, 30)]:
        d.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=g(5))
    # estaca
    d.rectangle([108, 452, 114, 500], fill=g(20))


def canoa(img, d, cx, cy, ang=0.0, virada=False):
    """Canoa de madeira com estrelas pintadas no casco."""
    w, h = 112, 26
    cap = Image.new("RGBA", (w + 20, h * 3), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cap)
    if not virada:
        cd.polygon([(4, h), (w + 14, h), (w + 4, h + 18), (16, h + 18)], fill=g(62) + (255,))
        cd.line([(4, h), (w + 14, h)], fill=g(130) + (255,), width=2)
        cd.rectangle([54, h - 2, 64, h + 4], fill=g(70) + (255,))  # banco
        cd.line([(36, h - 8), (90, h + 10)], fill=g(80) + (255,), width=2)  # remo
        estrelas_y = h + 9
    else:
        cd.chord([2, h - 14, w + 16, h + 22], 180, 360, fill=g(66) + (255,))
        cd.arc([2, h - 14, w + 16, h + 22], 190, 350, fill=g(140) + (255,), width=2)
        cd.line([(10, h + 4), (w + 8, h + 4)], fill=g(20) + (255,), width=2)
        cd.line([(14, h - 4), (w + 6, h - 4)], fill=g(70) + (255,), width=1)
        estrelas_y = h - 2
    for sx in (30, 60, 90):
        cd.polygon([(sx, estrelas_y - 4), (sx + 2, estrelas_y - 1), (sx + 5, estrelas_y - 1),
                    (sx + 3, estrelas_y + 1), (sx + 4, estrelas_y + 4), (sx, estrelas_y + 2),
                    (sx - 4, estrelas_y + 4), (sx - 3, estrelas_y + 1), (sx - 5, estrelas_y - 1),
                    (sx - 2, estrelas_y - 1)], fill=g(170) + (255,))
    cap = cap.rotate(ang, resample=Image.NEAREST)
    img.paste(cap, (int(cx - cap.width / 2), int(cy - cap.height / 2)), cap)


def corcova(img, d, t, tc, rng):
    """Corcova longa, anelada, passando rente à superfície (maior que a tela)."""
    yc = 392
    x0 = -420 + tc * 170
    esp = criatura.arco(x0, x0 + 900, yc + 34, 70, deriva=tc * 2)
    cam = criatura.desenha(esp, 24, img.size, fase=tc * 120, cabeca=False)
    criatura.compoe(img, cam, yc, submerso=0.25, cor_agua=(26, 26, 26))
    d = desenho(img)
    onda_margem(d, tc, rng)


def corcova_antiga(d, t, tc, rng):
    yc = 392
    vel = 150.0
    desloc = tc * vel
    xs = np.arange(-4, C.W + 4, 2)
    fase = (xs - desloc + 260) / 520.0
    amp = 30 * np.clip(np.sin(np.pi * np.clip(fase, 0, 1)), 0, 1) ** 0.8
    amp *= np.clip(tc / 0.3, 0, 1)
    topo = yc - amp
    # onda à frente (crista clara) e esteira
    for k, x in enumerate(xs):
        if amp[k] > 1:
            d.line([x, topo[k], x, yc + 6], fill=g(7), width=2)
    for k in range(1, len(xs)):
        if amp[k] > 1:
            d.line([xs[k - 1], topo[k - 1] + 2, xs[k], topo[k] + 2], fill=g(70), width=1)
    # anéis de pele lisa
    for anel in range(-30, 30):
        x = anel * 24 + (desloc % 24)
        k = int((x + 4) / 2)
        if 0 <= k < len(xs) and amp[k] > 4:
            d.arc([x - 6, topo[k] - 1, x + 6, yc + 4], 200, 340, fill=g(36), width=1)
    # espuma onde a corcova rompe a água
    for k in range(0, len(xs), 3):
        if 1 < amp[k] < 8:
            d.line([xs[k] - 3, yc + 4, xs[k] + 3, yc + 4], fill=g(150))
    onda_margem(d, tc, rng)


def onda_margem(d, tc, rng):
    onda = np.clip((tc - 0.8) / 0.4, 0, 1)
    if onda > 0:
        yw = Y_AGUA1 - 6 - 18 * np.sin(np.pi * onda)
        d.line([0, yw, C.W, yw + 3], fill=g(160), width=3)
        for _ in range(30):
            x = rng.integers(60, C.W)
            d.point((x, yw - rng.integers(0, 16)), fill=g(200))


def desmoronamento(img, d, t, tc, rng):
    # buraco que fica no barranco
    for (x, y, w, h, atraso) in _PEDACOS:
        if tc > atraso:
            d.rectangle([x, y, x + w, y + h], fill=g(26))
    # pedaços caindo
    for k, (x, y, w, h, atraso) in enumerate(_PEDACOS):
        dt = tc - atraso
        if dt < 0:
            continue
        yy = y + 0.5 * 900 * dt ** 2
        xx = x - 40 * dt
        if yy < Y_AGUA1 - 8:
            ang = dt * (60 + 30 * (k % 3))
            p = Image.new("RGBA", (w, h), g(70) + (255,))
            ImageDraw.Draw(p).line([0, 2, w, 2], fill=g(20) + (255,), width=2)
            p = p.rotate(ang, expand=True, resample=Image.NEAREST)
            img.paste(p, (int(xx), int(yy)), p)
        else:
            # respingo + nuvem de terra
            s = dt - np.sqrt(2 * (Y_AGUA1 - 8 - y) / 900)
            if s < 0.6:
                for _ in range(14):
                    ang = rng.uniform(np.pi * 1.1, np.pi * 1.9)
                    r = s * rng.uniform(40, 120)
                    d.point((xx + np.cos(ang) * r, Y_AGUA1 - 10 + np.sin(ang) * r + 200 * s ** 2), fill=g(210))
    poeira = np.clip((tc - 0.3) / 1.2, 0, 1)
    if poeira > 0:
        for k in range(26):
            r = 10 + poeira * (20 + k % 7 * 5)
            cx = X_BARR + 20 + (k * 29) % 80 - poeira * 30 + 10 * np.sin(k + tc)
            cy = Y_AGUA1 - 20 - poeira * (k * 13 % 70)
            d.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=g(90 - 40 * poeira))


def revelacao(img, t, tc, rng):
    """Corte final: a cabeça e o pescoço sobem na frente da lua."""
    d = desenho(img)
    sub = min(1.0, tc / 1.3)
    sub = 1 - (1 - sub) ** 2.2
    yb = 440
    yh = yb - 340 * sub
    u = np.linspace(0, 1, 70)
    xs = 236 + 22 * np.sin(u * 3.2 + tc * 1.5) * u + 14 * u
    ys = yb + 60 - (yb + 60 - yh) * u
    esp = np.stack([xs, ys], 1)
    boca = np.clip((tc - 1.35) / 0.4, 0, 1)
    cam = criatura.desenha(esp, lambda v: 17 + 7 * v, img.size, fase=tc * 25, boca=boca,
                           luz=(0.35, -0.9))
    # anéis de água em volta da base
    for k in range(4):
        rr = ((tc * 40 + k * 18) % 72) + 10
        d.ellipse([236 - rr * 1.6, yb - rr * 0.25, 236 + rr * 1.6, yb + rr * 0.25], outline=g(120 - rr))
    criatura.compoe(img, cam, yb, submerso=0.2, cor_agua=(26, 26, 26))
    d = desenho(img)
    if tc < 1.3:
        for k in range(10):
            x = 226 + k * 3
            yy = yh + 20 + ((tc * 300 + k * 41) % max(10, yb - yh - 20))
            d.line([x, yy, x, yy + 7], fill=g(190))
    canoa(img, d, 110, 404, ang=-3 + np.sin(t * 1.2), virada=True)


def cena(t, i):
    rng = rng_frame(i, 31)
    c, tc = corte_atual(t)
    img = Image.new("RGB", (C.W, C.H), (0, 0, 0))
    d = desenho(img)
    fundo(img, d, t, rng)
    ondulacoes(d, t, rng, agitacao=2.0 if c == 1 and tc > 0.5 else 1.0)
    barranco(d, t)
    if c == 0:
        canoa(img, d, 160, 446, ang=1.5 * np.sin(t * 1.6))
        d.line([(110, 456), (118, 470), (112, 482)], fill=g(60))
    elif c == 1:
        corcova(img, d, t, tc, rng)
        d = desenho(img)
        bob = 1.5 + 9 * np.clip((tc - 0.7) / 0.4, 0, 1)
        canoa(img, d, 160, 446 - 3 * np.sin(tc * 9) * (bob / 9), ang=bob * np.sin(tc * 7))
        d.line([(110, 456), (118, 470), (112, 482)], fill=g(60))
    elif c == 2:
        canoa(img, d, 200 + tc * 12, 404, ang=-4 + np.sin(t * 1.2), virada=True)
        # corda solta pendurada na estaca
        d.line([(111, 456), (124, 474), (132, 470)], fill=g(60))
    elif c == 3:
        desmoronamento(img, d, t, tc, rng)
        d.line([(111, 456), (124, 474), (132, 470)], fill=g(60))
    else:
        revelacao(img, t, tc, rng)
        d = desenho(img)
        d.line([(111, 456), (124, 474), (132, 470)], fill=g(60))
    margem_perto(d, t, rng)
    # leve desfoque de câmera barata
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    if c == 3 and tc > 0.2:  # tremor de câmera
        dx, dy = rng.integers(-5, 6, 2)
        img = Image.fromarray(np.roll(np.asarray(img), (dy, dx), (0, 1)))
    return img


def osd(t, i, img):
    c, tc = corte_atual(t)
    d = desenho(img)
    f = fonte(VT, 24)
    texto(d, (16, C.SAFE_TOP + 2), "CAM BARRA DO PARI", f, (230, 255, 230), sombra=(0, 0, 0))
    hh = HORAS[c]
    seg = int(hh[-2:]) + int(tc)
    texto(d, (16, C.SAFE_TOP + 24), hh[:-2] + f"{seg:02d}", f, (230, 255, 230), sombra=(0, 0, 0))
    if (i // 15) % 2 == 0:
        d.ellipse([C.W - 72, C.SAFE_TOP + 9, C.W - 60, C.SAFE_TOP + 21], fill=(230, 40, 40))
    texto(d, (C.W - 56, C.SAFE_TOP + 2), "REC", f, (230, 255, 230), sombra=(0, 0, 0))
    texto(d, (16, C.SAFE_BOTTOM - 28), "IV  ·  LP", f, (230, 255, 230), sombra=(0, 0, 0))
    if c >= 1 and (i // 7) % 2 == 0:
        nome = "alerta" if c not in (2, 4) else "minhocao"
        icones.cola_icone(img, nome, C.W - 30, C.SAFE_BOTTOM - 22, 26)


def estilo(t):
    return C.FX_INTENSIDADE["margem"], "noturna"
