"""Baixa arquivos escolhidos do Commons (miniatura 1400px) e registra origem/licença em build/fontes_imagens.json."""
import json, sys, time, urllib.request, os, re
UA = {"User-Agent": "HistoriaCannabisVideo/1.0 (https://claude.ai/code; educational short video)"}
db = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
reg_p = "build/fontes_imagens.json"; reg = json.load(open(reg_p)) if os.path.exists(reg_p) else {}
for spec in sys.argv[3:]:            # nome=consulta#indice
    name, rest = spec.split("="); q, i = rest.rsplit("#", 1); f = db[q][int(i)]
    ext = os.path.splitext(f["thumb"].split("?")[0])[1].lower() or ".jpg"
    if ext in (".svg", ".gif", ".tif", ".tiff", ".djvu"): ext = ".png"
    dst = f"{out}/{name}{ext}"
    url = re.sub(r"/(\d+)px-", "/1280px-", f["thumb"]) if f["w"] > 1280 else f["thumb"]   # tamanho de miniatura padrão do Commons
    for k in range(4):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read(); break
        except Exception as e: print("retry", name, e); time.sleep(40 * (k + 1))
    else: print("FALHOU", name); continue
    open(dst, "wb").write(data); time.sleep(10)
    reg[name] = {"arquivo": dst, "titulo": f["title"], "licenca": f["lic"], "autor": re.sub("<[^>]+>", "", f["artist"]), "pagina": f["page"]}
    print("ok", name, f["lic"], f["title"][5:70])
json.dump(reg, open(reg_p, "w"), ensure_ascii=False, indent=1)
