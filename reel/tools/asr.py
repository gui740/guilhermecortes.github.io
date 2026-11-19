import sys,json,soundfile as sf,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device="cpu",compute_type="int8")
def load(f):
    a,sr=sf.read(f,dtype='float32')
    if a.ndim>1:a=a.mean(1)
    if sr!=16000:
        import math
        n=int(len(a)*16000/sr); a=np.interp(np.linspace(0,len(a)-1,n),np.arange(len(a)),a).astype('float32')
    return a
if sys.argv[2]=='--json':
    segs,_=m.transcribe(load(sys.argv[3]),language="pt",word_timestamps=True,initial_prompt=sys.argv[5] if len(sys.argv)>5 else None)
    json.dump([dict(w=w.word.strip(),s=round(w.start,3),e=round(w.end,3)) for s in segs for w in s.words],open(sys.argv[4],'w'),ensure_ascii=False,indent=0)
else:
  for f in sys.argv[2:]:
    segs,_=m.transcribe(load(f),language="pt",word_timestamps=True)
    print(f.split('/')[-1],'|',' '.join(w.word.strip() for s in segs for w in s.words))
