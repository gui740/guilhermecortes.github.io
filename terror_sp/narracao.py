"""Gera a narração com Gemini TTS (Google AI Studio).
Uso: GEMINI_API_KEY=... python3 narracao.py
Salva narr/linha_N.wav (PCM 24 kHz mono)."""
import base64, json, os, sys, time, urllib.request, wave

KEY = os.environ["GEMINI_API_KEY"]
MODELS = os.environ.get("MODELS", "gemini-3.8-flash-tts,gemini-2.5-pro-preview-tts,gemini-2.5-flash-preview-tts").split(",")
VOICE = os.environ.get("VOICE", "Algenib")
STYLE = os.environ.get("STYLE", "")
LINES = [
    "E se um assassino de filme de terror... atacasse São Paulo?",
    "Ele surge do lago do Ibirapuera... e leva uma multa.",
    "Na Paulista? Ninguém tem tempo pra ser assustado.",
    "Estação Sé, horário de pico. Agora, a vítima é ele.",
    "Perseguição na Marginal... a três por hora.",
    "Pastel a dezoito reais. Isso sim é terror.",
    "Ele desistiu. São Paulo um, terror zero. Segue pra mais!",
]

def tts(text):
    body = {"contents": [{"parts": [{"text": STYLE + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    last = None
    for m in MODELS:
        for attempt in range(3):
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                data=json.dumps(body).encode(), method="POST",
                headers={"Content-Type": "application/json", "X-goog-api-key": KEY})
            try:
                d = json.load(urllib.request.urlopen(req, timeout=120))
                for p in d["candidates"][0]["content"]["parts"]:
                    if "inlineData" in p:
                        return m, base64.b64decode(p["inlineData"]["data"])
                last = f"{m}: sem áudio"
            except Exception as e:
                last = f"{m}: {e} {getattr(e, 'read', lambda: b'')()[:300]}"
                time.sleep(2 * (attempt + 1))
        print("falhou", last, file=sys.stderr)
    raise RuntimeError(last)

os.makedirs("narr", exist_ok=True)
only = [int(a) for a in sys.argv[1:]] or range(len(LINES))
for i in only:
    m, pcm = tts(LINES[i])
    with wave.open(f"narr/linha_{i}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    print(i, m, f"{len(pcm)/48000:.2f}s", LINES[i])
