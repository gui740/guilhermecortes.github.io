"""Configuração central: textos, tempos, seed e handle.

Todos os tempos em segundos no relógio global do vídeo.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ASSETS = RAIZ / "assets"
FONTES = ASSETS / "fonts"
SAIDA = RAIZ / "saida"
ARQUIVO_FINAL = SAIDA / "aviso_pescadores_rio_cuiaba.mp4"

HANDLE = "@talking_horror"
SEED = 1974

# Fita interna (efeitos aplicados aqui) e saída final
W, H = 360, 640
OUT_W, OUT_H = 1080, 1920
FPS = 30
SR = 48000  # áudio

# Área segura TikTok/Reels na resolução interna (180 px / 320 px na saída)
SAFE_TOP = 62
SAFE_BOTTOM = H - 108  # 532

# --------------------------------------------------------------------------
# Voz (TTS). Ordem de preferência: Gemini (Google AI Studio) -> Piper -> espeak-ng
# A chave vem da variável de ambiente GEMINI_API_KEY (nunca versionada).
# --------------------------------------------------------------------------
TTS_GEMINI_MODELO = "gemini-3.8-flash-tts"
TTS_GEMINI_VOZ = "Charon"

# --------------------------------------------------------------------------
# Regras: (ícone, texto da cartela, duração da cartela em s)
# Cada regra amarrada a um elemento da lenda do Minhocão do Pari.
# --------------------------------------------------------------------------
REGRAS = [
    ("peixe", "NA PIRACEMA O RIO É DELE. O MINHOCÃO GUARDA OS PEIXES E VIRA A CANOA DE QUEM PESCA.", 4.2),
    ("cego", "ELE É CEGO. ELE SENTE A VIBRAÇÃO. NÃO BATA O REMO NO CASCO. DESLIGUE O MOTOR.", 4.0),
    ("tronco", "TRONCO PRETO, LISO E ANELADO NÃO É TRONCO. SÃO AS COSTAS DELE. NÃO PISE.", 4.0),
    ("redemoinho", "NÃO PESQUE NOS DOIS POÇOS FUNDOS DO PARI. É ALI QUE ELE DORME.", 3.8),
    ("canoa", "CANOAS AMARRADAS BATENDO UMA NA OUTRA SEM VENTO? ELE ESTÁ EMBAIXO. VÁ PARA CASA.", 4.2),
    ("barranco", "BARRANCO CAINDO SEM CHUVA É ELE PASSANDO. SAIA DA MARGEM.", 3.6),
    ("igreja", "ELE ESTÁ PRESO SOB A IGREJA MATRIZ POR TRÊS FIOS DE CABELO DE NOSSA SENHORA. DOIS JÁ ARREBENTARAM.", 5.2),
]
# Versões faladas pelo locutor (pontuação para o TTS)
REGRAS_FALA = [
    "Regra um. Na piracema, o rio é dele. O Minhocão guarda os peixes, e vira a canoa de quem pesca.",
    "Regra dois. Ele é cego. Ele sente a vibração. Não bata o remo no casco. Desligue o motor.",
    "Regra três. Tronco preto, liso e anelado não é tronco. São as costas dele. Não pise.",
    "Regra quatro. Não pesque nos dois poços fundos do Pari. É ali que ele dorme.",
    "Regra cinco. Canoas amarradas batendo uma na outra, sem vento? Ele está embaixo. Vá para casa.",
    "Regra seis. Barranco caindo sem chuva é ele passando. Saia da margem.",
    "Regra sete. Ele está preso sob a igreja matriz, por três fios de cabelo de Nossa Senhora. Dois já arrebentaram.",
]
REGRA_FINAL = "NUNCA REFORME A IGREJA."
REGRA_FINAL_FALA = "Nunca reforme a igreja."
REGRA_1968 = "JÁ DERRUBARAM UMA EM 1968."

# --------------------------------------------------------------------------
# Linha do tempo (blocos). (nome, início, fim)
# --------------------------------------------------------------------------
T_GANCHO_FIM = 4.0
T_REGRAS_INI = 24.0
T_REGRAS0 = T_REGRAS_INI + 0.2
_t = T_REGRAS0
T_REGRA = []
for _ic, _tx, _d in REGRAS:
    T_REGRA.append((_t, _t + _d))
    _t += _d
T_REGRA_FINAL = _t + 0.1
T_1968 = T_REGRA_FINAL + 1.6
T_REGRAS_FIM = round(T_1968 + 2.0, 2)

T_SONAR = T_REGRAS_FIM
T_MARGEM = T_SONAR + 6.5
T_CORTES_MARGEM = [T_MARGEM + k * 2.0 for k in range(5)]
T_CONTATO = T_MARGEM + 10.4
T_PRETO = T_CONTATO + 6.2
T_FIM = T_PRETO + 0.6

BLOCOS = [
    ("gancho", 0.0, T_GANCHO_FIM),
    ("abertura", T_GANCHO_FIM, 5.4),
    ("boletim", 5.4, 17.0),
    ("fora_script", 17.0, T_REGRAS_INI),
    ("regras", T_REGRAS_INI, T_REGRAS_FIM),
    ("sonar", T_SONAR, T_MARGEM),
    ("margem", T_MARGEM, T_CONTATO),
    ("contato", T_CONTATO, T_FIM),
    ("fim", T_FIM, T_FIM + 8.3),
]
DURACAO = BLOCOS[-1][2]

# Sub-tempos ---------------------------------------------------------------
T_VOZ_GANCHO = 0.5
T_ETIQUETA = 5.05            # flash de 2 frames
T_VINHETA_FIM = 6.8          # vinheta -> mapa
T_VOZ1 = 7.0                 # início da fala do locutor (bloco 2)
SLOT_VOZ1 = 9.6              # cabe até ~16,6 s
T_REGUA = [(17.0, "8,4"), (18.4, "11,7"), (19.8, None)]  # None = embaralhado
T_VOZ_LENTA = 17.5
T_VOZ_CORRECAO = 20.4
T_SUBLIMINAR1 = 23.45

T_SONAR_LEITURAS = [(T_SONAR, "4 M"), (T_SONAR + 2.5, "12 M"), (T_SONAR + 3.7, "37 M"), (T_SONAR + 4.8, "---")]
T_CRIATURA_SONAR = T_SONAR + 1.4

T_LEGENDAS = [
    (T_CONTATO + 0.3, "[SOM NÃO IDENTIFICADO — POÇO DO PARI]"),
    (T_CONTATO + 1.6, "O RIO É DOS PEIXES ATÉ A ÁGUA BAIXAR."),
    (T_CONTATO + 4.0, "VOLTE EM FEVEREIRO."),
]

T_FIM_TEXTO = T_FIM
T_CARTAO_REAL = T_FIM + 1.6       # 4 s limpos
T_CARTAO_FICCAO = T_CARTAO_REAL + 4.0
T_STOP = T_CARTAO_FICCAO + 2.0    # ■ STOP + tela azul ~10 frames

# --------------------------------------------------------------------------
# Textos
# --------------------------------------------------------------------------
GANCHO_FALA = "Se você pesca no Rio Cuiabá... não pule este aviso."
GANCHO = ["SE VOCÊ PESCA NO RIO CUIABÁ,", "NÃO PULE ESTE AVISO."]

EMISSORA = ["TV RIBEIRINHA", "CANAL 6", "CUIABÁ MT"]
TIMESTAMP = "SEX 15 MAR 1974 05:12"
ETIQUETA = "BOLETIM — NÃO EXIBIR"

TITULO = "BOLETIM DO RIO"
SUBTITULO = "AVISO AOS PESCADORES"

# Falas do locutor (cada frase sintetizada separadamente => legendas sincronizadas)
FALAS_BOLETIM = [
    ("Bom dia, pescador.", "canoa"),
    ("Rio Cuiabá subindo devagar.", "gota"),
    ("Tempo firme na Barra do Pari.", "nuvem"),
    ("Peixe de escama começando a subir o rio.", "peixe"),
    ("Boa pescaria.", "anzol"),
]
FALA_LENTA = "Boa... pescaria..."
FALA_CORRECAO = ["Correção.", "Não há boa pescaria.", "O rio está fechado."]

SUBLIMINAR1 = "ELE NÃO FOI EMBORA NA ENCHENTE."

CABECALHO_REGRAS = ["SERVIÇO DE AVISOS AOS PESCADORES", "RIO CUIABÁ"]
LEIA = "LEIA ATÉ O FIM"

FALA_CONTATO = "O rio é dos peixes até a água baixar. Volte em fevereiro."

FIM = ["FIM DO BOLETIM.", "BOA NOITE, CUIABÁ."]
FIM_GLITCH = "FALTA UM FIO."

CARTAO_REAL = [
    "O MINHOCÃO DO PARI É UMA LENDA DO FOLCLORE CUIABANO, NASCIDA NA BARRA DO PARI. DIZEM QUE ELE SUMIU NA ENCHENTE DE 1974.",
    "A PIRACEMA É REAL: DURANTE O DEFESO, A PESCA É PROIBIDA NOS RIOS DE MATO GROSSO "
    "PARA PROTEGER A REPRODUÇÃO DOS PEIXES. CONSULTE AS DATAS NA SEMA-MT.",
]
CARTAO_FICCAO = "OBRA DE FICÇÃO."

# Intensidade VHS por bloco (mais limpa que a v1, a pedido)
FX_INTENSIDADE = {
    "gancho": 0.35, "abertura": 0.3, "boletim": 0.15, "fora_script": 0.3, "regras": 0.2,
    "sonar": 0.35, "margem": 0.35, "contato": 0.45, "fim": 0.3,
    "glitch": 0.9, "cartao": 0.05,
}
