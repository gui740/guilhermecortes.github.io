import json, sys, glob, os, soundfile as sf
from faster_whisper import WhisperModel
nome = sys.argv[1]
m = WhisperModel(nome, compute_type="int8", cpu_threads=4)
prompt = "Netflix, Reed Hastings, HBO, House of Cards, Round 6, La Casa de Papel, Wednesday, Stranger Things, Brand by Izoton, keeper test, Fortnite, Frank Underwood, Meio e Mensagem."
for w in sorted(glob.glob("wav16/*.wav")):
    out = "trans/" + os.path.basename(w).replace(".wav", f".{nome}.json")
    if os.path.exists(out): continue
    x, sr = sf.read(w, dtype="float32")
    segs, _ = m.transcribe(x, language="pt", word_timestamps=True, initial_prompt=prompt, vad_filter=False, condition_on_previous_text=False)
    pal = [[round(p.start, 2), round(p.end, 2), p.word.strip()] for s in segs for p in s.words]
    json.dump(pal, open(out, "w"), ensure_ascii=False)
    print(out, len(pal), flush=True)
