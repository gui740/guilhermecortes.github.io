"""Tratamento visual dos recortes: P&B alto contraste, granulado, retícula (halftone),
borda alfa erodida + feather, borda branca de adesivo (filmes), duotone amarelo (destaques),
molduras de polaroid para stills. Saída em public/ (servido pelo Remotion)."""
import glob, os, json, sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
PUB = os.path.join(ROOT, "public")
YEL = np.array([0xF2, 0xE6, 0x3A], float)
OFF = np.array([0xED, 0xED, 0xED], float)
CHAR = np.array([0x1C, 0x1C, 0x1C], float)
rng = np.random.default_rng(7)


def clean_alpha(a, erode=2, feather=1.2):
    im = Image.fromarray(a)
    im = im.point(lambda v: 0 if v < 40 else (255 if v > 215 else v))  # mata semitransparência de halo
    if erode:
        im = im.filter(ImageFilter.MinFilter(erode * 2 + 1))
    im = im.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(im)


def halftone_gray(g, cell=7, angle=45, mix=0.42, grain=16, contrast=1.0):
    """g: float 0..1 grayscale. retorna 0..1 com retícula visível + granulado."""
    h, w = g.shape
    # contraste alto (curva S) + autolevels
    lo, hi = np.percentile(g, 2), np.percentile(g, 98.5)
    g = np.clip((g - lo) / max(1e-3, hi - lo), 0, 1)
    g = np.clip(0.5 + (g - 0.5) * (1.35 * contrast), 0, 1)
    g = g * g * (3 - 2 * g)
    # retícula: pontos pretos cujo raio cresce com a escuridão
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    t = np.deg2rad(angle)
    u = (xx * np.cos(t) + yy * np.sin(t)) / cell
    v = (-xx * np.sin(t) + yy * np.cos(t)) / cell
    du, dv = u - np.round(u), v - np.round(v)
    d = np.sqrt(du * du + dv * dv)  # 0 no centro, ~0.707 no canto
    r = np.sqrt(np.clip(1 - g, 0, 1)) * 0.62
    dots = np.clip((d - r) / 0.06 + 0.5, 0, 1)  # 1 = papel, 0 = ponto (antialias)
    out = g * (1 - mix) + (g * dots) * mix
    out = out + rng.normal(0, grain / 255.0, out.shape)
    return np.clip(out, 0, 1)


def to_rgb(gray, duo=None):
    if duo is None:
        lo, hi = CHAR * 0.25, np.array([245, 245, 245], float)
    else:
        lo, hi = CHAR * 0.25, duo
    return (lo[None, None] + gray[..., None] * (hi - lo)[None, None]).astype(np.uint8)


def treat_cutout(src, dst, maxs=900, duo=None, sticker=0, cell=7, erode=2, contrast=1.0, crop=True, gamma=1.0):
    im = Image.open(src).convert("RGBA")
    if crop:
        bb = im.getchannel("A").point(lambda v: 255 if v > 30 else 0).getbbox()
        im = im.crop(bb)
    im.thumbnail((maxs, maxs), Image.LANCZOS)
    a = np.asarray(im)
    alpha = clean_alpha(a[..., 3], erode=erode)
    g = np.asarray(ImageOps.grayscale(im.convert("RGB"))).astype(float) / 255
    g = g ** gamma
    gray = halftone_gray(g, cell=cell, contrast=contrast)
    rgb = to_rgb(gray, duo)
    out = np.dstack([rgb, alpha])
    o = Image.fromarray(out, "RGBA")
    if sticker:
        pad = sticker + 4
        big = Image.new("RGBA", (o.width + 2 * pad, o.height + 2 * pad), (0, 0, 0, 0))
        big.paste(o, (pad, pad), o)
        A = big.getchannel("A").point(lambda v: 255 if v > 90 else 0)
        A = A.filter(ImageFilter.MaxFilter(sticker * 2 + 1)).filter(ImageFilter.GaussianBlur(1.0))
        white = Image.new("RGBA", big.size, (237, 237, 237, 0))
        white.putalpha(A)
        white.alpha_composite(big)
        o = white
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    o.save(dst, optimize=True)
    return o.size


def polaroid(src, dst, crop=None, size=700, frame=OFF, cell=6):
    im = Image.open(src).convert("RGB")
    W, H = im.size
    if crop:
        im = im.crop((int(crop[0] * W), int(crop[1] * H), int(crop[2] * W), int(crop[3] * H)))
    # recorte quadrado central
    s = min(im.size)
    l = (im.width - s) // 2
    t = (im.height - s) // 2
    im = im.crop((l, t, l + s, t + s)).resize((size, size), Image.LANCZOS)
    g = np.asarray(ImageOps.grayscale(im)).astype(float) / 255
    rgb = to_rgb(halftone_gray(g, cell=cell, mix=0.38))
    b = int(size * 0.06)
    P = Image.new("RGBA", (size + 2 * b, size + b + int(size * 0.22)), tuple(int(c) for c in frame) + (255,))
    # leve sujeira no papel
    paper = np.asarray(P).astype(float)
    paper[..., :3] -= rng.normal(0, 4, paper[..., :3].shape)
    P = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8), "RGBA")
    P.paste(Image.fromarray(rgb), (b, b))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    P.save(dst, optimize=True)
    return P.size


