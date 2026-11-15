"""Corta os PNGs de texto no bounding box do alpha e grava as dimensões reais em src/texts.json."""
import json, os, glob, re
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'public/tex/txt/*.png'))):
    k = os.path.basename(f)[:-4]
    im = Image.open(f).convert('RGBA'); bb = im.getchannel('A').point(lambda v: 255 if v > 2 else 0).getbbox()
    words = re.match(r'(hk|hb|hc|c\d|k\d|sd|q\d|f\d|cv)', k) is not None
    if bb:
        im = im.crop((bb[0], 0, bb[2], im.height) if words else bb); im.save(f)
    base = k[:-2] if k.endswith('_b') else k
    m = meta.setdefault(base, {})
    if k.endswith('_b'): m['bw'], m['bh'] = im.size
    else: m['w'], m['h'] = im.size
json.dump(meta, open(os.path.join(ROOT, 'src/texts.json'), 'w'), indent=1)
print(len(meta))
