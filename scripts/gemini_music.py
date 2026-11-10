"""Trilha de rock instrumental gerada com o Lyria (Google AI Studio).
A chave vem só de GEMINI_API_KEY. uso: python3 scripts/gemini_music.py [modelo] -> assets/music/rock_<n>.wav"""
import base64, json, os, subprocess, sys
PROMPT = ("Instrumental dark garage rock / horror punk backing track, 120 BPM, E minor. Gritty distorted electric guitar riff with palm-muted power chords, "
          "driving bass guitar and tight live drums. Tense, menacing, cool, like the soundtrack of a horror movie trailer. "
          "Steady groove from the first second, no intro, no vocals, no singing, no spoken words, no fade out.")
def gen(model, out):
    body = {"contents": [{"parts": [{"text": PROMPT}]}], "generationConfig": {"responseModalities": ["AUDIO"]}}
    r = subprocess.run(["curl", "-sS", "-m", "300", f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                        "-H", "x-goog-api-key: " + os.environ["GEMINI_API_KEY"], "-H", "Content-Type: application/json", "-d", "@-"],
                       input=json.dumps(body), capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        parts = d["candidates"][0]["content"]["parts"]
    except Exception:
        print(model, "falhou:", r.stdout[:400].replace("\n", " "), r.stderr[:200]); return False
    for p in parts:
        if "inlineData" in p:
            raw = base64.b64decode(p["inlineData"]["data"]); mime = p["inlineData"].get("mimeType", "")
            args = ["-i", "-"] if ("wav" in mime or "mp" in mime or "ogg" in mime) else ["-f", "s16le", "-ar", "48000", "-ac", "2", "-i", "-"]
            subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-ar", "48000", "-ac", "2", out], input=raw, check=True)
            print(model, mime, "->", out); return True
        elif "text" in p: print(model, "texto:", p["text"][:200])
    return False
if __name__ == "__main__":
    models = sys.argv[1:] or ["lyria-3.5", "lyria-3-pro-preview", "lyria-3-clip-preview"]
    for i, m in enumerate(models):
        if gen(m, f"assets/music/rock_{m}.wav"): break
