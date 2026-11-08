"""Vozes: TTS pt-BR + tratamento de rádio AM / voz do leito do rio.

Backend preferido: Gemini TTS (Google AI Studio), chave em GEMINI_API_KEY.
Fallback offline: Piper (pt_BR-faber-medium) e, por fim, espeak-ng.
"""
import base64
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from math import gcd

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly

import config as C

MODELO_PIPER = C.ASSETS / "voz" / "pt_BR-faber-medium.onnx"
CACHE = C.SAIDA / "cache_voz"

ESTILO_LOCUTOR = ("Fale em português do Brasil como um locutor de rádio AM dos anos 70, "
                  "voz masculina grave, simpática e tranquila, ritmo firme: ")
ESTILO_GANCHO = ("Fale em português do Brasil, voz masculina grave, baixa e tensa, quase um sussurro "
                 "urgente, como um aviso sério: ")
ESTILO_LENTO = ("Fale em português do Brasil muito devagar, arrastado e sem emoção, "
                "como uma fita perdendo velocidade: ")
ESTILO_SECO = ("Fale em português do Brasil, voz masculina grave, seca, fria e direta, "
               "sem nenhuma simpatia: ")
ESTILO_REGRA = ("Fale em português do Brasil como um aviso oficial de emergência, voz masculina grave, "
                "monótona e solene, ritmo constante: ")
ESTILO_RIO = ("Fale em português do Brasil, voz masculina muito grave, lenta e profunda, "
              "como se viesse do fundo de um rio: ")


# ---------------------------------------------------------------------------
# Backends
# ---------------------------------------------------------------------------
def _chave_gemini():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    arq = os.environ.get("GEMINI_API_KEY_FILE")
    if not k and arq and os.path.exists(arq):
        k = open(arq).read().strip()
    return k


