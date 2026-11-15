// Renderiza todos os textos/gráficos como PNG transparente (Chromium), com versão desfocada p/ a entrada (blur 12px).
import {createRequire} from 'module';
const {chromium} = createRequire(import.meta.url)(process.env.PLAYWRIGHT_PATH || 'playwright');
import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const F = (f) => 'file://' + path.join(ROOT, 'assets/fonts', f);
const K = '#1C1C1C', R = '#F23B3B', Y = '#F2E63A', G = '#EDEDED', W = '#FFFFFF';
const svg = (n) => fs.readFileSync(path.join(ROOT, 'assets/raw/logos', n + '.svg'), 'utf8').match(/<path d="([^"]+)"/)[1];

const anton = (t, c, size = 360) => `<span style="font-family:Anton;font-size:${size}px;line-height:1.02;color:${c};letter-spacing:-0.01em;padding:0 8px">${t}</span>`;
const play = (t, c, size = 200, w = 800) => `<span style="font-family:Playfair;font-style:italic;font-weight:${w};font-size:${size}px;line-height:1.1;color:${c};display:inline-block;transform:scaleX(.8);transform-origin:left top;padding:0 ${size * 0.12}px ${size * 0.1}px 0;white-space:nowrap">${t}</span>`;
const strip = (title, orig, bg, fg, origFont = 'Inter') => `<div style="display:inline-block;background:${bg};padding:26px 56px 30px 44px;transform:rotate(-1.2deg);margin:30px;box-shadow:0 0 0 7px ${W}">
  <div style="font-family:Playfair;font-style:italic;font-weight:900;font-size:150px;line-height:1.02;color:${fg};transform:scaleX(.8);transform-origin:left top;white-space:nowrap;margin-right:-20%">${title}</div>
  <div style="font-family:${origFont},Inter;font-weight:600;font-size:46px;color:${fg};opacity:.9;margin-top:10px;letter-spacing:.02em">${orig}</div></div>`;
const stamp = (a, b, c = R) => `<div style="display:inline-block;margin:30px;transform:rotate(-8deg);border:10px solid ${c};border-radius:26px;padding:10px;opacity:.92">
  <div style="border:4px solid ${c};border-radius:14px;padding:14px 40px 10px;text-align:center">
  <div style="font-family:Anton;font-size:120px;line-height:1;color:${c};letter-spacing:.04em">${a}</div>
  <div style="font-family:Inter;font-weight:800;font-size:44px;color:${c};letter-spacing:.3em;margin-top:6px">✦ ${b} ✦</div></div></div>`;
const logo = (name, label, sub, bg, fg, icon) => `<div style="display:inline-flex;align-items:center;gap:26px;background:${bg};padding:22px 44px 22px 30px;margin:30px;border-radius:999px;box-shadow:0 0 0 7px ${W}">
  <svg viewBox="0 0 24 24" width="120" height="120"><path d="${svg(name)}" fill="${icon}"/></svg>
  <div><div style="font-family:Inter;font-weight:800;font-size:40px;color:${fg};opacity:.8;letter-spacing:.08em">${sub}</div>
  <div style="font-family:Anton;font-size:110px;line-height:1;color:${fg};letter-spacing:.02em">${label}</div></div></div>`;
const star = () => { let p = ''; const n = 18; for (let i = 0; i < n * 2; i++) { const r = i % 2 ? 300 : 500, a = Math.PI * i / n; p += `${500 + r * Math.cos(a)},${500 + r * Math.sin(a)} `; }
  return `<svg width="1000" height="1000"><polygon points="${p}" fill="${Y}" stroke="${W}" stroke-width="10"/></svg>`; };
const pin = () => `<svg width="300" height="420" viewBox="0 0 300 420"><path d="M150 405 C150 405 30 250 30 150 A120 120 0 1 1 270 150 C270 250 150 405 150 405Z" fill="${R}" stroke="${W}" stroke-width="12"/><circle cx="150" cy="150" r="46" fill="${W}"/></svg>`;

