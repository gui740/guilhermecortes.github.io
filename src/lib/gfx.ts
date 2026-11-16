// Texturas geradas em canvas: palavras, carimbos, estrela, molécula de THC.
import * as THREE from 'three';
export const FONTS: Record<string, {family: string; weight: string; style: string; scaleX: number; px: number}> = {
  anton: {family: 'Anton', weight: '400', style: 'normal', scaleX: 1, px: 220},
  play: {family: 'Playfair Display', weight: '900', style: 'italic', scaleX: 0.8, px: 200},
  inter: {family: 'Inter', weight: '700', style: 'normal', scaleX: 1, px: 160},
};
function tex(c: HTMLCanvasElement) {
  const t = new THREE.CanvasTexture(c);
  t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter;
  t.colorSpace = THREE.NoColorSpace; t.anisotropy = 4; t.needsUpdate = true; return t;
}
/** palavra branca em fundo transparente (cor aplicada no shader). Retorna textura + razão largura/altura + fator altura/px */
export function wordTexture(text: string, font: string) {
  const F = FONTS[font]; const c = document.createElement('canvas'); const ctx = c.getContext('2d')!;
  ctx.font = `${F.style} ${F.weight} ${F.px}px "${F.family}"`;
  const m = ctx.measureText(text); const pad = Math.round(F.px * 0.18);
  const w = Math.ceil(m.width * F.scaleX) + pad * 2, h = Math.ceil(F.px * 1.32) + pad * 2;
  c.width = w; c.height = h;
  ctx.font = `${F.style} ${F.weight} ${F.px}px "${F.family}"`; ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.textAlign = 'center';
  ctx.save(); ctx.translate(w / 2, h / 2 + F.px * 0.04); ctx.scale(F.scaleX, 1); ctx.fillText(text, 0, 0); ctx.restore();
  return {tex: tex(c), aspect: w / h, hPerPx: h / F.px};
}
function rough(ctx: CanvasRenderingContext2D, w: number, h: number, seed: number) {
  // apaga pontinhos aleatórios: textura de carimbo
  let s = seed; const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  ctx.globalCompositeOperation = 'destination-out';
  for (let i = 0; i < (w * h) / 260; i++) { const r = rnd() * 3.2 + 0.4; ctx.globalAlpha = 0.25 + rnd() * 0.7; ctx.beginPath(); ctx.arc(rnd() * w, rnd() * h, r, 0, 7); ctx.fill(); }
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
}
/** kind: place (tinta = cor do texto no shader), proibido (vermelho em etiqueta clara), liberado (amarelo em etiqueta preta) */
export function stampTexture(text: string, kind: string, seed = 7) {
  const c = document.createElement('canvas'); const ctx = c.getContext('2d')!; const px = 120;
  ctx.font = `400 ${px}px "Anton"`; const tw = ctx.measureText(text).width;
  const w = Math.ceil(tw + px * 1.1), h = Math.ceil(px * 1.9); c.width = w; c.height = h;
  const ink = kind === 'proibido' ? '#F23B3B' : kind === 'liberado' ? '#F2E63A' : '#ffffff';
  const r = 22, lw = 12, inset = 14;
  const rr = (x: number, y: number, ww: number, hh: number) => { ctx.beginPath(); ctx.roundRect(x, y, ww, hh, r); };
  if (kind !== 'place') { ctx.fillStyle = kind === 'proibido' ? '#EDEDED' : '#1C1C1C'; rr(4, 4, w - 8, h - 8); ctx.fill(); }
  ctx.strokeStyle = ink; ctx.lineWidth = lw; rr(inset, inset, w - inset * 2, h - inset * 2); ctx.stroke();
  ctx.lineWidth = 4; rr(inset + 18, inset + 18, w - (inset + 18) * 2, h - (inset + 18) * 2); ctx.stroke();
  ctx.fillStyle = ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = `400 ${px}px "Anton"`; ctx.fillText(text, w / 2, h / 2 + 6);
  rough(ctx, w, h, seed);
  return {tex: tex(c), aspect: w / h, colored: kind !== 'place'};
}
export function starTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 1024; const ctx = c.getContext('2d')!;
  ctx.translate(512, 512); ctx.fillStyle = '#F2E63A'; ctx.beginPath();
  const n = 18; for (let i = 0; i < n * 2; i++) { const a = (i * Math.PI) / n - Math.PI / 2; const R = i % 2 ? 330 + (i % 4) * 22 : 500; ctx.lineTo(Math.cos(a) * R, Math.sin(a) * R); }
  ctx.closePath(); ctx.fill(); rough(ctx as any, 1024, 1024, 3);
  return {tex: tex(c), aspect: 1, colored: true};
}
// ---- THC (esqueleto estilizado do Δ9-THC: anel A ciclo-hexeno, B pirano, C aromático, OH e cadeia pentila)
const S3 = Math.sqrt(3);
function hexV(cx: number, cy: number) { return [0, 1, 2, 3, 4, 5].map((k) => [cx + Math.cos(((30 + 60 * k) * Math.PI) / 180), cy - Math.sin(((30 + 60 * k) * Math.PI) / 180)]); }
export function thcStrokes() {
  const A = hexV(0, 0), B = hexV(S3, 0); const cC = [S3 + S3 * Math.cos(Math.PI / 3), -S3 * Math.sin(Math.PI / 3)]; const C = hexV(cC[0], cC[1]);
  const L: number[][][] = []; const seg = (p: number[], q: number[]) => L.push([p, q]);
  const ring = (V: number[][], skip: number[] = []) => { for (let k = 0; k < 6; k++) if (!skip.includes(k)) seg(V[k], V[(k + 1) % 6]); };
  ring(A); ring(B, [5, 2]); ring(C, [3]);
  const inner = (p: number[], q: number[], c: number[]) => { const f = 0.2; const pp = [p[0] + (c[0] - p[0]) * f, p[1] + (c[1] - p[1]) * f], qq = [q[0] + (c[0] - q[0]) * f, q[1] + (c[1] - q[1]) * f]; seg(pp, qq); };
  inner(C[0], C[1], cC); inner(C[2], C[3], cC); inner(C[4], C[5], cC); inner(A[1], A[2], [0, 0]);
  const out = (p: number[], ang: number, len = 1) => { const q = [p[0] + Math.cos(ang) * len, p[1] - Math.sin(ang) * len]; seg(p, q); return q; };
  out(A[2], (150 * Math.PI) / 180); // metila
  out(B[4], (-60 * Math.PI) / 180); out(B[4], (-120 * Math.PI) / 180); // gem-dimetil
  const oh = out(C[2], (150 * Math.PI) / 180, 0.9); // OH
  let p = C[5]; let ang = (-30 * Math.PI) / 180; // pentila em zigue-zague
  for (let i = 0; i < 5; i++) { p = out(p, ang); ang = ang === (-30 * Math.PI) / 180 ? (30 * Math.PI) / 180 : (-30 * Math.PI) / 180; }
  return {lines: L, labels: [{t: 'O', p: B[5]}, {t: 'OH', p: oh}]};
}
export function moleculeCanvas() {
  const c = document.createElement('canvas'); c.width = 1400; c.height = 1000; const ctx = c.getContext('2d')!;
  const t = tex(c); const {lines, labels} = thcStrokes();
  let minx = 1e9, maxx = -1e9, miny = 1e9, maxy = -1e9;
  lines.forEach((l) => l.forEach(([x, y]) => { minx = Math.min(minx, x); maxx = Math.max(maxx, x); miny = Math.min(miny, y); maxy = Math.max(maxy, y); }));
  const sc = Math.min(1250 / (maxx - minx), 850 / (maxy - miny)), ox = 700 - ((minx + maxx) / 2) * sc, oy = 500 - ((miny + maxy) / 2) * sc;
  const P = (q: number[]) => [ox + q[0] * sc, oy + q[1] * sc];
  function draw(prog: number) {
    ctx.clearRect(0, 0, 1400, 1000); ctx.strokeStyle = '#fff'; ctx.lineWidth = 15; ctx.lineCap = 'round';
    const n = lines.length, f = prog * n;
    for (let i = 0; i < n; i++) {
      const u = Math.max(0, Math.min(1, f - i)); if (u <= 0) break;
      const [a, b] = lines[i].map(P); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u); ctx.stroke();
    }
    if (prog > 0.85) { ctx.globalAlpha = (prog - 0.85) / 0.15; ctx.fillStyle = '#fff'; ctx.font = '400 92px "Anton"'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      labels.forEach((l) => { const [x, y] = P(l.p); ctx.clearRect(x - 46, y - 52, 92, 104); ctx.fillText(l.t, x, y); }); ctx.globalAlpha = 1; }
    t.needsUpdate = true;
  }
  draw(0); return {tex: t, aspect: 1.4, draw};
}
