"""Gemini TTS helper. Reads the key from the GEMINI_API_KEY env var only."""
import base64, json, os, sys, urllib.request

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

def tts(text, voice, style, out_path, model="gemini-3.8-flash-tts"):
    key = os.environ["GEMINI_API_KEY"]
    body = {
        "model": model,
        "input": [{"type": "user_input", "content": [{
            "type": "text", "text": text,
            "annotations": [{"type": "speech_metadata", "style": style}]}]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    for step in d.get("steps", []):
        for c in step.get("content", []) or []:
            if c.get("data"):
                audio = base64.b64decode(c["data"])
                with open(out_path, "wb") as f:
                    f.write(audio)
                return out_path
    raise RuntimeError("no audio in response: " + json.dumps(d)[:800])

if __name__ == "__main__":
    tts(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
