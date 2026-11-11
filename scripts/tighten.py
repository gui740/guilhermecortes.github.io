"""Segunda passada: corta respirações/silêncios residuais > 200ms (após o speed-up),
preservando as pausas dramáticas listadas em KEEP (tempo aproximado -> duração mantida)."""
import sys, numpy as np, soundfile as sf
src, dst = sys.argv[1], sys.argv[2]
KEEP = {7.8: 0.30, 30.9: 0.28}   # antes de "É Buddy" (título) e antes de "5 milhões" (números)
a, sr = sf.read(src, dtype="float32"); h = sr//100
e = 20*np.log10(np.sqrt((a[:len(a)//h*h].reshape(-1, h)**2).mean(1))+1e-9)
quiet = e < -38
out = []; i = 0; n = len(quiet); last = 0
while i < n:
    if quiet[i]:
        j = i
        while j < n and quiet[j]: j += 1
        dur = (j-i)/100
        if dur > 0.20:
            keep = next((v for t, v in KEEP.items() if i/100-0.3 <= t <= j/100+0.3), 0.06)
            out.append(a[last*h:i*h + int(0.02*sr)])
            fill = int(max(0, keep-0.04)*sr)
            out.append(np.zeros(fill, np.float32))
            last = j - 2
        i = j
    else: i += 1
out.append(a[last*h:])
# crossfade simples nas emendas
y = np.concatenate(out)
sf.write(dst, y, sr)
print(f"{len(a)/sr:.2f}s -> {len(y)/sr:.2f}s")
