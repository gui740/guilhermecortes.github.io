"""Cliente mínimo da API Gemini (TTS e música). A chave é lida de GEMINI_KEY_FILE (fora do repositório)."""
import json, os, base64, time, urllib.request, urllib.error
KEY = open(os.environ["GEMINI_KEY_FILE"]).read().strip()
BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
def call(model, body, timeout=180, tries=4):
    req = urllib.request.Request(BASE + model + ":generateContent", data=json.dumps(body).encode(), headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
    for k in range(tries):
        try: return json.load(urllib.request.urlopen(req, timeout=timeout))
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:600]
            if e.code in (429, 500, 503) and k < tries - 1: time.sleep(8 * (k + 1)); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
def tts(text, style, voice="Zubenelgenubi", model="gemini-3.8-flash-tts"):
    body = {"systemInstruction": {"parts": [{"text": style}]}, "contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    r = call(model, body); p = r["candidates"][0]["content"]["parts"][0]["inlineData"]
    return base64.b64decode(p["data"]), p.get("mimeType", "")

def transcribe(wav_bytes, model="gemini-3.5-flash"):
    r = call(model, {"contents": [{"parts": [{"text": "Transcreva exatamente o que é falado neste áudio, em português, sem comentários."},
        {"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(wav_bytes).decode()}}]}]})
    return r["candidates"][0]["content"]["parts"][0]["text"].strip()
