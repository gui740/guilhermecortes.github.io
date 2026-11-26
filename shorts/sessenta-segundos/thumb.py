"""Thumbnail 1080x1920 do Short (mesmos elementos visuais do vídeo). -> out/thumbnail.png"""
import numpy as np
from PIL import Image, ImageFilter
import render as R

R.init()
t = 30.0
bg = R.background(t)
img = Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
R.particles(img, t)
# galáxia gigante ao fundo
g = R.icon_galaxy(1000, 12.0, sun=False, streak=True)
g.putalpha(g.getchannel("A").point(lambda v: int(v * 0.55)))
img.alpha_composite(g, (40, 380))
R.paste(img, R.pill("EM 60 SEGUNDOS", 52, bg=R.CYAN), R.CX, 300)
R.paste(img, R.rich_text("VOCÊ VOOU", 120), R.CX, 470)
R.num_text(img, "36.000 KM", 230, R.YEL, R.RED, R.CX, 690)
R.paste(img, R.rich_text("SEM SAIR DO", 110), R.CX, 900)
R.paste(img, R.rich_text("*SOFÁ*", 190), R.CX, 1060)
R.paste(img, R.icon_sofa(420), R.CX, 1330)
R.paste(img, R.icon_heart(170, 0.6), 230, 1240, rot=12)
R.paste(img, R.globe_rgba(80, 10.0, pin=True), 860, 1220)
R.paste(img, R.rich_text("PERA, OI?", 110, "anton", color=R.YEL, stroke=10), R.CX, 1560)
img.convert("RGB").save(R.OUT + "/thumbnail.png")
img.convert("RGB").resize((540, 960), Image.LANCZOS).save(R.OUT + "/thumbnail_preview.png")
print("ok")
