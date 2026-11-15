import json,urllib.request,urllib.parse,sys,os,concurrent.futures as cf
from PIL import Image,ImageDraw
Q={ 'id_mask':'topeng mask Java museum','id_wayang':'wayang kulit puppet','id_house':'joglo house Java','id_palm':'banana leaf isolated','id_offer':'sesajen offering Java','id_gong':'gamelan gong',
 'th_house':'traditional Thai stilt house wooden','th_spirit':'spirit house Thailand san phra phum','th_bamboo':'bamboo grove Thailand','th_mount':'Kanchanaburi mountains','th_banana':'banana tree Thailand',
 'tw_temple':'Taiwan temple roof','tw_lantern':'red lanterns Taiwan temple','tw_incense':'incense burner Taiwan temple','tw_talisman':'fulu talisman taoist paper','tw_tunnel':'Taiwan mountain tunnel old','cloud':'cumulus cloud isolated sky','paper':'old paper texture'}
def api(p):
    import time
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)
    for t in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'HorrorReelAssetBot/1.0 (educational video project; python-urllib)'}),timeout=40))
        except Exception as e: print('retry',e); time.sleep(8*(t+1))
    return {}
meta={}
def one(k):
    d=api({'action':'query','generator':'search','gsrsearch':Q[k]+' filetype:bitmap','gsrnamespace':6,'gsrlimit':8,'prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':1600,'format':'json'})
    out=[]
    for p in sorted(d.get('query',{}).get('pages',{}).values(),key=lambda p:p['index']):
        ii=p['imageinfo'][0];em=ii['extmetadata']
        out.append({'title':p['title'],'thumb':ii['thumburl'],'page':ii['descriptionurl'],'w':ii['width'],'h':ii['height'],'license':em.get('LicenseShortName',{}).get('value'),'artist':em.get('Artist',{}).get('value','')[:120]})
    return k,out
import time
for k in Q:
    meta[k]=one(k)[1]; time.sleep(1.5)
json.dump(meta,open('candidates.json','w'),indent=1,ensure_ascii=False)
def dl(a):
    k,i,c=a; fn=f'{k}_{i}.jpg'
    if not os.path.exists(fn):
        try:
            time.sleep(1.2); r=urllib.request.urlopen(urllib.request.Request(c['thumb'],headers={'User-Agent':'HorrorReelAssetBot/1.0 (educational video project; python-urllib)'}),timeout=60); open(fn,'wb').write(r.read())
        except Exception as e: print('fail',fn,e)
with cf.ThreadPoolExecutor(1) as ex: list(ex.map(dl,[(k,i,c) for k in meta for i,c in enumerate(meta[k])]))
