"""Monta a linha do tempo do episódio (timeline.json) a partir do roteiro aprovado.

Lê: narracao.json + <narr_dir>/duracoes.json (durações reais da voz) e cortes.json (falas de arquivo).
Escreve: ../video/src/timeline.json com trechos (narração, arquivo, respiro), cenas, efeitos e Shorts.
Uso: python3 montar_timeline.py <narr_dir>
"""
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
NARR_DIR = sys.argv[1]
DUR = json.load(open(os.path.join(NARR_DIR, "duracoes.json")))
CORTES = {c["id"]: c for c in json.load(open(os.path.join(AQUI, "cortes.json")))["cortes"]}
TXT = {s["id"]: s["texto"] for s in json.load(open(os.path.join(AQUI, "narracao.json"), encoding="utf8"))}

LT_TED = {"nome": "REED HASTINGS", "cargo": "CEO DA NETFLIX", "fonte": "TED · ABR. 2018"}
LT_BLITZ = {"nome": "REED HASTINGS", "cargo": "CEO DA NETFLIX", "fonte": "STANFORD CS183C · GREYLOCK · 2015"}
LT_HOUSE = {"nome": "EXECUTIVO DA NETFLIX", "cargo": "VÍDEO OFICIAL NETFLIX HOUSE", "fonte": "NETFLIX · DEZ. 2025"}
LT_FU = {"nome": "FRANK UNDERWOOD (PERSONAGEM)", "cargo": "COMERCIAL #FU2016 · HOUSE OF CARDS", "fonte": "NETFLIX · CNN · 15 DEZ. 2015"}

beats = []


def N(nid, *cenas, pos=0.35):
    beats.append({"tipo": "narr", "id": nid, "dur": DUR[nid] + pos, "audio": f"narr/{nid}.wav", "cenas": list(cenas)})


def A(cid, legenda, lt=LT_TED, modo="crt", pre=0.25, pos=0.3, extra=None):
    c = CORTES[cid]
    beats.append({"tipo": "arq", "id": cid, "dur": pre + (c["out"] - c["in"]) + pos, "pre": pre,
                  "audio": f"arquivo/{cid}.mp4", "cenas": [dict({"tipo": "arquivo" if modo == "crt" else ("tv" if cid.startswith("FU") else "cor"),
                                                                "clip": f"media/arquivo/{cid}.mp4", "lt": lt, "legenda": legenda,
                                                                "clipDur": c["out"] - c["in"]}, **(extra or {}))]})


def R(num, titulo, dur=2.6):
    beats.append({"tipo": "respiro", "id": f"r{num}", "dur": dur, "cenas": [{"tipo": "respiro", "num": num, "titulo": titulo}]})


def C(tipo, t=0, **kw):
    return dict(tipo=tipo, t=t, **kw)


STILLS = os.path.join(AQUI, "..", "video", "public", "media", "stills")


def EV(img, carimbo, t=0, trecho=None, frase=None, foco=None):
    from PIL import Image
    w, h = Image.open(os.path.join(STILLS, img)).size
    return C("evidencia", t, img=f"media/stills/{img}", w=w, h=h, carimbo=carimbo, trecho=trecho, frase=frase, foco=foco)


TR = json.load(open(os.path.join(AQUI, "..", "video", "public", "media", "stills", "_trechos.json"))) \
    if os.path.exists(os.path.join(AQUI, "..", "video", "public", "media", "stills", "_trechos.json")) else {}
WEB_TRECHO = [0.04, 0.30, 0.92, 0.10]   # capturas web: frase-alvo fica ~260 px abaixo do topo

# ------------------------------------------------------------------ BLOCO 0 · HOOK
A("HOOK", ["Você pode ver TV linear, jogar videogame,", "ver YouTube… ou ver Netflix."], pre=0.0, pos=0.7,
  extra={"desliga": True})
