"""Narração dos ganchos alternativos B e C (edge-tts) + tempos por palavra (Whisper)."""
import certifi, os, json, asyncio, subprocess, numpy as np, soundfile as sf
_w = certifi.where(); certifi.where = lambda: os.environ.get('SSL_CERT_FILE') or _w
import edge_tts
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'B': 'A gente separou o terror asiático que ninguém te mostrou.', 'C': 'Cê tem coragem de fazer essa viagem com a gente?'}
async def main():
    from faster_whisper import WhisperModel
    m = WhisperModel('small', device='cpu', compute_type='int8'); out = {}
    for k, txt in H.items():
        mp3 = os.path.join(ROOT, f'assets/audio/gancho_{k}.mp3'); wav = mp3[:-3] + 'wav'
        await edge_tts.Communicate(txt, 'pt-BR-AntonioNeural', rate='+8%', proxy=os.environ.get('HTTPS_PROXY')).save(mp3)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mp3, '-af', 'silenceremove=start_periods=1:start_threshold=-45dB', '-ar', '48000', '-ac', '1', wav], check=True)
        a, _ = sf.read(wav); import scipy.signal as ss; a16 = ss.resample_poly(a, 1, 3).astype(np.float32)
        seg, _ = m.transcribe(a16, language='pt', word_timestamps=True, initial_prompt=txt)
        out[k] = [(w.word.strip(), round(w.start, 2)) for s in seg for w in s.words]
        print(k, out[k])
    json.dump(out, open(os.path.join(ROOT, 'src/hooks_timing.json'), 'w'), ensure_ascii=False)
asyncio.run(main())
