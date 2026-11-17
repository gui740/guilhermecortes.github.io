"""Prepara os clipes de arquivo a partir de cortes.json.

modo "crt": detecta trocas de plano, acha o rosto de Hastings em cada plano, reenquadra com o rosto
na faixa central 9:16 e aplica o tratamento de TV falhada (P&B, grão, scanlines, curvatura, vinheta).
modo "cor": material da própria Netflix, só corta e converte para 30 fps, sem filtro.

Uso: python3 prep_arquivo.py <dir_midia_fontes> <dir_saida> [ID ...]
Arquivos-fonte esperados em <dir_midia_fontes>: ted_1080.mp4, blitz_1080.mp4, house_1080.mp4, fu2016_720.mp4
"""
import json, os, subprocess, sys
import numpy as np
import cv2

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = {"ted": "ted_1080.mp4", "blitz": "blitz_1080.mp4", "house": "house_1080.mp4", "fu": "fu2016_720.mp4"}
W, H, FPS = 1920, 1080, 30
# scanlines e barra de rolagem ficam no Remotion (CRTOverlay), para o render não ficar lento
CRT = ("format=yuv420p,hue=s=0,eq=contrast=1.45:brightness=0.05:gamma=1.12,noise=alls=22:allf=t+u,"
       "format=rgb24,lenscorrection=k1=0.06:k2=0.02,rgbashift=rh=-3:bh=3,vignette=PI/4.2,format=yuv420p")

FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
PROF = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")


def frames(path, t0, t1, fps=4, w=960):
    h = int(w * 9 / 16)
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0}", "-to", f"{t1}", "-i", path,
                        "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True, check=True).stdout
    n = len(p) // (w * h)
    return np.frombuffer(p[:n * w * h], np.uint8).reshape(n, h, w), w / 1920.0


def faces(g):
    out = []
    for c, flip in ((FACE, False), (PROF, False), (PROF, True)):
        img = cv2.flip(g, 1) if flip else g
        for (x, y, w, h) in c.detectMultiScale(img, 1.1, 5, minSize=(24, 24)):
            if flip:
                x = g.shape[1] - x - w
            out.append((x + w / 2, y + h / 2, h))
    return out


def plan(path, t0, t1, lado):
    fr, k = frames(path, t0, t1)
    # trocas de plano por diferença de histograma
    cuts = [0]
    hists = [cv2.calcHist([f], [0], None, [32], [0, 256]).flatten() / f.size for f in fr]
    for i in range(1, len(fr)):
        if np.abs(hists[i] - hists[i - 1]).sum() > 0.5:
            cuts.append(i)
    cuts.append(len(fr))
    shots = []
    last = None
    for a, b in zip(cuts[:-1], cuts[1:]):
        cand = []
        for f in fr[a:b]:
            fs = faces(f)
            if fs:
                fs = [x for x in fs if x[2] > 18]
            if fs:
                pick = max(fs, key=lambda q: q[0]) if lado == "direita" else min(fs, key=lambda q: q[0])
                # num close há um rosto só e grande: prefere o maior
                big = max(fs, key=lambda q: q[2])
                if big[2] > 0.18 * f.shape[0]:
                    pick = big
                cand.append(pick)
        if cand:
            cx, cy, fh = (float(np.median([c[i] for c in cand])) / k for i in range(3))
            last = (cx, cy, fh)
        elif last:
            cx, cy, fh = last
        else:
            cx, cy, fh = W / 2, H * 0.4, 300.0
        z = float(np.clip(0.28 * H / fh, 1.15, 2.4))
        # zoom mínimo para a janela conseguir centralizar o rosto (rosto perto da borda)
        z = float(min(2.6, max(z, (W / 2) / max(cx, 1), (W / 2) / max(W - cx, 1))))
        shots.append({"t0": t0 + a / 4.0, "t1": t0 + b / 4.0, "cx": cx, "cy": cy, "fh": fh, "z": z})
    # funde planos muito curtos (< 0,75 s) no anterior
    merged = []
    for s in shots:
        if merged and s["t1"] - s["t0"] < 0.75:
            merged[-1]["t1"] = s["t1"]
        else:
            merged.append(s)
    merged[-1]["t1"] = t1
    return merged


def render_crt(path, c, out):
    shots = plan(path, c["in"], c["out"], c.get("lado", "direita"))
    tmp = []
    for i, s in enumerate(shots):
        cw, ch = W / s["z"], H / s["z"]
        x = float(np.clip(s["cx"] - cw / 2, 0, W - cw))
        y = float(np.clip(s["cy"] - ch * 0.38, 0, H - ch))
        seg = out + f".s{i}.mp4"
        dur = s["t1"] - s["t0"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['t0']:.3f}", "-t", f"{dur:.3f}", "-i", path,
                        "-an", "-vf", f"fps={FPS},crop={cw:.0f}:{ch:.0f}:{x:.0f}:{y:.0f},scale={W}:{H}:flags=lanczos,{CRT}",
                        "-c:v", "libx264", "-preset", "fast", "-crf", "18", seg], check=True)
        tmp.append(seg)
    lst = out + ".txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(t)}'\n" for t in tmp))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-ss", f"{c['in']:.3f}", "-t", f"{c['out'] - c['in']:.3f}", "-i", path,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "highpass=f=80,lowpass=f=10000,afade=t=in:d=0.04,afade=t=out:st=%.3f:d=0.08" % (c['out'] - c['in'] - 0.08),
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", out], check=True)
    for t in tmp + [lst]:
        os.remove(t)
    return shots


def render_cor(path, c, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['in']:.3f}", "-t", f"{c['out'] - c['in']:.3f}", "-i", path,
                    "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                    "-af", "afade=t=in:d=0.04,afade=t=out:st=%.3f:d=0.08" % (c['out'] - c['in'] - 0.08),
                    "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out], check=True)


if __name__ == "__main__":
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])
    os.makedirs(out_dir, exist_ok=True)
    rel = {}
    for c in json.load(open(os.path.join(AQUI, "cortes.json")))["cortes"]:
        if only and c["id"] not in only:
            continue
        path = os.path.join(src_dir, SRC[c["src"]])
        out = os.path.join(out_dir, f"{c['id']}.mp4")
        if c["modo"] == "crt":
            shots = render_crt(path, c, out)
            rel[c["id"]] = [(round(s["t0"], 2), round(s["z"], 2), round(s["cx"])) for s in shots]
        else:
            render_cor(path, c, out)
            rel[c["id"]] = "cor"
        print(c["id"], rel[c["id"]], flush=True)
    json.dump(rel, open(os.path.join(out_dir, "_planos.json"), "w"), indent=1)
