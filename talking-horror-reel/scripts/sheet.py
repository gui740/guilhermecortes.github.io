"""Folha de contato: python3 scripts/sheet.py <dir de pngs|video> <saida.jpg> [cols] [largura] [passo_s p/ vídeo]"""
import sys, os, glob, subprocess, tempfile
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 5; W = int(sys.argv[4]) if len(sys.argv) > 4 else 270
step = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
if os.path.isdir(src): fs = sorted(glob.glob(src + '/*.png')); labels = [os.path.basename(f)[1:5] for f in fs]
else:
    d = tempfile.mkdtemp(); subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'fps=1/{step},scale={W}:-1', d + '/%04d.png'], check=True)
    fs = sorted(glob.glob(d + '/*.png')); labels = ['%.1fs' % (i * step) for i in range(len(fs))]
ims = [Image.open(f).convert('RGB') for f in fs]
H = round(ims[0].height * W / ims[0].width)
sheet = Image.new('RGB', (cols * (W + 6), ((len(ims) + cols - 1) // cols) * (H + 6)), (40, 40, 40))
for i, im in enumerate(ims):
    im = im.resize((W, H)); ImageDraw.Draw(im).rectangle((0, 0, 46, 13), fill='black'); ImageDraw.Draw(im).text((2, 1), labels[i], fill='white')
    sheet.paste(im, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
sheet.save(out, quality=85); print(out, sheet.size)
