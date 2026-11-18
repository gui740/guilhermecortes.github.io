"""Linha do tempo v3 do EP01 com a narração do Guilherme (timeline_v3.json).

Parte dos beats da v2 (montar_timeline.py) e:
- troca cada fala da Gacrux pelo bloco dele (mapa-blocos.md) e reposiciona as cenas pelas palavras dele (alinhamento palavra a palavra);
- blocos não gravados viram silêncio do tamanho estimado, marcados [REGRAVAR];
- cold open, colagem 01:09, fala TED 03:33 e viagens pelo painel entram como cenas v3;
- os respiros entre capítulos viram viagem pelo painel, com regancho falado quando gravado.
Uso: python3 montar_timeline_v3.py <narr_dir_v2> <palavras_v2.json>
"""
import difflib, json, os, re, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
NARR_V2, PAL_V2 = sys.argv[1], sys.argv[2]
src = open(os.path.join(AQUI, "montar_timeline.py"), encoding="utf8").read().split("# ------------------------------------------------------------------ tempos absolutos")[0]
g = {"__file__": os.path.join(AQUI, "montar_timeline.py")}
sys_argv = sys.argv
sys.argv = ["montar_timeline.py", NARR_V2]
exec(src, g)
sys.argv = sys_argv
beats_v2, CORTES, FX_POR_CENA = g["beats"], g["CORTES"], None

GUI = json.load(open(os.path.join(AQUI, "..", "video", "src", "v3", "palavras_gui.json")))
PV2 = json.load(open(PAL_V2))
MAPA = {"n01a": "03", "n01b": "04", "n01c": "05", "n02a": "06", "n02b": "07", "n02c": "08", "n02d": "09", "n02e": "10",
        "n03a": "12", "n03b": "13", "n03c": "14", "n03d": "15", "n03e": "16", "n03f": "17", "n03g": "18",
        "n04a": "20", "n04b": "21", "n04c": "22", "n05a": "24", "n05b": "25", "n05c": "26", "n05d": "27", "n05e": "28",
        "n06a": "29", "n06b": "30", "n06c": "31", "n06d": "32", "n06e": "33", "n07a": "34", "n07b": "35", "n07c": "36", "n07d": "37",
        "n08a": "38", "n08b": "39", "n08c": "40", "n08d": "41", "n08e": "42", "n09a": "44", "n09b": "45", "n09c": "46", "n09d": "47",
        "n09e": "48", "n09f": "49", "n10a": "50", "n10b": "51", "n10c": "52+53", "n10d": "54"}
REGANCHO = {3: ("11", "TER A SÉRIE NÃO BASTAVA.", "ELA PRECISAVA QUE VOCÊ NÃO PARASSE."),
            4: ("19", "E PARA ESCOLHER O QUE VOCÊ VÊ,", "A NETFLIX APRENDEU A NÃO CONFIAR NO QUE VOCÊ DIZ."),
            5: ("23", "UMA EMPRESA COM REGRAS", "QUE QUASE NENHUMA OUTRA ACEITARIA."),
            9: ("43", "TODA ESSA MÁQUINA TINHA UM PREÇO.", "EM 2023, ELE CHEGOU NA SUA CONTA.")}


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower()); w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", w)


def pares(antigo, novo):
    """Pares (t_antigo, t_novo) das palavras iguais, em ordem."""
    a = [norm(p[2]) for p in antigo]; b = [norm(p[2]) for p in novo]
    out = [(0.0, 0.0)]
    for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(m.size):
            out.append((antigo[m.a + k][0], novo[m.b + k][0]))
    return out


def warp(ps, t, dur_novo):
    ps = sorted(set(ps))
    if t <= ps[0][0]: v = t
    else:
        v = ps[-1][1] + (t - ps[-1][0])
        for (a0, b0), (a1, b1) in zip(ps, ps[1:]):
            if a0 <= t <= a1:
                v = b0 + (t - a0) * (b1 - b0) / max(1e-6, a1 - a0); break
    return round(max(0.0, min(v, dur_novo - 0.6)), 2)


# razão de ritmo (para estimar os blocos que faltam)
dur_v2 = json.load(open(os.path.join(NARR_V2, "duracoes.json")))
casados = [(dur_v2[k], sum(GUI[x]["dur"] for x in v.split("+"))) for k, v in MAPA.items() if all(x in GUI for x in v.split("+"))]
RITMO = sum(b for _, b in casados) / sum(a for a, _ in casados)

beats = []
cap = 0


def add(b): beats.append(b)


