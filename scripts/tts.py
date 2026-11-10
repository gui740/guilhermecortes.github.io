"""Narração frase a frase (edge-tts, pt-BR neural) com timestamps por palavra.
Uso: python3 scripts/tts.py  -> assets/vo/<id>.mp3 + assets/vo/<id>.json"""
import asyncio, json, os, sys
import certifi
# atrás de proxy corporativo/sandbox: usa o bundle de CA do ambiente, se existir
_CA = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
if _CA and os.path.exists(_CA): certifi.where = lambda: _CA
import edge_tts
PROXY = os.environ.get("HTTPS_PROXY") or None
VOICE = "pt-BR-AntonioNeural"
# id, texto falado, rate, pitch  (ritmo/entonação variam por frase)
LINES = [
 ("h1", "Três found footage que parecem gravação real.", "+12%", "+2Hz"),
 ("h2", "O último, cê não termina sozinho.", "+6%", "-2Hz"),
 ("f3a", "Três:", "+4%", "+0Hz"),
 ("f3b", "A Bruxa de Blair.", "+2%", "-3Hz"),
 ("f3c", "Juraram que era real.", "+12%", "+2Hz"),
 ("f3d", "Tá na Netflix.", "+10%", "+0Hz"),
 ("m1", "O próximo é pior.", "+8%", "-2Hz"),
 ("f2a", "Dois:", "+4%", "+0Hz"),
 ("f2b", "Entrevista com o Demônio.", "+2%", "-3Hz"),
 ("f2c", "Talk show ao vivo que dá errado.", "+12%", "+2Hz"),
 ("f2d", "Na HBO Max.", "+8%", "+0Hz"),
 ("s1", "Manda pra quem não tem medo.", "+12%", "+3Hz"),
 ("f1a", "Um:", "+2%", "-2Hz"),
 ("f1b", "Gonjiam.", "-2%", "-4Hz"),
 ("f1c", "Live num manicômio abandonado de verdade.", "+10%", "+1Hz"),
 ("f1d", "No Prime Video.", "+8%", "+0Hz"),
 ("c1", "Salva pro fim de semana.", "+12%", "+2Hz"),
 ("c2", "Qual dá mais medo? O dois nem devia tá aqui.", "+20%", "+3Hz"),
 ("c3", "Segue a talking horror pra mais", "+12%", "+1Hz"),
 # ganchos alternativos (3s)
 ("gA", "Três found footage que parecem gravação real.", "+12%", "+2Hz"),
 ("gB", "Cê não termina o número um sozinho.", "+8%", "-2Hz"),
 ("gC", "Esse filme, muita gente jura que é real.", "+8%", "+1Hz"),
]
async def one(i, text, rate, pitch):
    c = edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch, boundary="WordBoundary", proxy=PROXY)
    words = []
    with open(f"assets/vo/{i}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    json.dump({"text": text, "words": words}, open(f"assets/vo/{i}.json", "w"), ensure_ascii=False)
    print(i, len(words), [w["w"] for w in words])
async def main():
    only = sys.argv[1:]
    for l in LINES:
        if only and l[0] not in only: continue
        await one(*l)
asyncio.run(main())
