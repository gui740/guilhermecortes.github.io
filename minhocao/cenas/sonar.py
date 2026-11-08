"""Bloco 5a — tela de ecobatímetro/sonar antigo (fósforo verde)."""
import numpy as np
from PIL import Image

import config as C
import icones
from .comum import STM, VT, fonte, desenho, texto, rng_frame

X0, X1 = 14, 346
Y_SUP, Y_BASE = 176, 476        # superfície (0 m) e base do gráfico
PROF_MAX = 10.0                 # metros na base do gráfico
VEL = 55.0                      # px/s de rolagem
T0, T1 = 52.0, 59.0


def tempos_ping():
    """Pings do sonar acelerando (intervalo de 0,9 s até 0,12 s)."""
    out, t = [], T0 + 0.15
    while t < T1:
        out.append(t)
        prog = np.clip((t - T0) / (T1 - T0 - 1.0), 0, 1)
        t += 0.9 - 0.78 * prog ** 1.4
    return out


PINGS = tempos_ping()


def _m2y(m):
    return Y_SUP + m / PROF_MAX * (Y_BASE - Y_SUP)


def _fundo(tau):
    return 4.0 + 0.35 * np.sin(tau * 1.3) + 0.25 * np.sin(tau * 3.7 + 1) + 0.06 * np.sin(tau * 5.3 + 2)


def leitura(t, rng):
    s = C.T_SONAR_LEITURAS[0][1]
    for tt, v in C.T_SONAR_LEITURAS:
        if t >= tt:
            s = v
    return s


def cena(t, i):
    rng = rng_frame(i, 21)
    H, W = C.H, C.W
    a = np.zeros((H, W), np.float32)
    xs = np.arange(X0, X1)
    tau = t - (X1 - xs) / VEL
    ys = np.arange(H)[:, None]
    # superfície
    a[Y_SUP - 1:Y_SUP + 2, X0:X1] = 0.9
    # ruído de água
    zona = (ys > Y_SUP + 2) & (ys < Y_BASE)
    sp = (rng.random((H, X1 - X0)) < 0.012) & zona
    a[:, X0:X1] += sp * 0.45
    # fundo do rio
    db = _fundo(tau)
    yb = _m2y(db)
    sem_fundo = tau > C.T_SONAR_LEITURAS[1][0]
    banda_f = (ys >= yb) & (ys < yb + 5) & ~sem_fundo[None, :]
    a[:, X0:X1] += banda_f * 1.0
    abaixo = (ys >= yb + 5) & (ys < Y_BASE) & ~sem_fundo[None, :]
    a[:, X0:X1] += abaixo * (rng.random((H, X1 - X0)) < 0.25) * 0.35
    # peixes (arquinhos) antes da criatura
    for tf, prof in [(51.6, 2.2), (52.4, 1.6), (53.0, 2.8), (53.3, 3.1)]:
        dx = (tau - tf) * VEL
        m = np.abs(dx) < 6
        yy = _m2y(prof) + (dx / 6) ** 2 * 3
        a[:, X0:X1] += (m & (np.abs(ys - yy) < 1.2)) * 0.8
    # a criatura: forma longa, contínua, anelada — não acaba nunca
    tc = C.T_CRIATURA_SONAR
    pres = np.clip((tau - tc) * 1.5, 0, 1)
    if pres.max() > 0:
        topo = _m2y(1.3 + 0.25 * np.sin(tau * 1.7))
        prog = np.clip((tau - tc) / 2.5, 0, 1)
        base = _m2y(2.8 + 9.0 * prog)
        aneis = 0.55 + 0.45 * (np.abs(np.sin(np.pi * tau * 2.3)) ** 0.25)
        aneis = aneis * (np.sin(np.pi * tau * 2.3) ** 2 > 0.04)
        corpo = (ys >= topo) & (ys <= base) & (pres[None, :] > 0)
        # contorno brilhante em cima, corpo texturizado
        borda = (np.abs(ys - topo) < 2.5) & (pres[None, :] > 0)
        textura = 0.35 + 0.35 * rng.random((H, X1 - X0))
        a[:, X0:X1] += corpo * (aneis * pres)[None, :] * textura
        a[:, X0:X1] += borda * 0.9
    a = np.clip(a, 0, 1)
    rgb = np.stack([a * 0.35, a, a * 0.45], -1)
    img = Image.fromarray((rgb * 255).astype(np.uint8), "RGB")
    d = desenho(img)
    # grade
    for m in range(0, 11, 2):
        y = _m2y(m)
        for x in range(X0, X1, 4):
            d.point((x, y), fill=(30, 110, 50))
        texto(d, (X0 + 2, y - 15), f"{m}", fonte(STM, 14), (60, 200, 90))
    for x in range(X1 - int((t * VEL) % 50), X0, -50):
        for y in range(Y_SUP, Y_BASE, 4):
            d.point((x, y), fill=(30, 110, 50))
    d.rectangle([X0 - 2, Y_SUP - 40, X1 + 2, Y_BASE + 2], outline=(60, 200, 90), width=1)
    # canoa na superfície (coluna atual)
    ic = icones.icone_escalado("canoa", 28)
    g = Image.new("RGBA", ic.size, (80, 255, 120, 255))
    img.paste(g, (X1 - 34, Y_SUP - 27), ic)
    # textos
    f = fonte(STM, 18)
    texto(d, (16, C.SAFE_TOP + 2), "ECOBATÍMETRO  200 KHZ", f, (90, 255, 120))
    texto(d, (16, C.SAFE_TOP + 24), "PROFUNDIDADE:", f, (90, 255, 120))
    s = leitura(t, rng)
    fb = fonte(STM, 40)
    if s == "---" and (i // 4) % 2:
        s = ""
    tremor = rng.integers(-2, 3) if t > C.T_SONAR_LEITURAS[1][0] else 0
    texto(d, (170 + tremor, C.SAFE_TOP + 12), s, fb, (140, 255, 160))
    # indicador de ping
    ultimo = max([p for p in PINGS if p <= t], default=-9)
    if t - ultimo < 0.08:
        d.ellipse([X1 - 16, Y_SUP - 38, X1 - 6, Y_SUP - 28], fill=(160, 255, 170))
    texto(d, (X1 - 60, Y_SUP - 40), "PING", fonte(STM, 14), (60, 200, 90))
    texto(d, (16, Y_BASE + 8), "FUNDO", fonte(STM, 16), (60, 200, 90))
    texto(d, (16, Y_BASE + 26), "BARRA DO PARI  03:38", fonte(STM, 16), (60, 200, 90))
    # pop-up de canto
    if t > 55.0 and (i // 6) % 2 == 0:
        nome = "alerta" if (i // 24) % 2 == 0 else "serpente"
        icones.cola_icone(img, nome, C.W - 34, Y_BASE + 26, 30, int((t - 55) * C.FPS),
                          corrompido=nome == "serpente")
    return img


def estilo(t):
    return C.FX_INTENSIDADE["sonar"], "fosforo"
