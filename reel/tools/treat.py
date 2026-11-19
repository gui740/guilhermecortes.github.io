"""B&W alto contraste + granulado + retícula (halftone) + borda branca de adesivo."""
import sys,numpy as np,cv2
from PIL import Image
rng=np.random.default_rng(3)
def bw(rgb,contrast=1.5,gamma=1.0):
    g=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).astype(np.float32)/255
    clahe=cv2.createCLAHE(2.0,(8,8)); g=clahe.apply((g*255).astype(np.uint8)).astype(np.float32)/255
    g=np.clip((g-0.5)*contrast+0.5,0,1)**gamma
    return g
def halftone(g,cell=7,angle=45,mix=0.55):
    h,w=g.shape; yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    a=np.deg2rad(angle); u=(xx*np.cos(a)+yy*np.sin(a))/cell; v=(-xx*np.sin(a)+yy*np.cos(a))/cell
    d=np.sqrt((u-np.round(u))**2+(v-np.round(v))**2)  # 0..0.707
    blur=cv2.GaussianBlur(g,(0,0),cell*0.35)
    r=np.sqrt(np.clip(1-blur,0,1))*0.62
    dots=1-np.clip((r-d)*cell*1.4+0.5,0,1)  # 1 = paper, 0 = ink
    return np.clip(g*(1-mix)+dots*g.clip(0.15,1)**0.3*mix*1.0+ (dots-0.5)*0.0,0,1)*0+ (g*(1-mix)+np.minimum(g*1.25,dots)*mix)
def grain(g,amt=0.09):
    n=rng.standard_normal(g.shape).astype(np.float32); n=cv2.GaussianBlur(n,(0,0),0.7)
    return np.clip(g+n*amt,0,1)
def sticker(rgb_g,alpha,border=10):
    a=(alpha>127).astype(np.uint8)*255
    pad=border+8
    a2=cv2.copyMakeBorder(alpha,pad,pad,pad,pad,cv2.BORDER_CONSTANT,0)
    g2=cv2.copyMakeBorder(rgb_g,pad,pad,pad,pad,cv2.BORDER_CONSTANT,0)
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*border+1,2*border+1))
    outer=cv2.dilate(cv2.GaussianBlur(a2,(0,0),2),k)
    outer=cv2.GaussianBlur(outer,(0,0),1.0)
    af=a2.astype(np.float32)/255; of=outer.astype(np.float32)/255
    col=g2*af+0.93*(1-af)   # borda #EDEDED
    return col,of
def run(src,out,mode,border=10,cell=7,contrast=1.5,fadebottom=0):
    im=np.array(Image.open(src).convert('RGBA')); rgb=im[:,:,:3]; al=im[:,:,3]
    if fadebottom:
        h=al.shape[0]; ramp=np.clip((h-np.arange(h))/ (h*fadebottom),0,1)[:,None]; al=(al*ramp).astype(np.uint8)
    g=grain(halftone(bw(rgb,contrast),cell))
    if mode=='sticker':
        col,a=sticker(g,al,border)
    else:
        col,a=g,al.astype(np.float32)/255
    c=(np.clip(col,0,1)*237+0).astype(np.uint8)   # branco máximo = #EDEDED
    c=np.maximum(c,28)                              # preto mínimo = #1C1C1C
    Image.fromarray(np.dstack([c,c,c,(a*255).astype(np.uint8)])).save(out); print(out,c.shape)
if __name__=='__main__':
    a=sys.argv; run(a[1],a[2],a[3],*[float(x) for x in a[4:]])
