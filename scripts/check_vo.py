"""Confere a narração: transcreve cada bloco com o Gemini e compara com o roteiro."""
import base64, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemini_tts import BLOCKS, block_text
def transcribe(b):
    mp3 = subprocess.run(["ffmpeg", "-v", "error", "-i", f"assets/vo_gemini/{b}.wav", "-ac", "1", "-b:a", "64k", "-f", "mp3", "-"], capture_output=True).stdout
    body = {"contents": [{"parts": [{"text": "Transcreva exatamente o que é falado neste áudio, palavra por palavra, sem corrigir nada. Escreva palavras estrangeiras como soaram. Responda só com a transcrição."},
                                    {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(mp3).decode()}}]}]}
    import time
    last = ""
    for model in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.7-flash", "gemini-2.5-flash"] * 2:
        r = subprocess.run(["curl", "-sS", "-m", "120", f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", "-H", "x-goog-api-key: " + os.environ["GEMINI_API_KEY"], "-H", "Content-Type: application/json", "-d", "@-"], input=json.dumps(body), capture_output=True, text=True)
        try: return json.loads(r.stdout)["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception: last = (r.stdout or r.stderr)[:160].replace("\n", " "); time.sleep(4)
    return "ERRO " + last
for b in (sys.argv[1:] or BLOCKS):
    print(f"[{b}] roteiro: {block_text(b)}\n     ouvido : {transcribe(b)}\n")
