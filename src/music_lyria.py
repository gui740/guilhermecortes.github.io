# Gera trilha instrumental com Lyria (Google AI Studio). Chave só via GEMINI_API_KEY.
# Uso: GEMINI_API_KEY=... python3 src/music_lyria.py saida.(wav|mp3) [modelo] [prompt]
import os, sys, json, base64, urllib.request
KEY = os.environ['GEMINI_API_KEY']
out = sys.argv[1]; model = sys.argv[2] if len(sys.argv) > 2 else 'lyria-3.5'
prompt = sys.argv[3] if len(sys.argv) > 3 else (
    "Instrumental dark horror rock for a fast-paced 35-second vertical video about folk horror films. "
    "Heavy downtuned distorted electric guitar riff, driving live drums with punchy kick and snare, thick bass, "
    "about 125 BPM, minor key, ominous and energetic, stoner/doom rock with a hint of folk (a low tom pattern). "
    "Starts immediately with the riff (no long intro), builds intensity, short breakdown in the middle, "
    "bigger final section. No vocals, no singing, no spoken words.")
body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["AUDIO"]}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                             json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
try:
    d = json.load(urllib.request.urlopen(req, timeout=600))
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read()[:600].decode()); sys.exit(1)
parts = d['candidates'][0]['content']['parts']
for p in parts:
    if 'inlineData' in p:
        open(out, 'wb').write(base64.b64decode(p['inlineData']['data'])); print(out, p['inlineData'].get('mimeType'))
    elif 'text' in p: print('texto:', p['text'][:300])
