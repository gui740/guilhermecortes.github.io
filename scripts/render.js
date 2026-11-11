// Renderiza quadros do reel com Chromium (Playwright).
//   node scripts/render.js all            -> build/frames/f00000.jpg … (30 fps)
//   node scripts/render.js check t1,t2,…  -> build/check/t_XX.XX.jpg
const { chromium } = require('playwright'); const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '..'), FPS = 30, N = 4;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2' };
const srv = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); r.end(d); } }); });
(async () => {
  await new Promise(r => srv.listen(0, r)); const url = `http://127.0.0.1:${srv.address().port}/reel/index.html`;
  const b = await chromium.launch();
  const open = async () => { const p = await b.newPage({ viewport: { width: 1080, height: 1920 } }); p.on('pageerror', e => { console.error('ERRO', e.message); process.exit(1); }); await p.goto(url); await p.evaluate(() => window.ready); await p.waitForLoadState('networkidle'); return p; };
  const shot = async (p, t, file) => { await p.evaluate(t => { window.seek(t); return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); }, t); await p.screenshot({ path: file, type: 'jpeg', quality: 93, clip: { x: 0, y: 0, width: 1080, height: 1920 } }); };
  const mode = process.argv[2];
  if (mode === 'check') {
    const p = await open(); fs.mkdirSync(ROOT + '/build/check', { recursive: true });
    for (const t of process.argv[3].split(',').map(Number)) await shot(p, t, `${ROOT}/build/check/t_${t.toFixed(2).padStart(5, '0')}.jpg`);
    const info = await p.evaluate(() => ({ sfx: window.SFX, shots: window.SHOTS, dur: window.DURACAO, textos: Object.fromEntries(['url1', 'url2', 'urlm', 'url3', 'url4', 'url5', 'tel1', 'tel2', 'tel3'].map(i => [i, document.getElementById(i).textContent])) }));
    fs.writeFileSync(ROOT + '/build/info.json', JSON.stringify(info, null, 1));
  } else {
    const p0 = await open(); const dur = await p0.evaluate(() => window.DURACAO); const total = Math.round(dur * FPS);
    const from = +(process.argv[3] || 0), to = +(process.argv[4] || total);
    fs.mkdirSync(ROOT + '/build/frames', { recursive: true });
    const pages = [p0]; for (let i = 1; i < N; i++) pages.push(await open());
    let done = 0; await Promise.all(pages.map(async (p, k) => { for (let f = from + k; f < to; f += N) { await shot(p, f / FPS, `${ROOT}/build/frames/f${String(f).padStart(5, '0')}.jpg`); if (++done % 300 === 0) console.log(done, '/', to - from); } }));
    console.log('quadros:', total);
  }
  await b.close(); srv.close();
})();
