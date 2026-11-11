"""Folha de contato com guias de margem de segurança. Uso: sheet.py out.jpg cols img1 img2 ..."""
import sys
from PIL import Image, ImageDraw
out, cols, fs = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
tw, th = 270, 480
rows = (len(fs)+cols-1)//cols
S = Image.new("RGB", (cols*tw, rows*(th+22)), "white"); d = ImageDraw.Draw(S)
for i, f in enumerate(fs):
    im = Image.open(f).convert("RGB").resize((tw, th))
    g = ImageDraw.Draw(im); k = tw/1080
    g.rectangle([80*k, 250*k, (1080-140)*k, (1920-420)*k], outline=(0, 200, 255))
    x, y = (i % cols)*tw, (i//cols)*(th+22)
    S.paste(im, (x, y)); d.text((x+4, y+th+4), f.split("/")[-1], fill="black")
S.save(out, quality=85)
