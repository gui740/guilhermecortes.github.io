"""Gera a narração frase a frase com edge-tts (pt-BR neural) + timestamps por palavra."""
import asyncio, json, sys, os, certifi
if os.environ.get("SSL_CERT_FILE"): certifi.where = lambda: os.environ["SSL_CERT_FILE"]  # proxy corporativo/CI
import edge_tts
VOICE = os.environ.get("VOZ", "pt-BR-AntonioNeural")
RATE = os.environ.get("RATE", "+15%")
# (id, cena, texto falado). Grafia fonética só onde a voz precisa (URL).
FRASES = [
 ("c1a", 1, "A eleição acabou."),
 ("c1b", 1, "Mas o assédio eleitoral…"),
 ("c1c", 1, "não."),
 ("c2a", 2, "Foi vítima de ameaças ou represálias no trabalho por causa do seu voto?"),
 ("c2b", 2, "Denuncie."),
 ("c3a", 3, "Demissões, ameaças, retaliações,"),
 ("c3b", 3, "ou qualquer tipo de coação motivada pelo voto dos trabalhadores, configura assédio eleitoral."),
 ("c4a", 4, "O MPT e o TRT em Mato Grosso continuam recebendo denúncias:"),
 ("c4b", 4, "tanto das práticas ilegais durante a campanha, quanto da conduta após o resultado."),
 ("c5a", 5, "Ninguém é obrigado a contar em quem votou."),
 ("c5b", 5, "E ninguém pode perder o emprego, deixar de ser contratado, ou sofrer represália pela escolha que fez."),
 ("c6a", 6, "Sofreu ou presenciou?"),
 ("c6b", 6, "Denuncie."),
 ("c6c", 6, "Guarde provas: prints de tela, áudios, mensagens e nomes de testemunhas."),
 ("c6d", 6, "A denúncia pode ser anônima e sigilosa."),
 ("c7a", 7, "Como denunciar:"),
 ("c7b", 7, "acesse eme pê tê, ponto eme pê, ponto bê érre, barra, assédio eleitoral."),
 ("c7c", 7, "Em Mato Grosso, também dá pra ligar."),
 ("c8a", 8, "O combate ao assédio eleitoral é uma das frentes de atuação do MPT."),
 ("c9a", 9, "Liberdade política no trabalho é direito."),
 ("c9b", 9, "MPT e TRT em Mato Grosso seguem atentos e atuando."),
]
async def one(fid, text, out):
    c = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    words = []
    with open(f"{out}/{fid}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "t": ch["offset"]/1e7, "d": ch["duration"]/1e7})
    return words
async def main(out):
    os.makedirs(out, exist_ok=True)
    res = []
    for fid, cena, text in FRASES:
        for k in range(4):
            try: w = await one(fid, text, out); break
            except Exception as e: print("retry", fid, repr(e)[:300]); await asyncio.sleep(2)
        else: raise SystemExit("TTS falhou: "+fid)
        res.append({"id": fid, "cena": cena, "texto": text, "palavras": w})
    json.dump({"voz": VOICE, "rate": RATE, "frases": res}, open(f"{out}/frases.json", "w"), ensure_ascii=False, indent=1)
asyncio.run(main(sys.argv[1]))
