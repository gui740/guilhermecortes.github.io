"""Gera as falas da Professora Celeste (fictícia) com TTS offline e aplica tratamento de fita."""
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve

import config as C

DIR = C.SAIDA / "voz"
SR = C.SR


def _motor():
    if not shutil.which("espeak-ng"):
        raise SystemExit("espeak-ng não encontrado. Instale: apt-get install espeak-ng mbrola-br4")
    if C.VOZ_MOTOR == "mbrola" and shutil.which("mbrola"):
        r = subprocess.run(["espeak-ng", "-v", C.VOZ_MBROLA, "-q", "teste"], capture_output=True)
        if r.returncode == 0:
            return C.VOZ_MBROLA
    return C.VOZ_ESPEAK


def tts(texto, velocidade=135, pitch=None, voz=None):
    voz = voz or _motor()
    pitch = C.VOZ_PITCH if pitch is None else pitch
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "f.wav"
        subprocess.run(["espeak-ng", "-v", voz, "-s", str(velocidade), "-p", str(pitch),
                        "-g", "4", "-w", str(p), texto], check=True, capture_output=True)
        x, sr = sf.read(p, dtype="float32")
    if x.ndim > 1:
        x = x.mean(1)
    g = np.gcd(sr, SR)
    x = resample_poly(x, SR // g, sr // g).astype(np.float32)
    # apara silêncio
    env = np.abs(x) > 0.01
    if env.any():
        a, b = np.argmax(env), len(x) - np.argmax(env[::-1])
        x = x[max(0, a - 800):b + 1600]
    return x / (np.abs(x).max() + 1e-9) * 0.9


def tts_ajustado(texto, dur_max, vel=135):
    """Acelera o TTS até caber em dur_max segundos."""
    while True:
        x = tts(texto, vel)
        if len(x) / SR <= dur_max or vel > 200:
            return x, vel
        vel += 6


# ------------------------------------------------------------ tratamento
def passa_banda(x, lo=300, hi=3400, ordem=4):
    sos = butter(ordem, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x).astype(np.float32)


def passa_baixa(x, hi, ordem=4):
    sos = butter(ordem, hi, btype="low", fs=SR, output="sos")
    return sosfilt(sos, x).astype(np.float32)


def wow_flutter(x, wow=0.0025, flutter=0.0006, rng=None, fase=0.0):
    """Atraso variável: modulação lenta de pitch (wow) e rápida (flutter)."""
    n = len(x)
    t = np.arange(n) / SR
    rng = rng or np.random.default_rng(C.SEED)
    d = (wow * np.sin(2 * np.pi * 0.55 * t + fase) + wow * 0.5 * np.sin(2 * np.pi * 0.23 * t + 1.3 * fase)
         + flutter * np.sin(2 * np.pi * 6.3 * t)) * SR
    idx = np.clip(np.arange(n) - d - d.min(), 0, n - 1)
    return np.interp(idx, np.arange(n), x).astype(np.float32)


def mudar_tom(x, semitons):
    """Fita lenta: abaixa o tom e desacelera juntos (reamostragem)."""
    if semitons == 0:
        return x
    fator = 2 ** (-semitons / 12)          # >1 = mais longo/grave
    n = int(len(x) * fator)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def reverb_sala(x, dur=0.35, mix=0.22, rng=None):
    rng = rng or np.random.default_rng(C.SEED + 1)
    n = int(dur * SR)
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-np.linspace(0, 7, n)).astype(np.float32)
    ir = passa_baixa(ir, 4000)
    ir[0] = 0
    w = fftconvolve(x, ir)[: len(x) + n]
    w = w / (np.abs(w).max() + 1e-9) * np.abs(x).max()
    out = np.zeros(len(x) + n, np.float32)
    out[: len(x)] += x
    out[: len(w)] += mix * w
    return out


def tratar_fita(x, corr=0.0, semitons=0.0, seed=0, reverb=True):
    """Fita de rolo antiga. corr 0..1 aumenta wow e picotes."""
    rng = np.random.default_rng(C.SEED + seed)
    x = mudar_tom(x, semitons)
    x = wow_flutter(x, wow=0.0018 + 0.012 * corr, flutter=0.0005 + 0.001 * corr, rng=rng, fase=seed)
    x = passa_banda(x)
    x = np.tanh(x * (1.8 + 1.5 * corr)) / np.tanh(1.8 + 1.5 * corr)
    if reverb:
        x = reverb_sala(x, rng=rng)
    if corr > 0.2:  # picotes de drop-out
        n = len(x)
        for _ in range(int(corr * 6)):
            a = int(rng.integers(0, max(1, n - 4000)))
            b = a + int(rng.integers(600, 3500))
            x[a:b] *= rng.uniform(0.0, 0.25)
    chiado = passa_banda(rng.standard_normal(len(x)).astype(np.float32), 2000, 9000, 2) * 0.012
    return (x * 0.85 + chiado).astype(np.float32)


def lado_b(x):
    """Inverte e desacelera ~15%."""
    return mudar_tom(x[::-1].copy(), 12 * np.log2(1.15))


# ------------------------------------------------------------ geração
def gerar_todas(forcar=False):
    """Gera (ou reaproveita) os WAV brutos de cada fala. Retorna dict nome -> array."""
    DIR.mkdir(parents=True, exist_ok=True)
    falas = {}
    alvo = {
        "fala_a": (C.FALA_A, C.FALA_A_MAX),
        "fala_b": (C.FALA_B, 2.4),
        "voltar": (C.FALA_VOLTAR, 1.0),
        "quem": (C.FALA_QUEM, 1.4),
    }
    for i, linha in enumerate(C.LADO_B):
        alvo[f"ladob_{i}"] = (linha.capitalize(), 2.2)
    motor = _motor()
    for nome, (texto, dmax) in alvo.items():
        p = DIR / f"{nome}.wav"
        if p.exists() and not forcar:
            falas[nome], _ = sf.read(p, dtype="float32")
            continue
        x, vel = tts_ajustado(texto, dmax)
        sf.write(p, x, SR)
        print(f"  voz {nome:9s} {len(x)/SR:5.2f}s  vel={vel}  ({motor})")
        falas[nome] = x
    return falas


if __name__ == "__main__":
    gerar_todas(forcar=True)
