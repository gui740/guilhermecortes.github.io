# Narração via Gemini TTS (Google AI Studio). A chave vem SÓ da variável GEMINI_API_KEY (nunca gravada em arquivo).
# Uso: GEMINI_API_KEY=... python3 src/tts_gemini.py <voz> <saida.wav> [arquivo_de_linhas.json] [--modelo M]
import os, sys, json, base64, urllib.request, subprocess

KEY = os.environ['GEMINI_API_KEY']
MODEL = 'gemini-3.8-flash-tts'
if '--modelo' in sys.argv:
    MODEL = sys.argv[sys.argv.index('--modelo') + 1]

DIRECAO = """# AUDIO PROFILE: Narrador jovem brasileiro (uns 25 anos), criador de conteúdo de terror no Instagram.
## A CENA: Ele grava um Reel no quarto, empolgado, contando pra um amigo três filmes de terror que quase ninguém viu.
### NOTAS DO DIRETOR (não leia em voz alta)
Idioma: português do Brasil, sotaque paulista neutro, fala coloquial de verdade.
Estilo: conversa com amigo, nada de locutor, anúncio ou leitura robótica. Energia alta e sorriso na voz.
Ritmo: rápido, de Reels, com variação real: acelera nas premissas, segura um respiro de suspense e baixa um pouco a voz logo antes de cada título de filme.
Emoção: malícia no gancho; empolgação em "O dois é pior"; cumplicidade em "Manda pro amigo"; tom sério e arrepiado no número um; a pergunta final é uma provocação.
Pronúncia: leia "cê" exatamente como "cê" (NUNCA "você"); "pra" como "pra" (nunca "para"); "Errementari" = "É-rre-men-TÁ-ri"; "Netflix" como em inglês; "The Raid" = "dê rêid"; "Talking Horror" em inglês.
#### TRANSCRIÇÃO (leia só isto, exatamente)
"""

def tts(text, voice, out_wav):
    body = {
        "contents": [{"parts": [{"text": DIRECAO + text}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}},
    }
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                                 json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
    d = json.load(urllib.request.urlopen(req, timeout=300))
    part = d['candidates'][0]['content']['parts'][0]['inlineData']
    pcm = base64.b64decode(part['data'])
    rate = 24000
    for kv in part.get('mimeType', '').split(';'):
        if kv.strip().startswith('rate='): rate = int(kv.split('=')[1])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(rate), '-ac', '1', '-i', '-', out_wav], input=pcm, check=True)

if __name__ == '__main__':
    voice, out = sys.argv[1], sys.argv[2]
    src = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
    if src:
        L = json.load(open(src)); text = ' '.join(l['text'] for l in L)
    else:
        text = "Três filmes de ritual que cê nunca viu, e o último amaldiçoa quem assiste."
    tts(text, voice, out)
    print(out)
