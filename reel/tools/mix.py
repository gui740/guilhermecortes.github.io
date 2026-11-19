import numpy as np,soundfile as sf,json,sys,subprocess
import pyloudnorm as pyln
from scipy.ndimage import uniform_filter1d
tl,voice,out=sys.argv[1],sys.argv[2],sys.argv[3]
T=json.load(open(tl)); SR=48000; N=int((T['end'])*SR)
def rd(f):
    a,sr=sf.read(f,dtype='float32'); assert sr==SR
    if a.ndim==1: a=np.stack([a,a],1)
    b=np.zeros((N,2),np.float32); b[:min(N,len(a))]=a[:N]; return b
V=rd(voice); st={k:rd(f'assets/audio/stem_{k}.wav') for k in['drums','bass','pad','arp']}
t=np.arange(N)/SR
# arp only in stations/travessias (not gancho/outro)
arp_g=np.zeros(N)
for s in T['stations']: arp_g[(t>=s['numberIn'])&(t<s['end'])]=1
arp_g=uniform_filter1d(arp_g,int(0.4*SR))
music=st['drums']+st['bass']*0.9+st['pad']*0.8+st['arp']*arp_g[:,None]*0.7
m=pyln.Meter(SR)
Lm=m.integrated_loudness(music); under_db=-31.5-Lm   # música ~18 dB abaixo da voz durante a fala
g=np.full(N,under_db)
def up(a,b,db=7):
    g[(t>=a)&(t<b)]=under_db+db
up(T['vo'][0]['end']+0.1,T['hookEnd']+1.5,6)
for tr in T['travs']: up(tr['start'],tr['end'],5)
for s in T['stations']:
    up(s['titleIn']+0.75,s['bIn']-0.05,7); up(s['logoIn'],s['end'],8)
up(T['vo'][-1]['end'],T['end'],3)
# sidechain extra duck where voice present
ve=uniform_filter1d(np.abs(V[:,0]),int(0.05*SR)); vgate=(ve>0.01).astype(float); vgate=uniform_filter1d(vgate,int(0.25*SR))
gl=10**(g/20); gl=uniform_filter1d(gl,int(0.18*SR))*(1-0.3*vgate)
# silence before film 1 title: total silence
sil=np.ones(N)
for s in T['stations']:
    if 'silence' in s:
        a,b=s['silence']; sil[(t>=a-0.12)&(t<b)]=0
        # music comes back on the reveal
silk=uniform_filter1d(sil,int(0.06*SR))
mix=music*(gl*silk)[:,None]
# intro fade-in
mix*=np.clip(t/0.6,0,1)[:,None]
def place(f,at,db):
    a,_=sf.read(f'assets/audio/{f}.wav',dtype='float32'); s=int(at*SR); e=min(N,s+len(a))
    if s<N: mix[s:e]+=(a[:e-s]*10**(db/20))[:,None]
place('sfx_vhs',0.0,-10); place('sfx_vhs',T['diveStart']-0.2,-12)
for tr in T['travs']: place('sfx_curtain',tr['start']+0.55,-14)
for s in T['stations']: place('sfx_impact',s['titleIn'],-9 if s['n']!='1' else -6)
stat,_=sf.read('assets/audio/sfx_static.wav',dtype='float32'); loop=np.tile(stat,int(N/len(stat))+1)[:N]
mix+=(loop*10**(-40/20)*silk)[:,None]
mix=mix*silk[:,None]+V*1.0
sf.write('/tmp/claude-0/mix_pre.wav',mix,SR)
subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/claude-0/mix_pre.wav','-af','alimiter=limit=0.89:attack=2:release=50:level=disabled','-ar','48000',out],check=True)
a,_=sf.read(out); print('mix LUFS',round(m.integrated_loudness(a),2),'peak',round(float(np.abs(a).max()),3),'music under gain dB',round(under_db,1))
