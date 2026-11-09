#!/usr/bin/env python3
"""Busca/baixa imagens livres do Wikimedia Commons e registra crédito.
uso: commons.py search "termo"   |   commons.py get pasta "File:Nome.jpg" nome_local"""
import os, sys, json, time, urllib.request, urllib.parse, pathlib
UA = {"User-Agent": "reel-builder/1.0 (educational video project)"}
ROOT = pathlib.Path(__file__).resolve().parent.parent
def api(**p):
    p.update(format="json", action="query")
    for t in range(6):
        try:
            r = urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p), headers=UA), timeout=60)
            return json.load(r)
        except Exception as e:
            print("  retry", e, file=sys.stderr); time.sleep(5 * (t + 1))
    raise SystemExit("falhou")
def info(pages):
    for pg in pages.values():
        ii = pg["imageinfo"][0]; md = ii.get("extmetadata", {})
        yield pg["title"], ii, md.get("LicenseShortName", {}).get("value", "?"), md.get("Artist", {}).get("value", "?")
if sys.argv[1] == "search":
    d = api(generator="search", gsrsearch=sys.argv[2] + " filetype:bitmap", gsrnamespace=6, gsrlimit=10, prop="imageinfo", iiprop="url|size|extmetadata")
    for t, ii, lic, art in info(d.get("query", {}).get("pages", {})):
        print(ii["width"], "x", ii["height"], lic, "|", t)
else:
    pasta, titulo, nome = sys.argv[2:5]
    d = api(titles=titulo, prop="imageinfo", iiprop="url|size|extmetadata", iiurlwidth=int(os.environ.get("W","1920")))
    t, ii, lic, art = next(info(d["query"]["pages"]))
    url = ii.get("thumburl") or ii["url"]
    dest = ROOT / "assets" / "raw" / pasta / nome
    dest.parent.mkdir(parents=True, exist_ok=True)
    for k in range(6):
        try:
            dest.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()); break
        except Exception as e:
            print("  retry", e, file=sys.stderr); time.sleep(5 * (k + 1))
    else:
        raise SystemExit("download falhou: " + url)
    import re
    art = re.sub("<[^>]+>", "", art).strip()
    with open(ROOT / "assets" / "raw" / "fontes.tsv", "a") as f:
        f.write(f"{pasta}\t{nome}\t{ii['descriptionurl']}\tWikimedia Commons, {lic}, autor: {art}\n")
    print("ok", dest)
