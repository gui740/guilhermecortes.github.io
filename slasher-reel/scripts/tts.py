# edge-tts com o CA do proxy do ambiente
import ssl,sys,asyncio,json
import edge_tts, edge_tts.communicate as C
C._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
async def one(text,voice,rate,pitch,out):
    await edge_tts.Communicate(text,voice,rate=rate,pitch=pitch).save(out)
if __name__=="__main__":
    jobs=json.load(open(sys.argv[1]))
    async def main():
        for j in jobs: await one(j["text"],j["voice"],j.get("rate","+0%"),j.get("pitch","+0Hz"),j["out"])
    asyncio.run(main())
