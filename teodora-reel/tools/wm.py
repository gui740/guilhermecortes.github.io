"""URLs do Wikimedia Commons a partir do nome do arquivo (sem chamar a API)."""
import hashlib, urllib.parse, urllib.request, time, os
UA = {"User-Agent": "CollageResearchBot/1.0 (educational, low-volume) python-urllib"}
def norm(name): return name.replace("File:", "").replace(" ", "_")
def orig(name):
    n = norm(name); h = hashlib.md5(n.encode()).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{urllib.parse.quote(n)}"
def thumb(name, w=500):
    n = norm(name); h = hashlib.md5(n.encode()).hexdigest(); q = urllib.parse.quote(n)
    base = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/"
    low = n.lower()
    if low.endswith((".tif", ".tiff")): return base + f"lossy-page1-{w}px-{q}.jpg"
    if low.endswith(".svg"): return base + f"{w}px-{q}.png"
    return base + f"{w}px-{q}"
def get(url, path):
    for i in range(6):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
            open(path, "wb").write(data); return True
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(int(e.headers.get("Retry-After") or 10) + 2); continue
            print("  HTTP", e.code, url); return False
        except Exception as e:
            time.sleep(5)
    return False
