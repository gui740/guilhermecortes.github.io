"""Conferência: folha de contato (1 quadro a cada 0,5s), ampliações 200%, duração, loop, cores e textos x research."""
import json, subprocess, os, sys, numpy as np
from PIL import Image, ImageDraw
V = sys.argv[1] if len(sys.argv) > 1 else "out/video.mp4"; O = "out/conferencia_historia"; os.makedirs(O, exist_ok=True)
p = json.loads(subprocess.check_output(["ffprobe", "-v", "0", "-show_streams", "-show_format", "-of", "json", V]))
v = [s for s in p["streams"] if s["codec_type"] == "video"][0]; a = [s for s in p["streams"] if s["codec_type"] == "audio"]
dur = float(p["format"]["duration"]); br = int(p["format"]["bit_rate"]) / 1e6
print(f"vídeo {v['width']}x{v['height']} {v['r_frame_rate']} {v['codec_name']} · áudio {a[0]['codec_name'] if a else 'NENHUM'} · {dur:.2f}s · {br:.1f} Mbps")
assert 55 <= dur <= 65, "duração fora de 55–65s"
def frame(t):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", V, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(int(v["height"]), int(v["width"]), 3)
ts = np.arange(0, dur - 0.05, 0.5); cols = 12; w, h = 180, 320; rows = -(-len(ts) // cols)
sh = Image.new("RGB", (cols * w, rows * (h + 18)), (18, 18, 18)); d = ImageDraw.Draw(sh); prev = None; diffs = []
for i, t in enumerate(ts):
    f = frame(t); im = Image.fromarray(f).resize((w, h), Image.LANCZOS); x, y = (i % cols) * w, (i // cols) * (h + 18)
    sh.paste(im, (x, y)); d.text((x + 3, y + h + 2), f"{t:04.1f}s", fill=(242, 230, 58))
    small = np.asarray(im, np.float32)
    if prev is not None: diffs.append((t, float(np.abs(small - prev).mean())))
    prev = small
sh.save(f"{O}/folha_contato.jpg", quality=86)
# câmera parada? (diferença média entre quadros consecutivos a cada 1/30s em amostras)
still = []
for t in np.arange(0.5, dur - 0.5, 2.0):
    a1, a2 = frame(t).astype(np.float32), frame(t + 1 / 30).astype(np.float32); m = float(np.abs(a1 - a2).mean())
    if m < 0.6: still.append((round(t, 1), round(m, 2)))
print("quadros quase parados (diff < 0.6):", still or "nenhum")
# cortes secos: maior salto entre amostras de 0,5s
big = sorted(diffs, key=lambda x: -x[1])[:5]; print("maiores saltos entre amostras de 0,5s:", [(round(t, 1), round(m, 1)) for t, m in big])
# loop: primeiro x último quadro
f0, f1 = frame(0).astype(np.float32), frame(dur - 0.12).astype(np.float32)
print("loop (diferença 1º x último quadro):", round(float(np.abs(f0 - f1).mean()), 2))
# ampliações 200%
for k, (t, box) in enumerate([(12.8, (180, 900, 720, 1500)), (31.5, (60, 840, 600, 1440)), (45.5, (100, 880, 640, 1480))]):
    f = Image.fromarray(frame(t)).crop(box); f.resize((f.width * 2, f.height * 2), Image.NEAREST).save(f"{O}/zoom200_{k+1}_{t:04.1f}s.png")
print("ok", O)
