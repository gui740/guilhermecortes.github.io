"""Generate narration line by line with Gemini TTS, trim, and word-align."""
import json, os, sys, subprocess, difflib, re, unicodedata
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
import timeline as TL
from tts import tts

VOICE = os.environ.get("VOICE", "Enceladus")
SHOUT_VOICE = os.environ.get("SHOUT_VOICE", "Algenib")
BASE = ("Narrador brasileiro do interior de Mato Grosso, sotaque cuiabano leve, voz humana natural, "
        "contando um causo de assombração à noite, perto da fogueira, para quem está ouvindo bem de perto. ")
STYLE = {
    "whisper": BASE + "Aqui ele SUSSURRA, voz baixinha e arrepiada, devagar, com respiração audível.",
    "tell": BASE + "Voz grave e calma, ritmo lento, pausas naturais, como avô contando história.",
    "tense": BASE + "Tom tenso e misterioso, um pouco mais baixo, pausas dramáticas antes das palavras-chave.",
    "fast": BASE + "Tenso e com medo, acelerando aos poucos, respiração curta, as últimas palavras ditas secas e assustadas.",
    "shout": "Homem perdido na mata à noite gritando de muito longe por socorro, chamando o companheiro, voz esticada, rouca e desesperada.",
}
# phonetic spellings to help the TTS
FIX = {"poaieiro": "poaiêro", "esse assobio": "esse assobio"}
OUT = os.path.join(TL.VO, "lines")


def gen(line):
    lid, text, cap, style = line
    for a, b in FIX.items():
        text = text.replace(a, b)
    text = text.replace("<whisper> ", "")
    raw = os.path.join(OUT, lid + "_raw.wav")
    voice = SHOUT_VOICE if style == "shout" else VOICE
    if not os.path.exists(raw):
        import time
        for attempt in range(8):
            try:
                tts(text, voice, STYLE[style], raw, model=os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts"))
                break
            except Exception as e:
                print(lid, "retry", e, flush=True)
                time.sleep(15 * (attempt + 1))
    # trim leading/trailing silence, keep 24k mono
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
                    "silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-42dB:stop_silence=0.28,"
                    "atempo=" + os.environ.get("TEMPO", "1.08") + ","
                    "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse",
                    "-ar", "24000", "-ac", "1", os.path.join(OUT, lid + ".wav")], check=True)
    return lid


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def align_line(lid, cap, ww):
    cw = cap.split()
    a, b = [norm(x) for x in cw], [norm(x["w"]) for x in ww]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = [None] * len(cw)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out[i1 + k] = (ww[j1 + k]["s"], ww[j1 + k]["e"])
        elif tag == "replace" and j2 > j1:
            s0, e0 = ww[j1]["s"], ww[j2 - 1]["e"]
            n = i2 - i1
            for k in range(n):
                out[i1 + k] = (s0 + (e0 - s0) * k / n, s0 + (e0 - s0) * (k + 1) / n)
    # fill gaps by interpolation
    dur = TL.wav_duration(os.path.join(OUT, lid + ".wav"))
    for i in range(len(out)):
        if out[i] is None:
            prev = out[i - 1][1] if i and out[i - 1] else 0.0
            nxt = next((o[0] for o in out[i + 1:] if o), dur)
            out[i] = (prev, prev + max(0.12, (nxt - prev) * 0.8))
    return [{"w": w, "s": round(s, 3), "e": round(e, 3)} for w, (s, e) in zip(cw, out)]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    lines = [l for l in TL.LINES if not only or l[0] in only]
    with ThreadPoolExecutor(1) as ex:
        list(ex.map(gen, lines))
    import align
    wpath = os.path.join(OUT, "words.json")
    words = json.load(open(wpath)) if os.path.exists(wpath) else {}
    report = []
    for lid, text, cap, style in lines:
        ww = align.words(os.path.join(OUT, lid + ".wav"), prompt=None)
        nc = len(cap.split())
        al = align_line(lid, cap, ww)
        full_n = len(re.sub(r"<[^>]+>", "", text).split())
        if nc < full_n:  # caption shorter than take: cut audio after last kept word
            # find heard word matching last caption word
            last = norm(cap.split()[-1])
            cands = [w for w in ww if norm(w["w"]) == last or (len(norm(w["w"])) >= 3 and last.endswith(norm(w["w"])))]
            cut = (cands[0]["e"] if cands else al[-1]["e"]) + 0.15
            p = os.path.join(OUT, lid + ".wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-t", str(cut), "-af", "afade=t=out:st=%f:d=0.12" % (cut - 0.12), p + ".tmp.wav"], check=True)
            os.replace(p + ".tmp.wav", p)
            al = [w for w in al if w["s"] < cut]
        words[lid] = al
        heard = " ".join(x["w"] for x in ww)
        report.append((lid, round(TL.wav_duration(os.path.join(OUT, lid + ".wav")), 2), heard))
        print(lid, report[-1][1], "|", heard, flush=True)
    json.dump(words, open(wpath, "w"), ensure_ascii=False, indent=1)
