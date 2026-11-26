"""Linha do tempo derivada da narração: cada cena começa quando a fala dela começa.
Lê NARR (pasta com n00.wav|mp3 ... + words.json)."""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
LOOP_LEN = 0.9         # rebobina até 23:59:54 (frame 0)
T0 = 0.05


def _dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout
    return float(out.strip())


def build(narr):
    lines = json.load(open(os.path.join(HERE, "narracao.json")))
    words = json.load(open(os.path.join(narr, "words.json")))
    plan = {"lines": [], "S": {}, "E": {}, "words": []}
    t = T0
    for i, l in enumerate(lines):
        k = f"n{i:02d}"
        f = None
        for ext in ("wav", "mp3"):
            c = os.path.join(narr, f"{k}.{ext}")
            if os.path.exists(c):
                f = c
                break
        ws = words[k]
        if f.endswith(".mp3"):       # Edge TTS: arquivo com silêncio nas pontas
            lead = ws[0]["t"]
            speech = ws[-1]["t"] + ws[-1]["d"] - lead
        else:                        # Gemini: já vem aparado
            lead = 0.0
            speech = _dur(f)
        plan["lines"].append({"id": l["id"], "file": f, "start": round(t, 3), "lead": lead, "speech": speech})
        plan["S"][l["id"]] = round(t, 3)
        plan["E"][l["id"]] = round(t + speech, 3)
        for w in ws:
            plan["words"].append({"w": w["w"], "t": round(t + w["t"] - lead, 3), "d": w["d"], "line": l["id"]})
        t += speech + l.get("pause", 0.3)
    end = plan["E"][lines[-1]["id"]] + 0.35
    plan["T_LOOP"] = round(end, 3)
    dur = end + LOOP_LEN
    nfr = int(round(dur * FPS))
    plan["NFRAMES"] = nfr
    plan["DUR"] = nfr / FPS
    return plan


def load():
    narr = os.environ.get("NARR", os.path.join(HERE, "out", "narr"))
    return build(narr)


if __name__ == "__main__":
    p = load()
    for l in p["lines"]:
        print(f'{l["id"]:9s} {l["start"]:6.2f} -> {l["start"] + l["speech"]:6.2f}')
    print("DUR", p["DUR"], "frames", p["NFRAMES"])
