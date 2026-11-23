"""Trata os assets do vídeo do Flamengo (public/flamengo/raw -> escudos/, fotos/).
Reaproveita recorte (rembg) e filtro único de process-assets.py."""
import importlib.util, os, shutil
from PIL import Image

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("pa", os.path.join(HERE, "process-assets.py"))
pa = importlib.util.module_from_spec(spec); spec.loader.exec_module(pa)
PUB = os.path.join(HERE, "..", "public")
ROOT = os.path.join(PUB, "flamengo"); RAW = os.path.join(ROOT, "raw")
for d in ["escudos", "fotos"]: os.makedirs(os.path.join(ROOT, d), exist_ok=True)

CRESTS = {
    os.path.join(RAW, "flamengo.svg"): "flamengo.svg",
    os.path.join(RAW, "river.svg"): "river.svg",
    os.path.join(RAW, "athletico.svg"): "athletico.svg",
    os.path.join(PUB, "copa-do-brasil/escudos/fluminense.svg"): "fluminense.svg",
    os.path.join(PUB, "sao-paulo/escudos/escudo-liverpool-ge.svg"): "liverpool.svg",
    os.path.join(PUB, "palmeiras/escudos/palmeiras-atual.svg"): "palmeiras.svg",
}
PHOTOS = [  # (bruto, saída, recortar?, largura máx)
    ("zico1981.jpg", "zico-recorte.png", True, 700),
    ("zico-sportlegends.jpg", "zico-retrato.jpg", False, 375),
    ("gab_b.jpg", "gabigol-taca-2019.jpg", False, 800),
    ("gab_d.jpg", "final-2019-river.jpg", False, 713),
    ("bi2019.jpg", "festa-2019.jpg", False, 1400),
    ("danilo2025.jpg", "danilo-recorte.png", True, 1400),
    ("danilo2025.jpg", "danilo-2025.jpg", False, 1400),
    ("maracana-haugen.jpg", "maracana-torcida.jpg", False, 1024),
    ("torcida-ivanx.jpg", "torcida-maracana.jpg", False, 1024),
]
for s, d in CRESTS.items():
    shutil.copy(s, os.path.join(ROOT, "escudos", d)); print("ok", d)
for i, (s, d, cut, mw) in enumerate(PHOTOS):
    im = Image.open(os.path.join(RAW, s)); im.thumbnail((mw, mw * 2))
    if cut: im = pa.cutout(im)
    im = pa.film_look(im, seed=1895 + i); dst = os.path.join(ROOT, "fotos", d)
    (im.convert("RGB").save(dst, quality=90) if d.endswith(".jpg") else im.save(dst, optimize=True)); print("ok", d, im.size)
