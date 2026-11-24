"""Folha de cenas: um quadro de cada cena (no momento em que tudo já entrou), com legenda."""
import json, os
from scipy.io import wavfile
from render import *
durs = []
for k in range(len(SCENES)):
    p = f"narracao/cena_{k+1:02d}.wav"
    if os.path.exists(p):
        sr, x = wavfile.read(p); durs.append(len(x) / sr + .5)
    else:
        durs.append(len(SCENES[k]["text"].split()) / WPS + .5)
ims = []
for k, sc in enumerate(SCENES):
    dur = durs[k]; times = word_times(k, dur)
    bg, sp = build(sc, dur, times)
    t = dur - .25
    fr = compose(bg, sp, t, dur, sc["cam"], [])
    groups = chunks(sc["text"])
    fr.alpha_composite(caption_band(), (0, H - 420))
    fr.alpha_composite(caption_img(groups[-1], len(groups[-1]) - 1), (0, 1530))
    ims.append(film(fr, k).resize((360, 640)))
sheet = Image.new("RGB", (360 * 5, 640 * 2))
for i, im in enumerate(ims): sheet.paste(im, ((i % 5) * 360, (i // 5) * 640))
sheet.save("sheet.jpg", quality=88)
print("sheet.jpg")
