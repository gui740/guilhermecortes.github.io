"""Monta a narração: corta silêncios (>200ms), pausa dramática antes de cada título,
recalcula timestamps por palavra e gera public/timeline.json + build/vo_<nome>.wav."""
import json, os, subprocess, sys, numpy as np
SR = 48000
FPS = 30
def load(i):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"assets/vo/{i}.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy(), json.load(open(f"assets/vo/{i}.json"))
def speech_segments(x, thr_db=-42, max_gap=0.20, pad=0.03):
    """Segmentos de fala; silêncios internos acima de max_gap são encurtados para max_gap."""
    win = int(0.01 * SR)
    n = len(x) // win
    rms = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1) + 1e-12)
    on = 20 * np.log10(rms) > thr_db
    idx = np.where(on)[0]
    a, b = idx[0], idx[-1] + 1
    segs, start, i = [], a, a
    while i < b:
        if not on[i]:
            j = i
            while j < b and not on[j]: j += 1
            if (j - i) * 0.01 > max_gap:
                segs.append((start, i)); start = j - int(max_gap / 0.01)
            i = j
        else: i += 1
    segs.append((start, b))
    p = int(pad / 0.01)
    return [(max(0, (s - p)) * win, min(n, e + p) * win) for s, e in segs]
def build(order, gaps, default_gap, name, tail=0.0, lead=0.0):
    out, words, lines, cur = [np.zeros(int(lead * SR), np.float32)], [], [], lead
    for k, i in enumerate(order):
        x, meta = load(i)
        if k: 
            g = gaps.get(i, default_gap); out.append(np.zeros(int(g * SR), np.float32)); cur += g
        segs = speech_segments(x)
        t0 = cur; mapping = []
        for s, e in segs:
            piece = x[s:e].copy(); f = int(0.006 * SR)
            piece[:f] *= np.linspace(0, 1, f); piece[-f:] *= np.linspace(1, 0, f)
            mapping.append((s / SR, e / SR, cur)); out.append(piece); cur += (e - s) / SR
        def remap(t):
            for s, e, c in mapping:
                if t < s: return c
                if t <= e: return c + (t - s)
            return cur
        ws = []
        for w in meta["words"]:
            ws.append({"w": w["w"].strip(".,:?!"), "t": round(remap(w["t"]), 3), "e": round(remap(w["t"] + w["d"]), 3), "line": i})
        words += ws
        lines.append({"id": i, "text": meta["text"], "t": round(t0, 3), "e": round(cur, 3), "w0": len(words) - len(ws), "w1": len(words)})
    out.append(np.zeros(int(tail * SR), np.float32))
    y = np.concatenate(out); y = y / np.abs(y).max() * 0.89
    os.makedirs("build", exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", f"build/vo_{name}.wav"], input=y.tobytes(), check=True)
    return {"duration": round(len(y) / SR, 3), "words": words, "lines": lines}
MAIN = ["h1","h2","f3a","f3b","f3c","f3d","m1","f2a","f2b","f2c","f2d","s1","f1a","f1b","f1c","f1d","c1","c2","c3"]
# pausa dramática só antes dos títulos; o resto fica colado (<200ms)
GAPS = {"f3b": 0.30, "f2b": 0.30, "f1b": 0.42, "h2": 0.10, "f3a": 0.16, "f2a": 0.14, "f1a": 0.16, "c1": 0.14}
tl = {"fps": FPS, "main": build(MAIN, GAPS, 0.08, "main", tail=0.10, lead=0.06)}
for h in ["gA", "gB", "gC"]:
    tl[h] = build([h], {}, 0.08, h, lead=0.06)
json.dump(tl, open("public/timeline.json", "w"), ensure_ascii=False, indent=1)
m = tl["main"]
print("duração:", m["duration"], "palavras:", len(m["words"]))
for l in m["lines"]: print(f'{l["id"]:4s} {l["t"]:6.2f}-{l["e"]:6.2f}  {l["text"]}')
for h in ["gA","gB","gC"]: print(h, tl[h]["duration"], [(w["w"], w["t"]) for w in tl[h]["words"]])
