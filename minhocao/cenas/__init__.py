"""Tabela de cenas: (início, fim, cena(t, i), estilo(t), osd(t, i, img) | None)."""
import config as C
from . import abertura, boletim, regras, sonar, margem, contato, fim

_B = {nome: (a, b) for nome, a, b in C.BLOCOS}

CENAS = [
    ("abertura", *_B["abertura"], abertura.cena, abertura.estilo, abertura.osd),
    ("boletim", *_B["boletim"], boletim.cena_boletim, boletim.estilo_boletim, None),
    ("fora_script", *_B["fora_script"], boletim.cena_fora_script, boletim.estilo_fora, None),
    ("regras", *_B["regras"], regras.cena, regras.estilo, None),
    ("sonar", *_B["sonar"], sonar.cena, sonar.estilo, None),
    ("margem", *_B["margem"], margem.cena, margem.estilo, margem.osd),
    ("contato", *_B["contato"], contato.cena, contato.estilo, None),
    ("fim", *_B["fim"], fim.cena, fim.estilo, None),
]

# instantes usados no --preview (um PNG por momento-chave de cada cena)
PREVIEW = {
    "abertura": [0.5, 3.0, C.T_ETIQUETA],
    "boletim": [7.6, 15.5],
    "fora_script": [21.0, 25.8, C.T_SUBLIMINAR1],
    "regras": [36.0, 51.5],
    "sonar": [53.0, 57.6],
    "margem": [59.8, 61.8, 63.2, 65.0],
    "contato": [71.0],
    "fim": [73.6, 76.0, 79.5, 80.8],
}


def cena_em(t):
    for item in CENAS:
        if item[1] <= t < item[2]:
            return item
    return CENAS[-1]
