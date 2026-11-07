"""Configuração central do ROLO 7: A CASA DA ESQUINA.

Todos os tempos em segundos (tempo global do vídeo).
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ASSETS = RAIZ / "assets"
FONTES = ASSETS / "fonts"
SAIDA = RAIZ / "saida"
ARQUIVO_FINAL = SAIDA / "rolo7_casa_da_esquina.mp4"

# ---------------------------------------------------------------- vídeo
FPS = 30
W, H = 360, 640            # resolução interna de "fita"
OUT_W, OUT_H = 1080, 1920  # saída final
ESCALA = OUT_W // W
SEED = 1974
SR = 48000                 # áudio

HANDLE = "@talking_horror"
INCLUIR_CARTAO_HISTORIA = True

# área segura TikTok/Reels em px internos (180 px / 320 px na saída)
SEGURO_TOPO = 62
SEGURO_BASE = H - 108

# ---------------------------------------------------------------- blocos
B1 = (0.0, 6.0)      # o rolo
B2 = (6.0, 20.0)     # a voz da professora
B3 = (20.0, 30.0)    # a fita começa a falar
B4 = (30.0, 52.0)    # instruções
B5 = (52.0, 66.0)    # câmera de segurança
B6 = (66.0, 73.5)    # lado B
B7 = (73.5, 82.5)    # fim do rolo + a verdade
AZUL_FRAMES = 10
DURACAO = B7[1] + AZUL_FRAMES / FPS
N_FRAMES = int(round(DURACAO * FPS))

# fronteiras com estática (tempo, frames antes, frames depois)
TRANSICOES = [
    (B2[0], 2, 4), (B3[0], 3, 3), (B4[0], 3, 5), (B5[0], 3, 5),
    (B6[0], 3, 4), (B7[0] + 0.0, 0, 0),   # depois do preto: sem estática
    (75.5, 2, 2), (80.5, 2, 2), (B7[1], 2, 2),
]

# intensidade de efeitos por bloco (envelope sugerido)
FX_BLOCO = {1: 0.35, 2: 0.3, 3: 0.5, 4: 0.5, 5: 0.7, 6: 0.9, 7: 0.25}
FX_VERDADE = 0.1

# ---------------------------------------------------------------- textos
DATA_OSD = "SÁB 16 NOV 1974"
HORA_OSD_INICIO = (22, 4, 0)
ETIQUETA_ROLO = "ROLO 7 — DISCURSO — NÃO APAGAR"

VINHETA = ["CANAL 9", "CUIABÁ", "REPRISE ESPECIAL"]
TITULO_PROGRAMA = ["A VOZ DA", "PROFESSORA"]

FALA_A = ("Boa noite, Cuiabá. Boa noite à cidade verde. Hoje eu quero falar "
          "sobre esta casa, sobre esta rua, sobre as luzes que a gente deixa acesas")
FALA_B = "para quem ainda vai voltar..."
FALA_VOLTAR = "voltar..."
FALA_QUEM = "Quem está ouvindo?"
LADO_B = [
    "A LUZ DA COZINHA ESTÁ ACESA.",
    "O JANTAR ESTÁ NA MESA.",
    "SENTA. AINDA FALTA O ÚLTIMO PARÁGRAFO.",
    "VOCÊ VEIO OUVIR ATÉ O FIM?",
]

# bloco 2: tempos
T_VINHETA_FIM = 7.6
T_FALA_A = 7.8
FALA_A_MAX = 10.0    # duração máx. da fala A (s) – a velocidade do TTS se ajusta
ICONES_B2 = [(9.2, "microfone", "se"), (11.6, "rolo", "sd"),
             (14.0, "lampada_amarela", "ie"), (16.4, "casa", "id")]

# bloco 3
T_REPETE = 20.05
T_RETA = 23.6
T_QUEM = 24.6
CARTOES_B3 = [
    (25.6, "lampada", "1974. A CASA DA ESQUINA DOS BANDEIRANTES APAGA AS LUZES."),
    (26.7, "lampada_amarela", "SÓ A COZINHA FICA ACESA."),
    (27.8, "rolo", "TODA NOITE, LÁ DENTRO, O MESMO DISCURSO."),
    (28.9, "rolo_vermelho", "NINGUÉM SABE MAIS QUEM APERTA O PLAY."),
]
SUBLIMINAR = "ELA AINDA NÃO TERMINOU O DISCURSO."
SUBLIMINAR_T = [26.68, 28.86]   # 1 frame cada

# bloco 4
CABECALHO_REGRAS = ["AVISO AOS MORADORES", "DO BAIRRO BANDEIRANTES"]
LEIA = "LEIA ATÉ O FIM"
REGRAS = [
    ("lampada_amarela", "SE SÓ A LUZ DA COZINHA ESTIVER ACESA, PODE PASSAR. É JANTAR."),
    ("lampada_vermelha", "SE TODAS AS LUZES ESTIVEREM ACESAS, ATRAVESSE A RUA. A FESTA NÃO É PARA VOCÊ."),
    ("taca", "SE OUVIR COPOS BRINDANDO, NÃO CONTE QUANTOS. VOCÊ VAI CONTAR UM A MAIS."),
    ("microfone", "SE A VOZ DO DISCURSO DISSER O SEU NOME, ELA NÃO ESTÁ LENDO. ESTÁ CHAMANDO."),
    ("olho", "VULTO DE CAMISOLA NA VARANDA: NÃO ACENE. ELA ACENA DE VOLTA."),
    ("gota", "SE OUVIR ÁGUA PINGANDO NO ESCURO, NÃO CHAME O CASEIRO. ELE SAIU HÁ MUITO TEMPO."),
    ("tv", "NUNCA LIGUE A TV NEM O RÁDIO DENTRO DA CASA."),
]
REGRA_DUR = 2.8
REGRA_DIGITA = 1.6           # tempo de digitação de cada regra
REGRA7_EXTRA = "SE VOCÊ ESTÁ VENDO ISTO, ALGUÉM LIGOU."
T_REGRA7_EXTRA = B4[0] + 6 * REGRA_DUR + REGRA_DIGITA + 1.0

# bloco 5 (CFTV): (início, câmera, variante)
CORTES_CFTV = [
    (52.0, 1, "cozinha"),
    (54.5, 2, "sala"),
    (57.0, 3, "porta"),
    (60.0, 1, "festa"),
    (62.5, 3, "longe"),
    (64.3, 3, "perto"),
]
T_PORTA = 59.0
CFTV_HORA = (3, 13, 40)
ICONES_B5 = [(55.6, "aviso", "sd"), (61.2, "olho", "se"), (64.9, "olho", "id")]

# bloco 6
T_LADOB_LEGENDAS = 67.0
LADOB_DUR = 1.25
T_FITA_ARREBENTA = 72.0
T_CONGELA = 72.75
T_PRETO = 72.9               # até B6[1] (0,6 s de preto e silêncio)

# bloco 7
T_REBOBINANDO = 74.5
T_VERDADE = 75.5
T_FICCAO = 80.5
VERDADE = [
    'INSPIRADO NA LENDA URBANA DO "CASARÃO ASSOMBRADO" DO BAIRRO BANDEIRANTES, EM CUIABÁ.',
    'A MULHER REAL POR TRÁS DA LENDA, A PROFESSORA ANA MARIA DO COUTO, A "MAY" (1925–1971), '
    'FOI ATLETA, ADVOGADA, JORNALISTA, RADIALISTA E VEREADORA. NUNCA FOI UM FANTASMA.',
    "A LENDA NASCEU DO LUTO DE UMA MÃE QUE OUVIA, NO ESCURO, A VOZ GRAVADA DA FILHA.",
]
FICCAO = ["OBRA DE FICÇÃO.", "PERSONAGENS E EVENTOS", "SOBRENATURAIS INVENTADOS."]

# ---------------------------------------------------------------- voz
# motor: "mbrola" (espeak-ng + voz feminina br4) ou "espeak" (espeak-ng puro)
VOZ_MOTOR = "mbrola"
VOZ_MBROLA = "mb-br4"
VOZ_ESPEAK = "pt-br+f3"
VOZ_PITCH = 38


def bloco_de(t):
    for n, (a, b) in enumerate([B1, B2, B3, B4, B5, B6, B7], start=1):
        if a <= t < b:
            return n
    return 8  # tela azul final

# goteira (visual e áudio sincronizados): a gota bate no chão em GOTA_FASE + k*GOTA_PERIODO
GOTA_PERIODO = 1.25
GOTA_FASE = 52.4
