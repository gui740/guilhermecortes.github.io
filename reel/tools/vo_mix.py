import json,sys,numpy as np,soundfile as sf,subprocess
import pyloudnorm as pyln
tl=sys.argv[1]; out=sys.argv[2]
T=json.load(open(tl)); SR=48000; N=int((T['end']+0.2)*SR)
mix=np.zeros(N,np.float32); rng=np.random.default_rng(7)
def breath(at):
    n=int(0.32*SR); w=rng.standard_normal(n).astype(np.float32)
    # band-limit noise ~ breath (simple one-pole filters)
    for _ in range(3): w=np.convolve(w,np.ones(9)/9,'same')
    w-=np.convolve(w,np.ones(80)/80,'same')
    env=np.sin(np.linspace(0,np.pi,n))**2
    s=int(at*SR); e=min(N,s+n); mix[s:e]+=(w*env*0.012)[:e-s]
for v in T['vo']:
    a,sr=sf.read(f"assets/vo/trim/{v['clip']}.wav",dtype='float32'); assert sr==SR
    s=int(v['start']*SR); mix[s:s+len(a)]+=a[:N-s]
    if v['key'] in('f3a','f2a','f1a','fe1'): breath(v['start']-0.38)
sf.write('/tmp/claude-0/vo_dry.wav',mix,SR)
# EQ + leve compressão + room tone
subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/claude-0/vo_dry.wav','-f','lavfi','-i',f'anoisesrc=color=pink:amplitude=0.0009:r={SR}:d={N/SR}',
 '-filter_complex','[0]highpass=f=85,equalizer=f=220:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=2,equalizer=f=9000:t=q:w=1:g=-1.5,acompressor=threshold=-22dB:ratio=2.2:attack=12:release=140:makeup=2[v];[1]lowpass=f=3000[r];[v][r]amix=inputs=2:normalize=0[o]','-map','[o]','-ar',str(SR),'-ac','1','/tmp/claude-0/vo_proc.wav'],check=True)
a,sr=sf.read('/tmp/claude-0/vo_proc.wav',dtype='float32')
m=pyln.Meter(sr); L0=m.integrated_loudness(a); g=0.0
for it in range(4):
    sf.write('/tmp/claude-0/vo_g.wav',a*10**((g+(-16-L0))/20),sr)
    subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/claude-0/vo_g.wav','-af','alimiter=limit=0.84:attack=3:release=60:level=disabled','/tmp/claude-0/vo_l.wav'],check=True)
    b,_=sf.read('/tmp/claude-0/vo_l.wav',dtype='float32'); L=m.integrated_loudness(b)
    if abs(L+16)<0.15: break
    g+=(-16-L)
sf.write(out,b,sr); print('LUFS',round(L,2),'peak',round(float(np.abs(b).max()),3))
