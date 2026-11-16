"""Busca no Wikimedia Commons: lista arquivos (título, licença, autor, tamanho)."""
import json, sys, urllib.parse, urllib.request, urllib.error
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "historia-video-bot/1.0 (educational video; contact via repo)"}
import time
def get(params, tries=6):
    for k in range(tries):
        try: return _get(params)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(4 * (k + 1))
    raise RuntimeError("429 persistente")
def _get(params):
    q = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    return json.load(urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=40))
def search(q, n=12):
    r = get({"action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": n,
             "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1400})
    out = []
    for p in sorted(r.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]; md = ii.get("extmetadata", {})
        if not ii["mime"].startswith("image/"): continue
        out.append({"title": p["title"], "lic": md.get("LicenseShortName", {}).get("value", ""), "w": ii["width"], "h": ii["height"],
                    "thumb": ii.get("thumburl", ii["url"]), "page": ii["descriptionurl"],
                    "artist": urllib.parse.unquote(md.get("Artist", {}).get("value", ""))[:80]})
    return out
if __name__ == "__main__":
    res = {}
    for q in sys.argv[2:]:
        time.sleep(2.5)
        try: res[q] = search(q)
        except Exception as e: print("ERRO", q, e); continue
        print("\n##", q)
        for i, f in enumerate(res[q]): print(f"  {i:2d} {f['lic'][:18]:18s} {f['w']}x{f['h']} {f['title'][5:90]}")
    json.dump(res, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