N("n00a", C("lista", itens=["TV LINEAR", "VIDEOGAME", "YOUTUBE", "NETFLIX"], riscados=["HBO", "AMAZON"], riscarEm=0.42))
N("n00b", C("titulo", texto="A BRIGA PELO SEU TEMPO LIVRE", sub="TED · VANCOUVER · 10 ABR. 2018", grande=True),
  C("medidor", t=4.5, rotulo="TEMPO DE TELA", marcas=["TV", "GAMES", "YOUTUBE", "NETFLIX"], de=0.05, ate=0.75))
N("n00c", EV("web_sleep.png", "EVIDÊNCIA 01 · ENTREVISTA DE RESULTADOS Q1 2017 · 17 ABR. 2017", trecho=WEB_TRECHO))
N("n00d", C("citacao", texto="“ESTAMOS COMPETINDO COM O SONO, NA MARGEM.”",
           credito="REED HASTINGS · ENTREVISTA DE RESULTADOS Q1 2017",
           nota="“Nosso maior concorrente é o sono” é manchete, não fala literal."), pos=0.9)
N("n00e", C("abertura", ep="EP01", marca="NETFLIX", titulo="A NETFLIX NÃO COMPETE COM A HBO.", sub="COMPETE COM VOCÊ."), pos=1.2)

# ------------------------------------------------------------------ BLOCO 1 · DVD
R(1, "DO DVD AO STREAMING")
N("n01a", C("envelope", ano="1997", rotulo="DVD PELO CORREIO"))
A("T07", ["nascemos do DVD e sabíamos que ele seria temporário.", "Ninguém achou que ficaríamos 100 anos enviando discos.",
          "Então você fica paranoico com o que vem a seguir."])
N("n01b", C("titulo", texto="DESCONFIAR DO PRÓPRIO SUCESSO", sub="“founding ethos” · TED 2018"))
N("n01c", C("linha", itens=["CONTROLE REMOTO", "VIDEOCASSETE", "DVD", "STREAMING", "MARATONA"]),
  EV("web_jenner.png", "EVIDÊNCIA 02 · JENNER · SPRINGER · 2018", t=9.0, trecho=WEB_TRECHO),
  C("academico", t=9.0, texto="JENNER · Netflix and the re-invention of television · 2018"))

# ------------------------------------------------------------------ BLOCO 2 · ORIGINAL
R(2, "A APOSTA NO ORIGINAL")
N("n02a", C("titulo", texto="2005", sub="PRIMEIRA TENTATIVA · AINDA SÓ DVD", grande=True))
A("T01", ["tentamos entrar em conteúdo original em 2005,", "quando só tínhamos DVD (…) éramos um miniestúdio.",
          "E não funcionou, porque não tínhamos escala."])
N("n02b", C("titulo", texto="2011", sub="SEGUNDA TENTATIVA", grande=True))
A("T02", ["em 2011, Ted Sarandos, meu sócio que cuida do conteúdo,", "ficou muito empolgado com House of Cards.",
          "Na época, custava 100 milhões de dólares.", "Era um investimento fantástico, e competia com a HBO."],
  extra={"poster": "media/stills/poster_houseofcards.jpg"})
N("n02c", C("titulo", texto="COMO TER CERTEZA?", sub="CHRIS ANDERSON · TED 2018"))
A("T03", ["a gente não tinha certeza. Essa é a tensão toda.", "(…) foi assustador."])
N("n02d", C("posters", imgs=["media/stills/poster_houseofcards.jpg", "media/stills/poster_madmen.jpg"],
            rotulos=["DA NETFLIX", "SÓ EXIBIDA PELA NETFLIX"], pb=[False, True]))
A("T05", ["é sobre fortalecer a marca, para que mais gente queira assinar.", "E House of Cards fez isso (…)",
          "já Mad Men, que a gente exibia, ótima série da AMC,", "não era associada à Netflix, mesmo assistida na Netflix."])
N("n02e", C("titulo", texto="QUEM É DONO DA HISTÓRIA É LEMBRADO.", sub="QUEM SÓ EXIBE, NÃO."),
  C("medidor", t=4.5, rotulo="APOSTA EM CONTEÚDO", marcas=["US$ 100 MI · 2011", "", "", "US$ 8 BI · 2018"], de=0.05, ate=0.92))
