#!/usr/bin/env python3
"""
Gera a narração (public/<voice.file>) e o timing palavra-por-palavra a partir
do JSON do episódio, gravando o resultado em data["timing"].

Uso:  python3 scripts/gerar-voz.py src/data/ep01.json

Ordem de preferência do motor de voz:
- GEMINI_API_KEY  -> Gemini TTS (Google AI Studio, voice.geminiModel / geminiVoice / geminiStyle)
                     + alinhamento palavra a palavra com faster-whisper.
- ELEVENLABS_API_KEY -> ElevenLabs (/with-timestamps).
- nenhum         -> Microsoft Edge TTS (edge-tts, grátis) com WordBoundary.
Cada cena é sintetizada separadamente e concatenada com pequenas pausas,
assim os limites de cena saem exatos no timing.
"""
import asyncio, base64, json, os, re, ssl, subprocess, sys, tempfile, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CA = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if Path("/root/.ccr/ca-bundle.crt").exists() else None)


def sh(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


async def edge_scene(text, voice, rate, pitch, out_mp3):
    import edge_tts.communicate as c
    if CA:
        c._SSL_CTX = ssl.create_default_context(cafile=CA)
    comm = c.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append({"text": chunk["text"], "start": s, "end": s + chunk["duration"] / 1e7})
    return words


def eleven_scene(text, voice_id, out_mp3):
    key = os.environ["ELEVENLABS_API_KEY"]
    voice_id = voice_id or "pNInz6obpgDQGcFmaJgB"  # Adam (masculina); troque no JSON
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": "eleven_multilingual_v2",
                         "voice_settings": {"stability": 0.35, "similarity_boost": 0.8, "style": 0.6}}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    ctx = ssl.create_default_context(cafile=CA) if CA else None
    res = json.load(urllib.request.urlopen(req, context=ctx))
    Path(out_mp3).write_bytes(base64.b64decode(res["audio_base64"]))
    al = res["alignment"]
    words, cur, start, end = [], "", None, 0
    for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                words.append({"text": cur, "start": start, "end": end})
            cur, start = "", None
        else:
            if start is None:
                start = s
            cur += ch
            end = e
    if cur:
        words.append({"text": cur, "start": start, "end": end})
    return words


def gemini_scene(text, v, out_wav):
    key = os.environ["GEMINI_API_KEY"]
    model = v.get("geminiModel", "gemini-3.1-flash-tts-preview")
    body = {"contents": [{"role": "user", "parts": [{"text": v.get("geminiStyle", "") + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v.get("geminiVoice", "Puck")}}}}}
    import hashlib
    cache = ROOT / ".cache" / "tts"
    cache.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha1(json.dumps([model, v.get("geminiVoice", "Puck"), v.get("geminiStyle", ""), text]).encode()).hexdigest()[:16]
    cached = cache / f"{h}.json"
    if cached.exists():
        part = json.loads(cached.read_text())
        return _gemini_finish(part, v, out_wav, text)
    ctx = ssl.create_default_context(cafile=CA) if CA else None
    for attempt in range(6):
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                     data=json.dumps(body).encode(), headers={"X-goog-api-key": key, "Content-Type": "application/json"})
        try:
            res = json.load(urllib.request.urlopen(req, context=ctx))
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 5:
                import time; time.sleep(20 * (attempt + 1)); continue
            raise SystemExit(f"Gemini TTS falhou: {e.code} {e.read()[:300]}")
    part = res["candidates"][0]["content"]["parts"][0]["inlineData"]
    cached.write_text(json.dumps(part))
    return _gemini_finish(part, v, out_wav, text)


def _gemini_finish(part, v, out_wav, text):
    raw = base64.b64decode(part["data"])
    tmp = Path(str(out_wav) + ".raw")
    tmp.write_bytes(raw)
    if raw[:4] == b"RIFF":
        sh("ffmpeg", "-y", "-i", tmp, "-ar", "44100", "-ac", "1", out_wav)
    else:  # PCM 16-bit 24 kHz (audio/L16)
        rate = re.search(r"rate=(\d+)", part.get("mimeType", "")) if part.get("mimeType") else None
        sh("ffmpeg", "-y", "-f", "s16le", "-ar", rate.group(1) if rate else "24000", "-ac", "1", "-i", tmp, "-ar", "44100", "-ac", "1", out_wav)
    # corta silêncio no começo/fim e aplica tempo (voice.tempo)
    trimmed = Path(str(out_wav) + ".t.wav")
    tempo = float(v.get("tempo", 1.0))
    sh("ffmpeg", "-y", "-i", out_wav, "-af",
       f"silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tempo}",
       trimmed)
    trimmed.replace(out_wav)
    return align_words(text, out_wav)


_WHISPER = None


