"""Narração com a voz do Gemini (Google AI Studio), gerada por BLOCOS para a entonação fluir.
A chave vem só da variável de ambiente GEMINI_API_KEY (nunca fica em arquivo).
uso: GEMINI_API_KEY=... python3 scripts/gemini_tts.py [bloco ...]  -> assets/vo_gemini/<bloco>.wav"""
import base64, json, os, subprocess, sys, time
MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
VOICE = os.environ.get("GEMINI_VOICE", "Charon")
STYLE = """# AUDIO PROFILE: Rafa, criador de conteúdo de terror
Brasileiro, 25 anos, grava Reels sobre filmes de terror para o Instagram.

## THE SCENE
Sozinho no quarto, à noite, falando perto do microfone, como quem indica um filme para um amigo.

### DIRECTOR'S NOTES
Style: conversa natural, com suspense na medida e um leve sorriso de quem sabe que o filme assusta. Nada de voz de locutor ou de comercial.
Pacing: calmo, sem pressa, com uma pausa curta antes do nome de cada filme.
Accent: português do Brasil, sotaque neutro de São Paulo. Palavras em inglês (found footage, talk show, live, Netflix, HBO Max, Prime Video, Halloween, talking horror) com a pronúncia que um brasileiro jovem usa.

Fidelidade: leia o TRANSCRIPT palavra por palavra, sem acrescentar, trocar ou pular nenhuma palavra, e sem improvisar gírias.

#### TRANSCRIPT
"""
# blocos = grupos de falas (ids de scripts/tts.py)
BLOCKS = {
 "B0": ["h1", "h2"],
 "B1": ["a1", "a2", "a3", "a4", "a5", "a6", "a7"],
 "B2": ["m1"],
 "B3": ["b1", "b2", "b3", "b4", "b5", "b6", "b7"],
 "B4": ["s1"],
 "B5": ["c1", "c2", "c3", "c4", "c5", "c6", "c7"],
 "B6": ["e1", "e2", "e3", "e4"],
 "gA": ["gA"], "gB": ["gB"], "gC": ["gC"],
}
def texts():
    src = open(os.path.join(os.path.dirname(__file__), "tts.py"), encoding="utf8").read()
    ns = {}; exec(src[src.index("LINES = ["):src.index("async def one")], ns)
    return {l[0]: l[1] for l in ns["LINES"]}
def block_text(b):
    T = texts(); return " ".join(T[i] for i in BLOCKS[b])
def synth(b):
    body = {"contents": [{"parts": [{"text": STYLE + block_text(b)}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "-m", "180", f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                            "-H", "x-goog-api-key: " + os.environ["GEMINI_API_KEY"], "-H", "Content-Type: application/json", "-d", "@-"],
                           input=json.dumps(body), capture_output=True, text=True)
        try:
            d = json.loads(r.stdout); part = d["candidates"][0]["content"]["parts"][0]["inlineData"]
            break
        except Exception:
            print("  falhou:", r.stdout[:300].replace("\n", " "), r.stderr[:200]); time.sleep(20 * (attempt + 1))
    else:
        raise SystemExit("sem áudio para " + b)
    raw = base64.b64decode(part["data"]); mime = part.get("mimeType", "")
    os.makedirs("assets/vo_gemini", exist_ok=True)
    out = f"assets/vo_gemini/{b}.wav"
    if "wav" in mime:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "-", "-ac", "1", "-ar", "48000", out], input=raw, check=True)
    else:  # PCM 16 bits, 24 kHz
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", "-ar", "48000", out], input=raw, check=True)
    print(b, mime, out)
if __name__ == "__main__":
    for b in (sys.argv[1:] or BLOCKS): synth(b)
