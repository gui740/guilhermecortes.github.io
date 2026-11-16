"""Narração inteira num único pedido ao Gemini TTS (limite de cota gratuita) + ganchos B e C no mesmo áudio.
Saída: build/g_full.wav. Conferência por transcrição."""
import sys, json, base64, os
sys.path.insert(0, "scripts/historia"); import gemini
from tts_gemini import SPOKEN, norm
from tts import FRASES
MODEL = sys.argv[1] if len(sys.argv) > 1 else "gemini-3.1-flash-tts-preview"
VOICE = "Zubenelgenubi"
lines = [SPOKEN.get(fid, text) for fid, _, text, _ in FRASES]
lines += ["[pausa longa]", "Proibiram antes de saber o que era, puta merda.", "[pausa longa]", "Doze mil anos de maconha em sessenta segundos."]
prompt = ("# PERFIL DE ÁUDIO\nNarrador brasileiro jovem, voz masculina, sotaque brasileiro neutro (nada de sotaque de Portugal ou gringo).\n\n"
          "### NOTAS DO DIRETOR\nEstilo: amigo contando uma história no bar — solto, irônico, divertido, ritmo rápido, frases curtas e pausas curtas entre elas. "
          "Não é locutor de propaganda nem professor. Pausinha antes de palavrão e de piada. 'Os escravizados' é dito sério, seco. "
          "Onde estiver [pausa longa], faça silêncio de dois segundos e não leia a marcação.\n\n#### TRANSCRIÇÃO\n" + "\n".join(lines))
body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
r = gemini.call(MODEL, body, timeout=600)
if "content" not in r["candidates"][0]: print(json.dumps(r)[:800]); sys.exit(1)
p = r["candidates"][0]["content"]["parts"][0]["inlineData"]; d = base64.b64decode(p["data"])
open("build/g_full.wav", "wb").write(d); print(MODEL, p.get("mimeType"), len(d))
tr = gemini.transcribe(d, model="gemini-flash-lite-latest"); open("build/g_full_transcricao.txt", "w").write(tr); print(tr)
import difflib; print("score", round(difflib.SequenceMatcher(None, norm(" ".join(l for l in lines if "[" not in l)), norm(tr)).ratio(), 3))
