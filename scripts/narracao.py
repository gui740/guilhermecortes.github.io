"""Monta a narração: corta silêncios >250ms, mantém pausas dramáticas, normaliza em -16 LUFS
e grava build/timeline.json com o timestamp de cada palavra."""
import json, subprocess, numpy as np, sys
SR = 48000
MAXSIL = 0.25
GAP = 0.14                                   # pausa padrão entre frases
GAPS = {"c1c": 0.50, "c2b": 0.42, "c6b": 0.42,   # pausa antes de "não" e de "Denuncie"
        "c8a": 1.85, "c9a": 0.30}              # c8a: segura URL + telefones na tela
START = 0.20
def load(p):
    raw = subprocess.check_output(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"])
    return np.frombuffer(raw, np.float32).copy()
def silences(x, thr=0.012, win=0.01):
    n = int(win*SR); k = len(x)//n
    rms = np.sqrt((x[:k*n].reshape(k,n)**2).mean(1)); q = rms < thr
    out=[]; i=0
    while i<k:
        if q[i]:
            j=i
            while j<k and q[j]: j+=1
            out.append((i*win, j*win)); i=j
        else: i+=1
    return out, k*win
d = json.load(open("build/tts/frases.json"))
chunks=[]; t=START; tl=[]; chunks.append(np.zeros(int(START*SR),np.float32))
for i,f in enumerate(d["frases"]):
    x = load(f"build/tts/{f['id']}.mp3")
    sil, dur = silences(x)
    a = sil[0][1]-0.03 if sil and sil[0][0]==0 else 0.0
    b = sil[-1][0]+0.06 if sil and sil[-1][1]>=dur-0.011 else dur
    # mapa de tempo: remove o excesso de cada silêncio interno
    cuts=[(s0+MAXSIL/2, s1-MAXSIL/2) for s0,s1 in sil if s0>a and s1<b and s1-s0>MAXSIL]
    def remap(tt):
        r=tt-a
        for c0,c1 in cuts:
            if tt>=c1: r-=c1-c0
            elif tt>c0: r-=tt-c0
        return r
    keep=[]; p=a
    for c0,c1 in cuts: keep.append(x[int(p*SR):int(c0*SR)]); p=c1
    keep.append(x[int(p*SR):int(b*SR)])
    y=np.concatenate(keep); fd=int(0.008*SR); y[:fd]*=np.linspace(0,1,fd); y[-fd:]*=np.linspace(1,0,fd)
    if i>0:
        g=GAPS.get(f["id"],GAP); chunks.append(np.zeros(int(g*SR),np.float32)); t+=g
    words=[{"w":w["w"],"t":round(t+remap(w["t"]),3),"e":round(t+remap(w["t"]+w["d"]),3)} for w in f["palavras"]]
    tl.append({"id":f["id"],"cena":f["cena"],"t0":round(t,3),"t1":round(t+len(y)/SR,3),"palavras":words})
    chunks.append(y); t+=len(y)/SR
chunks.append(np.zeros(int(0.7*SR),np.float32))
x=np.concatenate(chunks)
p=subprocess.run(["ffmpeg","-y","-v","error","-f","f32le","-ar",str(SR),"-ac","1","-i","-",
   "-af","highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11","-ar",str(SR),"build/narracao.wav"],input=x.tobytes())
json.dump({"duracao":round(len(x)/SR,3),"frases":tl},open("build/timeline.json","w"),ensure_ascii=False,indent=1)
print("duracao",len(x)/SR)
for f in tl: print(f["id"],f["t0"],f["t1"])
open("reel/timeline.js","w").write("window.TL = "+json.dumps({"duracao":round(len(x)/SR,3),"frases":tl},ensure_ascii=False)+";\n")
