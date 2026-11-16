"""Monta a narração Gemini: corta cada frase do bloco pelos tempos alinhados, remove silêncios >200ms internos,
mantém pausas de piada, acelera 1.05x, normaliza e grava src/timeline.json (mesmo formato/índices de antes)."""
import json, subprocess, sys, numpy as np
sys.path.insert(0, "scripts/historia"); from alinhar import load, align, speech_bounds, SR
SPEED, GAP, MAXSIL, START, TAIL = 1.2, 0.04, 0.12, 0.08, 0.2
edge = {f["id"]: f for f in json.load(open("build/h_tts/frases.json"))["frases"]}
man = json.load(open("build/g_chunks/manifest.json"))
order = [f["id"] for f in json.load(open("build/h_tts/frases.json"))["frases"]]
pausa = {f["id"]: f["pausa"] for f in json.load(open("build/h_tts/frases.json"))["frases"]}
def ref_for(ids):
    """concatena os mp3 edge (só a parte falada) com 0.3s entre frases; devolve sinal e palavras com tempos"""
    parts, words, t = [], [], 0.0
    for fid in ids:
        f = edge[fid]; x = load(f"build/h_tts/{fid}.mp3"); a = max(0, f["palavras"][0]["t"] - 0.04); b = f["palavras"][-1]["t"] + f["palavras"][-1]["d"] + 0.06
        seg = x[int(a * SR):int(b * SR)]; parts += [seg, np.zeros(int(0.3 * SR), np.float32)]
        words += [(fid, i, p["w"], t + p["t"] - a, t + p["t"] + p["d"] - a) for i, p in enumerate(f["palavras"])]; t += len(seg) / SR + 0.3
    return np.concatenate(parts), words
def segments():
    out = {}
    for name, info in man.items():
        ids = [i for i in info["ids"] if i in edge]
        if not ids: continue
        q = load(f"build/g_chunks/{name}.wav"); ref, words = ref_for(ids)
        al = align(ref, [(w[2], w[3], w[4]) for w in words], q)
        for fid in ids:
            ws = [(w[1], a[1], a[2], w[2]) for w, a in zip(words, al) if w[0] == fid]
            out[fid] = {"src": f"build/g_chunks/{name}.wav", "a": ws[0][1], "b": ws[-1][2], "words": ws}
    # "Porra" isolado (bloco do gancho suavizou o palavrão)
    x = load("build/g_tts/g2.wav"); a, b = speech_bounds(x)
    out["g2"] = {"src": "build/g_tts/g2.wav", "a": a, "b": b, "words": [(0, a, b, "Porra")]}
    return out
def silences(x, thr=0.012, win=0.01):
    n = int(win * SR); k = len(x) // n; q = np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1)) < thr; out = []; i = 0
    while i < k:
        if q[i]:
            j = i
            while j < k and q[j]: j += 1
            out.append((i * win, j * win)); i = j
        else: i += 1
    return out
if __name__ == "__main__":
    S = segments(); chunks = [np.zeros(int(START * SR), np.float32)]; t = START; tl = []
    for n, fid in enumerate(order):
        s = S[fid]; full = load(s["src"])
        # limites da frase: expande até o silêncio mais próximo (não corta sílabas)
        a, b = max(0, s["a"] - 0.035), min(len(full) / SR, s["b"] + 0.06)
        n10 = int(0.01 * SR); e = np.sqrt(np.convolve(full ** 2, np.ones(n10) / n10, "same"))
        quiet = lambda tt: e[min(len(e) - 1, max(0, int(tt * SR)))] < 0.012
        for _ in range(25):                          # recua o início até um trecho silencioso (≤0.25s)
            if quiet(a) or a <= 0: break
            a = max(0, a - 0.01)
        for _ in range(30):                          # avança o fim até silêncio (≤0.3s)
            if quiet(b) or b >= len(full) / SR: break
            b = min(len(full) / SR, b + 0.01)
        x = full[int(a * SR):int(b * SR)].copy()
        sil = [(s0, s1) for s0, s1 in silences(x) if s1 - s0 > MAXSIL and s0 > 0.02 and s1 < len(x) / SR - 0.02]
        cuts = [(s0 + MAXSIL / 2, s1 - MAXSIL / 2) for s0, s1 in sil]
        def remap(tt):
            r = tt - a
            for c0, c1 in cuts:
                if r >= c1: r2 = c1 - c0; r -= r2
                elif r > c0: r = c0
            return r
        keep, p = [], 0.0
        for c0, c1 in cuts: keep.append(x[int(p * SR):int(c0 * SR)]); p = c1
        keep.append(x[int(p * SR):]); y = np.concatenate(keep); fd = int(0.008 * SR); y[:fd] *= np.linspace(0, 1, fd); y[-fd:] *= np.linspace(1, 0, fd)
        if n > 0: g = max(GAP, pausa[fid]); chunks.append(np.zeros(int(g * SR), np.float32)); t += g
        words = [{"w": w, "t": t + remap(wt), "e": t + remap(we)} for (_, wt, we, w) in s["words"]]
        tl.append({"id": fid, "estacao": edge[fid]["estacao"], "texto": edge[fid]["texto"], "t0": t, "t1": t + len(y) / SR, "palavras": words}); chunks.append(y); t += len(y) / SR
    chunks.append(np.zeros(int(TAIL * SR), np.float32)); x = np.concatenate(chunks)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"highpass=f=70,atempo={SPEED},loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "48000", "build/h_narracao.wav"], input=x.tobytes(), check=True)
    Sx = lambda v: round(v / SPEED, 3)
    for f in tl:
        f["t0"], f["t1"] = Sx(f["t0"]), Sx(f["t1"])
        for w in f["palavras"]: w["t"], w["e"] = Sx(w["t"]), Sx(w["e"])
    dur = float(subprocess.check_output(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", "build/h_narracao.wav"]))
    json.dump({"duracao": round(dur, 3), "voz": "Gemini gemini-3.1-flash-tts-preview / Zubenelgenubi", "frases": tl}, open("src/timeline.json", "w"), ensure_ascii=False, indent=1)
    print("duracao", round(dur, 2))
    for f in tl: print(f["id"], f["t0"], f["t1"], " ".join(f"{w['w']}@{w['t']:.2f}" for w in f["palavras"]))
