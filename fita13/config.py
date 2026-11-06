"""FITA 13: O ARSENAL — configuração central.

Tudo que é tempo, texto ou constante compartilhada entre vídeo e áudio mora aqui,
para que imagem e som fiquem sincronizados sem depender um do outro.
"""
import math
import os
import random

import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAIDA_DIR = os.path.join(BASE_DIR, "saida")
ARQUIVO_FINAL = os.path.join(SAIDA_DIR, "fita13_arsenal.mp4")
ARQUIVO_AUDIO = os.path.join(SAIDA_DIR, "audio.wav")
ARQUIVO_EVENTOS = os.path.join(SAIDA_DIR, "eventos.json")
ARQUIVO_NARRACAO = os.path.join(SAIDA_DIR, "narracao.wav")
ARQUIVO_ENV_BOCA = os.path.join(SAIDA_DIR, "narracao_boca.npy")
VOZES_DIR = os.path.join(BASE_DIR, "assets", "vozes")

# ------------------------------------------------------------------ formato
W, H = 360, 640            # "fita" interna (baixa resolução, como VHS)
OUT_W, OUT_H = 1080, 1920  # saída final
FPS = 30
SR = 48000
SEED = 1987

# Handle do canal no cartão final. Troque ou deixe "" para não mostrar.
HANDLE = "@talking_horror"

# Área segura TikTok/Reels: ~180 px livres em cima e ~320 px embaixo na saída
# final (1920). Na fita interna (÷3): 60 px em cima e ~107 px embaixo.
SAFE_TOP = 62
SAFE_BOTTOM = H - 110  # 530

random.seed(SEED)

# ------------------------------------------------------------------ linha do tempo
# Tudo é relativo: cada bloco começa onde o anterior termina. As durações dos
# cartões e das regras foram escolhidas para caber a narração do Zé Canhãozinho.
T_PATRIMONIO = 5.0
OLA_T = 5.5
CARTOES_INICIO = 8.0
CARTOES_DUR = [4.7, 4.6, 4.9, 7.2, 4.8]
CARTOES_T = [round(CARTOES_INICIO + sum(CARTOES_DUR[:i]), 3) for i in range(len(CARTOES_DUR))]
FALA_FINAL_INICIO = round(CARTOES_T[-1] + CARTOES_DUR[-1], 3)
T_CORR = round(FALA_FINAL_INICIO + 4.3, 3)  # a fita começa a estragar
T_REGRAS = T_CORR + 6.0
REGRAS_INTRO_DUR = 5.1
REGRAS_INICIO = round(T_REGRAS + REGRAS_INTRO_DUR, 3)
REGRAS_DUR = [5.3, 5.8, 5.7, 6.4, 6.6, 2.6, 2.8]
REGRAS_T = [round(REGRAS_INICIO + sum(REGRAS_DUR[:i]), 3) for i in range(len(REGRAS_DUR))]
T_ALERTA = round(REGRAS_T[-1] + REGRAS_DUR[-1], 3)
T_PATIO = T_ALERTA + 12.0
T_FIM = T_PATIO + 8.0
DURACAO = T_FIM + 6.8
N_FRAMES = int(round(DURACAO * FPS))

BLOCOS = [
    ("abertura", 0.0, T_PATRIMONIO),
    ("patrimonio", T_PATRIMONIO, T_CORR),
    ("corrupcao", T_CORR, T_REGRAS),
    ("regras", T_REGRAS, T_ALERTA),
    ("alerta", T_ALERTA, T_PATIO),
    ("patio", T_PATIO, T_FIM),
    ("fim", T_FIM, DURACAO),
]
# envelope de intensidade dos efeitos VHS por bloco
FX_BASE = {
    "abertura": 0.3, "patrimonio": 0.25, "corrupcao": 0.6, "regras": 0.4,
    "alerta": 0.5, "patio": 0.65, "fim": 0.4,
}


def bloco_em(t):
    for nome, a, b in BLOCOS:
        if a <= t < b:
            return nome, a, b
    return BLOCOS[-1]


