"""Narração Gemini TTS em blocos (cota gratuita pequena + filtro de segurança). Um bloco barrado é dividido em dois.
Saída: build/g_chunks/<bloco>.wav e manifest.json (ids das frases de cada bloco)."""
import sys, json, base64, os, difflib
sys.path.insert(0, "scripts/historia"); import gemini
from tts_gemini import SPOKEN, norm
from tts import FRASES
MODELS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["gemini-3.1-flash-tts-preview"]
OUT = "build/g_chunks"; os.makedirs(OUT, exist_ok=True)
TXT = {fid: SPOKEN.get(fid, text) for fid, _, text, _ in FRASES}
TXT["hB"] = "Proibiram antes de saber o que era, puta merda."; TXT["hC"] = "Doze mil anos de maconha em sessenta segundos."
GROUPS = [["g1", "g2"], ["s1", "s2"], ["s3a", "s3b", "s3c"], ["s4", "s5"], ["s6a", "s6b"], ["s6c", "s6d"], ["s7"], ["s8a", "s8b", "s8c", "s8d"], ["s9"], ["s10", "c1", "c2"], ["hB"], ["hC"]]
HEAD = ("# PERFIL DE ÁUDIO\nNarrador brasileiro jovem, voz masculina, sotaque brasileiro neutro.\n\n### NOTAS DO DIRETOR\n"
        "Vídeo educativo de história contado como conversa de bar: solto, irônico, divertido, ritmo rápido, pausas curtas entre as frases. "
        "Não é locutor de propaganda nem professor. Pausinha antes de palavrão e de piada.{extra}\n\n#### TRANSCRIÇÃO\n")
EXTRA = {"s6c": " A última frase é dita séria e seca."}
man = json.load(open(f"{OUT}/manifest.json")) if os.path.exists(f"{OUT}/manifest.json") else {}
def req(ids, model):
    extra = " A última frase é dita séria e seca." if "s6d" in ids else ""
    if "s10" in ids: extra += " Leia exatamente as palavras escritas, sem trocar nenhuma: 'cânhamo' (não 'cannabis'), 'pra' (não 'para'), 'Cê' (não 'você')."
    body = {"contents": [{"parts": [{"text": HEAD.format(extra=extra) + "\n".join(TXT[i] for i in ids)}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Zubenelgenubi"}}}}}
    r = gemini.call(model, body, timeout=300); c = r["candidates"][0]
    if "content" not in c: return None, c.get("finishReason")
    part = c["content"]["parts"][0]["inlineData"]; raw = base64.b64decode(part["data"]); mime = part.get("mimeType", "")
    if raw[:4] != b"RIFF":   # PCM cru (audio/L16;rate=24000) -> WAV
        import re, io, wave
        rate = int((re.search(r"rate=(\d+)", mime) or [0, 24000])[1]); b = io.BytesIO()
        with wave.open(b, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(raw)
        raw = b.getvalue()
    return raw, "OK"
queue = [g for g in GROUPS if "+".join(g) not in man]
mi = 0
while queue:
    g = queue.pop(0); name = "+".join(g)
    try: d, why = req(g, MODELS[mi])
    except RuntimeError as e:
        if "429" in str(e) and mi < len(MODELS) - 1: mi += 1; queue.insert(0, g); print("cota esgotada -> ", MODELS[mi]); continue
        print("ERRO", name, str(e)[:300]); break
    if d is None:
        print("barrado", name, why)
        if len(g) > 1: queue[:0] = [g[:len(g) // 2], g[len(g) // 2:]]
        else: print("frase única barrada:", name)
        continue
    open(f"{OUT}/{name}.wav", "wb").write(d)
    try: tr = gemini.transcribe(d, model="gemini-flash-lite-latest")
    except Exception as e: tr = "(sem transcrição: " + str(e)[:80] + ")"
    sc = difflib.SequenceMatcher(None, norm(" ".join(TXT[i] for i in g)), norm(tr)).ratio()
    man[name] = {"ids": g, "model": MODELS[mi], "transcricao": tr, "score": round(sc, 3)}
    print("ok", name, MODELS[mi], round(sc, 2), "|", tr); json.dump(man, open(f"{OUT}/manifest.json", "w"), ensure_ascii=False, indent=1)
print("faltam", [("+".join(g)) for g in queue])
