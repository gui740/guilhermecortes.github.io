"""Monta a narração: corta silêncios (>200ms), pausa dramática antes de cada título,
recalcula timestamps por palavra e gera public/timeline.json + build/vo_<nome>.wav."""
import json, os, subprocess, sys, numpy as np
SR = 48000
FPS = 30
def load(i):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"assets/vo/{i}.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy(), json.load(open(f"assets/vo/{i}.json"))
def speech_segments(x, thr_db=-42, max_gap=0.28, pad=0.03):
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
MAIN = ["h1","h2","a1","a2","a3","a4","a5","a6","a7","m1","b1","b2","b3","b4","b5","b6","b7","s1","c1","c2","c3","c4","c5","c6","c7","e1","e2","e3","e4"]
# respiro entre frases; pausa dramática antes de cada título e um tempo depois dele para dar pra ver o filme
T_PAUSE, T_HOLD = 0.42, 0.50
GAPS = {"h2": 0.22, "a1": 0.40, "a2": T_PAUSE, "a3": T_HOLD, "a4": 0.30, "a5": 0.38, "a6": 0.30, "a7": 0.40, "m1": 0.45,
        "b1": 0.40, "b2": T_PAUSE, "b3": T_HOLD, "b4": 0.14, "b5": 0.34, "b6": 0.30, "b7": 0.45, "s1": 0.45,
        "c1": 0.45, "c2": 0.12, "c3": 0.50, "c4": T_HOLD, "c5": 0.16, "c6": 0.34, "c7": 0.42,
        "e1": 0.45, "e2": 0.30, "e3": 0.22, "e4": 0.30}
tl = {"fps": FPS, "main": build(MAIN, GAPS, 0.2, "main", tail=0.12, lead=0.06)}
for h in ["gA", "gB", "gC"]:
    tl[h] = build([h], {}, 0.08, h, lead=0.06)
json.dump(tl, open("public/timeline.json", "w"), ensure_ascii=False, indent=1)
m = tl["main"]
print("duração:", m["duration"], "palavras:", len(m["words"]))
for l in m["lines"]: print(f'{l["id"]:4s} {l["t"]:6.2f}-{l["e"]:6.2f}  {l["text"]}')
for h in ["gA","gB","gC"]: print(h, tl[h]["duration"], [(w["w"], w["t"]) for w in tl[h]["words"]])
