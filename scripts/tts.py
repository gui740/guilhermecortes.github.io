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
 ("h1", "Três found footage que parecem gravação de verdade.", "+4%", "+2Hz"),
 ("h2", "E o último, cê não termina sozinho.", "+0%", "-2Hz"),
 ("a1", "Número três:", "+0%", "+0Hz"),
 ("a2", "A Bruxa de Blair.", "-2%", "-3Hz"),
 ("a3", "Três estudantes entram numa floresta pra gravar um documentário,", "+4%", "+1Hz"),
 ("a4", "e somem.", "-4%", "-3Hz"),
 ("a5", "Em noventa e nove, o site do filme dizia que eles tinham desaparecido de verdade.", "+4%", "+1Hz"),
 ("a6", "E muita gente acreditou.", "+0%", "-1Hz"),
 ("a7", "Tá na Netflix.", "+2%", "+0Hz"),
 ("m1", "E o próximo é pior.", "+0%", "-2Hz"),
 ("b1", "Número dois:", "+0%", "+0Hz"),
 ("b2", "Entrevista com o Demônio.", "-2%", "-3Hz"),
 ("b3", "É a fita de um talk show de setenta e sete,", "+4%", "+1Hz"),
 ("b4", "ao vivo, na noite de Halloween.", "+2%", "+0Hz"),
 ("b5", "O apresentador leva uma menina possuída pro palco,", "+4%", "+1Hz"),
 ("b6", "e perde o controle.", "-2%", "-3Hz"),
 ("b7", "Tá na HBO Max.", "+2%", "+0Hz"),
 ("s1", "Manda pra quem diz que não tem medo de nada.", "+4%", "+2Hz"),
 ("c1", "E o número um,", "+0%", "-1Hz"),
 ("c2", "que quase ninguém viu:", "+2%", "+0Hz"),
 ("c3", "Gonjiam.", "-4%", "-4Hz"),
 ("c4", "Uma equipe faz uma live dentro de um manicômio abandonado,", "+4%", "+1Hz"),
 ("c5", "que existiu de verdade, na Coreia do Sul.", "+2%", "+0Hz"),
 ("c6", "Cada um com uma câmera no rosto.", "+2%", "-1Hz"),
 ("c7", "Tá no Prime Video.", "+2%", "+0Hz"),
 ("e1", "Salva pra assistir no fim de semana.", "+4%", "+2Hz"),
 ("e2", "Qual dos três te dá mais medo?", "+4%", "+3Hz"),
 ("e3", "Comenta aqui.", "+2%", "+0Hz"),
 ("e4", "E segue a talking horror pra mais", "+4%", "+1Hz"),
 # ganchos alternativos (3s)
 ("gA", "Três found footage que parecem gravação de verdade.", "+8%", "+2Hz"),
 ("gB", "Cê não termina o número um sozinho.", "+4%", "-2Hz"),
 ("gC", "Esse filme, muita gente jura que é real.", "+4%", "+1Hz"),
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
