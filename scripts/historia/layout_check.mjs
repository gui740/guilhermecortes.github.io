// Verificador de layout: projeta cada elemento com a câmera real durante a janela em que deveria estar legível
// (do "at" até a câmera sair da estação ou o elemento sair) e aponta sobreposição, saída da área segura,
// cobertura por recortes e tempo de leitura curto.
import fs from 'node:fs';
import * as THREE from 'three';
import opentype from 'opentype.js';
import {STOPS, TOTAL} from '../../src/data/stops.mjs';
import {makeT, buildCamera, D, HM, TANH, ASPECT, FOV, TRAVEL_BEFORE} from '../../src/lib/path.mjs';
const TL = JSON.parse(fs.readFileSync('src/timeline.json', 'utf8')); const T = makeT(TL);
const R = (r) => (typeof r === 'string' && r.startsWith('end') ? TOTAL + parseFloat(r.slice(3) || '0') : T(r));
const starts = STOPS.map((s) => R(s.start)); const cam = buildCamera(starts, TOTAL);
const F = {anton: ['assets/historia/fonts/Anton-normal-400.ttf', 1], play: ['assets/historia/fonts/PlayfairDisplay-italic-900.ttf', 0.8], inter: ['assets/historia/fonts/Inter-normal-700.ttf', 1]};
const fonts = Object.fromEntries(Object.entries(F).map(([k, [p, sx]]) => [k, {f: opentype.parse(fs.readFileSync(p).buffer.slice(0)), sx}]));
const IMG = {}; for (const f of fs.readdirSync('assets/historia/tex')) if (f.endsWith('.png')) { const b = fs.readFileSync('assets/historia/tex/' + f); IMG[f.slice(0, -4)] = b.readUInt32BE(16) / b.readUInt32BE(20); }
function textBox(e) {  // largura/altura reais do texto em px de projeto (altura = cap/ascender útil)
  const {f, sx} = fonts[e.font]; const w = f.getAdvanceWidth(e.text, e.h) * sx; return {w, h: e.h * (e.font === 'inter' ? 0.78 : 0.86)};
}
const SAFE = {x0: 40, x1: 1080 - 140, y0: 250, y1: 1920 - 420};
const camera = new THREE.PerspectiveCamera(FOV, ASPECT, 0.05, 200);
function project(c, x, y, z) { const v = new THREE.Vector3(x, y, z).project(camera); return [(v.x + 1) / 2 * 1080, (1 - v.y) / 2 * 1920, v.z]; }
const issues = [];
STOPS.forEach((st, k) => {
  const depart = k < STOPS.length - 1 ? starts[k + 1] - TRAVEL_BEFORE + 0.25 : TOTAL - 0.7;   // início da travessia ainda é lento e legível
  const els = st.els.map((e, j) => {
    const dz = e.dz || 0, dd = HM - dz, hh = 2 * dd * TANH, ww = hh * ASPECT;
    let w, h;
    if (e.type === 'word') { const b = textBox(e); w = b.w; h = b.h; }
    else if (e.type === 'img') { h = e.h; w = e.h * (IMG[e.tex] || 1); }
    else if (e.type === 'stamp') { h = e.h * 1.9 / 1.6; w = (e.text.length * 0.48 + 1.1) * e.h * 0.85; }
    else return null;
    return {j, e, at: R(e.at), out: e.out != null ? R(e.out) : depart, X: (e.x / 1080 - .5) * ww, Y: (.5 - e.y / 1920) * hh, Z: -k * D + dz, W: w / 1920 * hh, H: h / 1920 * hh, rot: (e.rot || 0) * Math.PI / 180};
  }).filter(Boolean);
  for (let t = 0; t <= depart; t += 0.1) {
    if (t < starts[k] - 0.6) continue;
    const c = cam(t); camera.position.set(c.x, c.y, c.z); camera.lookAt(c.lx, c.ly, c.lz); camera.updateMatrixWorld(); camera.updateProjectionMatrix();
    const vis = els.filter((o) => t >= o.at + 0.15 && t <= Math.min(o.out, depart) && c.z - o.Z > 2.6).map((o) => {
      const pts = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([a, b]) => { const dx = a * o.W / 2, dy = b * o.H / 2; return project(c, o.X + dx * Math.cos(o.rot) - dy * Math.sin(o.rot), o.Y + dx * Math.sin(o.rot) + dy * Math.cos(o.rot), o.Z); });
      const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
      return {...o, b: [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)]};
    });
    const area = (b) => Math.max(0, b[2] - b[0]) * Math.max(0, b[3] - b[1]);
    const inter = (a, b) => area([Math.max(a[0], b[0]), Math.max(a[1], b[1]), Math.min(a[2], b[2]), Math.min(a[3], b[3])]);
    for (const o of vis) {
      if (o.e.type !== 'img' && (o.b[0] < SAFE.x0 - 4 || o.b[2] > SAFE.x1 + 4 || o.b[1] < SAFE.y0 - 4 || o.b[3] > SAFE.y1 + 30))
        issues.push({stop: st.id, t: +t.toFixed(1), kind: 'fora_da_margem', a: o.e.text || o.e.tex, box: o.b.map(Math.round)});
      for (const p of vis) {
        if (p === o || o.e.type === 'img') continue;
        const ov = inter(o.b, p.b) / area(o.b); if (ov <= 0) continue;
        const front = (p.e.dz || 0) > (o.e.dz || 0);
        if (p.e.type === 'img' && front) { if (ov > (o.e.dz < -0.5 ? 0.5 : 0.18)) issues.push({stop: st.id, t: +t.toFixed(1), kind: 'coberto_por_foto', a: o.e.text, b: p.e.tex, pct: Math.round(ov * 100)}); }
        else if (p.e.type !== 'img' && o.j < p.j && ov > 0.08) issues.push({stop: st.id, t: +t.toFixed(1), kind: 'sobreposicao', a: o.e.text, b: p.e.text, pct: Math.round(ov * 100)});
      }
    }
  }
  for (const o of els) { const vis = Math.min(o.out, depart) - o.at; if (o.e.type !== 'img' && vis < 0.7) issues.push({stop: st.id, kind: 'pouco_tempo', a: o.e.text, seg: +vis.toFixed(2)}); }
});
const key = (i) => [i.stop, i.kind, i.a, i.b].join('|'); const agg = {};
for (const i of issues) { const kk = key(i); if (!agg[kk]) agg[kk] = {...i, n: 0, tmin: i.t, tmax: i.t, pmax: i.pct || 0}; agg[kk].n++; agg[kk].tmax = i.t ?? agg[kk].tmax; agg[kk].pmax = Math.max(agg[kk].pmax, i.pct || 0); }
const out = Object.values(agg).filter((i) => i.kind === 'pouco_tempo' || i.n >= 3);
for (const i of out) console.log(i.stop.padEnd(11), i.kind.padEnd(17), JSON.stringify(i.a), i.b ? '× ' + JSON.stringify(i.b) : '', i.pmax ? i.pmax + '%' : '', i.seg != null ? i.seg + 's' : '', i.tmin != null ? `${i.tmin}–${i.tmax}s` : '', i.box ? JSON.stringify(i.box) : '');
console.log('total', out.length);