A("T06", ["Uns 8 bilhões de dólares no mundo todo.", "E não é suficiente."])

# ------------------------------------------------------------------ BLOCO 3 · BINGE
R(3, "O BINGE COMO PRODUTO")
N("n03a", C("titulo", texto="TODOS OS EPISÓDIOS DE UMA VEZ", sub="HOUSE OF CARDS · 2013"))
A("T04", ["crescemos enviando DVDs, e tinha as séries em box de DVD.", "Todos nós tivemos a experiência de ver ótimas séries da HBO",
          "(…) próximo episódio, próximo episódio.", "É muito poderoso ter todos os episódios de uma vez.",
          "E isso a TV linear não consegue fazer."])
N("n03b", C("fluxo", itens=["EPISÓDIO 1", "PRÓXIMO EPISÓDIO EM 5…", "PULAR ABERTURA", "EPISÓDIO 2"], rotulo="FLUXO ISOLADO"),
  C("academico", t=6.0, texto="JENNER · cap. “Scheduling the Binge” · 2018 · p. 119–137 · conceito de Lisa Perks"))
N("n03c", EV("pazperez_p9-09.png", "EVIDÊNCIA 04 · PAZ PÉREZ · ON RESEARCH · 2020 · P. 9"),
  C("academico", t=0.5, texto="PAZ PÉREZ · Next episode, next market · On Research · 2020 · p. 9"))
N("n03d", C("botao", texto="PULAR ABERTURA", contador="136.000.000", sufixo="CLIQUES POR DIA", nota="DADO DE 2022"))
N("n03e", C("mapa", titulo="250 SÉRIES · TESTE INICIAL", pontos=["EUA", "REINO UNIDO", "CANADÁ"], sub="WEB PRIMEIRO · TV EM AGO. 2017"),
  EV("web_skipintro_tv.png", "EVIDÊNCIA 05 · NETFLIX · 17 MAR. 2022", t=11.0, trecho=WEB_TRECHO))
N("n03f", C("contador", valor="195", sufixo="ANOS ECONOMIZADOS", rotulo="SOMA DO TEMPO DE TODOS · 2022"),
  C("academico", t=0.5, texto="JOHNSON · Looking back on the origin of Skip Intro · Netflix · 2022"),
  C("citacao", t=6.5, texto="“NEM UM BOTÃO ESCRITO ‘CUPCAKE GRÁTIS’ TERIA MAIS CLIQUES.”", credito="ENGENHEIRO DA NETFLIX, SEGUNDO JOHNSON (2022)"))
N("n03g", C("medidor", rotulo="TEMPO ATÉ A HISTÓRIA", marcas=["ABERTURA", "", "", "ZERO"], de=0.1, ate=0.95),
  C("titulo", t=3.0, texto="NÃO DEIXAR VOCÊ ESPERAR."))

# ------------------------------------------------------------------ BLOCO 4 · ALGORITMO
R(4, "O ALGORITMO")
N("n04a", C("cheque", valor="US$ 1.000.000", carimbo="+10%", rotulo="PRÊMIO DO ALGORITMO · C. 2007"))
A("T11", ["foi superempolgante na época. Isso foi por volta de 2007.", "Mas a gente não fez de novo."])
A("T12a", ["Todo mundo dava cinco estrelas para A Lista de Schindler", "e três para Zerando a Vida, do Adam Sandler.",
           "Mas, quando se olhava o que assistiam,", "era quase sempre Adam Sandler."], extra={"estrelas": True})
N("n04b", C("colunas", esquerda="O QUE VOCÊ DIZ", direita="O QUE VOCÊ ASSISTE"))
A("T12b", ["agrada muito mais olhar para as escolhas reais das pessoas.", "As preferências reveladas", "pelo quanto elas curtem prazeres simples."])
N("n04c", C("medidor", rotulo="PREFERÊNCIA REVELADA", marcas=["ASPIRAÇÃO", "", "", "PRAZER SIMPLES"], de=0.2, ate=0.8),
  C("titulo", t=5.0, texto="CURADORIA + FERRAMENTA", sub="TED 2018 · 12:13"))

