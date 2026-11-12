# Timestamps por palavra via faster-whisper; os textos são re-alinhados ao roteiro (grafia correta).
import json, sys, re, os, difflib
from faster_whisper import WhisperModel
wav=sys.argv[1]; lines=json.load(open(sys.argv[2])); out=sys.argv[3]
script=' '.join(l['text'] for l in lines)
m=WhisperModel('small',device='cpu',compute_type='int8')
import subprocess, numpy as np
pcm=subprocess.run(['ffmpeg','-v','error','-i',wav,'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
audio=np.frombuffer(pcm,np.int16).astype(np.float32)/32768
segs,_=m.transcribe(audio,language='pt',word_timestamps=True,initial_prompt=script,beam_size=5)
W=[(w.word.strip(),w.start,w.end) for s in segs for w in s.words]
norm=lambda s: re.sub(r'[^\wà-ú]','',s.lower())
ref=script.split()
a=[norm(x[0]) for x in W]; b=[norm(x) for x in ref]
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
res=[None]*len(ref)
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=='equal':
        for k in range(i2-i1): res[j1+k]=(W[i1+k][1],W[i1+k][2])
    elif tag=='replace' and i2>i1:
        t0,t1=W[i1][1],W[i2-1][2]; n=j2-j1
        for k in range(n): res[j1+k]=(t0+(t1-t0)*k/n, t0+(t1-t0)*(k+1)/n)
# interpola faltantes
for j in range(len(ref)):
    if res[j] is None:
        p=next((res[k][1] for k in range(j-1,-1,-1) if res[k]),0); 
        n=next((res[k][0] for k in range(j+1,len(ref)) if res[k]),p+0.3)
        res[j]=(p,(p+n)/2 if n>p else p+0.15)
# marca a qual linha pertence
o=[];j=0
for li,l in enumerate(lines):
    for w in l['text'].split():
        o.append({'w':w,'s':round(res[j][0],3),'e':round(res[j][1],3),'line':l['id']}); j+=1
json.dump(o,open(out,'w'),ensure_ascii=False,indent=0)
print('whisper:',' '.join(x[0] for x in W))
for x in o: print(f"{x['s']:6.2f} {x['e']:6.2f} {x['line']:6} {x['w']}")
