"""Converte os timestamps do Whisper (narracao-gemini.words.json) em legendas no JSON de dados,
corrigindo grafia e aplicando os cortes/deslocamentos da narração."""
import json, os
ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "src", "data", "sao-paulo.json")
d = json.load(open(DATA))
words = json.load(open(os.path.join(ROOT, "public", "sao-paulo", "audio", "narracao-gemini.words.json")))
FIX = {"Tele": "Telê", "-Santana,": "Santana,", "B": "bi", "Líverpo.": "Liverpool.", "Sene,": "Ceni,", "Mundial,": "mundial,"}
out = []
i = 0
while i < len(words):
    w = dict(words[i])
    if w["w"] == "A" and i + 1 < len(words) and words[i + 1]["w"] == ".A.":
        w = {"w": "AA", "s": w["s"], "e": words[i + 1]["e"]}
        i += 1
    txt = FIX.get(w["w"], w["w"])
    s = w["s"]
    off = None
    for c in d["audio"]["narracaoCortes"]:
        if c["de"] <= s < c["ate"]:
            off = c["em"] - c["de"]
    out.append({"text": txt, "start": round(s + off, 3), "end": round(w["e"] + off, 3)})
    i += 1
# "Mundial" com maiúscula volta ao normal (nome da competição)
for o in out:
    if o["text"] == "mundial,":
        o["text"] = "Mundial,"
d["legendas"] = out
json.dump(d, open(DATA, "w"), ensure_ascii=False, indent=2)
print(len(out), "palavras;", " ".join(o["text"] for o in out))
