import asyncio, ssl, sys, json
import edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
async def one(text, out, pitch, rate="+0%"):
    com = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate=rate, pitch=pitch)
    await com.save(out)
async def main():
    jobs=[l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip()]
    for k,t in jobs:
        for p in ["-4Hz","-2Hz","+0Hz"]:
            await one(t, f"assets/vo/raw/{k}_{p}.mp3", p)
asyncio.run(main())