def first(pattern):
    m = sorted(glob.glob(os.path.join(RAW, pattern)))
    if not m:
        raise SystemExit("faltou " + pattern)
    return m[0]


if __name__ == "__main__":
    manifest = {"kit": {}, "film": {}, "logos": {}}
    # ---- kit do cenário
    KIT = ("k_VHS_2 k_VHS_3 k_carnival_4 k_carnival_5 k_chain_1 k_chain_2 k_doll_4 k_gas_1 k_hammer_1 "
           "k_knife_2 k_knife_5 k_porcelai_2 k_porcelai_3 k_porcelai_4 k_saw_1 k_scissors_0 k_typewrit_2 "
           "r2_cassette_0 r2_cassette_4 r2_hanging_3 r2_hanging_4 r2_hanging_5 r2_kerosene_0 r2_kitchen_1 "
           "r2_kitchen_3 r2_padlock_3 r2_plaster_2 r2_plaster_3 r2_plaster_4 r2_polaroid_0 r2_screwdri_4 "
           "r2_teddy_0 r2_wooden_2").split()
    YELLOW = {"k_hammer_1", "r2_kerosene_0", "k_saw_1", "r2_cassette_0", "k_VHS_2"}
    for k in KIT:
        dst = os.path.join(PUB, "kit", k + ".png")
        sz = treat_cutout(os.path.join(RAW, "cut", k + ".png"), dst, maxs=760,
                          duo=YEL if k in YELLOW else None, cell=6)
        manifest["kit"][k] = {"w": sz[0], "h": sz[1], "yellow": k in YELLOW}
    # ---- assassinos (borda branca de adesivo)
    KILL = {"f1": ("killers/k1_mountainman_b.png", 1.15, 0.8), "f2": ("killers/k2_drill_b.png", 1.1, 0.62),
            "f3": ("killers/k3_full.png", 1.0, 1.0)}
    for f, (p, c, gm) in KILL.items():
        sz = treat_cutout(os.path.join(RAW, p), os.path.join(PUB, "film", f + "_killer.png"),
                          maxs=1300, sticker=9, cell=8, erode=2, contrast=c, gamma=gm)
        manifest["film"][f + "_killer"] = {"w": sz[0], "h": sz[1]}
    # ---- polaroids (stills)
    STILLS = {
        "f1": ["f1/poster_6X0Twn*", "f1/backdrop_2nP1xy*", "f1/backdrop_jzzCTR*", "f1/backdrop_l3xjbQ*",
               "f1/backdrop_99xMo0*", "f1/backdrop_w7EfId*"],
        "f2": ["f2/poster_laWfaJ*", "f2/backdrop_byiUU6*", "f2/backdrop_rO4pMP*", "f2/backdrop_iIvsKy*",
               "f2/poster_2bTOzr*", "f2/poster_5vL6gY*"],
        "f3": ["f3/backdrop_hPF3SP*", "f3/backdrop_mZ8lvI*", "f3/backdrop_96Q04*", "f3/backdrop_cYGB6*",
               "f3/backdrop_3WjO42*", "f3/backdrop_cPgxau*"],
    }
    CROPS = {"f1/poster_6X0Twn*": (0, 0.25, 1, 1), "f2/poster_laWfaJ*": (0, 0.45, 1, 1),
             "f2/poster_5vL6gY*": (0, 0, 1, 0.55), "f3/backdrop_hPF3SP*": (0.45, 0, 1, 1),
             "f2/backdrop_iIvsKy*": (0.55, 0, 0.98, 1), "f2/poster_2bTOzr*": (0.2, 0.05, 1, 0.62)}
    for f, lst in STILLS.items():
        for i, pat in enumerate(lst):
            sz = polaroid(first(pat), os.path.join(PUB, "film", f"{f}_pol{i}.png"), crop=CROPS.get(pat))
            manifest["film"][f"{f}_pol{i}"] = {"w": sz[0], "h": sz[1], "src": os.path.basename(first(pat))}
    # ---- logos brancos (upscale suave do HBO Max)
    for name in ["hbomax", "primevideo", "looke"]:
        im = Image.open(os.path.join(RAW, "logos", name + "_white.png")).convert("RGBA")
        if im.width < 800:
            s = 1000 / im.width
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
            A = np.asarray(im.getchannel("A")).astype(float) / 255
            A = np.clip((A - 0.5) * 3 + 0.5, 0, 1)
            im.putalpha(Image.fromarray((A * 255).astype(np.uint8)))
        os.makedirs(os.path.join(PUB, "logos"), exist_ok=True)
        im.save(os.path.join(PUB, "logos", name + ".png"))
        manifest["logos"][name] = {"w": im.width, "h": im.height}
    json.dump(manifest, open(os.path.join(ROOT, "src", "manifest.json"), "w"), indent=1)
    print("ok", len(manifest["kit"]), len(manifest["film"]))
