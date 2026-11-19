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
            5: ("23", "UMA COM REGRAS", "QUE QUASE NENHUMA OUTRA ACEITARIA."),
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
        add({"tipo": "narr", "id": bid, "bloco": alvo, "dur": dur, "audio": audio, "cenas": cenas, "_pal": [w[0] for w in novo], "_paltxt": [[w[0], w[2]] for w in novo],
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
 "n03f": [(V+"rec_relogio.png", "rec"), (V+"rec_cupcake.png", "rec"), (ST+"web_skipintro.png", "print")],
 "n03g": [(V+"rec_relogio.png", "rec"), (V+"rec_controle.png", "rec")],
 "n04a": [(V+"rec_hastings_2015.png", "rec"), (V+"card_losgatos.jpg", "card")],
 "n04b": [(V+"card_sofa.jpg", "card"), (V+"rec_hastings_2014.png", "rec")],
 "n04c": [(V+"rec_hastings_2015.png", "rec"), (V+"card_sofa.jpg", "card")],
 "n05a": [(V+"rec_hastings_2014.png", "rec"), (V+"card_losgatos.jpg", "card")],
 "n05b": [(ST+"web_keeper.png", "print"), (V+"rec_hastings_2015.png", "rec")],
 "n05c": [(V+"card_losgatos.jpg", "card"), (V+"rec_hastings_2014.png", "rec")],
 "n05d": [(V+"rec_hastings_2015.png", "rec"), (ST+"web_keeper.png", "print")],
 "n05e": [(ST+"web_keeper.png", "print"), (V+"rec_hastings_2014.png", "rec"), (V+"rec_peixe.png", "rec")],
 "n06e": [(ST+"pazperez_p12-12.png", "print")],
 "n07a": [(ST+"web_drum.png", "print"), (ST+"poster_houseofcards.jpg", "card")],
 "n07b": [(ST+"poster_houseofcards.jpg", "card"), (ST+"web_drum.png", "print")],
 "n07c": [(ST+"poster_houseofcards.jpg", "card")],
 "n07d": [(ST+"web_mm_senna.png", "print")],
 "n08a": [(V+"card_squid_cosplay.jpg", "card"), (ST+"poster_squidgame.jpg", "card"), (ST+"carta_q3_21-03.png", "print")],
 "n08b": [(ST+"poster_squidgame.jpg", "card"), (V+"card_house_guard.jpg", "card")],
 "n08c": [(ST+"poster_moneyheist.jpg", "card")],
 "n08e": [(V+"card_mapa.jpg", "print"), (ST+"poster_squidgame.jpg", "card"), (ST+"poster_moneyheist.jpg", "card")],
 "n09a": [(ST+"web_sharing.png", "print"), (ST+"carta_q4_22-06.png", "print")],
 "n09d": [(ST+"carta_q2_23-01.png", "print")],
 "n09e": [(ST+"web_ads.png", "print"), (ST+"carta_q4_24-05.png", "print")],
 "n09f": [(ST+"carta_q4_18-05.png", "print")],
 "n10a": [(V+"card_house_kop.jpg", "card"), (V+"card_house_guard.jpg", "card")],
 "n10b": [(V+"card_house_kop.jpg", "card"), (V+"rec_envelope.png", "rec")],
 "n10c": [(V+"rec_envelope.png", "rec"), (V+"card_house_kop.jpg", "card")],
}
ESTREITAS = {"titulo", "contador", "pergunta", "citacao", "medidor", "cheque", "botao", "pessoas", "anzol", "mapa", "fluxo", "lista", "aovivo", "barras", "envelope"}

# termos que podem virar ficha na lateral (revisados à mão a partir das palavras da narração; ver ENTREGA_v3b.md)
def norm_f(w):
    w = unicodedata.normalize("NFKD", w.lower()); return "".join(c for c in w if not unicodedata.combining(c)).strip(".,?!:;\"'()")
TERMOS_FICHA = """ACIONISTAS ADESÕES ANTÁRTIDA ANTARCTICA ANÚNCIO ANÚNCIOS ASSINATURA ASSINATURAS AUDIÊNCIA BOTÃO CAMPANHA CANADÁ CANCELAMENTOS CARTA CASA
CLIQUES CNN COMIDA CONCORRÊNCIA CONTA CONTEÚDO CONTROLE CORREIO CULTURA DALLAS DEBATE DENSIDADE DINHEIRO DVD DVDS DÓLARES EMPRESA ENGENHEIRO ENVELOPE
EPISÓDIO EPISÓDIOS ESTUDO EXPERIÊNCIAS FERRAMENTA FILADÉLFIA FORTNITE FRONTEIRAS GRÁTIS HASTINGS HBO HEINEKEN HORAS IZOTON JULHO MAIO MARÇO NOVEMBRO
FEVEREIRO DEZEMBRO ABRIL AGOSTO OUTUBRO LEGENDA LETRA MARATONA MARCA MERCADO MERCADOS MORDIDA NETFLIX NOME PAÍSES PARCERIAS PEIXE PERGUNTA PESCARIA
PESQUISA PESQUISADORA PLANO PORTA POSTS PRESIDENTE PRODUTO PRODUÇÃO PROIBIDO RECEITA RECOMENDAÇÃO REGRA SÉRIE SÉRIES SENHA SENHAS SENNA SONO
STREAMING TALENTO TECNOLOGIAS TEMPORADA TEMPO TRIMESTRE TRANSNACIONAL TWITTER VERMELHO WEDNESDAY YOUTUBE ALGORITMO SARANDOS UNDERWOOD SQUID ROUND
TED APPLE CUPCAKE""".split()
TERMOS_N = {norm_f(x) for x in TERMOS_FICHA}
FRASES_FICHA = [["house", "of", "cards"], ["stranger", "things"], ["keeper", "test"], ["estados", "unidos"], ["reino", "unido"], ["frank", "underwood"],
                ["guia", "de", "marca"], ["meio", "&", "mensagem"], ["la", "casa", "de", "papel"], ["round", "6"], ["reed", "hastings"], ["ted", "sarandos"],
                ["pular", "abertura"], ["controle", "remoto"], ["densidade", "de", "talento"], ["netflix", "house"], ["mad", "men"]]
UNIDADES = {"milhões": " MI", "%": "%", "anos": " ANOS", "dias": " DIAS", "países": " PAÍSES"}
QUALIF = {"mais de": "MAIS DE ", "cerca de": "CERCA DE ", "quase": "QUASE "}
TERMO_BLOCO = {}
LAT_EXTRA = {"n06b": [(0.6, "media/v3img/gui_brand_clearspace.png", "esq", 150, 4.4)],
             "n06c": [(0.5, "media/v3img/gui_brand_cor.png", "esq", 150, -0.3), (2.0, "media/v3img/gui_brand_clearspace.png", "dir", 560, -0.3)]}  # termo fixo por bloco, quando a fala não tem termo forte (preenchido na revisão)
SLOTS = [("esq", 150), ("dir", 210), ("esq", 600), ("dir", 640)]
for b in beats:
    if b["tipo"] not in ("narr",):
        continue
    pal = b.pop("_pal", None) or []
    b_paltxt = b.get("_paltxt")
    if not pal:  # bloco não gravado: marcas a cada 2,2 s
        pal = [x * 0.5 for x in range(int(b["dur"] / 0.5))]
    princ = [c for c in b["cenas"] if c["tipo"] != "academico"]
    marcas = []
    for i, c in enumerate(princ):
        t0 = c["t"]; t1 = princ[i + 1]["t"] if i + 1 < len(princ) else b["dur"]
        alvo = t0 + 0.5
        while alvo < t1 - 0.35:
            cand = [p for p in pal if alvo - 0.25 <= p <= alvo + 0.4 and t0 + 0.25 < p < t1 - 0.25]
            tm = cand[0] if cand else alvo
            marcas.append((round(tm, 2), c["tipo"] in ESTREITAS))
            alvo = tm + 0.85
    b["passos"] = [m for m, _ in marcas]
    imgs = IMG.get(b["id"], [])
    lat = []
    # laterais (rodada v3b): durante as cenas estreitas, uma imagem real entra a cada ~2,4 s, lados alternados,
    # cada uma fica até a próxima do mesmo lado ou até o fim da cena (cena larga não recebe lateral)
    LARG_OK = ESTREITAS | {"posters", "proibicoes"}
    ult = -9.0; vis = {"esq": None, "dir": None}; n = 0
    for m, _ in marcas:
        cena = next((c for c in reversed(princ) if c["t"] <= m + 0.01), princ[0])
        if not imgs or cena["tipo"] not in LARG_OK or m - ult < 2.4: continue
        ic = princ.index(cena); fim_cena = princ[ic + 1]["t"] if ic + 1 < len(princ) else b["dur"]
        if fim_cena - m < 1.2: continue
        lado = "esq" if n % 2 == 0 else "dir"
        outro = vis["dir" if lado == "esq" else "esq"]
        cands = [x for x in imgs if x[0] != outro]
        if not cands: continue  # nunca a mesma imagem dos dois lados ao mesmo tempo
        src, tipo = cands[(n // 2) % len(cands)]
        y = (150 if lado == "esq" else 210) if (n // 2) % 2 == 0 else (560 if lado == "esq" else 600)
        lat.append({"t": m, "src": src, "tipo": tipo, "lado": lado, "y": y, "grande": False, "fim": round(fim_cena, 2)})
        vis[lado] = src; ult = m; n += 1
    for i, l in enumerate(lat):  # sai quando a próxima do mesmo lado entra
        prox = next((x for x in lat[i + 1:] if x["lado"] == l["lado"]), None)
        if prox and prox["t"] < l["fim"]: l["fim"] = round(prox["t"] + 0.2, 2)
    # etiquetas: a palavra de conteúdo dita, a cada >= 0,9 s, fora dos instantes de entrada de lateral
    ocup = [l["t"] for l in lat]
    pal_txt = b.get("_paltxt") or []
    # fichas: só termo forte (substantivo do tema, nome próprio, número, data), por lista revisada à mão (TERMOS_FICHA, FRASES_FICHA).
    # Pronome, verbo, artigo, advérbio e adjetivo solto nunca entram. Se a palavra da vez não for forte, repete o termo da cena.
    etq = []
    ws = [(a_, w.strip(".,?!:;\"'()").lower()) for a_, w in pal_txt]
    fortes = []  # (t, TEXTO) de cada termo forte dito no bloco
    i = 0
    while i < len(ws):
        a_, lim = ws[i]
        achou = None
        for fr in FRASES_FICHA:  # nomes de várias palavras
            k = len(fr)
            if [norm_f(x[1]) for x in ws[i:i + k]] == [norm_f(x) for x in fr]:
                achou = (a_, " ".join(fr).upper(), k); break
        if achou: fortes.append(achou[:2]); i += achou[2]; continue
        dig = re.sub(r"\D", "", lim)
        if dig and len(dig) >= 2 and dig == re.sub(r"[.,]", "", lim):
            # número: leva junto a casa decimal, a unidade e o qualificador ditos ("mais de 100 milhões" -> MAIS DE 100 MI)
            txt, j = lim, i + 1
            if j < len(ws) and re.fullmatch(r",\d+", pal_txt[j][1].strip()): txt += pal_txt[j][1].strip(); j += 1
            uni = ws[j][1] if j < len(ws) else ""
            if uni in UNIDADES: txt += UNIDADES[uni]; j += 1
            ant = " ".join(x[1] for x in ws[max(0, i - 2):i])
            q = next((Q for k_, Q in QUALIF.items() if ant.endswith(k_)), "")
            fortes.append((a_, (q + txt).upper())); i = j; continue
        if norm_f(lim) in TERMOS_N:
            fortes.append((a_, lim.upper()))
        i += 1
    termo_cena = TERMO_BLOCO.get(b["id"]) or (fortes[0][1] if fortes else None)
    vistos = {t for t, _ in fortes}
    for a_, w in pal_txt:
        lim = w.strip(".,?!:;\"'()").lower()
        if not lim or a_ < 0.25 or a_ > b["dur"] - 0.4: continue
        if etq and a_ - etq[-1]["t"] < 0.9: continue
        if any(abs(a_ - o) < 0.3 for o in ocup): continue
        forte = next((T for t, T in fortes if abs(t - a_) < 0.01), None)
        if forte: termo_cena = forte
        elif len(lim) >= 4 and termo_cena: forte = termo_cena  # palavra fraca: repete o termo da cena
        else: continue
        if etq and etq[-1]["texto"] == forte: continue
        cena = next((c for c in reversed(princ) if c["t"] <= a_ + 0.01), princ[0])
        etq.append({"t": round(a_, 2), "texto": forte, "lado": "dir" if len(etq) % 2 else "esq", "estreita": cena["tipo"] in ESTREITAS})
    if b.get("regravar") == "09":  # bloco não gravado: o texto do roteiro entra na tela, em pedaços
        pedacos = ["O RETORNO", "NÃO ESTAVA", "EM CADA HORA", "ASSISTIDA.", "ESTAVA EM", "OUTRO LUGAR."]
        etq = [{"t": round(0.3 + i * (b["dur"] - 0.8) / len(pedacos), 2), "texto": x, "lado": "dir" if i % 2 else "esq", "estreita": True} for i, x in enumerate(pedacos)]
    b["etiquetas"] = etq
    rit = []
    for p in pal:
        if not rit or p - rit[-1] >= 0.5: rit.append(round(p, 2))
    b["ritmo"] = rit
    b.pop("_paltxt", None)
    # prints oficiais do guia de marca (brand.netflix.com, mandados pelo Guilherme): cartão de documento na lateral, em cor (o logo nunca vai para P&B)
    for (t_, src, lado, y, fim_) in LAT_EXTRA.get(b["id"], []):
        lat.append({"t": t_, "src": src, "tipo": "print", "lado": lado, "y": y, "grande": False, "fim": round(fim_ if fim_ > 0 else b["dur"] + fim_, 2)})
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
    for e in b.get("etiquetas", []):
        fx.append({"t": round(t + e["t"], 3), "som": f"click_{var % 4}", "vol": 0.18}); var += 1
    if b["tipo"] == "painel" and not b.get("audio") and not b.get("regancho"):
        for k in range(6):
            fx.append({"t": round(t + 0.5 + k * 0.17, 3), "som": f"tecla_{k % 4}", "vol": 0.16})
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
