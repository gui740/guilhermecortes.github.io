"""Recorta (rembg) e aplica textura de revista antiga: +contraste/saturação, retícula CMY colorida, granulado.
Saída: public/cut/<nome>.png (com contorno branco fino estilo adesivo) e public/cut/<nome>_n.png (sem contorno)."""
import sys, numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove, new_session

RAW = "assets/img/raw/"
JOBS = {  # nome: (arquivo, crop relativo (l,t,r,b))
 "buddy_wave":  ("po_1OXfvQAvhhsnZEWXcCXn6i8kzlG.jpg", (0.0, 0.0, 1.0, 0.70)),
 "buddy_group": ("po_6hlAe9tIdpUIlLvyrxb5y6BFLN9.jpg", (0.0, 0.25, 1.0, 0.68)),
 "buddy_close": ("bd_n7HFbOBJZsaCnBYPCXEViU2gObn.jpg", (0.25, 0.0, 0.75, 1.0)),
 "buddy_hug":   ("bd_oQFU9ncW1RLh4QRiIA0MHA92q4c.jpg", (0.20, 0.0, 0.85, 1.0)),
 "kids_scared": ("bd_i8Y6RYLaeoYXP8ncDjyCpp5ttFv.jpg", (0.0, 0.25, 0.80, 1.0)),
 "kids_forest": ("bd_pa5U0THGpqEmKf3R4LvuwBL5CbT.jpg", (0.0, 0.10, 1.0, 1.0)),
 "dark_buddy":  ("bd_464nqiPtcXCaIHnJcSIwKWQ3pFQ.jpg", (0.45, 0.0, 0.98, 1.0)),
 "girl_grab":   ("bd_94iCX0TLofZHqkrSah6TSlEfDVP.jpg", (0.0, 0.0, 0.75, 1.0)),
 "bunny":       ("bd_xvPqm419TsKtLkoMJq0SveEnd5W.jpg", (0.20, 0.0, 0.95, 1.0)),
 "buddy_point": ("po_cbJn9TSEQb5Lu1i3WP4SMrnnICI.jpg", (0.0, 0.22, 1.0, 0.86)),
 "buddy_tvpo":  ("po_9qbbndIBH7j0AcoOEOfwzkSAyvZ.jpg", (0.0, 0.0, 1.0, 0.75)),
}
only = sys.argv[1:] or list(JOBS)
sess = new_session("isnet-general-use")

def halftone_channel(ch, cell, angle):
    """ch: float 0..1 (tinta). Retorna máscara de pontos (1 = tinta)."""
    h, w = ch.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(angle); c, s = np.cos(a), np.sin(a)
    u = (xx*c + yy*s)/cell; v = (-xx*s + yy*c)/cell
    fu, fv = u - np.floor(u) - 0.5, v - np.floor(v) - 0.5
    d = np.sqrt(fu**2 + fv**2)           # 0 no centro da célula .. ~0.707
    r = np.sqrt(np.clip(ch, 0, 1)/np.pi) * 1.0  # raio proporcional à área de tinta
    return np.clip((r - d)*cell*1.2 + 0.5, 0, 1)

def texture(rgb, seed=0):
    img = ImageEnhance.Contrast(rgb).enhance(1.18)
    img = ImageEnhance.Color(img).enhance(1.30)
    a = np.asarray(img).astype(np.float32)/255
    cell = max(7, round(min(a.shape[:2])/115))  # retícula grande e visível
    cmy = 1 - a
    k = cmy.min(2)
    inks = [(cmy[..., i]-k)/(1-k+1e-6) for i in range(3)]
    dots = [halftone_channel(inks[i]*0.95, cell, ang) for i, ang in zip(range(3), (15, 75, 0))]
    kd = halftone_channel(k*0.9, cell, 45)
    ht = np.stack([1-dots[i] for i in range(3)], 2) * (1 - kd[..., None])
    out = a*0.45 + ht*0.55                  # mistura: cor original + retícula impressa
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 0.075, a.shape[:2])[..., None]
    g = np.asarray(Image.fromarray(((g[...,0]+0.5)*255).clip(0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)/255 - 0.5
    out = out + g[..., None]*0.55
    # papel levemente quente
    out = out*np.array([1.0, 0.985, 0.95]) + np.array([0.02, 0.015, 0.0])
    return Image.fromarray((out.clip(0, 1)*255).astype(np.uint8))

for i, name in enumerate(only):
    f, (l, t, r, b) = JOBS[name]
    im = Image.open(RAW+f).convert("RGB")
    W, H = im.size
    im = im.crop((int(l*W), int(t*H), int(r*W), int(b*H)))
    if max(im.size) > 1800: im.thumbnail((1800, 1800), Image.LANCZOS)
    cut = remove(im, session=sess, post_process_mask=True)
    am = np.asarray(cut.split()[-1])
    from scipy import ndimage
    lab, n = ndimage.label(am > 60)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(am), lab, range(1, n+1))
        keep = [i+1 for i, sz in enumerate(sizes) if sz >= 0.08*sizes.max()]
        am = np.where(np.isin(lab, keep), am, 0).astype(np.uint8)
    alpha = Image.fromarray(am).filter(ImageFilter.GaussianBlur(0.8))
    bbox = alpha.point(lambda v: 255 if v > 20 else 0).getbbox()
    tex = texture(im, seed=i)
    rgba = tex.convert("RGBA"); rgba.putalpha(alpha)
    rgba = rgba.crop(bbox); a2 = rgba.split()[-1]
    pad = 24
    canvas = Image.new("RGBA", (rgba.width+2*pad, rgba.height+2*pad), (0, 0, 0, 0))
    canvas.paste(rgba, (pad, pad))
    canvas.save(f"public/cut/{name}_n.png")
    # contorno branco (adesivo)
    m = canvas.split()[-1].point(lambda v: 255 if v > 90 else 0)
    stroke = m.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(1.2))
    st = Image.new("RGBA", canvas.size, (255, 255, 255, 0)); st.putalpha(stroke)
    st.alpha_composite(canvas)
    st.save(f"public/cut/{name}.png")
    print(name, canvas.size)