def _gemini(texto, estilo, arq):
    chave = _chave_gemini()
    if not chave:
        return False
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{C.TTS_GEMINI_MODELO}:generateContent")
    corpo = {
        "contents": [{"parts": [{"text": estilo + texto}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": C.TTS_GEMINI_VOZ}}},
        },
    }
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": chave})
    for tentativa in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            parte = d["candidates"][0]["content"]["parts"][0]["inlineData"]
            raw = base64.b64decode(parte["data"])
            if raw[:4] == b"RIFF":
                x, sr = sf.read(io.BytesIO(raw), dtype="float32")
            else:  # PCM 16-bit mono 24 kHz
                x, sr = np.frombuffer(raw, "<i2").astype(np.float32) / 32768, 24000
            sf.write(str(arq), x, sr)
            return True
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:200]
            if e.code in (429, 500, 503):
                espera = 8 * (tentativa + 1)
                print(f"  gemini {e.code}, tentando de novo em {espera}s...")
                time.sleep(espera)
                continue
            print("  gemini falhou:", e.code, msg)
            return False
        except Exception as e:  # noqa: BLE001
            print("  gemini falhou:", e)
            time.sleep(3)
    return False


def _piper(texto, arq, length_scale=1.0):
    if not MODELO_PIPER.exists():
        return False
    try:
        subprocess.run([sys.executable, "-m", "piper", "-m", str(MODELO_PIPER), "-f", str(arq),
                        "--length-scale", str(length_scale)],
                       input=texto.encode("utf-8"), check=True, capture_output=True)
        return True
    except Exception as e:  # noqa: BLE001
        print("  piper falhou:", e)
        return False


def _espeak(texto, arq):
    if not shutil.which("espeak-ng"):
        return False
    subprocess.run(["espeak-ng", "-v", "pt-br", "-s", "140", "-p", "30", "-w", str(arq), texto], check=True)
    return True


def sintetiza(texto, estilo):
    """Devolve o caminho do WAV (com cache por conteúdo)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    tem_chave = bool(_chave_gemini())
    chave = hashlib.sha1(f"{C.TTS_GEMINI_MODELO}|{C.TTS_GEMINI_VOZ}|{estilo}|{texto}|{tem_chave}".encode()).hexdigest()[:16]
    arq = CACHE / f"{chave}.wav"
    if arq.exists():
        return arq
    print(f"  TTS: {texto[:60]}")
    if (tem_chave and _gemini(texto, estilo, arq)) or _piper(texto, arq) or _espeak(texto, arq):
        return arq
    raise RuntimeError("Nenhum TTS disponível (defina GEMINI_API_KEY, instale piper-tts ou espeak-ng)")


# ---------------------------------------------------------------------------
# Processamento
# ---------------------------------------------------------------------------
def _carrega(arq):
    x, sr = sf.read(str(arq), dtype="float32")
    if x.ndim > 1:
        x = x.mean(1)
    g = gcd(sr, C.SR)
    x = resample_poly(x, C.SR // g, sr // g).astype(np.float32)
    return x / (np.abs(x).max() + 1e-9)


def apara(x, max_pausa=0.28):
    """Corta silêncio nas pontas e encurta pausas internas longas."""
    bloco = int(0.01 * C.SR)
    nb = len(x) // bloco
    if nb == 0:
        return x
    rms = np.sqrt((x[: nb * bloco].reshape(nb, bloco) ** 2).mean(1))
    voz = rms > 0.02
    if not voz.any():
        return x
    a, b = np.argmax(voz), nb - np.argmax(voz[::-1])
    partes, silencio = [], 0
    lim = int(max_pausa / 0.01)
    for k in range(max(0, a - 2), min(nb, b + 4)):
        if voz[k]:
            silencio = 0
        else:
            silencio += 1
            if silencio > lim:
                continue
        partes.append(x[k * bloco:(k + 1) * bloco])
    return np.concatenate(partes)


def atempo(x, fator):
    """Acelera sem mudar o tom (ffmpeg atempo)."""
    if abs(fator - 1) < 0.02:
        return x
    filtros = []
    f = fator
    while f > 2.0:
        filtros.append("atempo=2.0")
        f /= 2.0
    filtros.append(f"atempo={f:.4f}")
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(C.SR), "-ac", "1", "-i", "-",
                        "-af", ",".join(filtros), "-f", "f32le", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def cabe(x, slot):
    dur = len(x) / C.SR
    if dur > slot:
        fator = dur / slot
        if fator > 1.5:
            print(f"  aviso: fala {dur:.1f}s acelerada {fator:.2f}x para caber em {slot:.1f}s")
        x = atempo(x, fator)
    return x


def muda_tom(x, semitons):
    """Desloca tom por reamostragem (mais grave = mais lento, como fita)."""
    fator = 2 ** (-semitons / 12)
    return resample_poly(x, int(round(100 * fator)), 100).astype(np.float32)


def radio_am(x, rng, wow=1.0, picote=0.0, banda=(300, 3400), drive=2.4):
    t = np.arange(len(x)) / C.SR
    desloc = (0.0025 * wow * np.sin(2 * np.pi * 0.55 * t + rng.random() * 6)
              + 0.0004 * np.sin(2 * np.pi * 7.3 * t)) * C.SR
    pos = np.clip(np.arange(len(x)) + desloc, 0, len(x) - 1)
    x = np.interp(pos, np.arange(len(x)), x).astype(np.float32)
    x = sosfilt(butter(4, list(banda), btype="band", fs=C.SR, output="sos"), x)
    x = np.tanh(drive * x) / np.tanh(drive)
    x = x + rng.normal(0, 0.012, len(x))
    if picote > 0:
        bloco = int(0.045 * C.SR)
        for k in range(0, len(x), bloco):
            if rng.random() < picote:
                x[k:k + bloco] *= 0.0
    return (x / (np.abs(x).max() + 1e-9)).astype(np.float32)


def voz_do_rio(x, rng):
    """Voz do leito do rio: muito grave, abafada, com eco de poço."""
    x = sosfilt(butter(4, 900, btype="low", fs=C.SR, output="sos"), x)
    eco = np.zeros(len(x) + int(0.9 * C.SR), np.float32)
    for k, (atr, g) in enumerate([(0, 1.0), (0.11, 0.5), (0.23, 0.35), (0.41, 0.22), (0.67, 0.12)]):
        a = int(atr * C.SR)
        eco[a:a + len(x)] += x * g
    return (eco / (np.abs(eco).max() + 1e-9)).astype(np.float32)


# ---------------------------------------------------------------------------
def gera_voz(n_amostras):
    """Retorna (faixa_locutor, faixa_rio, tempos)."""
    rng = np.random.default_rng(C.SEED + 7)
    faixa = np.zeros(n_amostras, np.float32)
    rio = np.zeros(n_amostras, np.float32)
    tempos = {k: [] for k in ("gancho", "boletim", "lenta", "correcao", "regras", "final", "contato")}

    def coloca(x, t0, ganho, alvo=faixa):
        a = int(t0 * C.SR)
        b = min(n_amostras, a + len(x))
        alvo[a:b] += x[: b - a] * ganho
        return t0 + len(x) / C.SR

    def clipe(txt, estilo, slot):
        return cabe(apara(_carrega(sintetiza(txt, estilo))), slot)

    # gancho
    x = clipe(C.GANCHO_FALA, ESTILO_GANCHO, C.T_GANCHO_FIM - C.T_VOZ_GANCHO - 0.15)
    x = radio_am(x, rng, wow=0.4, banda=(120, 6000), drive=1.6)
    fim = coloca(x, C.T_VOZ_GANCHO, 0.95)
    tempos["gancho"].append((C.T_VOZ_GANCHO, fim, C.GANCHO_FALA))

    # boletim: 5 frases que precisam caber em SLOT_VOZ1
    clipes = [apara(_carrega(sintetiza(txt, ESTILO_LOCUTOR))) for txt, _ in C.FALAS_BOLETIM]
    gap = 0.28
    total = sum(len(c) for c in clipes) / C.SR + gap * (len(clipes) - 1)
    fator = max(1.0, total / C.SLOT_VOZ1)
    t = C.T_VOZ1
    for (txt, _), c in zip(C.FALAS_BOLETIM, clipes):
        c = radio_am(atempo(c, fator), rng)
        fim = coloca(c, t, 0.8)
        tempos["boletim"].append((t, fim, txt))
        t = fim + gap

    # repetição lenta e grave, com picotes
    x = clipe(C.FALA_LENTA, ESTILO_LENTO, 2.4 / 1.30)
    x = radio_am(muda_tom(x, -4.5), rng, wow=3.0, picote=0.1)
    fim = coloca(x, C.T_VOZ_LENTA, 0.85)
    tempos["lenta"].append((C.T_VOZ_LENTA, fim, C.FALA_LENTA))

    # correção, seca
    clipes = [apara(_carrega(sintetiza(txt, ESTILO_SECO))) for txt in C.FALA_CORRECAO]
    slot = C.T_SUBLIMINAR1 - C.T_VOZ_CORRECAO - 0.1
    total = sum(len(c) for c in clipes) / C.SR / 1.12 + 0.2 * 2
    fator = max(1.0, total / slot)
    t = C.T_VOZ_CORRECAO
    for txt, c in zip(C.FALA_CORRECAO, clipes):
        c = radio_am(muda_tom(atempo(c, fator), -2.0), rng, wow=0.3)
        fim = coloca(c, t, 0.9)
        tempos["correcao"].append((t, fim, txt))
        t = fim + 0.2

    # regras, uma por cartela
    for k, fala in enumerate(C.REGRAS_FALA):
        a, b = C.T_REGRA[k]
        x = clipe(fala, ESTILO_REGRA, b - a - 0.35)
        x = radio_am(x, rng, wow=0.5, banda=(200, 4200), drive=1.8)
        fim = coloca(x, a + 0.15, 0.85)
        tempos["regras"].append((a + 0.15, fim, fala))
    x = clipe(C.REGRA_FINAL_FALA, ESTILO_SECO, C.T_1968 - C.T_REGRA_FINAL - 0.2)
    x = radio_am(muda_tom(x, -1.5), rng, wow=0.8, banda=(200, 4200))
    fim = coloca(x, C.T_REGRA_FINAL + 0.1, 0.95)
    tempos["final"].append((C.T_REGRA_FINAL + 0.1, fim, C.REGRA_FINAL_FALA))

    # a voz do rio (contato)
    t0 = C.T_LEGENDAS[1][0]
    slot = (C.T_PRETO - t0 - 0.9) / 1.5
    x = clipe(C.FALA_CONTATO, ESTILO_RIO, slot)
    x = voz_do_rio(muda_tom(x, -7.0), rng)
    fim = coloca(x, t0, 1.0, rio)
    tempos["contato"].append((t0, fim, C.FALA_CONTATO))
    return faixa, rio, tempos


if __name__ == "__main__":
    f, r, tp = gera_voz(int(C.DURACAO * C.SR))
    for k, v in tp.items():
        for ini, fim, txt in v:
            print(f"{k:9s} {ini:6.2f}-{fim:6.2f}  {txt}")
