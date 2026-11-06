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

# ------------------------------------------------------------------ formato
W, H = 360, 640            # "fita" interna (baixa resolução, como VHS)
OUT_W, OUT_H = 1080, 1920  # saída final
FPS = 30
DURACAO = 75.0
N_FRAMES = int(round(DURACAO * FPS))
SR = 48000
SEED = 1987

# Handle do canal no cartão final. Troque ou deixe "" para não mostrar.
HANDLE = "@talking_horror"

# Área segura TikTok/Reels: ~180 px livres em cima e ~320 px embaixo na saída
# final (1920). Na fita interna (÷3): 60 px em cima e ~107 px embaixo.
SAFE_TOP = 62
SAFE_BOTTOM = H - 110  # 530

random.seed(SEED)

# ------------------------------------------------------------------ blocos
BLOCOS = [
    ("abertura", 0.0, 5.0),
    ("patrimonio", 5.0, 24.0),
    ("corrupcao", 24.0, 30.0),
    ("regras", 30.0, 50.0),
    ("alerta", 50.0, 62.0),
    ("patio", 62.0, 70.0),
    ("fim", 70.0, 75.0),
]
# envelope de intensidade dos efeitos VHS por bloco
FX_BASE = {
    "abertura": 0.35, "patrimonio": 0.3, "corrupcao": 0.7, "regras": 0.5,
    "alerta": 0.6, "patio": 0.8, "fim": 0.45,
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
CARTOES_INICIO = 8.0
CARTAO_DUR = 2.88
FALA_OLA = "OLÁ! EU SOU O ZÉ CANHÃOZINHO!"
FALA_OLA_T = (5.5, 7.8)
FALA_FINAL = "VAMOS VISITAR? O ARSENAL ESTÁ SEMPRE DE PORTAS ABERTAS!"
FALA_FINAL_T = (22.4, 25.6)            # continua (glitchando) na corrupção
CARTAO_CORROMPIDO = "O ARSENAL NUNCA PAROU DE TRABALHAR."
MORPH_T = (24.8, 28.2)
SUBLIMINAR_T = 28.0                    # 2 frames
SUBLIMINAR_TXT = "QUANTOS CANHÕES TEM NO PÁTIO?"

# Intervalos em que o mascote "fala" (boca + blips de voz)
FALAS = [FALA_OLA_T]
for _i in range(len(CARTOES)):
    _a = CARTOES_INICIO + _i * CARTAO_DUR + 0.2
    FALAS.append((_a, _a + 1.2))
FALAS.append((22.5, 24.0))
FALAS.append((24.25, 25.5))            # fala corrompida, arrastada


def _silabas(a, b):
    rng = random.Random(int(a * 1000) + SEED)
    ts, t = [], a
    while t < b:
        ts.append(t)
        lento = 1.0 + 1.4 * rampa(t, 24.0, 25.5)
        t += rng.uniform(0.085, 0.16) * lento
    return ts


SILABAS = [(a, b, _silabas(a, b)) for a, b in FALAS]


def boca(t):
    """Abertura da boca do mascote 0..1 (sincronizada com os blips)."""
    for a, b, ss in SILABAS:
        if a <= t < b + 0.12:
            antes = [s for s in ss if s <= t]
            if antes:
                return max(0.0, 1.0 - (t - antes[-1]) / 0.1)
    return 0.0


# Velocidade da fita (wow & flutter). Usada pelo áudio (pitch) e pelo vídeo
# (quique do mascote no ritmo da música que desacelera).
MUSICA_T = (5.0, 30.0)
BPM = 120.0


def taxa_fita(t):
    t = np.asarray(t, dtype=np.float64)
    p = np.clip((t - 24.0) / 6.0, 0.0, 1.0)
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
REGRAS_INICIO = 31.8
REGRA_DUR = 2.6


def regra_texto_digitado(i):
    txt = REGRAS[i][1]
    return txt if txt is not None else "█" * REGRA7_BARRAS


def regra_digitacao(i):
    """(início da digitação, caracteres por segundo) da regra i."""
    txt = regra_texto_digitado(i)
    ts = REGRAS_INICIO + i * REGRA_DUR + 0.3
    cps = max(24.0, len(txt) / 1.55)
    return ts, cps


# ------------------------------------------------------------------ alerta
ALERTA_CAB = "SERVIÇO DE RADIODIFUSÃO DE EMERGÊNCIA — MATO GROSSO"
ALERTA_LINHAS = [
    (51.0, "ALERTA PARA O BAIRRO DO PORTO, CUIABÁ."),
    (52.6, "ATIVIDADE NAS OFICINAS DO ANTIGO ARSENAL."),
    (54.2, "PERMANEÇAM EM CASA ATÉ O NASCER DO SOL."),
    (55.8, "NÃO ATENDAM QUEM BATER PEDINDO FERRAMENTAS."),
]
ALERTA_CRAWL = ("...CONVOCAÇÃO DE APRENDIZES REABERTA... IDADE MÍNIMA: 8 ANOS... "
                "APRESENTAR-SE NO PÁTIO... OS CANHÕES JÁ FORAM CONTADOS...")
ALERTA_ICONE_T = 50.3
ALERTA_TOM_ON, ALERTA_TOM_OFF = 1.6, 0.6   # pulsos do tom 853+960 Hz
ALERTA_TOM_T = (50.4, 61.7)


def alerta_tom_ligado(t):
    if not (ALERTA_TOM_T[0] <= t < ALERTA_TOM_T[1]):
        return False
    return ((t - ALERTA_TOM_T[0]) % (ALERTA_TOM_ON + ALERTA_TOM_OFF)) < ALERTA_TOM_ON


# ícones soltos de canto (sem texto) — (tempo, ícone, (cx, cy))
POPUPS = [
    (56.9, "olho", (316, 140)),
    (58.4, "aviso", (44, 140)),
    (60.1, "olho", (44, 450)),
    (65.3, "olho", (316, 110)),
    (67.5, "aviso", (44, 110)),
]

# ------------------------------------------------------------------ pátio
PATIO_CORTES = [62.0, 64.0, 66.0, 68.0]
PATIO_CONTAGEM = [4, 5, 6, 7]
PATIO_NEGATIVO_T = 70.0 - 2.0 / FPS
PATIO_STINGER_T = 69.85
PATIO_TS = "03:13:13"

# ------------------------------------------------------------------ fim
FIM_PRETO = 70.5
FIM_APRENDIZ_T = FIM_PRETO + 1.0
FIM_CARTAO = 72.6
FIM_AZUL = DURACAO - 10.0 / FPS
FICCAO_TXT = ("OBRA DE FICÇÃO. FATOS HISTÓRICOS REAIS; EVENTOS SOBRENATURAIS "
              "INVENTADOS. SEM RELAÇÃO COM O SESC.")

# ------------------------------------------------------------------ fotos
FOTOS_DIR = os.path.join(BASE_DIR, "assets", "fotos")


def eventos_icones():
    """Todas as aparições de ícone (tempo, corrompido) — o áudio toca um bipe em cada."""
    ev = []
    for i in range(len(CARTOES)):
        ev.append((CARTOES_INICIO + i * CARTAO_DUR + 0.1, False))
    for i in range(len(REGRAS)):
        ev.append((REGRAS_INICIO + i * REGRA_DUR + 0.05, i >= 3))
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
        k = 0.45 + 0.5 * rampa(t, 24.0, 29.5)
        if SUBLIMINAR_T <= t < SUBLIMINAR_T + 2.0 / FPS:
            k = 1.0
    if nome == "patio":
        k = 0.75 + 0.2 * rampa(t, 62.0, 70.0)
    if nome == "fim":
        if t < FIM_PRETO:
            return 0.0
        if t >= FIM_AZUL:
            return 0.1
        if t >= FIM_CARTAO:
            return 0.12
    return k
