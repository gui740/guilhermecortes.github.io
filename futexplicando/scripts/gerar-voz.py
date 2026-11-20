#!/usr/bin/env python3
"""
Gera a narração (public/<voice.file>) e o timing palavra-por-palavra a partir
do JSON do episódio, gravando o resultado em data["timing"].

Uso:  python3 scripts/gerar-voz.py src/data/ep01.json

- Se ELEVENLABS_API_KEY existir, usa ElevenLabs (/with-timestamps) por cena.
- Senão, usa Microsoft Edge TTS (edge-tts, grátis) com WordBoundary.
Cada cena é sintetizada separadamente e concatenada com pequenas pausas,
assim os limites de cena saem exatos no timing.
"""
import asyncio, base64, json, os, ssl, subprocess, sys, tempfile, urllib.request
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


def clean(w):
    return w.strip(".,:;!?…\"'()")


def main():
    json_path = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "src/data/ep01.json")
    data = json.loads(json_path.read_text())
    v = data["voice"]
    use_eleven = bool(os.environ.get("ELEVENLABS_API_KEY"))
    tmp = Path(tempfile.mkdtemp())
    sr = 44100
    sh("ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", str(v["leadInSeconds"]), tmp / "lead.wav")
    sh("ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", str(v["gapSeconds"]), tmp / "gap.wav")
    sh("ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", str(v["tailSeconds"]), tmp / "tail.wav")

    parts, words, scenes = [tmp / "lead.wav"], [], []
    t = v["leadInSeconds"]
    for i, sc in enumerate(data["scenes"]):
        mp3 = tmp / f"s{i}.mp3"
        if use_eleven:
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

    data["timing"] = {"engine": "elevenlabs" if use_eleven else "edge-tts:" + v["edgeVoice"],
                      "totalSeconds": round(t, 3), "scenes": scenes, "words": words}
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"OK {out} {t:.2f}s, {len(words)} palavras")


if __name__ == "__main__":
    main()
