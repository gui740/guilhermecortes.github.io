import sys,json,numpy as np,cv2
from PIL import Image
from rembg import remove,new_session
jobs=json.load(open(sys.argv[1])); sess={}
for j in jobs:
    m=j.get('model','isnet-general-use')
    if m not in sess: sess[m]=new_session(m)
    im=Image.open(j['src']).convert('RGB')
    if 'crop' in j: im=im.crop(tuple(j['crop']))
    if max(im.size)>1400: im.thumbnail((1400,1400))
    rgba=remove(im,session=sess[m],post_process_mask=True)
    a=np.array(rgba)[:,:,3]
    # keep largest components only (drop specks)
    _,bw=cv2.threshold(a,127,255,cv2.THRESH_BINARY)
    n,lab,stats,_=cv2.connectedComponentsWithStats(bw)
    if n>1:
        keep=np.zeros_like(bw); areas=stats[1:,cv2.CC_STAT_AREA]; mx=areas.max()
        for i,ar in enumerate(areas,1):
            if ar>mx*j.get('keep',0.15): keep[lab==i]=255
        a=np.minimum(a,cv2.dilate(keep,np.ones((5,5),np.uint8)))
    # fill small holes
    a=cv2.morphologyEx(a,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    # erosion 2px + feather
    a=cv2.erode(a,np.ones((3,3),np.uint8),iterations=j.get('erode',2))
    a=cv2.GaussianBlur(a,(0,0),j.get('feather',1.2))
    out=np.dstack([np.array(im),a])
    ys,xs=np.where(a>8); pad=6
    if len(ys)==0: print('EMPTY',j['out']); continue
    out=out[max(0,ys.min()-pad):ys.max()+pad,max(0,xs.min()-pad):xs.max()+pad]
    Image.fromarray(out).save(j['out']); print(j['out'],out.shape)
