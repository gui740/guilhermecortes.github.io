"""Processa as imagens baixadas: recorte (rembg), P&B/sépia envelhecido, borda de papel recortado.
Uso: python3 tools/process_assets.py [chave ...]   (sem chaves = todas)
Saída: assets/cut/<key>.png e src/assets.json
"""
import json, sys, os
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, CUT = os.path.join(ROOT, "assets/raw"), os.path.join(ROOT, "assets/cut")
os.makedirs(CUT, exist_ok=True)
cfg = json.load(open(os.path.join(ROOT, "tools/assets_config.json")))
only = set(sys.argv[1:])
_session = None
def rembg_cut(im):
    global _session
    from rembg import remove, new_session
    if _session is None: _session = new_session("isnet-general-use")
    out = remove(im.convert("RGB"), session=_session, post_process_mask=True)
    a = np.array(out.split()[-1]).astype(np.float32)
    a = np.clip((a - 40) * 255 / 175, 0, 255)           # limpa semitransparências
    out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out
def tone(im, mode):
    if mode == "keep": return im
    a = im.split()[-1] if im.mode == "RGBA" else None
    g = ImageOps.grayscale(im.convert("RGB"))
    g = ImageOps.autocontrast(g, cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.12)
    if mode == "sepia":
        lut_r = [int(min(255, v * 1.07 + 10)) for v in range(256)]
        lut_g = [int(min(255, v * .95 + 6)) for v in range(256)]
        lut_b = [int(min(255, v * .78)) for v in range(256)]
        rgb = Image.merge("RGB", (g.point(lut_r), g.point(lut_g), g.point(lut_b)))
    else:  # bw levemente quente (foto antiga)
        rgb = Image.merge("RGB", (g.point(lambda v: min(255, v * 1.02 + 3)), g, g.point(lambda v: v * .95)))
    if a is not None: rgb.putalpha(a)
    return rgb
def sticker(im, px, seed=1):
    """borda irregular de papel branco em volta do recorte"""
    if px <= 0: return im
    pad = px * 3
    im = ImageOps.expand(im, border=pad, fill=(0, 0, 0, 0))
    a = im.split()[-1]
    big = a.filter(ImageFilter.MaxFilter(px * 2 + 1 if px * 2 + 1 <= 61 else 61))
    rng = np.random.default_rng(seed)
    n = rng.random((big.height // 8 + 2, big.width // 8 + 2)).astype(np.float32)
    n = np.array(Image.fromarray((n * 255).astype(np.uint8)).resize(big.size, Image.BILINEAR)).astype(np.float32) / 255
    b = np.array(big.filter(ImageFilter.GaussianBlur(px * .6))).astype(np.float32) / 255
    mask = (b + (n - .5) * .5) > .5
    paper = Image.new("RGBA", im.size, (239, 231, 212, 0))
    pa = np.zeros((im.height, im.width), np.uint8); pa[mask] = 255
    paper.putalpha(Image.fromarray(pa))
    paper.alpha_composite(im)
    return paper
def trim(im):
    bb = im.split()[-1].getbbox()
    return im.crop(bb) if bb else im
def circle(im):
    g = np.array(ImageOps.grayscale(im)); ys, xs = np.where(g > 40)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max(); s = max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    im = im.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2)).convert("RGBA")
    m = Image.new("L", im.size, 0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).ellipse((2, 2, im.width - 3, im.height - 3), fill=255)
    im.putalpha(m); return im
manifest_path = os.path.join(ROOT, "src/assets.json")
manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
for i, it in enumerate(cfg["items"]):
    k = it["key"]
    if only and k not in only: continue
    src = os.path.join(RAW, k + ".jpg")
    if not os.path.exists(src): print("falta", k); continue
    im = Image.open(src); im.load()
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    if "crop" in it:
        x0, y0, x1, y1 = it["crop"]; W, H = im.size
        im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    m = it["method"]
    if m == "rembg": im = trim(rembg_cut(im))
    elif m == "circle": im = circle(im.convert("RGB"))
    elif m == "texture":
        im = ImageOps.fit(im.convert("RGB"), (1080, 1920))
        g = np.array(ImageOps.grayscale(im)).astype(np.float32)
        g = (g - g.mean()) / (g.std() + 1e-6) * 14 + 214          # papel claro, pouco contraste
        g = np.clip(g, 0, 255).astype(np.uint8); gi = Image.fromarray(g)
        im = Image.merge("RGB", (gi.point(lambda v: min(255, v + 6)), gi.point(lambda v: min(255, v + 1)), gi.point(lambda v: v * .93)))
    elif m == "dark":   # silhueta escura (gravura/cartaz): fundo claro/colorido vira transparente
        rgb = np.array(im.convert("RGB")).astype(np.float32)
        lum = rgb.mean(axis=2); sat = rgb.max(axis=2) - rgb.min(axis=2)
        a = np.clip((150 - lum) * 4, 0, 255) * np.clip((90 - sat) / 40, 0, 1)
        im = im.convert("RGB"); im.putalpha(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.MedianFilter(3)))
        im = trim(im)
    if it.get("tone") != "paper": im = tone(im, it.get("tone", "bw"))
    if m in ("rembg", "dark"): im = trim(sticker(im.convert("RGBA"), it.get("outline", 0), seed=i + 1))
    w = it.get("width", 1000)
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    out = os.path.join(CUT, k + (".jpg" if m in ("card", "texture") else ".png"))
    if out.endswith(".jpg"): im.convert("RGB").save(out, quality=90)
    else: im.save(out, optimize=True)
    manifest[k] = os.path.relpath(out, ROOT)
    # variantes derivadas
    if k == "teodora_full":
        back = ImageOps.mirror(im)
        r, g, b, a = back.split()
        dark = Image.merge("RGB", (r, g, b)).point(lambda v: v * .42)
        dark = Image.merge("RGBA", (*Image.merge("RGB", (dark.split()[0], dark.split()[1], dark.split()[2].point(lambda v: min(255, v * 1.25)))).split(), a))
        p2 = os.path.join(CUT, "teodora_back.png"); dark.save(p2, optimize=True); manifest["teodora_back"] = os.path.relpath(p2, ROOT)
    if k == "gate_close":   # portão: fundo recortado + folha fechada (a foto real tem uma folha aberta)
        C = (0, 40, 1140, 1330)
        bgim = im.convert("RGB").crop(C); bgim.save(os.path.join(CUT, "gate_bg.jpg"), quality=90)
        leaf = im.convert("RGB").crop((290, 705, 505, 1330))
        patch = leaf.crop((20, 220, 73, 360)); leaf.paste(patch, (75, 220))   # cobre o aviso de papel na grade
        leaf.save(os.path.join(CUT, "gate_leaf.jpg"), quality=92)
        manifest["gate_bg"] = "assets/cut/gate_bg.jpg"; manifest["gate_leaf"] = "assets/cut/gate_leaf.jpg"
        manifest["_gate"] = {"w": C[2] - C[0], "h": C[3] - C[1], "door": [290, 665, 725, 1290], "leafW": 215}
    print("ok", k, im.size, flush=True)
json.dump(manifest, open(manifest_path, "w"), indent=1, ensure_ascii=False)
