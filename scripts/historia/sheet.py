import glob, sys
from PIL import Image, ImageDraw
pat, out, bgc = sys.argv[1], sys.argv[2], tuple(int(sys.argv[3][i:i+2], 16) for i in (0, 2, 4)) if len(sys.argv) > 3 else (237, 237, 237)
fs = sorted(glob.glob(pat)); cell = 260; cols = 6; rows = -(-len(fs) // cols)
sh = Image.new("RGB", (cols * cell, rows * (cell + 18)), bgc); d = ImageDraw.Draw(sh)
for i, f in enumerate(fs):
    im = Image.open(f).convert("RGBA"); im.thumbnail((cell - 10, cell - 10)); x, y = (i % cols) * cell, (i // cols) * (cell + 18)
    sh.paste(im, (x + 5, y + 5), im); d.text((x + 5, y + cell), f.split("/")[-1], fill=(242, 59, 59))
sh.save(out, quality=88)
