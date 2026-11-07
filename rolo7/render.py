"""ROLO 7: A CASA DA ESQUINA — render procedural de analog horror.

    python render.py              # vídeo final
    python render.py --preview    # 1 PNG por cena em saida/preview/
    python render.py --preview --t 12.3 45   # PNGs de tempos específicos
"""
import argparse
import multiprocessing as mp
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import config as C
import fx_vhs as FX

sys.path.insert(0, str(C.RAIZ))


# ------------------------------------------------------------ eventos de glitch (vídeo + áudio)
def gerar_eventos():
    rng = np.random.default_rng(C.SEED)
    ev = []

    def add(t, nf, tipo):
        ev.append({"f0": int(round(t * C.FPS)), "nf": int(nf), "tipo": tipo})

    # aleatórios, densidade proporcional à intensidade do bloco
    zonas = [(C.B2[0] + 1, C.B2[1], 0.3), (C.B3[0], C.B3[1], 0.6), (C.B4[0], C.B4[1], 0.45),
             (C.B5[0], C.B5[1], 0.8), (C.B6[0], C.T_FITA_ARREBENTA, 1.0)]
    for a, b, dens in zonas:
        t = a + rng.exponential(2.5 / dens)
        while t < b - 0.2:
            if rng.random() < 0.18 * dens:
                add(t, rng.integers(1, 3), rng.choice(["blocos", "repete", "rola"]))
            else:
                add(t, rng.integers(2, 5), "dropout")
            t += rng.exponential(2.8 / dens) + 0.4
    # fixos (roteiro)
    add(C.B3[0], 3, "misto")           # pulo de fita
    add(C.T_RETA - 0.05, 3, "rola")
    add(C.T_PORTA, 2, "blocos")
    add(60.0, 2, "blocos")
    add(62.5, 2, "repete")
    add(64.3, 2, "misto")
    add(C.T_FITA_ARREBENTA, 3, "blocos")
    add(C.T_CONGELA + 2 / C.FPS, 2, "inverte")   # congela e inverte cores 2 frames
    add(C.T_REGRA7_EXTRA, 2, "blocos")
    # nada de glitch nos cartões limpos nem no preto
    ev = [e for e in ev if not (C.T_PRETO * C.FPS - 1 <= e["f0"] < C.B6[1] * C.FPS)
          and e["f0"] < C.T_VERDADE * C.FPS]
    ev.sort(key=lambda e: e["f0"])
    return ev


def _ativos(eventos, i):
    return [e for e in eventos if e["f0"] <= i < e["f0"] + e["nf"]]


def _estatica_transicao(i):
    for t0, fa, fd in C.TRANSICOES:
        f0 = int(round(t0 * C.FPS))
        if f0 - fa <= i < f0 + fd:
            return 1.0 if (i - (f0 - fa)) not in (0, fa + fd - 1) else 0.8
    return 0.0


# ------------------------------------------------------------ um quadro
_EVENTOS = []


def _init(eventos):
    global _EVENTOS
    _EVENTOS = eventos


def quadro(i, eventos=None):
    import cenas
    eventos = _EVENTOS if eventos is None else eventos
    rng = np.random.default_rng([C.SEED, i, 77])
    evs = _ativos(eventos, i)
    i_cena = i - 1 if any(e["tipo"] == "repete" for e in evs) else i
    t = i / C.FPS
    img = cenas.cena(i_cena / C.FPS, i_cena)
    info = img.info
    estat = max(_estatica_transicao(i), info.get("estat", 0.0))
    arr = FX.aplicar(np.asarray(img.convert("RGB")), info.get("fx", 0.3), t, rng,
                     info.get("grade", "tv"), [e for e in evs if e["tipo"] != "repete"], estat)
    osd = info.get("osd")
    if osd is not None and estat < 0.9:
        o = np.asarray(osd).astype(np.float32)
        a = o[..., 3:4] / 255.0
        cor = o[..., :3].copy()
        cor[..., 0] = np.roll(cor[..., 0], 1, axis=1)      # OSD com pouquíssimo efeito
        arr = (arr * (1 - a) + cor * a).astype(np.uint8)
    out = Image.fromarray(arr).resize((C.OUT_W, C.OUT_H), Image.BILINEAR)
    hires = info.get("hires")
    if hires and estat < 0.5:
        hires(out)
    return out


def _bytes(i):
    return quadro(i).tobytes()


# ------------------------------------------------------------ principal
def preparar_audio(eventos):
    import audio
    import voz
    print("» gerando vozes (TTS offline)…")
    falas = voz.gerar_todas()
    print("» mixando áudio…")
    return audio.mixar(eventos, falas)


def preview(eventos, tempos=None):
    import cenas
    pasta = C.SAIDA / "preview"
    pasta.mkdir(parents=True, exist_ok=True)
    if tempos:
        alvos = [(f"t_{t:06.2f}", t) for t in tempos]
    else:
        meio = [3.2, 15.5, 27.0, 34.0, 61.0, 68.5, 77.5]
        alvos = list(zip(cenas.NOMES, meio))
    for nome, t in alvos:
        img = quadro(int(round(t * C.FPS)), eventos)
        p = pasta / f"{nome}.png"
        img.save(p)
        print("  ", p)


def render_final(eventos, audio_wav):
    C.SAIDA.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stats",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{C.OUT_W}x{C.OUT_H}", "-r", str(C.FPS), "-i", "-",
           "-i", str(audio_wav),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
           "-t", f"{C.DURACAO:.3f}", "-movflags", "+faststart", str(C.ARQUIVO_FINAL)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = C.N_FRAMES
    procs = max(1, mp.cpu_count() - 1)
    with mp.get_context("fork").Pool(procs, initializer=_init, initargs=(eventos,)) as pool:
        for k, b in enumerate(pool.imap(_bytes, range(n), chunksize=6)):
            ff.stdin.write(b)
            if k % 150 == 0:
                print(f"\r  quadro {k}/{n}", end="", flush=True)
    ff.stdin.close()
    ff.wait()
    print()
    if ff.returncode != 0:
        raise SystemExit("ffmpeg falhou")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--t", type=float, nargs="*", help="tempos para o preview")
    ap.add_argument("--sem-audio", action="store_true", help="reaproveita saida/audio.wav")
    a = ap.parse_args()
    t0 = time.time()
    eventos = gerar_eventos()
    wav = C.SAIDA / "audio.wav"
    if not (a.sem_audio and wav.exists()):
        wav = preparar_audio(eventos)
    if a.preview:
        preview(eventos, a.t)
    else:
        print(f"» renderizando {C.N_FRAMES} quadros ({C.DURACAO:.1f} s)…")
        render_final(eventos, wav)
        print(f"✔ arquivo final: {C.ARQUIVO_FINAL}")
    print(f"⏱ tempo de render: {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
