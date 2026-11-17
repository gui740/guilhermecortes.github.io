"""Gera a narração do episódio a partir de narracao.json.

Modo principal: Gemini TTS (voz Gacrux) em poucos pedidos grandes, para caber na cota diária;
cada pedido é transcrito com Whisper e cortado nos segmentos pelo alinhamento das palavras.
Modo provisório (--provisoria): voz gratuita do Edge TTS, um arquivo por segmento.

Saída: <out>/<id>.wav (mono 48 kHz) e <out>/duracoes.json
Uso: python3 narrar.py <out_dir> [--provisoria]
"""
import difflib, json, os, re, subprocess, sys, wave
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SEGS = json.load(open(os.path.join(AQUI, "narracao.json"), encoding="utf8"))
GRUPOS = [(0, 2), (3, 4), (5, 7), (8, 10)]
VOZ, MODELO = "Gacrux", "gemini-3.1-flash-tts-preview"


def norm(t):
    t = t.lower()
    t = re.sub(r"[^\wà-ú ]", " ", t)
    return t.split()


def ffmpeg_48k(src, dst, start=None, end=None):
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}", "-to", f"{end:.3f}"]
    cmd += ["-i", src, "-ac", "1", "-ar", "48000", dst]
    subprocess.run(cmd, check=True)


def dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def gemini(out):
    sys.path.insert(0, AQUI)
    from tts import tts
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    for gi, (b0, b1) in enumerate(GRUPOS):
        segs = [s for s in SEGS if b0 <= s["bloco"] <= b1]
        bruto = os.path.join(out, f"_grupo{gi}.wav")
        if not os.path.exists(bruto):
            tts(VOZ, "\n\n".join(s["texto"] for s in segs), bruto, MODELO)
        # transcrição com tempo por palavra
        with wave.open(bruto) as w:
            sr = w.getframerate()
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        idx = np.round(np.arange(0, len(a), sr / 16000)).astype(int)
        a16 = a[idx[idx < len(a)]]
        ws = [(x.start, x.end, x.word) for g in model.transcribe(a16, language="pt", word_timestamps=True)[0] for x in g.words]
        heard = [norm(w)[0] if norm(w) else "" for _, _, w in ws]
        # palavras esperadas, com o segmento de cada uma
        exp, owner = [], []
        for k, s in enumerate(segs):
            for w in norm(s["texto"]):
                exp.append(w); owner.append(k)
        sm = difflib.SequenceMatcher(a=exp, b=heard, autojunk=False)
        e2h = {}
        for blk in sm.get_matching_blocks():
            for j in range(blk.size):
                e2h[blk.a + j] = blk.b + j
        total = dur(bruto)
        for k, s in enumerate(segs):
            ids = [i for i, o in enumerate(owner) if o == k]
            hs = [e2h[i] for i in ids if i in e2h]
            if not hs:
                raise RuntimeError(f"sem alinhamento para {s['id']}")
            first, last = min(hs), max(hs)
            prev_end = ws[first - 1][1] if first > 0 else 0.0
            next_start = ws[last + 1][0] if last + 1 < len(ws) else total
            st = max(0.0, (prev_end + ws[first][0]) / 2) if first > 0 else max(0.0, ws[first][0] - 0.15)
            en = min(total, (ws[last][1] + next_start) / 2) if last + 1 < len(ws) else min(total, ws[last][1] + 0.3)
            ffmpeg_48k(bruto, os.path.join(out, f"{s['id']}.wav"), st, en)
            print(f"{s['id']}: {st:7.2f}-{en:7.2f}  casou {len(hs)}/{len(ids)} palavras", flush=True)


def provisoria(out):
    import asyncio, ssl, edge_tts, edge_tts.communicate as etc
    ca = os.environ.get("SSL_CERT_FILE")  # proxy com CA própria: verificação continua ativa
    if ca and os.path.exists(ca):
        etc._SSL_CTX = ssl.create_default_context(cafile=ca)

    async def um(s):
        mp3 = os.path.join(out, f"_{s['id']}.mp3")
        await edge_tts.Communicate(s["texto"], "pt-BR-FranciscaNeural", rate="-6%", pitch="-4Hz").save(mp3)
        ffmpeg_48k(mp3, os.path.join(out, f"{s['id']}.wav"))
        os.remove(mp3)

    async def todos():
        for s in SEGS:
            await um(s)
            print(s["id"], flush=True)
    asyncio.run(todos())


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    (provisoria if "--provisoria" in sys.argv else gemini)(out)
    d = {s["id"]: round(dur(os.path.join(out, f"{s['id']}.wav")), 3) for s in SEGS}
    json.dump(d, open(os.path.join(out, "duracoes.json"), "w"), indent=1)
    print("total narração: %.1f s" % sum(d.values()))
