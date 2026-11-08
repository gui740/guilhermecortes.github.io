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
# Linha do tempo (blocos). (nome, início, fim)
# --------------------------------------------------------------------------
T_PLAY_FIM = 1.2
BLOCOS = [
    ("abertura", 0.0, 6.0),
    ("boletim", 6.0, 20.0),
    ("fora_script", 20.0, 28.0),
    ("regras", 28.0, 52.0),
    ("sonar", 52.0, 59.0),
    ("margem", 59.0, 66.0),
    ("contato", 66.0, 73.0),
    ("fim", 73.0, 81.0),
]
DURACAO = BLOCOS[-1][2]

# Sub-tempos ---------------------------------------------------------------
T_ETIQUETA = 5.40            # flash de 2 frames
T_VINHETA_FIM = 9.0          # vinheta -> mapa
T_VOZ1 = 9.4                 # início da fala do locutor (bloco 2)
T_REGUA = [(20.0, "8,4"), (21.6, "11,7"), (23.2, None)]  # None = embaralhado
T_VOZ_LENTA = 20.6           # "boa... pescaria..."
T_VOZ_CORRECAO = 23.5        # "Correção. ..."
T_SUBLIMINAR1 = 27.62

T_REGRAS0 = 29.0             # primeira regra
DT_REGRA = 2.85              # ~3 s por regra
CPS_REGRA = 46.0             # caracteres por segundo da máquina de escrever
T_1968_ATRASO = 1.0          # depois que a regra 7 termina de digitar

T_SONAR_LEITURAS = [(52.0, "4 M"), (54.6, "12 M"), (55.9, "37 M"), (57.1, "---")]
T_CRIATURA_SONAR = 53.6
T_CORTES_MARGEM = [59.0, 60.75, 62.5, 64.25]

T_LEGENDAS = [
    (66.4, "[SOM NÃO IDENTIFICADO — LEITO DO RIO]"),
    (68.0, "O RIO É DOS PEIXES ATÉ A ÁGUA BAIXAR."),
    (70.0, "VOLTE EM FEVEREIRO."),
]
T_PRETO = 72.4               # silêncio absoluto + preto (0,6 s)

T_FIM_TEXTO = 73.0
T_CARTAO_REAL = 74.6         # 4 s limpos
T_CARTAO_FICCAO = 78.6       # 2 s
T_STOP = 80.6                # ■ STOP + tela azul ~10 frames

# --------------------------------------------------------------------------
# Textos
# --------------------------------------------------------------------------
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
REGRAS = [
    ("peixe", "É PIRACEMA. O RIO ESTÁ FECHADO. QUEM PESCA AGORA, PESCA PARA ELE."),
    ("tronco", "NÃO PISE EM TRONCO SUBMERSO. SE O TRONCO RESPIRAR, NÃO CORRA. FIQUE PARADO ATÉ ELE AFUNDAR."),
    ("tronco_vermelho", "TRONCO QUE BOIA CONTRA A CORRENTEZA NÃO É TRONCO."),
    ("barranco", "SE O BARRANCO CAIR SEM CHUVA, AFASTE A CANOA DA MARGEM. ELE ESTÁ ALARGANDO O RIO."),
    ("redemoinho", "REBOJO PERTO DA GUIA: NÃO REME PARA FORA. REME PARA TRÁS."),
    ("estrela", "PINTE ESTRELAS NO CASCO E LEVE CACHAÇA. NÃO É PARA ELE. É PARA OS OUTROS DO RIO."),
    ("igreja", "REGRA 7: NUNCA REFORME A IGREJA."),
]
REGRA_1968 = "JÁ DERRUBARAM UMA EM 1968."

FIM = ["FIM DO BOLETIM.", "BOA NOITE, CUIABÁ."]
FIM_GLITCH = "ELE CONTA AS CANOAS."

CARTAO_REAL = [
    "O MINHOCÃO DO PARI É UMA LENDA DO FOLCLORE CUIABANO, NASCIDA NA BARRA DO PARI.",
    "A PIRACEMA É REAL: DURANTE O DEFESO, A PESCA É PROIBIDA NOS RIOS DE MATO GROSSO "
    "PARA PROTEGER A REPRODUÇÃO DOS PEIXES. CONSULTE AS DATAS NA SEMA-MT.",
]
CARTAO_FICCAO = "OBRA DE FICÇÃO."

# Intensidade VHS por bloco (seção 5 do roteiro)
FX_INTENSIDADE = {
    "abertura": 0.4, "boletim": 0.3, "fora_script": 0.5, "regras": 0.5,
    "sonar": 0.75, "margem": 0.75, "contato": 0.9, "fim": 0.5,
    "glitch": 1.0, "cartao": 0.1,
}
