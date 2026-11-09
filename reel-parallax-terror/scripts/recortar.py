#!/usr/bin/env python3
"""Recorta personagens/objetos e prepara as camadas do parallax.

Para cada imagem de config/imagens.json:
  tipo "recorte": <nome>_recorte.png (fundo transparente + borda branca grossa tipo adesivo)
                  e <nome>_fundo.png (original levemente desfocado, para a camada distante)
  tipo "fundo":   só <nome>_fundo.png
  tipo "foto":    <nome>.jpg redimensionada (polaroides/stills)

Ordem de tentativa para a máscara:
  1. assets/raw/<filme>/<arquivo>_mask.png desenhado à mão (branco = manter), se existir
  2. rembg (isnet-general-use / u2net)
  3. OpenCV GrabCut com retângulo central
Saída em assets/<filme>/.  Uso: python3 scripts/recortar.py [filme] [nome]
"""
import sys, json, pathlib
import numpy as np, cv2
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config" / "imagens.json").read_text())
BORDA = 12          # px da borda branca (recortes aparecem a ~70-100% do tamanho => 8–12 px na tela)
LADO_MAX = 900      # lado maior dos recortes
FUNDO_MAX = 2200    # lado maior dos fundos

_sess = None
def mascara_rembg(img):
    global _sess
    try:
        from rembg import remove, new_session
    except ImportError:
        return None
    if _sess is None:
        _sess = new_session("isnet-general-use")
    out = remove(img, session=_sess, post_process_mask=True)
    return np.array(out)[:, :, 3]

def mascara_grabcut(img):
    a = np.array(img.convert("RGB"))[:, :, ::-1].copy()
    h, w = a.shape[:2]
    m = np.zeros((h, w), np.uint8)
    rect = (int(w * .12), int(h * .05), int(w * .76), int(h * .93))
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(a, m, rect, bg, fg, 5, cv2.GC_INIT_WITH_RECT)
    return np.where((m == 1) | (m == 3), 255, 0).astype(np.uint8)

def limpar(alpha):
    """mantém só os componentes grandes e suaviza o contorno (corte de tesoura)."""
    b = (alpha > 128).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, 8)
    if n > 1:
        maior = st[1:, cv2.CC_STAT_AREA].max()
        keep = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 0.08 * maior]
        b = np.isin(lab, keep).astype(np.uint8)
    # fecha buracos
    cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cheio = np.zeros_like(b); cv2.drawContours(cheio, cnts, -1, 1, -1)
    return cheio

def adesivo(img, m):
    """aplica máscara, recorta no bbox e adiciona a borda branca (dilatação do alpha)."""
    rgba = img.convert("RGBA")
    ys, xs = np.where(m > 0)
    if len(xs) == 0:
        return None
    pad = 40
    x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
    x1, y1 = min(xs.max() + pad, m.shape[1]), min(ys.max() + pad, m.shape[0])
    rgba = rgba.crop((x0, y0, x1, y1)); mm = m[y0:y1, x0:x1]
    esc = min(1.0, LADO_MAX / max(rgba.size))
    if esc < 1:
        rgba = rgba.resize((int(rgba.width * esc), int(rgba.height * esc)), Image.LANCZOS)
        mm = cv2.resize(mm, rgba.size, interpolation=cv2.INTER_NEAREST)
    # contorno levemente simplificado = cara de recorte à tesoura
    cnts, _ = cv2.findContours(mm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    tes = np.zeros_like(mm)
    for c in cnts:
        cv2.drawContours(tes, [cv2.approxPolyDP(c, 2.5, True)], -1, 1, -1)
    # margem extra para a borda caber
    P = BORDA + 6
    W, H = rgba.width + 2 * P, rgba.height + 2 * P
    alpha = np.zeros((H, W), np.uint8); alpha[P:P + mm.shape[0], P:P + mm.shape[1]] = tes * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * BORDA + 1, 2 * BORDA + 1))
    borda = cv2.dilate(alpha, k)
    borda = cv2.GaussianBlur(borda, (3, 3), 0)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    branco = Image.new("RGBA", (W, H), (246, 242, 232, 255))   # branco papel
    out.paste(branco, (0, 0), Image.fromarray(borda))
    pessoa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pessoa.paste(rgba, (P, P))
    pa = np.array(pessoa); pa[:, :, 3] = cv2.GaussianBlur(alpha, (3, 3), 0)
    out.alpha_composite(Image.fromarray(pa))
    return out

def fundo(img, dest):
    im = img.convert("RGB")
    esc = min(1.0, FUNDO_MAX / max(im.size))
    if esc < 1:
        im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    im.filter(ImageFilter.GaussianBlur(2.2)).save(dest, quality=88)

def processar(filme, nome, item):
    src = ROOT / "assets" / "raw" / filme / item["src"]
    out = ROOT / "assets" / filme; out.mkdir(parents=True, exist_ok=True)
    img = Image.open(src); img.load()
    if item["tipo"] == "foto":
        im = img.convert("RGB"); im.thumbnail((1600, 1600), Image.LANCZOS)
        im.save(out / f"{nome}.jpg", quality=90); print("foto", filme, nome); return
    fundo(img, out / f"{nome}_fundo.jpg")
    if item["tipo"] == "fundo":
        print("fundo", filme, nome); return
    manual = src.with_name(src.stem + "_mask.png")
    if manual.exists():
        a = np.array(Image.open(manual).convert("L").resize(img.size)); metodo = "mask manual"
    else:
        a = mascara_rembg(img.convert("RGB")); metodo = "rembg"
        if a is None or (a > 128).mean() < 0.01:
            a = mascara_grabcut(img); metodo = "grabcut"
    m = limpar(a)
    cobertura = m.mean()
    res = adesivo(img, m)
    if res is None:
        print("FALHOU", filme, nome); return
    res.save(out / f"{nome}_recorte.png", optimize=True)
    print(f"recorte {filme} {nome} [{metodo}] cobertura={cobertura:.2f}")

if __name__ == "__main__":
    filmes = [sys.argv[1]] if len(sys.argv) > 1 else [k for k in CFG if not k.startswith("_")]
    for f in filmes:
        for nome, item in CFG[f].items():
            if len(sys.argv) > 2 and nome not in sys.argv[2:]:
                continue
            processar(f, nome, item)
