"""Narração do Zé Canhãozinho (TTS local com Piper, voz pt-BR "faber").

A voz de mascote sai de um truque simples: sintetiza a fala mais devagar
(length_scale) e depois acelera por reamostragem. Isso sobe o tom e os
formantes juntos — voz de boneco. Nas regras o fator vai subindo, e a voz
fica cada vez mais aguda.

Se o Piper ou o modelo de voz não estiverem disponíveis (e não der para
baixar), retorna None e o áudio cai de volta nos "blips" de voz.
"""
import io
import os
import urllib.request
import wave

import numpy as np

import config as C

VOZ = "pt_BR-faber-medium"
VOZ_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/"
VELOCIDADE = 0.7   # duração final / duração natural do Piper (menor = fala mais rápida)

# (texto falado, início, duração máxima, fator de tom, faixa)
# faixa "fita": passa pela mesma fita que a música (desafina/desacelera na corrupção)
# faixa "livre": por cima, sem wow


def roteiro():
    r = [("Olá! Eu sou o Zé Canhãozinho!", C.OLA_T, 2.2, 1.65, "fita")]
    falas_cartoes = [
        "Mil oitocentos e dezoito: Dom João Sexto ordena o Real Trem de Guerra!",
        "Estilo neoclássico, muros altos, e uma varanda em volta do pátio!",
        "Na Guerra do Paraguai, aqui consertavam armas dos dois lados!",
        "De mil oitocentos e quarenta e dois a mil oitocentos e noventa e nove, "
        "meninos aprendizes trabalhavam nas forjas!",
        "Mil novecentos e oitenta e quatro: tombado. Hoje, o prédio descansa.",
    ]
    for i, txt in enumerate(falas_cartoes):
        r.append((txt, C.CARTOES_T[i] + 0.2, C.CARTOES_DUR[i] - 0.3, 1.65, "fita"))
    r.append(("Vamos visitar? O Arsenal está sempre de portas abertas!",
              C.FALA_FINAL_INICIO + 0.1, C.T_CORR - C.FALA_FINAL_INICIO - 0.2, 1.7, "fita"))
    r.append(("O Arsenal... nunca parou... de trabalhar.", C.T_CORR + 0.4, 2.2, 1.65, "fita"))
    # regras: a mesma voz, cada vez mais aguda
    r.append(("Arsenal de Guerra. Aviso aos visitantes. Leia até o fim.",
              C.T_REGRAS + 0.15, C.REGRAS_INTRO_DUR - 0.3, 1.85, "livre"))
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
        tom = 1.95 + 0.75 * i / (n - 1)
        r.append((txt, C.REGRAS_T[i] + 0.25, C.REGRAS_DUR[i] - 0.3, tom, "livre"))
    r.append(("Até amanhã, aprendiz.", C.FIM_APRENDIZ_T, 1.4, 2.8, "livre"))
    return r


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
    from piper.config import SynthesisConfig
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voz.synthesize_wav(texto, w, syn_config=SynthesisConfig(length_scale=length_scale))
    buf.seek(0)
    with wave.open(buf) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768
    return x, sr


def _mascote(x, sr, tom):
    """Acelera por reamostragem (tom e formantes sobem juntos) e dá cara de brinquedo."""
    n_out = int(len(x) * C.SR / sr / tom)
    y = np.interp(np.linspace(0, len(x) - 1, n_out), np.arange(len(x)), x)
    y = np.tanh(y * 1.8) / np.tanh(1.8)            # leve saturação de alto-falante barato
    y = y - 0.6 * np.convolve(y, np.ones(9) / 9, mode="same")  # tira grave: som de rádio/boneco
    return y / (np.abs(y).max() + 1e-9)


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
    for texto, t0, slot, tom, faixa in roteiro():
        ls = VELOCIDADE * tom
        x, sr = _sintetizar(voz, texto, ls)
        dur = len(x) / sr / tom
        if dur > slot:  # não coube: fala um pouco mais rápido
            x, sr = _sintetizar(voz, texto, ls * slot / dur * 0.97)
        y = _mascote(x, sr, tom)
        i0 = int(t0 * C.SR)
        m = min(len(y), n - i0)
        faixas[faixa][i0:i0 + m] += y[:m]
    # regra 7: a voz é cortada por um bipe de censura
    t = C.REGRAS_T[6] + 1.0
    m = int(1.1 * C.SR)
    tt = np.arange(m) / C.SR
    bipe = np.sin(2 * np.pi * 1000 * tt) * 0.8
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
    env = np.clip(rms / (np.percentile(rms[rms > 0.01], 90) + 1e-9 if (rms > 0.01).any() else 1), 0, 1)
    env[env < 0.12] = 0
    env[int(C.T_REGRAS * C.FPS):] = 0
    return env.astype(np.float32)
