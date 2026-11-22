"""Trata os assets do vídeo do Corinthians (public/corinthians/raw -> escudos/, fotos/).
Reaproveita recorte (rembg) e filtro único de process-assets.py."""
import importlib.util, os, shutil
from PIL import Image

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("pa", os.path.join(HERE, "process-assets.py"))
pa = importlib.util.module_from_spec(spec); spec.loader.exec_module(pa)
ROOT = os.path.join(HERE, "..", "public", "corinthians"); RAW = os.path.join(ROOT, "raw")
for d in ["escudos", "fotos"]: os.makedirs(os.path.join(ROOT, d), exist_ok=True)

CRESTS = {"escudo-corinthians-ge.svg": "corinthians.svg", "escudo-ponte-ge.svg": "ponte-preta.svg", "escudo-vasco-ge.svg": "vasco.svg",
          "escudo-chelsea-ge.png": "chelsea.png", "escudo-boca-ge.png": "boca.png", "logo-libertadores-spfc.png": "libertadores.png"}
PHOTOS = [  # (bruto, saída, recortar?, largura máx)
    ("ln_socrates_idolos_corinthians-scaled.jpg", "socrates-recorte.png", True, 1800),
    ("basilio-crop.jpg", "basilio-recorte.png", True, 600),
    ("ln_61aad7448e0ca.jpeg", "democracia-dia15vote.jpg", False, 970),
    ("ln_584720451d3c7.jpeg", "mundial-2000.jpg", False, 840),
    ("quadro-gol-1977-crop2.jpg", "quadro-gol-1977.jpg", False, 1100),
    ("arena-milton-jung.jpg", "arena.jpg", False, 1024),
]
for s, d in CRESTS.items():
    src = os.path.join(RAW, s); dst = os.path.join(ROOT, "escudos", d)
    (pa.trim_png(src, dst) if s.endswith(".png") else shutil.copy(src, dst)); print("ok", d)
for i, (s, d, cut, mw) in enumerate(PHOTOS):
    im = Image.open(os.path.join(RAW, s)); im.thumbnail((mw, mw * 2))
    if cut: im = pa.cutout(im)
    im = pa.film_look(im, seed=1910 + i); dst = os.path.join(ROOT, "fotos", d)
    (im.convert("RGB").save(dst, quality=90) if d.endswith(".jpg") else im.save(dst, optimize=True)); print("ok", d, im.size)
