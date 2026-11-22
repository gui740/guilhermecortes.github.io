"""Sintetiza todos os efeitos sonoros do vídeo (autoria própria, sem samples de terceiros).

Uso: python3 scripts/sfx.py  -> grava WAVs em public/sao-paulo/audio/sfx/
"""
import os
import numpy as np
import wave

SR = 48000
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "sao-paulo", "audio", "sfx")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(1930)


def save(name, x):
    x = np.asarray(x, dtype=np.float64)
    peak = np.max(np.abs(x)) or 1
    x = x / peak * 0.89
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    print("sfx", name, round(len(x) / SR, 2), "s")


def t(d):
    return np.arange(int(d * SR)) / SR


def lp(x, a):
    """Filtro passa-baixa de 1 polo (a em 0..1, maior = mais grave)."""
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = a * acc + (1 - a) * v
        y[i] = acc
    return y


def hp(x, a):
    return x - lp(x, a)


# Moeda: parciais inarmônicas de um disco metálico (razões aproximadas de placa circular)
COIN_RATIOS = [1.0, 2.09, 3.42, 4.95, 6.7, 8.6]


def clink(d=0.9, f0=2350, amp=1.0, decay=7.0, bright=1.0):
    tt = t(d)
    x = np.zeros_like(tt)
    for k, r in enumerate(COIN_RATIOS):
        f = f0 * r
        if f > SR / 2.2:
            continue
        x += (bright ** k) * np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) * np.exp(-tt * decay * (1 + 0.6 * k))
    click = rng.normal(0, 1, len(tt)) * np.exp(-tt * 400)
    return amp * (x + 0.6 * hp(click, 0.6))


def coin_spin():
    """Moeda girando no ar: zumbido metálico com tremolo que acelera (0 a 1.5 s)."""
    d = 1.55
    tt = t(d)
    ring = sum(np.sin(2 * np.pi * 2350 * r * tt) / (k + 1.5) for k, r in enumerate(COIN_RATIOS[:4]))
    rate = 9 + 14 * tt / d  # giros por segundo
    phase = 2 * np.pi * np.cumsum(rate) / SR
    trem = np.abs(np.sin(phase)) ** 3
    whoosh = lp(rng.normal(0, 1, len(tt)), 0.93) * (0.4 + 0.6 * trem)
    env = np.minimum(1, tt / 0.08) * np.minimum(1, (d - tt) / 0.05)
    return env * (0.45 * ring * (0.25 + 0.75 * trem) + 0.5 * whoosh)


def coin_bounce_sequence():
    """Quiques + rolamento até parar em pé. Tempos relativos ao primeiro quique."""
    hits = [(0.0, 1.0), (0.36, 0.72), (0.60, 0.5), (0.74, 0.32)]
    d = 1.6
    x = np.zeros(int(d * SR))
    for at, a in hits:
        c = clink(d=0.8, f0=2350 * (1 + rng.uniform(-0.02, 0.02)), amp=a, decay=6)
        i = int(at * SR)
        x[i:i + len(c)] += c[: len(x) - i]
    # "wobble" final: batidinhas rápidas que aceleram e param (moeda assentando em pé)
    at = 0.80
    gap = 0.045
    a = 0.22
    while gap > 0.008 and at < 0.84 + 0.25:
        c = clink(d=0.25, f0=2400, amp=a, decay=18, bright=0.7)
        i = int(at * SR)
        x[i:i + len(c)] += c[: len(x) - i]
        at += gap
        gap *= 0.72
        a *= 0.85
    return x


