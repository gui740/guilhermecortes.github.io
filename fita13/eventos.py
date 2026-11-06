"""Lista de eventos de falha da fita, compartilhada entre vídeo e áudio.

Gerada de forma determinística (seed 1987): render.py usa para desenhar
estática, tracking, drop-outs e glitches; audio.py usa a MESMA lista para
colocar chiados, cortes e drop-outs no som exatamente nos mesmos frames.
"""
import json

import numpy as np

import config as C


def _zona_limpa(t):
    """Momentos em que nada deve glitchar (telas azuis, preto, cartão final, subliminar)."""
    if t < C.ABERTURA_AZUL_FIM + 0.2:
        return True
    if C.ETIQUETA_T - 0.1 <= t < C.ETIQUETA_T + 0.2:
        return True
    if C.SUBLIMINAR_T - 0.1 <= t < C.SUBLIMINAR_T + 0.2:
        return True
    if t >= C.PATIO_NEGATIVO_T - 0.2:
        # do fim do pátio em diante só drop-outs leves na estática final
        return not (C.FIM_PRETO + 0.1 <= t < C.FIM_CARTAO - 0.1)
    return False


def gerar():
    rng = np.random.default_rng(C.SEED + 7)
    ev = {"transicoes": [], "tracking": [], "dropouts": [], "glitches": []}

    # --- estática entre blocos (4–10 frames) — exceto o corte seco para o preto
    for nome, ini, _ in C.BLOCOS[1:]:
        if nome == "fim":
            continue
        f = int(round(ini * C.FPS))
        antes, depois = int(rng.integers(2, 5)), int(rng.integers(2, 6))
        ev["transicoes"].append([f - antes, f + depois])
    # cortes internos da câmera do pátio
    for t in C.PATIO_CORTES[1:]:
        f = int(round(t * C.FPS))
        ev["transicoes"].append([f, f + int(rng.integers(3, 5))])

    def em_transicao(f):
        return any(a <= f < b for a, b in ev["transicoes"])

    # --- barras de tracking rolando
    rolagens = {"abertura": 1, "patrimonio": 1, "corrupcao": 2, "regras": 4,
                "alerta": 2, "patio": 2}  # regras: rolagem esporádica
    for nome, ini, fim in C.BLOCOS:
        n = rolagens.get(nome, 0)
        for j in range(n):
            for _ in range(20):
                t0 = ini + (fim - ini) * (j + rng.uniform(0.15, 0.85)) / n
                dur = int(rng.integers(18, 40))
                ok = all(not _zona_limpa(t0 + d / C.FPS) for d in range(dur))
                if ok:
                    ev["tracking"].append([int(t0 * C.FPS), dur])
                    break

    # --- drop-outs (riscos brancos)
    for f in range(C.N_FRAMES):
        t = f / C.FPS
        if _zona_limpa(t) and not (C.FIM_PRETO <= t < C.FIM_CARTAO):
            continue
        k = C.intensidade(t)
        if k <= 0.15:
            continue
        if rng.random() < 0.01 + 0.045 * k * k:
            for _ in range(int(rng.integers(1, 4))):
                ev["dropouts"].append([f, int(rng.integers(0, C.H)), int(rng.integers(0, C.W - 20)),
                                       int(rng.integers(8, 70))])

    # --- glitches fortes
    tipos = ["blocos", "congelar", "inverter", "vsync"]
    quantos = {"patrimonio": 1, "corrupcao": 6, "regras": 2, "alerta": 3, "patio": 3}
    for nome, ini, fim in C.BLOCOS:
        n = quantos.get(nome, 0)
        for _ in range(n):
            for _try in range(30):
                t0 = rng.uniform(ini + (0.7 if nome == "corrupcao" else 0.3), fim - 0.4)
                if nome == "patrimonio":  # um só, já anunciando o fim
                    t0 = rng.uniform(C.T_CORR - 3.5, C.T_CORR - 0.5)
                f0 = int(t0 * C.FPS)
                tipo = tipos[int(rng.integers(0, len(tipos)))]
                dur = {"blocos": int(rng.integers(2, 6)), "congelar": int(rng.integers(4, 9)),
                       "inverter": int(rng.integers(1, 3)), "vsync": int(rng.integers(6, 12))}[tipo]
                if all(not _zona_limpa((f0 + d) / C.FPS) and not em_transicao(f0 + d)
                       for d in range(dur)):
                    ev["glitches"].append([f0, dur, tipo])
                    break
    ev["glitches"].sort()
    return ev


def indexar(ev):
    """Dicionários por frame para consulta rápida no render."""
    trans = set()
    for a, b in ev["transicoes"]:
        trans.update(range(a, b))
    track = {}
    for f0, dur in ev["tracking"]:
        for d in range(dur):
            track[f0 + d] = d / max(1, dur - 1)
    drops = {}
    for f, y, x, l in ev["dropouts"]:
        drops.setdefault(f, []).append((y, x, l))
    glit = {}
    for f0, dur, tipo in ev["glitches"]:
        for d in range(dur):
            glit[f0 + d] = (tipo, d / max(1, dur - 1))
    return {"transicoes": trans, "tracking": track, "dropouts": drops, "glitches": glit}


def salvar(ev, caminho=C.ARQUIVO_EVENTOS):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
