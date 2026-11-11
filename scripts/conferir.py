"""Conferência final: URL e telefones caractere por caractere contra conteudo.json, formato do vídeo e folha de frames."""
import json, subprocess, os, sys
from PIL import Image
c = json.load(open("conteudo.json")); info = json.load(open("build/info.json")); tx = info["textos"]; ok = True
def chk(nome, got, exp):
    global ok; good = got == exp; ok &= good
    print(("OK  " if good else "ERRO"), nome, repr(got), "==" if good else "!=", repr(exp))
s6 = c["slides"][5]
chk("URL (tarja, 2 linhas)", tx["url1"] + tx["url2"], s6["url"])
chk("URL (linha única)", tx["urlm"], s6["url"])
chk("URL (cena dos telefones)", tx["url3"] + tx["url4"], s6["url"])
for i, t in enumerate(s6["telefones"]): chk("Telefone " + t["cidade"], tx[f"tel{i+1}"], t["numero"])
chk("URL final", tx["url5"].split()[-1], c["slides"][7]["url"])
p = json.loads(subprocess.check_output(["ffprobe", "-v", "0", "-show_streams", "-show_format", "-of", "json", "out/reel.mp4"]))
v = [s for s in p["streams"] if s["codec_type"] == "video"][0]; d = float(p["format"]["duration"])
chk("resolução", f'{v["width"]}x{v["height"]}', "1080x1920"); chk("fps", v["r_frame_rate"], "30/1")
good = 45 <= d <= 60; ok &= good; print("OK  " if good else "ERRO", "duração", round(d, 2), "s (45–60)")
# frames de conferência: um por tomada (no fim de cada uma, com tudo na tela)
os.makedirs("out/conferencia", exist_ok=True); ts = [max(s["from"] + 0.6 * (min(s["to"], info["dur"]) - s["from"]), min(s["to"], info["dur"]) - 0.4) for s in info["shots"]]; ims = []
for i, t in enumerate(ts):
    f = f"out/conferencia/{i+1:02d}_{t:05.2f}s.jpg"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", "out/reel.mp4", "-frames:v", "1", "-q:v", "3", f], check=True); ims.append(Image.open(f))
cols = 7; rows = -(-len(ims) // cols); sh = Image.new("RGB", (cols * 360, rows * 640), (17, 17, 17))
for i, im in enumerate(ims): sh.paste(im.resize((360, 640), Image.LANCZOS), ((i % cols) * 360, (i // cols) * 640))
sh.save("out/conferencia/folha.jpg", quality=88)
sys.exit(0 if ok else 1)
