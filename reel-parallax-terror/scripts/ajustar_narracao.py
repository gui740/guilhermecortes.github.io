#!/usr/bin/env python3
"""Aperta a narração: limita pausas longas e acelera levemente (sem mudar o tom).
Uso: python3 scripts/ajustar_narracao.py [TEMPO=1.2] [PAUSA_MAX=0.45]
Lê assets/narracao/bruto/<cena>.wav (cria a cópia na 1ª vez), grava assets/narracao/<cena>.wav
e regera os timestamps em src/data/narracao.json."""
import sys, json, shutil, subprocess, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from whisper_util import load16k
from faster_whisper import WhisperModel

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.2
PMAX = float(sys.argv[2]) if len(sys.argv) > 2 else 0.45
ND = ROOT / "assets" / "narracao"; BR = ND / "bruto"; BR.mkdir(exist_ok=True)
JS = ROOT / "src" / "data" / "narracao.json"
roteiro = json.loads((ROOT / "config" / "roteiro.json").read_text())
dados = json.loads(JS.read_text())
model = WhisperModel("small", compute_type="int8")
SR = 24000

def ler(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def palavras(path, k):
    segs, _ = model.transcribe(load16k(str(path)), language="pt", word_timestamps=True, initial_prompt=roteiro[k])
    ws = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
    # se a contagem bate com o roteiro, usa a grafia exata do roteiro nas legendas
    tokens = roteiro[k].split()
    if len(tokens) == len(ws):
        for w, t in zip(ws, tokens):
            w["w"] = t
    return ws

for k in dados["cenas"]:
    if not (BR / f"{k}.wav").exists():
        shutil.copy(ND / f"{k}.wav", BR / f"{k}.wav")
    x = ler(BR / f"{k}.wav")
    ws = palavras(BR / f"{k}.wav", k)
    out, cur, xf = [], 0, int(0.02 * SR)
    for a, b in zip(ws, ws[1:]):
        gap = b["s"] - a["e"]
        if gap > PMAX:
            meio = (a["e"] + b["s"]) / 2
            c0, c1 = int((meio - PMAX / 2) * SR), int((meio + PMAX / 2) * SR)
            # corta o miolo [c0, c1) da pausa, com crossfade curto
            out.append(x[cur:c0]); cur = c1
    out.append(x[cur:])
    y = out[0]
    for seg in out[1:]:
        if len(y) > xf and len(seg) > xf:
            r = np.linspace(0, 1, xf, dtype=np.float32)
            y = np.concatenate([y[:-xf], y[-xf:] * (1 - r) + seg[:xf] * r, seg[xf:]])
        else:
            y = np.concatenate([y, seg])
    tmp = ND / f"{k}.tmp.f32"
    tmp.write_bytes(y.astype(np.float32).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(tmp),
                    "-af", f"atempo={TEMPO}", "-c:a", "pcm_s16le", str(ND / f"{k}.wav")], check=True)
    tmp.unlink()
    dur = len(ler(ND / f"{k}.wav")) / SR
    dados["cenas"][k] = {"dur": round(dur, 3), "palavras": palavras(ND / f"{k}.wav", k)}
    print(f"{k}: {len(x)/SR:.2f}s -> {dur:.2f}s")
dados["ajuste"] = {"tempo": TEMPO, "pausa_max": PMAX}
JS.write_text(json.dumps(dados, ensure_ascii=False, indent=1))
print("total narração:", round(sum(c["dur"] for c in dados["cenas"].values()), 2), "s")
