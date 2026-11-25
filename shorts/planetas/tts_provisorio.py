"""Narração provisória via Edge TTS (pt-BR). Uso: python tts_provisorio.py out_dir"""
import asyncio, ssl, sys, os, json
import edge_tts, edge_tts.communicate as c
ca = os.environ.get("CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
if os.path.exists(ca):
    c._SSL_CTX = ssl.create_default_context(cafile=ca)
VOICE, RATE = "pt-BR-AntonioNeural", "+12%"
LINES = json.load(open(os.path.join(os.path.dirname(__file__), "narracao.json")))
async def main(out):
    os.makedirs(out, exist_ok=True)
    for i, l in enumerate(LINES):
        await edge_tts.Communicate(l["text"], VOICE, rate=l.get("rate", RATE), pitch="+2Hz").save(f"{out}/n{i:02d}.mp3")
asyncio.run(main(sys.argv[1]))
