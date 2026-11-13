"""Helper para buscar/baixar arquivos do Wikimedia Commons com metadados de licença."""
import re, json, sys, time, urllib.request, urllib.error, urllib.parse, os
UA = "TeodoraReelBot/1.1 (https://github.com/gui740/guilhermecortes.github.io; educational) python-urllib"
API = "https://commons.wikimedia.org/w/api.php"
def get(params, tries=12):
    params = dict(params, format="json", maxlag=5)
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return json.load(urllib.request.urlopen(req, timeout=40))
        except urllib.error.HTTPError as e:
            ra = int(e.headers.get("Retry-After") or 20)
            print(f"   (HTTP {e.code}, aguardando {ra+2}s)", file=sys.stderr, flush=True)
            time.sleep(ra + 2)
        except Exception as e:
            time.sleep(10)
    raise RuntimeError("falhou: " + url)
def search(q, n=15, ns="6"):
    d = get({"action": "query", "list": "search", "srsearch": q, "srnamespace": ns, "srlimit": n})
    return [x["title"] for x in d["query"]["search"]]
def catmembers(cat, n=50):
    d = get({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmlimit": n, "cmtype": "file|subcat"})
    return [x["title"] for x in d["query"]["categorymembers"]]
def gsearch(q, n=12):
    d = get({"action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": n,
             "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiextmetadatafilter": "LicenseShortName|Artist|DateTimeOriginal|ImageDescription|Credit", "iiurlwidth": 1600})
    return _parse(d)
def _parse(d):
    out = []
    for p in d.get("query", {}).get("pages", {}).values():
        if "imageinfo" not in p: continue
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        g = lambda k: (m.get(k, {}).get("value") or "")
        out.append(dict(title=p["title"], url=ii["url"], thumb=ii.get("thumburl"), w=ii["width"], h=ii["height"],
                        license=g("LicenseShortName"), artist=re.sub("<[^>]+>","",g("Artist"))[:120], date=re.sub("<[^>]+>","",g("DateTimeOriginal"))[:40],
                        page="https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_"))))
    return out
def info(titles):
    d = get({"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
             "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1600})
    out = []
    for p in d["query"]["pages"].values():
        if "imageinfo" not in p: continue
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        g = lambda k: (m.get(k, {}).get("value") or "")
        out.append(dict(title=p["title"], url=ii["url"], thumb=ii.get("thumburl"), w=ii["width"], h=ii["height"],
                        mime=ii.get("mime"), license=g("LicenseShortName"), artist=g("Artist"), date=g("DateTimeOriginal"),
                        credit=g("Credit"), desc=g("ImageDescription")[:200],
                        page="https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_"))))
    return out
def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(5):
        try:
            data = urllib.request.urlopen(req, timeout=90).read()
            open(path, "wb").write(data); return path
        except Exception:
            time.sleep(3 + 4 * i)
    raise RuntimeError("download falhou " + url)
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        for q in sys.argv[2:]:
            print("==", q)
            ts = search(q)
            for r in info(ts) if ts else []:
                print(f"  {r['title'][:90]} | {r['license']} | {r['w']}x{r['h']}")
            time.sleep(1)
    elif cmd == "cat":
        for c in sys.argv[2:]:
            print("==", c)
            for t in catmembers(c): print("  ", t)
