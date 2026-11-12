# Edita a tomada única do Gemini: corta silêncios > 200ms (exceto antes dos títulos), acelera e normaliza.
# Uso: python3 src/edit_voice.py raw.wav lines.json words_raw.json out.wav [tempo]
import sys, json, subprocess, numpy as np
raw, lines, wraw, out = sys.argv[1:5]; tempo = float(sys.argv[5]) if len(sys.argv) > 5 else 1.07
SR = 48000
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', raw, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
W = json.load(open(wraw)); L = json.load(open(lines))
title_lines = {l['id'] for l in L if l.get('pause_before')}
# energia em janelas de 10ms para achar silêncio real entre palavras
win = SR // 100; e = np.array([np.sqrt(np.mean(a[i:i + win] ** 2)) for i in range(0, len(a) - win, win)])
thr = max(0.012, np.percentile(e, 20) * 1.6)
silent = e < thr
segs = []; i = 0
while i < len(silent):
    if silent[i]:
        j = i
        while j < len(silent) and silent[j]: j += 1
        segs.append((i / 100, j / 100)); i = j
    else: i += 1
first_of_line = {}
for w in W: first_of_line.setdefault(w['line'], w['s'])
keep = []; cur = 0.0
for s, e2 in segs:
    d = e2 - s
    nxt = min((t for t in first_of_line.values() if t >= e2 - 0.15), default=None)
    is_title = any(abs(first_of_line[k] - e2) < 0.35 for k in title_lines)
    maxd = 0.36 if is_title else 0.18
    if s == 0: keep.append((cur, s)); cur = max(s, e2 - 0.02); continue
    if d > maxd:
        keep.append((cur, s + maxd / 2)); cur = e2 - maxd / 2
keep.append((cur, len(a) / SR))
y = np.concatenate([a[int(p * SR):int(q * SR)] for p, q in keep if q > p])
# tira silêncio final
nz = np.where(np.abs(y) > 0.01)[0]; y = y[:nz[-1] + int(0.05 * SR)]
tmp = out + '.tmp.wav'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', tmp], input=(np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes(), check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', f'atempo={tempo},loudnorm=I=-16:TP=-1.5', '-ar', str(SR), '-ac', '1', out], check=True)
import os; os.remove(tmp)
print(out, round(len(y) / SR / tempo, 2), 's')
