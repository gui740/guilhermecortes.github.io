"""Falas da locutora (fictícia). Gemini TTS com cache em saida/voz/; fallback espeak-ng.

A chave vem de GEMINI_API_KEY (variável de ambiente) e nunca é gravada em arquivo.
"""
import base64
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve

import config as C

DIR = C.SAIDA / "voz"
SR = C.SR


# ------------------------------------------------------------ motores
def _gemini(texto):
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        return None
    for modelo in [C.TTS_MODELO] + C.TTS_RESERVA:
        r = _gemini_modelo(texto, chave, modelo)
        if r is not None:
            return r
    raise SystemExit("Cota diária do Gemini TTS esgotada em todos os modelos. Tente amanhã.")


def _gemini_modelo(texto, chave, modelo):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    corpo = {"contents": [{"parts": [{"text": texto}]}],
             "generationConfig": {"responseModalities": ["AUDIO"],
                                  "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": C.TTS_VOZ}}}}}
    for tentativa in range(6):
        req = urllib.request.Request(url, data=json.dumps(corpo).encode(),
                                     headers={"Content-Type": "application/json", "x-goog-api-key": chave})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=300))
            parte = r["candidates"][0]["content"]["parts"][0]["inlineData"]
            dados = base64.b64decode(parte["data"])
            if dados[:4] == b"RIFF":
                x, sr = sf.read(io.BytesIO(dados), dtype="float32")
            else:  # PCM 16 bits cru, 24 kHz
                x, sr = np.frombuffer(dados, np.int16).astype(np.float32) / 32768, 24000
            return x, sr
        except urllib.error.HTTPError as e:
            corpo_erro = e.read().decode(errors="ignore")
            if e.code == 429 and "PerDay" in corpo_erro:
                print(f"  (cota diária de {modelo} esgotada, tentando outro modelo)")
                return None
            if e.code in (429, 500, 503) and tentativa < 5:
                espera = 2 ** tentativa * 5
                print(f"  (TTS {e.code}, nova tentativa em {espera}s)")
                time.sleep(espera)
                continue
            raise SystemExit(f"Gemini TTS falhou: {e.code} {corpo_erro[:300]}")
        except (TimeoutError, urllib.error.URLError):
            if tentativa < 5:
                time.sleep(5)
                continue
            raise


def _espeak(texto):
    if not shutil.which("espeak-ng"):
        raise SystemExit("Sem GEMINI_API_KEY e sem espeak-ng: não há como gerar a voz.")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "f.wav"
        subprocess.run(["espeak-ng", "-v", "pt-br+f3", "-s", "140", "-w", str(p), texto],
                       check=True, capture_output=True)
        return sf.read(p, dtype="float32")


def tts(texto):
    r = _gemini(texto)
    motor = "gemini"
    if r is None:
        r, motor = _espeak(texto), "espeak"
    x, sr = r
    if x.ndim > 1:
        x = x.mean(1)
    g = np.gcd(sr, SR)
    x = resample_poly(x, SR // g, sr // g).astype(np.float32)
    env = np.abs(x) > 0.01
    if env.any():
        a, b = np.argmax(env), len(x) - np.argmax(env[::-1])
        x = x[max(0, a - 600):b + 2400]
    return x / (np.abs(x).max() + 1e-9) * 0.9, motor


def gerar_todas():
    DIR.mkdir(parents=True, exist_ok=True)
    falas = {}
    for nome, texto in C.FALAS.items():
        h = hashlib.sha1(f"{C.TTS_VOZ}|{texto}".encode()).hexdigest()[:10]
        p = DIR / f"{nome}_{h}.wav"
        if p.exists():
            falas[nome], _ = sf.read(p, dtype="float32")
            continue
        x, motor = tts(texto)
        if motor == "gemini":   # só guarda em cache o que veio do Gemini
            sf.write(p, x, SR)
        print(f"  voz {nome:7s} {len(x) / SR:5.2f}s ({motor})")
        falas[nome] = x
    return falas


# ------------------------------------------------------------ tratamento
def _f(x, f, tipo, ordem=2):
    return sosfilt(butter(ordem, f, btype=tipo, fs=SR, output="sos"), x).astype(np.float32)


def wow(x, prof=0.0008, seed=0):
    n = len(x)
    t = np.arange(n) / SR
    d = (prof * np.sin(2 * np.pi * 0.5 * t + seed) + prof * 0.3 * np.sin(2 * np.pi * 6.1 * t)) * SR
    idx = np.clip(np.arange(n) - d - d.min(), 0, n - 1)
    return np.interp(idx, np.arange(n), x).astype(np.float32)


def mudar_tom(x, semitons):
    if semitons == 0:
        return x
    fator = 2 ** (semitons / 12)
    n = int(len(x) * fator)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def sala(x, dur=0.5, mix=0.12, seed=0):
    rng = np.random.default_rng(C.SEED + seed)
    n = int(dur * SR)
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-np.linspace(0, 7, n)).astype(np.float32)
    ir = _f(ir, 3500, "low")
    w = fftconvolve(x, ir)
    w = w / (np.abs(w).max() + 1e-9) * np.abs(x).max()
    out = np.zeros(len(w), np.float32)
    out[: len(x)] += x
    return out + mix * w


def transmissao(x, seed=0):
    """Locução de TV/rádio de época: banda limitada, leve saturação, pouco wow. A voz continua clara."""
    x = wow(x, 0.0007, seed)
    x = _f(x, 140, "high")
    x = _f(x, 6500, "low", 4)
    x = np.tanh(x * 1.6) / np.tanh(1.6)
    return sala(x, 0.45, 0.10, seed)


def corrompida(x, semitons=-3, seed=0):
    """Fim do vídeo: fita lenta, mais grave e abafada."""
    x = mudar_tom(x, -semitons)
    x = wow(x, 0.004, seed)
    x = _f(x, 300, "high")
    x = _f(x, 2800, "low", 4)
    x = np.tanh(x * 2.4) / np.tanh(2.4)
    return sala(x, 1.4, 0.35, seed)
