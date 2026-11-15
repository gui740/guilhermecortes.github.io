import os, json, base64, re, urllib.request, sys, time
import numpy as np, soundfile as sf
from scipy import signal
KEY=os.environ['GEMINI_API_KEY']; MODEL=sys.argv[1]; VOICE=sys.argv[2]; out=sys.argv[3]
T="""# AUDIO PROFILE: Narrador de Reels
Criador de conteúdo brasileiro, uns 25 anos, da página de terror Talking Horror.

## DIRECTOR'S NOTES
Estilo: animado e envolvente, energia de quem conta uma descoberta pra um amigo, sorriso na voz, com um toque de suspense nas partes de lenda. Sem gritar, sem voz de locutor.
Ritmo: ágil, de vídeo viral, frases curtas, pausas mínimas entre as frases.
Sotaque: português do Brasil, natural. Pronuncie "pesugihan" como "pessuguírran" e "Impetigore" como "impetigór".

## TRANSCRIPT
Três filmes, três maldições, e a última cê não assiste sozinho.
Primeira parada: Tailândia.
O autor jura que aconteceu na família dele: um sussurro de noite, e a irmã muda.
Quando a Morte Sussurra. Tá na Netflix.
Manda pra quem acha que terror bom só vem de Hollywood.
Agora a gente desce pra Indonésia.
Existe o pesugihan: pacto de riqueza pago com sangue.
Fortuna Maldita. Netflix também.
E sem sair da ilha:
Impetigore.
Uma herança, um teatro de sombras e uma vila que quer ela morta.
Pra alugar na Apple TV.
Qual desses lugares cê não visitaria de jeito nenhum?
Segue a Talking Horror."""
body={'contents':[{'parts':[{'text':T}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':VOICE}}}}}
for a in range(6):
    try:
        d=json.load(urllib.request.urlopen(urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':KEY}),timeout=180)); break
    except Exception as e:
        m=getattr(e,'read',lambda:b'')().decode()[:700]; print('retry',e,re.findall(r'retry in ([\d.]+)s|quotaId": "([^"]+)',m)); time.sleep(35)
else: raise SystemExit('falhou')
p=d['candidates'][0]['content']['parts'][0]['inlineData']; rate=int(re.search(r'rate=(\d+)',p['mimeType']).group(1)) if 'rate=' in p['mimeType'] else 24000
pcm=np.frombuffer(base64.b64decode(p['data']),dtype='<i2').astype(np.float32)/32768
sf.write(out,signal.resample_poly(pcm,48000,rate),48000); print('ok',len(pcm)/rate,'s')