# ------------------------------------------------------------------ BLOCO 5 · CULTURA
R(5, "A CULTURA")
N("n05a", C("titulo", texto="A PRIMEIRA EMPRESA", sub="ANOS 1990"))
A("T08", ["toda vez que alguém errava, a gente criava um processo", "para aquilo não se repetir (…)",
          "E, no fim, só os bobos queriam trabalhar lá."])
N("n05b", C("titulo", texto="MÍNIMO DE PROCESSO. SEM CAOS.", sub="TED 2018"))
A("T09", ["Somos tipo a anti-Apple. Sabe como eles compartimentam?", "A gente faz o contrário:", "todo mundo recebe todas as informações."])
A("T10", ["queremos que as pessoas digam a verdade.", "E dizemos: discordar em silêncio é desleal."])
N("n05c", C("pessoas", de=120, ate=80, ano="2001"))
A("B01", ["depois de demitir um terço, de 120 para 80 pessoas,", "a gente esperava travar (…)",
          "seriam precisos 80 só para manter as luzes acesas.", "Mas, na verdade, fizemos mais com só 80 pessoas."], lt=LT_BLITZ)
N("n05d", C("titulo", texto="DENSIDADE DE TALENTO"))
A("B02", ["os gestores têm de, todo ano, dar um testemunho sobre cada pessoa:", "se ela tentasse pedir demissão,",
          "eles tentariam fazê-la mudar de ideia?", "(…) às vezes você percebe que tem gente no time",
          "que, se pedisse para sair, você pensaria: até que seria bom."], lt=LT_BLITZ)
N("n05e", C("pergunta", texto="SE ESSA PESSOA QUISESSE SAIR, EU LUTARIA PARA MANTÊ-LA?", rotulo="KEEPER TEST"),
  EV("web_keeper.png", "EVIDÊNCIA 09 · NETFLIX CULTURE MEMO", t=6.0, trecho=WEB_TRECHO),
  C("anzol", t=14.0, texto="“THAT’S A KEEPER, REED!”"))

# ------------------------------------------------------------------ BLOCO 6 · IDENTIDADE
R(6, "A IDENTIDADE")
N("n06a", C("logoN", silencio=True), pos=0.6)
N("n06b", C("logoN", legenda="EXISTE PODER EM SER DONO DE UMA LETRA DO ALFABETO."),
  EV("web_brand_n.png", "EVIDÊNCIA 10 · BRAND.NETFLIX.COM", t=6.0, trecho=WEB_TRECHO))
N("n06c", C("cores"))
N("n06d", C("proibicoes", itens=["ESTICAR", "GIRAR", "UMA COR SÓ", "EFEITOS", "FUNDO POLUÍDO", "SOBRE VERMELHO", "NO CHÃO", "NA COMIDA"]),
  EV("web_brand_avoid.png", "EVIDÊNCIA 11 · BRAND.NETFLIX.COM · THINGS TO AVOID", t=10.5, trecho=[0.04, 0.33, 0.92, 0.12]))
N("n06e", C("barras", titulo="INTENÇÃO DE HUMOR · TWITTER", a=["EUA", 36.7], b=["ESPANHA", 60.0]),
  EV("pazperez_p12-12.png", "EVIDÊNCIA 12 · PAZ PÉREZ · 2020 · P. 12", t=14.0, trecho=TR.get("pazperez_p12-12", {}).get("trecho")),
  C("academico", t=0.5, texto="PAZ PÉREZ · Next episode, next market · On Research · 2020 · p. 11–12 · estudo preliminar de 3 meses"))

