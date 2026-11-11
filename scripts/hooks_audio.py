"""Corta o áudio da mixagem nos mesmos trechos dos ganchos (ver src/Root.tsx) e faz o mux."""
import json, subprocess
T = json.load(open("src/data/timeline.json")); b = T["blocks"]
H = {"A": [(0, 90)],
     "B": [(b[4]["start"], b[4]["start"]+87)],
     "C": [(b[12]["start"], b[12]["end"]), (b[13]["start"], b[13]["start"] + 90 - (b[12]["end"]-b[12]["start"]))]}
for k, segs in H.items():
    parts = []; f = ""
    for i, (a, z) in enumerate(segs):
        f += f"[0:a]atrim={a/30}:{z/30},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={(z-a)/30-0.02}:d=0.02[a{i}];"
        parts.append(f"[a{i}]")
    f += "".join(parts) + f"concat=n={len(segs)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg","-v","error","-y","-i","build/mix.wav","-i",f"build/gancho_{k}.mp4","-filter_complex",f,
        "-map","1:v","-map","[o]","-c:v","libx264","-b:v","12M","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",f"out/gancho_{k}.mp4"],check=True)
    print(k, segs)
