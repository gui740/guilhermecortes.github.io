"""O Minhocão do Pari desenhado por código.

Corpo cilíndrico e anelado, pele escura (quase negra / verde-musgo) coberta de
muco, cabeça rombuda e cega com olhos leitosos e boca circular — segundo as
descrições da tradição oral cuiabana.
"""
import numpy as np
from PIL import Image, ImageDraw

PELE = (26, 32, 25)
PELE_LUZ = (78, 92, 66)
ANEL = (14, 17, 13)
MUCO = (196, 214, 186)
OLHO = (222, 230, 214)


def _mistura(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def reamostra(pts, passo):
    """Reamostra uma polilinha em espaçamento ~constante; devolve (pts, s)."""
    pts = np.asarray(pts, np.float32)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    if s[-1] <= 0:
        return pts[:1], np.zeros(1)
    novo_s = np.arange(0, s[-1], passo)
    x = np.interp(novo_s, s, pts[:, 0])
    y = np.interp(novo_s, s, pts[:, 1])
    return np.stack([x, y], 1), novo_s


def desenha(espinha, raio, tam, fase=0.0, cabeca=True, boca=0.0, luz=(-0.5, -0.85),
            anel=None, escuro=1.0, olhos=True):
    """Desenha o corpo numa camada RGBA (tam = (W, H)).

    espinha: pontos do rabo para a cabeça. raio: número ou função de s (0..1).
    fase: desloca os anéis ao longo do corpo (corpo deslizando).
    boca: 0..1 abertura da boca circular. escuro: 0..1 multiplica a luz.
    """
    camada = Image.new("RGBA", tam, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    r_med = raio if np.isscalar(raio) else raio(0.5)
    pts, s = reamostra(espinha, max(1.5, r_med / 4))
    if len(pts) < 2:
        return camada
    tot = s[-1] if s[-1] > 0 else 1
    anel = anel or r_med * 0.9
    lx, ly = luz
    pele = _mistura((0, 0, 0), PELE, escuro)
    luzc = _mistura(pele, PELE_LUZ, escuro)
    anelc = _mistura((0, 0, 0), ANEL, escuro)
    medio = _mistura(pele, luzc, 0.5)
    rng = np.random.default_rng(int(abs(fase)) % 97 + len(pts))
    for k, ((x, y), sk) in enumerate(zip(pts, s)):
        u = sk / tot
        r = raio if np.isscalar(raio) else raio(u)
        if r < 0.8:
            continue
        # anéis irregulares, de largura variável, levemente mais escuros
        pos = (sk + fase) / anel
        larg = 0.14 + 0.06 * np.sin(np.floor(pos) * 2.3)
        no_anel = (pos % 1) < larg
        base = anelc if no_anel else pele
        d.ellipse([x - r, y - r, x + r, y + r], fill=base + (255,))
        # sombreado em 3 passos (volume liso, sem cara de brinquedo)
        for frac, cor in ((0.78, medio), (0.45, luzc)):
            rh = r * frac
            cx, cy = x + lx * r * (1 - frac) * 0.8, y + ly * r * (1 - frac) * 0.8
            c = _mistura(cor, anelc, 0.55) if no_anel else cor
            d.ellipse([cx - rh, cy - rh, cx + rh, cy + rh], fill=c + (255,))
        # brilho do muco, irregular
        if not no_anel and rng.random() < 0.10:
            mx = x + lx * r * rng.uniform(0.3, 0.6)
            my = y + ly * r * rng.uniform(0.3, 0.6)
            m = max(0.8, r * rng.uniform(0.05, 0.12))
            d.ellipse([mx - m, my - m, mx + m, my + m], fill=_mistura(luzc, MUCO, 0.7 * escuro) + (255,))
    if cabeca:
        (x, y) = pts[-1]
        (xa, ya) = pts[-min(len(pts), 6)]
        ang = np.arctan2(y - ya, x - xa)
        r = (raio if np.isscalar(raio) else raio(1.0)) * 1.08
        hx, hy = x + np.cos(ang) * r * 0.3, y + np.sin(ang) * r * 0.3
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=pele + (255,))
        for frac, cor in ((0.78, medio), (0.45, luzc)):
            rh = r * frac
            cx, cy = hx + lx * r * (1 - frac) * 0.8, hy + ly * r * (1 - frac) * 0.8
            d.ellipse([cx - rh, cy - rh, cx + rh, cy + rh], fill=cor + (255,))
        bx, by = hx + np.cos(ang) * r * 0.5, hy + np.sin(ang) * r * 0.5
        if boca > 0.05:
            # boca circular de lampreia, com anel de dentes pálidos
            rb = r * (0.15 + 0.45 * boca)
            d.ellipse([bx - rb * 1.15, by - rb * 1.15, bx + rb * 1.15, by + rb * 1.15], fill=anelc + (255,))
            d.ellipse([bx - rb, by - rb, bx + rb, by + rb], fill=(4, 4, 4, 255))
            nd = 18
            for j in range(nd):
                a = 2 * np.pi * j / nd
                for anel_d, fr in ((0.88, 0.09), (0.62, 0.07)):
                    dx, dy = np.cos(a + anel_d) * rb * anel_d, np.sin(a + anel_d) * rb * anel_d
                    m = max(0.7, rb * fr)
                    d.ellipse([bx + dx - m, by + dy - m, bx + dx + m, by + dy + m],
                              fill=_mistura((60, 60, 55), OLHO, 0.75 * escuro) + (255,))
        else:
            d.line([bx - r * 0.25, by, bx + r * 0.25, by], fill=anelc + (255,), width=max(1, int(r * 0.06)))
        if olhos:
            # olhos cegos: pequenos, leitosos, quase enterrados na pele
            px, py = -np.sin(ang), np.cos(ang)
            for lado in (-1, 1):
                ox = hx + np.cos(ang) * r * 0.05 + px * lado * r * 0.62
                oy = hy + np.sin(ang) * r * 0.05 + py * lado * r * 0.62
                ro = max(0.9, r * 0.075)
                d.ellipse([ox - ro * 1.6, oy - ro * 1.3, ox + ro * 1.6, oy + ro * 1.3], fill=anelc + (255,))
                d.ellipse([ox - ro, oy - ro * 0.8, ox + ro, oy + ro * 0.8],
                          fill=_mistura((90, 95, 85), OLHO, 0.8 * escuro) + (255,))
    return camada


def compoe(img, camada, y_agua=None, submerso=0.18, cor_agua=(20, 30, 40)):
    """Cola a camada na imagem; abaixo de y_agua o corpo fica quase todo coberto."""
    if y_agua is None:
        img.paste(camada, (0, 0), camada)
        return
    arr = np.asarray(camada).copy()
    ya = int(np.clip(y_agua, 0, arr.shape[0]))
    a = arr[..., 3].astype(np.float32)
    a[ya:] *= submerso
    arr[ya:, :, :3] = (arr[ya:, :, :3] * 0.5 + np.array(cor_agua) * 0.5).astype(np.uint8)
    arr[..., 3] = a.astype(np.uint8)
    c = Image.fromarray(arr, "RGBA")
    img.paste(c, (0, 0), c)
    # espuma onde o corpo rompe a água
    linha = np.asarray(camada)[max(0, ya - 2):ya + 1, :, 3].max(0) > 0
    d = ImageDraw.Draw(img)
    xs = np.nonzero(linha)[0]
    if len(xs):
        for x in xs[::2]:
            d.line([x - 2, ya, x + 2, ya], fill=(200, 210, 215))
        # borda das quebras de água
        quebras = np.nonzero(np.diff(linha.astype(int)))[0]
        for x in quebras:
            d.ellipse([x - 5, ya - 3, x + 5, ya + 2], fill=(215, 225, 230))


def arco(x0, x1, y_base, altura, n=120, deriva=0.0):
    """Espinha em arco (corcova saindo e entrando na água)."""
    u = np.linspace(0, 1, n)
    x = x0 + (x1 - x0) * u
    y = y_base - altura * np.sin(np.pi * u) + 6 * np.sin(u * 9 + deriva)
    return np.stack([x, y], 1)
