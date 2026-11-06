"""Registro das cenas: nome do bloco -> função cena(t, frame_idx) -> PIL.Image 360x640."""
from . import abertura, alerta, fim, patio, patrimonio, regras

CENAS = {
    "abertura": abertura.cena,
    "patrimonio": patrimonio.cena,
    "corrupcao": patrimonio.cena_corrupcao,
    "regras": regras.cena,
    "alerta": alerta.cena,
    "patio": patio.cena,
    "fim": fim.cena,
}
