"""00:05–00:30 — "CONHEÇA SEU PATRIMÔNIO" e a fita começando a estragar.

As duas cenas (programete e corrupção) usam o mesmo desenho, parametrizado
pelo tempo global: céu vira noite, janelas acendem, o sorriso estica.
"""
import math

import numpy as np
from PIL import Image

import config as C
import icones
from config import FPS, H, W

from .comum import (bloco_centro, desenho, ease, foto, fonte, gradiente_v, largura, lerp,
                    lerp_cor, nova, quebrar, rng_frame, texto)

rampa = C.rampa

PAINEL = (14, 128, 346, 300)       # fachada
CARD_Y = 312
MASC = (92, 470)                   # centro do mascote
_G1 = gradiente_v(W, H, (255, 214, 90), (245, 120, 30))
_G2 = gradiente_v(W, H, (255, 236, 140), (255, 160, 60))
_rng_fixo = np.random.default_rng(C.SEED + 11)
_ESTRELAS = [(int(_rng_fixo.integers(PAINEL[0] + 4, PAINEL[2] - 4)),
              int(_rng_fixo.integers(PAINEL[1] + 4, PAINEL[1] + 50))) for _ in range(26)]
_ORDEM_JANELAS = list(_rng_fixo.permutation(12))


# ------------------------------------------------------------------ fundo
def _fundo(T, c):
    """Raios de sol girando (programa educativo dos anos 80)."""
    from PIL import ImageDraw
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    cx, cy = W / 2, 330
    giro = (min(T, C.T_CORR + c * 2) - C.T_PATRIMONIO) * 0.35
    n = 18
    for i in range(n):
        a0 = giro + i * 2 * math.pi / n
        a1 = a0 + math.pi / n
        md.polygon([(cx, cy), (cx + 900 * math.cos(a0), cy + 900 * math.sin(a0)),
                    (cx + 900 * math.cos(a1), cy + 900 * math.sin(a1))], fill=255)
    img = Image.composite(_G2, _G1, mask)
    if c > 0:
        arr = np.asarray(img).astype(np.float32)
        g = arr.mean(axis=2, keepdims=True)
        arr = g + (arr - g) * (1 - 0.75 * c)
        arr *= (1 - 0.6 * c)
        arr[..., 0] += 25 * c
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return img


