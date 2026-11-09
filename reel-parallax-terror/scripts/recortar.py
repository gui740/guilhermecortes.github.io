#!/usr/bin/env python3
"""Recortes estilo colagem de papel (adesivo cortado à tesoura) + camadas de fundo do parallax.

Para cada imagem de config/imagens.json:
  tipo "recorte": <nome>_recorte.png — personagem/objeto com:
        • máscara BiRefNet (alpha suave no cabelo); "modelo": "pessoa" | "objeto"
        • gradação de cor do filme + grão de impressão + leve vinco/dobra
        • borda de papel grossa com contorno de TESOURA (segmentos irregulares, não segue cada fio de cabelo)
        • textura de fibra/amarelado na borda e linha de sombra no corte
        • onde o personagem encosta na borda do frame (bustos), a base vira PAPEL RASGADO
     e <nome>_fundo.jpg (original desfocado para a camada distante)
  tipo "fundo": só <nome>_fundo.jpg     ·   tipo "foto": <nome>.jpg tratada (polaroides / impressos)

Máscara: 1) assets/raw/<filme>/<arquivo>_mask.png desenhado à mão (branco = manter), se existir
         2) rembg BiRefNet   3) OpenCV GrabCut
Uso: python3 scripts/recortar.py [filme] [nome ...]      Saída: assets/<filme>/
"""
import sys, json, pathlib
import numpy as np, cv2
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config" / "imagens.json").read_text())
LADO_MAX = 1000     # lado maior do PNG final
BORDA = 15          # espessura da borda de papel (px no PNG final => ~9-12 px na tela)
PROC_MAX = 1800     # resolução de trabalho

# gradação por filme: (saturação, multiplicadores RGB, contraste, levantamento de pretos)
GRADE = {
    "possum":    (0.78, (1.10, 1.03, 0.90), 1.18, 4),
    "calvaire":  (0.78, (0.98, 1.06, 1.02), 1.18, 4),
    "hagazussa": (0.72, (0.98, 1.03, 1.10), 1.16, 4),
}
PAPEL = np.array([242, 236, 222], np.float32)

_sess = {}
def mascara_rembg(img, modelo):
    try:
        from rembg import remove, new_session
    except ImportError:
        return None
    nome = {"pessoa": "birefnet-portrait", "objeto": "birefnet-general-lite"}[modelo]
    if nome not in _sess:
        _sess[nome] = new_session(nome)
    return np.array(remove(img, session=_sess[nome], only_mask=True))

def mascara_grabcut(img):
    a = np.array(img)[:, :, ::-1].copy(); h, w = a.shape[:2]
    m = np.zeros((h, w), np.uint8); bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
    cv2.grabCut(a, m, (int(w * .12), int(h * .05), int(w * .76), int(h * .93)), bg, fg, 5, cv2.GC_INIT_WITH_RECT)
    return np.where((m == 1) | (m == 3), 255, 0).astype(np.uint8)