for b in beats_v2:
    bid = b["id"]
    if bid in ("HOOK", "n00a", "n00b", "n00c", "n00d"):
        continue
    if bid == "n00e":
        add({"tipo": "v3", "id": "coldopen", "comp": "coldopen", "dur": 15.0, "cenas": [{"tipo": "v3", "t": 0, "nome": "Cold open (blocos 01+02)"}],
             "fala": "01: Em 2017, o CEO da Netflix disse que a empresa compete com o seu sono. 02: Repara: a HBO não está na lista. Neste episódio, as jogadas da Netflix nessa briga pelo seu tempo. E a conta que ela mandou para você no fim."})
        continue
    if b["tipo"] == "respiro":
        cap = b["cenas"][0]["num"]
        reg = REGANCHO.get(cap)
        blk = reg[0] if reg else None
        gravado = blk in GUI if blk else False
        dur = (GUI[blk]["dur"] + 1.2) if gravado else (4.5 if reg else 2.6)
        add({"tipo": "painel", "id": f"painel{cap}", "dur": round(dur, 3), "de": max(0, cap - 2), "para": cap - 1,
             "audio": f"narr_gui/b{blk}.wav" if gravado else None, "regancho": [reg[1], reg[2]] if reg else None,
             "regravar": (blk if reg and not gravado else None), "titulo": b["cenas"][0]["titulo"],
             "cenas": [{"tipo": "painel", "t": 0, "nome": f"Viagem pelo painel → cap. {cap}"}],
             "fala": (f"{blk}: " + " ".join(reg[1:])) if reg else "(sem fala)"})
        continue
    if b["tipo"] == "arq" and bid == "T04":
        add({"tipo": "v3", "id": "T04", "comp": "falaT04", "dur": 25.36, "cenas": [{"tipo": "v3", "t": 0, "nome": "Fala TED 03:33 com camadas"}],
             "fala": "[arquivo TED] box sets de DVD, próximo episódio… a TV linear não consegue fazer.", "arq": "T04"})
        continue
    if b["tipo"] == "arq":
        nb = dict(b); nb["fala"] = "[arquivo] " + " ".join(b["cenas"][0].get("legenda", [])); add(nb); continue
    # narração
    alvo = MAPA[bid]
    blocos = alvo.split("+")
    if bid == "n01b":
        add({"tipo": "v3", "id": "n01b", "comp": "colagem", "dur": 11.9, "bloco": "04", "cenas": [{"tipo": "v3", "t": 0, "nome": "Colagem 01:09"}],
             "fala": "04: Nascer num formato com prazo de validade virou método: desconfiar do próprio sucesso. Hastings diz que essa preocupação com o que vem a seguir faz parte do espírito de fundação da empresa."})
        continue
    if all(x in GUI for x in blocos):
        if len(blocos) == 1:
            novo = GUI[blocos[0]]["palavras"]; dur_novo = GUI[blocos[0]]["dur"]; audio = f"narr_gui/b{blocos[0]}.wav"
        else:  # 52+53 em sequência, com 0,35 s entre eles
            d0 = GUI[blocos[0]]["dur"] + 0.35
            novo = GUI[blocos[0]]["palavras"] + [[a + d0, e + d0, w] for a, e, w in GUI[blocos[1]]["palavras"]]
            dur_novo = d0 + GUI[blocos[1]]["dur"]; audio = [f"narr_gui/b{blocos[0]}.wav", f"narr_gui/b{blocos[1]}.wav", round(d0, 3)]
        ps = pares(PV2[bid], novo)
        pos = 0.25 if b["dur"] - dur_v2[bid] < 0.5 else (b["dur"] - dur_v2[bid])  # mantém respiros longos (n06a, n10c, n10d)
        dur = round(dur_novo + pos, 3)
        cenas = []
        for c in b["cenas"]:
            nc = dict(c); nc["t"] = warp(ps, c.get("t", 0), dur_novo) if c.get("t", 0) > 0 else 0
            if "riscarEm" in nc: pass
            cenas.append(nc)
        add({"tipo": "narr", "id": bid, "bloco": alvo, "dur": dur, "audio": audio, "cenas": cenas, "_pal": [w[0] for w in novo],
             "fala": f"{alvo}: " + " ".join(w for _, _, w in novo)})
    else:
        dur = round(dur_v2[bid] * RITMO + 0.35, 3)
        cenas = [dict(c, t=round(c.get("t", 0) * RITMO, 2)) for c in b["cenas"]]
        add({"tipo": "narr", "id": bid, "bloco": alvo, "dur": dur, "audio": None, "regravar": alvo, "cenas": cenas,
             "fala": f"{alvo}: [REGRAVAR] silêncio de {dur:.1f} s estimado"})

