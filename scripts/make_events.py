"""Deriva os eventos de SFX a partir da timeline (mesma regra de frames usada no Remotion)."""
import json, math
T = json.load(open("public/timeline.json")); FPS = 30
def scene_start(t): return max(0, round(t * FPS) - 3) / FPS
m = T["main"]; L = {l["id"]: l for l in m["lines"]}; W = m["words"]
def w(line, i): return W[L[line]["w0"] + i]["t"]
frames = math.ceil(m["duration"] * FPS)
sfx = [["vhs", 0.0], ["whoosh", 0.05]]
for l in ["h2", "f3a", "f3d", "m1", "f2a", "f2d", "s1", "f1a", "f1d", "c1", "c2", "c3"]: sfx.append(["whoosh", scene_start(L[l]["t"])])
for l in ["f3b", "f2b", "f1b"]: sfx += [["riser", L[l]["t"]], ["thud", L[l]["t"]]]
for line, i in [("h1", 1), ("h1", 6), ("h2", 5), ("f3a", 0), ("f3c", 3), ("f3d", 2), ("m1", 3), ("f2a", 0), ("f2c", 3), ("f2d", 1), ("s1", 5), ("f1a", 0), ("f1c", 0), ("f1c", 5), ("f1d", 1), ("c1", 0), ("c2", 3), ("c2", 5), ("c3", 0), ("c3", 2)]:
    sfx.append(["pop", w(line, i)])
ev = {"main": {"frames": frames, "duration": frames / FPS, "sfx": sfx}}
for h in ["gA", "gB", "gC"]:
    hw = T[h]["words"]
    ev[h] = {"frames": 90, "duration": 3.0, "sfx": [["vhs", 0.0], ["whoosh", 0.05], ["pop", hw[1]["t"]], ["thud", hw[-1]["t"]], ["pop", 2.55]]}
json.dump(ev, open("public/events.json", "w"), indent=1)
print("frames", frames)
