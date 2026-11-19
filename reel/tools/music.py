"""Trilha original: synthwave sombrio, 92 BPM, Ré menor. Gera stems separados (drums/bass/pad/arp)."""
import numpy as np,soundfile as sf,json,sys
from scipy.signal import butter,sosfilt,fftconvolve
SR=48000; T=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'src/timeline.json'))
L=T['end']+1.5; N=int(L*SR); BPM=92; beat=60/BPM; rng=np.random.default_rng(5)
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def note(n): return 440*2**((n-69)/12)
def add(buf,sig,t,g=1.0):
    s=int(t*SR); e=min(len(buf),s+len(sig))
    if s<len(buf) and e>s: buf[s:e]+=sig[:e-s]*g
def env(n,a,d,s=0.0,r=0.0,sl=1.0):
    t=np.arange(n)/SR; e=np.where(t<a,t/max(a,1e-4),np.exp(-(t-a)/max(d,1e-4))*(1-s)+s)
    return e
def saw(f,n,ph=0): t=np.arange(n)/SR; return 2*((t*f+ph)%1)-1
# sections (intensity 0..1 for drums)
st=T['stations']; hookEnd=T['hookEnd']
def drum_level(t):
    if t<hookEnd-0.2: return 0.0
    for s in st:
        if 'silence' in s and s['silence'][0]-0.25<=t<s['titleIn']: return 0.0
    if t>=T['outroStart']+0.2: return 0.35
    for tr in T['travs']:
        if tr['start']<=t<tr['end']: return 1.0
    return 0.6
drums=np.zeros(N); bass=np.zeros(N); pad=np.zeros((N,)); arp=np.zeros(N)
kick=None
def mkkick():
    n=int(0.45*SR); t=np.arange(n)/SR; f=45+80*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    k=np.sin(ph)*np.exp(-t*7.5); k[:int(0.004*SR)]+=rng.standard_normal(int(0.004*SR))*0.3
    return np.tanh(k*1.6)
def mksnare():
    n=int(0.32*SR); t=np.arange(n)/SR; nz=bp(rng.standard_normal(n),900,7000)*np.exp(-t*16)
    tone=np.sin(2*np.pi*185*t)*np.exp(-t*25)*0.6; return (nz*0.8+tone)
def mkhat(open_=False):
    n=int((0.18 if open_ else 0.05)*SR); t=np.arange(n)/SR; return hp(rng.standard_normal(n),7500,4)*np.exp(-t*(14 if open_ else 70))
K=mkkick(); S=mksnare(); H=mkhat(); HO=mkhat(True)
nb=int(L/beat)+1
for b in range(nb):
    t=b*beat; lv=drum_level(t)
    if lv<=0: continue
    if b%4 in(0,) or (b%4==2 and lv>0.8) or (b%8==7 and lv>0.8): add(drums,K,t,0.9*lv)
    if b%4 in(1,3) and lv>0.5: add(drums,S,t,0.45*lv)
    for k in range(2):
        th=t+k*beat/2+(0.018 if k==1 else 0)
        if drum_level(th)>0: add(drums,H if (b*2+k)%8!=7 else HO,th,(0.16 if k==0 else 0.22)*lv)
# chord progression Dm Bb Gm A (2 bars each)
prog=[(50,[62,65,69]),(46,[58,62,65]),(43,[55,58,62]),(45,[57,61,64])]
bar=4*beat
for b in range(int(L/bar)+1):
    root,ch=prog[(b//2)%4]; t0=b*bar
    # bass: 8ths, octave jumps
    for i in range(8):
        t=t0+i*beat/2; n=int(beat/2*SR*0.92)
        f=note(root-12+(12 if i%4==3 else 0))
        s=(saw(f,n)+saw(f*1.004,n))*0.5; fe=np.exp(-np.arange(n)/SR*9); s=(lp(s,900,2)*fe+lp(s,320,2)*(1-fe))*env(n,0.004,0.22,0.35)
        add(bass,s,t,0.55)
    # pad: whole chord, 2 bars, slow attack
    if b%2==0:
        n=int(bar*2*SR)+SR//2
        p=np.zeros(n)
        for m in ch+[root]:
            for d in(-0.11,0,0.09): p+=saw(note(m)*2**(d/12),n,rng.random())
        t=np.arange(n)/SR; e=np.clip(t/1.2,0,1)*np.clip((bar*2+0.5-t)/0.6,0,1)
        p=lp(p,1100,2)*e/12; add(pad,p,t0)
    # arp: 16ths pluck, chord tones up
    seq=[ch[0],ch[1],ch[2],ch[1]+12,ch[2],ch[1],ch[0]+12,ch[2]]
    for i in range(16):
        t=t0+i*beat/4; n=int(beat/4*SR); f=note(seq[i%8]+0)
        sq=np.sign(np.sin(2*np.pi*f*np.arange(n)/SR))*0.5+saw(f,n)*0.5
        add(arp,lp(sq,2400,2)*env(n,0.002,0.06),t,0.18)
def reverb(x,sec=2.4,mix=0.25,seed=0):
    r=np.random.default_rng(seed); n=int(sec*SR); t=np.arange(n)/SR
    ir=r.standard_normal((n,2))*np.exp(-t*3.2/sec*2.3)[:,None]; ir=np.stack([lp(ir[:,0],6000),lp(ir[:,1],6000)],1)
    ir/=np.sqrt((ir**2).sum(0)); wet=np.stack([fftconvolve(x,ir[:,c])[:len(x)] for c in range(2)],1)
    dry=np.stack([x,x],1); return dry*(1-mix)+wet*mix
out={'drums':reverb(drums,1.2,0.15,1),'bass':reverb(bass,1.0,0.08,2),'pad':reverb(pad,3.5,0.45,3),'arp':reverb(arp,2.5,0.4,4)}
# arp ping-pong-ish stereo
out['arp'][:,0]*=0.8; 
for k,v in out.items():
    v=v/ (np.abs(v).max()+1e-9)*0.7; sf.write(f'assets/audio/stem_{k}.wav',v.astype(np.float32),SR); print(k,v.shape)
