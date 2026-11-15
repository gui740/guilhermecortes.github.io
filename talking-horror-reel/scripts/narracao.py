"""Gera a narração frase a frase (edge-tts pt-BR), corta silêncios >200ms, concatena e extrai timestamps por palavra (Whisper)."""
import certifi, os, sys, json, asyncio, subprocess, re
_w = certifi.where()
certifi.where = lambda: os.environ.get('SSL_CERT_FILE') or _w  # respeita proxy/CA corporativa
import edge_tts, numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets/audio/narr2')
VOICE = 'pt-BR-AntonioNeural'; RATE = '+8%'
# (id, texto exibido, texto fonético p/ TTS, pausa depois em s)
S = [
 ('hook', 'Três filmes, três maldições, e a última cê não assiste sozinho.', None, 0.28),
 ('th1',  'Primeira parada: Tailândia.', None, 0.24),
 ('th2',  'O autor jura que aconteceu na família dele: um sussurro de noite, e a irmã muda.', None, 0.34),
 ('th3',  'Quando a Morte Sussurra. Tá na Netflix.', None, 0.30),
 ('send', 'Manda pra quem acha que terror bom só vem de Hollywood.', 'Manda pra quem acha que terror bom só vem de Róliud.', 0.28),
 ('fm1',  'Agora a gente desce pra Indonésia.', None, 0.24),
 ('fm2',  'Existe o pesugihan: pacto de riqueza pago com sangue.', 'Existe o pessuguírran: pacto de riqueza, pago com sangue.', 0.34),
 ('fm3',  'Fortuna Maldita. Netflix também.', None, 0.30),
 ('im1',  'E sem sair da ilha:', 'E sem sair da ilha...', 0.32),
 ('im2',  'Impetigore.', 'Impetigór.', 0.22),
 ('im3',  'Uma herança, um teatro de sombras e uma vila que quer ela morta.', None, 0.24),
 ('im4',  'Pra alugar na Apple TV.', 'Pra alugar na Épol tivi.', 0.32),
 ('q',    'Qual desses lugares cê não visitaria de jeito nenhum?', None, 0.22),
 ('cta',  'Segue a Talking Horror.', 'Segue a Tóquin Rórror.', 0.30),
]
SR = 48000
async def tts(text, path):
    for t in range(4):
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE, proxy=os.environ.get('HTTPS_PROXY')).save(path); return
        except Exception as e: print('retry', e); await asyncio.sleep(3)
    raise SystemExit('tts falhou')
def load(path):
    raw = subprocess.run(['ffmpeg','-v','error','-i',path,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()
def trim_sil(x, max_gap=0.2, thr_db=-42):
    """remove bordas mudas e encurta silêncios internos para no máx. max_gap"""
    win = int(SR*0.01); n = len(x)//win
    rms = np.sqrt((x[:n*win].reshape(n,win)**2).mean(1)+1e-12); loud = 20*np.log10(rms) > thr_db
    idx = np.where(loud)[0]; a, b = idx[0], idx[-1]+1
    keep = np.zeros(n, bool); keep[a:b] = True
    run = 0
    for i in range(a, b):
        if loud[i]: run = 0
        else:
            run += 1
            if run > max_gap/0.01: keep[i] = False
    y = x[:n*win].reshape(n,win)[keep].reshape(-1)
    f = int(SR*0.008); y[:f] *= np.linspace(0,1,f); y[-f:] *= np.linspace(1,0,f)
    return y
async def main():
    os.makedirs(OUT, exist_ok=True)
    parts = []; t = 0.0; segs = []
    for sid, disp, phon, pause in S:
        p = os.path.join(OUT, sid+'.mp3')
        if not os.path.exists(p): await tts(phon or disp, p)
        y = trim_sil(load(p))
        segs.append({'id': sid, 'text': disp, 'start': round(t,3), 'end': round(t+len(y)/SR,3)})
        parts += [y, np.zeros(int(SR*pause), np.float32)]; t += len(y)/SR + pause
    full = np.concatenate(parts); full /= max(1e-6, np.abs(full).max())/0.89
    sf.write(os.path.join(ROOT,'assets/audio/narracao.wav'), full, SR)
    # Whisper: timestamps por palavra
    from faster_whisper import WhisperModel
    m = WhisperModel('small', device='cpu', compute_type='int8')
    ws = []
    for sg in segs:
        a, b = int(sg['start']*SR), int(sg['end']*SR)
        clip = np.concatenate([np.zeros(SR//5,np.float32), full[a:b], np.zeros(SR//5,np.float32)])
        import scipy.signal as ss
        c16 = ss.resample_poly(clip, 1, 3).astype(np.float32)
        r, _ = m.transcribe(c16, language='pt', word_timestamps=True, initial_prompt=sg['text'], condition_on_previous_text=False)
        wh = [w for s in r for w in s.words]
        words = sg['text'].split()
        dur = sg['end']-sg['start']
        if len(wh) == len(words):
            tm = [(max(0,w.start-0.2), min(dur,w.end-0.2)) for w in wh]; how='whisper'
        else:  # fallback: distribui por nº de caracteres dentro da frase
            L = np.array([len(re.sub(r'\W','',w))+1.5 for w in words], float); c = np.concatenate([[0],np.cumsum(L)])/L.sum()*dur
            tm = [(c[i], c[i+1]) for i in range(len(words))]; how='interp(%d!=%d: %s)'%(len(wh),len(words),' '.join(w.word for w in wh))
        print(sg['id'], how)
        for w,(s,e) in zip(words, tm): ws.append({'w': w, 's': round(sg['start']+s,3), 'e': round(sg['start']+e,3), 'seg': sg['id']})
    json.dump({'duration': round(len(full)/SR,3), 'segments': segs, 'words': ws}, open(os.path.join(ROOT,'src/timing.json'),'w'), ensure_ascii=False, indent=1)
    print('dur', len(full)/SR, 'palavras', len(ws))
asyncio.run(main())
