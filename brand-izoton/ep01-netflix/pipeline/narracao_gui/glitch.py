import subprocess, numpy as np, sys
for f in sys.argv[1:]:
    out = subprocess.run(['ffmpeg','-v','error','-i',f,'-vf','scale=160:90,format=gray','-f','rawvideo','-'], capture_output=True).stdout
    a = np.frombuffer(out, np.uint8).reshape(-1,90,160).astype(float)
    g = []
    for i in range(1, len(a)-1):
        p, n, pn = [np.abs(x-y).mean() for x, y in ((a[i],a[i-1]), (a[i],a[i+1]), (a[i-1],a[i+1]))]
        if p > 3 and n > 3 and pn < min(p, n) / 2: g.append((i, round(p,1), round(pn,1)))
    print(f.split('/')[-1], 'quadros isolados:', g)
