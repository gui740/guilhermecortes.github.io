"""Narração frase a frase (edge-tts pt-BR-AntonioNeural) com timestamps por palavra.
Sem chave Gemini/ElevenLabs no ambiente e sem acesso aos modelos Whisper (HF/openaipublic bloqueados),
os timestamps vêm dos WordBoundary do próprio TTS (alinhamento exato do sintetizador)."""
import asyncio, json, sys, os, certifi
if os.environ.get("SSL_CERT_FILE"): certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts
VOICE, RATE, PITCH = "pt-BR-AntonioNeural", "+8%", "+4Hz"
# (id, estação, texto). "pausa" = silêncio antes da frase (timing de piada).
FRASES = [
 ("g1", 0, "O Rio proibiu maconha cem anos antes dos Estados Unidos.", 0),
 ("g2", 0, "Porra.", .30),
 ("s1", 1, "Volta doze mil anos: a planta é domesticada na Ásia.", .12),
 ("s2", 2, "Na Índia, vira bhang, bebida sagrada.", .1),
 ("s3a", 3, "No Pamir, queimavam erva com THC em funeral.", .1),
 ("s3b", 3, "Os citas? Sauna de fumaça.", .1),
 ("s3c", 3, "Heródoto jura que uivavam de prazer.", .1),
 ("s4", 4, "No Cairo medieval, o haxixe bomba.", .12),
 ("s5", 5, "Nas navegações, corda de cânhamo segura os navios.", .1),
 ("s6a", 6, "No Brasil, vira fumo de Angola, pito do pango.", .12),
 ("s6b", 6, "E em 1830 o Rio proíbe: cadeia pra quem fumasse.", .1),
 ("s6c", 6, "Adivinha quem era o alvo?", .1),
 ("s6d", 6, "Os escravizados.", .30),
 ("s7", 7, "Nos Estados Unidos, Anslinger espalha pânico, Reefer Madness, e em 37 a lei trava tudo.", .14),
 ("s8a", 8, "Em 61, a ONU manda proibir no planeta inteiro.", .1),
 ("s8b", 8, "Em 64, Mechoulam isola o THC.", .1),
 ("s8c", 8, "Proibiram antes de saber o que era.", .1),
 ("s8d", 8, "Puta merda.", .28),
 ("s9", 9, "Aí vira: Uruguai legaliza em 2013, Canadá em 2018, Alemanha em 2024, e o STF tira o porte do crime.", .14),
 ("s10", 10, "Em 2026, a Anvisa libera plantio de cânhamo pra remédio.", .1),
 ("c1", 10, "Cê sabia que o Rio proibiu antes dos gringos?", .14),
 ("c2", 10, "Comenta e segue aí.", .06),
]
async def one(fid, text, out):
    c = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary"); words = []
    with open(f"{out}/{fid}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    return words
async def main(out):
    os.makedirs(out, exist_ok=True); res = []
    for fid, st, text, pausa in FRASES:
        for k in range(4):
            try: w = await one(fid, text, out); break
            except Exception as e: print("retry", fid, repr(e)[:200]); await asyncio.sleep(2)
        else: raise SystemExit("TTS falhou: " + fid)
        res.append({"id": fid, "estacao": st, "texto": text, "pausa": pausa, "palavras": w})
    json.dump({"voz": VOICE, "rate": RATE, "pitch": PITCH, "frases": res}, open(f"{out}/frases.json", "w"), ensure_ascii=False, indent=1)
if __name__ == "__main__": asyncio.run(main(sys.argv[1]))
