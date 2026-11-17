"""Finalização: junta vídeo e mix, monta os Shorts 9:16, gera folha de contato e checagens de enquadramento.

Uso:
  python3 finalizar.py episodio <video_mudo.mp4> <mix.wav> <saida.mp4>
  python3 finalizar.py shorts   <timeline.json> <shorts_dir> <mix.wav>
  python3 finalizar.py contato  <video.mp4> <saida.jpg> [intervalo_s]
  python3 finalizar.py checar   <short.mp4> <saida.jpg>
"""
import json, os, subprocess, sys

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())


def episodio(video, mix, out):
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out])
    print("episodio:", out, f"{dur(out):.1f}s")


def shorts(tl_path, sdir, mix):
    tl = json.load(open(tl_path, encoding="utf8"))
    for s in tl["shorts"]:
        partes = []
        for i, (a, b) in enumerate(s["trechos"]):
            raw = os.path.join(sdir, f"{s['id']}_parte{i}_raw.mp4")
            if not os.path.exists(raw):
                print("faltando", raw); break
            v = os.path.join(sdir, f"_{s['id']}_{i}.mp4")
            d = dur(raw)
            # recorte da faixa central (608 px em 1920 -> 912 px em 2880) e áudio do mesmo trecho do mix
            run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", mix,
                 "-filter_complex", "[0:v]crop=912:1620:984:0,scale=1080:1920:flags=lanczos,setsar=1[v];"
                 f"[1:a]afade=t=in:d=0.08,afade=t=out:st={max(0, d - 0.25):.3f}:d=0.25[a]",
                 "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "256k", "-ar", "48000", v])
            partes.append(v)
        else:
            lst = os.path.join(sdir, f"_{s['id']}.txt")
            open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in partes))
            cat = os.path.join(sdir, f"_{s['id']}_cat.mp4")
            run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cat])
            hook = os.path.join(sdir, f"{s['id']}_hook.png")
            out = os.path.join(sdir, f"{s['id']}.mp4")
            # gancho nos 2,5 s iniciais (entra já visível, sai com fade) + loudness -14 LUFS
            run(["ffmpeg", "-v", "error", "-y", "-i", cat, "-loop", "1", "-t", "2.8", "-i", hook,
                 "-filter_complex", "[1:v]format=rgba,fade=t=out:st=2.3:d=0.4:alpha=1[h];[0:v][h]overlay=0:0:eof_action=pass[v]",
                 "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                 "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", out])
            for p in partes + [lst, cat]:
                os.remove(p)
            print(s["id"], f"{dur(out):.1f}s", out)


def contato(video, out, passo="25"):
    d = dur(video)
    n = int(d // float(passo)) + 1
    cols = 6
    rows = (n + cols - 1) // cols
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
         f"fps=1/{passo},scale=480:270,drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.7,"
         f"tile={cols}x{rows}:padding=6:margin=6:color=white", "-frames:v", "1", "-q:v", "3", out])
    print("contato:", out)


def checar(short, out):
    """Folha de checagem 9:16: um quadro a cada 1,5 s."""
    d = dur(short)
    n = int(d // 1.5) + 1
    cols = 10
    rows = (n + cols - 1) // cols
    run(["ffmpeg", "-v", "error", "-y", "-i", short, "-vf",
         f"fps=1/1.5,scale=216:384,drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=4:y=4:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.7,"
         f"tile={cols}x{rows}:padding=4:margin=4:color=gray", "-frames:v", "1", "-q:v", "3", out])
    print("checagem:", out)


if __name__ == "__main__":
    modo, *args = sys.argv[1:]
    {"episodio": episodio, "shorts": shorts, "contato": contato, "checar": checar}[modo](*args)
