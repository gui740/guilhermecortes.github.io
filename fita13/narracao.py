"""Narração do vídeo.

Motor de voz:
* Gemini TTS (Google AI Studio), se houver chave em GEMINI_API_KEY (ou um arquivo
  em GEMINI_API_KEY_FILE). Cada fala é gerada UMA vez e guardada em
  assets/narracao_gemini/ — renders seguintes não gastam cota nem precisam da chave.
* Piper (TTS local, voz pt-BR "faber") como reserva.

Duas vozes, ambas na velocidade natural da fala (sem acelerar):

* ZÉ CANHÃOZINHO (programete): tom mais agudo com pitch-shift WSOLA, que muda o
  tom sem mudar a duração. Voz de mascote simpático.
* VOZ DE TERROR (depois que o Zé se transforma, e nas regras): tom grave, uma
  segunda camada uma oitava abaixo, leve aspereza/distorção e eco de pátio.
  A cada regra fica mais grave e mais suja.

Se o Piper ou o modelo de voz não estiverem disponíveis (e não der para baixar),
retorna None e o áudio cai de volta nos "blips" de voz.
"""
import base64
import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
import wave

import numpy as np

import config as C

VOZ = "pt_BR-faber-medium"
VOZ_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/"
VELOCIDADE_ZE = 0.92      # length_scale do Piper (1 = natural; menor = um pouco mais rápido)
VELOCIDADE_TERROR = 1.0
TOM_ZE = 1.3              # +4,5 semitons (Piper)

# Gemini TTS
# A cota gratuita é de ~10 falas/dia POR MODELO: quando uma acaba, passa para a próxima.
# Os modelos 3.x leem a direção de estilo em voz alta, então recebem só o texto.
# Todas as requisições fixam languageCode pt-BR (sem isso algumas falas saíam em espanhol).
GEMINI_MODELOS = {
    "ze": ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts", "gemini-3.1-flash-tts-preview"],
    "terror": ["gemini-3.8-flash-lite-tts", "gemini-3.8-flash-tts", "gemini-3.1-flash-tts-preview"],
}
GEMINI_IDIOMA = "pt-BR"
GEMINI_VOZ_ZE = "Puck"
GEMINI_VOZ_TERROR = "Algenib"
GEMINI_ESTILO_ZE = "Say fast and excitedly, like a hyperactive cartoon mascot on a kids TV show: "
GEMINI_ESTILO_TERROR = "Say in a deep, gravelly, menacing voice, at a brisk pace without long pauses: "
TOM_ZE_GEMINI = 1.15      # o Puck já é animado; um toque mais agudo, de mascote
CACHE_GEMINI = os.path.join(C.BASE_DIR, "assets", "narracao_gemini")


def roteiro():
    """(texto falado, início, duração máxima, voz, intensidade 0..1, faixa).

    faixa "fita": passa pela mesma fita que a música (desafina/desacelera na corrupção)
    faixa "livre": por cima, sem wow
    """
    r = [("Olá, criançada! Eu sou o Zé... Canhãozinho!", C.OLA_T, C.CARTOES_INICIO - C.OLA_T - 0.1, "ze", 0, "fita")]
    falas_cartoes = [
        "Mil oitocentos e dezoito: Dom João Sexto ordena o Real Trem de Guerra!",
        "Aqui, meninos aprendizes trabalhavam nas forjas!",
        "Mil novecentos e oitenta e quatro: tombado. Hoje, o prédio descansa.",
    ]
    for i, txt in enumerate(falas_cartoes):
        r.append((txt, C.CARTOES_T[i] + 0.2, C.CARTOES_DUR[i] - 0.25, "ze", 0, "fita"))
    r.append(("Vamos visitar? O Arsenal está sempre de portas abertas!",
              C.FALA_FINAL_INICIO + 0.1, C.T_CORR - C.FALA_FINAL_INICIO - 0.15, "ze", 0, "fita"))
    # a transformação: a voz do Zé vira a voz de terror
    r.append(("O Arsenal... nunca parou... de trabalhar.", C.T_CORR + 0.4, 4.5, "terror", 0.0, "fita"))
    r.append(("Aviso aos visitantes. Leia até o fim.",
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


def _chave_gemini():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    arq = os.environ.get("GEMINI_API_KEY_FILE")
    if not k and arq and os.path.exists(arq):
        k = open(arq).read().strip()
    return k


def _cache_path(texto, tipo, modelo):
    voz = GEMINI_VOZ_ZE if tipo == "ze" else GEMINI_VOZ_TERROR
    estilo = GEMINI_ESTILO_ZE if tipo == "ze" else GEMINI_ESTILO_TERROR
    if not modelo.startswith("gemini-2.5"):
        estilo = ""
    h = hashlib.sha1(("%s|%s|%s|%s%s" % (modelo, voz, GEMINI_IDIOMA, estilo, texto)).encode()).hexdigest()[:16]
    return os.path.join(CACHE_GEMINI, "%s_%s.wav" % (tipo, h)), voz, estilo + texto


def _em_cache(texto, tipo):
    for m in GEMINI_MODELOS[tipo]:
        c = _cache_path(texto, tipo, m)[0]
        if os.path.exists(c):
            return c
    return None


_ultima_chamada = [0.0]
_sem_cota = set()   # modelos cuja cota diária acabou nesta execução


def _baixar(texto, tipo, modelo, chave):
    """Gera a fala com um modelo. Retorna o caminho do cache, "COTA" ou None."""
    caminho, voz, prompt = _cache_path(texto, tipo, modelo)
    os.makedirs(CACHE_GEMINI, exist_ok=True)
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"languageCode": GEMINI_IDIOMA,
                                                  "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz}}}}}
    url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % modelo
    for tentativa in range(6):
        espera = 21.0 - (time.time() - _ultima_chamada[0])   # cota gratuita: poucas req/min
        if espera > 0:
            time.sleep(espera)
        _ultima_chamada[0] = time.time()
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "x-goog-api-key": chave})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=180))
            b = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")
            if e.code == 429 and "PerDay" in msg:
                print("  cota diária do %s acabou." % modelo)
                return "COTA"
            if e.code in (429, 500, 503) and tentativa < 5:
                print("  gemini %d, tentando de novo em 30s..." % e.code)
                time.sleep(30)
                continue
            print("  gemini falhou: %d %s" % (e.code, msg[:200]))
            return None
        except Exception as e:
            print("  gemini falhou:", e)
            return None
    else:
        return None
    if b[:4] == b"RIFF":
        with wave.open(io.BytesIO(b)) as w:
            sr, b = w.getframerate(), w.readframes(w.getnframes())
    else:
        sr = 24000
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b)
    print("  voz gerada (%s): %s" % (modelo, texto[:50]))
    return caminho


