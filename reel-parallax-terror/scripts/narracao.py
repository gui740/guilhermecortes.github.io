#!/usr/bin/env python3
"""Gera a narração final (uma faixa por cena) + timestamps por palavra (Whisper).
Requer GEMINI_API_KEY no ambiente.  Uso: python3 scripts/narracao.py [Voz] [cena ...]
Saídas: assets/narracao/<cena>.wav  e  src/data/narracao.json (durações + palavras)
"""
import sys, json, re, pathlib, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tts import tts, CENAS, ROOT
from whisper_util import load16k
from faster_whisper import WhisperModel

VOZ = sys.argv[1] if len(sys.argv) > 1 else "Enceladus"
alvo = sys.argv[2:] or list(CENAS)
OUT = ROOT / "src" / "data" / "narracao.json"
dados = json.loads(OUT.read_text()) if OUT.exists() else {"voz": VOZ, "cenas": {}}
dados["voz"] = VOZ
model = WhisperModel("small", compute_type="int8")

def norm(s): return re.findall(r"\w+", s.lower())

for k in alvo:
    esperado = len(norm(CENAS[k]))
    for tentativa in range(2):
        wav = ROOT / "assets" / "narracao" / f"{k}.wav"
        tts(CENAS[k], VOZ, wav)
        # corta silêncio no começo/fim (deixa ~0.15s)
        tmp = wav.with_suffix(".trim.wav")
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(wav),"-af",
            "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse,"
            "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.25,areverse",str(tmp)],check=True)
        tmp.replace(wav)
        x = load16k(str(wav))
        segs, _ = model.transcribe(x, language="pt", word_timestamps=True, initial_prompt=CENAS[k])
        words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
        n = len(words)
        print(f"{k}: {n} palavras (esperado {esperado}), {len(x)/16000:.2f}s")
        if 0.8 * esperado <= n <= 1.2 * esperado:
            break
        print("  transcrição não bate, gerando de novo")
    dados["cenas"][k] = {"dur": round(len(x) / 16000, 3), "palavras": words}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dados, ensure_ascii=False, indent=1))
print("ok", OUT)