def align_words(text, wav):
    """Timing de cada palavra do roteiro: transcreve com faster-whisper e alinha ao texto."""
    global _WHISPER
    import difflib
    import numpy as np
    from faster_whisper import WhisperModel
    if _WHISPER is None:
        _WHISPER = WhisperModel(os.environ.get("WHISPER_MODEL", "small"), device="cpu", compute_type="int8")
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.float32)
    segs, _ = _WHISPER.transcribe(audio, language="pt", word_timestamps=True, initial_prompt=text)
    heard = [w for s in segs for w in s.words]
    total = len(audio) / 16000
    script = text.split()
    n = lambda w: re.sub(r"[^0-9a-z]", "", w.lower().translate(str.maketrans("áàâãéêíóôõúüç", "aaaaeeiooouuc")))
    a, b = [n(w) for w in script], [n(w.word) for w in heard]
    times = [None] * len(script)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            hw = heard[blk.b + k]
            times[blk.a + k] = (hw.start, hw.end)
    # interpola palavras não reconhecidas
    known = [i for i, t in enumerate(times) if t]
    print(f"    alinhamento: {len(known)}/{len(script)} palavras reconhecidas", flush=True)
    for i, t in enumerate(times):
        if t:
            continue
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        s0 = times[prev][1] if prev is not None else 0.0
        s1 = times[nxt][0] if nxt is not None else total
        gap_words = (nxt if nxt is not None else len(script)) - (prev if prev is not None else -1) - 1
        pos = i - (prev if prev is not None else -1) - 1
        step = (s1 - s0) / max(1, gap_words)
        times[i] = (s0 + step * pos, s0 + step * (pos + 1))
    return [{"text": w, "start": t[0], "end": t[1]} for w, t in zip(script, times)]


def clean(w):
    return w.strip(".,:;!?…\"'()")


def main():
    json_path = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "src/data/ep01.json")
    data = json.loads(json_path.read_text())
    v = data["voice"]
    use_gemini = bool(os.environ.get("GEMINI_API_KEY"))
    use_eleven = not use_gemini and bool(os.environ.get("ELEVENLABS_API_KEY"))
    tmp = Path(tempfile.mkdtemp())
    sr = 44100
    sh("ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", str(v["leadInSeconds"]), tmp / "lead.wav")
    sh("ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", str(v["gapSeconds"]), tmp / "gap.wav")
    sh("ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", str(v["tailSeconds"]), tmp / "tail.wav")

    parts, words, scenes = [tmp / "lead.wav"], [], []
    t = v["leadInSeconds"]
    for i, sc in enumerate(data["scenes"]):
        mp3 = tmp / f"s{i}.mp3"
        if use_gemini:
            mp3 = tmp / f"s{i}.gem.wav"
            ws = gemini_scene(sc["narration"], v, mp3)
            print(f"  cena {sc['id']}: ok", flush=True)
        elif use_eleven:
            ws = eleven_scene(sc["narration"], v.get("elevenVoiceId"), mp3)
        else:
            ws = asyncio.run(edge_scene(sc["narration"], v["edgeVoice"], v["edgeRate"], v.get("edgePitch", "+0Hz"), mp3))
        wav = tmp / f"s{i}.wav"
        sh("ffmpeg", "-y", "-i", mp3, "-ar", str(sr), "-ac", "1", wav)
        d = duration(wav)
        voice_start = t
        for w in ws:
            words.append({"text": w["text"], "key": clean(w["text"]).lower(),
                          "start": round(t + w["start"], 3), "end": round(t + w["end"], 3), "scene": sc["id"]})
        t += d
        scenes.append({"id": sc["id"], "voiceStart": round(voice_start, 3), "voiceEnd": round(t, 3)})
        parts.append(wav)
        if i < len(data["scenes"]) - 1:
            parts.append(tmp / "gap.wav")
            t += v["gapSeconds"]
    parts.append(tmp / "tail.wav")
    t += v["tailSeconds"]

    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    out = ROOT / "public" / v["file"]
    sh("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
       "-ar", str(sr), "-ac", "1", "-b:a", "160k", out)

    # limites de cena: cada cena começa no meio da pausa anterior
    for i, s in enumerate(scenes):
        s["start"] = 0.0 if i == 0 else round((scenes[i - 1]["voiceEnd"] + s["voiceStart"]) / 2, 3)
    for i, s in enumerate(scenes):
        s["end"] = round(t, 3) if i == len(scenes) - 1 else scenes[i + 1]["start"]

    engine = (f"gemini:{v.get('geminiModel')}:{v.get('geminiVoice')}" if use_gemini
              else "elevenlabs" if use_eleven else "edge-tts:" + v["edgeVoice"])
    data["timing"] = {"engine": engine,
                      "totalSeconds": round(t, 3), "scenes": scenes, "words": words}
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"OK {out} {t:.2f}s, {len(words)} palavras")


if __name__ == "__main__":
    main()
