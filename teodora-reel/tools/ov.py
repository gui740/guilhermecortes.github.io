"""Busca no Openverse restrita ao Wikimedia Commons, licenças livres para uso comercial (PDM, CC0, BY, BY-SA)."""
import json, sys, time, urllib.request, urllib.parse, os
res = json.load(open('ov_found.json')) if os.path.exists('ov_found.json') else {}
for q in sys.argv[1:]:
    p = urllib.parse.urlencode({"q": q, "source": "wikimedia", "license": "pdm,cc0,by,by-sa", "page_size": 14})
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request("https://api.openverse.org/v1/images/?" + p, headers={"User-Agent": "TeodoraReelBot/1.1"}), timeout=40))
    except Exception as e:
        print("ERR", q, e); time.sleep(5); continue
    res[q] = d["results"]
    print("==", q, d["result_count"])
    for r in d["results"]:
        print(f"  {r['title'][:80]} | {r['license']} {r.get('license_version') or ''} | {r.get('width')}x{r.get('height')}")
    json.dump(res, open('ov_found.json', 'w'), indent=1)
    time.sleep(1.2)
