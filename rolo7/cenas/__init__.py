"""Cenas. cena(t, i) -> PIL.Image (C.W x C.H).

img.info:
  fx     intensidade dos efeitos de fita (fundo)
  grade  "tv" | "cftv" | "limpa"
  texto  camada RGBA de texto/OSD composta depois dos efeitos, com tratamento leve (legível)
  hires  função(img_1080) para texto limpo na resolução final
  estat  estática extra (0..1)
"""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import config as C
from . import desenhos as D

W, H = C.W, C.H
ROTEIRO = []          # preenchido por render.py (roteiro.montar)

AZUL = (10, 22, 104)
BRANCO = (244, 244, 240, 255)


@lru_cache(None)
def fonte(nome, tam):
    arq = {"b": "Arimo-Bold.ttf", "r": "Arimo-Regular.ttf", "mono": "Cousine-Bold.ttf"}[nome]
    return ImageFont.truetype(str(C.FONTES / arq), tam)


def quebrar(texto, fnt, largura):
    linhas, atual = [], ""
    for p in texto.split():
        teste = (atual + " " + p).strip()
        if fnt.getlength(teste) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def centralizado(d, linhas, y, fnt, cor, entre=1.22, sombra=True):
    alt = int(fnt.size * entre)
    for ln in linhas:
        if sombra:
            d.text((W / 2 + 3, y + 3), ln, font=fnt, fill=(0, 0, 0, 170), anchor="ma")
        d.text((W / 2, y), ln, font=fnt, fill=cor, anchor="ma")
        y += alt
    return y


def _meta(img, fx, grade="tv", texto=None, hires=None, estat=0.0):
    img.info.update(fx=fx, grade=grade, texto=texto, hires=hires, estat=estat)
    return img


def _camada():
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return o, ImageDraw.Draw(o)


def _topo(d):
    """Cabeçalho fixo das telas de aviso."""
    y = C.SEGURO_TOPO + 8
    d.text((W / 2, y), C.EMISSORA, font=fonte("b", 22), fill=(205, 210, 225, 255), anchor="ma")
    d.line([(40, y + 36), (W - 40, y + 36)], fill=(205, 210, 225, 255), width=2)
    centralizado(d, C.CABECALHO, y + 50, fonte("b", 26), BRANCO, sombra=False)
    d.line([(40, y + 118), (W - 40, y + 118)], fill=(205, 210, 225, 255), width=2)


# ====================================================================== telas de aviso
def tela_cabecalho(s, t, i):
    img = Image.new("RGB", (W, H), AZUL)
    o, d = _camada()
    d.text((W / 2, C.SEGURO_TOPO + 8), C.EMISSORA, font=fonte("b", 24), fill=(205, 210, 225, 255), anchor="ma")
    # faixa de alerta
    d.rectangle([0, 300, W, 312], fill=(230, 230, 230, 255))
    y = centralizado(d, C.CABECALHO, 352, fonte("b", 34), BRANCO)
    d.rectangle([0, y + 26, W, y + 38], fill=(230, 230, 230, 255))
    if t - s["t0"] > 1.2:
        centralizado(d, [C.SUBCABECALHO], y + 80, fonte("b", 30), (220, 220, 220, 255))
    return _meta(img, C.FX_AVISO, "aviso", o)


def tela_regra(s, t, i):
    rng = np.random.default_rng([C.SEED, i, 3])
    img = Image.new("RGB", (W, H), AZUL)
    o, d = _camada()
    _topo(d)
    n = s["n"]
    d.text((W / 2, 300), f"REGRA {n}", font=fonte("b", 32), fill=(200, 205, 225, 255), anchor="ma")
    f = fonte("b", 40)
    linhas = quebrar(C.REGRAS[n - 1], f, W - 70)
    alt = int(40 * 1.24)
    y0 = 372 if n < 7 else 360
    y = centralizado(d, linhas, y0, f, BRANCO)
    fx = C.FX_AVISO
    if n == 7 and t >= s["t_extra"]:
        f2 = fonte("b", 36)
        yy = y + 46
        for ln in quebrar(C.REGRA7_EXTRA, f2, W - 80):
            dx, dy = int(rng.integers(-3, 4)), int(rng.integers(-2, 3))
            d.text((W / 2 + dx + 3, yy + dy + 3), ln, font=f2, fill=(60, 0, 0, 200), anchor="ma")
            d.text((W / 2 + dx, yy + dy), ln, font=f2, fill=(255, 92, 80, 255), anchor="ma")
            yy += int(36 * 1.24)
        fx = 0.5 + 0.3 * min(1.0, (t - s["t_extra"]) / 2.5)
    return _meta(img, fx, "aviso", o)


