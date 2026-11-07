"""ROLO 7: A CASA DA ESQUINA — analog horror procedural (aviso de emergência).

    GEMINI_API_KEY=... python render.py      # vídeo final
    python render.py --preview               # 1 PNG por tela em saida/preview/
    python render.py --preview --t 12 40     # PNGs de tempos específicos

As falas ficam em cache em saida/voz/; depois de geradas, a chave não é mais necessária.
"""
import argparse
import multiprocessing as mp
import subprocess
import time

import numpy as np
from PIL import Image

import config as C
import fx_vhs as FX

ROT = []
EVENTOS = []


def gerar_eventos(roteiro):
    """Glitches (vídeo e áudio usam a mesma lista). Poucos nas telas de texto, mais no CFTV."""
    rng = np.random.default_rng(C.SEED)
    ev = []

    def add(t, nf, tipo):
        ev.append({"f0": int(round(t * C.FPS)), "nf": int(nf), "tipo": tipo})

    for s in roteiro:
        if s["tipo"] == "regra":
            # um drop-out curto no fim de algumas regras, depois que a voz terminou
            if rng.random() < 0.6:
                add(s["t1"] - rng.uniform(0.2, 0.5), rng.integers(2, 4), "dropout")
            if s["n"] == 7:
                add(s["t_extra"], 3, "blocos")
                t = s["t_extra"] + 0.6
                while t < s["t1"] - 0.2:
                    add(t, rng.integers(1, 3), rng.choice(["blocos", "repete", "dropout"]))
                    t += rng.uniform(0.35, 0.8)
        elif s["tipo"] == "cftv":
            add(s["t0"] + rng.uniform(0.3, 0.6), 2, rng.choice(["blocos", "dropout"]))
            if s["var"] == "perto":
                add(s["t0"], 2, "misto")
                add(s["t1"] - 0.2, 3, "inverte")
    ev.sort(key=lambda e: e["f0"])
    return ev


def _init(rot, ev):
    global ROT, EVENTOS
    import cenas
    ROT, EVENTOS = rot, ev
    cenas.ROTEIRO[:] = rot


def quadro(i):
    import cenas
    rng = np.random.default_rng([C.SEED, i, 77])
    evs = [e for e in EVENTOS if e["f0"] <= i < e["f0"] + e["nf"]]
    ic = i - 1 if any(e["tipo"] == "repete" for e in evs) else i
    t = i / C.FPS
    img = cenas.cena(ic / C.FPS, ic)
    info = img.info
    fx = info.get("fx", 0.3)
    estat = info.get("estat", 0.0)
    arr = FX.aplicar(np.asarray(img.convert("RGB")), fx, t, rng, info.get("grade", "tv"),
                     [e for e in evs if e["tipo"] != "repete"], estat)
    camada = info.get("texto")
    if camada is not None and estat < 0.9:
        arr = FX.compor_texto(arr, camada, rng, fx)
        if any(e["tipo"] == "inverte" for e in evs):
            arr = 255 - arr
    out = Image.fromarray(arr).resize((C.OUT_W, C.OUT_H), Image.BILINEAR)
    if info.get("hires"):
        info["hires"](out)
    return out


def _bytes(i):
    return quadro(i).tobytes()


def preparar():
    import audio
    import roteiro
    import voz
    print("» falas (Gemini TTS, com cache)…")
    falas = voz.gerar_todas()
    for k in ("intro1", "intro2"):
        falas[k] = roteiro.encurtar_pausas(falas[k])
    rot, total = roteiro.montar(falas)
    ev = gerar_eventos(rot)
    print("» mixando áudio…")
    wav = audio.mixar(rot, total, ev, falas)
    return rot, total, ev, wav


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--t", type=float, nargs="*")
    a = ap.parse_args()
    t0 = time.time()
    rot, total, ev, wav = preparar()
    _init(rot, ev)
    n = int(round(total * C.FPS))
    if a.preview:
        pasta = C.SAIDA / "preview"
        pasta.mkdir(parents=True, exist_ok=True)
        if a.t:
            alvos = [(f"t_{x:06.2f}", x) for x in a.t]
        else:
            alvos = []
            for k, s in enumerate(rot):
                if s["tipo"] in ("abre", "preto"):
                    continue
                tm = s.get("t_extra", s["t0"]) + min(1.5, (s["t1"] - s.get("t_extra", s["t0"])) * 0.6)
                nome = s["tipo"] + (f"_{s['n']}" if "n" in s else "") + (f"_{s['var']}" if "var" in s else "")
                alvos.append((f"{k:02d}_{nome}", tm))
        for nome, tm in alvos:
            p = pasta / f"{nome}.png"
            quadro(int(round(tm * C.FPS))).save(p)
            print("  ", p)
    else:
        print(f"» renderizando {n} quadros ({total:.1f} s)…")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stats",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{C.OUT_W}x{C.OUT_H}", "-r", str(C.FPS), "-i", "-",
               "-i", str(wav), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
               "-t", f"{total:.3f}", "-movflags", "+faststart", str(C.ARQUIVO_FINAL)]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with mp.get_context("fork").Pool(max(1, mp.cpu_count() - 1), initializer=_init, initargs=(rot, ev)) as pool:
            for k, b in enumerate(pool.imap(_bytes, range(n), chunksize=6)):
                ff.stdin.write(b)
        ff.stdin.close()
        ff.wait()
        if ff.returncode:
            raise SystemExit("ffmpeg falhou")
        print(f"✔ arquivo final: {C.ARQUIVO_FINAL}")
    print(f"⏱ tempo de render: {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
