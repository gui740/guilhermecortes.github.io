"""Split a full-narration take into per-line wavs using Whisper word timestamps."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import timeline as TL, align, vo

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
lines = [l for l in TL.LINES if l[0] != "L07B"]
caps = []
for l in lines:
    for w in l[2].split():
        caps.append((l[0], w))
ww = align.words(src, prompt=" ".join(l[2] for l in lines))
print("heard:", " ".join(w["w"] for w in ww))
# align whole sequence
import difflib
a = [vo.norm(w) for _, w in caps]
b = [vo.norm(x["w"]) for x in ww]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
m = [None] * len(caps)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ("equal", "replace"):
        for k in range(min(i2 - i1, j2 - j1)):
            m[i1 + k] = ww[j1 + k]
bounds = {}
for lid, _, _, _ in lines:
    idx = [i for i, (l, _) in enumerate(caps) if l == lid and m[i]]
    bounds[lid] = (m[idx[0]]["s"], m[idx[-1]]["e"])
ids = [l[0] for l in lines]
for k, lid in enumerate(ids):
    s, e = bounds[lid]
    s0 = (bounds[ids[k - 1]][1] + s) / 2 if k else max(0, s - 0.2)
    e0 = (e + bounds[ids[k + 1]][0]) / 2 if k + 1 < len(ids) else e + 0.4
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ss", str(s0), "-to", str(e0),
                    os.path.join(outdir, lid + "_raw.wav")], check=True)
    print(lid, round(e - s, 2))
