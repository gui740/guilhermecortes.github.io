"""Narração com Gemini TTS: 3 takes por frase. Uso: GEMINI_API_KEY=... python3 tools/tts_gemini.py lines.tsv VOICE"""
import os,sys,json,base64,subprocess,time,urllib.request
KEY=os.environ['GEMINI_API_KEY']; MODEL=os.environ.get('TTS_MODEL','gemini-3.8-flash-tts')
STYLE=os.environ.get("TTS_STYLE","Say in Brazilian Portuguese, relaxed and friendly, like recommending a movie to a close friend, unhurried, with natural pauses and a little smile in the voice: ")
def tts(text,voice,out):
    body={"contents":[{"parts":[{"text":PROMPT.replace("{TRANSCRIPT}",text)}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":voice}}}}}
    req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    for i in range(5):
        try:
            d=json.load(urllib.request.urlopen(req,timeout=120)); break
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:300]; print('HTTP',e.code,msg,file=sys.stderr); time.sleep(40*(i+1))
    else: raise SystemExit('tts failed')
    part=d['candidates'][0]['content']['parts'][0]['inlineData']
    pcm=base64.b64decode(part['data']); open(out+'.pcm','wb').write(pcm)
    rate=24000
    if 'rate=' in part.get('mimeType',''): rate=int(part['mimeType'].split('rate=')[1].split(';')[0])
    subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar',str(rate),'-ac','1','-i',out+'.pcm','-ar','48000',out],check=True); os.remove(out+'.pcm')
PROMPT="""# AUDIO PROFILE: Gui
## Apresentador jovem brasileiro de uma página de terror no Instagram.

## THE SCENE
Fim de noite, ele indica filmes de terror pra um amigo próximo, sem pressa.

### DIRECTOR'S NOTES
Estilo: descontraído, tranquilo, com um sorrisinho na voz. Nada de locutor de rádio.
Ritmo: sem pressa, velocidade normal, pausas naturais entre as frases e uma pausa curta antes de cada nome de filme.
Sotaque: português do Brasil, neutro.
Pronúncia: Ghostland (gôust-lénd), Huesera (ue-SÉ-ra), Talking Horror (tóking rórror).

#### TRANSCRIPT
{TRANSCRIPT}"""
voice=sys.argv[2]; takes=int(os.environ.get('TAKES','3'))
for l in open(sys.argv[1]):
    if not l.strip(): continue
    k,t=l.rstrip("\n").split("\t"); t=t.replace("\\n","\n")
    for n in range(takes):
        out=f'assets/vo/gemini/{k}_{voice}_{n}.wav'
        if not os.path.exists(out): tts(t,voice,out); print(out,flush=True)
