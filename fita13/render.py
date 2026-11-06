#!/usr/bin/env python3
"""FITA 13: O ARSENAL — ponto de entrada.

    python render.py            # vídeo completo -> saida/fita13_arsenal.mp4
    python render.py --preview  # 1 PNG por cena em saida/preview/
"""
import argparse
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C  # noqa: E402
import eventos  # noqa: E402
import fx_vhs  # noqa: E402
from cenas import CENAS  # noqa: E402
from cenas.comum import contorno, desenho, quadrado_stop, triangulo_play  # noqa: E402

PREVIEWS = [
    ("01_abertura_azul", 0.5), ("02_abertura_barras", 2.2), ("03_abertura_etiqueta", C.ETIQUETA_T),
    ("04_patrimonio_intro", 6.6), ("05_patrimonio_cartao", C.CARTOES_T[1] + 2.0),
    ("06_patrimonio_balao", C.FALA_FINAL_INICIO + 1.5),
    ("07_corrupcao", C.T_CORR + 3.4), ("08_corrupcao_subliminar", C.SUBLIMINAR_T),
    ("09_regras_intro", C.T_REGRAS + 1.0), ("10_regras", C.REGRAS_T[3] + 3.0), ("11_regras_7", C.REGRAS_T[6] + 2.5),
    ("12_alerta", C.T_ALERTA + 7.4), ("13_patio", C.T_PATIO + 3.0), ("14_patio_final", C.T_PATIO + 7.5),
    ("15_patio_negativo", C.PATIO_NEGATIVO_T), ("16_fim", C.FIM_APRENDIZ_T + 0.4), ("17_fim_cartao", C.FIM_CARTAO + 1.5),
    ("18_fim_stop", C.DURACAO - 0.2),
]


# ------------------------------------------------------------------ OSD
def desenhar_osd(img, t):
    """OSD do videocassete: desenhado por cima do sinal, quase sem efeito."""
    d = desenho(img)
    branco = (235, 255, 235)
    if t < 3.0:
        if int(t * 2.5) % 2 == 0 or t < 1.0:
            triangulo_play(d, 18, 66, 16, branco)
            contorno(d, (40, 64), "PLAY", 18, branco)
        contorno(d, (C.W - 18, 64), "SP", 18, branco, anchor="ra")
    if t >= C.FIM_AZUL:
        quadrado_stop(d, 18, 68, 14, branco)
        contorno(d, (40, 64), "STOP", 18, branco)
        contorno(d, (C.W - 18, 64), "SP", 18, branco, anchor="ra")
    if (C.ABERTURA_AZUL_FIM <= t < C.T_ALERTA and not (C.SUBLIMINAR_T <= t < C.SUBLIMINAR_T + 0.07)) \
            or C.FIM_PRETO <= t < C.FIM_CARTAO:
        contorno(d, (16, 512), C.timestamp(t), 13, branco)
    return img


# ------------------------------------------------------------------ frame
class Estado:
    ultimo = None


def renderizar_frame(fi, idx, estado):
    t = fi / C.FPS
    nome, a, _ = C.bloco_em(t)
    k = C.intensidade(t)
    rng = np.random.default_rng([C.SEED, fi, 99])
    if fi in idx["transicoes"]:
        arr = fx_vhs.estatica(rng)
        if estado.ultimo is not None:
            arr = arr * 0.85 + np.asarray(estado.ultimo, np.float32) * 0.15
        k = max(k, 0.7)
    else:
        g = idx["glitches"].get(fi)
        if g and g[0] == "congelar" and estado.ultimo is not None:
            img = estado.ultimo
        else:
            img = CENAS[nome](t - a, fi)
            estado.ultimo = img
        arr = np.asarray(img, np.float32).copy()
        if g and g[0] != "congelar":
            arr = fx_vhs.glitch_forte(arr, g[0], g[1], rng)
    arr = fx_vhs.aplicar(arr, k, t, rng, idx["tracking"].get(fi), idx["dropouts"].get(fi))
    out = Image.fromarray(arr.astype(np.uint8))
    return desenhar_osd(out, t)


# ------------------------------------------------------------------ modos
def preview():
    pasta = os.path.join(C.SAIDA_DIR, "preview")
    os.makedirs(pasta, exist_ok=True)
    idx = eventos.indexar(eventos.gerar())
    if C.carregar_env_boca() is None:
        import audio
        print("Gerando narração (para a boca do mascote)...")
        audio.narracao_processada()
    for nome, t in PREVIEWS:
        fi = int(round(t * C.FPS))
        est = Estado()
        img = renderizar_frame(fi, idx, est)
        img.resize((C.OUT_W, C.OUT_H), Image.BILINEAR).save(os.path.join(pasta, nome + ".png"))
        print("  preview:", nome)
    print("Previews em", pasta)


def video():
    import audio
    t0 = time.time()
    ev = eventos.gerar()
    eventos.salvar(ev)
    idx = eventos.indexar(ev)
    print("Sintetizando narração e áudio...")
    audio.gerar(C.ARQUIVO_AUDIO, ev)
    print("Áudio pronto (%.1fs). Renderizando %d frames..." % (time.time() - t0, C.N_FRAMES))
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (C.W, C.H), "-r", str(C.FPS), "-i", "-",
           "-i", C.ARQUIVO_AUDIO,
           "-vf", "scale=%d:%d:flags=bilinear,gblur=sigma=0.6" % (C.OUT_W, C.OUT_H),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
           "-movflags", "+faststart", "-shortest", C.ARQUIVO_FINAL]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    est = Estado()
    for fi in range(C.N_FRAMES):
        img = renderizar_frame(fi, idx, est)
        proc.stdin.write(img.tobytes())
        if fi % 150 == 0:
            el = time.time() - t0
            print("  frame %4d/%d  (%.0fs)" % (fi, C.N_FRAMES, el), flush=True)
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        sys.exit("ffmpeg falhou (código %d)" % proc.returncode)
    print("Pronto em %.1f s -> %s" % (time.time() - t0, os.path.abspath(C.ARQUIVO_FINAL)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", action="store_true", help="renderiza 1 frame por cena em PNG")
    args = ap.parse_args()
    os.makedirs(C.SAIDA_DIR, exist_ok=True)
    if args.preview:
        preview()
    else:
        video()


if __name__ == "__main__":
    main()
