"""Monta a narração: corta silêncios >200ms (mantém as pausas de piada definidas em tts.py),
acelera 1.07x e grava src/timeline.json com o timestamp de cada palavra."""
import json, subprocess, numpy as np
SR, MAXSIL, GAP, SPEED, START, TAIL = 48000, 0.20, 0.07, 1.07, 0.15, 0.35
def load(p): return np.frombuffer(subprocess.check_output(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"]),np.float32).copy()
def silences(x, thr=0.01, win=0.01):
    n=int(win*SR); k=len(x)//n; q=np.sqrt((x[:k*n].reshape(k,n)**2).mean(1))<thr; out=[]; i=0
    while i<k:
        if q[i]:
            j=i
            while j<k and q[j]: j+=1
            out.append((i*win,j*win)); i=j
        else: i+=1
    return out,k*win
d=json.load(open("build/h_tts/frases.json")); chunks=[np.zeros(int(START*SR),np.float32)]; t=START; tl=[]
for i,f in enumerate(d["frases"]):
    x=load(f"build/h_tts/{f['id']}.mp3"); sil,dur=silences(x)
    a=sil[0][1]-0.02 if sil and sil[0][0]==0 else 0.0
    b=sil[-1][0]+0.05 if sil and sil[-1][1]>=dur-0.011 else dur
    cuts=[(s0+MAXSIL/2,s1-MAXSIL/2) for s0,s1 in sil if s0>a and s1<b and s1-s0>MAXSIL]
    def remap(tt):
        r=tt-a
        for c0,c1 in cuts:
            if tt>=c1: r-=c1-c0
            elif tt>c0: r-=tt-c0
        return r
    keep=[];p=a
    for c0,c1 in cuts: keep.append(x[int(p*SR):int(c0*SR)]); p=c1
    keep.append(x[int(p*SR):int(b*SR)]); y=np.concatenate(keep)
    fd=int(.006*SR); y[:fd]*=np.linspace(0,1,fd); y[-fd:]*=np.linspace(1,0,fd)
    if i>0:
        g=max(GAP,f["pausa"]); chunks.append(np.zeros(int(g*SR),np.float32)); t+=g
    w=[{"w":p["w"],"t":t+remap(p["t"]),"e":t+remap(p["t"]+p["d"])} for p in f["palavras"]]
    tl.append({"id":f["id"],"estacao":f["estacao"],"texto":f["texto"],"t0":t,"t1":t+len(y)/SR,"palavras":w}); chunks.append(y); t+=len(y)/SR
chunks.append(np.zeros(int(TAIL*SR),np.float32)); x=np.concatenate(chunks)
subprocess.run(["ffmpeg","-y","-v","error","-f","f32le","-ar",str(SR),"-ac","1","-i","-","-af",f"highpass=f=70,atempo={SPEED},loudnorm=I=-16:TP=-1.5:LRA=9","-ar",str(SR),"build/h_narracao.wav"],input=x.tobytes(),check=True)
S=lambda v: round(v/SPEED,3)
for f in tl:
    f["t0"],f["t1"]=S(f["t0"]),S(f["t1"])
    for w in f["palavras"]: w["t"],w["e"]=S(w["t"]),S(w["e"])
dur=float(subprocess.check_output(["ffprobe","-v","0","-show_entries","format=duration","-of","csv=p=0","build/h_narracao.wav"]))
json.dump({"duracao":round(dur,3),"frases":tl},open("src/timeline.json","w"),ensure_ascii=False,indent=1)
print("duracao",dur)
for f in tl: print(f["id"],f["t0"],f["t1"],f["texto"][:40])
