import timing from './timing.json';

export const FPS = 30;
export const NARR_OFFSET = 0.15; // narração começa 0,15s depois do frame 0
export const DURATION = 37.0;
export const TOTAL_FRAMES = Math.round(DURATION * FPS);

export const K = '#1C1C1C', R = '#F23B3B', Y = '#F2E63A', G = '#EDEDED', W = '#FFFFFF';

type Word = {w: string; s: number; e: number; seg: string};
export const WORDS = (timing.words as Word[]).map((w) => ({...w, s: w.s + NARR_OFFSET, e: w.e + NARR_OFFSET}));
/** tempo (s, na timeline do vídeo) da n-ésima palavra do segmento */
export const wt = (seg: string, i = 0) => WORDS.filter((w) => w.seg === seg)[i].s;

// projeção do mapa -> mundo
export const world = (lon: number, lat: number): [number, number] => [(lon - 105) * 0.97, -(lat - 15)];
export const SCALE = 0.5; // escala dos dioramas (unidades locais -> mundo)

export type Stop = {
  id: 'th' | 'fm' | 'imp'; anchor: [number, number]; ta: number; tt: number; td: number;
  bg: string; fg: string; accent: string; piece: 'Thailand' | 'Indonesia'; pieceColor: string;
};
export const STOPS: Stop[] = [
  {id: 'th', anchor: world(99.6, 14.2), ta: 5.6, tt: wt('th3', 0) - 0.05, td: 12.95, bg: G, fg: K, accent: R, piece: 'Thailand', pieceColor: R},
  {id: 'fm', anchor: world(107.0, -6.9), ta: 17.7, tt: wt('fm3', 0) - 0.05, td: 24.0, bg: R, fg: W, accent: Y, piece: 'Indonesia', pieceColor: Y},
  {id: 'imp', anchor: world(112.0, -7.6), ta: 25.7, tt: wt('im2', 0) + 0.05, td: 31.5, bg: K, fg: G, accent: Y, piece: 'Indonesia', pieceColor: Y},
];

export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
export const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2); // cúbico
export const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
export const backOut = (t: number) => { const c = 1.70158; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
export const prog = (t: number, a: number, b: number) => clamp01((t - a) / (b - a));

const hex = (h: string) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
export const mix = (a: string, b: string, t: number) => {
  const A = hex(a), B = hex(b);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join('');
};
/** cor de fundo dominante: troca em degradê DURANTE os voos */
export const bgAt = (t: number) => {
  if (t < 13.3) return G;
  if (t < 16.6) return mix(G, R, easeInOut(prog(t, 13.3, 16.6)));
  if (t < 24.1) return R;
  if (t < 25.6) return mix(R, K, easeInOut(prog(t, 24.1, 25.6)));
  return K;
};
