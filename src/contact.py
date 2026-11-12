# Folha de contato: 1 frame a cada 0,5s, com timestamp e a fala daquele momento.
import sys, subprocess, json, os
from PIL import Image, ImageDraw, ImageFont
vid, out = sys.argv[1], sys.argv[2]; step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
dur = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',vid],capture_output=True,text=True).stdout)
words = json.load(open(os.path.join(os.path.dirname(__file__), 'words.json')))
tmp = os.path.join(os.path.dirname(out), '_cs'); os.makedirs(tmp, exist_ok=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',vid,'-vf',f'fps=1/{step},scale=216:384',f'{tmp}/%04d.png'])
fs = sorted(os.listdir(tmp)); cols = 10; W, H = 216, 384; rows = (len(fs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * W, rows * (H + 34)), 'white'); d = ImageDraw.Draw(sheet)
font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '..', 'public/fonts/Inter.ttf'), 13)
for i, f in enumerate(fs):
    t = i * step; x, y = (i % cols) * W, (i // cols) * (H + 34)
    sheet.paste(Image.open(f'{tmp}/{f}'), (x, y))
    said = ' '.join(w['w'] for w in words if w['s'] <= t + 0.25 and w['e'] >= t - 0.25)[:30]
    d.text((x + 4, y + H + 2), f'{t:05.2f}s', fill='black', font=font); d.text((x + 4, y + H + 17), said, fill=(150, 30, 30), font=font)
sheet.save(out); [os.remove(f'{tmp}/{f}') for f in fs]; os.rmdir(tmp)
print(out, len(fs), 'frames')