# ------------------------------------------------------------------ BLOCO 7 · PUBLICIDADE
R(7, "A PUBLICIDADE")
N("n07a", C("aovivo", linha1="AO VIVO", linha2="DEBATE REPUBLICANO · CNN · 15 DEZ. 2015"),
  EV("web_drum.png", "EVIDÊNCIA 13 · THE DRUM · 16 DEZ. 2015", t=7.0, trecho=[0.04, 0.69, 0.92, 0.29]))
A("FU1", ["É um novo dia na América. Hoje, mais pessoas vão trabalhar,", "voltar para suas famílias e dormir mais tranquilas do que nunca.",
          "(…) Esse homem é Frank Underwood."], lt=LT_FU, modo="cor")
N("n07b", C("titulo", texto="#FU2016", sub="SITE DE CAMPANHA FALSO · ESTREIA DA T4 EM 4 DE MARÇO", grande=True),
  C("academico", t=0.5, texto="CONNELLY · The Drum · 16 dez. 2015"))
A("FU2", ["Eu sou Frank Underwood, e aprovo esta mensagem."], lt=LT_FU, modo="cor")
N("n07c", C("titulo", texto="ENTROU NA CONVERSA."))
N("n07d", C("lista", itens=["HEINEKEN", "GUARANÁ ANTARCTICA", "CLARO", "McDONALD'S", "TAG HEUER", "PERSOL", "FANATICS"], titulo="SENNA · 2024 · PARCERIAS"),
  EV("web_mm_senna.png", "EVIDÊNCIA 14 · MEIO & MENSAGEM · NOV. 2024", t=9.0, trecho=WEB_TRECHO))

# ------------------------------------------------------------------ BLOCO 8 · FENÔMENOS
R(8, "OS FENÔMENOS")
N("n08a", C("posters", imgs=["media/stills/poster_squidgame.jpg"], rotulos=["ROUND 6 · 2021"]),
  C("contador", t=7.5, valor="142 MI", sufixo="DOMICÍLIOS · 4 SEMANAS", rotulo="NÚMERO 1 EM 94 PAÍSES · CARTA Q3 2021"))
N("n08b", EV("web_top10.png", "EVIDÊNCIA 15 · NETFLIX TOP 10 · CONSULTA EM 17 NOV. 2026", trecho=[0.04, 0.42, 0.92, 0.09]),
  C("contador", t=6.0, valor="265,2 MI", sufixo="VIEWS · 91 DIAS", rotulo="SÉRIE MAIS VISTA DA HISTÓRIA DA NETFLIX"))
N("n08c", C("posters", imgs=["media/stills/poster_moneyheist.jpg"], rotulos=["LA CASA DE PAPEL"]),
  EV("carta_q3_21-03.png", "EVIDÊNCIA 16 · CARTA AOS ACIONISTAS Q3 2021 · P. 3", t=6.5, trecho=TR.get("carta_q3_21-03", {}).get("trecho")))
N("n08d", C("posters", imgs=["media/stills/poster_wednesday.jpg", "media/stills/poster_strangerthings.jpg"],
            rotulos=["WEDNESDAY · 252,1 MI", "STRANGER THINGS 4 · 140,7 MI"]))
N("n08e", C("mapa", titulo="AUDIÊNCIA TRANSNACIONAL", pontos=[], sub="FRAGMENTADA ENTRE FRONTEIRAS"),
  C("academico", t=0.5, texto="JENNER · cap. “The Netflix Audience” · 2018 · p. 241–259"))

# ------------------------------------------------------------------ BLOCO 9 · CRÍTICAS
R(9, "A CONTA")
N("n09a", C("contador", valor="100.000.000", sufixo="DE CASAS COMPARTILHANDO", rotulo="NETFLIX · 8 FEV. 2023"),
  EV("web_sharing.png", "EVIDÊNCIA 17 · NETFLIX · AN UPDATE ON SHARING", t=6.0, trecho=WEB_TRECHO))
