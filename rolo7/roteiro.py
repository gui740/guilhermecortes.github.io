"""Monta a linha do tempo a partir da duração real das falas.

Cada segmento: dict(t0, t1, tipo, ...). Cenas e áudio leem a mesma lista.
"""
import numpy as np

import config as C

SR = C.SR


def encurtar_pausas(x, max_pausa=0.38):
    """Encurta silêncios internos longos para a introdução ficar rápida."""
    blk = 480
    e = np.array([np.sqrt(np.mean(x[i:i + blk] ** 2)) for i in range(0, len(x), blk)])
    sil = e < 0.012
    manter = np.ones(len(e), bool)
    k, lim = 0, int(max_pausa * SR / blk)
    while k < len(e):
        if sil[k]:
            j = k
            while j < len(e) and sil[j]:
                j += 1
            if j - k > lim and k > 0 and j < len(e):
                meio = k + lim // 2
                manter[meio:meio + (j - k - lim)] = False
            k = j
        else:
            k += 1
    partes = [x[i * blk:(i + 1) * blk] for i in range(len(e)) if manter[i]]
    return np.concatenate(partes).astype(np.float32)


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
    f = add(0.7 + dur["intro1"] + 0.3, "fita")
    f["t_voz"] = f["t0"] + 0.7
    al = add(0.35 + dur["intro2"] + 0.6, "alvo")
    al["t_voz"] = al["t0"] + 0.35
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
    return seg, t


def achar(seg, t):
    for s in seg:
        if s["t0"] <= t < s["t1"]:
            return s
    return seg[-1]
