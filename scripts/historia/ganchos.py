"""Ganchos alternativos (3s): TTS, timestamps, elementos de tela (src/data/hooks.json) e áudio."""
import asyncio, json, os, subprocess, sys, certifi
if os.environ.get("SSL_CERT_FILE"): certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts, numpy as np
sys.path.insert(0, "scripts/historia")
HOOKS = {
  "B": "Proibiram antes de saber o que era, puta merda.",
  "C": "Doze mil anos de maconha em sessenta segundos.",
}
async def tts(text, out):
    c = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+12%", pitch="+4Hz", boundary="WordBoundary"); w = []
    with open(out, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": w.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    return w
def W(text, font, x, y, h, at, **o): return {"type": "word", "text": text, "font": font, "x": x, "y": y, "h": h, "at": at, **o}
out = {"A": {"audio": "audio/gancho_A.wav", "els": None}}
os.makedirs("assets/historia/audio", exist_ok=True)
for k, text in HOOKS.items():
    mp3 = f"build/h_hook_{k}.mp3"; w = asyncio.run(tts(text, mp3))
    lead = w[0]["t"] - 0.12; t = [x["t"] - lead for x in w]   # começa quase imediatamente
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{lead:.3f}", "-i", mp3, "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "48000", "-ac", "1", f"build/h_hook_{k}.wav"], check=True)
    print(k, [(x["w"], round(tt, 2)) for x, tt in zip(w, t)])
    if k == "B":   # Proibiram antes de saber o que era . Puta merda
        els = [W("PROIBIRAM", "anton", 540, 720, 250, -0.4, hook=1, hl=1), W("ANTES", "anton", 540, 930, 200, t[1]), W("DE SABER", "anton", 540, 1100, 150, t[3]),
               W("O QUE ERA", "anton", 540, 1260, 150, t[4]), W("PUTA MERDA", "anton", 540, 1030, 270, t[7], dz=1.2, shake=1, hl=1, rot=-6)]
    else:          # Doze mil anos de maconha em sessenta segundos. Bora.
        els = [W("12 MIL", "anton", 540, 720, 300, -0.4, hook=1), W("ANOS", "anton", 540, 930, 170, t[2]), W("de", "inter", 300, 1070, 60, t[3]),
               W("MACONHA", "anton", 600, 1080, 190, t[4], hl=1), W("EM 60 SEGUNDOS", "anton", 540, 1270, 120, t[5])]
    out[k] = {"audio": f"audio/gancho_{k}.wav", "els": els}
json.dump(out, open("src/data/hooks.json", "w"), ensure_ascii=False, indent=1)

E = json.load(open("build/h_eventos.json"))
for k in ["A", "B", "C"]:
    ev = [e for e in E["ev"] if e["t"] < 3.0 and e["n"] != "thump"]
    if k != "A": ev = [e for e in ev if e["n"] not in ("flick",)]
    els = out[k]["els"] or []
    ev += [{"t": e["at"], "n": "thump"} for e in els if e.get("shake")]
    if k == "A": ev += [{"t": 3.44, "n": "thump"}]
    json.dump({"total": 3.0, "speed": E["speed"][:91], "ev": ev}, open(f"build/h_hook_{k}_ev.json", "w"))
    narr = "build/h_narracao.wav" if k == "A" else f"build/h_hook_{k}.wav"
    subprocess.run([sys.executable, "scripts/historia/audio.py", f"build/h_hook_{k}_ev.json", narr, f"assets/historia/audio/gancho_{k}.wav"], check=True)
