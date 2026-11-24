"""Gera videos/<id>/tempos.json: duração de cada cena (fala + respiros) e o tempo de cada palavra do TEXTO
(alinhado ao Whisper de narracao/cena_XX.words.json). Uso: python3 tools/preparar.py historias/lusa2013.json"""
import json, sys, os, wave, difflib, unicodedata
ANTES, DEPOIS = 0.15, 0.35
def norm(w):
    w = unicodedata.normalize("NFD", w.lower()); return "".join(c for c in w if c.isalnum())
H = json.load(open(sys.argv[1])); base = os.path.join("videos", H["id"])
out = []
for k, c in enumerate(H["cenas"]):
    wav = os.path.join(base, "narracao", f"cena_{k+1:02d}.wav")
    f = wave.open(wav); fala = f.getnframes() / f.getframerate()
    asr = json.load(open(wav.replace(".wav", ".words.json")))
    words = c["texto"].split()
    a = [norm(w) for w in words]; b = [norm(q["w"]) for q in asr]
    t = [None] * len(words)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for j in range(blk.size): t[blk.a + j] = asr[blk.b + j]["s"]
    if t[0] is None: t[0] = 0.0
    fim = fala - 0.1
    for i in range(len(t)):
        if t[i] is None:
            j = next((x for x in range(i + 1, len(t)) if t[x] is not None), None)
            nxt = t[j] if j is not None else fim
            t[i] = t[i - 1] + (nxt - t[i - 1]) / (((j if j is not None else len(t)) - i) + 1)
    pal = []
    for i, w in enumerate(words):
        fimw = t[i + 1] if i + 1 < len(t) else fim
        pal.append({"w": w, "t": round(t[i] + ANTES, 3), "f": round(fimw + ANTES, 3)})
    out.append({"id": c["id"], "fala": round(fala, 3), "dur": round(fala + ANTES + DEPOIS, 3), "audio": f"{H['id']}/cena_{k+1:02d}.wav", "palavras": pal})
json.dump(out, open(os.path.join(base, "tempos.json"), "w"), ensure_ascii=False, indent=1)
print("total", round(sum(c["dur"] for c in out), 2), "s")
