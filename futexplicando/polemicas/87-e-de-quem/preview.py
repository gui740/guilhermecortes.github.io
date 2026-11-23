from render import *
ims=[]
for sc in SCENES:
    dur=len(sc["text"].split())/WPS+.5
    bg,sp=build(sc,dur)
    for s in sp:
        bg.alpha_composite(s.img,(int(s.x-s.img.width/2),int(s.y-s.img.height/2)))
    bg.alpha_composite(caption(chunks(sc["text"])[0]),(0,1560))
    ims.append(bg.convert("RGB").resize((360,640)))
sheet=Image.new("RGB",(360*5,640*2))
for i,im in enumerate(ims): sheet.paste(im,((i%5)*360,(i//5)*640))
sheet.save("sheet.jpg",quality=85)
ims[0]; 
