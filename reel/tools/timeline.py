"""Builds the master timeline (seconds) from real clip durations, following decupagem.md."""
import json,subprocess,sys
def dur(k): return float(subprocess.check_output(['ffprobe','-v','0','-show_entries','format=duration','-of','csv=p=0',f'assets/vo/trim/{k}.wav']))
hook=sys.argv[1] if len(sys.argv)>1 else 'g'
clip={'g':f'{hook}_-2Hz','f3a':'t_a1_-2Hz','f3n':'f3n_sel','f3b':'f3b_-2Hz','p1':'p1_-2Hz','f2a':'t_b1_-2Hz','f2n':'f2n_-2Hz','f2b':'f2b_-2Hz','p2':'p2_-2Hz','f1a':'f1a_-2Hz','f1n':'f1n_sel','f1b':'f1b_-2Hz','fe1':'fe1_-2Hz','fe2':'fe2_sel'}
D={k:dur(v) for k,v in clip.items()}
vo=[];T={}
def say(k,t): vo.append(dict(key=k,clip=clip[k],start=round(t,3),end=round(t+D[k],3))); return t+D[k]
t=say('g',0.35)
T['hookEnd']=max(t+0.45,3.9)   # palavra-chave final ('PRIME', falada ~2.4s) fica parada >1s
TRAV=1.5; NUM_LEAD=0.5; NUM_ALONE=0.9; PAUSE=0.4; TITLE_HOLD=1.85; LOGO_GAP=0.15; LOGO_HOLD=1.6
stations=[]; cur=T['hookEnd']
travs=[]
for i,(f,ponte) in enumerate([('3',None),('2','p1'),('1','p2')]):
    ts=cur; travs.append(dict(start=round(ts,3),end=round(ts+TRAV,3),ponte=ponte))
    if ponte: say(ponte,ts+0.08)
    S=ts+TRAV
    st=dict(n=f,start=round(S,3),numberIn=round(S-NUM_LEAD,3))
    a0=S+NUM_ALONE; a1=say(f'f{f}a',a0); st['aIn']=round(a0,3); st['aEnd']=round(a1,3)
    extra=0.5 if f=='1' else 0.0
    nm=a1+PAUSE+extra; say(f'f{f}n',nm); st['titleIn']=round(nm-0.05,3)
    if f=='1': st['silence']=[round(nm-0.5,3),round(nm,3)]
    b0=nm+TITLE_HOLD; b1=say(f'f{f}b',b0); st['bIn']=round(b0,3); st['bEnd']=round(b1,3)
    lg=b1+LOGO_GAP; st['logoIn']=round(lg,3); st['end']=round(lg+LOGO_HOLD+0.1,3)
    stations.append(st); cur=st['end']
fe=cur; e1=say('fe1',fe+0.35); e2=say('fe2',e1+0.3)
T.update(stations=stations,travs=travs,outroStart=round(fe,3),outroQuestionIn=round(fe+0.35,3),handleIn=round(e1+0.3,3),diveStart=round(e2-0.45,3),end=round(e2+0.35,3))
T['vo']=vo; T['durationInFrames']=int(round(T['end']*30))
json.dump(T,open(f'src/timeline{"" if hook=="g" else "_"+hook}.json','w'),indent=1)
print(json.dumps({k:v for k,v in T.items() if k!='vo'},indent=0)[:1500]); print('END',T['end'])
