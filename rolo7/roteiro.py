"""Monta a linha do tempo a partir da duração real das falas.

Cada segmento: dict(t0, t1, tipo, ...). Cenas e áudio leem a mesma lista.
"""
import numpy as np

import config as C

SR = C.SR


def cortar_intro(x):
    """Usa só a primeira frase da intro ("Aviso aos moradores do bairro Bandeirantes.")."""
    e = np.array([np.sqrt(np.mean(x[i:i + 480] ** 2)) for i in range(0, len(x), 480)])
    silencio = e < 0.012
    ini = int(1.4 * SR / 480)
    run = 0
    for k in range(ini, len(e)):
        run = run + 1 if silencio[k] else 0
        if run >= int(0.28 * SR / 480):
            fim = (k - run + 1) * 480 + int(0.12 * SR)
            y = x[:fim].copy()
            y[-1200:] *= np.linspace(1, 0, 1200)
            return y
    return x


def montar(falas):
    dur = {k: len(v) / SR for k, v in falas.items()}
    seg = []
    t = 0.0

    def add(d, tipo, **kw):
        nonlocal t
        seg.append(dict(t0=t, t1=t + d, tipo=tipo, **kw))
        t += d
        return seg[-1]

    add(0.35, "abre")
    add(1.45 + dur["intro"] + 0.55, "cabecalho", voz="intro", t_voz=0.35 + 1.45)
    for k in range(1, 8):
        d = 0.35 + dur[f"regra{k}"] + 0.75
        s = add(d, "regra", n=k, voz=f"regra{k}", t_voz=0.35)
        s["t_voz"] = s["t0"] + 0.35
        if k == 7:
            s["t1"] += 0.5
            t = s["t1"]
            s["t_extra"] = t
            s["t_voz_extra"] = t + 0.25
            s["t1"] = t + 0.25 + dur["extra"] * 1.19 + 1.3     # fala corrompida (mais lenta)
            t = s["t1"]
        if k in C.INSERTOS:
            var, d_ins = C.INSERTOS[k]
            add(d_ins, "cftv", var=var)
    a = add(1.6, "cftv", var="longe")
    b = add(1.9, "cftv", var="perto")
    b["t_voz"] = a["t0"] + 0.5
    add(0.55, "preto")
    if C.INCLUIR_CARTAO_HISTORIA:
        add(C.CARTAO_DUR, "cartao")
    seg[1]["t_voz"] = seg[1]["t0"] + 1.45
    return seg, t


def achar(seg, t):
    for s in seg:
        if s["t0"] <= t < s["t1"]:
            return s
    return seg[-1]
