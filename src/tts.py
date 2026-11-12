# Gera narração frase a frase com edge-tts, junta, acelera, corta silêncios e extrai timestamps por palavra (Whisper)
import json, subprocess, sys, os, asyncio, ssl, edge_tts, edge_tts.communicate as _c
_ca=os.environ.get('SSL_CERT_FILE') or '/root/.ccr/ca-bundle.crt'
if os.path.exists(_ca): _c._SSL_CTX=ssl.create_default_context(cafile=_ca)
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/..')
L=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'assets/audio/lines.json'))
out=sys.argv[2] if len(sys.argv)>2 else 'assets/audio/narracao'
os.makedirs('assets/audio/lines',exist_ok=True)
VOICE='pt-BR-AntonioNeural'
async def gen(l,f):
    await edge_tts.Communicate(l['text'],VOICE,rate=l['rate'],pitch=l['pitch']).save(f)
def sh(c): subprocess.run(c,shell=True,check=True,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
parts=[]
for l in L:
    f=f"assets/audio/lines/{l['id']}.mp3"
    if not os.path.exists(f): asyncio.run(gen(l,f))
    w=f"assets/audio/lines/{l['id']}.wav"
    # tira silêncio das pontas, acelera 1.07x
    sh(f"ffmpeg -y -i {f} -af \"silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse,silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.02,areverse,silenceremove=stop_periods=-1:stop_duration=0.12:stop_threshold=-36dB:stop_silence=0.10,atempo=1.07\" -ar 48000 -ac 1 {w}")
    gap=0.34 if l.get('pause_before') else 0.07   # pausa antes de cada título; resto <=200ms
    sh(f"ffmpeg -y -f lavfi -i anullsrc=r=48000:cl=mono -t {gap} assets/audio/lines/gap_{l['id']}.wav")
    parts+= [f"assets/audio/lines/gap_{l['id']}.wav", w]
parts=parts[1:]  # sem silêncio no início
open('assets/audio/lines/concat.txt','w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in parts))
# corta silêncios internos > 200ms (exceto os de título que são 320ms -> mantidos por não-cortar acima de 0.35)
sh(f"ffmpeg -y -f concat -safe 0 -i assets/audio/lines/concat.txt -af \"loudnorm=I=-16:TP=-1.5\" -ar 48000 -ac 1 {out}.wav")
print(subprocess.run(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {out}.wav",shell=True,capture_output=True,text=True).stdout)
