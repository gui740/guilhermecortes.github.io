"""Narração PROVISÓRIA via Edge TTS (pt-BR) com tempos de cada palavra.
Uso: python tts_provisorio.py out_dir   -> n00.mp3... + words.json"""
import asyncio, ssl, sys, os, json
import edge_tts, edge_tts.communicate as c
ca = os.environ.get("CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
if os.path.exists(ca):
    c._SSL_CTX = ssl.create_default_context(cafile=ca)
VOICE, RATE = "pt-BR-AntonioNeural", "+8%"
LINES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "narracao.json")))


async def one(i, text, out):
    com = edge_tts.Communicate(text, VOICE, rate=RATE, pitch="+3Hz", boundary="WordBoundary")
    audio, words = bytearray(), []
    async for ch in com.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    open(f"{out}/n{i:02d}.mp3", "wb").write(audio)
    return words


async def main(out):
    os.makedirs(out, exist_ok=True)
    allw = {}
    for i, l in enumerate(LINES):
        allw[f"n{i:02d}"] = await one(i, l["text"], out)
    json.dump(allw, open(f"{out}/words.json", "w"), ensure_ascii=False, indent=0)

asyncio.run(main(sys.argv[1]))
