import sys,glob
from PIL import Image,ImageDraw
files=sorted(sum([glob.glob(p) for p in sys.argv[2:]],[])); W=300; cols=5
ims=[]
for f in files:
    im=Image.open(f).convert('RGB'); im.thumbnail((W,W)); ims.append((f,im))
rows=(len(ims)+cols-1)//cols; sheet=Image.new('RGB',(cols*W,rows*(W+16)),'#222')
d=ImageDraw.Draw(sheet)
for i,(f,im) in enumerate(ims):
    x=(i%cols)*W; y=(i//cols)*(W+16); sheet.paste(im,(x,y)); d.text((x+4,y+W+2),f.split('/')[-2][:6]+'/'+f.split('/')[-1],fill='yellow')
sheet.save(sys.argv[1]); print(sheet.size)