def impact():
    """Pancada grave + estalo (entrada do escudo)."""
    tt = t(1.8)
    f = 38 + 90 * np.exp(-tt * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
    noise = lp(rng.normal(0, 1, len(tt)), 0.7) * np.exp(-tt * 14)
    snap = hp(rng.normal(0, 1, len(tt)), 0.3) * np.exp(-tt * 90)
    return 1.0 * boom + 0.5 * noise + 0.35 * snap


def whoosh(d=0.7, up=True):
    tt = t(d)
    n = rng.normal(0, 1, len(tt))
    env = np.sin(np.pi * tt / d) ** 2
    # varre o filtro (aproximação: mistura de duas bandas)
    lo = lp(n, 0.97)
    hi = hp(lp(n, 0.6), 0.9)
    mix = (tt / d) if up else (1 - tt / d)
    return env * ((1 - mix) * lo * 3 + mix * hi)


def coin_flyby():
    """Transição: moeda girando passando pela tela."""
    w = whoosh(0.75)
    tt = t(0.75)
    ring = np.sin(2 * np.pi * 2350 * tt) * np.abs(np.sin(2 * np.pi * 10 * tt)) * np.sin(np.pi * tt / 0.75)
    return w + 0.25 * ring


def crack():
    """Escudo quebrando: estalos + estilhaços."""
    d = 1.6
    x = np.zeros(int(d * SR))
    tt = t(d)
    x += impact()[: len(x)] * 0.6
    for _ in range(26):
        at = rng.uniform(0, 0.5) ** 1.6
        c = hp(rng.normal(0, 1, int(0.06 * SR)), 0.2) * np.exp(-t(0.06) * rng.uniform(60, 160))
        i = int(at * SR)
        x[i:i + len(c)] += c * rng.uniform(0.3, 1)
    for _ in range(14):  # pedacinhos caindo
        at = rng.uniform(0.25, 1.2)
        c = clink(d=0.2, f0=rng.uniform(2800, 5200), amp=rng.uniform(0.05, 0.18), decay=30, bright=0.5)
        i = int(at * SR)
        x[i:i + len(c)] += c[: len(x) - i]
    return x


def reassemble():
    """Peças voltando: estalos ao contrário + riser."""
    d = 2.2
    x = np.zeros(int(d * SR))
    tt = t(d)
    riser = lp(rng.normal(0, 1, len(tt)), 0.9) * (tt / d) ** 2
    x += 0.5 * riser
    for k in range(9):
        at = 0.2 + k * 0.2
        c = clink(d=0.25, f0=1800 + 120 * k, amp=0.35, decay=20, bright=0.6)
        i = int(at * SR)
        x[i:i + len(c)] += c[: len(x) - i]
    return x


def stamp():
    """Carimbo de data."""
    tt = t(0.5)
    thump = np.sin(2 * np.pi * (70 + 60 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 18)
    slap = lp(rng.normal(0, 1, len(tt)), 0.4) * np.exp(-tt * 45)
    return thump + 0.6 * slap


def tick():
    tt = t(0.05)
    return np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 120)


def score_sting():
    """Vinheta de placar de TV: dois tons + brilho."""
    tt = t(0.9)
    x = np.zeros_like(tt)
    for i, (f, at) in enumerate([(660, 0.0), (990, 0.09)]):
        s = np.zeros_like(tt)
        n = int(at * SR)
        tt2 = tt[: len(tt) - n]
        s[n:] = (np.sin(2 * np.pi * f * tt2) + 0.3 * np.sin(2 * np.pi * 2 * f * tt2)) * np.exp(-tt2 * 5)
        x += s
    return x + 0.4 * whoosh(0.9)[: len(x)]


def count_up(d=1.4, n=24):
    x = np.zeros(int(d * SR))
    for k in range(n):
        at = d * (1 - (1 - k / n) ** 0.6) * 0.92
        c = tick() * (0.5 + 0.5 * k / n)
        i = int(at * SR)
        x[i:i + len(c)] += c[: len(x) - i]
    return x


def bass_drop():
    tt = t(1.2)
    f = 60 * np.exp(-tt * 0.8)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.5) * np.minimum(1, tt / 0.01)


def pop():
    tt = t(0.15)
    return np.sin(2 * np.pi * (300 + 900 * np.exp(-tt * 50)) * tt) * np.exp(-tt * 30)


def flap_clatter(d=1.1, n=34):
    """Letreiro de placas girando: cliques secos e rápidos."""
    x = np.zeros(int(d * SR))
    for k in range(n):
        at = (k / n) ** 0.8 * (d - 0.08) + rng.uniform(-0.01, 0.01)
        tt = t(0.03)
        c = hp(rng.normal(0, 1, len(tt)), 0.5) * np.exp(-tt * 260) + 0.4 * np.sin(2 * np.pi * 1300 * tt) * np.exp(-tt * 200)
        i = max(0, int(at * SR))
        x[i:i + len(c)] += c[: len(x) - i] * rng.uniform(0.5, 1.0)
    return x


if __name__ == "__main__":
    save("letreiro", flap_clatter())
    save("moeda-girando", coin_spin())
    save("moeda-quicando", coin_bounce_sequence())
    save("impacto", impact())
    save("whoosh", whoosh())
    save("moeda-transicao", coin_flyby())
    save("quebra", crack())
    save("remonta", reassemble())
    save("carimbo", stamp())
    save("placar", score_sting())
    save("contagem", count_up())
    save("drop", bass_drop())
    save("pop", pop())
