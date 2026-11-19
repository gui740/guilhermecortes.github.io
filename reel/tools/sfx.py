"""Efeitos sintetizados: fita entrando no videocassete, cortina de tiras plásticas, chuvisco, impacto grave."""
import numpy as np,soundfile as sf
from scipy.signal import butter,sosfilt,fftconvolve
SR=48000; rng=np.random.default_rng(9)
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def add(buf,sig,t,g=1):
    s=int(t*SR); e=min(len(buf),s+len(sig)); buf[s:e]+=sig[:e-s]*g
def room(x,sec=0.6,mix=0.25):
    n=int(sec*SR); t=np.arange(n)/SR; ir=lp(rng.standard_normal(n),5000)*np.exp(-t*7/sec); ir/=np.sqrt((ir**2).sum())
    return x*(1-mix)+fftconvolve(x,ir)[:len(x)]*mix
def click(n_ms,f,dec,amp=1):
    n=int(n_ms/1000*SR); t=np.arange(n)/SR
    return (bp(rng.standard_normal(n),f*0.6,min(f*1.8,20000))*0.7+np.sin(2*np.pi*f*t)*0.5)*np.exp(-t*dec)*amp
# VHS insert
v=np.zeros(int(1.9*SR))
add(v,click(40,2200,140,0.8),0.00)                       # flap
n=int(0.32*SR); t=np.arange(n)/SR; add(v,bp(rng.standard_normal(n),600,3000)*np.sin(np.pi*t/0.32)**2*0.25,0.03)  # slide
add(v,click(90,180,40,1.4)+np.pad(click(25,3200,200,0.7),(0,int(0.065*SR))),0.36)     # clunk
n=int(0.95*SR); t=np.arange(n)/SR; f=55+25*np.clip(t/0.4,0,1)
ph=2*np.pi*np.cumsum(f)/SR; mot=(np.sin(ph)+0.5*np.sin(2*ph)+0.3*np.sin(3*ph))*0.18
mot=lp(mot+bp(rng.standard_normal(n),200,900)*0.05,1500)*np.clip(t/0.08,0,1)*np.clip((0.95-t)/0.2,0,1)
add(v,mot,0.48); add(v,click(30,1500,180,0.6),1.42); add(v,click(30,900,200,0.4),1.55)
v=room(v,0.5,0.2); v/=np.abs(v).max(); sf.write('assets/audio/sfx_vhs.wav',(v*0.9).astype(np.float32),SR)
# plastic strip curtain
c=np.zeros(int(1.2*SR))
n=int(0.9*SR); t=np.arange(n)/SR; add(c,lp(rng.standard_normal(n),900)*np.sin(np.pi*t/0.9)**3*0.35,0.0)  # whoosh
for i in range(22):
    tt=0.18+rng.random()*0.55; m=int(rng.uniform(0.03,0.08)*SR); tm=np.arange(m)/SR
    f0=rng.uniform(1500,4500); s=bp(rng.standard_normal(m),f0*0.7,f0*1.4)*np.exp(-tm*rng.uniform(40,90))
    add(c,s*rng.uniform(0.25,0.6),tt)
c=room(c,0.4,0.2); c/=np.abs(c).max(); sf.write('assets/audio/sfx_curtain.wav',(c*0.8).astype(np.float32),SR)
# TV static loop 3s
n=3*SR; s=bp(rng.standard_normal(n),1200,8000)*0.4
cr=np.zeros(n); idx=rng.integers(0,n,400); cr[idx]=rng.uniform(-1,1,400); s+=hp(cr,2000)*0.5
s*=0.85+0.15*np.sin(2*np.pi*60*np.arange(n)/SR)
fade=int(0.05*SR); s[:fade]*=np.linspace(0,1,fade); s[-fade:]*=np.linspace(1,0,fade)
s/=np.abs(s).max(); sf.write('assets/audio/sfx_static.wav',(s*0.6).astype(np.float32),SR)
# low impact
n=int(2.6*SR); t=np.arange(n)/SR; f=30+40*np.exp(-t*9); ph=2*np.pi*np.cumsum(f)/SR
im=np.sin(ph)*np.exp(-t*2.2)*1.0+lp(rng.standard_normal(n),400)*np.exp(-t*10)*0.6+bp(rng.standard_normal(n),80,2500)*np.exp(-t*30)*0.35
im=np.tanh(im*1.3); im=room(im,1.8,0.3); im/=np.abs(im).max(); sf.write('assets/audio/sfx_impact.wav',(im*0.95).astype(np.float32),SR)
print('sfx ok')
