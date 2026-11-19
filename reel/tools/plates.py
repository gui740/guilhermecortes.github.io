import sys,numpy as np,cv2
sys.path.insert(0,'tools'); from treat import bw,halftone,grain,sticker
from PIL import Image
rng=np.random.default_rng(11)
def torn(h,w,inset=26,rough=10):
    m=np.zeros((h,w),np.uint8)
    def edge(n): 
        e=np.cumsum(rng.standard_normal(n))*1.4; e=e-np.linspace(e[0],e[-1],n); return cv2.GaussianBlur(e.reshape(1,-1),(0,0),3).ravel()+rng.standard_normal(n)*1.2
    top=inset+edge(w)*rough/10; bot=h-inset+edge(w)*rough/10; lef=inset+edge(h)*rough/10; rig=w-inset+edge(h)*rough/10
    yy,xx=np.mgrid[0:h,0:w]
    m[(yy>top[None,:])&(yy<bot[None,:])&(xx>lef[:,None])&(xx<rig[:,None])]=255
    return cv2.GaussianBlur(m,(0,0),0.8)
def plate(src,out,crop=None,width=1000,cell=6,contrast=1.4):
    im=Image.open(src).convert('RGB')
    if crop: im=im.crop(crop)
    im=im.resize((width,int(im.height*width/im.width)),Image.LANCZOS)
    rgb=np.array(im); h,w=rgb.shape[:2]
    g=grain(halftone(bw(rgb,contrast),cell)); al=torn(h,w)
    col,a=sticker(g,al,9)
    c=np.maximum((np.clip(col,0,1)*237).astype(np.uint8),28)
    Image.fromarray(np.dstack([c,c,c,(a*255).astype(np.uint8)])).save(out); print(out,c.shape)
def still(src,out,w=640,h=480):
    im=Image.open(src).convert('RGB'); r=max(w/im.width,h/im.height)
    im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS); x=(im.width-w)//2; y=(im.height-h)//2; im=im.crop((x,y,x+w,y+h))
    g=grain(halftone(bw(np.array(im),1.35),5,mix=0.4),0.07); c=np.maximum((g*237).astype(np.uint8),28)
    Image.fromarray(c).save(out)
plate('assets/films/ghostland/backdrop_05.jpg','public/img/films/ghost_set.png',(0,0,1280,720))
plate('assets/films/huesera/backdrop_01.jpg','public/img/films/huesera_set.png',(150,0,1130,720))
import os; os.makedirs('public/img/stills',exist_ok=True)
S={'ghost':['ghostland/backdrop_02','ghostland/backdrop_05','ghostland/backdrop_06','ghostland/backdrop_11','ghostland/backdrop_01','ghostland/backdrop_09'],
   'medium':['medium/backdrop_01','medium/backdrop_03','medium/backdrop_04','medium/backdrop_06','medium/backdrop_08','medium/poster_01'],
   'huesera':['huesera/backdrop_01','huesera/backdrop_02','huesera/backdrop_03','huesera/backdrop_05','huesera/backdrop_00','huesera/backdrop_04']}
for k,l in S.items():
    for i,s in enumerate(l): still(f'assets/films/{s}.jpg',f'public/img/stills/{k}_{i}.jpg')
print('stills ok')
