"""Monta a narração (voz do Gemini, por blocos): corta silêncios longos, garante a pausa dramática
antes de cada título e o respiro depois dele, recalcula timestamps por palavra.
Saída: public/timeline.json + build/vo_<nome>.wav"""
import json, os, subprocess, sys, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from gemini_tts import BLOCKS, texts
SR, FPS = 48000, 30
def load(b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"assets/vo_gemini/{b}.wav", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy(), json.load(open(f"assets/vo_gemini/{b}.json"))["words"]
def silences(x, thr_db=-40, min_len=0.14):
    win = int(0.01 * SR); n = len(x) // win
    db = 20 * np.log10(np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1) + 1e-12))
    on = db > max(thr_db, db.max() - 42)
    out, i = [], 0
    while i < n:
        if not on[i]:
            j = i
            while j < n and not on[j]: j += 1
            if (j - i) * 0.01 >= min_len or i == 0 or j == n: out.append((i * 0.01, j * 0.01))
            i = j
        else: i += 1
    return out, n * 0.01
# pausa mínima ANTES destas falas (título = pausa dramática; depois do título = tempo pra ver o filme)
MIN_GAP = {"a2": 0.40, "b2": 0.40, "c3": 0.45, "a3": 0.50, "b3": 0.50, "c4": 0.50, "a7": 0.32, "b7": 0.32, "c7": 0.32, "h2": 0.22}
MAX_GAP = 0.55
def process(b):
    x, words = load(b)
    sil, total = silences(x)
    # encaixa o início das palavras no fim do silêncio mais próximo (corrige pequenos desvios do alinhamento)
    used = set()
    for n, (s, e) in enumerate(sil):
        if e >= total: continue
        k = 0 if (n == 0 and s <= 0.001) else min(range(len(words)), key=lambda i: abs(words[i]["t"] - e))
        if k in used: continue
        if k == 0 or abs(words[k]["t"] - e) < 0.30: words[k]["t"] = round(e, 3); used.add(k)
    for a, c in zip(words, words[1:]):
        if c["t"] <= a["t"] + 0.05: c["t"] = round(a["t"] + 0.08, 3)
    first_of_line = {w["line"]: i for i, w in reversed(list(enumerate(words)))}
    # mapa de cortes/inserções: lista de (ini, fim, novo_comprimento) para cada silêncio
    edits = []
    for s, e in sil:
        L = e - s
        if s <= 0.001: new = 0.0                                   # silêncio inicial
        elif e >= total - 0.001: new = 0.0                          # silêncio final
        else:
            new = min(L, MAX_GAP)
            for line, mg in MIN_GAP.items():
                if line in first_of_line and abs(words[first_of_line[line]]["t"] - e) < 0.05: new = max(L if L < MAX_GAP else MAX_GAP, mg)
        edits.append((s, e, new))
    pieces, cur, pos, tmap = [], 0.0, 0.0, []
    for s, e, new in edits:
        seg = x[int(pos * SR):int(s * SR)]; pieces.append(seg); tmap.append((pos, s, cur)); cur += len(seg) / SR
        keep = min(new, e - s); half = keep / 2
        if keep > 0:
            a = x[int(s * SR):int((s + half) * SR)]; c = x[int((e - half) * SR):int(e * SR)]
            pad = np.zeros(int(max(0, new - keep) * SR), np.float32)
            pieces += [a, pad, c]
        tmap.append((s, e, cur, new)); cur += new; pos = e
    seg = x[int(pos * SR):]; pieces.append(seg); tmap.append((pos, total + 1, cur))
    def remap(t):
        for m in tmap:
            if m[0] <= t < m[1]:
                if len(m) == 4: return m[2] + min(m[3], max(0.0, m[3] - (m[1] - t)))  # dentro de silêncio: conta a partir do fim
                return m[2] + (t - m[0])
        return cur
    y = np.concatenate(pieces)
    y = y / (np.sqrt((y[np.abs(y) > 0.01] ** 2).mean()) + 1e-9) * 0.12     # mesmo volume em todos os blocos
    ws = [{"w": w["w"], "t": remap(w["t"]), "e": remap(w["t"] + w["d"]), "line": w["line"]} for w in words]
    for a, c in zip(ws, ws[1:]): a["e"] = min(max(a["e"], a["t"] + 0.05), c["t"])
    return y, ws
def build(blocks, name, gap=0.45, lead=0.05, tail=0.15, fit=None):
    out, words, cur = [np.zeros(int(lead * SR), np.float32)], [], lead
    for k, b in enumerate(blocks):
        y, ws = process(b)
        if fit and len(y) / SR > fit:                               # ganchos: cabe em 3 s
            r = (len(y) / SR) / fit
            y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={r:.4f}", "-f", "f32le", "-"], input=y.astype(np.float32).tobytes(), capture_output=True).stdout, np.float32)
            for w in ws: w["t"] /= r; w["e"] /= r
        if k: out.append(np.zeros(int(gap * SR), np.float32)); cur += gap
        for w in ws: words.append({"w": w["w"], "t": round(cur + w["t"], 3), "e": round(cur + w["e"], 3), "line": w["line"]})
        out.append(y); cur += len(y) / SR
    out.append(np.zeros(int(tail * SR), np.float32))
    y = np.concatenate(out); y = np.clip(y / np.abs(y).max() * 0.89, -1, 1)
    T = texts(); lines = []
    for i, w in enumerate(words):
        if not lines or lines[-1]["id"] != w["line"]: lines.append({"id": w["line"], "text": T[w["line"]], "t": w["t"], "e": w["e"], "w0": i, "w1": i + 1})
        else: lines[-1]["e"] = w["e"]; lines[-1]["w1"] = i + 1
    os.makedirs("build", exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", f"build/vo_{name}.wav"], input=y.astype(np.float32).tobytes(), check=True)
    return {"duration": round(len(y) / SR, 3), "words": words, "lines": lines}
tl = {"fps": FPS, "main": build(["B0", "B1", "B2", "B3", "B4", "B5", "B6"], "main")}
for h in ["gA", "gB", "gC"]: tl[h] = build([h], h, fit=2.85, tail=0.0)
json.dump(tl, open("public/timeline.json", "w"), ensure_ascii=False, indent=1)
m = tl["main"]
print("duração:", m["duration"], "palavras:", len(m["words"]))
for l in m["lines"]: print(f'{l["id"]:4s} {l["t"]:6.2f}-{l["e"]:6.2f}  {l["text"]}')
for h in ["gA", "gB", "gC"]: print(h, tl[h]["duration"], [(w["w"], w["t"]) for w in tl[h]["words"]])
