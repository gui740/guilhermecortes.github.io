"""Gera src/data/timeline.json a partir dos timestamps por palavra (Whisper) da narração final.
Os inícios das palavras são refinados pelo envelope de energia do áudio (onset real da voz)."""
import json, numpy as np, soundfile as sf, re
FPS = 30
W = json.load(open("build/words_raw.json"))
FIX = {84: "teasers"}                      # Whisper ouviu "teenagers"; no áudio é "teasers"
a, sr = sf.read("assets/narracao_limpa.wav"); h = sr//100
env = 20*np.log10(np.sqrt((a[:len(a)//h*h].reshape(-1, h)**2).mean(1))+1e-9)
DUR = len(a)/sr
words = []
for i, x in enumerate(W):
    s, e = x["s"], x["e"]
    i0, i1 = int(s*100), max(int(s*100)+1, int(min(e, s+0.5)*100))
    seg = env[i0:i1]; on = np.argmax(seg > -36) if (seg > -36).any() else 0
    t = s + on/100
    txt = FIX.get(i, x["w"])
    words.append(dict(i=i, raw=txt, t=round(t, 3), f=int(round(t*FPS))))

# estilos: B=chave gigante Anton, b=Anton médio, s=conectivo minúsculo, P=Playfair itálico grande, p=Playfair médio
# sufixo "!" = palavra de destaque (1 por bloco); "x" = some do título (só na legenda) em blocos de close
BLOCKS = [
 dict(r=(0, 6),   bg="G", cut="buddy_wave",  scale="medium", enter="cross", grid=True,
      st="B b s B! p s b"),
 dict(r=(7, 14),  bg="K", cut="buddy_close", scale="close", enter="pop", cap=True,
      st="x P x B! x x x x"),
 dict(r=(15, 18), bg="R", cut="buddy_point", scale="small", enter="pop", fx="cursor",
      st="b B! s B"),
 dict(r=(19, 25), bg="G", cut="buddy_close", scale="small", enter="pop", fx="strike",
      st="s b s B! s b P"),
 dict(r=(26, 36), bg="R", cut="buddy_wave",  scale="medium", enter="pop", fx="star", title=True, burst=True,
      st="s T s s b s B! s b s b"),
 dict(r=(37, 44), bg="G", cut="buddy_tvpo",  scale="tv", enter="zoomout", fx="tv",
      st="s p s b B! s b P"),
 dict(r=(45, 53), bg="K", cut="buddy_hug",   scale="medium", enter="pop", dup=True,
      st="b b s s p B! b s P"),
 dict(r=(54, 61), bg="G", cut="girl_grab",   scale="medium", enter="whip",
      st="b s s b s B! s P"),
 dict(r=(62, 70), bg="K", cut="dark_buddy",  scale="close", enter="whip", cap=True,
      st="x x P x x x x x B!"),
 dict(r=(71, 76), bg="R", cut="kids_scared", scale="medium", enter="pop",
      st="s b s b B! p"),
 dict(r=(77, 82), bg="K", cut="buddy_tvpo",  scale="small", enter="pop", fx="eraser",
      st="s b B! s B p"),
 dict(r=(83, 91), bg="G", cut="bunny",       scale="medium", enter="whip", fx="scissors",
      st="s B p s s b B! s p"),
 dict(r=(92, 95), bg="K", cut="buddy_wave",  scale="small", enter="pop", swap=dict(at=94, cut="dark_buddy", scale="medium", dup=True),
      st="b P B! B"),
 dict(r=(96, 102), bg="R", cut="kids_forest", scale="medium", enter="whip",
      st="b b B! s b s p"),
 dict(r=(103, 111), bg="K", cut="buddy_point", scale="small", enter="whip", fx="num",
      st="s s s b b P! B s p"),
 dict(r=(112, 123), bg="R", cut="buddy_group", scale="medium", enter="whip", dup=True,
      st="s s b s s P! B s s s b b"),
 dict(r=(124, 129), bg="G", cut="buddy_wave",  scale="small", enter="pop", fx="dash",
      st="s b s B s P!"),
 dict(r=(130, 134), bg="K", cut="buddy_close", scale="close", enter="pop", cap=True,
      st="x x b x B!"),
 dict(r=(135, 141), bg="G", cut="buddy_wave",  scale="small", enter="pop", handle=True,
      st="B! s s b s p P"),
]
out = []
total = int(round((DUR + 0.12)*FPS))
for k, b in enumerate(BLOCKS):
    i0, i1 = b["r"]
    start = 0 if k == 0 else words[i0]["f"] - 2   # corte seco 2 frames antes da 1ª palavra
    end = total if k == len(BLOCKS)-1 else words[BLOCKS[k+1]["r"][0]]["f"] - 2
    sts = b["st"].split()
    assert len(sts) == i1-i0+1, (k, len(sts), i1-i0+1)
    ws = []
    for j, st in zip(range(i0, i1+1), sts):
        txt = re.sub(r"[.,?!:]", "", words[j]["raw"])
        ws.append(dict(text=txt, f=words[j]["f"]-start, role=st.replace("!", ""), hl=st.endswith("!")))
    d = {kk: v for kk, v in b.items() if kk not in ("r", "st")}
    if k == 0: ws[0]["f"] = -6   # texto gigante já formado no frame 0
    if "swap" in d: d["swap"] = dict(d["swap"], atLocal=d["swap"]["at"]-i0)
    d.update(start=start, end=end, words=ws)
    out.append(d)
assert all(o["end"] > o["start"] for o in out)
json.dump(dict(fps=FPS, total=total, blocks=out, words=words), open("src/data/timeline.json", "w"), ensure_ascii=False, indent=1)
for o in out: print(f'{o["start"]/FPS:6.2f}-{o["end"]/FPS:6.2f} ({(o["end"]-o["start"])/FPS:.2f}s) {o["bg"]} {o["cut"]:12s}', " ".join(w["text"] for w in o["words"]))
print("total", total, total/FPS)
