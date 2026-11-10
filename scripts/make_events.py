"""Deriva os eventos de SFX a partir da timeline (mesma regra de frames usada no Remotion)."""
import json, math
T = json.load(open("public/timeline.json")); FPS = 30
def scene_start(t): return max(0, round(t * FPS) - 3) / FPS
m = T["main"]; L = {l["id"]: l for l in m["lines"]}; W = m["words"]
def w(line, i): return W[L[line]["w0"] + i]["t"]
frames = math.ceil(m["duration"] * FPS)
sfx = [["vhs", 0.0], ["whoosh", 0.05]]
for l in ["h2","a1","a3","a4","a5","a6","a7","m1","b1","b3","b4","b5","b6","b7","s1","c1","c4","c5","c6","c7","e1","e2","e4"]: sfx.append(["whoosh", scene_start(L[l]["t"])])
for l in ["a2", "b2", "c3"]: sfx += [["riser", L[l]["t"]], ["thud", L[l]["t"]]]
for line, i in [("h1",1),("h1",7),("h2",6),("a1",0),("a3",4),("a4",1),("a5",1),("a5",12),("a6",3),("a7",2),("m1",4),("b1",0),("b3",5),("b3",8),("b4",1),("b4",5),("b5",5),("b6",3),("b7",2),("s1",0),("s1",7),("c1",2),("c4",4),("c4",8),("c5",3),("c6",4),("c7",2),("e1",0),("e2",6),("e3",0),("e4",1),("e4",3)]:
    sfx.append(["pop", w(line, i)])
ev = {"main": {"frames": frames, "duration": frames / FPS, "sfx": sfx}}
for h in ["gA", "gB", "gC"]:
    hw = T[h]["words"]
    ev[h] = {"frames": 90, "duration": 3.0, "sfx": [["vhs", 0.0], ["whoosh", 0.05], ["pop", hw[1]["t"]], ["thud", hw[-1]["t"]], ["pop", 2.55]]}
json.dump(ev, open("public/events.json", "w"), indent=1)
print("frames", frames)