const items = {
  // gancho (sobre cinza)
  hk1: anton('TRÊS', K), hk2: anton('FILMES,', K), hk3: anton('TRÊS', K), hk4: anton('MALDIÇÕES,', R),
  hk5: play('e a última', K, 170), hk6: anton('CÊ', K), hk7: anton('NÃO', K), hk8: anton('ASSISTE', K), hk9: anton('SOZINHO.', K),
  // variantes de gancho (entregas A/B/C)
  hb1: anton('O TERROR', K), hb2: anton('ASIÁTICO', R), hb3: play('que ninguém', K, 170), hb4: anton('TE MOSTROU', K),
  hc1: anton('CÊ', K), hc2: anton('TEM', K), hc3: anton('CORAGEM', R), hc4: play('de fazer essa', K, 170), hc5: anton('VIAGEM?', K),
  // parada 1 — Tailândia (cinza)
  c1: play('Tailândia', R, 260, 900), n1: play('1', K, 600, 900),
  k1a: play('o autor jura que aconteceu:', K, 150), k1: anton('SUSSURRO', K, 420), k1b: play('…e a irmã muda.', R, 150),
  t1: strip('Quando a Morte<br>Sussurra', 'ธี่หยด · Tee Yod · 2023', K, W, 'NotoThai'),
  // parada 2 — Indonésia / Fortuna Maldita (vermelho)
  c2: play('Indonésia', Y, 260, 900), n2: play('2', W, 600, 900),
  k2a: play('lá existe o pesugihan:', W, 150), k2: anton('PACTO', W, 460), k2b: play('pago com sangue', Y, 150),
  t2: strip('Fortuna<br>Maldita', 'Sebelum Iblis Menjemput · 2018', W, K),
  // parada 3 — Indonésia / Impetigore (preto)
  c3: play('Java, Indonésia', Y, 220, 900), n3: play('3', Y, 600, 900),
  k3a: play('uma herança, um teatro de', G, 150), k3: anton('SOMBRAS', Y, 430), k3b: play('e uma vila que quer ela morta', G, 150),
  t3: strip('Impetigore', 'Perempuan Tanah Jahanam · 2019', Y, K),
  nfK: logo('netflix', 'NETFLIX', 'ASSISTA NA', W, K, '#E50914'),
  atv: logo('appletv', 'APPLE TV', 'ALUGUE NA', W, K, K),
  // envio (voo)
  sd1: anton('MANDA', K, 300), sd2: play('pra quem acha que', K, 130), sd3: anton('TERROR BOM', K, 300), sd4: play('só vem de', K, 130), sd5: anton('HOLLYWOOD', W, 300),
  // fecho (preto)
  q1: anton('QUAL DESSES', G, 300), q2: anton('LUGARES', Y, 300), q3: play('cê não', G, 150), q4: anton('VISITARIA?', G, 300),
  f1: play('segue a', G, 150), f2: anton('TALKING HORROR', Y, 260),
  cv1: anton('TERROR', K, 420), cv2: anton('ASIÁTICO', R, 420), cv3: play('fora do radar', K, 200, 900),
  st1: stamp('TAILÂNDIA', '2023'), st2: stamp('INDONÉSIA', '2018', K), st3: stamp('INDONÉSIA', '2019', Y),
  star: star(), pin: pin(),
};
const NOBLUR = new Set(['star', 'pin', 'st1', 'st2', 'st3', 'n1', 'n2', 'n3']);
const html = `<html><head><style>
@font-face{font-family:Anton;src:url('${F('Anton-Regular.ttf')}')}
@font-face{font-family:Playfair;src:url('${F('PlayfairDisplay-Italic.ttf')}');font-style:italic;font-weight:400 900}
@font-face{font-family:Inter;src:url('${F('Inter.ttf')}');font-weight:100 900}
@font-face{font-family:NotoThai;src:url('${F('NotoSansThai.ttf')}');font-weight:100 900}
body{margin:0;background:transparent} .it{display:inline-block;margin:60px;padding:4px}
</style></head><body>${Object.entries(items).map(([k, v]) => `<div><div class="it" id="${k}">${v}</div></div>`).join('')}</body></html>`;
const out = path.join(ROOT, 'public/tex/txt'); fs.mkdirSync(out, {recursive: true});
const tmp = path.join(ROOT, 'out/_text.html'); fs.writeFileSync(tmp, html);
const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 3200, height: 2000}});
await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
const meta = {};
for (const k of Object.keys(items)) {
  const el = p.locator('#' + k);
  const bb = await el.boundingBox();
  await el.screenshot({path: path.join(out, k + '.png'), omitBackground: true});
  meta[k] = {w: Math.round(bb.width), h: Math.round(bb.height), blur: !NOBLUR.has(k)};
  if (!NOBLUR.has(k)) {
    await el.evaluate((e) => { e.style.filter = 'blur(12px)'; e.style.padding = '40px'; e.style.margin = '24px'; });
    const b2 = await el.boundingBox(); meta[k].bw = Math.round(b2.width); meta[k].bh = Math.round(b2.height);
    await el.screenshot({path: path.join(out, k + '_b.png'), omitBackground: true});
    await el.evaluate((e) => { e.style.filter = ''; e.style.padding = '4px'; e.style.margin = '60px'; });
  }
}
fs.writeFileSync(path.join(ROOT, 'src/texts.json'), JSON.stringify(meta, null, 1));
await b.close(); console.log(Object.keys(meta).length, 'textos');
