"""Limpa a narração: redução de ruído, remoção de retakes, corte de silêncios >200ms.
Uso: python3 scripts/clean_audio.py assets/narracao.m4a build/voz_edit.wav
A normalização para -16 LUFS é feita depois com ffmpeg loudnorm (2 passadas)."""
import sys, subprocess, numpy as np, soundfile as sf, noisereduce as nr

src, dst = sys.argv[1], sys.argv[2]
SR = 48000
raw = subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","1","-ar",str(SR),"-f","f32le","-"],
                     capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32).copy()

# 1) redução de ruído com perfil do trecho sem fala no fim da gravação
noise = a[int(70.2*SR):int(72.4*SR)]
a = nr.reduce_noise(y=a, sr=SR, y_noise=noise, stationary=True, prop_decrease=0.85)
a = np.convolve(a, [1.0], mode="same")
# high-pass leve (remove ronco < 80 Hz)
from scipy.signal import butter, sosfilt
a = sosfilt(butter(2, 80, "hp", fs=SR, output="sos"), a).astype(np.float32)

# 2) trechos mantidos (última/melhor tomada de cada frase; tempos no arquivo original)
KEEP = [  # (início, fim, pausa_antes_s)
    (2.20, 12.45, 0.0),   # Pais levaram ... não é filme infantil
    (17.15, 20.55, 0.32), # [pausa antes do título] É Buddy, um dos filmes de terror mais comentados do ano
    (23.85, 30.75, 0.10), # A história: um programa infantil ... amizade
    (33.25, 35.45, 0.08), # até que uma criança se recusa a brincar
    (39.90, 42.40, 0.08), # e o Buddy mostra quem ele é de verdade
    (43.40, 69.30, 0.10), # e como tanta gente caiu nessa ... segue o Talking Horror
]
# pausas preservadas dentro dos trechos (antes dos números): tempo original -> pausa mantida
KEEP_PAUSE_BEFORE = {58.22: 0.28}  # "custou 5 milhões"

HOP = int(0.01*SR)
def env_db(x):
    n = len(x)//HOP
    f = x[:n*HOP].reshape(n, HOP)
    return 20*np.log10(np.sqrt((f**2).mean(1))+1e-9)

e = env_db(a)
thr = np.percentile(e, 12) + 14  # limiar fala/silêncio
MAXGAP, NEWGAP, FADE = 0.20, 0.07, int(0.008*SR)

out = []
def fade(x):
    x = x.copy(); n = min(FADE, len(x)//2)
    if n: x[:n] *= np.linspace(0,1,n); x[-n:] *= np.linspace(1,0,n)
    return x

for (s, t, pre) in KEEP:
    if pre: out.append(np.zeros(int(pre*SR), np.float32))
    i0, i1 = int(s*100), int(t*100)
    speech = e[i0:i1] > thr
    # suaviza: ignora buracos < 40ms
    k = 0; segs = []; cur = None
    for j, v in enumerate(speech):
        if v and cur is None: cur = j
        if not v and cur is not None:
            segs.append([cur, j]); cur = None
    if cur is not None: segs.append([cur, len(speech)])
    merged = []
    for sg in segs:
        if merged and (sg[0]-merged[-1][1]) < 4: merged[-1][1] = sg[1]
        else: merged.append(sg)
    # remove ruídos curtos isolados (<50ms)
    merged = [m for m in merged if m[1]-m[0] >= 5]
    pad = 3  # 30ms de folga em volta da fala
    prev_end = None
    for m in merged:
        ms, me = max(0, m[0]-pad), min(len(speech), m[1]+pad)
        if prev_end is not None:
            gap = (ms - prev_end)/100
            gs = (i0 + prev_end)/100
            keep = None
            for tt, pp in KEEP_PAUSE_BEFORE.items():
                if gs - 0.1 <= tt <= (i0+ms)/100 + 0.15: keep = pp
            if keep is not None: out.append(np.zeros(int(max(0, keep-0.0)*SR), np.float32))
            elif gap > MAXGAP: out.append(np.zeros(int(NEWGAP*SR), np.float32))
            else: out.append(a[(i0+prev_end)*HOP:(i0+ms)*HOP])
        out.append(fade(a[(i0+ms)*HOP:(i0+me)*HOP]))
        prev_end = me

y = np.concatenate(out)
sf.write(dst, y, SR, subtype="FLOAT")
print(f"duração editada: {len(y)/SR:.2f}s")
