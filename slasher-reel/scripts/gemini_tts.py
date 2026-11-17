"""Gemini TTS (Google AI Studio). Chave lida de GEMINI_KEY_FILE (nunca vai para o repositório).
uso: python3 gemini_tts.py jobs.json   (lista de {text, voice, model, style, out})"""
import base64, json, os, sys, time, wave, subprocess

KEY = open(os.environ["GEMINI_KEY_FILE"]).read().strip()

def tts(text, voice, model, style, out):
    body = {
        "contents": [{"parts": [{"text": style.replace("{TRANSCRIPT}", text)}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}},
    }
    for attempt in range(5):
        r = subprocess.run(["curl", "-s", "-m", "120", "-H", f"x-goog-api-key: {KEY}", "-H", "Content-Type: application/json",
                            "-d", json.dumps(body), f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            data = d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            pcm = base64.b64decode(data)
            with wave.open(out, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
            return True
        except Exception:
            msg = r.stdout[:400].replace(KEY, "***")
            print("retry", attempt, out, msg, file=sys.stderr)
            if '"code": 429' in r.stdout or '"code": 400' in r.stdout:
                return False
            time.sleep(4 * (attempt + 1))
    return False

if __name__ == "__main__":
    jobs = json.load(open(sys.argv[1]))
    for j in jobs:
        if os.path.exists(j["out"]) and os.path.getsize(j["out"]) > 1000:
            continue
        ok = tts(j["text"], j["voice"], j["model"], j["style"], j["out"])
        print("ok" if ok else "FAIL", j["out"], flush=True)