# ------------------------------------------------------------------ Passo 3: imagens reais nas laterais + passos de câmera
V = "media/v3img/"; ST = "media/stills/"
IMG = {  # (arquivo, tipo) — tipo: rec (recorte com borda) | card (foto) | print (captura de documento)
 "n01a": [(V+"rec_envelope.png", "rec"), (V+"card_losgatos.jpg", "card")],
 "n01c": [(V+"rec_controle.png", "rec"), (V+"rec_vhs.png", "rec"), (V+"card_boxset.jpg", "card")],
 "n02a": [(V+"card_losgatos.jpg", "card"), (V+"rec_envelope.png", "rec")],
 "n02b": [(V+"card_sarandos.jpg", "card"), (ST+"poster_houseofcards.jpg", "card")],
 "n02c": [(V+"rec_hastings_2015.png", "rec"), (ST+"poster_houseofcards.jpg", "card")],
 "n02d": [(V+"rec_hastings_2014.png", "rec")],
 "n02e": [(ST+"poster_houseofcards.jpg", "card"), (ST+"poster_madmen.jpg", "card"), (V+"rec_hastings_2015.png", "rec")],
 "n03a": [(V+"card_boxset.jpg", "card"), (ST+"poster_houseofcards.jpg", "card")],
 "n03b": [(ST+"web_skipintro.png", "print"), (V+"rec_controle.png", "rec")],
 "n03c": [(V+"rec_controle.png", "rec")],
 "n03d": [(V+"rec_controle.png", "rec"), (ST+"web_skipintro_tv.png", "print")],
 "n03e": [(ST+"poster_strangerthings.jpg", "card"), (ST+"poster_wednesday.jpg", "card"), (ST+"poster_houseofcards.jpg", "card")],
 "n03f": [(ST+"web_skipintro.png", "print"), (V+"rec_controle.png", "rec")],
 "n03g": [(V+"rec_controle.png", "rec"), (V+"rec_hastings_2014.png", "rec")],
 "n04a": [(V+"rec_hastings_2015.png", "rec"), (V+"card_losgatos.jpg", "card")],
 "n04b": [(V+"rec_hastings_2014.png", "rec")],
 "n04c": [(V+"rec_hastings_2015.png", "rec"), (ST+"web_jenner.png", "print")],
 "n05a": [(V+"rec_hastings_2014.png", "rec"), (V+"card_losgatos.jpg", "card")],
 "n05b": [(ST+"web_keeper.png", "print"), (V+"rec_hastings_2015.png", "rec")],
 "n05c": [(V+"card_losgatos.jpg", "card"), (V+"rec_hastings_2014.png", "rec")],
 "n05d": [(V+"rec_hastings_2015.png", "rec"), (ST+"web_keeper.png", "print")],
 "n05e": [(ST+"web_keeper.png", "print"), (V+"rec_hastings_2014.png", "rec")],
 "n06e": [(ST+"pazperez_p12-12.png", "print")],
 "n07a": [(ST+"web_drum.png", "print"), (ST+"poster_houseofcards.jpg", "card")],
 "n07b": [(ST+"poster_houseofcards.jpg", "card"), (ST+"web_drum.png", "print")],
 "n07c": [(ST+"poster_houseofcards.jpg", "card")],
 "n07d": [(ST+"web_mm_senna.png", "print")],
 "n08a": [(V+"card_squid_cosplay.jpg", "card"), (ST+"poster_squidgame.jpg", "card"), (ST+"carta_q3_21-03.png", "print")],
 "n08b": [(ST+"poster_squidgame.jpg", "card"), (V+"card_house_guard.jpg", "card")],
 "n08c": [(ST+"poster_moneyheist.jpg", "card")],
 "n08e": [(ST+"poster_squidgame.jpg", "card"), (ST+"poster_moneyheist.jpg", "card"), (ST+"poster_wednesday.jpg", "card")],
 "n09a": [(ST+"web_sharing.png", "print"), (ST+"carta_q4_22-06.png", "print")],
 "n09d": [(ST+"carta_q2_23-01.png", "print")],
 "n09e": [(ST+"web_ads.png", "print"), (ST+"carta_q4_24-05.png", "print")],
 "n09f": [(ST+"carta_q4_18-05.png", "print")],
 "n10a": [(V+"card_house_kop.jpg", "card"), (V+"card_house_guard.jpg", "card")],
 "n10b": [(V+"card_house_kop.jpg", "card"), (V+"rec_envelope.png", "rec")],
 "n10c": [(V+"rec_envelope.png", "rec"), (V+"card_house_kop.jpg", "card")],
}
ESTREITAS = {"titulo", "contador", "pergunta", "citacao", "medidor", "cheque", "botao", "pessoas", "anzol", "mapa", "fluxo", "lista", "aovivo", "barras", "envelope"}
SLOTS = [("esq", 150), ("dir", 210), ("esq", 600), ("dir", 640)]
for b in beats:
    if b["tipo"] not in ("narr",):
        continue
    pal = b.pop("_pal", None) or []
    if not pal:  # bloco não gravado: marcas a cada 2,2 s
        pal = [x * 0.5 for x in range(int(b["dur"] / 0.5))]
    princ = [c for c in b["cenas"] if c["tipo"] != "academico"]
    marcas = []
    for i, c in enumerate(princ):
        t0 = c["t"]; t1 = princ[i + 1]["t"] if i + 1 < len(princ) else b["dur"]
        alvo = t0 + 0.6
        while alvo < t1 - 0.4:
            cand = [p for p in pal if alvo - 0.4 <= p <= alvo + 0.9 and t0 + 0.3 < p < t1 - 0.3]
            tm = cand[0] if cand else alvo
            marcas.append((round(tm, 2), c["tipo"] in ESTREITAS))
            alvo = tm + 2.0
    b["passos"] = [m for m, _ in marcas]
    imgs = IMG.get(b["id"], [])
    lat = []
    for k, (m, estreita) in enumerate([x for x in marcas if x[1]]):
        if k >= len(SLOTS) or not imgs: break
        src, tipo = imgs[k % len(imgs)]
        if k >= len(imgs) and len(imgs) < 3: break
        lado, y = SLOTS[k]
        lat.append({"t": m, "src": src, "tipo": tipo, "lado": lado, "y": y})
    b["laterais"] = lat

