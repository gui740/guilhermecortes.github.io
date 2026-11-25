"""YouTube Short v2: O TAMANHO REAL DOS PLANETAS (~58 s, 1080x1920, 30 fps, loop perfeito).

  NARR=out/narr_gemini python render.py times                -> momentos-chave
  NARR=out/narr_gemini python render.py preview 0 5 12.3     -> frames-chave em out/preview
  NARR=out/narr_gemini python render.py video                -> out/video_mudo.mp4
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import (W, H, FPS, CX, SAFE_R, YEL, WHITE, NAVY, PLANETS, IDX, XS, R_KM, RING_OUT, EARTH_D,
                    clamp, smoother, ease_out_cubic, ease_out_back, rich_text, paste, pop, rounded_panel,
                    planet_card, arrow_img, font, fmt_km, draw_body)
import plan as PL

P = PL.load()
S, EN = P["S"], P["E"]
DUR, NFRAMES, T_LOOP = P["DUR"], P["NFRAMES"], P["T_LOOP"]
E.DUR = DUR
RE = EARTH_D / 2
FRONT = np.array([0.25, 0.3, 0.92], np.float32) / np.linalg.norm([0.25, 0.3, 0.92])


def word_t(line, frag, which="t"):
    """instante de uma palavra dentro de uma fala"""
    frag = frag.lower()
    for w in P["words"]:
        if w["line"] == line and frag in w["w"].lower():
            return w["t"] + (w["d"] if which == "end" else 0.0)
    return (S[line] + EN[line]) / 2


# ---------------------------------------------------------------- momentos-chave
T_KM = S["km"]
T_REV = S["s109"] - 0.25                     # revelação do Sol (BOOM)
T_109A, T_109B = S["s109"] + 0.35, EN["s109"] - 0.05
T_FILL_A = S["encher"] + 0.55
T_FILL_B = EN["milhao"] + 0.25
T_AQUI = S["aqui"]
T_BET = word_t("betel", "betelgeuse") + 0.05
T_CTA = S["cta"]
NEI_POP = {"VÊNUS": S["viz"] + 0.15, "MARTE": S["viz"] + 0.30, "MERCÚRIO": S["viz"] + 0.45}

# Terras lado a lado nos gigantes: (planeta, início, fim, quantidade)
ROWS = [
    ("NETUNO", word_t("netuno", "quase"), word_t("netuno", "lado", "end"), 49244 / EARTH_D),
    ("URANO", word_t("urano", "quatro") - 0.5, word_t("urano", "terras", "end"), 50724 / EARTH_D),
    ("SATURNO", word_t("saturno", "nove") - 0.15, word_t("saturno", "terras", "end"), 116460 / EARTH_D),
    ("JÚPITER", word_t("jupiter", "onze") - 0.6, word_t("jupiter", "terras", "end"), 139820 / EARTH_D),
]
T_RINGS_A, T_RINGS_B = word_t("saturno", "anéis") - 0.1, EN["saturno"]
CARD_T = {"NETUNO": (S["netuno"], S["urano"] - 0.15), "URANO": (S["urano"], S["saturno"] - 0.15),
          "SATURNO": (S["saturno"], S["jupiter"] - 0.15), "JÚPITER": (S["jupiter"], S["mancha"] + 0.2)}

# ---------------------------------------------------------------- geometria
S_SUN = 880 / PLANETS[IDX["SOL"]][1]
SUN_C = (CX, 860.0)
X_SUN = XS[IDX["SOL"]]
X_JUP = XS[IDX["JÚPITER"]]
R_JUP = R_KM[IDX["JÚPITER"]]
ROW_SHIFT = X_SUN - X_JUP - R_JUP + 170 / S_SUN     # planetas deslizam para a frente do Sol
X_BET = XS[IDX["BETELGEUSE"]]
S_BET = 860 / PLANETS[IDX["BETELGEUSE"]][1]

# Júpiter gira de modo que a Grande Mancha fique de frente na cena dela
T_GRS = S["mancha"] + 0.8
E.ROT_OFF["JÚPITER"] = 0.18 / (2 * math.pi) - T_GRS * E.ROT_SPEED["JÚPITER"]
E.ROT_SPEED["TERRA"] = 1.0 / DUR              # 1 volta exata = loop perfeito
LAT_GRS = -22 * math.pi / 180


def row_dx(t):
    a = smoother((t - (T_REV - 1.1)) / 1.6)
    b = smoother((t - (T_BET + 0.5)) / 0.5)   # volta quando já é sub-pixel
    return ROW_SHIFT * a * (1 - b)


def grs_world(t):
    lon = -2 * math.pi * (t * E.ROT_SPEED["JÚPITER"] + E.ROT_OFF["JÚPITER"])
    X = math.cos(LAT_GRS) * math.sin(lon)
    Yd = -math.sin(LAT_GRS)
    return X_JUP + X * R_JUP, R_JUP * (1 - Yd), math.cos(lon)


# ---------------------------------------------------------------- câmera
def focus(name, d_px, cy=800.0, sx=CX, xw=None):
    i = IDX[name]
    s = d_px / PLANETS[i][1]
    x = XS[i] if xw is None else xw
    return s, x - (sx - CX) / s, cy + d_px / 2


def build_keys():
    K = []
    s0, x0, b0 = focus("TERRA", 640, cy=900)
    K.append((0.0, s0, x0, b0, "soft"))
    s0b, x0b, b0b = focus("TERRA", 590, cy=880)
    K.append((S["viz"], s0b, x0b, b0b, "soft"))
    left, right = XS[0] - R_KM[0], XS[3] + R_KM[3]
    s1 = 860 / (right - left)
    mid = (left + right) / 2
    for line, tgt, zf, sh in [("merc", XS[0], 1.16, 0.38), ("marte", XS[1], 1.08, 0.32), ("venus", XS[2], 1.0, 0.25)]:
        x = mid + (tgt - mid) * sh
        K.append((S[line] + 0.45, s1 * zf, x, 1000.0, "soft"))
    K.append((S["gigantes"] + 0.2, s1 * 0.97, mid + 2000, 1000.0, "soft"))
    for line, n, d in [("netuno", "NETUNO", 500), ("urano", "URANO", 470), ("saturno", "SATURNO", 300),
                       ("jupiter", "JÚPITER", 400)]:
        s, x, b = focus(n, d, 780)
        K.append((S[line] + 0.35, s, x, b, "soft"))
        if n == "SATURNO":
            s, x, b = focus("SATURNO", 285, 780)
            K.append((T_RINGS_A + 0.3, s, x, b, "soft"))
    s, x, b = focus("JÚPITER", 380, 780)
    K.append((EN["jupiter"] + 0.1, s, x, b, "soft"))
    # Grande Mancha Vermelha
    sg = 300 / 16000
    gx, gh, _ = grs_world(T_GRS)
    K.append((S["mancha"] + 0.9, sg, gx - (400 - CX) / sg + 4000, 760 + gh * sg, "soft"))
    sg2 = sg * 0.93
    K.append((EN["mancha"] + 0.25, sg2, gx - (400 - CX) / sg2 + 4000, 760 + gh * sg2, "soft"))
    s, x, b = focus("JÚPITER", 300, 760)
    K.append((S["sol"] + 0.7, s, x, b, "soft"))
    # Sol inteiro: centro (480, 860), 880 px
    bs = SUN_C[1] + 440
    K.append((T_REV, S_SUN, X_SUN, bs, "in", X_SUN))
    K.append((T_AQUI, S_SUN, X_SUN, bs, "lin"))           # parada; o zoom fino é pós-processado
    # "você está aqui": aproxima da Terra (já na frente do Sol)
    sa = S_SUN * 2.3
    xe = ROW_SHIFT
    K.append((T_AQUI + 1.1, sa, xe - (300 - CX) / sa, 1180 + RE * sa, "soft"))
    sa2 = sa * 0.96
    K.append((S["estrela"] + 0.15, sa2, xe - (310 - CX) / sa2, 1185 + RE * sa2, "soft"))
    # Betelgeuse
    bb = 840 + 430
    K.append((T_BET, S_BET, X_BET - (540 - CX) / S_BET, bb, "in", X_SUN))
    sb2 = S_BET * 0.94
    K.append((T_LOOP, sb2, X_BET - (548 - CX) / sb2, bb + 8, "lin"))
    K.append((DUR, s0, x0, b0, "loop", 0.0))
    return K


KEYS = build_keys()


def camera(t):
    t = min(max(t, 0.0), DUR)
    for k in range(len(KEYS) - 1):
        ta, sa, xa, ba = KEYS[k][:4]
        tb, sb, xb, bb, mode = KEYS[k + 1][:5]
        anchor = KEYS[k + 1][5] if len(KEYS[k + 1]) > 5 else None
        if ta <= t <= tb:
            tau = clamp((t - ta) / max(tb - ta, 1e-6))
            if mode == "soft":
                u = 0.8 * smoother(tau) + 0.2 * tau
            elif mode == "in":
                u = 0.3 * tau + 0.7 * tau ** 2.4
            elif mode == "lin":
                u = tau
            else:
                u = smoother(tau)
            s = math.exp(math.log(sa) + (math.log(sb) - math.log(sa)) * u)
            uo = u if mode == "in" else smoother(tau)
            if anchor is not None:      # um ponto do mundo desliza em linha reta na tela
                pa = CX + (anchor - xa) * sa
                pb = CX + (anchor - xb) * sb
                x = anchor - (pa + (pb - pa) * uo - CX) / s
            else:
                x = xb - (xb - xa) * sa * (1 - uo) / s
            b = ba + (bb - ba) * (u if mode == "in" else smoother(tau))
            return s, x, b
    return KEYS[0][1:4]


def post_zoom(t):
    if T_REV <= t < T_AQUI + 0.6:
        return 1 + 0.045 * smoother((t - T_REV) / (T_AQUI + 0.6 - T_REV))
    return 1.0


def shake(t):
    ox = oy = 0.0
    for t0, amp in [(T_REV, 36), (T_BET, 26)]:
        dt = t - t0
        if 0 <= dt < 1.0:
            a = amp * math.exp(-dt * 5)
            ox += a * math.sin(dt * 71) * math.cos(dt * 13)
            oy += a * math.sin(dt * 53 + 1.3)
    return ox, oy


def flash(t):
    f = 0.0
    for t0, peak in [(T_REV, 1.0), (T_BET, 0.75)]:
        if t0 - 0.03 <= t < t0 + 0.5:
            f = max(f, peak * (1.0 if t < t0 + 0.05 else 1 - smoother((t - t0 - 0.05) / 0.45)))
    return f


# ---------------------------------------------------------------- Terras enchendo o Sol
FILL = None
SUN_RPX = 440.0


def build_fill():
    global FILL
    R = SUN_RPX
    de = 2 * R / 109
    rs = de / 2
    spr_n = int(math.ceil(de)) + 3
    pad = 8
    big = np.zeros((spr_n + 2 * pad, spr_n + 2 * pad, 3), np.float32)
    draw_body(big, "TERRA", pad + spr_n / 2, pad + spr_n / 2, rs, 0.0, light=FRONT)
    can = np.clip(big[pad:pad + spr_n, pad:pad + spr_n] * np.array([1.5, 1.75, 2.1], np.float32) + 0.03, 0, 1)
    yy, xx = np.mgrid[0:spr_n, 0:spr_n] + 0.5
    al = np.clip(rs - np.sqrt((xx - spr_n / 2) ** 2 + (yy - spr_n / 2) ** 2) + 0.5, 0, 1).astype(np.float32)
    size = int(2 * R + spr_n + 4)
    off = size / 2
    rgb = np.zeros((size, size, 3), np.float32)
    alpha = np.zeros((size, size), np.float32)
    rev = np.full((size, size), 9.0, np.float32)
    rng = np.random.default_rng(4)
    pts = []
    dy = de * 0.866
    j = 0
    y = -R + rs
    while y <= R - rs + 1e-6:
        x = -R + (rs if j % 2 == 0 else de)
        while x <= R - rs + 1e-6:
            if x * x + y * y <= (R - rs * 0.6) ** 2:
                pts.append((x, y))
            x += de
        y += dy
        j += 1
    pts = np.array(pts)
    # enche de baixo para cima, superfície ondulada
    r = (1 - (pts[:, 1] / R + 1) / 2) * 0.88 + 0.12 * rng.random(len(pts)) + 0.03 * np.sin(pts[:, 0] / 40)
    r = (r - r.min()) / (r.max() - r.min())
    for (x, y), rv in zip(pts, r):
        ix = int(round(off + x - spr_n / 2))
        iy = int(round(off + y - spr_n / 2))
        a_reg = alpha[iy:iy + spr_n, ix:ix + spr_n]
        m = al > a_reg
        rgb[iy:iy + spr_n, ix:ix + spr_n][m] = can[m]
        a_reg[m] = al[m]
        rev[iy:iy + spr_n, ix:ix + spr_n][m & (al > 0.05)] = rv
    fly = []
    for k in range(0, len(pts), 16):
        ang = rng.uniform(-math.pi, math.pi)
        fly.append((pts[k][0], pts[k][1], r[k], ang, rng.uniform(0.35, 0.65), rng.uniform(-1, 1)))
    FILL = dict(rgb=rgb, alpha=alpha, rev=rev, off=off, size=size, fly=fly, n=len(pts), rs=rs,
                spr=can, spr_a=al, spr_n=spr_n)
    # tempo de chegada de cada voadora
    FILL["fly_t"] = [time_of_progress(f[2]) for f in fly]


def fill_progress(t):
    if t < T_FILL_A:
        return 0.0
    u = clamp((t - T_FILL_A) / (T_FILL_B - T_FILL_A))
    return 0.5 - 0.5 * math.cos(math.pi * u ** 0.85)


def time_of_progress(p):
    lo, hi = T_FILL_A, T_FILL_B
    for _ in range(30):
        m = (lo + hi) / 2
        if fill_progress(m) < p:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def draw_fill(canvas, t, sun_cx, sun_cy):
    if t < T_FILL_A - 0.8 or t > T_AQUI + 0.7:
        return
    F = FILL
    p = fill_progress(t)
    ga = 1.0 if t < T_AQUI else 1 - smoother((t - T_AQUI) / 0.6)
    if p > 0 and ga > 0:
        a = F["alpha"] * np.clip((p - F["rev"]) / 0.015, 0, 1) * ga
        size, off = F["size"], F["off"]
        x0, y0 = int(round(sun_cx - off)), int(round(sun_cy - off))
        xa, ya = max(0, x0), max(0, y0)
        xb, yb = min(W, x0 + size), min(H, y0 + size)
        if xa < xb and ya < yb:
            sub = a[ya - y0:yb - y0, xa - x0:xb - x0][..., None]
            reg = canvas[ya:yb, xa:xb]
            reg[:] = reg * (1 - sub) + F["rgb"][ya - y0:yb - y0, xa - x0:xb - x0] * sub
    R = SUN_RPX
    for (px, py, rv, ang, fd, bend), tr in zip(F["fly"], F["fly_t"]):
        ts = tr - fd
        if ts <= t < tr:
            u = (t - ts) / fd
            e = u * u * (3 - 2 * u)
            sx, sy = math.cos(ang) * R * 1.9, math.sin(ang) * R * 1.9 - 200
            cxp, cyp = (sx + px) / 2 + bend * 260, (sy + py) / 2 - 180
            bx = (1 - e) ** 2 * sx + 2 * (1 - e) * e * cxp + e * e * px
            by = (1 - e) ** 2 * sy + 2 * (1 - e) * e * cyp + e * e * py
            draw_body(canvas, "TERRA", sun_cx + bx, sun_cy + by, F["rs"] * (3.2 - 2.2 * e), t, light=FRONT, gain=1.7)


# ---------------------------------------------------------------- mundo
def nei_scale(name, t):
    a = NEI_POP[name]
    if t < a:
        return 0.0
    if t > T_LOOP + 0.3:
        return 1 - smoother((t - T_LOOP - 0.3) / 0.6)
    x = (t - a) / 0.35
    return 1.0 if x >= 1 else max(0.0, ease_out_back(x, 2.0))


def row_items(name, ta, tb, count, cx, R, re):
    n_full = int(math.floor(count))
    n_tot = n_full + (1 if count - n_full > 0.05 else 0)
    items = []
    for k in range(n_tot):
        tk = ta + (tb - ta) * (k / max(1, n_tot - 1)) ** 0.9
        items.append((cx - R + re * (2 * k + 1), tk, cx + R if k == n_full else None))
    if name == "SATURNO":
        nside = int((R * RING_OUT - R) / (2 * re))
        for j in range(nside):
            tk = T_RINGS_A + (T_RINGS_B - T_RINGS_A) * (j / max(1, nside - 1))
            items.append((cx - R - re * (2 * j + 1), tk, None))
            items.append((cx - R + count * 2 * re + re * (2 * j + 1), tk + 0.05, None))
    return items


def earth_rows(canvas, t, pos, s):
    for name, ta, tb, count in ROWS:
        a_end = CARD_T[name][1] + 0.1
        if t < ta or t > a_end or name not in pos:
            continue
        cx, cy, R = pos[name]
        fade = clamp((a_end - t) / 0.3)
        for x, tk, clip in row_items(name, ta, tb, count, cx, R, RE * s):
            if t >= tk:
                sc = ease_out_back(clamp((t - tk) / 0.28), 2.2) * fade
                if sc > 0.02:
                    draw_body(canvas, "TERRA", x, cy, RE * s, t, sc, clip_x1=clip)


def t109(k):
    return T_109A + (T_109B - T_109A) * (k / 108) ** 0.6


def sun_row(canvas, t, sun_cx, sun_cy):
    if t < T_109A or t > T_FILL_A + 0.6:
        return
    de = 2 * SUN_RPX / 109
    fade = 1 - smoother((t - T_FILL_A) / 0.6)
    for k in range(109):
        tk = t109(k)
        if t < tk:
            break
        u = clamp((t - tk) / 0.22)
        a = clamp(u * 3) * fade
        lift = (1 - ease_out_back(u, 2.5)) * 30
        n = FILL["spr_n"]
        ix = int(round(sun_cx - SUN_RPX + de * (k + 0.5) - n / 2))
        iy = int(round(sun_cy - n / 2 - lift))
        if 0 <= ix and ix + n <= W and 0 <= iy and iy + n <= H and a > 0:
            al3 = (FILL["spr_a"] * a)[..., None]
            reg = canvas[iy:iy + n, ix:ix + n]
            reg[:] = reg * (1 - al3) + FILL["spr"] * al3


def count_109(t):
    return sum(1 for k in range(109) if t >= t109(k))


def world_layer(t):
    s, xc, B = camera(t)
    canvas = E.render_bg(t, s)
    shx, shy = shake(t)
    rdx = row_dx(t)
    pos = {}
    for i in [IDX["BETELGEUSE"], IDX["SOL"]] + list(range(8)):
        name, d, _ = PLANETS[i]
        R = d / 2 * s
        cx = CX + (XS[i] + (rdx if i < 8 else 0.0) - xc) * s + shx
        cy = B - R + shy
        pos[name] = (cx, cy, R)
        ext = R * (RING_OUT if name == "SATURNO" else (2.6 if i >= 8 else 1.2)) + 2
        if cx + ext < 0 or cx - ext > W or cy + ext < 0 or cy - ext > H:
            continue
        sc = nei_scale(name, t) if name in NEI_POP else 1.0
        if sc > 0:
            draw_body(canvas, name, cx, B - R * sc + shy, R, t, sc)
    earth_rows(canvas, t, pos, s)
    if S["mancha"] + 0.3 <= t < EN["mancha"] + 0.9:
        gx, gh, cl = grs_world(t)
        ex = CX + (gx + 8200 * cl + RE + 2600 - xc) * s + shx
        ey = B - gh * s + shy
        tk = word_t("mancha", "maior") - 0.35
        if t >= tk:
            sc = ease_out_back(clamp((t - tk) / 0.35), 2.0) * clamp((EN["mancha"] + 0.9 - t) / 0.3)
            draw_body(canvas, "TERRA", ex, ey, RE * s, t, sc)
        pos["_grs"] = (CX + (gx - xc) * s + shx, ey, 8000 * s * cl)
        pos["_grs_earth"] = (ex, ey, RE * s)
    sx_, sy_, _ = pos["SOL"]
    sun_row(canvas, t, sx_, sy_)
    draw_fill(canvas, t, sx_, sy_)
    canvas *= E.VIGNETTE
    f = flash(t)
    if f > 0:
        canvas = canvas * (1 - f) + f
    return np.clip(canvas, 0, 1), pos


# ---------------------------------------------------------------- legendas
CHUNKS = []


def build_chunks():
    CHUNKS.clear()
    cur, line = [], None
    for w in P["words"]:
        if w["line"] == "hook":      # o título já mostra; deixa o frame 0 igual ao último
            continue
        if cur and (w["line"] != line or len(cur) >= 3 or sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > 16):
            CHUNKS.append(cur); cur = []
        cur.append(w); line = w["line"]
    if cur:
        CHUNKS.append(cur)


def caption(frame, t):
    for ci, ch in enumerate(CHUNKS):
        a = ch[0]["t"] - 0.05
        b = ch[-1]["t"] + ch[-1]["d"] + 0.15
        if ci + 1 < len(CHUNKS) and CHUNKS[ci + 1][0]["line"] == ch[0]["line"]:
            b = min(b, CHUNKS[ci + 1][0]["t"] - 0.05)
        if a <= t < b:
            parts = []
            for w in ch:
                txt = w["w"].upper().strip(",.!?:;…")
                active = w["t"] - 0.03 <= t < w["t"] + w["d"] + 0.03 or (w is ch[-1] and t >= w["t"])
                parts.append(f"*{txt}*" if active else txt)
            img = rich_text(" ".join(parts), 62, maxw=900)
            sc = 0.82 + 0.18 * ease_out_back(clamp((t - a) / 0.16), 2.0)
            paste(frame, img, CX, 1520, sc, 1.0)
            return


# ---------------------------------------------------------------- interface
TOP_Y = 235


def top(frame, t, text, a, b, size=84, grow=0.0, y=TOP_Y):
    if a <= t < b:
        paste(frame, rich_text(text, size, maxw=860), CX, y, pop(t, a) * (1 + grow * (t - a)), clamp((b - t) / 0.12))


def pill(text, size=40, fg=NAVY, bg=YEL):
    key = ("pill", text, size)
    if key not in _cache:
        f = font("mont", size)
        tl = int(f.getlength(text))
        img = rounded_panel(tl + 44, size + 30, bg + (255,), (size + 30) // 2, outline=(0, 0, 0, 255), ow=4)
        ImageDraw.Draw(img).text((22, 12), text, font=f, fill=fg)
        _cache[key] = img
    return _cache[key]


def big_counter(n, suffix="x", size=210):
    return rich_text(f"{n:,}".replace(",", ".") + suffix, size, "anton", color=YEL, stroke=12)


def ui_layer(frame, t, pos):
    d = ImageDraw.Draw(frame)
    # 1) gancho (visível no frame 0) + medida da Terra
    if t < S["viz"]:
        sc = 1 + 0.025 * math.sin(t * 5)
        paste(frame, rich_text("A TERRA PARECE *GRANDE?*", 92, maxw=860), CX, TOP_Y, sc, clamp((S["viz"] - t) / 0.12))
    if t >= T_LOOP + 0.75:
        u = (t - T_LOOP - 0.75) / 0.45
        sc = (0.55 + 0.45 * ease_out_back(clamp(u), 2.0)) if u < 1 else 1.0
        paste(frame, rich_text("A TERRA PARECE *GRANDE?*", 92, maxw=860), CX, TOP_Y, sc, clamp(u * 3))
    if T_KM <= t < S["viz"] + 0.2:
        ex, ey, er = pos["TERRA"]
        u = ease_out_cubic((t - T_KM) / 1.2)
        al = clamp((S["viz"] + 0.2 - t) / 0.2)
        L = er * u
        col = (255, 214, 60, int(255 * al))
        d.line((ex - L, ey, ex + L, ey), fill=(0, 0, 0, int(200 * al)), width=12)
        d.line((ex - L, ey, ex + L, ey), fill=col, width=6)
        for sx in (ex - L, ex + L):
            d.line((sx, ey - 22, sx, ey + 22), fill=col, width=6)
        km = rich_text(fmt_km(12742 * u), 120, "anton", color=YEL, stroke=10)
        paste(frame, km, CX, ey + er + 95, pop(t, T_KM), al)
    # 2) vizinhos
    top(frame, t, "PERTO DOS *VIZINHOS...*", S["viz"], S["gigantes"])
    labels = [("MERCÚRIO", "38%", S["merc"]), ("MARTE", "53%", S["marte"]), ("VÊNUS", "95%", S["venus"]),
              ("TERRA", "100%", S["viz"] + 0.6)]
    for nm, pct, ta in labels:
        if ta <= t < S["gigantes"] + 0.1:
            cx, cy, R = pos[nm]
            al = clamp((S["gigantes"] + 0.1 - t) / 0.15)
            sc = pop(t, ta)
            lab = rich_text(nm, 34, maxw=400)
            lx = max(cx, lab.width / 2 + 8)
            paste(frame, lab, lx, cy + R + 40 + (36 if nm == "MERCÚRIO" else 0), sc, al)
            paste(frame, pill(pct, 34), cx, cy - R - 46, sc, al)
    if S["venus"] + 0.6 <= t < S["gigantes"] + 0.1:
        cx, cy, R = pos["VÊNUS"]
        paste(frame, rich_text("*QUASE GÊMEA!*", 46, maxw=500), cx + 40, cy - R - 120,
              pop(t, S["venus"] + 0.6), clamp((S["gigantes"] + 0.1 - t) / 0.15))
    # 3) gigantes
    top(frame, t, "MAS AÍ CHEGAM OS *GIGANTES*", S["gigantes"], S["sol"] - 0.1, size=88)
    for nm, (a, b) in CARD_T.items():
        if a <= t < b:
            i = IDX[nm]
            label = PLANETS[i][2]
            if nm == "SATURNO" and t >= T_RINGS_A:
                label = "21x A TERRA (COM ANÉIS)"
            card = planet_card(nm, PLANETS[i][1], label, (t - a) / 0.9)
            e = ease_out_back(clamp((t - a) / 0.3), 1.6)
            al = min(clamp((t - a) / 0.15), clamp((b - t) / 0.18))
            paste(frame, card, CX, 1225 + (1 - e) * 100, 0.76 + 0.08 * e, al)
    for name, ta, tb, count in ROWS:
        a_end = CARD_T[name][1]
        if ta <= t < a_end:
            k = count * clamp((t - ta) / max(tb - ta, 0.1))
            if name == "SATURNO" and t >= T_RINGS_A:
                k = count + (21 - count) * clamp((t - T_RINGS_A) / max(T_RINGS_B - T_RINGS_A, 0.1))
            txt = (f"{k:.1f}".replace(".", ",").replace(",0", "")) + " *TERRAS*"
            paste(frame, rich_text(txt, 60), CX, 470, pop(t, ta), clamp((a_end - t) / 0.15))
    if S["mancha"] + 0.5 <= t < EN["mancha"] + 0.8 and "_grs" in pos:
        al = clamp((EN["mancha"] + 0.8 - t) / 0.2)
        gx, gy, gr = pos["_grs"]
        ex, ey, er = pos["_grs_earth"]
        paste(frame, rich_text("MANCHA VERMELHA", 42, maxw=500), max(gx, 190), gy + gr * 0.6 + 70, pop(t, S["mancha"] + 0.5), al)
        tk = word_t("mancha", "maior") - 0.2
        if t >= tk:
            paste(frame, rich_text("*TERRA*", 44, maxw=400), ex, ey + er + 50, pop(t, tk), al)
            paste(frame, pill("MAIOR QUE A TERRA!", 48), CX, 470, pop(t, tk + 0.15), al)
    # 4) Sol
    top(frame, t, "AGORA OLHA O *SOL...*", S["sol"], T_REV - 0.02, size=92, grow=0.025, y=300)
    if T_REV <= t < T_109A:
        paste(frame, rich_text("O *SOL*", 130, maxw=860), CX, 260, pop(t, T_REV, 0.3), clamp((T_109A - t) / 0.1))
    if T_109A <= t < T_FILL_A - 0.3:
        n = count_109(t)
        al = clamp((T_FILL_A - 0.3 - t) / 0.2)
        bump = 1.06 if n == 109 and t < T_109B + 0.25 else 1.0
        paste(frame, big_counter(max(n, 1)), CX, 210, pop(t, T_109A) * bump, al)
        paste(frame, rich_text("TERRAS DE *PONTA A PONTA*", 52, maxw=860), CX, 345, pop(t, T_109A + 0.2), al)
    if S["encher"] <= t < T_FILL_B + 0.15:
        top(frame, t, "E PRA *ENCHER* POR DENTRO?", S["encher"], T_FILL_A + 0.3, size=74, y=250)
        if t >= T_FILL_A + 0.1:
            n = int(round(1_300_000 * fill_progress(t) / 100)) * 100 if t < T_FILL_B else 1_300_000
            paste(frame, big_counter(n, "", 170), CX, 215, pop(t, T_FILL_A + 0.1), 1.0)
            paste(frame, rich_text("TERRAS", 56, maxw=860), CX, 335, pop(t, T_FILL_A + 0.2), 1.0)
    if T_FILL_B + 0.15 <= t < T_AQUI + 0.3:
        al = clamp((T_AQUI + 0.3 - t) / 0.2)
        e = ease_out_back(clamp((t - T_FILL_B - 0.15) / 0.35), 1.8)
        paste(frame, _milhao_panel(), CX, 255, 0.8 + 0.2 * e, al)
    # 5) você está aqui
    if T_AQUI + 0.5 <= t < S["estrela"] + 0.35:
        ex, ey, er = pos["TERRA"]
        al = clamp((S["estrela"] + 0.35 - t) / 0.25)
        bob = 10 * math.sin((t - T_AQUI) * 7)
        sc = pop(t, T_AQUI + 0.5, 0.3)
        ar = arrow_img(200)
        paste(frame, ar, ex, ey - er - 16 - ar.height / 2 + bob, sc, al)
        lab = rich_text("*VOCÊ ESTÁ AQUI*", 76, maxw=700)
        lx = clamp(ex + 60, lab.width / 2 + 30, SAFE_R - lab.width / 2 - 10)
        paste(frame, lab, lx, ey - er - 300 + bob * 0.5, sc, al)
        ph = (t - T_AQUI) * 1.6 % 1
        rr = er + 12 + 16 * ph
        d.ellipse((ex - rr, ey - rr, ex + rr, ey + rr), outline=(255, 214, 60, int(255 * al * (1 - ph))), width=5)
    # 6) Betelgeuse
    top(frame, t, "O SOL É UMA ESTRELA *COMUM*", S["estrela"] + 0.1, T_BET - 0.02, size=80)
    if T_BET <= t < T_LOOP + 0.15:
        al = clamp((T_LOOP + 0.15 - t) / 0.15)
        paste(frame, rich_text("*BETELGEUSE*", 104, maxw=880), CX, 205, pop(t, T_BET + 0.05), al)
        paste(frame, pill("~760x MAIOR QUE O SOL", 46), CX, 330, pop(t, T_BET + 0.3), al)
        sx_, sy_, _ = pos["SOL"]
        ta = T_BET + 0.6
        if t >= ta:
            sc = pop(t, ta)
            ar = arrow_img(150)
            paste(frame, ar, sx_, sy_ - 22 - ar.height / 2, sc, al)
            paste(frame, rich_text("*SOL*", 60, maxw=300), max(sx_, 80), sy_ - 22 - ar.height - 40, sc, al)
    # 7) CTA
    if T_CTA <= t < T_LOOP + 0.15:
        al = clamp((T_LOOP + 0.15 - t) / 0.15)
        e = ease_out_back(clamp((t - T_CTA) / 0.35), 1.8)
        paste(frame, _cta_panel(), CX, 1150, (0.8 + 0.2 * e) * (1 + 0.015 * math.sin(t * 6)), al)
    caption(frame, t)


_cache = {}


def _milhao_panel():
    if "m" not in _cache:
        a = rich_text("DENTRO DELE CABEM", 56, maxw=820)
        b = rich_text("1,3 MILHÃO", 170, "anton", color=YEL, stroke=12)
        c = rich_text("DE TERRAS", 76, maxw=820)
        pw, ph = 820, 34 + a.height + b.height + c.height
        img = rounded_panel(pw, ph, (8, 16, 46, 215), 44, outline=(255, 214, 60, 255), ow=6)
        y = 16
        for im in (a, b, c):
            img.alpha_composite(im, ((pw - im.width) // 2, y))
            y += im.height
        _cache["m"] = img
    return _cache["m"]


def _cta_panel():
    if "c" not in _cache:
        a = rich_text("QUAL A PRÓXIMA *COMPARAÇÃO?*", 70, maxw=780)
        b = pill("COMENTA AÍ!", 50)
        pw, ph = 840, a.height + b.height + 70
        img = rounded_panel(pw, ph, (8, 16, 46, 215), 44, outline=(255, 214, 60, 255), ow=6)
        img.alpha_composite(a, ((pw - a.width) // 2, 22))
        img.alpha_composite(b, ((pw - b.width) // 2, 30 + a.height))
        _cache["c"] = img
    return _cache["c"]


# ---------------------------------------------------------------- eventos de som (usados por audio.py)
def sound_events():
    ev = {"whoosh": [], "pop": [], "tick": [], "blip": [], "riser": [], "boom": [], "swarm": [], "rwhoosh": []}
    for k in range(1, len(KEYS) - 1):
        ta, sa = KEYS[k - 1][0], KEYS[k - 1][1]
        tb, sb = KEYS[k][0], KEYS[k][1]
        if abs(math.log(sb / sa)) > 0.25 and KEYS[k][4] == "soft":
            ev["whoosh"].append((ta + tb) / 2)
    ev["whoosh"].append(T_AQUI + 0.55)
    for t0 in NEI_POP.values():
        ev["pop"].append((t0, 0))
    for name, ta, tb, count in ROWS:
        n_tot = int(math.ceil(count - 0.05))
        for k in range(n_tot):
            ev["pop"].append((ta + (tb - ta) * (k / max(1, n_tot - 1)) ** 0.9, k))
    for j in range(5):
        ev["pop"].append((T_RINGS_A + (T_RINGS_B - T_RINGS_A) * j / 4, 9 + j))
    ev["blip"] = [a for a, b in CARD_T.values()] + [S["merc"], S["marte"], S["venus"], word_t("mancha", "maior") - 0.2,
                                                     T_AQUI + 0.5, T_FILL_B + 0.15, T_CTA, T_BET + 0.6]
    tc = T_KM
    while tc < T_KM + 1.2:
        ev["tick"].append((tc, 0.5)); tc += 0.06 + 0.05 * (tc - T_KM)
    for k in range(109):
        ev["tick"].append((t109(k), 0.4 + k / 160))
    tc = T_FILL_A + 0.1
    while tc < T_FILL_B:
        ev["tick"].append((tc, 0.3)); tc += 0.045
    ev["riser"] = [(S["sol"], T_REV), (S["estrela"] + 0.1, T_BET)]
    ev["boom"] = [(T_REV, 1.0), (T_BET, 0.8)]
    ev["swarm"] = [(T_FILL_A - 0.5, T_FILL_B)]
    ev["rwhoosh"] = [T_LOOP]
    ev["sections"] = dict(riser1=(S["sol"], T_REV), calm=(T_REV, T_109A), riser2=(S["estrela"] + 0.1, T_BET),
                          loop=(T_LOOP, DUR))
    return ev


# ---------------------------------------------------------------- render
def init():
    E.init()
    build_fill()
    build_chunks()


def render_frame(f):
    t = f / FPS
    canvas, pos = world_layer(t)
    img = Image.fromarray((canvas * 255 + 0.5).astype(np.uint8))
    z = post_zoom(t)
    if z > 1.0001:
        cx, cy = pos["SOL"][0], pos["SOL"][1]
        x0, y0 = cx - cx / z, cy - cy / z
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + W / z, y0 + H / z))
        for k, (x, y, r) in list(pos.items()):
            pos[k] = ((x - x0) * z, (y - y0) * z, r * z)
    img = img.convert("RGBA")
    ui_layer(img, t, pos)
    return img.convert("RGB")


def render_range(args):
    a, b, path = args
    init()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(render_frame(f).tobytes())
        if f % 60 == 0:
            print(f"frame {f}/{NFRAMES}", flush=True)
    p.stdin.close()
    p.wait()
    return path


def main():
    out = E.OUT
    os.makedirs(out, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if cmd == "times":
        items = {**{f"S.{a}": b for a, b in S.items()}, "T_REV": T_REV, "T_BET": T_BET, "T_FILL_A": T_FILL_A,
                 "T_FILL_B": T_FILL_B, "T_LOOP": T_LOOP, "DUR": DUR}
        for k, v in sorted(items.items(), key=lambda x: x[1]):
            print(f"{v:7.2f}  {k}")
    elif cmd == "preview":
        init()
        pd = os.path.join(out, os.environ.get("PDIR", "preview"))
        os.makedirs(pd, exist_ok=True)
        for ts in sys.argv[2:]:
            f = int(round(float(ts) * FPS))
            im = render_frame(f)
            if os.environ.get("GUIDES"):
                d = ImageDraw.Draw(im)
                d.line((SAFE_R, 0, SAFE_R, H), fill=(255, 0, 0), width=2)
                d.line((0, E.SAFE_B, W, E.SAFE_B), fill=(255, 0, 0), width=2)
            im.save(os.path.join(pd, f"f{f:04d}.png"))
            print("ok", f, flush=True)
    elif cmd == "video":
        from multiprocessing import Pool
        E.init()
        nw = int(os.environ.get("WORKERS", os.cpu_count() or 4))
        step = math.ceil(NFRAMES / (nw * 3))
        jobs = [(i, min(NFRAMES, i + step), os.path.join(out, f"seg{k:02d}.mp4"))
                for k, i in enumerate(range(0, NFRAMES, step))]
        with Pool(nw) as pool:
            segs = pool.map(render_range, jobs, chunksize=1)
        lst = os.path.join(out, "segs.txt")
        open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                        os.path.join(out, "video_mudo.mp4")], check=True)
        print("video ok")


if __name__ == "__main__":
    main()
