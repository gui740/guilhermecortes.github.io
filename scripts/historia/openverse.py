"""Busca/baixa imagens CC0 / domínio público / CC BY pelo Openverse (api.openverse.org)."""
import json, sys, time, os, urllib.request, urllib.parse
UA = {"User-Agent": "HistoriaCannabisVideo/1.0 (https://claude.ai/code; educational short video)"}
def j(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
def search(q, lic="cc0,pdm,by", n=20):
    src = None
    if q.startswith("wm:"): q, src = q[3:], "wikimedia"
    p = {"q": q, "license": lic, "page_size": n}
    if src: p["source"] = src
    r = j("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(p))
    return [{"id": x["id"], "title": (x.get("title") or "")[:90], "url": x["url"], "thumb": x.get("thumbnail"), "lic": f'{x["license"]} {x.get("license_version") or ""}'.strip(),
             "creator": x.get("creator") or "", "page": x.get("foreign_landing_url"), "src": x.get("source"), "w": x.get("width"), "h": x.get("height")} for x in r["results"]]
def fetch(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
if __name__ == "__main__":
    if sys.argv[1] == "search":
        db = {}
        for q in sys.argv[3:]:
            db[q] = search(q, lic="cc0,pdm,by,by-sa" if q.startswith("wm:") else "cc0,pdm,by"); time.sleep(1); print("\n##", q)
            for i, f in enumerate(db[q]): print(f"  {i:2d} {f['lic']:10s} {f['src'][:12]:12s} {f['w']}x{f['h']} {f['title'][:70]}")
        json.dump(db, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    else:
        db = json.load(open(sys.argv[2])); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
        reg_p = "build/fontes_imagens.json"; reg = json.load(open(reg_p)) if os.path.exists(reg_p) else {}
        for spec in sys.argv[4:]:
            name, rest = spec.split("="); q, i = rest.rsplit("#", 1); f = db[q][int(i)]; data = None
            for u in (f["url"], f["thumb"] + "?full_size=true", f["thumb"]):
                try: data = fetch(u); via = u; break
                except Exception as e: pass
            if not data: print("FALHOU", name); continue
            ext = ".png" if data[:4] == b"\x89PNG" else ".jpg"; dst = f"{out}/{name}{ext}"; open(dst, "wb").write(data)
            reg[name] = {"arquivo": dst, "titulo": f["title"], "licenca": f["lic"], "autor": f["creator"], "pagina": f["page"], "baixado_de": via}
            print("ok", name, len(data), f["lic"], f["title"][:50]); time.sleep(1)
        json.dump(reg, open(reg_p, "w"), ensure_ascii=False, indent=1)
