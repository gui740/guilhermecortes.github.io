"""00:30–00:50 — "INSTRUÇÕES PARA VISITANTES APÓS O FECHAMENTO"."""
import numpy as np
from PIL import Image

import config as C
import icones
from config import FPS, H, W

from .comum import bloco_centro, desenho, foto, fonte, largura, quebrar, rng_frame, texto

MARINHO = (14, 22, 70)
BRANCO = (240, 240, 240)


def _fundo(i):
    img = Image.new("RGB", (W, H), MARINHO)
    nome = {4: "porao", 5: "varanda"}.get(i)
    if nome:
        ft = foto(nome)
        if ft is not None:
            arr = np.asarray(ft.convert("L")).astype(np.float32)[..., None] / 255.0
            base = np.array(MARINHO, np.float32)
            arr = base + arr * np.array([30, 34, 60], np.float32)
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return img


def _cabecalho(d):
    y = 66
    for ln in quebrar(C.REGRAS_CAB, 12, 330):
        texto(d, (W // 2, y), ln, 12, BRANCO, anchor="ma")
        y += 16
    d.line([20, y + 4, W - 20, y + 4], fill=BRANCO, width=1)


def cena(t, fi):
    T = fi / FPS
    rng = rng_frame(fi, 3)
    if T < C.REGRAS_INICIO:
        img = Image.new("RGB", (W, H), MARINHO)
        d = desenho(img)
        d.rectangle([16, 150, W - 16, 420], outline=BRANCO, width=2)
        y = 182
        texto(d, (W // 2, y), C.REGRAS_INTRO[0], 22, BRANCO, anchor="ma")
        d.line([60, y + 38, W - 60, y + 38], fill=BRANCO, width=2)
        bloco_centro(d, W // 2, y + 56, C.REGRAS_INTRO[1], 20, BRANCO, maxw=300, entre=8)
        if int(T * 3) % 2 == 0:
            texto(d, (W // 2, 360), C.LEIA, 18, (255, 255, 255), anchor="ma")
        return img

    i = min(len(C.REGRAS) - 1, int((T - C.REGRAS_INICIO) // C.REGRA_DUR))
    t0 = C.REGRAS_INICIO + i * C.REGRA_DUR
    img = _fundo(i)
    d = desenho(img)
    _cabecalho(d)
    nome_icone, txt = C.REGRAS[i]
    fr = (T - t0 - 0.05) * FPS
    # ícone ao lado do número da regra, piscando
    icones.colar_animado(img, nome_icone, 62, 186, 4, fr, corrompido=i >= 3, rng=rng, piscar_sempre=True)
    rotulo = "REGRA %d" % (i + 1) + (":" if txt is None else "")
    texto(d, (108, 170), rotulo, 26, BRANCO)
    d.line([108, 204, 108 + largura(rotulo, 26), 204], fill=BRANCO, width=2)

    ts, cps = C.regra_digitacao(i)
    n = int(max(0.0, T - ts) * cps)
    cursor_on = (fi // 8) % 2 == 0
    y0 = 252
    if txt is not None:
        linhas = quebrar(txt, 17, 322)
        resto = n
        y = y0
        ult = None
        for ln in linhas:
            if resto <= 0:
                break
            vis = ln[:resto]
            texto(d, (20, y), vis, 17, BRANCO)
            ult = (20 + largura(vis, 17), y)
            resto -= len(ln) + 1
            y += 26
        if ult is None:
            ult = (20, y0)
        if cursor_on:
            d.rectangle([ult[0] + 2, ult[1] + 2, ult[0] + 11, ult[1] + 19], fill=BRANCO)
    else:
        # regra 7: texto escondido sob barras pretas que tremem
        nb = min(C.REGRA7_BARRAS, n)
        por_linha = C.REGRA7_BARRAS / len(C.REGRA7_OCULTO)
        y = y0
        for j, ln in enumerate(C.REGRA7_OCULTO):
            frac = min(1.0, max(0.0, (nb - j * por_linha) / por_linha))
            if frac <= 0:
                break
            larg = min(322, largura(ln, 17) + 12)
            dx, dy = int(rng.integers(-2, 3)), int(rng.integers(-1, 2))
            if frac >= 1:
                texto(d, (20, y), ln, 17, BRANCO)
                if rng.random() < 0.05:  # a barra escorrega e deixa espiar
                    dx += int(rng.integers(25, 70))
            d.rectangle([14 + dx, y - 3 + dy, 14 + larg * frac + dx, y + 21 + dy], fill=(0, 0, 0))
            y += 30
        if cursor_on and nb < C.REGRA7_BARRAS:
            d.rectangle([20, y + 2, 29, y + 19], fill=BRANCO)
    texto(d, (W // 2, 500), "%d / %d  •  %s" % (i + 1, len(C.REGRAS), C.LEIA), 12, (170, 180, 220),
          anchor="ma")
    return img
