# -*- coding: utf-8 -*-
"""Roteiro: textos de narração e dados das fichas."""

ANIMALS = [
    dict(key="onca", num="001", name="ONÇA-PINTADA", sci="Panthera onca",
         types=["MAMÍFERO", "CARNÍVORO"], alt="0,75 m", peso="100 kg",
         habitat=["MATAS CILIARES", "E BEIRAS DE RIO"],
         stats=[("FORÇA", 10), ("NADO", 8), ("FURTIV.", 9)],
         status="QUASE AMEAÇADA", status_ok=False,
         say_name="Onça-pintada.",
         pages=["O maior felino das Américas.",
                "Nadadora habilidosa, tem uma das mordidas mais fortes entre os felinos.",
                "Seu cardápio inclui até jacarés."]),
    dict(key="tuiuiu", num="002", name="TUIUIÚ", sci="Jabiru mycteria",
         types=["AVE", "PERNALTA"], alt="1,40 m", peso="8 kg",
         habitat=["BAÍAS E CAMPOS", "ALAGADOS"],
         stats=[("VOO", 8), ("PESCA", 9), ("ENVERG.", 10)],
         status="POUCO PREOCUPANTE", status_ok=True,
         say_name="Tuiuiú.",
         pages=["Ave símbolo do Pantanal.",
                "De asas abertas, passa de dois metros e meio.",
                "Faz ninhos enormes no alto das árvores."]),
    dict(key="capivara", num="003", name="CAPIVARA", sci="Hydrochoerus hydrochaeris",
         types=["MAMÍFERO", "HERBÍVORO"], alt="0,60 m", peso="50 kg",
         habitat=["MARGENS DE RIOS", "E LAGOAS"],
         stats=[("NADO", 9), ("FORÇA", 4), ("SOCIAL", 10)],
         status="POUCO PREOCUPANTE", status_ok=True,
         say_name="Capivara.",
         pages=["O maior roedor do mundo.",
                "Vive em grupos à beira d'água e mergulha muito bem.",
                "Fica submersa por até cinco minutos."]),
]

NARRATION = {
    "boot": "Pantadex. Sistema de campo iniciado.",
    "world": "Pantanal mato-grossense. A maior planície alagável do planeta.",
    "scan1": "Sinal detectado! Escaneando.",
    "scan2": "Novo sinal! Escaneando.",
    "scan3": "Mais um sinal! Escaneando.",
    "end": "Três espécies catalogadas. Conhecer é o primeiro passo para proteger o Pantanal.",
}
for i, a in enumerate(ANIMALS, 1):
    NARRATION[f"a{i}_name"] = a["say_name"]
    for j, p in enumerate(a["pages"], 1):
        NARRATION[f"a{i}_p{j}"] = p
