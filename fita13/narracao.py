"""Narração (TTS local com Piper, voz pt-BR "faber").

Duas vozes, ambas na velocidade natural da fala (sem acelerar):

* ZÉ CANHÃOZINHO (programete): tom mais agudo com pitch-shift WSOLA, que muda o
  tom sem mudar a duração. Voz de mascote simpático.
* VOZ DE TERROR (depois que o Zé se transforma, e nas regras): tom grave, uma
  segunda camada uma oitava abaixo, leve aspereza/distorção e eco de pátio.
  A cada regra fica mais grave e mais suja.

Se o Piper ou o modelo de voz não estiverem disponíveis (e não der para baixar),
retorna None e o áudio cai de volta nos "blips" de voz.
"""
import io
import os
import urllib.request
import wave

import numpy as np

import config as C

VOZ = "pt_BR-faber-medium"
VOZ_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/"
VELOCIDADE_ZE = 0.92      # length_scale do Piper (1 = natural; menor = um pouco mais rápido)
VELOCIDADE_TERROR = 1.0
TOM_ZE = 1.3              # +4,5 semitons


def roteiro():
    """(texto falado, início, duração máxima, voz, intensidade 0..1, faixa).

    faixa "fita": passa pela mesma fita que a música (desafina/desacelera na corrupção)
    faixa "livre": por cima, sem wow
    """
    r = [("Olá! Eu sou o Zé Canhãozinho!", C.OLA_T, 2.3, "ze", 0, "fita")]
    falas_cartoes = [
        "Mil oitocentos e dezoito: Dom João Sexto ordena o Real Trem de Guerra!",
        "Estilo neoclássico, muros altos, e uma varanda em volta do pátio!",
        "Na Guerra do Paraguai, aqui consertavam armas dos dois lados!",
        "De mil oitocentos e quarenta e dois a mil oitocentos e noventa e nove, "
        "meninos aprendizes trabalhavam nas forjas!",
        "Mil novecentos e oitenta e quatro: tombado. Hoje, o prédio descansa.",
    ]
    for i, txt in enumerate(falas_cartoes):
        r.append((txt, C.CARTOES_T[i] + 0.2, C.CARTOES_DUR[i] - 0.25, "ze", 0, "fita"))
    r.append(("Vamos visitar? O Arsenal está sempre de portas abertas!",
              C.FALA_FINAL_INICIO + 0.1, C.T_CORR - C.FALA_FINAL_INICIO - 0.15, "ze", 0, "fita"))
    # a transformação: a voz do Zé vira a voz de terror
    r.append(("O Arsenal... nunca parou... de trabalhar.", C.T_CORR + 0.4, 2.6, "terror", 0.0, "fita"))
    r.append(("Arsenal de Guerra. Aviso aos visitantes. Leia até o fim.",
              C.T_REGRAS + 0.15, C.REGRAS_INTRO_DUR - 0.25, "terror", 0.0, "livre"))
    falas_regras = [
        "Conte os canhões do pátio ao entrar. Conte de novo ao sair.",
        "Se o número mudou, não volte para conferir. Saia pela Rua Treze de Junho.",
        "Se ouvir marteladas de forja depois das vinte e duas horas, não é reforma.",
        "Os aprendizes podem pedir ajuda com o trabalho. Não pergunte o nome deles. Eles não lembram.",
        "O porão fecha às dezoito horas. Se a porta estiver aberta, ela não é para você.",
        "Não fique de costas para a varanda.",
        "Regra sete:",
    ]
    n = len(falas_regras)
    for i, txt in enumerate(falas_regras):
        r.append((txt, C.REGRAS_T[i] + 0.2, C.REGRAS_DUR[i] - 0.25, "terror", (i + 1) / n, "livre"))
    r.append(("Até amanhã, aprendiz.", C.FIM_APRENDIZ_T, 1.9, "terror", 1.0, "livre"))
    return r


