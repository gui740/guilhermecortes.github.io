"""Narração com a voz do Google (Gemini TTS, API do Google AI Studio).
Gera tudo numa tomada só (economiza cota), corta nas pausas e encaixa cada fala no tempo da cena.
Uso: GOOGLE_API_KEY=... python3 audio/gemini_tts.py   (a chave NUNCA vai no código)"""
import base64, json, os, subprocess, sys, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'out')
TMP = os.path.join(OUT, 'tts_tmp')
KEY = os.environ['GOOGLE_API_KEY']
MODELS = ['gemini-3.1-flash-tts-preview', 'gemini-3.8-flash-tts',
          'gemini-2.5-flash-preview-tts', 'gemini-3.8-flash-lite-tts']
TOTAL = 43.0


def tts(model, voice, style, text):
    prompt = ('# AUDIO PROFILE: Locutor de trailer de terror\n'
              '## THE SCENE: Reel de Instagram de um perfil brasileiro de filmes de terror.\n'
              f'### DIRECTOR\'S NOTES\n{style}\n\n'
              f'#### TRANSCRIPT\n{text}')
    body = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
            'generationConfig': {'responseModalities': ['AUDIO'],
                                 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}}}}
    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        json.dumps(body).encode(), {'content-type': 'application/json', 'x-goog-api-key': KEY})
    d = json.load(urllib.request.urlopen(req, timeout=180))
    c = d['candidates'][0]
    if 'content' not in c:
        raise RuntimeError(f"sem áudio: {c.get('finishReason')} {json.dumps(c)[:200]}")
    return c['content']['parts'][0]['inlineData']


def dur(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


def silences(p):
    r = subprocess.run(['ffmpeg', '-i', p, '-af', 'silencedetect=n=-38dB:d=0.18', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    st = [float(l.split('silence_start: ')[1]) for l in r.splitlines() if 'silence_start' in l]
    en = [float(l.split('silence_end: ')[1].split()[0]) for l in r.splitlines() if 'silence_end' in l]
    return list(zip(st, en))


def main():
    cfg = json.load(open(os.path.join(HERE, 'narracao.json')))
    segs = cfg['segments']
    os.makedirs(TMP, exist_ok=True)
    raw = os.path.join(TMP, 'take.wav')
    if '--reuse' not in sys.argv:
        text = '\n'.join(s['text'] for s in segs)
        for m in MODELS:
            try:
                data = tts(m, cfg['voice'], cfg['style'], text)
                print('modelo:', m, data['mimeType'])
                break
            except urllib.error.HTTPError as e:
                print('falhou', m, e.code, e.read().decode()[:300].replace(chr(10), ' '))
            except RuntimeError as e:
                print('falhou', m, e)
        else:
            sys.exit('nenhum modelo de TTS disponível (cota?)')
        b = base64.b64decode(data['data'])
        if b[:4] == b'RIFF':
            open(raw, 'wb').write(b)
        else:  # PCM cru 24 kHz
            open(raw + '.pcm', 'wb').write(b)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', '24000', '-ac', '1',
                            '-i', raw + '.pcm', raw], check=True)
    total = dur(raw)
    sil = [s for s in silences(raw) if s[0] > 0.05 and s[1] < total - 0.05]
    need = len(segs) - 1
    if len(sil) < need:
        sys.exit(f'só achei {len(sil)} pausas, preciso de {need}: {sil}')
    cuts = sorted(sorted(sil, key=lambda s: s[1] - s[0], reverse=True)[:need])
    bounds = [0.0] + [(a + b) / 2 for a, b in cuts] + [total]
    parts = []
    for i, s in enumerate(segs):
        a, b = bounds[i], bounds[i + 1]
        seg = os.path.join(TMP, f"{s['id']}_cut.wav")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-i', raw, '-af',
                        'silenceremove=start_periods=1:start_threshold=-42dB,areverse,'
                        'silenceremove=start_periods=1:start_threshold=-42dB,areverse', seg], check=True)
        d = dur(seg)
        tempo = min(1.35, max(1.0, d / s['slot']))
        fit = os.path.join(TMP, f"{s['id']}.wav")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', seg, '-af', f'atempo={tempo:.3f}', fit], check=True)
        nd = dur(fit)
        warn = '  <-- passa do slot' if nd > s['slot'] + 0.2 else ''
        print(f"{s['id']:10s} {d:5.2f}s -> {nd:5.2f}s (slot {s['slot']}, x{tempo:.2f}){warn}")
        parts.append((s['start'], fit))
    ins, fl = [], []
    for i, (st, f) in enumerate(parts):
        ins += ['-i', f]
        fl.append(f'[{i}]aresample=48000,adelay={int(st * 1000)}:all=1[a{i}]')
    fl.append(''.join(f'[a{i}]' for i in range(len(parts))) +
              f'amix=inputs={len(parts)}:normalize=0,apad,atrim=0:{TOTAL},aformat=channel_layouts=stereo[o]')
    dst = os.path.join(OUT, 'narracao.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', '[o]', dst],
                   check=True)
    print('ok', dst)


main()
