"""Legendas palavra a palavra do vídeo do Palmeiras (Whisper + correções de grafia)."""
import json, os
ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "src", "data", "palmeiras.json")
d = json.load(open(DATA))
w = json.load(open(os.path.join(ROOT, "public", "palmeiras", "audio", "narracao-gemini.words.json")))
off = d["audio"]["narracaoCortes"][0]["em"]
FIX = {"obrigada": "obrigado", "série": "Série", "brasileiro": "Brasileiro", "Comente": "Comenta", "Alliance": "Allianz", "Alianz": "Allianz", "Park": "Parque",
       "corou": "coroa", "ao": "o", "segunda": "Segunda", "heroica.": "Heroica!", "palestra": "Palestra", "palmerense": "palmeirense", "academias": "Academias", "libertadores": "Libertadores",
       "libertadores.": "Libertadores!", "arrancada": "Arrancada", "heroica.": "Heroica!"}
out, i = [], 0
while i < len(w):
    x = w[i]; nxt = w[i + 1] if i + 1 < len(w) else None
    if x["w"] == "a" and nxt and nxt["w"] in ("Belferreira.", "Bel"):
        if nxt["w"] == "Belferreira.":
            mid = (x["s"] + nxt["e"]) / 2
            out += [("Abel", x["s"], mid), ("Ferreira:", mid, nxt["e"])]
        else:
            out.append(("Abel", x["s"], nxt["e"]))
        i += 2; continue
    if x["w"] == "B" and nxt and nxt["w"] == "da":
        out.append(("bi", x["s"], x["e"])); i += 1; continue
    if x["w"] == "Bida,":
        mid = (x["s"] + x["e"]) / 2
        out += [("bi", x["s"], mid), ("da", mid, x["e"])]; i += 1; continue
    if x["w"] == "a" and nxt and nxt["w"] == "campeão,":
        out.append(("é", x["s"], x["e"])); i += 1; continue
    out.append((FIX.get(x["w"], x["w"]), x["s"], x["e"])); i += 1
d["legendas"] = [{"text": t, "start": round(s + off, 3), "end": round(e + off, 3)} for t, s, e in out]
json.dump(d, open(DATA, "w"), ensure_ascii=False, indent=2)
print(" ".join(t for t, _, _ in out))
