"""Linha do tempo única do vídeo: cenas, falas, eventos de som e
sincronização com assets/narracao.wav (se existir).

Toda a animação é escrita em "tempo base" (o roteiro de 70 s). Se a narração
gravada for mais longa, um mapa tempo-base -> tempo-real estica as cenas entre
uma fala e outra, sem cortar a voz.
"""
import math
import os
import subprocess

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
FPS = 30
SR = 44100
BASE_END = 70.0

SCENES = [  # (nome, início, fim) em tempo base
    ('titulo', 0.0, 5.0),
    ('level1', 5.0, 15.0),
    ('puxao', 15.0, 25.0),
    ('noite', 25.0, 35.0),
    ('perseguicao', 35.0, 52.0),
    ('jumpscare', 52.0, 58.0),
    ('gameover', 58.0, 63.0),
    ('aviso', 63.0, 70.0),
]

# (início base, fim base sem áudio, texto da legenda)
LINES = [
    (5.4, 9.0, 'Em Cuiabá, no Parque das Águas, vive um morador antigo.'),
    (9.2, 13.2, 'Ele não paga aluguel, não incomoda ninguém… e divide a margem da lagoa com as capivaras.'),
    (13.4, 15.4, 'O nome dele é Celso.'),
    (16.0, 20.3, 'Mas um dia… alguém achou que seria engraçado puxar o rabo dele.'),
    (22.3, 24.8, 'E se o Celso resolvesse revidar?'),
    (26.0, 29.9, 'Quando o sol se põe e as luzes da lagoa se acendem…'),
    (30.2, 34.4, 'dizem que é melhor não correr pela pista sozinho.'),
    (40.0, 42.8, 'Porque o Celso não esquece.'),
    (58.4, 60.4, '…Game over.'),
]

AVISO = [
    'Este vídeo é uma obra de ficção.',
    'O jacaré Celso é dócil e vive em seu habitat natural no Parque das Águas.',
    'Mas ele é um animal silvestre: acidentes podem acontecer.',
    'Não toque, não alimente, não provoque.',
    'Maus-tratos a animais é crime (Lei 9.605/98).',
]
HANDLE = '@terroremmatogrosso'

# glitches (início base, duração, força 0..1)
GLITCHES = [(0.0, 0.35, 0.8), (4.55, 0.2, 0.5), (19.5, 0.9, 1.0), (20.6, 0.25, 0.6),
            (25.0, 0.4, 0.7), (31.0, 0.35, 0.8), (34.7, 0.35, 0.9), (45.25, 0.2, 0.8),
            (52.0, 1.4, 1.0), (53.47, 0.7, 0.6), (58.0, 0.3, 0.7), (63.0, 0.25, 0.4)]


# ---------------------------------------------------------------- utilidades
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_out_bounce(t):
    t = clamp(t)
    n, d = 7.5625, 2.75
    if t < 1 / d:
        return n * t * t
    if t < 2 / d:
        t -= 1.5 / d
        return n * t * t + 0.75
    if t < 2.5 / d:
        t -= 2.25 / d
        return n * t * t + 0.9375
    t -= 2.625 / d
    return n * t * t + 0.984375