def rampa(t, a, b):
    """0 antes de a, 1 depois de b, linear no meio."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return min(1.0, max(0.0, (t - a) / (b - a)))


# ------------------------------------------------------------------ abertura
AZUL_VCR = (16, 36, 196)
ABERTURA_AZUL_FIM = 1.0
ETIQUETA_T = 3.0                       # flash de 2 frames
ETIQUETA_TXT = ["ARSENAL —", "NÃO GRAVAR", "POR CIMA"]
CANAL_TXT = "CANAL 13 — PORTO — CUIABÁ MT"
EMISSAO_TXT = "EMISSÃO EXPERIMENTAL"
TOM_TESTE = (ABERTURA_AZUL_FIM, 4.9)   # 1 kHz nas barras


def timestamp(t):
    s = 23 * 3600 + 58 * 60 + 12 + int(t)
    s %= 24 * 3600
    return "SEX 13 NOV 1987 %02d:%02d:%02d" % (s // 3600, (s // 60) % 60, s % 60)


# ------------------------------------------------------------------ programete
TITULO = ["CONHEÇA SEU", "PATRIMÔNIO"]
CARTOES = [
    ("pergaminho", "1818: DOM JOÃO VI ORDENA O REAL TREM DE GUERRA"),
    ("coluna", "ESTILO NEOCLÁSSICO • MUROS ALTOS • VARANDA EM VOLTA DO PÁTIO"),
    ("canhao", "GUERRA DO PARAGUAI: AQUI CONSERTAVAM ARMAS DOS DOIS LADOS"),
    ("martelo", "1842–1899: MENINOS APRENDIZES TRABALHAVAM NAS FORJAS"),
    ("chave", "1984: TOMBADO. HOJE O PRÉDIO DESCANSA."),
]
FALA_OLA = "OLÁ! EU SOU O ZÉ CANHÃOZINHO!"
FALA_OLA_T = (OLA_T, 7.8)
FALA_FINAL = "VAMOS VISITAR? O ARSENAL ESTÁ SEMPRE DE PORTAS ABERTAS!"
FALA_FINAL_T = (FALA_FINAL_INICIO, T_CORR + 1.6)   # continua (glitchando) na corrupção
CARTAO_CORROMPIDO = "O ARSENAL NUNCA PAROU DE TRABALHAR."
MORPH_T = (T_CORR + 0.8, T_CORR + 4.2)
SUBLIMINAR_T = T_CORR + 4.0            # 2 frames
SUBLIMINAR_TXT = "QUANTOS CANHÕES TEM NO PÁTIO?"

# Intervalos em que o mascote "fala" (boca + blips de voz)
# (usado só se a narração não estiver disponível: blips no lugar da voz)
FALAS = [FALA_OLA_T]
for _i in range(len(CARTOES)):
    _a = CARTOES_T[_i] + 0.2
    FALAS.append((_a, _a + 1.2))
FALAS.append((FALA_FINAL_INICIO + 0.1, T_CORR))
FALAS.append((T_CORR + 0.25, T_CORR + 1.5))   # fala corrompida, arrastada


def _silabas(a, b):
    rng = random.Random(int(a * 1000) + SEED)
    ts, t = [], a
    while t < b:
        ts.append(t)
        lento = 1.0 + 1.4 * rampa(t, T_CORR, T_CORR + 1.5)
        t += rng.uniform(0.085, 0.16) * lento
    return ts


SILABAS = [(a, b, _silabas(a, b)) for a, b in FALAS]


_ENV_BOCA = None


def carregar_env_boca(caminho=None):
    """Envelope (1 valor por frame) da voz do mascote, gerado por narracao.py."""
    global _ENV_BOCA
    caminho = caminho or ARQUIVO_ENV_BOCA
    if os.path.exists(caminho):
        _ENV_BOCA = np.load(caminho)
    return _ENV_BOCA


def boca(t):
    """Abertura da boca do mascote 0..1 (sincronizada com a narração ou com os blips)."""
    if _ENV_BOCA is not None:
        f = int(t * FPS)
        return float(_ENV_BOCA[f]) if 0 <= f < len(_ENV_BOCA) else 0.0
    for a, b, ss in SILABAS:
        if a <= t < b + 0.12:
            antes = [s for s in ss if s <= t]
            if antes:
                return max(0.0, 1.0 - (t - antes[-1]) / 0.1)
    return 0.0


# Velocidade da fita (wow & flutter). Usada pelo áudio (pitch) e pelo vídeo
# (quique do mascote no ritmo da música que desacelera).
MUSICA_T = (T_PATRIMONIO, T_REGRAS)
BPM = 120.0


def taxa_fita(t):
    t = np.asarray(t, dtype=np.float64)
    p = np.clip((t - T_CORR) / 6.0, 0.0, 1.0)
    base = 1.0 - 0.62 * p ** 1.4
    wow = (0.004 + 0.07 * p ** 1.2) * np.sin(2 * np.pi * 0.55 * t)
    flutter = (0.002 + 0.02 * p) * np.sin(2 * np.pi * 6.3 * t + 1.3)
    return base + wow + flutter


_MG = np.arange(MUSICA_T[0], MUSICA_T[1] + 0.002, 0.001)
_MP = np.concatenate([[0.0], np.cumsum(taxa_fita(_MG[:-1]) * 0.001)])


def musica_pos(t):
    """Posição (s) dentro da música no instante global t."""
    return float(np.interp(t, _MG, _MP))


# ------------------------------------------------------------------ regras
REGRAS_INTRO = ["ARSENAL DE GUERRA", "AVISO AOS VISITANTES"]
REGRAS_CAB = "ARSENAL DE GUERRA — AVISO AOS VISITANTES"
LEIA = "LEIA ATÉ O FIM"
REGRAS = [
    ("canhao", "CONTE OS CANHÕES DO PÁTIO AO ENTRAR. CONTE DE NOVO AO SAIR."),
    ("canhao_vermelho", "SE O NÚMERO MUDOU, NÃO VOLTE PARA CONFERIR. SAIA PELA RUA TREZE DE JUNHO."),
    ("martelo", "SE OUVIR MARTELADAS DE FORJA DEPOIS DAS 22H, NÃO É REFORMA."),
    ("crianca", "OS APRENDIZES PODEM PEDIR AJUDA COM O TRABALHO. NÃO PERGUNTE O NOME DELES. ELES NÃO LEMBRAM."),
    ("porta", "O PORÃO FECHA ÀS 18H. SE A PORTA ESTIVER ABERTA, ELA NÃO É PARA VOCÊ."),
    ("olho", "NÃO FIQUE DE COSTAS PARA A VARANDA."),
    ("aviso", None),  # regra 7: censurada
]
REGRA7_BARRAS = 16
REGRA7_OCULTO = ["VOCÊ JÁ ESTÁ", "NO PÁTIO.", "CONTE DE NOVO."]


def regra_texto_digitado(i):
    txt = REGRAS[i][1]
    return txt if txt is not None else "█" * REGRA7_BARRAS


def regra_digitacao(i):
    """(início da digitação, caracteres por segundo) da regra i."""
    txt = regra_texto_digitado(i)
    ts = REGRAS_T[i] + 0.3
    if REGRAS[i][1] is None:
        return ts, 14.0
    cps = max(18.0, len(txt) / max(1.0, REGRAS_DUR[i] - 0.8))
    return ts, cps


def indice_em(T, inicios):
    """Índice do último início <= T (ou 0)."""
    i = 0
    for j, a in enumerate(inicios):
        if T >= a:
            i = j
    return i


# ------------------------------------------------------------------ alerta
ALERTA_CAB = "SERVIÇO DE RADIODIFUSÃO DE EMERGÊNCIA — MATO GROSSO"
ALERTA_LINHAS = [
    (T_ALERTA + 1.0, "ALERTA PARA O BAIRRO DO PORTO, CUIABÁ."),
    (T_ALERTA + 2.6, "ATIVIDADE NAS OFICINAS DO ANTIGO ARSENAL."),
    (T_ALERTA + 4.2, "PERMANEÇAM EM CASA ATÉ O NASCER DO SOL."),
    (T_ALERTA + 5.8, "NÃO ATENDAM QUEM BATER PEDINDO FERRAMENTAS."),
]
ALERTA_CRAWL = ("...CONVOCAÇÃO DE APRENDIZES REABERTA... IDADE MÍNIMA: 8 ANOS... "
                "APRESENTAR-SE NO PÁTIO... OS CANHÕES JÁ FORAM CONTADOS...")
ALERTA_ICONE_T = T_ALERTA + 0.3
ALERTA_TOM_ON, ALERTA_TOM_OFF = 1.6, 0.6   # pulsos do tom 853+960 Hz
ALERTA_TOM_T = (T_ALERTA + 0.4, T_PATIO - 0.3)


def alerta_tom_ligado(t):
    if not (ALERTA_TOM_T[0] <= t < ALERTA_TOM_T[1]):
        return False
    return ((t - ALERTA_TOM_T[0]) % (ALERTA_TOM_ON + ALERTA_TOM_OFF)) < ALERTA_TOM_ON


# ícones soltos de canto (sem texto) — (tempo, ícone, (cx, cy))
POPUPS = [
    (T_ALERTA + 6.9, "olho", (316, 140)),
    (T_ALERTA + 8.4, "aviso", (44, 140)),
    (T_ALERTA + 10.1, "olho", (44, 450)),
    (T_PATIO + 3.3, "olho", (316, 110)),
    (T_PATIO + 5.5, "aviso", (44, 110)),
]

# ------------------------------------------------------------------ pátio
PATIO_CORTES = [T_PATIO, T_PATIO + 2.0, T_PATIO + 4.0, T_PATIO + 6.0]
PATIO_CONTAGEM = [4, 5, 6, 7]
PATIO_NEGATIVO_T = T_FIM - 2.0 / FPS
PATIO_STINGER_T = T_FIM - 0.15
PATIO_TS = "03:13:13"

# ------------------------------------------------------------------ fim
FIM_PRETO = T_FIM + 0.5
FIM_APRENDIZ_T = FIM_PRETO + 1.0
FIM_CARTAO = T_FIM + 3.4
FIM_AZUL = DURACAO - 10.0 / FPS
FICCAO_TXT = ("OBRA DE FICÇÃO. FATOS HISTÓRICOS REAIS; EVENTOS SOBRENATURAIS "
              "INVENTADOS. SEM RELAÇÃO COM O SESC.")
# créditos das fotos reais (licenças livres do Wikimedia Commons)
CREDITOS_FOTOS = [
    "FOTO DA FACHADA: MATEUS HIDALGO, CC BY-SA 2.5 BR",
    "FOTO DA VARANDA: PRBURLEY, CC BY 4.0",
    "VIA WIKIMEDIA COMMONS",
]

# ------------------------------------------------------------------ fotos
FOTOS_DIR = os.path.join(BASE_DIR, "assets", "fotos")


def eventos_icones():
    """Todas as aparições de ícone (tempo, corrompido) — o áudio toca um bipe em cada."""
    ev = []
    for i in range(len(CARTOES)):
        ev.append((CARTOES_T[i] + 0.1, False))
    for i in range(len(REGRAS)):
        ev.append((REGRAS_T[i] + 0.05, i >= 3))
    ev.append((ALERTA_ICONE_T, True))
    for t, _, _ in POPUPS:
        ev.append((t, True))
    return ev


def intensidade(t):
    """Intensidade (0..1) do pipeline VHS no instante t."""
    nome, a, b = bloco_em(t)
    k = FX_BASE[nome]
    if nome == "abertura" and t < ABERTURA_AZUL_FIM:
        return 0.12
    if nome == "corrupcao":
        k = 0.38 + 0.42 * rampa(t, T_CORR, T_CORR + 5.5)
        if SUBLIMINAR_T <= t < SUBLIMINAR_T + 2.0 / FPS:
            k = 1.0
    if nome == "patio":
        k = 0.6 + 0.15 * rampa(t, T_PATIO, T_FIM)
    if nome == "fim":
        if t < FIM_PRETO:
            return 0.0
        if t >= FIM_AZUL:
            return 0.1
        if t >= FIM_CARTAO:
            return 0.12
    return k
