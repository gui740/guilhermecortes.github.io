import sys, os, numpy as np
from PIL import Image
from rembg import new_session, remove
R='assets/raw/'
S={ 'e_smith':'477033/2HnptuDUrUwWarEqJ0UKpWmRbay','e_mask':'477033/nSCEgpwCZK2xvBpBnPsmBjatimI','e_girl':'477033/xhoHM4zEY359isn59VeFJTdXejY','e_fence':'477033/cq5f3HHiNM9OoXxUnVR5M1Kqzpu',
 'a_dan':'424121/xvFwSLv9bMsXA2slpQhZA63YEA5','a_hill':'424121/4BJi7377x2PJWna8vjORIDRyYha','a_hood':'424121/7Y567LQGQTb5IPbcqQKR8jtXnHB','a_book':'424121/58EDJlVNVPpSuVIVA6zeaWhNYq6','a_boat':'424121/tvGTSdLjKJgFHTcF4x9HSxoTIgW',
 'i_face':'864370/cEcz50ZFqSRgI0fqaNqVBYWCEm9','i_lantern':'864370/5j3YVzeo9gVGz36gJVl7PGekGPw','i_hands':'864370/6d1mHKcozT5AaZeI76ehJrBt0hr','i_woman':'864370/bfjLEraeBQ9Er79QEJeHwQal6e9','i_flash':'864370/11eJ9OWvXOmQoYYxFktJ0xvonU3','i_candle':'864370/cHDFdIj6VZtZBqcvPWB7qW9p74g'}
import glob
sess=new_session(sys.argv[1] if len(sys.argv)>1 else 'isnet-general-use')
for k,v in S.items():
    f=glob.glob(R+v.split('/')[0]+'/'+v.split('/')[1][:8]+'*')[0]
    im=Image.open(f).convert('RGB')
    m=remove(im,session=sess,only_mask=True)
    m.save(f'assets/masks/{k}.png'); print(k,f)
