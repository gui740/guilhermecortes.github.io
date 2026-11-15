import {SCALE, STOPS, Stop, DURATION} from './timeline';

type V3 = [number, number, number];
type Key = {t: number; p: V3; q: V3; fov: number};

const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const norm = (a: V3): V3 => { const l = Math.hypot(...a); return [a[0] / l, a[1] / l, a[2] / l]; };

/** local do diorama -> mundo */
export const toWorld = (s: Stop, l: V3): V3 => [s.anchor[0] + SCALE * l[0], SCALE * l[1], s.anchor[1] + SCALE * l[2]];
const orbit = (deg: number, d: number, h: number): V3 => { const a = (deg * Math.PI) / 180; return [d * Math.sin(a), h, d * Math.cos(a)]; };
export const LOCAL_TARGET: V3 = [0, 8.6, 0];

// visão geral de abertura e o gongo (objeto da abertura/fecho)
export const O: V3 = [5, 115, 85];
export const M0: V3 = [2, 0, -5];
const dO = norm(sub(M0, O));
const upO: V3 = [-0.03, 0.585, -0.81];
export const GONG: V3 = add(add(add(O, mul(dO, 22)), [4.5, 0, 0]), mul(upO, 6));
const nG = norm(sub(O, GONG));
export const C0: V3 = add(GONG, mul(nG, 1.55));
export const HOOK_POS: V3 = add(add(O, mul(dO, 62)), mul(upO, 5));
export const E: V3 = [4.5, 78, 70]; // visão das três paradas no fecho
export const E_TARGET: V3 = [1.5, 0, 5];
export const END_POS: V3 = add(E, mul(norm(sub(E_TARGET, E)), 44));

const stopKeys = (s: Stop): Key[] => {
  // deriva lenta -> arrancada que atravessa a camada de primeiro plano na revelação do título -> deriva lenta
  const q = toWorld(s, LOCAL_TARGET);
  const early = s.tt - s.ta < 1.2; // parada 3: o título vem logo na chegada
  if (early) return [
    {t: s.ta, p: toWorld(s, orbit(-6, 34.5, 9.3)), q, fov: 40},
    {t: s.ta + (s.td - s.ta) * 0.5, p: toWorld(s, orbit(-0.5, 29.2, 8.9)), q, fov: 40},
    {t: s.td, p: toWorld(s, orbit(5, 25.8, 8.6)), q, fov: 40},
  ];
  return [
    {t: s.ta, p: toWorld(s, orbit(-6, 35.5, 9.4)), q, fov: 40},
    {t: s.tt - 0.5, p: toWorld(s, orbit(-1.5, 31.4, 9.0)), q, fov: 40},
    {t: s.tt + 0.25, p: toWorld(s, orbit(1, 27.9, 8.8)), q, fov: 40},
    {t: s.td, p: toWorld(s, orbit(5, 25.8, 8.6)), q, fov: 40},
  ];
};

const [S1, S2, S3] = STOPS;
export const KEYS: Key[] = [
  {t: 0, p: C0, q: GONG, fov: 50},
  {t: 1.35, p: O, q: M0, fov: 50},
  {t: 3.95, p: add(O, mul(dO, 13)), q: [0.5, 0, -3], fov: 50},
  {t: 4.9, p: [-3.5, 27, 30], q: [-5, 3, 2], fov: 44},
  ...stopKeys(S1),
  {t: 14.4, p: [-3.2, 22, 25], q: [-3.4, 0, 7], fov: 44},
  {t: 16.1, p: [0.2, 25, 41], q: [1.2, 1, 21], fov: 44},
  ...stopKeys(S2),
  {t: 24.85, p: [5.4, 11, 42.5], q: [4.6, 3.4, 22.2], fov: 42},
  ...stopKeys(S3),
  {t: 33.1, p: E, q: E_TARGET, fov: 45},
  {t: 35.3, p: add(E, [0.6, 7, 3]), q: add(E_TARGET, [0.5, 0, 1]), fov: 46},
  {t: DURATION, p: C0, q: GONG, fov: 50},
];

// Hermite cúbica (Catmull-Rom não uniforme): velocidade contínua, sem trancos
const hermite = (ks: number[], ts: number[], t: number) => {
  const n = ts.length;
  let i = 0;
  while (i < n - 2 && t > ts[i + 1]) i++;
  const t0 = ts[i], t1 = ts[i + 1], h = t1 - t0, u = Math.max(0, Math.min(1, (t - t0) / h));
  const m = (j: number) => {
    if (j === 0 || j === n - 1) return 0;
    const a = (ks[j] - ks[j - 1]) / (ts[j] - ts[j - 1]), b = (ks[j + 1] - ks[j]) / (ts[j + 1] - ts[j]);
    if (a * b <= 0) return 0; // monotônica: evita overshoot
    return (2 * a * b) / (a + b);
  };
  const u2 = u * u, u3 = u2 * u;
  return (2 * u3 - 3 * u2 + 1) * ks[i] + (u3 - 2 * u2 + u) * h * m(i) + (-2 * u3 + 3 * u2) * ks[i + 1] + (u3 - u2) * h * m(i + 1);
};
const TS = KEYS.map((k) => k.t);
const comp = (f: (k: Key) => number) => KEYS.map(f);
const PX = comp((k) => k.p[0]), PY = comp((k) => k.p[1]), PZ = comp((k) => k.p[2]);
const QX = comp((k) => k.q[0]), QY = comp((k) => k.q[1]), QZ = comp((k) => k.q[2]);
const FV = comp((k) => k.fov);

export const cameraAt = (t: number) => {
  const p: V3 = [hermite(PX, TS, t), hermite(PY, TS, t), hermite(PZ, TS, t)];
  const q: V3 = [hermite(QX, TS, t), hermite(QY, TS, t), hermite(QZ, TS, t)];
  // respiração de câmera na mão: nunca fica 100% parada (some nas pontas p/ o loop fechar)
  const fade = Math.min(1, t / 1.0, (DURATION - t) / 1.0);
  const amp = 0.05 * fade * Math.min(3, 0.6 + p[1] / 30);
  p[0] += amp * Math.sin(t * 1.1 + 0.4); p[1] += amp * 0.7 * Math.sin(t * 0.83 + 2.0); p[2] += amp * Math.sin(t * 0.61 + 1.1);
  p[1] = Math.max(1.2, p[1]);
  return {p, q, fov: hermite(FV, TS, t)};
};
export const cameraSpeed = (t: number) => {
  const a = cameraAt(t - 1 / 60).p, b = cameraAt(t + 1 / 60).p;
  return Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) * 30;
};
/** z local da câmera no instante t (para posicionar a camada que ela atravessa) */
export const localCamZ = (s: Stop, t: number) => (cameraAt(t).p[2] - s.anchor[1]) / SCALE;