def ruido(h, w, seed, escalas=((4, .5), (16, .3), (64, .2))):
    """ruído fractal barato (fibra de papel / manchas)"""
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32)
    for s, a in escalas:
        n = rng.standard_normal((h // s + 2, w // s + 2)).astype(np.float32)
        out += a * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    return out / (np.abs(out).max() + 1e-6)

def gradar(rgb, filme, seed):
    sat, mul, con, lift = GRADE.get(filme, GRADE["possum"])
    x = rgb.astype(np.float32)
    lum = x @ np.array([0.299, 0.587, 0.114], np.float32)
    x = lum[..., None] + (x - lum[..., None]) * sat
    x = (x - 128) * con + 128
    x = x * np.array(mul, np.float32)
    x = lift + x * (255 - lift) / 255
    x = x * 1.08 + 6  # um pouco mais de luz: clima menos pesado
    # grão de impressão + leve textura de papel por baixo da foto
    h, w = x.shape[:2]
    rng = np.random.default_rng(seed)
    x += rng.normal(0, 5, (h, w, 1)).astype(np.float32)
    x *= (1 + 0.035 * ruido(h, w, seed + 1))[..., None]
    return np.clip(x, 0, 255)

def linha_rasgada(n, base, amp, seed):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    y = base + amp * (0.5 * np.sin(t / (n / 3.1) + rng.uniform(0, 6)) + 0.3 * np.sin(t / 37 + rng.uniform(0, 6)))
    y += np.cumsum(rng.normal(0, 0.9, n)); y -= np.linspace(0, 1, n) * (y[-1] - y[0])
    y += rng.normal(0, amp * 0.05, n)  # fibras
    return y

def processar_recorte(img, alpha, filme, seed):
    W0, H0 = img.size
    rgb = np.array(img).astype(np.float32)
    a = alpha.astype(np.float32) / 255
    b = (a > 0.5).astype(np.uint8)
    # só os componentes grandes; fecha buracos
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, 8)
    if n > 1:
        maior = st[1:, cv2.CC_STAT_AREA].max()
        b = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 0.06 * maior]).astype(np.uint8)
    cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cheio = np.zeros_like(b); cv2.drawContours(cheio, cnts, -1, 1, -1)
    a = a * cv2.dilate(cheio, np.ones((5, 5), np.uint8)).astype(np.float32)

    # lados onde o personagem é cortado pelo frame => rasgo
    m = 4
    lados = {"baixo": cheio[-m:, :].mean(), "cima": cheio[:m, :].mean(), "esq": cheio[:, :m].mean(), "dir": cheio[:, -m:].mean()}
    rasgos = [k for k, v in lados.items() if v > 0.03]

    # recorta no bbox com margem e reduz para o tamanho final
    ys, xs = np.where(cheio > 0)
    pad = int(max(W0, H0) * 0.04)
    x0, y0, x1, y1 = max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, W0), min(ys.max() + pad, H0)
    rgb, a, cheio = rgb[y0:y1, x0:x1], a[y0:y1, x0:x1], cheio[y0:y1, x0:x1]
    toca = {"baixo": y1 >= H0, "cima": y0 <= 0, "esq": x0 <= 0, "dir": x1 >= W0}
    rasgos = [k for k in rasgos if toca[k]]
    esc = min(1.0, (LADO_MAX - 2 * (BORDA + 10)) / max(rgb.shape[:2]))
    if esc < 1:
        sz = (int(rgb.shape[1] * esc), int(rgb.shape[0] * esc))
        rgb = cv2.resize(rgb, sz, interpolation=cv2.INTER_AREA)
        a = cv2.resize(a, sz, interpolation=cv2.INTER_AREA)
        cheio = cv2.resize(cheio, sz, interpolation=cv2.INTER_NEAREST)
    P = BORDA + 10
    h, w = a.shape
    H, W = h + 2 * P, w + 2 * P
    A = np.zeros((H, W), np.float32); A[P:P + h, P:P + w] = a
    B = np.zeros((H, W), np.uint8); B[P:P + h, P:P + w] = cheio
    RGB = np.zeros((H, W, 3), np.float32); RGB[P:P + h, P:P + w] = rgb

    # rasgo da foto (um pouco pra dentro da borda do frame)
    rasgo_foto = np.ones((H, W), np.float32); rasgo_papel = np.ones((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    for i, lado in enumerate(rasgos):
        if lado in ("baixo", "cima"):
            base = (P + h - 8) if lado == "baixo" else (P + 8)
            lf = linha_rasgada(W, base - (10 if lado == "baixo" else -10), 9, seed + i)
            lp = lf + (BORDA * 0.75 if lado == "baixo" else -BORDA * 0.75) + np.random.default_rng(seed + 9 + i).normal(0, 1.0, W)
            if lado == "baixo":
                rasgo_foto *= (yy < lf[None, :]).astype(np.float32); rasgo_papel *= (yy < lp[None, :]).astype(np.float32)
            else:
                rasgo_foto *= (yy > lf[None, :]).astype(np.float32); rasgo_papel *= (yy > lp[None, :]).astype(np.float32)
        else:
            base = (P + w - 8) if lado == "dir" else (P + 8)
            lf = linha_rasgada(H, base - (10 if lado == "dir" else -10), 9, seed + 5 + i)
            lp = lf + (BORDA * 0.75 if lado == "dir" else -BORDA * 0.75) + np.random.default_rng(seed + 19 + i).normal(0, 1.0, H)
            if lado == "dir":
                rasgo_foto *= (xx < lf[:, None]).astype(np.float32); rasgo_papel *= (xx < lp[:, None]).astype(np.float32)
            else:
                rasgo_foto *= (xx > lf[:, None]).astype(np.float32); rasgo_papel *= (xx > lp[:, None]).astype(np.float32)
    rasgo_foto = cv2.GaussianBlur(rasgo_foto, (3, 3), 0); rasgo_papel = cv2.GaussianBlur(rasgo_papel, (3, 3), 0)
    A *= rasgo_foto

    # contorno de tesoura: fecha concavidades (cabelo, vãos), engorda, suaviza e simplifica em segmentos
    k = max(9, int(max(H, W) * 0.035)) | 1
    S = cv2.morphologyEx(B, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    S = cv2.dilate(S, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * BORDA + 1, 2 * BORDA + 1)))
    S = (cv2.GaussianBlur(S.astype(np.float32), (0, 0), 4) > 0.5).astype(np.uint8)
    up = 4
    cnts, _ = cv2.findContours(S, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    canvas = np.zeros((H * up, W * up), np.uint8)
    rng = np.random.default_rng(seed + 3)
    for c in cnts:
        c2 = cv2.approxPolyDP(c, 3.2, True).astype(np.float32)
        c2 += rng.normal(0, 0.7, c2.shape)  # mão humana
        cv2.fillPoly(canvas, [(c2 * up).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    papel_a = cv2.resize(canvas, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    papel_a *= rasgo_papel
    papel_a = np.maximum(papel_a, A)

    # textura do papel da borda: fibra + amarelado/sujeira perto do corte
    fib = ruido(H, W, seed + 4, ((2, .6), (8, .25), (40, .15)))
    dist = cv2.distanceTransform((papel_a > 0.5).astype(np.uint8), cv2.DIST_L2, 3)
    borda_sujeira = np.clip(1 - dist / 9, 0, 1)
    papel = PAPEL[None, None, :] * (1 + 0.035 * fib[..., None])
    papel -= (borda_sujeira[..., None] * np.array([14, 18, 30], np.float32))           # amarelado
    papel -= (np.clip(1 - dist / 2.2, 0, 1)[..., None] * 55)                            # linha de sombra do corte
    manchas = np.clip(ruido(H, W, seed + 5, ((60, 1.0),)), 0, 1)
    papel -= (manchas[..., None] * np.array([10, 14, 24], np.float32))

    # foto gradada
    foto = gradar(RGB, filme, seed)
    # leve sombra interna da foto sobre o papel (impressa e colada)
    sombra = cv2.GaussianBlur(A, (0, 0), 3) * (1 - A)
    papel *= (1 - 0.25 * sombra)[..., None]
    out = papel * (1 - A[..., None]) + foto * A[..., None]

    # vinco/dobra atravessando o recorte (luz + sombra), às vezes
    if rng.random() < 0.75:
        ang = rng.uniform(-0.9, 0.9) + (np.pi / 2 if rng.random() < 0.5 else 0)
        cx, cy = W * rng.uniform(.3, .7), H * rng.uniform(.3, .7)
        d = (xx - cx) * np.cos(ang) + (yy - cy) * np.sin(ang)
        vinco = np.exp(-(d / 1.6) ** 2) * 26 - np.exp(-((d - 3) / 2.5) ** 2) * 18
        out += vinco[..., None] * (0.6 + 0.4 * ruido(H, W, seed + 6, ((30, 1.0),)))[..., None]
    # desgaste: pontinhos claros
    sp = (rng.random((H, W)) > 0.99992) & (A < 0.5)  # só no papel
    out[sp] = out[sp] * 0.4 + 255 * 0.6

    res = np.dstack([np.clip(out, 0, 255), np.clip(papel_a * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(res, "RGBA"), rasgos

def foto(img, filme, seed, dest):
    im = img.convert("RGB"); im.thumbnail((1600, 1600), Image.LANCZOS)
    x = gradar(np.array(im), filme, seed)
    h, w = x.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
    vin = 1 - 0.28 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 2
    x *= vin[..., None]
    # riscos finos de foto velha
    rng = np.random.default_rng(seed)
    for _ in range(rng.integers(2, 6)):
        x0 = rng.integers(0, w); cv2.line(x, (int(x0), 0), (int(x0 + rng.integers(-40, 40)), h), (235, 230, 220), 1, cv2.LINE_AA)
    Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)).save(dest, quality=90)

def fundo(img, dest):
    im = img.convert("RGB")
    esc = min(1.0, 2200 / max(im.size))
    if esc < 1:
        im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    im.filter(ImageFilter.GaussianBlur(2.0)).save(dest, quality=88)

def processar(filme, nome, item):
    src = ROOT / "assets" / "raw" / filme / item["src"]
    out = ROOT / "assets" / filme; out.mkdir(parents=True, exist_ok=True)
    img = Image.open(src).convert("RGB"); img.load()
    seed = abs(hash(filme + nome)) % 10_000
    if item["tipo"] == "foto":
        foto(img, filme, seed, out / f"{nome}.jpg"); print("foto", filme, nome); return
    fundo(img, out / f"{nome}_fundo.jpg")
    if item["tipo"] == "fundo":
        print("fundo", filme, nome); return
    if max(img.size) > PROC_MAX:
        img.thumbnail((PROC_MAX, PROC_MAX), Image.LANCZOS)
    manual = src.with_name(src.stem + "_mask.png")
    if manual.exists():
        a = np.array(Image.open(manual).convert("L").resize(img.size)); metodo = "mask manual"
    else:
        a = mascara_rembg(img, item.get("modelo", "pessoa")); metodo = "birefnet-" + item.get("modelo", "pessoa")
        if a is None or (a > 128).mean() < 0.01:
            a = mascara_grabcut(img); metodo = "grabcut"
    res, rasgos = processar_recorte(img, a, filme, seed)
    res.save(out / f"{nome}_recorte.png", optimize=True)
    print(f"recorte {filme} {nome} [{metodo}] rasgo={rasgos} {res.size}")

if __name__ == "__main__":
    filmes = [sys.argv[1]] if len(sys.argv) > 1 else [k for k in CFG if not k.startswith("_")]
    for f in filmes:
        for nome, item in CFG[f].items():
            if len(sys.argv) > 2 and nome not in sys.argv[2:]:
                continue
            processar(f, nome, item)
