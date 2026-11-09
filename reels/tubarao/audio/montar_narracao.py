"""Monta out/narracao.wav (70s) a partir da tomada do Google TTS, em velocidade natural.
Cada fala entra no início do seu bloco (src/timeline.json) + offset. Uso: python3 audio/montar_narracao.py"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
tl = json.load(open(os.path.join(ROOT, 'src', 'timeline.json')))
cfg = json.load(open(os.path.join(HERE, 'narracao.json')))
fps, total = tl['fps'], tl['total'] / tl['fps']
ins, fl = [], []
for i, s in enumerate(cfg['segments']):
    src = os.path.join(HERE, s.get('src', cfg['take']))
    start = tl[s['block']][0] / fps + s.get('offset', tl['narrationOffset'])
    dur = s['out'] - s['in']
    blk_end = (tl[s['block']][0] + tl[s['block']][1]) / fps
    assert start + dur <= blk_end + 0.25, f"{s['id']} passa do bloco ({start + dur:.2f} > {blk_end:.2f})"
    ins += ['-ss', f"{s['in']:.3f}", '-t', f'{dur:.3f}', '-i', src]
    fl.append(f"[{i}]aresample=48000,afade=t=in:d=0.02,afade=t=out:st={dur - 0.06:.3f}:d=0.06,"
              f"adelay={int(start * 1000)}:all=1[a{i}]")
    print(f"{s['id']:10s} {start:6.2f}s → {start + dur:6.2f}s (bloco até {blk_end:.2f}s)")
n = len(cfg['segments'])
# voz: tira grave embolado, dá presença e segura a dinâmica
fl.append(''.join(f'[a{i}]' for i in range(n)) + f'amix=inputs={n}:normalize=0,'
          'highpass=f=75,equalizer=f=3200:t=q:w=1.2:g=2.5,'
          'acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=4,'
          f'apad,atrim=0:{total},aformat=channel_layouts=stereo[o]')
dst = os.path.join(ROOT, 'out', 'narracao.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', '[o]', dst], check=True)
print('ok', dst)
