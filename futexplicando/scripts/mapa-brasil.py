"""Converte o GeoJSON dos estados (click_that_hood, licença MIT/ODbL) em paths SVG simplificados (viewBox 1000x1000)."""
import json, os, math
ROOT = os.path.join(os.path.dirname(__file__), "..")
g = json.load(open(os.path.join(ROOT, "public", "copa-do-brasil", "raw", "brazil-states.geojson")))
LON0, LON1, LAT0, LAT1 = -74.5, -34.0, -34.5, 6.0
def proj(lon, lat):
    x = (lon - LON0) / (LON1 - LON0) * 1000
    y = (LAT1 - lat) / (LAT1 - LAT0) * 1000 * 1.0
    return round(x, 1), round(y, 1)
def simplify(pts, tol=1.6):
    out = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0]-out[-1][0], p[1]-out[-1][1]) >= tol: out.append(p)
    return out
estados = []
for f in g["features"]:
    pr = f["properties"]; sigla = pr.get("sigla") or pr.get("name")
    geom = f["geometry"]; polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    d = []; sx = sy = n = 0
    for poly in polys:
        ring = simplify([proj(*c) for c in poly[0]])
        if len(ring) < 4: continue
        d.append("M" + "L".join(f"{x},{y}" for x, y in ring) + "Z")
        for x, y in ring: sx += x; sy += y; n += 1
    estados.append({"sigla": sigla, "nome": pr.get("name"), "d": "".join(d), "cx": round(sx/n, 1), "cy": round(sy/n, 1)})
json.dump(estados, open(os.path.join(ROOT, "src", "data", "brasil-estados.json"), "w"), ensure_ascii=False)
print(len(estados), [e["sigla"] for e in estados], os.path.getsize(os.path.join(ROOT, "src", "data", "brasil-estados.json")))
