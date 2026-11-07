"""Configuração central do ROLO 7: A CASA DA ESQUINA (versão 2: aviso de emergência).

O roteiro é montado em tempo de execução a partir da duração real de cada fala
(roteiro.py), para que cada texto fique na tela exatamente o tempo da leitura.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ASSETS = RAIZ / "assets"
FONTES = ASSETS / "fonts"
SAIDA = RAIZ / "saida"
ARQUIVO_FINAL = SAIDA / "rolo7_casa_da_esquina.mp4"

# ---------------------------------------------------------------- vídeo
FPS = 30
W, H = 540, 960            # resolução interna de "fita" (metade da saída)
OUT_W, OUT_H = 1080, 1920
SEED = 1974
SR = 48000

HANDLE = "@talking_horror"
INCLUIR_CARTAO_HISTORIA = True

# área segura TikTok/Reels em px internos (180 px em cima / 320 px embaixo na saída)
SEGURO_TOPO = 96
SEGURO_BASE = H - 166

# ---------------------------------------------------------------- efeitos
FX_AVISO = 0.32        # telas de texto: granulado presente, mas sem atrapalhar a leitura
FX_CFTV = 0.75
FX_FINAL = 0.95

# ---------------------------------------------------------------- textos
EMISSORA = "CANAL 9  ·  CUIABÁ"
CABECALHO = ["INSTRUÇÕES AO VIGIA NOTURNO", "BAIRRO BANDEIRANTES"]
SUBCABECALHO = "LEIA ATÉ O FIM"

# introdução (fita de treinamento do vigia)
FITA = ["FITA DE TREINAMENTO Nº 7", "VIGILÂNCIA NOTURNA", "BAIRRO BANDEIRANTES", "TURNO: 22:00 — 06:00"]
ALVO = "CASARÃO BANDEIRANTES"
OBJETIVO = "OBJETIVO: COMPLETAR A RONDA"

REGRAS = [
    "SE SÓ A LUZ DA COZINHA ESTIVER ACESA, PODE PASSAR. É JANTAR.",
    "SE TODAS AS LUZES ESTIVEREM ACESAS, ATRAVESSE A RUA. A FESTA NÃO É PARA VOCÊ.",
    "SE OUVIR COPOS BRINDANDO, NÃO CONTE QUANTOS. VOCÊ VAI CONTAR UM A MAIS.",
    "SE A VOZ DO DISCURSO DISSER O SEU NOME, ELA NÃO ESTÁ LENDO. ESTÁ CHAMANDO.",
    "VULTO DE CAMISOLA NA VARANDA: NÃO ACENE. ELA ACENA DE VOLTA.",
    "SE OUVIR ÁGUA PINGANDO NO ESCURO, NÃO CHAME O CASEIRO. ELE SAIU HÁ MUITO TEMPO.",
    "NUNCA LIGUE A TV NEM O RÁDIO DENTRO DA CASA.",
]
REGRA7_EXTRA = "SE VOCÊ ESTÁ VENDO ISTO, ALGUÉM LIGOU."

# falas (o que a locutora lê; texto natural, não caixa alta)
FALAS = {
    "intro1": "Você é o novo vigia noturno do bairro Bandeirantes.",
    "intro2": "Esta é a casa da esquina. Durante a ronda, siga estas regras.",
    "regra1": "Regra um. Se só a luz da cozinha estiver acesa, pode passar. É jantar.",
    "regra2": "Regra dois. Se todas as luzes estiverem acesas, atravesse a rua. A festa não é para você.",
    "regra3": "Regra três. Se ouvir copos brindando, não conte quantos. Você vai contar um a mais.",
    "regra4": "Regra quatro. Se a voz do discurso disser o seu nome, ela não está lendo. Está chamando.",
    "regra5": "Regra cinco. Vulto de camisola na varanda: não acene. Ela acena de volta.",
    "regra6": "Regra seis. Se ouvir água pingando no escuro, não chame o caseiro. Ele saiu há muito tempo.",
    "regra7": "Regra sete. Nunca ligue a TV nem o rádio dentro da casa.",
    "extra": "Se você está vendo isto, alguém ligou.",
    "quem": "Quem está ouvindo?",
}

# cortes rápidos de câmera de segurança inseridos depois de algumas regras
# regra (1-based) -> (variante, duração em s)
INSERTOS = {2: ("festa", 1.1), 5: ("varanda", 1.2), 6: ("goteira", 1.6)}

CARTAO = [
    'INSPIRADO NA LENDA URBANA DO "CASARÃO ASSOMBRADO" DO BAIRRO BANDEIRANTES, EM CUIABÁ.',
    'A PROFESSORA ANA MARIA DO COUTO, A "MAY" (1925–1971), FOI ATLETA, ADVOGADA, JORNALISTA, '
    "RADIALISTA E VEREADORA. NUNCA FOI UM FANTASMA.",
    "OBRA DE FICÇÃO.",
]
CARTAO_DUR = 5.5

CFTV_HORA = (3, 13, 40)
GOTA_PERIODO = 1.25
GOTA_FASE = 0.3

# ---------------------------------------------------------------- voz
# Gemini TTS (precisa da variável de ambiente GEMINI_API_KEY; a chave nunca vai para o repositório).
# Sem chave, cai para espeak-ng.
TTS_MODELO = "gemini-3.8-flash-tts"
TTS_RESERVA = ["gemini-3.8-flash-lite-tts", "gemini-3.1-flash-tts-preview"]  # se a cota diária acabar
TTS_VOZ = "Kore"
