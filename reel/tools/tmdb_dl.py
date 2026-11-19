import re,urllib.request,json,os,time,subprocess
def get(u): return subprocess.check_output(['curl','-sL','-A','Mozilla/5.0 Chrome/124',u])
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) Chrome/124"}
films={'ghostland':476299,'medium':745881,'huesera':772515}
src={}
for k,i in films.items():
    os.makedirs(f'assets/films/{k}',exist_ok=True); src[k]=[]
    for kind in ['backdrops','posters']:
        h=get(f'https://www.themoviedb.org/movie/{i}/images/{kind}').decode()
        paths=list(dict.fromkeys(re.findall(r'/t/p/w(?:500|1000)_and_h\d+_face(/[A-Za-z0-9]+\.jpg)',h)+re.findall(r'/t/p/w(?:220_and_h330|500)(?:_face)?(/[A-Za-z0-9]+\.jpg)',h)))
        for n,p in enumerate(paths[:14 if kind=='backdrops' else 4]):
            url='https://image.tmdb.org/t/p/original'+p; fn=f'assets/films/{k}/{kind[:-1]}_{n:02d}.jpg'
            if not os.path.exists(fn):
                open(fn,'wb').write(get(url))
            src[k].append(dict(file=fn,url=url,page=f'https://www.themoviedb.org/movie/{i}/images/{kind}'))
        time.sleep(1)
    print(k,len(src[k]))
json.dump(src,open('assets/films/sources.json','w'),indent=1)
