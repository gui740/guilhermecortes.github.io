"""Tabela de cenas: (início, fim, cena(t, i), estilo(t), osd(t, i, img) | None)."""
import config as C
from . import gancho, abertura, boletim, regras, sonar, margem, contato, fim

_B = {nome: (a, b) for nome, a, b in C.BLOCOS}

CENAS = [
    ("gancho", *_B["gancho"], gancho.cena, gancho.estilo, gancho.osd),
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
    "gancho": [0.9, 2.6, 3.5],
    "abertura": [4.6],
    "boletim": [6.0, 13.5],
    "fora_script": [18.0, 21.8, C.T_SUBLIMINAR1],
    "regras": [C.T_REGRA[1][0] + 2.5, C.T_REGRA[6][0] + 4.0, C.T_1968 + 1.5],
    "sonar": [C.T_SONAR + 1.0, C.T_SONAR + 5.5],
    "margem": [C.T_CORTES_MARGEM[0] + 1.0, C.T_CORTES_MARGEM[1] + 1.0, C.T_CORTES_MARGEM[3] + 1.0,
               C.T_CORTES_MARGEM[4] + 1.0, C.T_CORTES_MARGEM[4] + 1.7],
    "contato": [C.T_CONTATO + 5.0],
    "fim": [C.T_FIM + 0.8, C.T_CARTAO_REAL + 2.0, C.T_CARTAO_FICCAO + 1.0],
}


def cena_em(t):
    for item in CENAS:
        if item[1] <= t < item[2]:
            return item
    return CENAS[-1]
