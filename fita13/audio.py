"""Síntese de todo o áudio da fita com numpy -> saida/audio.wav (48 kHz, estéreo, 16 bits)."""
import struct
import wave

import numpy as np

import config as C

SR = C.SR
N = int(C.DURACAO * SR)


# ------------------------------------------------------------------ utilitários
def _t(n):
    return np.arange(n) / SR


def _somar(buf, t0, sig, ganho=1.0):
    i0 = int(round(t0 * SR))
    if i0 >= len(buf):
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    n = min(len(sig), len(buf) - i0)
    buf[i0:i0 + n] += sig[:n] * ganho


def _env(n, ataque=0.005, queda=None):
    e = np.ones(n)
    a = max(1, int(ataque * SR))
    e[:a] = np.linspace(0, 1, a)
    if queda:
        e *= np.exp(-np.arange(n) / (queda * SR))
    r = max(1, int(0.005 * SR))
    e[-r:] *= np.linspace(1, 0, r)
    return e


def _filtro_fft(x, lo=None, hi=None, rolagem=0.15):
    """Passa-faixa suave no domínio da frequência."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi:
        g *= 1 / (1 + (f / hi) ** 8)
    if lo:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * g, n=len(x))


def _rosa(n, rng):
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = 1
    y = np.fft.irfft(X / np.sqrt(f), n=n)
    return y / (np.abs(y).max() + 1e-9)


def _quadrada(fase, duty=0.5):
    return np.where((fase % 1.0) < duty, 1.0, -1.0)


def _triangular(fase):
    return 2 * np.abs(2 * (fase % 1.0) - 1) - 1


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ------------------------------------------------------------------ camadas
def musica():
    """Melodia alegre de sintetizador barato (C maior, 120 BPM), sem wow ainda."""
    dur = C.MUSICA_T[1] - C.MUSICA_T[0] + 2
    n = int(dur * SR)
    out = np.zeros(n)
    colc = 60.0 / C.BPM / 2  # colcheia
    A = [72, 76, 79, 76, 72, 76, 79, 84]
    B = [77, 81, 84, 81, 77, 81, 79, 77]
    Cc = [79, 83, 86, 83, 79, 77, 76, 74]
    D1 = [72, 74, 76, 79, 76, 72, 72, None]
    D2 = [84, 83, 81, 79, 77, 76, 74, 72]
    frase = A + B + Cc + D1 + A + B + Cc + D2
    baixos = [48, 53, 55, 48]
    passos = int(dur / colc)
    for i in range(passos):
        t0 = i * colc
        nota = frase[i % len(frase)]
        if nota is not None:
            m = int(colc * 0.9 * SR)
            tt = _t(m)
            sig = 0.6 * _quadrada(_midi(nota) * tt, 0.5) + 0.4 * _quadrada(_midi(nota) * 1.003 * tt, 0.25)
            _somar(out, t0, sig * _env(m, 0.004, 0.18), 0.16)
        if i % 2 == 0:  # baixo em semínimas
            b = baixos[(i // 8) % 4]
            m = int(colc * 1.8 * SR)
            tt = _t(m)
            _somar(out, t0, _triangular(_midi(b) * tt) * _env(m, 0.005, 0.35), 0.3)
        # bateria
        tt = _t(int(0.12 * SR))
        if i % 4 == 0:  # bumbo
            f = 120 * np.exp(-tt * 25) + 45
            _somar(out, t0, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 22), 0.5)
        if i % 4 == 2:  # caixa
            rng = np.random.default_rng(i)
            _somar(out, t0, rng.uniform(-1, 1, len(tt)) * np.exp(-tt * 30), 0.18)
        if i % 2 == 1:  # chimbal
            rng = np.random.default_rng(1000 + i)
            h = rng.uniform(-1, 1, int(0.03 * SR))
            h = np.diff(h, prepend=0)
            _somar(out, t0, h * np.exp(-_t(len(h)) * 120), 0.08)
    return out


def aplicar_fita(src):
    """Wow & flutter + queda de pitch, lendo a música na velocidade da fita."""
    a, b = C.MUSICA_T
    n = int((b - a) * SR)
    tt = a + _t(n)
    pos = np.concatenate([[0.0], np.cumsum(C.taxa_fita(tt[:-1]))]) / SR
    idx = pos * SR
    y = np.interp(idx, np.arange(len(src)), src)
    fade = np.ones(n)
    fade[:int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
    fim = (tt > 29.0)
    fade[fim] = np.linspace(1, 0.2, fim.sum())
    return y * fade


def blip(freq, dur=0.05):
    m = int(dur * SR)
    tt = _t(m)
    return (0.7 * _quadrada(freq * tt, 0.3) + 0.3 * np.sin(2 * np.pi * freq * 2 * tt)) * _env(m, 0.002, dur / 2)


def bipe_icone(corrompido, rng):
    f1, f2 = (880.0, 1320.0)
    if corrompido:
        f1 *= rng.uniform(0.6, 0.8)
        f2 *= rng.uniform(0.55, 0.75)
    m = int(0.06 * SR)
    tt = _t(m)
    a = np.sin(2 * np.pi * f1 * tt) * _env(m, 0.002)
    b = np.sin(2 * np.pi * f2 * tt) * _env(m, 0.002)
    return np.concatenate([a, b])


def clique(rng):
    m = int(0.012 * SR)
    nz = rng.uniform(-1, 1, m)
    nz = np.diff(nz, prepend=0)
    thunk = np.sin(2 * np.pi * 180 * _t(m)) * 0.5
    return (nz + thunk) * np.exp(-_t(m) * 400)


def martelada(rng, distante=True):
    m = int(1.6 * SR)
    tt = _t(m)
    base = rng.uniform(0.9, 1.1)
    sig = np.zeros(m)
    for f, dec, amp in [(220, 0.35, 1.0), (563, 0.25, 0.7), (1187, 0.15, 0.5),
                        (1840, 0.09, 0.35), (2650, 0.06, 0.25), (3420, 0.04, 0.2)]:
        sig += amp * np.sin(2 * np.pi * f * base * tt + rng.uniform(0, 6)) * np.exp(-tt / dec)
    nz = rng.uniform(-1, 1, m) * np.exp(-tt / 0.01)
    sig += nz * 0.8
    # eco com realimentação (pátio de pedra)
    out = sig.copy()
    for d, g in [(0.11, 0.45), (0.23, 0.3), (0.37, 0.2)]:
        k = 1
        while g ** k > 0.02:
            i = int(d * k * SR)
            if i >= m:
                break
            out[i:] += sig[:m - i] * g ** k
            k += 1
    if distante:
        out = np.convolve(out, np.ones(12) / 12, mode="same")
    return out


# ------------------------------------------------------------------ montagem
def gerar(caminho=C.ARQUIVO_AUDIO, ev=None):
    rng = np.random.default_rng(C.SEED)
    if ev is None:
        import eventos
        ev = eventos.gerar()
    tt = _t(N)
    mono = np.zeros(N)

    # tom de teste 1 kHz nas barras
    a, b = C.TOM_TESTE
    i0, i1 = int(a * SR), int(b * SR)
    tom = 0.35 * np.sin(2 * np.pi * 1000 * tt[i0:i1])
    e0, e1 = int(C.ETIQUETA_T * SR) - i0, int((C.ETIQUETA_T + 2 / C.FPS) * SR) - i0
    tom[e0:e1] = 0
    mono[i0:i1] += tom

    # música com wow & flutter
    mono_m = aplicar_fita(musica())
    _somar(mono, C.MUSICA_T[0], mono_m, 0.9)

    # voz do mascote (blips sincronizados com a boca)
    escala = [0, 2, 4, 7, 9, 12]
    for j, (fa, fb, sils) in enumerate(C.SILABAS):
        r = np.random.default_rng(C.SEED + j)
        for s in sils:
            f = _midi(84 + escala[int(r.integers(0, len(escala)))])
            if s >= 24.0:
                f *= float(C.taxa_fita(s)) * 0.7
                _somar(mono, s, blip(f, 0.09), 0.2)
            else:
                _somar(mono, s, blip(f), 0.16)

    # bipes dos ícones
    for t0, corr in C.eventos_icones():
        _somar(mono, t0, bipe_icone(corr, rng), 0.22)

    # máquina de escrever nas regras
    for i in range(len(C.REGRAS)):
        ts, cps = C.regra_digitacao(i)
        txt = C.regra_texto_digitado(i)
        fim_regra = C.REGRAS_INICIO + (i + 1) * C.REGRA_DUR
        for k, ch in enumerate(txt):
            tc = ts + k / cps
            if tc >= fim_regra:
                break
            if ch != " ":
                _somar(mono, tc, clique(rng), 0.28 if ch != "█" else 0.4)

    # marteladas de forja: baixinhas nas regras, mais altas no pátio
    t = 33.0
    while t < 69.7:
        if t < 50:
            g = 0.04 + 0.05 * (t - 33) / 17
        elif t < 62:
            g = 0.07
        else:
            g = 0.12 + 0.2 * (t - 62) / 8
        _somar(mono, t, martelada(rng, distante=t < 62), g)
        t += rng.uniform(1.1, 2.6) if t < 62 else rng.uniform(0.7, 1.5)

    # alerta 853 + 960 Hz em pulsos
    a, b = C.ALERTA_TOM_T
    i0, i1 = int(a * SR), int(b * SR)
    seg = tt[i0:i1]
    on = np.array([C.alerta_tom_ligado(x) for x in seg[::480]])
    on = np.repeat(on, 480)[:len(seg)].astype(float)
    on = np.convolve(on, np.ones(240) / 240, mode="same")
    alerta = 0.5 * (np.sin(2 * np.pi * 853 * seg) + np.sin(2 * np.pi * 960 * seg))
    alerta = np.tanh(alerta * 1.4) * 0.32
    chiado = rng.uniform(-1, 1, len(seg)) * 0.1 * (1 - on)
    mono[i0:i1] += alerta * on + chiado

    # pátio: drone grave crescendo + stinger
    a, b = 62.0, C.PATIO_STINGER_T
    i0, i1 = int(a * SR), int(b * SR)
    seg = tt[i0:i1]
    cres = ((seg - a) / (b - a)) ** 1.5
    drone = (np.sin(2 * np.pi * 45 * seg) + 0.8 * np.sin(2 * np.pi * 52.3 * seg)
             + 0.3 * np.sin(2 * np.pi * 90 * seg + np.sin(2 * np.pi * 0.3 * seg)))
    mono[i0:i1] += drone * (0.06 + 0.32 * cres)
    m = int((70.0 - C.PATIO_STINGER_T) * SR)
    st_t = _t(m)
    saw = 2 * ((110 * st_t) % 1) - 1
    stinger = np.tanh(4 * (saw + 0.9 * rng.uniform(-1, 1, m) + np.sin(2 * np.pi * 61 * st_t)))
    _somar(mono, C.PATIO_STINGER_T, stinger, 0.95)

    # estática fraca no fim
    a, b = C.FIM_PRETO, C.FIM_CARTAO
    i0, i1 = int(a * SR), int(b * SR)
    mono[i0:i1] += rng.uniform(-1, 1, i1 - i0) * 0.06

    # eventos de falha compartilhados com o vídeo
    for f0, f1 in ev["transicoes"]:
        a, b = f0 / C.FPS, f1 / C.FPS
        m = int((b - a) * SR)
        _somar(mono, a, rng.uniform(-1, 1, m) * _env(m, 0.003), 0.35)
        mono[int(a * SR):int(a * SR) + m] *= 0.25  # o sinal some na estática
        _somar(mono, a, rng.uniform(-1, 1, m) * _env(m, 0.003), 0.3)
    for f0, dur in ev["tracking"]:
        a = f0 / C.FPS
        m = int(dur / C.FPS * SR)
        i0 = int(a * SR)
        w = np.sin(np.linspace(0, np.pi, m))
        trem = 1 - 0.5 * w * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * _t(m)))
        mono[i0:i0 + m] *= trem[:len(mono[i0:i0 + m])]
        _somar(mono, a, rng.uniform(-1, 1, m) * w * 0.08)
    vistos = set()
    for f, _, _, _ in ev["dropouts"]:
        if f in vistos:
            continue
        vistos.add(f)
        a = f / C.FPS
        m = int(rng.uniform(0.02, 0.05) * SR)
        i0 = int(a * SR)
        mono[i0:i0 + m] *= 0.15
        _somar(mono, a, rng.uniform(-1, 1, m) * 0.12)
    for f0, dur, tipo in ev["glitches"]:
        a = f0 / C.FPS
        m = int(dur / C.FPS * SR)
        i0 = int(a * SR)
        if tipo == "congelar":  # gagueira: repete um pedacinho
            pedaco = mono[i0:i0 + int(0.04 * SR)].copy()
            reps = np.tile(pedaco, m // len(pedaco) + 1)[:m]
            mono[i0:i0 + m] = reps
        else:
            _somar(mono, a, rng.uniform(-1, 1, m) * 0.25)

    # camada base: chiado de fita (rosa) + zumbido de 60 Hz
    hum = (np.sin(2 * np.pi * 60 * tt) + 0.5 * np.sin(2 * np.pi * 120 * tt)
           + 0.3 * np.sin(2 * np.pi * 180 * tt) + 0.15 * np.sin(2 * np.pi * 300 * tt)) * 0.012
    L = mono + hum + _rosa(N, rng) * 0.035
    R = mono + hum + _rosa(N, rng) * 0.035
    # leve abertura estéreo na música
    d = int(0.0004 * SR)
    R[d:] = R[d:] * 0.85 + mono[:-d] * 0.15 - mono[d:] * 0.15

    # degradação: passa-baixa ~8 kHz e bitcrush
    out = []
    for ch in (L, R):
        ch = _filtro_fft(ch, lo=25, hi=8000)
        ch = ch / (np.abs(ch).max() + 1e-9) * 0.9
        ch = np.round(ch * 2 ** 9) / 2 ** 9      # ~10 bits
        out.append(ch)
    est = np.stack(out, axis=1)
    est = est / (np.abs(est).max() + 1e-9) * 10 ** (-1 / 20)   # pico -1 dBFS

    # silêncio absoluto: telas azuis do VCR e corte para preto
    for a, b in [(0.0, C.ABERTURA_AZUL_FIM), (70.0, C.FIM_PRETO), (C.FIM_AZUL, C.DURACAO)]:
        est[int(a * SR):int(b * SR)] = 0
    # pequenas rampas nas bordas do silêncio para não estalar
    r = int(0.004 * SR)
    i = int(C.ABERTURA_AZUL_FIM * SR)
    est[i:i + r] *= np.linspace(0, 1, r)[:, None]
    i = int(C.FIM_AZUL * SR)
    est[i - r:i] *= np.linspace(1, 0, r)[:, None]

    pcm = (np.clip(est, -1, 1) * 32767).astype("<i2")
    with wave.open(caminho, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return caminho


if __name__ == "__main__":
    import os
    os.makedirs(C.SAIDA_DIR, exist_ok=True)
    print(gerar())
