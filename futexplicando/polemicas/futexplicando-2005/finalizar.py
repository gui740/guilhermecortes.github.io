"""Finaliza o vídeo com a narração.

Pré-requisito: narracao/cena_01.wav ... narracao/cena_10.wav (um áudio por cena, na ordem de cenas.json).
Uso:  python3 finalizar.py
Saída: fut2005_FINAL.mp4
"""
import json, subprocess, sys, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

SR = 44100
PAD_ANTES, PAD_DEPOIS = 0.15, 0.35   # respiro antes/depois da fala em cada cena

def ler(path):
    """Lê qualquer áudio (wav/mp3) convertendo pra mono 44.1k via ffmpeg."""
    tmp = path + ".tmp.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", path, "-ac", "1", "-ar", str(SR), tmp], check=True)
    sr, x = wavfile.read(tmp); os.remove(tmp)
    x = x.astype(np.float32) / (32768 if x.dtype == np.int16 else 1)
    return x

cenas = json.load(open("cenas.json"))
falas, timings = [], []
for c in cenas:
    cand = [f"narracao/cena_{c['cena']:02d}.{e}" for e in ("wav", "mp3", "m4a", "ogg")]
    p = next((x for x in cand if os.path.exists(x)), None)
    if not p:
        sys.exit(f"Falta o áudio da cena {c['cena']} ({c['id']}): {cand[0]}")
    x = ler(p)
    falas.append(x)
    timings.append(round(len(x) / SR + PAD_ANTES + PAD_DEPOIS, 3))
print("durações por cena:", timings, "total:", round(sum(timings), 1), "s")

# 1) vídeo re-cronometrado pela voz (escreve timings.json)
import render
render.main("fut2005_video_final.mp4", timings)
# 2) trilha + efeitos nos tempos novos
subprocess.run([sys.executable, "audio.py"], check=True)

# 3) mixagem: narração por cima, trilha abaixando quando tem voz
total = sum(timings)
N = int((total + 0.5) * SR)
narr = np.zeros(N, np.float32)
t = 0.0
for x, d in zip(falas, timings):
    i = int((t + PAD_ANTES) * SR)
    x = x[: N - i]; narr[i:i + len(x)] += x
    t += d
narr = narr / (np.abs(narr).max() + 1e-9) * 0.95

def stem(path):
    sr, x = wavfile.read(path); x = x[:, 0].astype(np.float32) / 32767
    x = np.pad(x, (0, max(0, N - len(x))))[:N]
    return x
musica, efeitos = stem("so_trilha.wav"), stem("so_efeitos.wav")

# envelope da voz -> ducking da trilha (abaixa ~10 dB com voz)
win = int(0.25 * SR)
envv = np.convolve(np.abs(narr), np.ones(win) / win, mode="same")
voz = np.clip(envv / (envv.max() * 0.15 + 1e-9), 0, 1)
ganho_musica = 1.0 - 0.68 * voz
mix = narr * 1.0 + musica * 1.6 * ganho_musica + efeitos * 0.75
mix = np.tanh(mix * 1.1) * 0.92
wavfile.write("mix_final.wav", SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))

subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "fut2005_video_final.mp4", "-i", "mix_final.wav",
                "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                "-shortest", "fut2005_FINAL.mp4"], check=True)
print("PRONTO: fut2005_FINAL.mp4")
