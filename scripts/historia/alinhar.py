"""Alinhamento por DTW (MFCC) entre o áudio Gemini e a referência edge-tts (que tem tempos por palavra).
Transfere os tempos de cada palavra para a voz Gemini mantendo a mesma tokenização/índices."""
import numpy as np, subprocess, librosa
SR = 16000; HOP = 160
def load(p, a=None, b=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", f"{a:.3f}"] if a is not None else []) + (["-to", f"{b:.3f}"] if b is not None else []) + ["-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.check_output(cmd), np.float32).copy()
def feats(x):
    m = librosa.feature.mfcc(y=x, sr=SR, n_mfcc=20, hop_length=HOP, n_fft=512)[1:]
    f = np.vstack([m, librosa.feature.delta(m)])
    return (f - f.mean(1, keepdims=True)) / (f.std(1, keepdims=True) + 1e-6)
def align(ref, words_ref, qry):
    """ref/qry: sinais 16k; words_ref: [(w, t, e)] em s no ref. Retorna [(w, t, e)] em s no qry."""
    Fr, Fq = feats(ref), feats(qry)
    D, wp = librosa.sequence.dtw(X=Fr, Y=Fq, metric="cosine", step_sizes_sigma=np.array([[1, 1], [1, 0], [0, 1]]), weights_add=np.array([0, 0.1, 0.1]))
    wp = wp[::-1]; m = {}
    for i, j in wp: m.setdefault(i, []).append(j)
    nr = Fr.shape[1]; mapf = np.array([np.median(m.get(i, [0])) for i in range(nr)])
    mp = lambda t: float(np.interp(t * SR / HOP, np.arange(nr), mapf) * HOP / SR)
    return [(w, mp(t), mp(e)) for w, t, e in words_ref]
def speech_bounds(x, thr=0.015):
    n = HOP; k = len(x) // n; e = np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1)); on = np.nonzero(e > thr)[0]
    return (on[0] * n / SR, (on[-1] + 1) * n / SR) if len(on) else (0, len(x) / SR)