# ====================================================================== CFTV
def _osd_cftv(cam, nome, t):
    o, d = _camada()
    f = fonte("mono", 26)
    y0 = C.SEGURO_TOPO + 8

    def txt(x, y, s, anchor="la"):
        d.text((x + 2, y + 2), s, font=f, fill=(0, 0, 0, 220), anchor=anchor)
        d.text((x, y), s, font=f, fill=(228, 236, 228, 255), anchor=anchor)

    txt(24, y0, f"CAM {cam:02d}  {nome}")
    if int(t * 2) % 2 == 0:
        d.ellipse([W - 104, y0 + 6, W - 88, y0 + 22], fill=(230, 30, 30, 255))
    txt(W - 24, y0, "REC", "ra")
    h, m, sg = C.CFTV_HORA
    tot = h * 3600 + m * 60 + sg + int(t)
    yb = C.SEGURO_BASE - 40
    txt(24, yb, f"{tot // 3600:02d}:{tot // 60 % 60:02d}:{tot % 60:02d}")
    txt(W - 24, yb, "16-11-1974", "ra")
    return o


def tela_cftv(s, t, i):
    var = s["var"]
    base = Image.new("RGB", (D.W, D.H))
    tg = t - s["t0"] + C.GOTA_FASE + 0.95   # a primeira gota cai logo
    if var in ("festa", "varanda"):
        D.casa_fachada(base, todas_acesas=True, vulto=(var == "varanda"))
        cam, nome = 1, "FACHADA"
    elif var == "goteira":
        D.corredor(base, porta_aberta=0.5, vulto=None, t=tg)
        cam, nome = 3, "CORREDOR"
    else:
        D.corredor(base, porta_aberta=0.0, vulto=var, t=tg)
        cam, nome = 3, "CORREDOR"
    if cam == 1:   # fachada mais de perto
        base = base.crop((40, 66, 320, 564))
    img = base.resize((W, H), Image.BILINEAR)
    est = 0.7 if t - s["t0"] < 2 / C.FPS else 0.0
    fx = C.FX_FINAL if var in ("longe", "perto") else C.FX_CFTV
    return _meta(img, fx, "cftv", _osd_cftv(cam, nome, t), estat=est)


# ====================================================================== fim
def tela_cartao(s, t, i):
    img = Image.new("RGB", (W, H), (10, 10, 12))

    def desenhar(out):
        d = ImageDraw.Draw(out)
        f = ImageFont.truetype(str(C.FONTES / "Arimo-Regular.ttf"), 44)
        fb = ImageFont.truetype(str(C.FONTES / "Arimo-Bold.ttf"), 52)
        blocos = [quebrar(p, f, C.OUT_W - 200) for p in C.CARTAO]
        alt = int(44 * 1.4)
        total = sum(len(b) for b in blocos) * alt + 50 * len(blocos) + 90
        y = (180 + (C.OUT_H - 320)) / 2 - total / 2
        for b in blocos:
            for ln in b:
                d.text((C.OUT_W / 2, y), ln, font=f, fill=(225, 225, 220), anchor="ma")
                y += alt
            y += 50
        d.text((C.OUT_W / 2, y + 20), C.HANDLE, font=fb, fill=(255, 255, 255), anchor="ma")
    return _meta(img, 0.08, "limpa", hires=desenhar)


def cena(t, i):
    from roteiro import achar
    s = achar(ROTEIRO, t)
    tipo = s["tipo"]
    if tipo == "abre":
        return _meta(Image.new("RGB", (W, H), AZUL), C.FX_AVISO, "aviso", estat=1.0)
    if tipo == "cabecalho":
        return tela_cabecalho(s, t, i)
    if tipo == "regra":
        return tela_regra(s, t, i)
    if tipo == "cftv":
        return tela_cftv(s, t, i)
    if tipo == "preto":
        return _meta(Image.new("RGB", (W, H)), 0.0, "limpa")
    return tela_cartao(s, t, i)