# ------------------------------------------------------------------ fachada
def _fachada(img, noite, janelas_acesas, fi):
    x0, y0, x1, y1 = PAINEL
    pw, ph = x1 - x0, y1 - y0
    d = desenho(img)
    ft = foto("fachada", pw, ph)
    if ft is not None:
        arr = _foto_noite(ft, noite, janelas_acesas, fi)
        img.paste(Image.fromarray(arr), (x0, y0))
    else:
        ceu = gradiente_v(pw, ph, lerp_cor((80, 160, 235), (6, 6, 22), noite),
                          lerp_cor((190, 228, 252), (40, 18, 40), noite))
        img.paste(ceu, (x0, y0))
        d = desenho(img)
        if noite < 0.6:
            icones.colar_animado(img, "sol", x1 - 34, y0 + 26, 2, 99)
            if noite > 0:
                d.rectangle([x1 - 52, y0 + 8, x1 - 16, y0 + 44],
                            fill=lerp_cor((150, 200, 245), (20, 14, 36), noite))
        else:
            for sx, sy in _ESTRELAS:
                if (sx * 7 + fi // 6) % 5:
                    d.point((sx, sy), fill=(230, 230, 255))
            d.ellipse([x1 - 46, y0 + 12, x1 - 24, y0 + 34], fill=(200, 60, 40))
        chao = y1 - 22
        parede_topo = y0 + 62
        ocre = lerp_cor((224, 192, 124), (70, 55, 50), noite)
        base = lerp_cor((180, 148, 92), (45, 36, 34), noite)
        cornija = lerp_cor((245, 230, 196), (90, 80, 76), noite)
        telha = lerp_cor((172, 82, 52), (60, 28, 24), noite)
        # chão (rua)
        d.rectangle([x0, chao, x1, y1], fill=lerp_cor((196, 168, 118), (36, 30, 34), noite))
        # telhado baixo
        d.polygon([(x0, parede_topo), (x0 + 8, parede_topo - 9), (x1 - 8, parede_topo - 9),
                   (x1, parede_topo)], fill=telha)
        # muro/fachada longa e térrea
        d.rectangle([x0, parede_topo, x1, chao], fill=ocre)
        d.rectangle([x0, parede_topo, x1, parede_topo + 3], fill=cornija)
        d.rectangle([x0, chao - 8, x1, chao], fill=base)
        # janelas em arco
        jan = []
        for lado in (0, 1):
            for j in range(6):
                jx = (x0 + 12 + j * 21) if lado == 0 else (x1 - 22 - j * 21)
                jan.append(jx)
        acesas = set(_ORDEM_JANELAS[:janelas_acesas])
        rng = rng_frame(fi, 9)
        for idx, jx in enumerate(jan):
            jy0, jy1 = parede_topo + 20, chao - 14
            # pilastra
            d.rectangle([jx - 5, parede_topo + 4, jx - 4, chao - 9], fill=cornija)
            if idx in acesas:
                fl = int(110 + 50 * rng.random())
                d.rectangle([jx - 2, jy0 - 2, jx + 12, jy1 + 2], fill=(150, 60, 10))
                cor = (255, fl + 40, 25)
            else:
                cor = lerp_cor((70, 52, 40), (16, 12, 14), noite)
            d.ellipse([jx, jy0 - 6, jx + 10, jy0 + 6], fill=cor)
            d.rectangle([jx, jy0, jx + 10, jy1], fill=cor)
            d.line([jx + 5, jy0 - 4, jx + 5, jy1], fill=lerp_cor((40, 30, 24), (8, 6, 6), noite))
            d.rectangle([jx - 2, jy1, jx + 12, jy1 + 2], fill=cornija)
        # portão central com frontão triangular e insígnia em relevo
        cx = (x0 + x1) // 2
        d.rectangle([cx - 26, parede_topo - 4, cx + 26, chao], fill=lerp_cor((236, 208, 146), (80, 64, 58), noite))
        d.polygon([(cx - 32, parede_topo - 2), (cx, parede_topo - 30), (cx + 32, parede_topo - 2)],
                  fill=cornija, outline=base)
        d.ellipse([cx - 7, parede_topo - 21, cx + 7, parede_topo - 7], fill=ocre, outline=base)
        d.polygon([(cx - 4, parede_topo - 15), (cx - 4, parede_topo - 19), (cx - 2, parede_topo - 17),
                   (cx, parede_topo - 20), (cx + 2, parede_topo - 17), (cx + 4, parede_topo - 19),
                   (cx + 4, parede_topo - 15)], fill=base)
        porta = (255, 140, 30) if janelas_acesas >= 11 else lerp_cor((96, 56, 30), (20, 12, 10), noite)
        d.ellipse([cx - 15, parede_topo + 16, cx + 15, parede_topo + 40], fill=porta)
        d.rectangle([cx - 15, parede_topo + 28, cx + 15, chao], fill=porta)
        d.line([cx, parede_topo + 18, cx, chao], fill=(30, 18, 10))
    # moldura do quadro
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=(110, 50, 15), width=3)
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=(255, 250, 230), width=1)


