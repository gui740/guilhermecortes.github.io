import sys,glob
from PIL import Image,ImageDraw
fs=sorted(sum([glob.glob(p) for p in sys.argv[2:]],[])); W=320
tiles=[]
for f in fs:
    im=Image.open(f).convert('RGBA'); im.thumbnail((W,W))
    t=Image.new('RGBA',(W,W+14),(90,90,90,255)); 
    # half bright half dark bg to see halos
    d=ImageDraw.Draw(t); d.rectangle([W//2,0,W,W],fill=(235,235,235,255))
    t.alpha_composite(im,((W-im.width)//2,(W-im.height)//2)); d.text((3,W),f.split('/')[-1],fill='yellow'); tiles.append(t)
cols=4; rows=(len(tiles)+cols-1)//cols; S=Image.new('RGBA',(cols*W,rows*(W+14)),(20,20,20,255))
for i,t in enumerate(tiles): S.paste(t,((i%cols)*W,(i//cols)*(W+14)))
S.convert('RGB').save(sys.argv[1])
