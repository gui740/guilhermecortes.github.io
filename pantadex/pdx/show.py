# -*- coding: utf-8 -*-
"""Linha do tempo: cenas, botões, narração e efeitos — e o quadro (tela + estado do aparelho) em cada instante."""
import os, math
import soundfile as sf
from .common import *
from .script import ANIMALS, NARRATION
from . import world, screens

def ndur(key):
    return sf.info(os.path.join(ROOT, "assets", "narration", key + ".wav")).duration

ROUTES = [[(3, 7), (18, 7), (18, 5), (21, 5)], [(21, 5), (21, 8), (25, 8)], [(25, 8), (19, 8), (19, 10)]]

class Show:
    def __init__(s):
        s.scenes = []; s.narr = []; s.sfx = []; s.btn = []; s.music = []
        s.t = 0.0
        s._build()
        s.total = s.t

    # ---- construção
    def add(s, kind, dur, **kw):
        sc = dict(kind=kind, t0=s.t, t1=s.t + dur, **kw); s.scenes.append(sc); s.t += dur; return sc
    def press(s, name, t, dur=0.16):
        s.btn.append((name, t, t + dur)); s.sfx.append((t, "click", None))

    def world_frame(s, i, lt, sc):
        route = ROUTES[i]; L = world.route_len(route)
        f = clamp((lt - sc["w0"]) / sc["wdur"])
        x, y, dr, fin = world.route_state(route, f * L)
        moving = 0 < f < 1
        ex = lt - sc["excl"] if lt >= sc["excl"] else 0
        im = world.render(sc["t0"] + lt, x, y, dr, moving, excl=max(ex, 0.001) if lt >= sc["excl"] else 0, walk_dist=f * L)
        return im, (dr if moving else None)

    def _build(s):
        # BOOT
        b = s.add("boot", 4.75)
        s.press("START", 0.25, 0.25); s.sfx += [(0.5, "power", None), (0.7, "logo", None), (2.55, "chord", None)]
        for k in range(21): s.sfx.append((2.9 + k * 0.9 / 21, "blip", None))
        s.narr.append(("boot", 2.5)); s.press("START", 4.62)
        s.sfx.append((4.62, "confirm", None))
        for i, a in enumerate(ANIMALS):
            # MUNDO
            wdur = 6.6 if i == 0 else 2.3
            w0 = 0.5
            excl = w0 + wdur + 0.15
            wl = excl + 0.55
            t_tr = s.t
            wsc = dict(kind="world", i=i, w0=w0 - 0.5 if False else w0, wdur=wdur, excl=excl)
            # transição de entrada (da cena anterior para o mundo)
            prev = s.scenes[-1]
            tr = s.add("trans", 0.5, a=prev, b=None, flash=False)
            wsc.update(t0=s.t - 0.5, t1=s.t - 0.5 + wl); wsc["w0"] = w0
            s.scenes.append(wsc); tr["b"] = wsc; tr["b_lt"] = 0.0; tr["a_lt"] = prev["t1"] - prev["t0"] - 0.001
            s.t = wsc["t1"]
            s.music.append(("world", wsc["t0"], wsc["t0"] + excl))
            if i == 0: s.narr.append(("world", wsc["t0"] + 0.9))
            te = wsc["t0"] + excl
            s.sfx.append((te, "excl", None)); s.narr.append((f"scan{i + 1}", te + 0.15))
            s.press("A", te + 0.42)
            # transição com flash em faixas -> escaneamento
            sdur = 2.6 if i == 0 else 1.7
            ssc = dict(kind="scan", i=i)
            tr2 = s.add("trans", 0.75, a=wsc, b=ssc, flash=True, a_lt=wl - 0.001, b_lt=0.0)
            s.sfx.append((tr2["t0"], "flash", None))
            ssc.update(t0=s.t, t1=s.t + sdur); s.scenes.append(ssc); s.t += sdur
            s.sfx.append((ssc["t0"], "scan", sdur)); s.sfx.append((ssc["t0"] + sdur * 0.93, "ident", None))
            # FICHA
            f0 = s.t
            nm = f"a{i + 1}_name"
            tname = 0.45
            s.sfx.append((f0, "reveal", None)); s.sfx.append((f0 + 0.05, "cry", a["key"]))
            s.narr.append((nm, f0 + tname))
            ps = tname + ndur(nm) + 0.35
            pages = []
            for j, txt in enumerate(a["pages"]):
                d = ndur(f"a{i + 1}_p{j + 1}")
                pages.append((ps, d)); s.narr.append((f"a{i + 1}_p{j + 1}", f0 + ps))
                nb = len(txt) // 2
                for k in range(nb): s.sfx.append((f0 + ps + k * d / nb, "blip", None))
                if j < len(a["pages"]) - 1:
                    s.press("A", f0 + ps + d + 0.2); ps = ps + d + 0.45
                else: ps = ps + d
            selo = ps + 0.25
            s.sfx.append((f0 + selo, "stamp", None))
            fend = selo + 1.45
            s.press("B", f0 + fend - 0.2)
            for k in range(3):
                for q in range(a["stats"][k][1]):
                    s.sfx.append((f0 + 0.9 + k * 0.7 + q * 0.06, "tick", k * 3 + q))
            for r in range(7): s.sfx.append((f0 + 0.2 + r * 0.1, "row", r))
            s.add("ficha", fend, i=i, pages=pages, selo=selo)
            s.music.append(("ficha", f0 + 0.3, f0 + fend))
        # ENCERRAMENTO
        prev = s.scenes[-1]
        esc = dict(kind="end")
        s.add("trans", 0.5, a=prev, b=esc, flash=False, a_lt=prev["t1"] - prev["t0"] - 0.001, b_lt=0.0)
        e0 = s.t
        esc.update(t0=e0, t1=e0 + 8.0); s.scenes.append(esc); s.t += 8.0
        for k in range(3): s.sfx.append((e0 + 0.4 + k * 0.5, "row", 3)); s.sfx.append((e0 + 0.65 + k * 0.5, "tick", 12 + k * 2))
        s.sfx.append((e0 + 2.1, "confirm", None))
        s.narr.append(("end", e0 + 0.5))
        s.press("START", e0 + 3.2); s.sfx.append((e0 + 3.3, "save", None)); s.sfx.append((e0 + 4.5, "saved", None))
        s.press("START", e0 + 7.0); s.sfx.append((e0 + 7.1, "off", None))
        s.music.append(("end", e0 + 0.1, e0 + 7.0))
        s.scenes.sort(key=lambda c: c["t0"])

    # ---- consulta
    def fstate(s, sc, lt):
        st = dict(page=-1, chars=0, done=False, bars=[0, 0, 0], selo=None, rows=int(clamp((lt - 0.2) / 0.1, 0, 9)))
        a = ANIMALS[sc["i"]]
        for j, (ps, d) in enumerate(sc["pages"]):
            if lt >= ps:
                n = len(a["pages"][j])
                st["page"] = j; st["chars"] = int(clamp((lt - ps) / max(d - 0.15, 0.1)) * n + 0.999); st["done"] = lt >= ps + d
        st["bars"] = [clamp((lt - 0.9 - k * 0.7) / (0.06 * a["stats"][k][1])) for k in range(3)]
        if lt >= sc["selo"]: st["selo"] = lt - sc["selo"]
        return st

    def render_scene(s, sc, lt, t):
        """devolve (imagem 240x160, hud parcial)"""
        k = sc["kind"]
        hud = dict(power=True, signal=1, scan=0.0, rec=False, battery=3, buttons=set())
        if k == "boot":
            hud.update(power=lt > 0.5, signal=1 if lt > 3 else 0, scan=clamp(1 - (lt - 0.5) / 0.5) if lt > 0.5 else 0)
            return screens.boot(lt), hud
        if k == "world":
            im, dr = s.world_frame(sc["i"], lt, sc)
            if dr: hud["buttons"].add(dr)
            if lt >= sc["excl"]: hud.update(signal=3, scan=1.0 if int(lt * 12) % 2 else 0.3)
            if sc["i"] == 0 and 0.3 < lt < 4.2:     # placa de localização
                d = draw(im); yy = -18 + int(ease((lt - 0.3) / 0.3) * 22) - int(ease((lt - 3.8) / 0.3) * 22)
                screens.box(d, 4, yy, 122, yy + 15, fill=CREAM, border=DKGREEN)
                text(d, 10, yy + 4, "PANTANAL - MT", F8, DKGREEN)
            return im, hud
        if k == "scan":
            p = lt / (sc["t1"] - sc["t0"])
            hud.update(signal=3, scan=0.55 + 0.45 * math.sin(lt * 2 * math.pi * 3), rec=int(lt * 4) % 2 == 0)
            return screens.scan(sc["i"], p, lt), hud
        if k == "ficha":
            st = s.fstate(sc, lt)
            im = screens.ficha(sc["i"], lt, st)
            hud.update(signal=3, scan=0.3, rec=True)
            if lt < 0.15: im = screens.white(im, 1 - lt / 0.15); hud["scan"] = 1.0
            if st["selo"] is not None and st["selo"] < 0.2:
                o = Image.new("RGB", (W, H), BLACK); o.paste(im, ((2, -1, 1, 0)[int(st["selo"] * 20) % 4], (1, 2, -1, 0)[int(st["selo"] * 20) % 4])); im = o
                hud["scan"] = 1.0
            return im, hud
        if k == "end":
            hud.update(signal=2, battery=2, power=lt < 7.5, rec=3.3 <= lt < 4.5 and int(lt * 6) % 2 == 0)
            return screens.end(lt), hud

    def frame(s, t):
        sc = None
        for c in s.scenes:
            if c["t0"] <= t < c["t1"] and (sc is None or c["kind"] == "trans"): sc = c
        if sc is None: sc = s.scenes[-1]
        lt = t - sc["t0"]
        if sc["kind"] == "trans":
            p = lt / (sc["t1"] - sc["t0"])
            A, hud = s.render_scene(sc["a"], sc["a_lt"], t)
            B, hud2 = s.render_scene(sc["b"], sc["b_lt"], t)
            if sc["flash"]:
                if p < 0.25:
                    im = screens.white(A, 1.0 if int(p * 16) % 2 == 0 else 0.0)
                else: im = screens.stripes(A, B, (p - 0.25) / 0.75)
                hud["scan"] = 1.0 if int(p * 16) % 2 == 0 else 0.2
            else:
                im = screens.stripes(A, B, p)
                if p > 0.5: hud = hud2
            hud["buttons"] = set()
        else:
            im, hud = s.render_scene(sc, lt, t)
        for name, b0, b1 in s.btn:
            if b0 <= t < b1: hud["buttons"].add(name)
        return im, hud

    def scene_times(s):
        return [(c["kind"], c.get("i"), round(c["t0"], 2), round(c["t1"], 2)) for c in s.scenes]
