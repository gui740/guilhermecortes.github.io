"""Legendas palavra a palavra do vídeo do Corinthians (Whisper + correções de grafia)."""
import json, os
ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "src", "data", "corinthians.json")
d = json.load(open(DATA))
w = json.load(open(os.path.join(ROOT, "public", "corinthians", "audio", "narracao-gemini.words.json")))
off = d["audio"]["narracaoCortes"][0]["em"]
FIX = {"Retir.": "Retiro.", "ponte": "Ponte", "preta": "Preta", "democracia": "Democracia", "curintiana.": "Corinthiana:",
       "Clubs": "Clubes", "CRB.": "Série B...", "libertadores": "Libertadores", "Vickta": "invicta", "guerreiro.": "Guerrero.",
       "Afiel.": "a Fiel.", "acaba.": "acaba!", "Corinthians.": "Corinthians!"}
out = []
skip = False
for i, x in enumerate(w):
    if skip:
        skip = False; continue
    t = x["w"]
    if t == "em" and i + 1 < len(w) and w[i + 1]["w"] == "Vickta":
        out.append({"text": "invicta", "start": round(x["s"] + off, 3), "end": round(w[i + 1]["e"] + off, 3)}); skip = True; continue
    if t == "Corinthians," and i > 0 and w[i - 1]["w"] == "o":
        t = "Corinthian,"
    out.append({"text": FIX.get(t, t), "start": round(x["s"] + off, 3), "end": round(x["e"] + off, 3)})
d["legendas"] = out
json.dump(d, open(DATA, "w"), ensure_ascii=False, indent=2)
print(" ".join(o["text"] for o in out))