# ------------------------------------------------------------------ síntese
def _modelo():
    os.makedirs(C.VOZES_DIR, exist_ok=True)
    onnx = os.path.join(C.VOZES_DIR, VOZ + ".onnx")
    for arq in (VOZ + ".onnx", VOZ + ".onnx.json"):
        p = os.path.join(C.VOZES_DIR, arq)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            print("  baixando voz", arq, "...")
            req = urllib.request.Request(VOZ_URL + arq, headers={"User-Agent": "fita13-render/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp, open(p + ".part", "wb") as f:
                f.write(resp.read())
            os.replace(p + ".part", p)
    return onnx


def _sintetizar(voz, texto, length_scale):
    """Fala do Piper já reamostrada para 48 kHz (sem mudar tom nem velocidade)."""
    from piper.config import SynthesisConfig
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voz.synthesize_wav(texto, w, syn_config=SynthesisConfig(length_scale=length_scale))
    buf.seek(0)
    with wave.open(buf) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768
    n = int(len(x) * C.SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


# ------------------------------------------------------------------ DSP
def _reamostrar(x, fator):
    """fator > 1 encurta (tom sobe); < 1 alonga (tom desce)."""
    n = max(1, int(len(x) / fator))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def wsola(x, fator, quadro=0.04, tolerancia=0.012):
    """Time-stretch WSOLA: saída com len(x)*fator amostras, mesmo tom."""
    N = int(quadro * C.SR)
    Hs = N // 2
    Ha = Hs / fator
    delta = int(tolerancia * C.SR)
    jan = np.hanning(N)
    n_out = int(len(x) * fator)
    out = np.zeros(n_out + N)
    peso = np.zeros(n_out + N)
    xp = np.concatenate([x, np.zeros(2 * N + 2 * delta)])
    k, ini_ant = 0, 0
    while True:
        alvo = int(k * Ha)
        if alvo >= len(x) or k * Hs >= n_out:
            break
        if k == 0:
            ini = 0
        else:
            ref = xp[ini_ant + Hs:ini_ant + Hs + N]
            lo = max(0, alvo - delta)
            hi = alvo + delta
            trecho = xp[lo:hi + N]
            corr = np.correlate(trecho, ref, mode="valid")
            ini = lo + int(np.argmax(corr))
        out[k * Hs:k * Hs + N] += xp[ini:ini + N] * jan
        peso[k * Hs:k * Hs + N] += jan
        ini_ant = ini
        k += 1
    return (out / np.maximum(peso, 1e-3))[:n_out]


def mudar_tom(x, fator):
    """Pitch-shift mantendo a duração."""
    y = _reamostrar(x, fator)
    y = wsola(y, len(x) / len(y))
    return y[:len(x)]


def _norm(y):
    return y / (np.abs(y).max() + 1e-9)


def voz_ze(x):
    y = mudar_tom(x, TOM_ZE)
    y = y - 0.5 * np.convolve(y, np.ones(11) / 11, mode="same")   # menos grave: alto-falante de TV
    y = np.tanh(_norm(y) * 1.4) / np.tanh(1.4)
    return _norm(y)


def voz_terror(x, k):
    """k 0..1: quanto mais alto, mais grave e mais suja."""
    tom = 0.78 - 0.12 * k
    base = _norm(mudar_tom(x, tom))
    sub = _norm(mudar_tom(x, tom * 0.5))                       # uma oitava abaixo
    v = base * 0.85 + sub * (0.35 + 0.3 * k)
    tt = np.arange(len(v)) / C.SR
    v = v * (1 - 0.15 * k + 0.15 * k * np.sin(2 * np.pi * 33 * tt))  # aspereza leve
    v = np.tanh(_norm(v) * (1.4 + 1.2 * k))
    v = np.convolve(v, np.ones(4) / 4, mode="same")
    out = np.zeros(len(v) + int(0.6 * C.SR))
    out[:len(v)] += v
    for d, g in [(0.12, 0.3), (0.25, 0.18), (0.39, 0.1)]:      # eco de pátio
        i = int(d * C.SR)
        out[i:i + len(v)] += v * g
    return _norm(out)


# ------------------------------------------------------------------ montagem
def gerar():
    """Retorna {"fita": array, "livre": array} (48 kHz, duração total) ou None."""
    try:
        from piper import PiperVoice
        voz = PiperVoice.load(_modelo())
    except Exception as e:  # sem Piper / sem rede
        print("  narração indisponível (%s); usando blips de voz." % e)
        return None
    n = int(C.DURACAO * C.SR)
    faixas = {"fita": np.zeros(n), "livre": np.zeros(n)}
    for texto, t0, slot, tipo, k, faixa in roteiro():
        ls = VELOCIDADE_ZE if tipo == "ze" else VELOCIDADE_TERROR
        x = _sintetizar(voz, texto, ls)
        dur = len(x) / C.SR
        if dur > slot:  # não coube: só um pouquinho mais rápido (nunca menos que 0.85)
            x = _sintetizar(voz, texto, max(0.85, ls * slot / dur))
        y = voz_ze(x) if tipo == "ze" else voz_terror(x, k)
        i0 = int(t0 * C.SR)
        m = min(len(y), n - i0)
        faixas[faixa][i0:i0 + m] += y[:m]
    # regra 7: a voz é cortada por um bipe de censura
    t = C.REGRAS_T[6] + 1.0
    m = int(1.1 * C.SR)
    tt = np.arange(m) / C.SR
    bipe = np.sin(2 * np.pi * 1000 * tt) * 0.7
    bipe[:200] *= np.linspace(0, 1, 200)
    bipe[-200:] *= np.linspace(1, 0, 200)
    faixas["livre"][int(t * C.SR):int(t * C.SR) + m] += bipe
    return faixas


def envelope_boca(voz_fita_processada):
    """Abertura da boca por frame (0..1) a partir da voz que realmente toca."""
    spf = C.SR // C.FPS
    nf = C.N_FRAMES
    x = np.abs(voz_fita_processada[:nf * spf])
    x = np.pad(x, (0, nf * spf - len(x)))
    rms = np.sqrt((x.reshape(nf, spf) ** 2).mean(axis=1))
    ativo = rms > 0.01
    ref = np.percentile(rms[ativo], 90) if ativo.any() else 1.0
    env = np.clip(rms / (ref + 1e-9), 0, 1)
    env[env < 0.12] = 0
    env[int(C.T_REGRAS * C.FPS):] = 0
    return env.astype(np.float32)
