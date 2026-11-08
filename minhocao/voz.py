"""Voz do locutor: TTS pt_BR offline (Piper; fallback espeak-ng) + tratamento de rádio AM."""
import shutil
import subprocess
import sys
from math import gcd

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly

import config as C

MODELO = C.ASSETS / "voz" / "pt_BR-faber-medium.onnx"
CACHE = C.SAIDA / "cache_voz"


def _sintetiza(texto, arq, length_scale=1.0):
    if arq.exists():
        return
    arq.parent.mkdir(parents=True, exist_ok=True)
    if MODELO.exists():
        try:
            subprocess.run(
                [sys.executable, "-m", "piper", "-m", str(MODELO), "-f", str(arq),
                 "--length-scale", str(length_scale), "--sentence-silence", "0.0"],
                input=texto.encode("utf-8"), check=True, capture_output=True)
            return
        except Exception as e:  # noqa: BLE001
            print("  piper falhou, usando espeak-ng:", e)
    if shutil.which("espeak-ng"):
        vel = int(150 / length_scale)
        subprocess.run(["espeak-ng", "-v", "pt-br", "-s", str(vel), "-p", "30", "-w", str(arq), texto], check=True)
        return
    raise RuntimeError("Nenhum TTS disponível (instale piper-tts ou espeak-ng)")


def _carrega(arq):
    x, sr = sf.read(str(arq), dtype="float32")
    if x.ndim > 1:
        x = x.mean(1)
    g = gcd(sr, C.SR)
    x = resample_poly(x, C.SR // g, sr // g).astype(np.float32)
    # apara silêncio
    env = np.abs(x) > 0.01
    if env.any():
        a, b = np.argmax(env), len(env) - np.argmax(env[::-1])
        x = x[max(0, a - 480): b + 960]
    return x / (np.abs(x).max() + 1e-9)


def muda_tom(x, semitons):
    """Desloca tom por reamostragem (mais grave = mais lento, como fita)."""
    fator = 2 ** (-semitons / 12)  # >1 alonga
    n = int(round(100 * fator))
    return resample_poly(x, n, 100).astype(np.float32)


def radio_am(x, rng, wow=1.0, picote=0.0):
    t = np.arange(len(x)) / C.SR
    # wow & flutter
    desloc = (0.0025 * wow * np.sin(2 * np.pi * 0.55 * t + rng.random() * 6)
              + 0.0004 * np.sin(2 * np.pi * 7.3 * t)) * C.SR
    pos = np.clip(np.arange(len(x)) + desloc, 0, len(x) - 1)
    x = np.interp(pos, np.arange(len(x)), x).astype(np.float32)
    # passa-banda 300–3400 Hz
    sos = butter(4, [300, 3400], btype="band", fs=C.SR, output="sos")
    x = sosfilt(sos, x)
    # saturação leve
    x = np.tanh(2.4 * x) / np.tanh(2.4)
    # chiado
    x = x + rng.normal(0, 0.02, len(x))
    if picote > 0:
        bloco = int(0.045 * C.SR)
        for k in range(0, len(x), bloco):
            if rng.random() < picote:
                x[k:k + bloco] *= 0.0
    return (x / (np.abs(x).max() + 1e-9)).astype(np.float32)


def gera_voz(n_amostras):
    """Retorna (faixa_mono, tempos) — tempos: {chave: [(ini, fim, texto), ...]}."""
    rng = np.random.default_rng(C.SEED + 7)
    faixa = np.zeros(n_amostras, np.float32)
    tempos = {"boletim": [], "lenta": [], "correcao": []}

    def coloca(x, t0, ganho):
        a = int(t0 * C.SR)
        b = min(n_amostras, a + len(x))
        faixa[a:b] += x[: b - a] * ganho
        return t0 + len(x) / C.SR

    # Bloco 2 — boletim normal
    t = C.T_VOZ1
    for k, (txt, _) in enumerate(C.FALAS_BOLETIM):
        arq = CACHE / f"boletim_{k}.wav"
        _sintetiza(txt, arq, 1.08)
        x = radio_am(muda_tom(_carrega(arq), -1.5), rng)
        fim = coloca(x, t, 0.8)
        tempos["boletim"].append((t, fim, txt))
        t = fim + 0.32
    # Bloco 3 — repetição lenta e grave, com picotes
    arq = CACHE / "lenta.wav"
    _sintetiza(C.FALA_LENTA, arq, 2.1)
    x = radio_am(muda_tom(_carrega(arq), -4.5), rng, wow=3.0, picote=0.12)
    fim = coloca(x, C.T_VOZ_LENTA, 0.85)
    tempos["lenta"].append((C.T_VOZ_LENTA, fim, C.FALA_LENTA))
    # ... corte, e volta seco
    t = C.T_VOZ_CORRECAO
    for k, txt in enumerate(C.FALA_CORRECAO):
        arq = CACHE / f"correcao_{k}.wav"
        _sintetiza(txt, arq, 1.15)
        x = radio_am(muda_tom(_carrega(arq), -2.0), rng, wow=0.3)
        fim = coloca(x, t, 0.9)
        tempos["correcao"].append((t, fim, txt))
        t = fim + 0.3
    return faixa, tempos


if __name__ == "__main__":
    f, tp = gera_voz(int(C.DURACAO * C.SR))
    for k, v in tp.items():
        for ini, fim, txt in v:
            print(f"{k:9s} {ini:6.2f}-{fim:6.2f}  {txt}")
