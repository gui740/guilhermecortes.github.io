"""Tempo por palavra (Whisper) de cada arquivo de narração. Uso: python3 palavras.py <saida.json> <wav> [wav...]"""
import json, os, sys, wave
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
out = {}
for f in sys.argv[2:]:
    w = wave.open(f); sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    idx = np.round(np.arange(0, len(a), sr / 16000)).astype(int); a = a[idx[idx < len(a)]]
    segs, _ = m.transcribe(a, language="pt", word_timestamps=True)
    out[os.path.basename(f)[:-4]] = [[round(x.start, 3), round(x.end, 3), x.word.strip()] for s in segs for x in s.words]
    print(os.path.basename(f), len(out[os.path.basename(f)[:-4]]), flush=True)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=0)