def _gemini(texto, tipo, chave):
    """Fala do Gemini TTS a 48 kHz (com cache em disco). Retorna None se falhar."""
    caminho = _em_cache(texto, tipo)
    if caminho is None:
        if not chave:
            return None
        for m in GEMINI_MODELOS[tipo]:
            if m in _sem_cota:
                continue
            r = _baixar(texto, tipo, m, chave)
            if r == "COTA":
                _sem_cota.add(m)
                continue
            caminho = r
            break
        if caminho is None:
            return None
    with wave.open(caminho) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768
    # apara silêncio no começo/fim
    ativo = np.where(np.abs(x) > 0.02)[0]
    if len(ativo):
        x = x[max(0, ativo[0] - int(0.03 * sr)):ativo[-1] + int(0.08 * sr)]
    n = int(len(x) * C.SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def _usa_gemini():
    if _chave_gemini():
        return True
    # sem chave: usa o cache se TODAS as falas já estiverem lá
    return all(_em_cache(t, tipo) for t, _, _, tipo, _, _ in roteiro())


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


def voz_ze(x, tom=TOM_ZE):
    y = mudar_tom(x, tom)
    y = y - 0.5 * np.convolve(y, np.ones(11) / 11, mode="same")   # menos grave: alto-falante de TV
    y = np.tanh(_norm(y) * 1.4) / np.tanh(1.4)
    return _norm(y)


def voz_terror(x, k, base_grave=False):
    """k 0..1: quanto mais alto, mais grave e mais suja."""
    tom = (0.9 - 0.12 * k) if base_grave else (0.78 - 0.12 * k)
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
    gem = _usa_gemini()
    voz = None
    if gem:
        print("  narração: Gemini TTS (%s / %s)" % (GEMINI_VOZ_ZE, GEMINI_VOZ_TERROR))
    else:
        try:
            from piper import PiperVoice
            voz = PiperVoice.load(_modelo())
            print("  narração: Piper (%s)" % VOZ)
        except Exception as e:  # sem Piper / sem rede
            print("  narração indisponível (%s); usando blips de voz." % e)
            return None
    chave = _chave_gemini()
    n = int(C.DURACAO * C.SR)
    faixas = {"fita": np.zeros(n), "livre": np.zeros(n)}
    for texto, t0, slot, tipo, k, faixa in roteiro():
        x = _gemini(texto, tipo, chave) if gem else None
        if x is not None:
            dur = len(x) / C.SR
            if dur > slot:  # não coube: comprime de leve sem mudar o tom (máx. 15%)
                fator = max(slot / dur, 1 / 1.15)
                x = wsola(x, fator)
                if len(x) / C.SR > slot + 0.05:
                    print("  aviso: fala passa do tempo de tela (%.2fs > %.2fs): %s"
                          % (len(x) / C.SR, slot, texto[:40]))
            y = voz_ze(x, TOM_ZE_GEMINI) if tipo == "ze" else voz_terror(x, k, base_grave=True)
        else:
            if voz is None:
                from piper import PiperVoice
                voz = PiperVoice.load(_modelo())
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
