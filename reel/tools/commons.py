import json,subprocess,sys,time,os,urllib.parse
def api(params):
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(dict(params,format='json'))
    for i in range(5):
        try: return json.loads(subprocess.check_output(['curl','-s','-m','30','-A','ReelResearchBot/1.0 (educational video project)',u]))
        except Exception: time.sleep(2+i*2)
    raise SystemExit('api fail')
out=json.load(open('assets/kit/commons.json')) if os.path.exists('assets/kit/commons.json') else {}
for q in sys.argv[1:]:
    r=api(dict(action='query',generator='search',gsrnamespace=6,gsrsearch=q+' filetype:bitmap',gsrlimit=12,prop='imageinfo',iiprop='url|size|extmetadata',iiurlwidth=1400))
    pages=sorted(r.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',0))
    for p in pages:
        ii=p['imageinfo'][0]; em=ii.get('extmetadata',{})
        lic=em.get('LicenseShortName',{}).get('value','?')
        print(q,'|',p['title'][:70],'|',ii['width'],'x',ii['height'],'|',lic)
        out[p['title']]=dict(q=q,thumb=ii.get('thumburl'),url=ii['url'],page=ii['descriptionurl'],license=lic,artist=em.get('Artist',{}).get('value','')[:200])
    time.sleep(1)
json.dump(out,open('assets/kit/commons.json','w'),indent=1)
