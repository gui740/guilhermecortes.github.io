# Segmentação de alta qualidade com BiRefNet (rembg) sobre stills candidatas. Salva máscara suave (0-255).
import glob, os, sys, time
from PIL import Image
from rembg import new_session, remove
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = ['477033/2HnptuDU','477033/aEzgJI57','477033/nSCEgpwC','477033/pymXjNBy','477033/xhoHM4zE','477033/xKF1B9wl','477033/cYxWqbdZ',
     '424121/4BJi7377','424121/58EDJlVN','424121/7Y567LQG','424121/9laS3d3q','424121/dbrZtHyh','424121/tvGTSdLj','424121/xvFwSLv9','424121/a3qsXYK0','424121/dnU1fJ53',
     '864370/11eJ9OWv','864370/5j3YVzeo','864370/6d1mHKco','864370/bfjLErae','864370/cEcz50ZF','864370/eCL3LXv1','864370/h3tpJXKs','864370/cg5xvUeM','864370/cHDFdIj6','864370/kdCSEl5y']
only = sys.argv[2] if len(sys.argv) > 2 else None   # uma imagem por processo (o ONNX do BiRefNet acumula memória)
sess = new_session(sys.argv[1] if len(sys.argv) > 1 else 'birefnet-general')
for c in ([only] if only else C):
    d, p = c.split('/'); f = glob.glob(f'{ROOT}/assets/raw/{d}/{p}*')[0]
    out = f'{ROOT}/assets/masks_bf/{d}_{p}.png'
    if os.path.exists(out): continue
    t0 = time.time()
    m = remove(Image.open(f).convert('RGB'), session=sess, only_mask=True)
    m.save(out); print(c, round(time.time() - t0, 1), 's', flush=True)
print('SEGDONE' if not only else '', flush=True)
