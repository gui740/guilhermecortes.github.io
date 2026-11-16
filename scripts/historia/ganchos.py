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
    # voz Gemini (bloco hB/hC) com tempos por palavra transferidos da referência edge-tts via DTW
    from alinhar import load as aload, align, speech_bounds, SR as ASR
    ref = aload(mp3); q = aload(f"build/g_chunks/h{k}.wav"); al = align(ref, [(x["w"], x["t"], x["t"] + x["d"]) for x in w], q)
    a, b = speech_bounds(q); SPD = 1.15; lead = max(0, a - 0.08); x = q[int(lead * ASR):int((b + 0.1) * ASR)].copy()
    from narracao_gemini import silences
    cuts = [(s0 + 0.06, s1 - 0.06) for s0, s1 in silences(x) if s1 - s0 > 0.14 and s0 > 0.02]
    def remap(tt):
        r = tt
        for c0, c1 in cuts:
            if tt >= c1: r -= c1 - c0
            elif tt > c0: r -= tt - c0
        return r
    keep, p0 = [], 0.0
    for c0, c1 in cuts: keep.append(x[int(p0 * ASR):int(c0 * ASR)]); p0 = c1
    keep.append(x[int(p0 * ASR):]); y = np.concatenate(keep)
    t = [remap(z[1] - lead) / SPD for z in al]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(ASR), "-ac", "1", "-i", "-", "-af", f"atempo={SPD},loudnorm=I=-16:TP=-1.5", "-ar", "48000", "-ac", "1", f"build/h_hook_{k}.wav"], input=y.astype(np.float32).tobytes(), check=True)
    print(k, "duração", round(len(y) / ASR / SPD, 2))
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
    ev = [e for e in E["ev"] if e["t"] < 3.5 and e["n"] != "thump"]
    if k != "A": ev = [e for e in ev if e["n"] not in ("flick",)]
    els = out[k]["els"] or []
    ev += [{"t": e["at"], "n": "thump"} for e in els if e.get("shake")]
    if k == "A": ev += [{"t": 3.44, "n": "thump"}]
    json.dump({"total": 3.5, "speed": E["speed"][:106], "ev": ev}, open(f"build/h_hook_{k}_ev.json", "w"))
    narr = "build/h_narracao.wav" if k == "A" else f"build/h_hook_{k}.wav"
    subprocess.run([sys.executable, "scripts/historia/audio.py", f"build/h_hook_{k}_ev.json", narr, f"assets/historia/audio/gancho_{k}.wav"], check=True)