def _caixas_foto():
    import json
    import os
    p = os.path.join(C.FOTOS_DIR, "fachada_janelas.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


_CAIXAS = _caixas_foto()


def _foto_noite(ft, noite, janelas_acesas, fi):
    """Foto real da fachada: o céu azul vira noite e as janelas acendem em laranja de forja."""
    arr = np.asarray(ft).astype(np.float32)
    h, w = arr.shape[:2]
    if noite > 0:
        lum = arr.mean(axis=2, keepdims=True)
        # céu (azul saturado) escurece mais que o prédio
        ceu = np.clip((arr[..., 2:3] - arr[..., 0:1] - 40) / 60, 0, 1)
        noturno = lum * np.array([0.35, 0.33, 0.55], np.float32) * (1 - ceu) + \
            np.array([8, 6, 22], np.float32) * ceu
        arr = arr * (1 - noite) + noturno * noite
    if janelas_acesas:
        rng = rng_frame(fi, 5)
        caixas = []
        if _CAIXAS:
            caixas = [b for b in _CAIXAS["janelas"]] + [_CAIXAS["portao"]]
        else:  # foto do usuário sem mapa de janelas: faixa genérica
            caixas = [[0.1 + 0.16 * j, 0.6, 0.18 + 0.16 * j, 0.85] for j in range(6)]
        n = min(len(caixas), max(1, int(janelas_acesas / 12 * len(caixas) + 0.5)))
        ordem = [0, 3, 5, 1, 4, 2, 6, 7, 8, 9][:len(caixas)]
        for k in ordem[:n]:
            if k >= len(caixas):
                continue
            bx0, by0, bx1, by1 = caixas[k]
            xa, xb, ya, yb = int(bx0 * w), int(bx1 * w), int(by0 * h), int(by1 * h)
            reg = arr[ya:yb, xa:xb]
            lum = reg.mean(axis=2, keepdims=True)
            escuro = np.clip((150 - lum) / 120, 0, 1)        # o vão escuro acende, a grade fica
            fogo = np.array([255, 120 + 50 * rng.random(), 25], np.float32)
            arr[ya:yb, xa:xb] = reg * (1 - escuro) + fogo * escuro
    return np.clip(arr, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ mascote
def _mascote(img, cx, cy, s, boca, c):
    d = desenho(img)
    madeira, madeira_esc = (112, 70, 34), (58, 34, 14)
    bronze, bronze_esc, bronze_cl = (204, 128, 56), (110, 60, 20), (238, 176, 96)
    # rodas e carreta
    d.rectangle([cx - 44 * s, cy + 16 * s, cx + 40 * s, cy + 30 * s], fill=madeira, outline=madeira_esc, width=2)
    for wx in (cx - 30 * s, cx + 28 * s):
        r = 18 * s
        d.ellipse([wx - r, cy + 34 * s - r, wx + r, cy + 34 * s + r], fill=madeira, outline=madeira_esc, width=2)
        for a in range(4):
            ang = a * math.pi / 4
            d.line([wx - r * math.cos(ang), cy + 34 * s - r * math.sin(ang),
                    wx + r * math.cos(ang), cy + 34 * s + r * math.sin(ang)], fill=madeira_esc, width=2)
        d.ellipse([wx - 5 * s, cy + 29 * s, wx + 5 * s, cy + 39 * s], fill=(60, 60, 64))
    # cascavel (botão traseiro)
    d.ellipse([cx - 78 * s, cy - 9 * s, cx - 58 * s, cy + 11 * s], fill=bronze, outline=bronze_esc, width=2)
    # tubo
    d.rounded_rectangle([cx - 64 * s, cy - 34 * s, cx + 52 * s, cy + 30 * s], radius=int(28 * s),
                        fill=bronze, outline=bronze_esc, width=2)
    d.rounded_rectangle([cx - 50 * s, cy - 29 * s, cx + 40 * s, cy - 20 * s], radius=int(4 * s), fill=bronze_cl)
    # boca do canhão
    d.ellipse([cx + 42 * s, cy - 38 * s, cx + 70 * s, cy + 34 * s], fill=(176, 104, 42), outline=bronze_esc, width=2)
    d.ellipse([cx + 50 * s, cy - 24 * s, cx + 64 * s, cy + 20 * s], fill=(36, 18, 8))
    fx = cx - 8 * s
    # bochechas
    if c < 0.3:
        for bx in (fx - 30 * s, fx + 30 * s):
            d.ellipse([bx - 6 * s, cy + 2 * s, bx + 6 * s, cy + 10 * s], fill=(236, 120, 100))
    # olhos
    for ex in (fx - 18 * s, fx + 18 * s):
        ey = cy - 10 * s
        rx, ry = 11 * s, 13 * s
        d.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        pr = lerp(5, 11.5, min(1, c / 0.6)) * s
        pry = lerp(6, 13.5, min(1, c / 0.6)) * s
        px = ex + lerp(2, 0, min(1, c / 0.6)) * s
        py = ey + lerp(2, 0, min(1, c / 0.6)) * s
        d.ellipse([px - pr, py - pry, px + pr, py + pry], fill=(0, 0, 0))
        if c < 0.55:
            d.ellipse([px - 3 * s, py - 4 * s, px, py - 1 * s], fill=(255, 255, 255))
    # boca: sorriso que estica além do rosto
    my = cy + 12 * s
    w = (26 + 170 * c ** 1.3) * s
    h = (5 + 11 * boca + 22 * c) * s
    d.pieslice([fx - w / 2, my - h, fx + w / 2, my + h], 0, 180, fill=(70, 10, 12), outline=(0, 0, 0), width=2)
    if c > 0.25:
        n = int(6 + 18 * c)
        for i in range(n):
            tx = fx - w / 2 + (i + 0.5) * w / n
            d.rectangle([tx - w / n * 0.35, my + 1, tx + w / n * 0.35, my + 3 * s + 1], fill=(235, 230, 210))
        # cantos subindo
        d.line([fx - w / 2, my, fx - w / 2 - 8 * c * s, my - 14 * c * s], fill=(0, 0, 0), width=2)
        d.line([fx + w / 2, my, fx + w / 2 + 8 * c * s, my - 14 * c * s], fill=(0, 0, 0), width=2)
    elif boca > 0.2:
        d.ellipse([fx - 6 * s, my + h * 0.3, fx + 6 * s, my + h * 0.9], fill=(220, 70, 80))


def _balao(img, txt, rng=None, glitch=0.0):
    d = desenho(img)
    x0, y0, x1 = 168, 400, 350
    linhas = quebrar(txt, 13, x1 - x0 - 16)
    y1 = y0 + 12 + len(linhas) * 17
    d.polygon([(x0 + 4, y1 - 14), (x0 - 18, y1 + 14), (x0 + 22, y1 - 2)], fill=(0, 0, 0))
    d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    d.polygon([(x0 + 6, y1 - 15), (x0 - 13, y1 + 9), (x0 + 21, y1 - 4)], fill=(255, 255, 255))
    y = y0 + 8
    for ln in linhas:
        if glitch and rng is not None:
            ln = "".join(ch if rng.random() > glitch else "#%@?!0"[int(rng.integers(0, 6))] for ch in ln)
            dx = int(rng.integers(-3, 4) * glitch * 2)
        else:
            dx = 0
        texto(d, ((x0 + x1) // 2 + dx, y), ln, 13, (20, 10, 10), anchor="ma")
        y += 17


def _cartao(img, nome_icone, txt, frames_desde, corrompido=False, rng=None, cor_txt=(70, 34, 10)):
    d = desenho(img)
    linhas = quebrar(txt, 14, 252)
    h = max(70, 20 + len(linhas) * 19)
    slide = (1 - ease(frames_desde / 6.0)) * W
    x0, x1 = 12 + slide, 348 + slide
    y0 = CARD_Y
    d.rectangle([x0 + 5, y0 + 5, x1 + 5, y0 + h + 5], fill=(130, 50, 0))
    d.rectangle([x0, y0, x1, y0 + h], fill=(255, 246, 222), outline=(120, 60, 20), width=3)
    icones.colar_animado(img, nome_icone, x0 + 38, y0 + h / 2, 3, frames_desde, corrompido, rng)
    y = y0 + (h - len(linhas) * 19) / 2 + 2
    for ln in linhas:
        texto(d, (x0 + 74, y), ln, 14, cor_txt)
        y += 19


def _titulo(img, T, c, rng):
    d = desenho(img)
    entrada = ease((T - C.T_PATRIMONIO) / 0.5)
    y = int(64 - (1 - entrada) * 80)
    if T - C.T_PATRIMONIO < 0.8:
        y += int(math.sin((T - C.T_PATRIMONIO) * 18) * 4 * (1 - entrada))
    for i, ln in enumerate(C.TITULO):
        if c > 0.2 and rng.random() < c * 0.25:
            ln = "".join(ch if rng.random() > 0.15 else "#" for ch in ln)
        texto(d, (W // 2, y + i * 30), ln, 26, lerp_cor((255, 252, 214), (200, 190, 170), c),
              sombra=lerp_cor((150, 40, 0), (40, 0, 0), c), off=(3, 3), anchor="ma")


def _morph(prog, rng):
    src = C.CARTOES[-1][1]
    dst = C.CARTAO_CORROMPIDO
    n = max(len(src), len(dst))
    src, dst = src.ljust(n), dst.ljust(n)
    k = int(prog * n)
    out = []
    for i in range(n):
        if i < k:
            out.append(dst[i])
        elif i < k + 3 and prog > 0:
            out.append("#@%&?$0X"[int(rng.integers(0, 8))])
        else:
            out.append(src[i])
    return "".join(out).strip()


# ------------------------------------------------------------------ cenas
def desenhar(T, fi):
    rng = rng_frame(fi, 1)
    tc = C.T_CORR
    c_masc = rampa(T, tc + 0.3, tc + 2.9)
    c_fundo = rampa(T, tc + 0.3, tc + C.DUR_CORR - 0.5)
    noite = rampa(T, tc + 0.2, tc + 2.3)
    janelas = int(rampa(T, tc + 1.6, tc + C.DUR_CORR - 0.3) * 12)

    if C.SUBLIMINAR_T <= T < C.SUBLIMINAR_T + 2.0 / FPS:
        img = nova((0, 0, 0))
        d = desenho(img)
        bloco_centro(d, W // 2, 270, C.SUBLIMINAR_TXT, 24, (220, 0, 0), maxw=320, entre=8)
        return img

    img = _fundo(T, c_fundo)
    _titulo(img, T, c_fundo, rng)
    # fachada entra com cortina
    rev = ease((T - C.T_PATRIMONIO - 0.2) / 0.6)
    if rev > 0:
        _fachada(img, noite, janelas, fi)
        if rev < 1:
            d = desenho(img)
            d.rectangle([PAINEL[0] - 5 + (PAINEL[2] - PAINEL[0] + 10) * rev, PAINEL[1] - 5,
                         PAINEL[2] + 5, PAINEL[3] + 5], fill=(245, 150, 50))

    # cartões
    if T >= C.CARTOES_INICIO:
        i = C.indice_em(T, C.CARTOES_T)
        t0 = C.CARTOES_T[i]
        nome, txt = C.CARTOES[i]
        fr = (T - t0) * FPS
        if i == len(C.CARTOES) - 1 and T >= C.MORPH_T[0]:
            prog = rampa(T, *C.MORPH_T)
            txt = _morph(prog, rng)
            cor = lerp_cor((70, 34, 10), (150, 0, 0), prog)
            _cartao(img, nome, txt, 99, corrompido=True, rng=rng, cor_txt=cor)
        else:
            _cartao(img, nome, txt, fr - 0.0, corrompido=False, rng=rng)

    # mascote quicando no ritmo da música
    entra = ease((T - C.T_PATRIMONIO - 0.2) / 0.45)
    pos = C.musica_pos(T)
    beat = 60.0 / C.BPM
    quique = abs(math.sin(math.pi * pos / beat)) * 7 * (1 - 0.6 * c_masc)
    mx = MASC[0] - (1 - entra) * 220
    my = MASC[1] - quique
    if c_masc > 0.5:
        mx += rng.integers(-1, 2)
    _mascote(img, mx, my, 0.95, C.boca(T), c_masc)

    # balões de fala
    if C.FALA_OLA_T[0] <= T < C.FALA_OLA_T[1]:
        _balao(img, C.FALA_OLA)
    elif C.FALA_FINAL_T[0] <= T < C.FALA_FINAL_T[1]:
        g = rampa(T, tc + 0.3, tc + 1.5) * 0.6
        if not (g > 0.3 and rng.random() < 0.2):
            _balao(img, C.FALA_FINAL, rng, g)
    return img


def cena(t, fi):
    return desenhar(fi / FPS, fi)


def cena_corrupcao(t, fi):
    return desenhar(fi / FPS, fi)
