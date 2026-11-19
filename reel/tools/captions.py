"""Legenda: texto do roteiro (grafia certa) + tempo por palavra do Whisper. Blocos de até 4 palavras."""
import json,sys,re,unicodedata
tl=json.load(open(sys.argv[1])); words=json.load(open(sys.argv[2])); out=sys.argv[3]
lines={}
for l in open('src_vo_lines.tsv'):
    if l.strip(): k,t=l.rstrip('\n').split('\t'); lines[k]=t
hook=sys.argv[4] if len(sys.argv)>4 else 'g'
lines['g']=lines[hook] if hook in lines else lines['g']
caps=[]
for v in tl['vo']:
    txt=lines[v['key']].replace('...',' … ').replace('…',' ')
    sw=[w for w in txt.split() if re.search(r'\w',w)]
    ww=[w for w in words if w['key']==v['key']]
    n=len(sw)
    if not ww: ww=[{'s':v['start'],'e':v['end']}]
    # mapeia palavra i do roteiro -> intervalo proporcional nos timestamps do Whisper
    def t_at(i,end=False):
        if len(ww)==n: return ww[i]['e'] if end else ww[i]['s']
        f=(i+(1 if end else 0))/n; j=min(len(ww)-1,int(f*len(ww)-(1e-6 if end else 0)))
        return ww[j]['e'] if end else ww[j]['s']
    FUNC={'no','na','de','do','da','a','o','e','uma','um','que','te','seu','sua','pra','em','as','os','até','como','cê','ele','mas'}
    raw=lines[v['key']].replace('…','...')
    pause_after=set(); idx=0
    for tok in re.findall(r'\.\.\.|[^\s]+',raw):
        if tok=='...': pause_after.add(idx-1); continue
        if re.search(r'\w',tok):
            idx+=1
            if tok.endswith('...'): pause_after.add(idx-1)
    chunk=[]
    for i,w in enumerate(sw):
        chunk.append(i)
        end_here = i==n-1 or i in pause_after or re.search(r'[.?!,]$',w)
        if not end_here and len(chunk)>=3:
            # não termina bloco em palavra de ligação
            if w.lower() in FUNC and len(chunk)<4: continue
            end_here=True
        if end_here:
            text=' '.join(sw[j] for j in chunk).rstrip(',.')
            caps.append(dict(text=text,start=round(t_at(chunk[0])-0.05,3),end=round(t_at(chunk[-1],True)+0.12,3)))
            chunk=[]
# não deixa um bloco "comer" o próximo e garante leitura mínima
for a,b in zip(caps,caps[1:]):
    a['end']=min(max(a['end'],a['start']+0.7),b['start']-0.02)
json.dump(caps,open(out,'w'),ensure_ascii=False,indent=0); print(len(caps)); [print(c) for c in caps[:8]]
