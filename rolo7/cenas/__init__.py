"""Cenas. Cada função: cena(t, i) -> PIL.Image 360x640.

Metadados vão em img.info:
  fx     intensidade dos efeitos (0..1)
  grade  "tv" | "cftv" | "fria" | "limpa"
  osd    camada RGBA desenhada por cima dos efeitos
  hires  função(draw, img1080) para texto limpo na resolução final
  estat  estática extra (0..1)
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import audio as A
import config as C
import icones as I
from .comum import (W, H, fonte, nova, draw_serrilhado, quebrar, texto_bloco, contorno,
                    osd_vcr, osd_cftv, gravador, etiqueta, silhueta_radialista,
                    casa_fachada, corredor, sala)

CANTOS = {"se": (46, 128), "sd": (W - 46, 128), "ie": (46, 470), "id": (W - 46, 470)}


def _meta(img, fx, grade="tv", osd=None, hires=None, estat=0.0):
    img.info.update(fx=fx, grade=grade, osd=osd, hires=hires, estat=estat)
    return img


def _rng(i, k=0):
    return np.random.default_rng([C.SEED, i, k])


def angulo_rolo(t):
    """Ângulo acumulado do carretel: motor acelera de 0 até a velocidade normal."""
    w0 = 2 * math.pi * 0.55
    t0, tr = 0.35, 1.6
    if t < t0:
        return 0.0
    if t < t0 + tr:
        return w0 * (t - t0) ** 2 / (2 * tr)
    return w0 * tr / 2 + w0 * (t - t0 - tr)


# ====================================================================== 1. O ROLO
def cena_rolo(t, i):
    img = nova((24, 20, 18))
    d = draw_serrilhado(img)
    # mesa de madeira
    d.rectangle([0, 470, W, H], fill=(54, 36, 24))
    for y in range(480, H, 9):
        d.line([(0, y), (W, y + 3)], fill=(46, 30, 20))
    ang = angulo_rolo(t)
    vu = A.voz_env(t) + (0.05 + 0.04 * math.sin(t * 23) if t > 0.6 else 0)
    c1, c2, r = gravador(img, 180, 342, 0.95, ang, vu)
    # etiqueta pequena colada no carretel (gira junto)
    mini = etiqueta("ROLO 7", 14).rotate(-math.degrees(ang), expand=True, resample=Image.NEAREST)
    img.paste(mini, (int(c1[0] - mini.width / 2), int(c1[1] - r * 0.62 - mini.height / 2)), mini)
    # etiqueta datilografada grande colada no gravador
    et = etiqueta(C.ETIQUETA_ROLO, 24, larg=290).rotate(1.5, expand=True, resample=Image.BICUBIC)
    img.paste(et, (int(180 - et.width / 2), 100), et)
    osd = osd_vcr("play", t) if t > 0.25 else osd_vcr("stop", t)
    return _meta(img, C.FX_BLOCO[1], "tv", osd)


# ====================================================================== 2. A VOZ DA PROFESSORA
def _fundo_programa(img, desbota=0.0):
    d = ImageDraw.Draw(img)
    verde = (60, 120, 70)
    amarelo = (210, 180, 70)
    for k in range(16):
        cor = verde if k % 2 == 0 else (48, 100, 58)
        d.pieslice([-420, -260, 780, 940], -90 + k * 22.5, -90 + (k + 1) * 22.5, fill=cor)
    d.rectangle([0, 0, W, 190], fill=amarelo)
    d.rectangle([0, 190, W, 198], fill=(150, 110, 40))
    if desbota:
        a = np.asarray(img).astype(np.float32)
        y = a.mean(-1, keepdims=True)
        a = a * (1 - desbota) + y * desbota * 0.6
        img.paste(Image.fromarray(a.astype(np.uint8)))


def _titulo(d, y, tremor=0, rng=None):
    f = fonte("vt", 46)
    for k, ln in enumerate(C.TITULO_PROGRAMA):
        dx = int(rng.integers(-tremor, tremor + 1)) if tremor else 0
        w = f.getlength(ln)
        x = 180 - w / 2 + dx
        yy = y + k * 42
        d.text((x + 4, yy + 4), ln, font=f, fill=(120, 40, 30))
        d.text((x + 2, yy + 2), ln, font=f, fill=(40, 30, 20))
        d.text((x, yy), ln, font=f, fill=(255, 250, 230))


def _osciloscopio(img, t, y0=440, y1=520, cor=(140, 255, 160), reta=False, rng=None):
    d = ImageDraw.Draw(img)
    d.rectangle([24, y0, W - 24, y1], fill=(8, 18, 10), outline=(30, 60, 36), width=2)
    for x in range(24, W - 24, 26):
        d.line([(x, y0), (x, y1)], fill=(16, 40, 22))
    cy = (y0 + y1) / 2
    d.line([(24, cy), (W - 24, cy)], fill=(20, 52, 28))
    xs = np.linspace(28, W - 28, 160)
    if reta:
        amos = np.zeros(160)
    else:
        amos = A.voz_amostras(t, 160)
        amos = np.sign(amos) * np.abs(amos) ** 0.55 * (y1 - y0) * 0.55
        amos = np.clip(amos, -(y1 - y0) / 2 + 3, (y1 - y0) / 2 - 3)
    pts = list(zip(xs, cy - amos))
    d.line(pts, fill=cor, width=2)


def cena_programa(t, i):
    rng = _rng(i, 2)
    img = nova()
    if t < C.T_VINHETA_FIM:
        # vinheta da emissora fictícia
        d = draw_serrilhado(img)
        barras = [(200, 200, 190), (210, 190, 60), (60, 170, 160), (70, 160, 60),
                  (170, 60, 150), (180, 50, 40), (40, 50, 160)]
        bw = W / len(barras)
        for k, c in enumerate(barras):
            d.rectangle([k * bw, 0, (k + 1) * bw, H], fill=c)
        d.rectangle([20, 200, W - 20, 430], fill=(20, 40, 24), outline=(230, 200, 80), width=4)
        y = texto_bloco(d, [C.VINHETA[0]], 180, 222, fonte("vt", 72), (250, 220, 90),
                        sombra=(4, 4, (90, 40, 20)))
        y = texto_bloco(d, [C.VINHETA[1]], 180, y + 6, fonte("vt", 36), (240, 240, 230))
        texto_bloco(d, [C.VINHETA[2]], 180, y + 8, fonte("vt", 30), (140, 230, 150))
        osd = osd_vcr("play", t) if t < C.B2[0] + 1.2 else None
        return _meta(img, C.FX_BLOCO[2], "tv", osd)
    _fundo_programa(img, 0.25)
    d = draw_serrilhado(img)
    _titulo(d, 92)
    silhueta_radialista(d, 165, 262, 0.92, (22, 26, 22))
    _osciloscopio(img, t)
    for t0, nome, canto in C.ICONES_B2:
        I.colar_animado(img, nome, *CANTOS[canto], t - t0)
    return _meta(img, C.FX_BLOCO[2], "tv")


# ====================================================================== 3. A FITA FALA COM QUEM ESCUTA
def cena_fita_fala(t, i):
    rng = _rng(i, 3)
    if t < C.T_RETA:
        img = nova()
        _fundo_programa(img, 0.5 + 0.4 * (t - C.B3[0]) / (C.T_RETA - C.B3[0]))
        d = draw_serrilhado(img)
        _titulo(d, 92, tremor=3, rng=rng)
        sx = 165 + int(rng.integers(-3, 4))
        silhueta_radialista(d, sx, 262, 0.92, (12, 14, 12))
        _osciloscopio(img, t, cor=(200, 255, 160))
        return _meta(img, 0.6, "tv")
    if t < C.T_QUEM:
        img = nova((6, 8, 6))
        _osciloscopio(img, t, 280, 360, reta=True)
        return _meta(img, 0.45, "fria")
    if t < C.CARTOES_B3[0][0]:
        img = nova((4, 4, 4))
        _osciloscopio(img, t, 280, 360, cor=(230, 255, 230))
        d = draw_serrilhado(img)
        f = fonte("vt", 40)
        n = int(min(1, (t - C.T_QUEM) / 0.7) * len(C.FALA_QUEM.upper()))
        texto_bloco(d, [C.FALA_QUEM.upper()[:n]], 180, 400, f, (240, 240, 240))
        return _meta(img, 0.5, "fria")
    # subliminar
    for ts in C.SUBLIMINAR_T:
        if int(ts * C.FPS) == i:
            img = nova((150, 0, 0))
            d = draw_serrilhado(img)
            linhas = quebrar(C.SUBLIMINAR, fonte("vt", 40), 300)
            texto_bloco(d, linhas, 180, 250, fonte("vt", 40), (0, 0, 0))
            return _meta(img, 0.8, "tv")
    # cartões datilografados
    idx = max(k for k, c in enumerate(C.CARTOES_B3) if c[0] <= t)
    t0, ico, txt = C.CARTOES_B3[idx]
    img = nova((10, 10, 10))
    d = draw_serrilhado(img)
    d.rectangle([22, 150, W - 22, 470], fill=(226, 218, 196), outline=(120, 110, 90), width=2)
    corr = idx >= 2
    I.colar_animado(img, ico, 180, 212, t - t0, escala=4, corrompido=corr, rng=rng)
    f = fonte("se", 24)
    linhas = quebrar(txt, f, 290)
    n_car = int(min(1.0, (t - t0) / 0.45) * len(txt))
    vis, cont = [], 0
    for ln in linhas:
        vis.append(ln[:max(0, n_car - cont)])
        cont += len(ln) + 1
    dd = ImageDraw.Draw(img)
    texto_bloco(dd, vis, 181, 268, f, (25, 22, 30), entre=8)
    texto_bloco(dd, vis, 180, 268, f, (10, 8, 14), entre=8)
    return _meta(img, 0.55 if not corr else 0.7, "tv")


# ====================================================================== 4. INSTRUÇÕES
AZUL = (14, 26, 88)


def cena_regras(t, i):
    rng = _rng(i, 4)
    img = nova(AZUL)
    d = draw_serrilhado(img)
    branco = (240, 240, 240)
    texto_bloco(d, C.CABECALHO_REGRAS, 180, 74, fonte("vt", 30), branco, entre=2)
    if int(t * 2) % 2 == 0 or t - C.B4[0] > 3:
        texto_bloco(d, [C.LEIA], 180, 136, fonte("vt", 26), (255, 220, 90))
    d.line([(24, 168), (W - 24, 168)], fill=branco, width=2)
    k = min(6, int((t - C.B4[0]) / C.REGRA_DUR))
    t0 = C.B4[0] + k * C.REGRA_DUR
    tl = t - t0
    ico, txt = C.REGRAS[k]
    numero = f"REGRA {k + 1}:" if k == 6 else f"{k + 1}."
    # ícone piscando ao lado do número
    pisca = k < 6 and tl > 0.6 and int(tl * 4) % 2 == 1
    if not pisca:
        I.colar_animado(img, ico, 56, 232, tl, escala=4)
    f = fonte("vt", 30)
    d.text((98, 214), numero, font=f, fill=(255, 220, 90))
    linhas = quebrar(txt, f, 304)
    n_car = int(np.clip((tl - 0.25) / C.REGRA_DIGITA, 0, 1) * len(txt))
    y, cont = 282, 0
    alt = 27
    ult = (28, 282)
    for ln in linhas:
        s = ln[:max(0, n_car - cont)]
        d.text((28, y), s, font=f, fill=branco)
        if s:
            ult = (28 + f.getlength(s), y)
        cont += len(ln) + 1
        y += alt
    if n_car < len(txt) or int(t * 3) % 2 == 0:
        d.rectangle([ult[0] + 2, ult[1] + 4, ult[0] + 13, ult[1] + 24], fill=branco)
    if k == 6 and t >= C.T_REGRA7_EXTRA:
        tr = fonte("vt", 30)
        lin = quebrar(C.REGRA7_EXTRA, tr, 300)
        yy = y + 22
        for ln in lin:
            dx, dy = rng.integers(-3, 4), rng.integers(-2, 3)
            w = tr.getlength(ln)
            d.text((180 - w / 2 + dx + 2, yy + dy), ln, font=tr, fill=(120, 0, 0))
            d.text((180 - w / 2 + dx, yy + dy), ln, font=tr, fill=(255, 70, 60))
            yy += 28
    # progresso 1..7
    fp = fonte("vt", 26)
    for j in range(7):
        x = 60 + j * 40
        cor = (255, 220, 90) if j == k else ((150, 160, 200) if j < k else (60, 70, 130))
        d.text((x, 488), str(j + 1), font=fp, fill=cor, anchor="ma")
    fx = C.FX_BLOCO[4] + (0.12 if t >= C.T_REGRA7_EXTRA else 0)
    return _meta(img, fx, "fria")


# ====================================================================== 5. CFTV
def cena_cftv(t, i):
    rng = _rng(i, 5)
    corte = max(c for c in C.CORTES_CFTV if c[0] <= t)
    t0, cam, var = corte
    img = nova()
    if cam == 1:
        casa_fachada(img, todas_acesas=(var == "festa"), vulto=(var == "festa"), t=t)
        nome = "FACHADA"
    elif cam == 2:
        ang = angulo_rolo(t) * 1.0
        sala(img, t, ang, A.voz_env(t) * 1.5)
        nome = "SALA"
    else:
        aberta = 0.0
        if var == "porta":
            aberta = 0.55 if t < C.T_PORTA else 0.0
        corredor(img, aberta, None if var == "porta" else var, t)
        nome = "CORREDOR"
    # salto de 2 frames na batida da porta
    if 0 <= t - C.T_PORTA < 2 / C.FPS:
        img = Image.fromarray(np.roll(np.asarray(img), 14, axis=0))
    for tp, ico, canto in C.ICONES_B5:
        if 0 <= t - tp < 2.2:
            I.colar_animado(img, ico, *CANTOS[canto], t - tp, escala=3, corrompido=True, rng=rng)
    osd = osd_cftv(cam, nome, t)
    est = 0.6 if (t - t0) < 2 / C.FPS and t0 > C.B5[0] else 0.0
    return _meta(img, C.FX_BLOCO[5], "cftv", osd, estat=est)


# ====================================================================== 6. LADO B
def cena_lado_b(t, i):
    rng = _rng(i, 6)
    if t >= C.T_PRETO:
        return _meta(nova((0, 0, 0)), 0.0, "limpa")
    if C.T_CONGELA <= t:
        img = cena_lado_b(C.T_CONGELA - 1 / C.FPS, int((C.T_CONGELA - 1 / C.FPS) * C.FPS))
        img.info["fx"] = 0.6
        return img
    img = nova((10, 8, 8))
    if t < C.T_LADOB_LEGENDAS:
        d = draw_serrilhado(img)
        et = etiqueta("ROLO 7 — LADO B — TRANSCRIÇÃO", 22, larg=300)
        img.paste(et, (int(180 - et.width / 2), 250), et)
        return _meta(img, 0.6, "tv", osd_vcr("rew", t, data=False))
    quebrada = t >= C.T_FITA_ARREBENTA
    if not quebrada:
        ang = -angulo_rolo(t) * 0.8           # ao contrário
    else:
        ang = -angulo_rolo(C.T_FITA_ARREBENTA) * 0.8 - (t - C.T_FITA_ARREBENTA) * 30
    vu = A.voz_env(t)
    gravador(img, 180, 290, 0.95, ang, vu, quebrada=quebrada, flap=t * 55)
    a = np.asarray(img).astype(np.float32) * 0.55
    img = Image.fromarray(a.astype(np.uint8))
    osd = None
    if not quebrada:
        osd = osd_vcr("play", t, data=False)
        d = draw_serrilhado(osd)
        k = min(len(C.LADO_B) - 1, int((t - C.T_LADOB_LEGENDAS) / C.LADOB_DUR))
        f = fonte("vt", 32)
        linhas = quebrar(C.LADO_B[k], f, 310)
        y = 452 - (len(linhas) - 1) * 14
        for ln in linhas:
            contorno(d, (180, y), ln, f, (255, 225, 40, 255), (0, 0, 0, 255), r=2, anchor="ma")
            y += 30
        d.text((W - 20, C.SEGURO_TOPO + 36), "LADO B", font=fonte("vt", 24), fill=(235, 240, 235, 255), anchor="ra")
    return _meta(img, C.FX_BLOCO[6] if not quebrada else 1.0, "tv", osd)


# ====================================================================== 7. FIM + A VERDADE
def _hires_bloco(paragrafos, tam=44, cor=(232, 232, 226), y_centro=None, entre_par=34, extra=None):
    def desenhar(img):
        from PIL import ImageFont
        d = ImageDraw.Draw(img)
        f = ImageFont.truetype(str(C.FONTES / "IBMPlexMono-Regular.ttf"), tam)
        larg = C.OUT_W - 2 * 96
        blocos = [quebrar(p, f, larg) for p in paragrafos]
        alt_l = int(tam * 1.38)
        total = sum(len(b) for b in blocos) * alt_l + entre_par * (len(blocos) - 1)
        topo, base = 180 * 1.15, C.OUT_H - 320 * 1.1
        y = (topo + base) / 2 - total / 2 if y_centro is None else y_centro - total / 2
        for b in blocos:
            for ln in b:
                d.text((C.OUT_W / 2, y), ln, font=f, fill=cor, anchor="ma")
                y += alt_l
            y += entre_par
        if extra:
            extra(d, y)
    return desenhar


def cena_fim(t, i):
    if t < C.T_VERDADE or (not C.INCLUIR_CARTAO_HISTORIA and t < C.T_FICCAO):
        img = nova((8, 8, 10))
        d = draw_serrilhado(img)
        texto_bloco(d, ["FIM DO ROLO 7."], 180, 260, fonte("vt", 44), (240, 240, 240))
        osd = None
        if t >= C.T_REBOBINANDO:
            if int(t * 3) % 3 != 2:
                texto_bloco(d, ["REBOBINANDO..."], 180, 320, fonte("vt", 32), (200, 200, 200))
            osd = osd_vcr("rew", t, data=False)
        return _meta(img, 0.4, "fria", osd, estat=0.22)
    if t < C.T_FICCAO:
        img = nova((14, 14, 17))
        return _meta(img, C.FX_VERDADE, "limpa", hires=_hires_bloco(C.VERDADE, 44))
    if t < C.B7[1]:
        img = nova((8, 8, 10))

        def handle(d, y):
            from PIL import ImageFont
            f = ImageFont.truetype(str(C.FONTES / "IBMPlexMono-Bold.ttf"), 56)
            d.text((C.OUT_W / 2, y + 60), C.HANDLE, font=f, fill=(255, 255, 255), anchor="ma")
        return _meta(img, C.FX_VERDADE, "limpa",
                     hires=_hires_bloco([" ".join(C.FICCAO)], 46, (200, 200, 200), extra=handle))
    # tela azul de VCR + STOP
    img = nova((10, 40, 200))
    return _meta(img, 0.15, "limpa", osd_vcr("stop", t, data=False))


CENAS = [(C.B1, cena_rolo), (C.B2, cena_programa), (C.B3, cena_fita_fala), (C.B4, cena_regras),
         (C.B5, cena_cftv), (C.B6, cena_lado_b), ((C.B7[0], 1e9), cena_fim)]
NOMES = ["1_rolo", "2_programa", "3_fita_fala", "4_regras", "5_cftv", "6_lado_b", "7_fim"]


def cena(t, i):
    for (a, b), fn in CENAS:
        if a <= t < b:
            return fn(t, i)
    return cena_fim(t, i)
