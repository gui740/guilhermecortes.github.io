import json,sys,soundfile as sf
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
T=json.load(open(sys.argv[1])); out=[]
for v in T['vo']:
    a,sr=sf.read(f"assets/vo/trim/{v['clip']}.wav",dtype='float32')
    import numpy as np
    a16=np.interp(np.linspace(0,len(a)-1,int(len(a)*16000/sr)),np.arange(len(a)),a).astype('float32')
    segs,_=m.transcribe(a16,language="pt",word_timestamps=True)
    for s in segs:
        for w in s.words: out.append(dict(key=v['key'],w=w.word.strip(),s=round(v['start']+w.start,3),e=round(v['start']+w.end,3)))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
print(' '.join(f"{x['w']}@{x['s']}" for x in out))