N("n09b", EV("carta_q4_22-06.png", "EVIDÊNCIA 18 · CARTA Q4 2022 · P. 6", trecho=TR.get("carta_q4_22-06", {}).get("trecho")))
N("n09c", EV("carta_q2_23-01.png", "EVIDÊNCIA 19 · CARTA Q2 2023 · P. 1", trecho=TR.get("carta_q2_23-01", {}).get("trecho")))
N("n09d", C("pergunta", texto="FOI UM ACERTO?", rotulo="PELOS NÚMEROS DA EMPRESA: SIM"))
N("n09e", C("contador", valor="4–5 MIN", sufixo="DE ANÚNCIOS POR HORA", rotulo="PLANO COM ANÚNCIOS · NOV. 2022 · 12 PAÍSES"),
  EV("carta_q4_24-05.png", "EVIDÊNCIA 20 · CARTA Q4 2024 · P. 5", t=9.0, trecho=TR.get("carta_q4_24-05", {}).get("trecho")),
  C("titulo", t=17.5, texto="“PAGUE UM POUCO MAIS.”", sub="CARTA Q4 2024"))
N("n09f", EV("carta_q4_18-05.png", "EVIDÊNCIA 21 · CARTA Q4 2018 · P. 5", trecho=TR.get("carta_q4_18-05", {}).get("trecho"),
             frase="“COMPETIMOS COM O FORTNITE (E PERDEMOS PARA ELE) MAIS DO QUE COM A HBO.”"),
  C("medidor", t=10.0, rotulo="TEMPO DE TELA", marcas=["FORTNITE", "YOUTUBE", "", "NETFLIX"], de=0.1, ate=0.85))
A("T13", ["a gente tenta não pensar em termos de vício.", "A gente pensa assim: o que você vai fazer com o seu tempo",
          "e quando quiser relaxar? Você pode ver TV linear,", "jogar videogame, ver YouTube… ou ver Netflix."])

# ------------------------------------------------------------------ BLOCO 10 · CASA
R(10, "A CASA")
A("H01", ["Nosso trabalho número um é o fandom."], lt=LT_HOUSE, modo="cor")
N("n10a", C("cor_clip", clip="media/arquivo/H03.mp4", mudo=True),
  C("contador", t=6.0, valor="≈ 9.290 M²", sufixo="NETFLIX HOUSE DALLAS", rotulo="DEZ. 2025 · PRESS RELEASE OFICIAL"),
  C("titulo", t=14.0, texto="LAS VEGAS · 2027"))
N("n10b", C("envelope", ano="2025", rotulo="A PORTA É UM ENVELOPE VERMELHO", porta=True),
  EV("house_release-1.png", "EVIDÊNCIA 22 · NETFLIX · PRESS RELEASE · 11 DEZ. 2025", t=5.0, trecho=[0.06, 0.70, 0.88, 0.10]))
A("H02", ["Estivemos na sua sala por muito tempo.", "Agora estamos dizendo: venha para a nossa sala."], lt=LT_HOUSE, modo="cor")
N("n10c", C("titulo", texto="DO ENVELOPE QUE CHEGAVA À SUA CASA", sub="AO ENVELOPE EM QUE VOCÊ ENTRA"),
  C("logoN", t=8.0), pos=0.8)
N("n10d", C("fim", marca="BRAND BY IZOTON", sub="ATÉ O PRÓXIMO ARQUIVO."), pos=4.0)

# ------------------------------------------------------------------ tempos absolutos e efeitos
FX_POR_CENA = {"evidencia": [("papel", 0.0), ("carimbo", 0.55)], "medidor": [("geiger", 0.2)], "contador": [("sweep", 0.0), ("tecla", 0.15)],
               "titulo": [("bip", 0.0)], "pergunta": [("carimbo", 0.3)], "respiro": [("click", 0.0)], "lista": [("tecla", 0.0)],
               "posters": [("sweep", 0.0)], "botao": [("click", 0.25)], "cheque": [("carimbo", 0.6)], "pessoas": [("click", 0.4)],
               "aovivo": [("bip", 0.0), ("bip", 0.35)], "abertura": [("sweep", 0.0)], "envelope": [("papel", 0.0)],
               "proibicoes": [("tecla", 0.0)], "barras": [("geiger", 0.2)], "cheque2": [], "fluxo": [("click", 0.0)],
               "logoN": [], "citacao": [("bip", 0.0)], "mapa": [("bip", 0.1)], "colunas": [("plin", 0.2)], "linha": [("click", 0.0)],
               "academico": [], "cores": [("bip", 0.0)], "anzol": [("plin", 0.0)], "cor_clip": [], "fim": [("crt_off", 3.0)]}
