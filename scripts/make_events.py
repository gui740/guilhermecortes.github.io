"""Deriva os eventos de áudio (SFX + marcações da trilha) a partir da timeline.
Usa a mesma regra de frames do Remotion, então som e imagem batem."""
import json, math
T = json.load(open("public/timeline.json")); FPS = 30
def scene_start(t): return max(0, round(t * FPS) - 3) / FPS
m = T["main"]; L = {l["id"]: l for l in m["lines"]}; W = m["words"]
def w(line, i): return W[L[line]["w0"] + i]["t"]
frames = math.ceil(m["duration"] * FPS)
sfx = [["tape_start", 0.0], ["whoosh", 0.05]]
# cortes entre cenas: whoosh nas viradas grandes, glitch nos cortes secos dentro do mesmo filme
for l in ["h2", "a1", "m1", "b1", "s1", "c1", "e1", "e2", "e4"]: sfx.append(["whoosh", scene_start(L[l]["t"])])
for l in ["a3", "a5", "a6", "b3", "b4", "b5", "b6", "c4", "c5", "c6"]: sfx.append(["glitch", scene_start(L[l]["t"])])
for l in ["a2", "b2", "c3"]: sfx += [["riser", L[l]["t"]], ["impact", L[l]["t"]]]
sfx.append(["tape_stop", L["a4"]["t"] - 0.12])
for line, i in [("h1", 1), ("b3", 2), ("c4", 4), ("c6", 4)]: sfx.append(["rec", w(line, i)])
for l in ["a7", "b7", "c7"]: sfx += [["whoosh", scene_start(L[l]["t"])], ["ding", w(l, 2)]]
sfx += [["send", w("s1", 0)], ["save", w("e1", 0) + 0.2], ["bubble", w("e3", 0)]]
for line, i in [("h1", 7), ("h2", 6), ("a3", 4), ("a5", 12), ("a6", 3), ("m1", 4), ("b3", 8), ("b4", 5), ("b5", 5), ("b6", 3), ("s1", 7), ("c4", 8), ("c5", 3), ("c6", 6), ("e2", 6), ("e4", 3)]:
    sfx.append(["tick", w(line, i)])
# a trilha recomeça no tempo forte em cada título; pára um pouco antes (pausa dramática) e no "e somem"
music = {"segments": [[0.0, L["a2"]["t"] - 0.34], [L["a2"]["t"], L["a4"]["t"] - 0.10], [L["a5"]["t"] - 0.05, L["b2"]["t"] - 0.34],
                      [L["b2"]["t"], L["c3"]["t"] - 0.38], [L["c3"]["t"], frames / FPS]], "tape_stop": [1]}
ev = {"main": {"frames": frames, "duration": frames / FPS, "sfx": sfx, "music": music}}
for h in ["gA", "gB", "gC"]:
    hw = T[h]["words"]
    ev[h] = {"frames": 90, "duration": 3.0, "sfx": [["tape_start", 0.0], ["whoosh", 0.05], ["rec", hw[1]["t"]], ["tick", hw[-1]["t"]], ["impact", 2.5]], "music": {"segments": [[0.0, 3.0]], "tape_stop": []}}
json.dump(ev, open("public/events.json", "w"), indent=1)
print("frames", frames)
