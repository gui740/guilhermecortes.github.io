"""Gera a narração pt-BR (Kokoro TTS, offline). Uso: python tts.py <dir_modelos>
Os .wav resultantes ficam em assets/narration e são versionados; o render não precisa do modelo."""
import sys, os, json
import numpy as np, soundfile as sf
from pdx.script import NARRATION
VOICE, SPEED = "pf_dora", 1.0
def trim(a, sr, thr=0.01, pad=0.04):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    p = int(pad * sr)
    return a[max(0, idx[0] - p): idx[-1] + p]
def main():
    from kokoro_onnx import Kokoro
    md = sys.argv[1]
    k = Kokoro(f"{md}/kokoro-v1.0.onnx", f"{md}/voices-v1.0.bin")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "narration")
    only = sys.argv[2:]
    for key, txt in NARRATION.items():
        if only and key not in only: continue
        a, sr = k.create(txt, voice=VOICE, speed=SPEED, lang="pt-br")
        a = trim(a.astype(np.float32), sr)
        a = a / max(1e-6, np.abs(a).max()) * 0.9
        sf.write(f"{out}/{key}.wav", a, sr)
        print(f"{key:10s} {len(a)/sr:5.2f}s  {txt}")
if __name__ == "__main__": main()
