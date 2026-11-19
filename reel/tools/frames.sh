#!/bin/bash
# usage: frames.sh COMP outsheet f1 f2 ...
comp=$1; sheet=$2; shift 2
for f in "$@"; do npx remotion still src/index.ts $comp out/test/f$f.png --frame=$f --gl=swangle --log=error >/dev/null 2>&1 || echo fail $f; done
python3 - "$sheet" "$@" <<'PY'
import sys
from PIL import Image,ImageDraw
sheet=sys.argv[1]; fs=[int(x) for x in sys.argv[2:]]; n=len(fs); cols=min(4,n); rows=(n+cols-1)//cols
S=Image.new('RGB',(270*cols,500*rows),'#000'); d=ImageDraw.Draw(S)
for i,f in enumerate(fs):
    im=Image.open(f'out/test/f{f}.png').convert('RGB').resize((270,480)); S.paste(im,((i%cols)*270,(i//cols)*500)); d.text(((i%cols)*270+4,(i//cols)*500+482),f'f{f} {f/30:.2f}s',fill='yellow')
S.save(sheet)
PY
