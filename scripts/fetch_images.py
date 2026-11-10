"""Baixa pôster + stills (TMDB) e logos (Wikimedia) e registra as URLs de origem."""
import re, json, os, sys, urllib.request, urllib.parse
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36", "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"}
import subprocess
def get(u):
    # curl: o TMDB recusa o handshake do urllib
    return subprocess.run(["curl","-sS","-L","-m","90","-A",UA["User-Agent"],"-H","Accept-Language: pt-BR",u],capture_output=True,check=True).stdout
FILMS = {"blair": "2667", "demonio": "938614", "gonjiam": None}
out = {}
def find_id(q):
    h = get("https://www.themoviedb.org/search/movie?query=" + urllib.parse.quote(q)).decode("utf8", "ignore")
    return re.findall(r'href="/movie/(\d+)[^"]*"', h)[:5]
if len(sys.argv) > 1 and sys.argv[1] == "search":
    for q in sys.argv[2:]: print(q, find_id(q))
    sys.exit()
ids = json.load(open("assets/raw/ids.json"))
for key, mid in ids.items():
    d = f"assets/raw/{key}"; os.makedirs(d, exist_ok=True)
    rec = {"tmdb": f"https://www.themoviedb.org/movie/{mid}", "poster": [], "stills": []}
    for kind, n in (("posters", 2), ("backdrops", 14)):
        page = f"https://www.themoviedb.org/movie/{mid}/images/{kind}"
        h = get(page).decode("utf8", "ignore")
        paths = []
        for p in re.findall(r'/t/p/[a-z0-9_]+(/[A-Za-z0-9]+\.(?:jpg|png))', h):
            if p not in paths: paths.append(p)
        for i, p in enumerate(paths[:n]):
            url = "https://image.tmdb.org/t/p/original" + p
            fn = f"{d}/{kind[:-1]}_{i}{os.path.splitext(p)[1]}"
            if not os.path.exists(fn): open(fn, "wb").write(get(url))
            rec["poster" if kind == "posters" else "stills"].append({"file": fn, "url": url, "page": page})
    out[key] = rec
    print(key, len(rec["poster"]), len(rec["stills"]))
json.dump(out, open("assets/raw/sources.json", "w"), indent=1, ensure_ascii=False)
