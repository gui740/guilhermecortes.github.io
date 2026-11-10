"""Recorta UMA imagem com o BiRefNet (um processo por imagem, para não estourar a memória).
uso: python3 scripts/rembg_one.py <entrada> <saida.png>"""
import sys
from PIL import Image
from rembg import remove, new_session
im = Image.open(sys.argv[1]).convert("RGB"); im.thumbnail((1600, 1600), Image.LANCZOS)
remove(im, session=new_session("birefnet-general")).save(sys.argv[2])