t = 0.0
fx = []
var = 0
for b in beats:
    b["start"] = round(t, 3)
    for c in b["cenas"]:
        c.setdefault("t", 0.0)
        for name, off in FX_POR_CENA.get(c["tipo"], []):
            fx.append({"t": round(t + c["t"] + off, 3), "som": f"{name}_{var % 4}"}); var += 1
    if b["tipo"] == "arq":
        fx.append({"t": round(t, 3), "som": f"crt_on_{var % 4}" if CORTES[b['id']]['modo'] == 'crt' else f"sweep_{var % 4}"}); var += 1
        fx.append({"t": round(t + b["dur"] - 0.25, 3), "som": f"crt_off_{var % 4}" if CORTES[b['id']]['modo'] == 'crt' else f"click_{var % 4}"}); var += 1
    t += b["dur"]
total = round(t, 3)

# Shorts: intervalos no master, a partir dos trechos
def at(bid):
    return next(x for x in beats if x["id"] == bid)

def span(a, b):
    return [at(a)["start"], round(at(b)["start"] + at(b)["dur"], 3)]

shorts = [
    {"id": "SHORT01", "nome": "A Netflix diz que compete com o seu sono", "trechos": [span("HOOK", "n00d"), span("n09f", "T13")],
     "hook": "A NETFLIX NÃO COMPETE COM A HBO."},
    {"id": "SHORT02", "nome": "O botão mais apertado da Netflix", "trechos": [span("n03d", "n03g")], "hook": "136 MILHÕES DE CLIQUES POR DIA"},
    {"id": "SHORT03", "nome": "Você dá 5 estrelas para Schindler e assiste Adam Sandler", "trechos": [span("T12a", "n04c")],
     "hook": "5 ESTRELAS PARA SCHINDLER. E VOCÊ ASSISTE SANDLER."},
    {"id": "SHORT04", "nome": "O teste que todo chefe da Netflix precisa fazer", "trechos": [span("n05c", "n05e")],
     "hook": "VOCÊ LUTARIA PARA MANTÊ-LA?"},
    {"id": "SHORT05", "nome": "Por que a Netflix lidera com uma letra", "trechos": [span("n06a", "n06d")], "hook": "POR QUE UMA LETRA SÓ?"},
    {"id": "SHORT06", "nome": "A campanha da Netflix que entrou num debate presidencial", "trechos": [span("n07a", "n07c")],
     "hook": "NO INTERVALO, UM CANDIDATO QUE NÃO EXISTE."},
    {"id": "SHORT07", "nome": "O fim da senha compartilhada foi um acerto?", "trechos": [span("n09a", "n09d")], "hook": "A NETFLIX COBROU A SENHA. DEU CERTO?"},
    {"id": "SHORT08", "nome": "A Netflix saiu da tela", "trechos": [span("H01", "n10d")], "hook": "AGORA É VOCÊ QUE ENTRA NA NETFLIX."},
]

capitulos = []
for b in beats:
    if b["tipo"] == "respiro":
        capitulos.append({"t": b["start"], "titulo": b["cenas"][0]["titulo"].capitalize()})

out = {"fps": 30, "duracao": total, "trechos": beats, "fx": fx, "shorts": shorts, "capitulos": capitulos}
dst = os.path.join(AQUI, "..", "video", "src", "timeline.json")
json.dump(out, open(dst, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(f"total {total:.1f} s ({total/60:.2f} min), {len(beats)} trechos, {len(fx)} efeitos")
for s in shorts:
    print(s["id"], [round(b - a, 1) for a, b in s["trechos"]])
