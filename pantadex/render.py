# -*- coding: utf-8 -*-
"""Renderiza out/pantadex.mp4 (1080x1920, 30 fps, H.264 + AAC).
Uso: python render.py            -> vídeo completo
     python render.py shots 1 8  -> só quadros de prévia nos tempos dados (segundos)"""
import sys, os, subprocess
from pdx.common import *
from pdx.show import Show
from pdx import audio, gadget

OUT = os.path.join(ROOT, "out")
def main():
    os.makedirs(OUT, exist_ok=True)
    sh = Show()
    wav = os.path.join(OUT, "audio.wav")
    spk = audio.build(sh, wav)
    n = int(round(sh.total * FPS))
    print(f"duração {sh.total:.2f}s, {n} quadros")
    def fr(i):
        t = i / FPS
        im, hud = sh.frame(t)
        hud["speaker"] = float(spk[i]) if hud.get("power") else 0.0
        if not hud.get("power"): hud.update(scan=0, rec=False)
        return gadget.compose(im, hud, t)
    if len(sys.argv) > 1 and sys.argv[1] == "shots":
        for ts in sys.argv[2:]:
            fr(int(float(ts) * FPS)).save(os.path.join(OUT, f"shot_{float(ts):05.1f}.png"))
        return
    mp4 = os.path.join(OUT, "pantadex.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", "-shortest", mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(fr(i).tobytes())
        if i % 300 == 0: print(f"  {i}/{n}", flush=True)
    p.stdin.close(); p.wait()
    print("ok:", mp4)
if __name__ == "__main__": main()
