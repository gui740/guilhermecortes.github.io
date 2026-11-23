"""Trata os assets do vídeo do Vasco (public/vasco/raw -> escudos/, fotos/).
Reaproveita recorte (rembg) e filtro único de process-assets.py."""
import importlib.util, os, shutil
from PIL import Image

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("pa", os.path.join(HERE, "process-assets.py"))
pa = importlib.util.module_from_spec(spec); spec.loader.exec_module(pa)
PUB = os.path.join(HERE, "..", "public")
ROOT = os.path.join(PUB, "vasco"); RAW = os.path.join(ROOT, "raw")
for d in ["escudos", "fotos"]: os.makedirs(os.path.join(ROOT, d), exist_ok=True)

CRESTS = {
    os.path.join(RAW, "vasco.svg"): "vasco.svg",
    os.path.join(RAW, "barcelona.svg"): "barcelona.svg",
    os.path.join(RAW, "botafogo.svg"): "botafogo.svg",
}
PHOTOS = [  # (bruto, saída, recortar?, largura máx)
    ("resposta1.jpg", "camisas-negras.jpg", False, 1280),
    ("expresso1.jpg", "expresso-da-vitoria.jpg", False, 480),
    ("sj1.jpg", "sao-januario.jpg", False, 1600),
    ("sj2.jpg", "libertadores-1998.jpg", False, 900),
    ("dinamite2.jpg", "dinamite-recorte.png", True, 1400),
    ("edmundo1.jpg", "edmundo-recorte.png", True, 760),
]
for s, d in CRESTS.items():
    shutil.copy(s, os.path.join(ROOT, "escudos", d)); print("ok", d)
for i, (s, d, cut, mw) in enumerate(PHOTOS):
    im = Image.open(os.path.join(RAW, s)); im.thumbnail((mw, mw * 2))
    if cut: im = pa.cutout(im)
    im = pa.film_look(im, seed=1898 + i); dst = os.path.join(ROOT, "fotos", d)
    (im.convert("RGB").save(dst, quality=90) if d.endswith(".jpg") else im.save(dst, optimize=True)); print("ok", d, im.size)
