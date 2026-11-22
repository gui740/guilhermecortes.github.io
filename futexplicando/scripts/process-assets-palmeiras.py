"""Trata os assets do vídeo do Palmeiras (public/palmeiras/raw -> escudos/, fotos/).
Reaproveita recorte (rembg) e filtro único (contraste + granulado) de process-assets.py."""
import importlib.util, os, shutil
from PIL import Image

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("pa", os.path.join(HERE, "process-assets.py"))
pa = importlib.util.module_from_spec(spec); spec.loader.exec_module(pa)

ROOT = os.path.join(HERE, "..", "public", "palmeiras")
RAW = os.path.join(ROOT, "raw")
for d in ["escudos", "fotos"]:
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)

CRESTS = {
    "escudo-palmeiras-ge.svg": "palmeiras-atual.svg",
    "escudo-palmeiras-1915-4.png": "palestra-1915.png",
    "escudo-palmeiras-1937-1.png": "palestra-1937.png",
    "escudo-palmeiras-1942.png": "palmeiras-1942.png",
    "escudo-palmeiras-1959.png": "palmeiras-1959.png",
    "escudo-saopaulo-ge.svg": "sao-paulo.svg",
    "escudo-santos-ge.svg": "santos.svg",
    "escudo-flamengo-ge.svg": "flamengo.svg",
    "escudo-estudiantes-ge.svg": "estudiantes.svg",
}
PHOTOS = [  # (bruto, saída, recortar?, largura máx)
    ("30102026_cg_palmeiras_7925_27.jpg", "abel-recorte.png", True, 1500),
    ("Ademir-da-Guia-colorida.jpeg", "ademir-recorte.png", True, 1280),
    ("marcos-libertadores-1999.jpg", "marcos-1999.jpg", False, 1000),
    ("arrancada-heroica-foto.jpg", "arrancada-1942.jpg", False, 900),
    ("allianz-aerea-2020.jpeg", "allianz-aerea.jpg", False, 2000),
]

for src, dst in CRESTS.items():
    s = os.path.join(RAW, src); d = os.path.join(ROOT, "escudos", dst)
    (pa.trim_png(s, d) if src.endswith(".png") else shutil.copy(s, d)); print("ok", dst)
for i, (src, dst, cut, maxw) in enumerate(PHOTOS):
    im = Image.open(os.path.join(RAW, src)); im.thumbnail((maxw, maxw * 2))
    if cut: im = pa.cutout(im)
    im = pa.film_look(im, seed=1914 + i)
    d = os.path.join(ROOT, "fotos", dst)
    (im.convert("RGB").save(d, quality=90) if dst.endswith(".jpg") else im.save(d, optimize=True)); print("ok", dst, im.size)
