import json,urllib.request,urllib.parse,os,time,sys
from PIL import Image,ImageDraw
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) Chrome/126 Safari/537.36'}
Q=json.loads(sys.argv[1]); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
meta=json.load(open(out+'/meta.json')) if os.path.exists(out+'/meta.json') else {}
for k,q in Q.items():
    if k in meta: continue
    u='https://api.openverse.org/v1/images/?'+urllib.parse.urlencode({'q':q,'page_size':8,'license':'cc0,pdm,by,by-sa','mature':'false','source':'flickr'})
    try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
    except Exception as e: print(k,'ERR',e); time.sleep(5); continue
    meta[k]=[]
    for i,r in enumerate(d['results']):
        fn=f'{out}/{k}_{i}.jpg'
        try:
            open(fn,'wb').write(urllib.request.urlopen(urllib.request.Request(r['thumbnail']+'?full_size=true',headers=UA),timeout=60).read()); Image.open(fn).verify()
        except Exception as e:
            if os.path.exists(fn): os.remove(fn)
            continue
        meta[k].append({'file':os.path.basename(fn),'title':r.get('title'),'creator':r.get('creator'),'license':r.get('license'),'license_version':r.get('license_version'),'page':r.get('foreign_landing_url'),'source':r.get('source')})
    time.sleep(1.2); json.dump(meta,open(out+'/meta.json','w'),ensure_ascii=False,indent=1)
    # contact sheet
    tiles=[]
    for m in meta[k]:
        im=Image.open(out+'/'+m['file']).convert('RGB'); sz=im.size; im.thumbnail((300,220)); t=Image.new('RGB',(300,240),'white'); t.paste(im,(0,0)); ImageDraw.Draw(t).text((3,224),'%s %dx%d %s'%(m['file'],*sz,m['license']),fill='black'); tiles.append(t)
    if tiles:
        sh=Image.new('RGB',(300*len(tiles),240),'white')
        for i,t in enumerate(tiles): sh.paste(t,(300*i,0))
        sh.save(f'{out}/_cs_{k}.jpg',quality=70)
    print(k,len(meta[k]))