# efeitos (mesma regra da v2) e tempos absolutos
FX = {"evidencia": [("papel", 0.0), ("carimbo", 0.55)], "medidor": [("geiger", 0.2)], "contador": [("sweep", 0.0), ("tecla", 0.15)],
      "titulo": [("bip", 0.0)], "pergunta": [("carimbo", 0.3)], "lista": [("tecla", 0.0)], "posters": [("sweep", 0.0)], "botao": [("click", 0.25)],
      "cheque": [("carimbo", 0.6)], "pessoas": [("click", 0.4)], "aovivo": [("bip", 0.0), ("bip", 0.35)], "envelope": [("papel", 0.0)],
      "proibicoes": [("tecla", 0.0)], "barras": [("geiger", 0.2)], "fluxo": [("click", 0.0)], "citacao": [("bip", 0.0)], "mapa": [("bip", 0.1)],
      "colunas": [("plin", 0.2)], "linha": [("click", 0.0)], "cores": [("bip", 0.0)], "anzol": [("plin", 0.0)], "fim": [("crt_off", 3.0)]}
t = 0.0; fx = []; var = 0
for b in beats:
    b["start"] = round(t, 3)
    for c in b["cenas"]: c.setdefault("t", 0.0)
    if b["tipo"] in ("narr", "arq"):
        for c in b["cenas"]:
            for name, off in FX.get(c["tipo"], []):
                fx.append({"t": round(t + c["t"] + off, 3), "som": f"{name}_{var % 4}"}); var += 1
    for l in b.get("laterais", []):
        fx.append({"t": round(t + l["t"], 3), "som": f"papel_{var % 4}"}); var += 1
    if b["tipo"] == "arq":
        crt = CORTES[b["id"]]["modo"] == "crt"
        fx.append({"t": round(t, 3), "som": f"crt_on_{var % 4}" if crt else f"sweep_{var % 4}"}); var += 1
        fx.append({"t": round(t + b["dur"] - 0.25, 3), "som": f"crt_off_{var % 4}" if crt else f"click_{var % 4}"}); var += 1
    t += b["dur"]
capitulos = [{"t": b["start"], "titulo": b["titulo"].capitalize()} for b in beats if b["tipo"] == "painel"]
out = {"fps": 30, "duracao": round(t, 3), "trechos": beats, "fx": fx, "capitulos": capitulos, "ritmo": round(RITMO, 3)}
json.dump(out, open(os.path.join(AQUI, "..", "video", "src", "timeline_v3.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(f"total {t:.1f} s ({t/60:.2f} min), {len(beats)} trechos, ritmo dele/Gacrux = {RITMO:.3f}")
for b in beats[:16]:
    print(f"{b['start']:7.2f} {b['dur']:6.2f} {b['tipo']:7} {b['id']:9} {b.get('bloco','')}")
