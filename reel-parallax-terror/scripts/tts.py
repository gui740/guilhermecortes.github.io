#!/usr/bin/env python3
"""Gera narração com Gemini TTS. A chave vem SEMPRE de GEMINI_API_KEY (nunca no código).
Uso:
  python3 scripts/tts.py teste            -> amostras de voz em out/testes-voz/
  python3 scripts/tts.py cenas VOZ        -> um .wav por cena em assets/narracao/
"""
import base64, json, os, subprocess, sys, urllib.request, urllib.error, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
# Obs.: no plano gratuito o gemini-3.8-flash-tts tem só 10 req/dia e o 2.5-pro-tts tem cota zero.
# Com billing ativo, troque por GEMINI_TTS_MODEL=gemini-3.8-flash-tts (ou o 2.5-pro).
KEY = os.environ.get("GEMINI_API_KEY")
if not KEY:
    sys.exit("Defina GEMINI_API_KEY no ambiente.")

# Direção de interpretação. Só o que vem depois de "#### TRANSCRIPT" é falado.
DIRECAO = """# AUDIO PROFILE: Narrador do @talking_horror
Homem adulto, voz grave e baixa, português do Brasil com sotaque neutro.

## THE SCENE
Madrugada, luz apagada. Um amigo que viu coisa demais conta, bem perto do microfone,
sobre filmes de terror que ninguém indica.

### DIRECTOR'S NOTES
Estilo: conversa íntima, intrigada, levemente desconfortável. Nunca teatral, nunca locutor
de comercial, nada de voz robótica.
Ritmo: calmo, pausas naturais nas reticências e entre frases, respiração audível.
Não leia estas notas, fale apenas o TRANSCRIPT.

#### TRANSCRIPT
"""

CENAS = json.loads((ROOT / "config" / "roteiro.json").read_text())

def tts(texto: str, voz: str, saida: pathlib.Path):
    body = {
        "contents": [{"parts": [{"text": DIRECAO + texto}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz}}},
        },
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
    )
    import time
    for tentativa in range(8):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            corpo = e.read().decode(errors="ignore")
            if "PerDay" in corpo:
                raise SystemExit(f"Cota diária do {MODEL} esgotada (plano gratuito).")
            if e.code in (429, 500, 503) and tentativa < 7:
                espera = 20 * (tentativa + 1)
                print(f"  {e.code}, tentando de novo em {espera}s"); time.sleep(espera)
            else:
                raise
    pcm = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    saida.parent.mkdir(parents=True, exist_ok=True)
    raw = saida.with_suffix(".pcm")
    raw.write_bytes(pcm)
    # PCM 16-bit 24kHz mono -> wav
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", "24000", "-ac", "1",
                    "-i", str(raw), str(saida)], check=True)
    raw.unlink()
    print("ok", saida)

if __name__ == "__main__":
    modo = sys.argv[1]
    if modo == "teste":
        vozes = sys.argv[2:] or ["Charon", "Algenib", "Enceladus", "Orus"]
        for v in vozes:
            tts(CENAS["gancho"], v, ROOT / "out" / "testes-voz" / f"{v}.wav")
    else:
        voz = sys.argv[2]
        cenas = sys.argv[3:] or list(CENAS)
        for k in cenas:
            tts(CENAS[k], voz, ROOT / "assets" / "narracao" / f"{k}.wav")
