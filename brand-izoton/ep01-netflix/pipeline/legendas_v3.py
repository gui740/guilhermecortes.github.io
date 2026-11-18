"""Legendas PT-BR (SRT) do EP01 v3 a partir da voz do Guilherme (palavras_gui.json) e das falas de arquivo (timeline_v3.json)."""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(AQUI, "..", "video", "src", "timeline_v3.json")))
PAL = json.load(open(os.path.join(AQUI, "..", "video", "src", "v3", "palavras_gui.json")))
COLD = [("01", 0.0), ("02", 5.0)]
def ts(s):
    h, r = divmod(max(0, s), 3600); m, r = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(r):02d},{int(round((r % 1) * 1000)) % 1000:03d}"
linhas = []
def palavras(bloco, t0):
    ws = PAL[bloco]["palavras"]; cur = []
    for w in ws:
        cur.append((t0 + w[0], t0 + w[1], w[2]))
        fim_frase = w[2].endswith((".", "?", "!", ","))
        if len(cur) >= 7 or (fim_frase and len(cur) >= 3) or (cur and cur[-1][1] - cur[0][0] > 2.6):
            linhas.append((cur[0][0], cur[-1][1], " ".join(x[2] for x in cur))); cur = []
    if cur: linhas.append((cur[0][0], cur[-1][1], " ".join(x[2] for x in cur)))
for b in TL["trechos"]:
    t = b["start"]
    if b["id"] == "coldopen":
        for bl, off in COLD: palavras(bl, t + off)
    elif b["id"] == "n01b": palavras("04", t)
    elif b["tipo"] == "narr" and b.get("audio"):
        if isinstance(b["audio"], list):
            palavras("52", t); palavras("53", t + b["audio"][2])
        else: palavras(b["bloco"], t)
    elif b["tipo"] == "painel" and b.get("audio"):
        palavras(b["audio"].split("/b")[-1][:2], t + 0.5)
    elif b["tipo"] == "arq" or b["id"] == "T04":
        c = b["cenas"][0] if b["tipo"] == "arq" else {"legenda": ["crescemos enviando DVDs, e tinha as séries em box de DVD.", "Todos nós tivemos a experiência de ver ótimas séries da HBO", "(…) próximo episódio, próximo episódio.", "É muito poderoso ter todos os episódios de uma vez.", "E isso a TV linear não consegue fazer."], "clipDur": 24.0}
        leg = c.get("legenda") or []; dur = c.get("clipDur", b["dur"]); pre = b.get("pre", 0.25 if b["tipo"] == "arq" else 0.8)
        for i, l in enumerate(leg):
            a = t + pre + dur * i / len(leg); linhas.append((a, a + dur / len(leg) - 0.05, l))
linhas.sort()
junt = []
for a, b, txt in linhas:  # palavra solta colada na anterior entra na mesma legenda
    if junt and len(txt.split()) == 1 and a - junt[-1][1] < 0.3:
        junt[-1] = (junt[-1][0], b, junt[-1][2] + " " + txt)
    else: junt.append((a, b, txt))
linhas = junt
out = os.path.join(AQUI, "..", "legendas", "EP01_v3_ptBR.srt"); os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf8") as f:
    for i, (a, b, txt) in enumerate(sorted(linhas), 1): f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
print(len(linhas), "legendas ->", out)
