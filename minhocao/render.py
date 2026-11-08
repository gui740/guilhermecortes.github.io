"""AVISO AOS PESCADORES: RIO CUIABÁ — render procedural em estilo analog horror.

    python render.py            # vídeo final em saida/aviso_pescadores_rio_cuiaba.mp4
    python render.py --preview  # um PNG por momento-chave em saida/preview/
"""
import argparse
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import config as C
import fx_vhs
from cenas import CENAS, PREVIEW, cena_em
from cenas.comum import CTX, VT, fonte, nova, desenho, centro, quebra
from cenas import fim as cena_fim

FPS = C.FPS
N_FRAMES = int(round(C.DURACAO * FPS))


# ---------------------------------------------------------------------------
# Lista única de eventos (vídeo + áudio)
# ---------------------------------------------------------------------------
def monta_eventos():
    ev = []

    def est(t, frames):
        ev.append({"tipo": "estatica", "t": t - frames / 2 / FPS, "dur": frames / FPS})

    def gl(t, frames, sub=None):
        ev.append({"tipo": "glitch", "t": t, "dur": frames / FPS, "sub": sub})

    # transições: estática + barra de tracking
    est(C.T_PLAY_FIM, 4)
    est(6.0, 6)
    est(28.0, 8)
    est(52.0, 8)
    est(59.0, 6)
    for tc in C.T_CORTES_MARGEM[1:]:
        est(tc, 4)
    est(66.0, 10)
    est(73.0, 6)
    est(C.T_CARTAO_REAL, 4)
    # glitches fortes pontuais
    gl(20.0, 3, "blocos")
    gl(22.1, 2, "repete")
    gl(23.15, 3, "blocos")
    gl(24.95, 2, "rola")
    gl(26.1, 1, "inverte")
    from cenas import regras
    gl(regras.t_1968() - 0.05, 3, "rola")
    gl(51.0, 2, "blocos")
    gl(55.85, 2, "blocos")
    gl(57.1, 3, "rola")
    gl(61.9, 2, "repete")
    gl(65.4, 2, "inverte")
    gl(68.9, 3, "blocos")
    gl(70.9, 2, "rola")
    # subliminar (2 frames)
    ev.append({"tipo": "subliminar", "t": C.T_SUBLIMINAR1, "dur": 2 / FPS, "texto": C.SUBLIMINAR1})
    # glitches do "ELE CONTA AS CANOAS."
    for i in range(int(C.T_FIM_TEXTO * FPS), int(C.T_CARTAO_REAL * FPS)):
        if cena_fim.glitch_frame(i / FPS, i):
            ev.append({"tipo": "dropout", "t": i / FPS, "dur": 1 / FPS})
    return sorted(ev, key=lambda e: e["t"])


def eventos_no_frame(eventos, i):
    t = (i + 0.5) / FPS
    return [e for e in eventos if e["t"] <= t < e["t"] + e["dur"]]


# ---------------------------------------------------------------------------
def tela_subliminar(txt):
    img = nova((0, 0, 0))
    d = desenho(img)
    f = fonte(VT, 40)
    linhas = quebra(txt, f, 320)
    y = 300 - len(linhas) * 18
    for ln in linhas:
        centro(d, y, ln, f, (255, 255, 255))
        y += 36
    return img


def para_np(img):
    return np.asarray(img, dtype=np.float32) / 255.0


def para_pil(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


class Renderizador:
    def __init__(self, eventos):
        self.eventos = eventos
        self.anterior = None

    def frame(self, i):
        t = i / FPS
        rng = np.random.default_rng(C.SEED * 31 + i)
        evs = eventos_no_frame(self.eventos, i)
        tipos = {e["tipo"]: e for e in evs}
        nome, a, b, cena, estilo, osd = cena_em(t)

        if "estatica" in tipos:
            arr = fx_vhs.estatica(rng, i)
            self.anterior = arr
            return para_pil(arr)
        if "subliminar" in tipos:
            arr = fx_vhs.aplica(para_np(tela_subliminar(tipos["subliminar"]["texto"])), 1.0, "nenhum", i, rng)
            return para_pil(fx_vhs.glitch(arr, rng, "blocos"))
        if "glitch" in tipos and tipos["glitch"].get("sub") == "repete" and self.anterior is not None:
            return para_pil(self.anterior)

        k, modo = estilo(t)
        img = cena(t, i)
        if modo == "limpo":
            arr = fx_vhs.leve(para_np(img), rng)
        else:
            if "glitch" in tipos or "dropout" in tipos:
                k = C.FX_INTENSIDADE["glitch"]
            arr = fx_vhs.aplica(para_np(img), k, modo, i, rng)
            if "glitch" in tipos:
                arr = fx_vhs.glitch(arr, rng, tipos["glitch"].get("sub"))
            elif "dropout" in tipos:
                arr = fx_vhs.glitch(arr, rng, "blocos")
        if osd is not None and modo != "preto":
            pil = para_pil(arr)
            camada = Image.new("RGB", pil.size, (0, 0, 0))
            osd(t, i, camada)
            mascara = Image.fromarray((np.asarray(camada).max(-1) > 8).astype(np.uint8) * 255, "L")
            pil.paste(camada, (0, 0), mascara)
            arr = fx_vhs.leve(para_np(pil), rng)
        self.anterior = arr
        return para_pil(arr)


def escala_final(img):
    return img.resize((C.OUT_W, C.OUT_H), Image.BILINEAR)


# ---------------------------------------------------------------------------
def prepara_audio(eventos):
    import voz
    import audio
    print("» voz (TTS + rádio AM)...")
    faixa_voz, tempos = voz.gera_voz(int(C.DURACAO * C.SR))
    CTX["voz"] = tempos
    print("» mixagem...")
    st, mono = audio.gera_mix(faixa_voz, eventos)
    CTX["onda"] = mono
    arq = C.SAIDA / "audio_mix.wav"
    audio.salva(st, arq)
    return arq


def preview(eventos):
    pasta = C.SAIDA / "preview"
    pasta.mkdir(parents=True, exist_ok=True)
    r = Renderizador(eventos)
    for nome, tempos in PREVIEW.items():
        for k, t in enumerate(tempos):
            i = int(round(t * FPS))
            img = escala_final(r.frame(i))
            arq = pasta / f"{list(PREVIEW).index(nome) + 1}_{nome}_{k}.png"
            img.save(arq)
            print("  ", arq.relative_to(C.RAIZ))


def render_final(eventos, wav):
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{C.OUT_W}x{C.OUT_H}", "-r", str(FPS),
           "-i", "-", "-i", str(wav),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", str(C.SR), "-ac", "2",
           "-shortest", "-movflags", "+faststart", str(C.ARQUIVO_FINAL)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    r = Renderizador(eventos)
    t0 = time.time()
    for i in range(N_FRAMES):
        proc.stdin.write(escala_final(r.frame(i)).tobytes())
        if i % 150 == 0:
            el = time.time() - t0
            print(f"  frame {i:5d}/{N_FRAMES}  ({el:5.1f}s)", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg falhou")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    C.SAIDA.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    eventos = monta_eventos()
    wav = prepara_audio(eventos)
    if args.preview:
        preview(eventos)
    else:
        print(f"» renderizando {N_FRAMES} frames ({C.DURACAO:.1f} s)...")
        render_final(eventos, wav)
        print(f"Arquivo final: {C.ARQUIVO_FINAL}")
    print(f"Tempo de render: {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
