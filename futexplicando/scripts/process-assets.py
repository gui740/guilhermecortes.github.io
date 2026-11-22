"""Organiza e trata os assets baixados em public/sao-paulo/raw/.

- Escudos e logos -> public/sao-paulo/escudos/ e logos/ (SVG intactos; PNG recortados nas bordas transparentes)
- Fotos -> public/sao-paulo/fotos/: mesmo filtro em todas (contraste + granulado leve);
  fotos de pessoas recebem recorte de fundo com rembg (modelo u2net_human_seg).

Uso: python3 scripts/process-assets.py [--placeholders]
"""
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), "..", "public", "sao-paulo")
RAW = os.path.join(ROOT, "raw")
OUT = {k: os.path.join(ROOT, k) for k in ["escudos", "logos", "fotos"]}
for d in OUT.values():
    os.makedirs(d, exist_ok=True)

CRESTS = {
    "escudo-spfc-atual.svg": "escudo-spfc-atual.svg",
    "escudo-spfc-2022-site.svg": "escudo-spfc-2022-site.svg",
    "escudo-spfc-1930-bsp-1000px.png": "escudo-sp-floresta-1930.png",
    "escudo-spfc-1935-1981.png": "escudo-spfc-1935-1981.png",
    "escudo-spfc-1935-bsp-1000px.png": "escudo-casp-1935.png",
    "escudo-paulistano.svg": "escudo-paulistano.svg",
    "escudo-aa-palmeiras.svg": "escudo-aa-palmeiras.svg",
    "escudo-barcelona.svg": "escudo-barcelona.svg",
    "escudo-milan.svg": "escudo-milan.svg",
    "escudo-liverpool.svg": "escudo-liverpool.svg",
    "escudo-flamengo.svg": "escudo-flamengo.svg",
}
LOGOS = {
    "logo-libertadores.svg": "logo-libertadores.svg",
    "logo-conmebol-libertadores.svg": "logo-conmebol-libertadores.svg",
    "logo-mundial-clubes-fifa.svg": "logo-mundial-clubes-fifa.svg",
    "logo-copa-do-brasil.svg": "logo-copa-do-brasil.svg",
}
# (arquivo bruto, saída, recortar fundo?, largura máx)
PHOTOS = [
    ("foto-tele-santana.jpg", "tele-santana-recorte.png", True, 1400),
    ("foto-rogerio-ceni.jpg", "rogerio-ceni-recorte.png", True, 1600),
    ("foto-rai.jpg", "rai-recorte.png", True, 1400),
    ("foto-morumbi-aerea.jpg", "morumbi-aerea.jpg", False, 3000),
    ("foto-time-1930.jpg", "time-1930.jpg", False, 2000),
]


def trim_png(src, dst):
    im = Image.open(src).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    im.save(dst, optimize=True)


def film_look(im, seed):
    """Filtro único para todas as fotos: contraste + leve dessaturação + granulado."""
    rgb = im.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(1.28)
    rgb = ImageEnhance.Color(rgb).enhance(0.88)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.15)
    a = np.asarray(rgb).astype(np.float32)
    rng = np.random.default_rng(seed)
    grain = rng.normal(0, 9.0, a.shape[:2])[..., None]
    grain = np.asarray(Image.fromarray(np.clip(grain[..., 0] + 128, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)[..., None] - 128
    a = np.clip(a + grain * 1.2, 0, 255).astype(np.uint8)
    out = Image.fromarray(a)
    if im.mode == "RGBA":
        out = out.convert("RGBA")
        out.putalpha(im.getchannel("A"))
    return out


def cutout(im):
    from rembg import new_session, remove

    sess = new_session("u2net_human_seg")
    res = remove(im.convert("RGB"), session=sess, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15)
    bbox = res.getchannel("A").getbbox()
    return res.crop(bbox) if bbox else res


def placeholder(dst, w, h, label):
    from PIL import ImageDraw

    im = Image.new("RGBA", (w, h), (138, 138, 138, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, w - 5, h - 5], outline=(17, 17, 17, 255), width=8)
    d.text((20, 20), "PLACEHOLDER " + label, fill=(17, 17, 17, 255))
    if dst.endswith(".jpg"):
        im = im.convert("RGB")
    im.save(dst)


def main():
    use_ph = "--placeholders" in sys.argv
    missing = []
    for src, dst in {**CRESTS, **LOGOS}.items():
        folder = OUT["logos"] if src.startswith("logo") else OUT["escudos"]
        s = os.path.join(RAW, src)
        d = os.path.join(folder, dst)
        if not os.path.exists(s) or os.path.getsize(s) == 0:
            missing.append(src)
            if use_ph and not os.path.exists(d):
                if dst.endswith(".svg"):
                    shutil.copy(os.path.join(RAW, "escudo-spfc-atual.svg"), d)
                else:
                    placeholder(d, 300, 300, src)
            continue
        if src.endswith(".png"):
            trim_png(s, d)
        else:
            shutil.copy(s, d)
        print("ok", dst)
    for i, (src, dst, cut, maxw) in enumerate(PHOTOS):
        s = os.path.join(RAW, src)
        d = os.path.join(OUT["fotos"], dst)
        if not os.path.exists(s) or os.path.getsize(s) == 0:
            missing.append(src)
            if use_ph and not os.path.exists(d):
                placeholder(d, 800, 1000, src)
                if d.endswith(".jpg"):
                    Image.open(d).convert("RGB").save(d, "JPEG")
            continue
        if os.path.exists(d) and os.path.getmtime(d) > os.path.getmtime(s) and "--force" not in sys.argv:
            print("skip", dst)
            continue
        im = Image.open(s)
        im.thumbnail((maxw, maxw * 2))
        if cut:
            im = cutout(im)
        im = film_look(im, seed=1930 + i)
        if dst.endswith(".jpg"):
            im.convert("RGB").save(d, quality=90)
        else:
            im.save(d, optimize=True)
        print("ok", dst, im.size)
    print("FALTANDO:", missing)


if __name__ == "__main__":
    main()
