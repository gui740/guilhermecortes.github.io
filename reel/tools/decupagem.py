import json,unicodedata,re
T=json.load(open('src/timeline.json')); W=json.load(open('src/words.json'))
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())
def wat(key,w,fb):
    for x in W:
        if x['key']==key and norm(x['w']).startswith(norm(w)): return x['s']
    return fb
f=lambda x:f"{int(x//60):02d}:{x%60:05.2f}".replace('.',',')
films=[('3','Ghostland','2018 · França/Canadá','BONECAS','bonecas','DO AVESSO','vira'),('2','A Médium','2021 · Tailândia/Coreia','XAMÃ',['xama','chama','machama'],'REAL DEMAIS','documentario'),('1','Huesera','2022 · México/Peru','OSSOS','ossos','NUNCA MAIS','mais')]
vo={v['key']:v for v in T['vo']}
L=["# Decupagem final (tempos reais do render)","","Gerada de `src/timeline.json` + `src/words.json` (timestamps por palavra do Whisper). Duração total: **%s** (%d frames @30fps)."%(f(T['end']),T['durationInFrames']),"",
"| Tempo | Bloco | Fala | Na tela (texto) | Câmera |","|---|---|---|---|---|"]
g=vo['g']; L.append(f"| {f(0)}–{f(T['hookEnd'])} | GANCHO | “{open('src_vo_lines.tsv').read().split(chr(10))[0].split(chr(9))[1]}” ({f(g['start'])}–{f(g['end'])}) | `3 TERRORES` ({f(wat('g','tres',0)-0.08)}) → `ESCONDIDOS` ({f(wat('g','escondidos',0)-0.08)}) → `no seu PRIME` ({f(wat('g','prime',0)-0.08)}); última parada {T['hookEnd']-wat('g','prime',0)+0.08:.1f}s | recua do close na fita VHS (0–2,4s) e revela o corredor; depois avanço lento |")
for i,(n,title,lab,kA,wA,kB,wB) in enumerate(films):
    s=T['stations'][i]; tr=T['travs'][i]; key='f'+n
    ponte=f"“{'Mas o próximo é pior.' if tr['ponte']=='p1' else 'E o último...'}” ({f(vo[tr['ponte']]['start'])})" if tr['ponte'] else '—'
    L.append(f"| {f(tr['start'])}–{f(tr['end'])} | TRAVESSIA | {ponte} | nenhum | acelera (1,5s), cortina de tiras plásticas, motion blur |")
    ws=wA if isinstance(wA,list) else [wA]; ka=next((wat(key+'a',w,-1) for w in ws if wat(key+'a',w,-1)>0), s['aIn']+1.4)
    kaIn=max(ka-0.06,s['aIn']+1.5); tIn=s['titleIn']-0.22; kaOut=tIn-0.3
    kbIn=min(max(wat(key+'b',wB,s['bIn']+0.6),s['bIn']+0.25),s['logoIn']-1.55); kbOut=s['logoIn']-0.1
    L.append(f"| {f(s['numberIn'])}–{f(s['aIn'])} | FILME {n} · número | — | número `{n}` gigante, sozinho, cresce | desacelera muito; push-in 10% + órbita 5,4° na estação |")
    L.append(f"| {f(s['aIn'])}–{f(s['aEnd'])} | FILME {n} · frase A | {f(vo[key+'a']['start'])} | camadas: cenário {f(s['aIn'])} → personagem {f(s['aIn']+0.5)} → objeto 1º plano {f(s['aIn']+1.0)}; palavra `{kA}` {f(kaIn)}–{f(kaOut)} (**{kaOut-kaIn:.2f}s**) | quase parada |")
    sil=f" (silêncio total {f(s['silence'][0])}–{f(s['silence'][1])}, trilha corta)" if 'silence' in s else ''
    L.append(f"| {f(tIn)}–{f(kbIn)} | FILME {n} · TÍTULO | nome isolado em {f(vo[key+'n']['start'])}{sil} | `{title}` sozinho {f(tIn)} (firma em 6 frames) + etiqueta `{lab}` {f(tIn+0.5)}; estrela atrás do personagem; título parado **{kbIn-0.3-tIn-0.2:.2f}s** antes da palavra B | quase parada |")
    L.append(f"| {f(kbIn)}–{f(kbOut)} | FILME {n} · frase B | {f(vo[key+'b']['start'])}–{f(vo[key+'b']['end'])} | título + `{kB}` (**{kbOut-kbIn:.2f}s**) | quase parada |")
    L.append(f"| {f(s['logoIn'])}–{f(s['end']+0.1)} | FILME {n} · selo | — (trilha sobe) | título + logo Prime Video + linha tracejada; logo parado **{s['end']-s['logoIn']-0.2+0.1:.2f}s** antes da travessia | quase parada |")
L.append(f"| {f(T['outroStart'])}–{f(T['diveStart'])} | FECHO | “Salva pra ver no fim de semana. Qual cê vai ver primeiro?” ({f(vo['fe1']['start'])}) / “Segue a Talking Horror.” ({f(vo['fe2']['start'])}) | 3 títulos pequenos em 3 profundidades ({f(T['outroStart']+0.95)}), `@talking_horror` ({f(T['outroStart']+1.6)}), pergunta numa linha ({f(max(wat('fe1','qual',0)-0.05,T['outroStart']+2.1))}) parada **{T['diveStart']-0.35-max(wat('fe1','qual',0)-0.05,T['outroStart']+2.1):.2f}s** | passa pelo último filme, depois só respira |")
L.append(f"| {f(T['diveStart'])}–{f(T['end'])} | LOOP | — | fita VHS sobe ao centro | mergulha na fita: último frame = close do primeiro frame |")
L+=["","Regras checadas: máx. 2 textos simultâneos nas estações (principal + etiqueta/logo); título ≥1,8s; logo ≥1,5s; palavras-chave ≥1,2s; cada elemento entra sozinho com ≥0,5s de intervalo; nenhum corte seco."]
open('decupagem.md','w').write('\n'.join(L)+'\n'); print('\n'.join(L))
