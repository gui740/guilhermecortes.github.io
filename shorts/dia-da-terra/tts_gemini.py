"""Narração com Gemini TTS (Google AI Studio).
Uso: GEMINI_KEY_FILE=/caminho/da/chave python tts_gemini.py out_dir [voz]
Gera n00.wav, n01.wav... (uma fala por linha de narracao.json) e words.json
com o tempo estimado de cada palavra (para as legendas)."""
import base64, json, os, re, sys, time, wave, urllib.request, urllib.error
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get("TTS_MODEL", "gemini-2.5-flash-preview-tts")
STYLE = ("Narre em português do Brasil, como o narrador do canal de curiosidades PERA, OI? no YouTube Shorts: "
         "voz jovem, empolgada, ritmo ágil, com ênfase nos números e pausas dramáticas nas reticências. "
         "Leia exatamente o texto: ")


def key():
    p = os.environ.get("GEMINI_KEY_FILE")
    if p:
        return open(p).read().strip()
    return os.environ["GEMINI_API_KEY"]


def tts(text, voice, style=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {"contents": [{"parts": [{"text": (STYLE if style is None else style) + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for attempt in range(8):
        req = urllib.request.Request(url, json.dumps(body).encode(),
                                     {"Content-Type": "application/json", "x-goog-api-key": key()})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            part = d["candidates"][0]["content"]["parts"][0]["inlineData"]
            rate = int(re.search(r"rate=(\d+)", part["mimeType"]).group(1))
            pcm = np.frombuffer(base64.b64decode(part["data"]), "<i2")
            return pcm, rate
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if "quota" in msg.lower() and "exceeded your current quota" in msg.lower() and attempt >= 1:
                raise
            wait = 20 * (attempt + 1) if e.code in (429, 500, 503) else None
            print(f"  HTTP {e.code}: {msg[:160]}", flush=True)
            if wait is None:
                raise
            time.sleep(wait)
        except (KeyError, IndexError) as e:
            print("  resposta sem áudio, tentando de novo", flush=True)
            time.sleep(5)
    raise RuntimeError("falhou: " + text)


def trim(pcm, rate, thr=0.02):
    x = pcm.astype(np.float32) / 32768
    win = int(rate * 0.01)
    env = np.sqrt(np.convolve(x * x, np.ones(win) / win, "same"))
    idx = np.nonzero(env > thr)[0]
    if len(idx) == 0:
        return pcm, env
    a = max(0, idx[0] - int(0.02 * rate))
    b = min(len(pcm), idx[-1] + int(0.06 * rate))
    return pcm[a:b], env[a:b]


def estimate_words(text, env, rate):
    """tempo de cada palavra: proporcional às letras, encaixando as pausas
    de pontuação nos silêncios detectados no áudio"""
    words = text.split()
    dur = len(env) / rate
    # silêncios internos > 120 ms
    quiet = env < 0.02
    gaps, i, n = [], 0, len(quiet)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) / rate > 0.12 and i > 0 and j < n:
                gaps.append((i / rate, j / rate))
            i = j
        else:
            i += 1
    # grupos de palavras separados por pontuação
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[,.!?:;…]$", w):
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    if len(gaps) >= len(groups) - 1 and len(groups) > 1:
        gaps = sorted(sorted(gaps, key=lambda g: g[0] - g[1])[: len(groups) - 1])
        spans, t0 = [], 0.0
        for g in gaps:
            spans.append((t0, g[0])); t0 = g[1]
        spans.append((t0, dur))
    else:
        groups, spans = [words], [(0.0, dur)]
    out = []
    for grp, (a, b) in zip(groups, spans):
        wts = [len(re.sub(r"\W", "", w)) + 2 for w in grp]
        tot = sum(wts)
        t = a
        for w, wt in zip(grp, wts):
            d = (b - a) * wt / tot
            out.append({"w": w.strip(".,!?:;…"), "t": round(t, 3), "d": round(d, 3)})
            t += d
    return out


BATCH_STYLE = ("Narre em português do Brasil, como o narrador do canal de curiosidades PERA, OI? no YouTube Shorts: "
               "voz jovem, empolgada, ritmo ágil, com ênfase nos números. Cada linha abaixo é uma frase separada: "
               "faça uma pausa de UM SEGUNDO INTEIRO entre uma linha e a próxima. Leia exatamente o texto:\n\n")


def split_batch(pcm, rate, n, texts=None):
    """corta o áudio em n falas: entre todos os silêncios, escolhe os n-1 cortes cuja
    duração de cada trecho mais combina com o tamanho do texto (programação dinâmica)"""
    x = pcm.astype(np.float32) / 32768
    win = int(rate * 0.02)
    env = np.sqrt(np.convolve(x * x, np.ones(win) / win, "same"))
    quiet = env < 0.015
    gaps, i, N = [], 0, len(quiet)
    while i < N:
        if quiet[i]:
            j = i
            while j < N and quiet[j]:
                j += 1
            if i > 0 and j < N and (j - i) / rate > 0.18:
                gaps.append((i, j))
            i = j
        else:
            i += 1
    cands = [(a + b) // 2 for a, b in gaps]
    glen = [(b - a) / rate for a, b in gaps]
    w = [len(t) + 8 for t in texts] if texts else [1] * n
    tot = sum(w)
    exp_frac = np.cumsum(w) / tot
    import math
    M = len(cands)
    INF = 1e18
    # dp[k][m]: melhor custo com k cortes, último corte = candidato m
    dp = [[INF] * M for _ in range(n)]
    back = [[-1] * M for _ in range(n)]
    def seg_cost(a, b, k):
        d = (b - a) / N
        e = w[k] / tot
        return math.log(max(d, 1e-4) / e) ** 2
    for m in range(M):
        dp[1][m] = seg_cost(0, cands[m], 0) - 0.15 * glen[m]
    for k in range(2, n):
        for m in range(M):
            best, bi = INF, -1
            for q in range(m):
                if dp[k - 1][q] < INF:
                    c = dp[k - 1][q] + seg_cost(cands[q], cands[m], k - 1)
                    if c < best:
                        best, bi = c, q
            dp[k][m] = best - 0.15 * glen[m]
            back[k][m] = bi
    best, bm = INF, -1
    for m in range(M):
        if dp[n - 1][m] < INF:
            c = dp[n - 1][m] + seg_cost(cands[m], N, n - 1)
            if c < best:
                best, bm = c, m
    cut_idx = []
    k, m = n - 1, bm
    while k >= 1 and m >= 0:
        cut_idx.append(m)
        m = back[k][m]
        k -= 1
    cut_idx = cut_idx[::-1]
    cuts = [0] + [cands[m] for m in cut_idx] + [N]
    return [pcm[cuts[k]:cuts[k + 1]] for k in range(len(cuts) - 1)], [glen[m] for m in cut_idx]


def main_batch(out, voice):
    os.makedirs(out, exist_ok=True)
    lines = json.load(open(os.path.join(HERE, "narracao.json")))
    raw = os.path.join(out, "lote.wav")
    if not os.path.exists(raw):
        pcm, rate = tts("\n".join(l["text"] for l in lines), voice, BATCH_STYLE)
        with wave.open(raw, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
    with wave.open(raw) as w:
        rate = w.getframerate(); pcm = np.frombuffer(w.readframes(w.getnframes()), "<i2")
    segs, gl = split_batch(pcm, rate, len(lines), [l["text"] for l in lines])
    if len(segs) != len(lines):
        raise SystemExit(f"cortes: {len(segs)} != {len(lines)}")
    words, ratios = {}, []
    for i, (l, sg) in enumerate(zip(lines, segs)):
        sg, env = trim(sg, rate)
        f = os.path.join(out, f"n{i:02d}.wav")
        with wave.open(f, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(sg.tobytes())
        words[f"n{i:02d}"] = estimate_words(l["text"], env, rate)
        r = (len(sg) / rate) / max(1, len(l["text"]))
        ratios.append(r)
        print(f"[{i:02d}] {len(sg) / rate:5.2f}s  {r * 100:4.1f} cs/letra  {l['text']}")
    med = sorted(ratios)[len(ratios) // 2]
    bad = [i for i, r in enumerate(ratios) if r > med * 1.9 or r < med * 0.5]
    print("menor pausa usada: %.2fs" % min(gl))
    if bad:
        raise SystemExit(f"cortes suspeitos nas falas {bad}")
    json.dump(words, open(os.path.join(out, "words.json"), "w"), ensure_ascii=False, indent=0)


def main(out, voice="Puck"):
    os.makedirs(out, exist_ok=True)
    lines = json.load(open(os.path.join(HERE, "narracao.json")))
    words = {}
    for i, l in enumerate(lines):
        f = os.path.join(out, f"n{i:02d}.wav")
        print(f"[{i:02d}] {l['text']}", flush=True)
        if not os.path.exists(f):
            pcm, rate = tts(l["text"], voice)
            pcm, env = trim(pcm, rate)
            with wave.open(f, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
                w.writeframes(pcm.tobytes())
        with wave.open(f) as w:
            rate = w.getframerate()
            pcm = np.frombuffer(w.readframes(w.getnframes()), "<i2")
        _, env = trim(pcm, rate)
        words[f"n{i:02d}"] = estimate_words(l["text"], env, rate)
        print(f"     {len(pcm) / rate:.2f}s", flush=True)
    json.dump(words, open(os.path.join(out, "words.json"), "w"), ensure_ascii=False, indent=0)


if __name__ == "__main__":
    if os.environ.get("TTS_MODE", "batch") == "batch":
        main_batch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "Puck")
    else:
        main(sys.argv[1], *(sys.argv[2:3]))
