"""Narração com Gemini TTS (gemini-3.8-flash-tts, voz Zubenelgenubi), frase por frase, com conferência por
transcrição (regera se não bater). Saída: build/g_tts/<id>.wav + frases.json (mesmos ids/textos de tts.py)."""
import sys, json, os, base64, re, unicodedata, difflib
sys.path.insert(0, "scripts/historia"); import gemini
from tts import FRASES
OUT = "build/g_tts"; os.makedirs(OUT, exist_ok=True)
BASE = ("# PERFIL DE ÁUDIO\nNarrador brasileiro jovem, voz masculina, sotaque brasileiro neutro.\n\n### NOTAS DO DIRETOR\n"
        "Estilo: amigo contando história no bar, solto, irônico, ritmo rápido, frases curtas. Não é locutor de propaganda nem professor. {extra}\n\n#### TRANSCRIÇÃO\n")
EXTRA = {"g2": "Palavrão dito com espanto, curto.", "s3c": "Tom de quem acha graça.", "s6c": "Pergunta provocadora, com ironia.", "s6d": "Sério, seco, sem ironia.",
         "s8c": "Incrédulo.", "s8d": "Palavrão de espanto, curto.", "c1": "Pergunta direta pro público.", "c2": "Chamada rápida e amigável."}
SPOKEN = {"s7": "Nos Estados Unidos, Anslinger espalha pânico, Reefer Madness, e em trinta e sete a lei trava tudo.",
          "s8a": "Em sessenta e um, a ONU manda proibir no planeta inteiro.", "s8b": "Em sessenta e quatro, Mechoulam isola o THC.",
          "s6b": "E em mil oitocentos e trinta o Rio proíbe: cadeia pra quem fumasse.",
          "s9": "Aí vira: Uruguai legaliza em dois mil e treze, Canadá em dois mil e dezoito, Alemanha em dois mil e vinte e quatro, e o STF tira o porte do crime.",
          "s10": "Em dois mil e vinte e seis, a Anvisa libera plantio de cânhamo pra remédio."}
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    num = {"100": "cem", "1830": "mil oitocentos e trinta", "37": "trinta e sete", "61": "sessenta e um", "64": "sessenta e quatro", "2013": "dois mil e treze",
           "2018": "dois mil e dezoito", "2024": "dois mil e vinte e quatro", "2026": "dois mil e vinte e seis", "12": "doze"}
    for k, v in num.items(): s = re.sub(rf"\b{k}\b", v, s)
    return re.sub(r"[^a-z ]", " ", s).split()
def body(txt):
    return {"contents": [{"parts": [{"text": txt}]}], "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Zubenelgenubi"}}}}}
if __name__ == "__main__":
    only = set(sys.argv[1:]); res = []
    prev = json.load(open(f"{OUT}/frases.json")) if os.path.exists(f"{OUT}/frases.json") else {"frases": []}
    pmap = {f["id"]: f for f in prev["frases"]}
    for fid, st, text, pausa in FRASES:
        if only and fid not in only and fid in pmap: res.append(pmap[fid]); continue
        spoken = SPOKEN.get(fid, text); best = None
        for k in range(4):
            r = gemini.call("gemini-3.8-flash-tts", body(BASE.format(extra=EXTRA.get(fid, "")) + spoken))
            d = base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            tr = gemini.transcribe(d); score = difflib.SequenceMatcher(None, norm(spoken), norm(tr)).ratio()
            print(fid, k, round(score, 2), "|", tr)
            if best is None or score > best[0]: best = (score, d, tr)
            if score >= 0.93: break
        open(f"{OUT}/{fid}.wav", "wb").write(best[1])
        res.append({"id": fid, "estacao": st, "texto": text, "falado": spoken, "pausa": pausa, "transcricao": best[2], "score": round(best[0], 3)})
    json.dump({"voz": "gemini-3.8-flash-tts / Zubenelgenubi", "frases": res}, open(f"{OUT}/frases.json", "w"), ensure_ascii=False, indent=1)
