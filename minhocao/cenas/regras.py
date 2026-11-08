"""Bloco 4 — Serviço de avisos aos pescadores: uma cartela por regra."""
import numpy as np

import config as C
import criatura
import icones
from .comum import VT, fonte, nova, desenho, texto, centro, quebra, rng_frame

MARINHO = (10, 18, 88)
F_REGRA = 30
PASSO = 27
CPS = 48.0
Y_TXT = 268


def inicio_regra(k):
    return C.T_REGRA[k][0]


def t_1968():
    return C.T_1968


def regra_em(t):
    for k, (a, b) in enumerate(C.T_REGRA):
        if a <= t < b:
            return k
    return None


def tempos_teclas():
    """Instantes de cada tecla (para o áudio da máquina de escrever)."""
    out = []
    for k, (_, txt, _) in enumerate(C.REGRAS):
        t0 = inicio_regra(k) + 0.25
        out += [t0 + c / CPS for c, ch in enumerate(txt) if ch != " "]
    out += [C.T_REGRA_FINAL + 0.2 + c / 30 for c, ch in enumerate(C.REGRA_FINAL) if ch != " "]
    out += [C.T_1968 + c / 28 for c, ch in enumerate(C.REGRA_1968) if ch != " "]
    return out


def tempos_bipes():
    return [inicio_regra(k) for k in range(len(C.REGRAS))] + [C.T_REGRA_FINAL]


def moldura(img, d, t, i):
    d.rectangle([8, C.SAFE_TOP - 4, C.W - 8, C.SAFE_BOTTOM + 4], outline=(200, 210, 255), width=2)
    d.rectangle([13, C.SAFE_TOP + 1, C.W - 13, C.SAFE_BOTTOM - 1], outline=(90, 100, 180), width=1)
    fh = fonte(VT, 21)
    centro(d, C.SAFE_TOP + 6, C.CABECALHO_REGRAS[0], fh)
    centro(d, C.SAFE_TOP + 25, C.CABECALHO_REGRAS[1], fh, (255, 230, 120))
    d.line([24, C.SAFE_TOP + 48, C.W - 24, C.SAFE_TOP + 48], fill=(200, 210, 255))


def minhocao_fundo(img, t, k):
    """O corpo dele passando por baixo da cartela, sempre maior que a tela."""
    xs = np.linspace(-120, C.W + 120, 90)
    base = 500 + 8 * np.sin(t * 0.8 + k)
    ys = base - 26 * np.sin(xs / 70 + t * 1.6 + k)
    esp = np.stack([xs, ys], 1)
    if k % 2:
        esp = esp[::-1]
    cam = criatura.desenha(esp, 22, img.size, fase=t * 70, cabeca=False, escuro=0.55,
                           luz=(-0.3, -0.95))
    arr = np.asarray(cam).copy()
    arr[..., 3] = (arr[..., 3] * 0.85).astype(np.uint8)
    arr[: C.SAFE_TOP + 52, :, 3] = 0
    from PIL import Image
    c = Image.fromarray(arr, "RGBA")
    img.paste(c, (0, 0), c)


def cartela(img, d, t, i, k):
    rng = rng_frame(i, 11)
    nome, txt, _ = C.REGRAS[k]
    t0 = inicio_regra(k)
    tl = t - t0
    # número da regra + progresso
    fn = fonte(VT, 36)
    centro(d, C.SAFE_TOP + 58, f"REGRA {k + 1} DE 7", fn, (255, 214, 50), sombra=(0, 0, 40))
    for j in range(7):
        x = C.W // 2 - 60 + j * 20
        cor = (255, 214, 50) if j <= k else (60, 70, 140)
        d.rectangle([x - 4, C.SAFE_TOP + 100, x + 4, C.SAFE_TOP + 108], fill=cor)
    # ícone grande com entrada e balanço
    frames = int(tl * C.FPS)
    bob = 3 * np.sin(t * 4)
    icones.cola_icone(img, nome, C.W // 2, 212 + bob, 64, frames)
    # texto datilografado
    f = fonte(VT, F_REGRA)
    linhas = quebra(txt, f, 322)
    n = int(max(0, tl - 0.25) * CPS)
    for j, ln in enumerate(linhas):
        parte = ln[:max(0, n)]
        n -= len(ln) + 1
        if parte:
            centro(d, Y_TXT + j * PASSO, parte, f, (255, 255, 255), sombra=(0, 0, 40))


def cena(t, i):
    rng = rng_frame(i, 12)
    img = nova(MARINHO)
    k = regra_em(t)
    minhocao_fundo(img, t, k if k is not None else 7)
    d = desenho(img)
    moldura(img, d, t, i)
    if k is not None:
        cartela(img, d, t, i, k)
        return img
    if t < C.T_REGRA_FINAL:
        return img
    # cartela final: NUNCA REFORME A IGREJA + "JÁ DERRUBARAM UMA EM 1968."
    tl = t - C.T_REGRA_FINAL
    icones.cola_icone(img, "igreja", C.W // 2, 180, 72, int(tl * C.FPS))
    f = fonte(VT, 40)
    n = int(max(0, tl - 0.2) * 30)
    linhas = quebra(C.REGRA_FINAL, f, 320)
    for j, ln in enumerate(linhas):
        parte = ln[:max(0, n)]
        n -= len(ln) + 1
        centro(d, 240 + j * 36, parte, f, (255, 255, 255), sombra=(0, 0, 40))
    if t >= C.T_1968:
        n = int((t - C.T_1968) * 28)
        s = C.REGRA_1968[:n]
        f2 = fonte(VT, 30)
        dx, dy = rng.integers(-2, 3, 2)
        for j, ln in enumerate(quebra(s, f2, 320)):
            y = 350 + j * 28 + dy
            texto(d, (C.W // 2 + dx + 2, y), ln, f2, (90, 0, 0), ancora="ma")
            texto(d, (C.W // 2 + dx, y), ln, f2, (255, 60, 50), ancora="ma")
    return img


def estilo(t):
    k = C.FX_INTENSIDADE["regras"]
    if t >= C.T_1968:
        k = 0.45
    return k, "frio"
