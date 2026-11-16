// Exporta para o mix de áudio: velocidade da câmera por quadro e eventos sonoros (carimbos, odômetro, scratch...).
import fs from 'node:fs';
import {STOPS, TOTAL} from '../../src/data/stops.mjs';
import {makeT, buildCamera, D, H0} from '../../src/lib/path.mjs';
const TL = JSON.parse(fs.readFileSync('src/timeline.json', 'utf8'));
const T = makeT(TL);
const R = (r) => (typeof r === 'string' && r.startsWith('end') ? TOTAL + parseFloat(r.slice(3) || '0') : T(r));
const starts = STOPS.map((s) => R(s.start)); const cam = buildCamera(starts, TOTAL);
const speed = []; for (let f = 0; f <= Math.round(TOTAL * 30); f++) speed.push(+cam(f / 30).speed.toFixed(3));
const ev = [];
STOPS.forEach((s, k) => {
  s.els.forEach((e) => {
    const t = R(e.at);
    if (e.type === 'stamp') ev.push({t: t + 0.13, n: e.kind === 'place' ? 'stamp' : 'stamp_big'});
    if (e.shake) ev.push({t, n: 'thump'});
    if (e.type === 'img') ev.push({t, n: 'flick'});
    if (e.type === 'molecule') for (let i = 0; i < 8; i++) ev.push({t: t + i * e.dur / 8, n: 'pen'});
  });
  if (s.cover) { // instante em que a câmera atravessa a folha/fumaça
    const zc = -k * D + 6.2 + 3.2; let tt = starts[k] - 2; while (tt < starts[k] + 1 && cam(tt).z > zc) tt += 1 / 120; ev.push({t: tt - 0.15, n: 'whoosh_big'});
  }
  const counts = s.counterAt ? s.counterAt.map(([r]) => R(r) - 0.25) : s.counter ? [starts[k] - 0.25] : [];
  counts.forEach((t0) => { for (let i = 0; i < 6; i++) ev.push({t: t0 + i * 0.075, n: 'tick'}); });
});
ev.push({t: T('s6b:4') - 0.05, n: 'scratch'});
ev.sort((a, b) => a.t - b.t);
fs.writeFileSync('build/h_eventos.json', JSON.stringify({total: TOTAL, speed, ev}, null, 0));
console.log('eventos', ev.length, 'vel max', Math.max(...speed).toFixed(1));
