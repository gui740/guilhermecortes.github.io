"""Gera/edita imagem no Gemini (Nano Banana). Chave só pela variável GEMINI_API_KEY.
Uso: python3 gimg.py <modelo> <saida.png> <aspect> <size> "<prompt>" [ref1.png ref2.png ...]"""
import base64, json, os, sys, time, urllib.request, urllib.error
KEY = os.environ["GEMINI_API_KEY"]
def gen(model, out, prompt, refs=(), aspect="9:16", size="2K"):
    parts = [{"text": prompt}]
    for r in refs:
        mt = "image/png" if r.lower().endswith(".png") else "image/jpeg"
        parts.append({"inline_data": {"mime_type": mt, "data": base64.b64encode(open(r, "rb").read()).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect, "imageSize": size}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for k in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
            d = json.load(urllib.request.urlopen(req, timeout=300)); break
        except urllib.error.HTTPError as e:
            msg = e.read()[:400]; print("HTTP", e.code, msg)
            if e.code in (400, 403, 404): sys.exit(1)
            time.sleep(15)
    imgs = [p["inlineData"] for c in d.get("candidates", []) for p in c["content"]["parts"] if "inlineData" in p]
    if not imgs:
        print(json.dumps(d)[:600]); sys.exit(1)
    open(out, "wb").write(base64.b64decode(imgs[-1]["data"]))  # a última é a final (as anteriores podem ser "thought images")
    print(out, imgs[-1]["mimeType"], d.get("usageMetadata", {}).get("candidatesTokenCount"))
if __name__ == "__main__":
    m, out, asp, size, prompt, *refs = sys.argv[1:]
    gen(m, out, prompt, refs, asp, size)
