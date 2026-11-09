import {Easing, interpolate, random} from 'remotion';

export const EASE = Easing.bezier(0.33, 0, 0.2, 1);
export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));

/** progresso 0..1 entre dois frames, com easing suave */
export const prog = (f: number, a: number, b: number, ease = EASE) =>
  interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});

/** número pseudo-aleatório determinístico em [a,b] */
export const rnd = (seed: string, a = 0, b = 1) => a + (b - a) * random(seed);

export type Pt = {x: number; y: number};

/** caminho "à mão": amostra uma curva quadrática e adiciona tremor perpendicular */
export const caminhoMao = (p1: Pt, p2: Pt, curva: number, seed: string, tremor = 2.6, n = 26) => {
  const mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2;
  const dx = p2.x - p1.x, dy = p2.y - p1.y;
  const len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len, ny = dx / len;
  const c = {x: mx + nx * curva, y: my + ny * curva};
  const pts: Pt[] = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const x = (1 - t) ** 2 * p1.x + 2 * (1 - t) * t * c.x + t * t * p2.x;
    const y = (1 - t) ** 2 * p1.y + 2 * (1 - t) * t * c.y + t * t * p2.y;
    const j = i === 0 || i === n ? 0 : (random(`${seed}-${i}`) - 0.5) * 2 * tremor;
    pts.push({x: x + nx * j, y: y + ny * j});
  }
  return {pts, d: suave(pts), c};
};

/** polyline -> path suave (catmull-rom) */
export const suave = (pts: Pt[]) => {
  if (pts.length < 2) return '';
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
    const c1 = {x: p1.x + (p2.x - p0.x) / 6, y: p1.y + (p2.y - p0.y) / 6};
    const c2 = {x: p2.x - (p3.x - p1.x) / 6, y: p2.y - (p3.y - p1.y) / 6};
    d += ` C ${c1.x.toFixed(1)} ${c1.y.toFixed(1)} ${c2.x.toFixed(1)} ${c2.y.toFixed(1)} ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`;
  }
  return d;
};

/** polígono de borda rasgada (em %) para clip-path */
export const bordaRasgada = (seed: string, amp = 1.6, passos = 22) => {
  const pts: string[] = [];
  const j = (k: string) => (random(`${seed}${k}`) * amp).toFixed(2);
  for (let i = 0; i <= passos; i++) pts.push(`${((i / passos) * 100).toFixed(2)}% ${j('t' + i)}%`);
  for (let i = 0; i <= passos; i++) pts.push(`${(100 - +j('r' + i)).toFixed(2)}% ${((i / passos) * 100).toFixed(2)}%`);
  for (let i = passos; i >= 0; i--) pts.push(`${((i / passos) * 100).toFixed(2)}% ${(100 - +j('b' + i)).toFixed(2)}%`);
  for (let i = passos; i >= 0; i--) pts.push(`${j('l' + i)}% ${((i / passos) * 100).toFixed(2)}%`);
  return `polygon(${pts.join(',')})`;
};
