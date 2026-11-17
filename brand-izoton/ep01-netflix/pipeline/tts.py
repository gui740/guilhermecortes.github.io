"""Narração via Gemini TTS. A chave vem SEMPRE da variável de ambiente GEMINI_API_KEY (nunca do repo).
Uso: python3 tts.py <voz> <arquivo_texto> <saida.wav> [modelo]
"""
import base64, json, os, sys, time, urllib.error, urllib.request, wave

STYLES = {
    "radio": ("Narre em português do Brasil como um locutor de rádio de uma cidade retrofuturista: "
              "voz masculina grave, dicção nítida, ritmo firme e enfático, com uma ironia leve e inteligente. "
              "Tom de documentário curioso, sem gritar e sem exagero. Pausas curtas entre as frases."),
    "serena": ("Narre em português do Brasil com voz feminina de registro médio-grave, nunca aguda nem fina. "
               "Calma, serena e segura, como a locutora de um abrigo que mantém a paz num futuro apocalíptico: "
               "autoridade tranquila, calor humano, nenhuma pressa. Dicção nítida, frases bem assentadas, "
               "pausas respiradas entre as ideias. Curiosa e inteligente, levemente irônica, sem dramatizar e sem sussurrar."),
}
STYLE = STYLES[os.environ.get("TTS_STYLE", "serena")]

PROMPT = ("# AUDIO PROFILE\nNarrador de documentário de um canal de design e marcas.\n\n"
          "## DIRECTOR'S NOTES\n{style}\nLeia SOMENTE o texto da seção TRANSCRIPT.\n\n"
          "## TRANSCRIPT\n{text}")

def tts(voice, text, out, model="gemini-3.8-flash-tts"):
    key = os.environ["GEMINI_API_KEY"]
    body = {
        "contents": [{"parts": [{"text": PROMPT.format(style=STYLE, text=text)}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    for attempt in range(6):  # limite por minuto da API: espera e tenta de novo
        try:
            d = json.load(urllib.request.urlopen(req, timeout=300)); break
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 503) or attempt == 5: raise
            time.sleep(20 * (attempt + 1))
    for retry in range(3):
        c = d.get("candidates", [{}])[0]
        if "content" in c:
            break
        print("TTS sem áudio:", c.get("finishReason"), d.get("promptFeedback"), file=sys.stderr)
        if c.get("finishReason") in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "OTHER"):
            raise RuntimeError(f"bloqueado pelo filtro: {c.get('finishReason')}")
        time.sleep(5)
        d = json.load(urllib.request.urlopen(req, timeout=300))
    pcm = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    with wave.open(out, "wb") as w:  # PCM 16-bit mono 24 kHz
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)

if __name__ == "__main__":
    tts(sys.argv[1], open(sys.argv[2], encoding="utf8").read(), sys.argv[3], *(sys.argv[4:5]))
