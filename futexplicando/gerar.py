#!/usr/bin/env python3
"""Gera as imagens de uma historia via Gemini (Nano Banana Pro).

Uso:
  python gerar.py historias/galo1981.json            # gera tudo que falta
  python gerar.py historias/galo1981.json ficha_mestre galo_neutro   # so esses
  python gerar.py historias/galo1981.json --force galo_neutro        # refaz

A chave vem de GEMINI_API_KEY (ou ~/.gemini_key). Nunca grave a chave no projeto.
Backend: GEMINI_BACKEND=vertex (padrao) ou studio.
"""
import base64, json, os, sys, time, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent


def api_key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        p = pathlib.Path.home() / ".gemini_key"
        if p.exists():
            k = p.read_text().strip()
    if not k:
        sys.exit("Defina GEMINI_API_KEY")
    return k


def endpoint(model):
    if os.environ.get("GEMINI_BACKEND", "vertex") == "studio":
        return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", {"x-goog-api-key": api_key()}
    return f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent?key={api_key()}", {}


def call(model, body, tries=4):
    url, headers = endpoint(model)
    headers["Content-Type"] = "application/json"
    for t in range(tries):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:500]
            if e.code in (429, 500, 503) and t < tries - 1:
                time.sleep(10 * (t + 1)); continue
            raise SystemExit(f"HTTP {e.code}: {msg}")


def img_part(path):
    p = ROOT / path
    mime = "image/png" if p.suffix == ".png" else "image/jpeg"
    return {"inlineData": {"mimeType": mime, "data": base64.b64encode(p.read_bytes()).decode()}}


def gerar(item, cfg, outdir):
    out = outdir / item["arquivo"]
    parts = [img_part(r) for r in item.get("referencias", [])]
    prompt = item["prompt"]
    if cfg.get("estilo_comum") and item.get("usar_estilo_comum", True):
        prompt = prompt + "\n\n" + cfg["estilo_comum"]
    parts.append({"text": prompt})
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": item.get("proporcao", "1:1")},
        },
    }
    res = call(cfg.get("modelo_imagem", "gemini-3-pro-image-preview"), body)
    for c in res.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(base64.b64decode(p["inlineData"]["data"]))
                return out
    raise SystemExit(f"Sem imagem para {item['id']}: {json.dumps(res)[:500]}")


def main():
    args = sys.argv[1:]
    force = "--force" in args
    args = [a for a in args if a != "--force"]
    cfg = json.loads((ROOT / args[0]).read_text())
    only = set(args[1:])
    outdir = ROOT / cfg["pasta_assets"]
    for item in cfg["imagens"]:
        if only and item["id"] not in only:
            continue
        out = outdir / item["arquivo"]
        if out.exists() and not force:
            print("pula", item["id"]); continue
        missing = [r for r in item.get("referencias", []) if not (ROOT / r).exists()]
        if missing:
            print("aguardando referencia", item["id"], missing); continue
        t = time.time()
        gerar(item, cfg, outdir)
        print(f"ok {item['id']} ({time.time()-t:.0f}s)")


if __name__ == "__main__":
    main()
