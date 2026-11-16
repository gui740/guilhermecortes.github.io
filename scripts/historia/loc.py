"""Busca e download no acervo da Library of Congress (loc.gov), com registro de origem."""
import json, sys, time, re, os, urllib.request, urllib.parse
UA = {"User-Agent": "HistoriaCannabisVideo/1.0 (educational short video)"}
def j(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
def search(q, n=10):
    r = j("https://www.loc.gov/photos/?" + urllib.parse.urlencode({"q": q, "fo": "json", "c": n}))
    out = []
    for it in r.get("results", []):
        imgs = it.get("image_url") or []
        if not imgs: continue
        big = re.sub(r"#.*$", "", imgs[-1])
        out.append({"title": it.get("title", "")[:110], "img": big, "page": it.get("id", ""), "date": it.get("date", ""),
                    "rights": "; ".join(it.get("rights_information", []) if isinstance(it.get("rights_information"), list) else [str(it.get("rights_information", ""))])[:120]})
    return out
if __name__ == "__main__":
    if sys.argv[1] == "search":
        db = {}
        for q in sys.argv[3:]:
            db[q] = search(q); time.sleep(1.5); print("\n##", q)
            for i, f in enumerate(db[q]): print(f"  {i:2d} {f['date'][:10]:10s} {f['title'][:85]} | {f['img'][-40:]}")
        json.dump(db, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    else:  # get db.json outdir nome=consulta#i ...
        db = json.load(open(sys.argv[2])); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
        reg_p = "build/fontes_imagens.json"; reg = json.load(open(reg_p)) if os.path.exists(reg_p) else {}
        for spec in sys.argv[4:]:
            name, rest = spec.split("="); q, i = rest.rsplit("#", 1); f = db[q][int(i)]
            cands = [re.sub(r"(_\d+px)?\.(jpg|gif)$", "v.jpg", f["img"]) if re.search(r"/pnp/", f["img"]) else None, f["img"].replace("_150px", "").replace("r.jpg", "v.jpg"), f["img"]]
            data = None
            for u in [c for c in cands if c]:
                try: data = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read(); break
                except Exception as e: pass
            if not data: print("FALHOU", name); continue
            dst = f"{out}/{name}.jpg"; open(dst, "wb").write(data); time.sleep(1.5)
            reg[name] = {"arquivo": dst, "titulo": f["title"], "licenca": "Library of Congress — " + (f["rights"] or "sem restrições conhecidas"), "pagina": f["page"], "data": f["date"]}
            print("ok", name, len(data), f["title"][:60])
        json.dump(reg, open(reg_p, "w"), ensure_ascii=False, indent=1)