def lerp_keys(t, keys):
    """keys: [(t, v), ...] interpolação linear com easing suave entre chaves."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * ease_io(u)
    return keys[-1][1]


# ---------------------------------------------------------------- perseguição
RUN_SPEED = 92.0          # px nativos/s
PX_PER_M = 5.0
RUNNER_SCREEN_X = 150     # posição do corredor na tela (px nativo, borda esquerda do sprite)
LAMP_SPACING = 80
LAMP_OFFSET = 40
CHASE_T0 = 35.0
CHASE_T1 = 52.0
STICK_HIT = 45.25


def runner_world_x(tb):
    return 400 + RUN_SPEED * (tb - CHASE_T0)


def chase_cam_x(tb):
    return runner_world_x(tb) - RUNNER_SCREEN_X


def distance_m(tb):
    return lerp_keys(tb, [(35.0, 30.0), (40.0, 21.0), (44.0, 13.5), (45.25, 11.5), (45.9, 11.2),
                          (48.5, 5.5), (51.0, 2.0), (52.0, 0.6)])


def celso_world_x(tb):
    """borda esquerda do frame do Celso (128 px; focinho em +124)."""
    return runner_world_x(tb) + 6 - distance_m(tb) * PX_PER_M - 124


def lamp_x(k):
    return k * LAMP_SPACING + LAMP_OFFSET


def celso_nose_x(tb):
    return celso_world_x(tb) + 120


def lamp_off_time(k):
    """Tempo base em que o poste k apaga porque o Celso passou por ele."""
    x = lamp_x(k)
    tb = 37.0
    while tb < CHASE_T1:
        if celso_nose_x(tb) >= x:
            return tb
        tb += 1 / FPS
    return None


def lamp_final_off(k, tb_ref=49.0):
    """Nos segundos finais os postes à frente também morrem, em sequência."""
    x = lamp_x(k) - chase_cam_x(tb_ref)
    if -40 < x < 700:
        return 49.0 + clamp(x / 320) * 2.6
    return None


def lamp_state(k, tb):
    """1 = aceso, 0 = apagado, valores intermediários = piscando."""
    offs = [t for t in (lamp_off_time(k), lamp_final_off(k)) if t is not None]
    if not offs:
        return 1.0
    t_off = min(offs)
    if tb < t_off - 0.35:
        return 1.0
    if tb >= t_off:
        return 0.0
    # pisca antes de apagar
    ph = int((tb - t_off) * FPS)
    return 1.0 if ph % 3 else 0.25


def lamp_events():
    ev = []
    k0 = int((chase_cam_x(CHASE_T0) - 60) // LAMP_SPACING)
    k1 = int((chase_cam_x(CHASE_T1) + 400) // LAMP_SPACING)
    for k in range(k0, k1 + 1):
        offs = [t for t in (lamp_off_time(k), lamp_final_off(k)) if t is not None]
        if offs and CHASE_T0 + 1 < min(offs) < CHASE_T1:
            sx = lamp_x(k) - chase_cam_x(min(offs))
            if -20 < sx < 290:
                ev.append(min(offs))
    return sorted(ev)


def runner_frame(tb):
    """Retorna (índice de frame do visitante A, é_passo)."""
    ph = (tb - CHASE_T0) * 12
    i = int(ph) % 4
    look = ((tb - CHASE_T0) % 2.6) > 2.0 or 50.6 < tb < 51.4
    if look:
        return (9 if i < 2 else 10), False
    return [6, 7, 8, 7][i], i in (0, 2)


def step_times():
    ts = []
    n0 = int(CHASE_T0 * 12)
    n1 = int(CHASE_T1 * 12)
    for n in range(n0, n1):
        tb = n / 12
        if n % 2 == 0:
            ts.append(tb)
    # passos da corridinha na cena da noite (32.4–35)
    ts += [32.4 + k / 6 for k in range(16)]
    return ts


# ---------------------------------------------------------------- narração
def _ffmpeg_load(path, sr=SR):
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(sr), '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def _speech_segments(x, sr, min_sil):
    win = int(sr * 0.02)
    n = len(x) // win
    rms = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    peak = np.percentile(db, 98)
    floor = np.percentile(db, 10)
    thr = max(floor + 0.35 * (peak - floor), peak - 38)
    voiced = db > thr
    segs, i = [], 0
    while i < n:
        if voiced[i]:
            j = i
            while j < n and voiced[j]:
                j += 1
            segs.append([i, j])
            i = j
        else:
            i += 1
    # junta buracos curtos
    out = []
    gap_min = int(min_sil / 0.02)
    for s in segs:
        if out and s[0] - out[-1][1] < gap_min:
            out[-1][1] = s[1]
        else:
            out.append(s)
    out = [s for s in out if (s[1] - s[0]) * 0.02 > 0.12]
    return [(a * 0.02, b * 0.02) for a, b in out]


def _group_segments(segs, nlines, weights):
    """Agrupa segmentos de fala em nlines falas (programação dinâmica):
    proporção de duração ~ proporção de caracteres; pausas longas viram fronteiras."""
    n = len(segs)
    if n < nlines:
        return None
    total = segs[-1][1] - segs[0][0]
    wsum = sum(weights)
    gaps = [segs[i + 1][0] - segs[i][1] for i in range(n - 1)]
    maxgap = max(gaps) if gaps else 1
    INF = 1e18
    cost = [[INF] * (nlines + 1) for _ in range(n + 1)]
    back = [[0] * (nlines + 1) for _ in range(n + 1)]
    cost[0][0] = 0
    for i in range(1, n + 1):
        for g in range(1, min(i, nlines) + 1):
            for j in range(g - 1, i):
                if cost[j][g - 1] >= INF:
                    continue
                dur = segs[i - 1][1] - segs[j][0]
                c = ((dur / total) - (weights[g - 1] / wsum)) ** 2 * 40
                if i < n:
                    c -= 0.6 * gaps[i - 1] / maxgap
                v = cost[j][g - 1] + c
                if v < cost[i][g]:
                    cost[i][g] = v
                    back[i][g] = j
    if cost[n][nlines] >= INF:
        return None
    bounds, i = [], n
    for g in range(nlines, 0, -1):
        j = back[i][g]
        bounds.append((segs[j][0], segs[i - 1][1]))
        i = j
    return bounds[::-1]


class Timeline:
    def __init__(self, use_narration=True):
        self.narr = None
        self.narr_sr = SR
        self.line_audio = None       # [(start_in_wav, end_in_wav)] por fala
        self.knots = [(0.0, 0.0), (5.0, 5.0)]
        self.mode = 'sem narração (tempos do roteiro)'
        path = os.path.join(ASSETS, 'narracao.wav')
        real_starts = [l[0] for l in LINES]
        real_ends = [l[1] for l in LINES]
        if use_narration and os.path.exists(path):
            x = _ffmpeg_load(path)
            self.narr = x
            bounds = self._find_lines(x)
            if bounds:
                self.line_audio = bounds
                real_starts, real_ends = [], []
                prev_end = 0
                for i, ((s0, _, _), (a, b)) in enumerate(zip(LINES, bounds)):
                    # cada fala entra no seu tempo do roteiro; só é empurrada se a anterior
                    # ainda não terminou (e o trecho entre falas nunca acelera mais que 1.33x)
                    r = max(s0, prev_end + 0.25)
                    if i:
                        r = max(r, real_starts[-1] + 0.75 * (s0 - LINES[i - 1][0]))
                    real_starts.append(r)
                    prev_end = r + (b - a)
                    real_ends.append(prev_end + 0.35)
                self.mode = 'narração sincronizada por fala (%d falas detectadas)' % len(bounds)
            else:
                # fallback: arquivo inteiro a partir de 5.4 s, esticando proporcionalmente
                dur = len(x) / SR
                span = LINES[-1][1] - LINES[0][0]
                f = max(1.0, dur / span)
                real_starts = [LINES[0][0] + (l[0] - LINES[0][0]) * f for l in LINES]
                real_ends = [LINES[0][0] + (l[1] - LINES[0][0]) * f for l in LINES]
                self.mode = 'narração inteira (não detectei 9 falas), fator %.2f' % f
        for (s0, _, _), r in zip(LINES, real_starts):
            self.knots.append((s0, r))
        self.real_starts, self.real_ends = real_starts, real_ends
        last_shift = real_starts[-1] - LINES[-1][0]
        self.duration = BASE_END + max(0.0, last_shift)
        kb = np.array([k[0] for k in self.knots])
        kr = np.array([k[1] for k in self.knots])
        self._kb, self._kr = kb, kr

    def _find_lines(self, x):
        marks = os.path.join(ASSETS, 'narracao_marcas.txt')
        dur = len(x) / SR
        if os.path.exists(marks):
            vals = [float(v.replace(',', '.')) for v in open(marks).read().split()]
            if len(vals) == len(LINES):
                ends = vals[1:] + [dur]
                segs = _speech_segments(x, SR, 0.25)
                out = []
                for a, b in zip(vals, ends):
                    inside = [s for s in segs if s[0] >= a - 0.05 and s[1] <= b + 0.05]
                    out.append((a, inside[-1][1] if inside else b))
                return out
        weights = [len(l[2]) for l in LINES]
        for ms in (0.35, 0.28, 0.22, 0.16):
            segs = _speech_segments(x, SR, ms)
            g = _group_segments(segs, len(LINES), weights)
            if g:
                return g
        return None

    # tempo base -> real e inverso
    def to_real(self, tb):
        kb, kr = self._kb, self._kr
        if tb >= kb[-1]:
            return tb + (kr[-1] - kb[-1])
        return float(np.interp(tb, kb, kr))

    def to_base(self, tr):
        kb, kr = self._kb, self._kr
        if tr >= kr[-1]:
            return tr - (kr[-1] - kb[-1])
        return float(np.interp(tr, kr, kb))

    def subtitles_at(self, tr):
        for (s, e, (_, _, txt)) in zip(self.real_starts, self.real_ends, LINES):
            if s <= tr < e:
                return txt, tr - s, e - tr
        return None
