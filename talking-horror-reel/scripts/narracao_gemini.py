"""Narração pelo Google AI Studio (Gemini TTS), frase a frase, tom animado.
Cada frase é encaixada no início do mesmo segmento da versão anterior (src/timing_edge.json),
para manter câmera e textos sincronizados; depois o Whisper refaz os timestamps por palavra.
Requer GEMINI_API_KEY no ambiente (a chave não fica no repositório)."""
import os, sys, json, base64, time, re, urllib.request
import numpy as np, soundfile as sf
from scipy import signal
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get('GEMINI_TTS_MODEL', 'gemini-3.8-flash-tts')
VOICE = os.environ.get('GEMINI_VOICE', 'Puck')
OUT = os.path.join(ROOT, 'assets/audio/narr_gemini'); os.makedirs(OUT, exist_ok=True)
SR = 48000
STYLE = ('Leia em português do Brasil, com sotaque brasileiro natural. Você é um criador de conteúdo jovem, de uns 25 anos, '
         'narrando um Reels de filmes de terror pra um amigo: animado, com energia e sorriso na voz, ritmo ágil, '
         'mas sem gritar e sem parecer locutor de rádio. Diga só o texto: ')
PHON = {'send': 'Manda pra quem acha que terror bom só vem de Hollywood!',
        'fm2': 'Existe o pessuguírran: pacto de riqueza, pago com sangue.',
        'im1': 'E sem sair da ilha...', 'im2': 'Impetigór!', 'im4': 'Pra alugar na Apple TV.',
        'cta': 'Segue a Talking Horror!', 'th1': 'Primeira parada: Tailândia!', 'hook': 'Três filmes, três maldições... e a última, cê não assiste sozinho.'}
base = json.load(open(os.path.join(ROOT, 'src/timing_edge.json')))
TAKE = os.path.join(OUT, os.environ.get('GEMINI_TAKE', 'take_puck.wav'))   # gerado por scripts/gemini_take.py (1 requisição)

def trim(x, max_gap=0.2, thr_db=-40):
    win = int(SR * 0.01); n = len(x) // win
    rms = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1) + 1e-12); loud = 20 * np.log10(rms) > thr_db
    idx = np.where(loud)[0]; a, b = idx[0], idx[-1] + 1
    keep = np.zeros(n, bool); keep[a:b] = True; run = 0
    for i in range(a, b):
        if loud[i]: run = 0
        else:
            run += 1
            if run > max_gap / 0.01: keep[i] = False
    y = x[:n * win].reshape(n, win)[keep].reshape(-1).copy()
    f = int(SR * 0.008); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y

def stretch(y, factor):  # acelera sem mudar o tom (ffmpeg atempo)
    import subprocess, tempfile
    a = tempfile.mktemp(suffix='.wav'); b = tempfile.mktemp(suffix='.wav'); sf.write(a, y, SR)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', a, '-af', f'atempo={factor:.4f}', b], check=True)
    return sf.read(b)[0].astype(np.float32)

# 1) transcreve a tomada única e acha onde cada frase começa/termina
from faster_whisper import WhisperModel
import difflib, unicodedata
m = WhisperModel('small', device='cpu', compute_type='int8')
take = sf.read(TAKE)[0].astype(np.float32)
r, _ = m.transcribe(signal.resample_poly(take, 1, 3).astype(np.float32), language='pt', word_timestamps=True,
                    initial_prompt='Quando a Morte Sussurra, Netflix, pesugihan, Fortuna Maldita, Impetigore, Apple TV, Talking Horror, cê.')
wh = [w for s_ in r for w in s_.words]
nrm = lambda w: re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', w.lower()).encode('ascii', 'ignore').decode())
segs = base['segments']
script = [(nrm(w), i) for i, sg in enumerate(segs) for w in sg['text'].split()]
heard = [nrm(w.word) for w in wh]
print('ouvido:', ' '.join(w.word.strip() for w in wh))
sm = difflib.SequenceMatcher(None, [w for w, _ in script], heard, autojunk=False)
first = {}; last = {}
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        si = script[blk.a + k][1]; hw = wh[blk.b + k]
        first.setdefault(si, hw.start); last[si] = hw.end
total = int(base['duration'] * SR) + SR
full = np.zeros(total, np.float32); new = []
for i, sg in enumerate(segs):
    if i not in first: raise SystemExit('frase não encontrada na tomada: ' + sg['text'])
    a0 = first[i] - 0.12 if i == 0 else (last.get(i - 1, first[i]) + first[i]) / 2
    b0 = (last[i] + first[i + 1]) / 2 if i + 1 in first else last[i] + 0.35
    y = trim(take[int(max(0, a0) * SR):int(b0 * SR)])
    budget = (segs[i + 1]['start'] if i + 1 < len(segs) else base['duration'] + 0.25) - sg['start'] - 0.08
    dur = len(y) / SR; fac = 1.0
    if dur > budget: fac = min(1.3, dur / budget); y = stretch(y, fac)
    a = int(sg['start'] * SR); full[a:a + len(y)] += y
    new.append({'id': sg['id'], 'text': sg['text'], 'start': sg['start'], 'end': round(sg['start'] + len(y) / SR, 3)})
    print(f"{sg['id']:5s} dur {dur:.2f}s orçamento {budget:.2f}s atempo {fac:.2f}")
full = full[:int(base['duration'] * SR)] if np.abs(full[int(base['duration'] * SR):]).max() < 1e-4 else full
full /= max(1e-6, np.abs(full).max()) / 0.89
sf.write(os.path.join(ROOT, 'assets/audio/narracao.wav'), full, SR)

ws = []
for sg in new:
    a, b = int(sg['start'] * SR), int(sg['end'] * SR)
    clip = np.concatenate([np.zeros(SR // 5, np.float32), full[a:b], np.zeros(SR // 5, np.float32)])
    r, _ = m.transcribe(signal.resample_poly(clip, 1, 3).astype(np.float32), language='pt', word_timestamps=True, initial_prompt=sg['text'], condition_on_previous_text=False)
    wh = [w for s in r for w in s.words]; words = sg['text'].split(); dur = sg['end'] - sg['start']
    if len(wh) == len(words): tm = [(max(0, w.start - 0.2), min(dur, w.end - 0.2)) for w in wh]; how = 'whisper'
    else:
        L = np.array([len(re.sub(r'\W', '', w)) + 1.5 for w in words], float); c = np.concatenate([[0], np.cumsum(L)]) / L.sum() * dur
        tm = [(c[k], c[k + 1]) for k in range(len(words))]; how = 'interp (%d!=%d) %s' % (len(wh), len(words), ' '.join(w.word for w in wh))
    print(sg['id'], how)
    for w, (s, e) in zip(words, tm): ws.append({'w': w, 's': round(sg['start'] + s, 3), 'e': round(sg['start'] + e, 3), 'seg': sg['id']})
json.dump({'duration': base['duration'], 'segments': new, 'words': ws, 'voz': f'Gemini TTS {MODEL} / {VOICE}'}, open(os.path.join(ROOT, 'src/timing.json'), 'w'), ensure_ascii=False, indent=1)
