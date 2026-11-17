// Linha do tempo única: caminho da câmera, estações, textos — tudo função determinística do tempo.
import wordsRaw from './words.json';
import beatsRaw from './beats.json';

export const FPS = 30;
export const VO = 0.4; // atraso da narração no vídeo (s)
export const TOTAL = 39.56;
export const DURATION_FRAMES = Math.round(TOTAL * FPS);
export const FOV = 50;
export const ASPECT = 1080 / 1920;
export const TAN = Math.tan(((FOV / 2) * Math.PI) / 180);

export type Word = {w: string; s: number; e: number; phrase: number};
export const WORDS: Word[] = (wordsRaw as Word[]).map((w) => ({...w, s: w.s + VO, e: w.e + VO}));
export const BEATS = beatsRaw as unknown as {
  strong: {t: number; s: number; beat: number}[];
  fills: [number, number][];
  breque: [number, number];
  bars: number[];
};
export const STRONG = BEATS.strong.map((b) => b.t);

// tempo (s) de uma palavra: frase + palavra (busca pelo texto, n-ésima ocorrência)
export const wt = (word: string, nth = 0): number => {
  const m = WORDS.filter((w) => w.w.toLowerCase().replace(/[^\p{L}\d]/gu, '') === word.toLowerCase());
  if (!m[nth]) throw new Error('palavra não encontrada: ' + word + ' #' + nth);
  return m[nth].s;
};
// encaixa no tranco mais próximo se estiver perto (palavras de impacto cravadas na batida)
export const snap = (t: number, win = 0.14) => {
  let best = t;
  let bd = win;
  for (const b of STRONG) {
    const d = Math.abs(b - t);
    if (d < bd) {
      bd = d;
      best = b;
    }
  }
  return best;
};

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const smooth = (a: number, b: number, x: number) => {
  const t = clamp((x - a) / (b - a));
  return t * t * (3 - 2 * t);
};
export const easeOutCubic = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
export const easeInOutCubic = (x: number) => {
  x = clamp(x);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// ---------------- perfil de velocidade (unidades/s), easing cúbico entre chaves
const SPEED: [number, number][] = [
  [0, 0], [1.0, 0], [1.6, 5.0], [3.9, 5.0],
  [6.2, 0.48], [12.6, 0.4], // estação 3 (desacelera sem parar)
  [13.0, 3.5], [13.7, 16], [14.45, 16], [15.3, 2.4], // virada 1: travessia
  [16.2, 0.48], [21.9, 0.42], // estação 2
  [22.6, 3.4], [23.05, 3.6], [23.7, 14], [24.5, 13], [25.05, 1.1], // envio + virada 2
  [25.72, 0.9], [25.85, 4.6], [26.6, 0.48], // breque seco e pancada
  [32.45, 0.4], // estação 1
  [33.0, 5.5], [33.7, 2.6], [36.8, 2.4], [38.1, 1.0], [38.4, 0.22], [39.6, 0.22], // fecho
];
const speedAt = (t: number) => {
  for (let i = 0; i < SPEED.length - 1; i++) {
    const [t0, v0] = SPEED[i];
    const [t1, v1] = SPEED[i + 1];
    if (t >= t0 && t <= t1) return lerp(v0, v1, easeInOutCubic((t - t0) / (t1 - t0)));
  }
  return SPEED[SPEED.length - 1][1];
};

// integra em alta resolução
const DT = 1 / 240;
const N = Math.ceil((TOTAL + 1) / DT);
const ZF = new Float32Array(N + 1); // avanço (positivo = andou pra frente)
const VF = new Float32Array(N + 1);
{
  let s = 0;
  for (let i = 0; i <= N; i++) {
    const t = i * DT;
    const v = speedAt(t);
    VF[i] = v;
    ZF[i] = s;
    s += v * DT;
  }
}
const sample = (arr: Float32Array, t: number) => {
  const x = clamp(t / DT, 0, N - 1);
  const i = Math.floor(x);
  return lerp(arr[i], arr[i + 1], x - i);
};

// trancos nas batidas fortes: +avanço em 2 frames, cumulativo (sempre pra frente)
const JOLT = 0.28;
export const joltAt = (t: number) => {
  let j = 0;
  for (const b of STRONG) j += JOLT * smooth(b - 1 / FPS, b + 1 / FPS, t);
  return j;
};
// impulso recente (0..1) p/ balanço das máscaras e chacoalhão
export const kickAt = (t: number) => {
  let k = 0;
  for (const b of STRONG) {
    const d = t - b;
    if (d >= 0 && d < 0.6) k = Math.max(k, Math.exp(-d * 7));
  }
  return k;
};

// recuo da abertura (câmera recua rápido revelando o corredor)
const RECOIL = 4.6;
const recoilAt = (t: number) => RECOIL * easeOutCubic((t - 0.3) / 0.9);

export const camZ = (t: number) => -sample(ZF, t) - joltAt(t) + recoilAt(t);
export const camSpeed = (t: number) => {
  const h = 1 / 120;
  return Math.abs(camZ(t + h) - camZ(t - h)) / (2 * h);
};

// ---------------- estações
export type Station = {
  id: 'f3' | 'f2' | 'f1';
  num: string;
  t0: number; // começo (palavra "Número")
  tTitle: number;
  tReveal: number; // assassino revelado
  tEnd: number; // começo da travessia
  killerZ: number;
  killerY: number;
  killerH: number;
  orbitDeg: number;
};
const st = (id: Station['id'], num: string, t0: number, tTitle: number, tReveal: number, tEnd: number, ahead: number, killerH: number, orbitDeg: number): Station => ({
  id, num, t0, tTitle, tReveal, tEnd,
  killerZ: camZ(tEnd) - ahead,
  killerY: -0.35,
  killerH,
  orbitDeg,
});
export const STATIONS: Station[] = [
  st('f3', '3', wt('número', 0), wt('palhaço'), wt('mascote'), 12.95, 4.3, 3.5, 12),
  st('f2', '2', wt('número', 1), wt('massacre'), wt('assassino'), 22.75, 4.3, 3.2, -12),
  st('f1', '1', wt('número', 2), wt('presos'), wt('cara', 1), 32.95, 4.3, 2.5, 12),
];

// peso da estação (0..1) com bordas suaves
export const stationWeight = (s: Station, t: number) => smooth(s.t0 - 0.6, s.t0 + 1.4, t) * (1 - smooth(s.tEnd - 0.2, s.tEnd + 0.7, t));

// ---------------- câmera completa (posição, alvo, fov)
const noise1 = (t: number, seed: number) =>
  Math.sin(t * 1.3 + seed) * 0.5 + Math.sin(t * 2.7 + seed * 2.1) * 0.3 + Math.sin(t * 5.1 + seed * 3.7) * 0.2;

export type Cam = {x: number; y: number; z: number; tx: number; ty: number; tz: number; roll: number; fov: number; speed: number};
export const camAt = (t: number): Cam => {
  const z = camZ(t);
  let x = noise1(t, 1) * 0.05;
  let y = noise1(t, 2) * 0.04;
  let tx = x;
  let ty = y;
  let tz = z - 10;
  let fov = FOV;
  for (const s of STATIONS) {
    const w = stationWeight(s, t);
    if (w <= 0) continue;
    const d = Math.max(0.5, z - s.killerZ);
    // órbita de ~10° em volta do assassino
    const prog = smooth(s.t0, s.tEnd, t);
    const th = ((lerp(-0.5, 0.5, prog) * s.orbitDeg) * Math.PI) / 180;
    const ox = Math.sin(th) * d;
    x = lerp(x, ox, w);
    tx = lerp(tx, 0, w);
    ty = lerp(ty, s.killerY + 0.25, w);
    tz = lerp(tz, s.killerZ, w);
    fov = lerp(fov, FOV - 6 * prog, w); // push-in
  }
  // chacoalhão nas batidas
  const k = kickAt(t);
  y += k * 0.03 * Math.sin(t * 80);
  const roll = noise1(t, 7) * 0.012 + k * 0.01 * Math.sin(t * 60);
  return {x, y, z, tx, ty, tz, roll, fov, speed: camSpeed(t)};
};

// direção da lanterna: varredura irregular
export const beamAt = (t: number) => {
  const a = Math.sin(t * 0.9) * 0.55 + Math.sin(t * 2.3 + 1.2) * 0.25 + Math.sin(t * 5.7) * 0.06;
  const b = Math.sin(t * 0.7 + 2.0) * 0.32 + Math.sin(t * 1.9) * 0.16 + Math.sin(t * 6.3 + 0.5) * 0.04;
  // nas estações, a lanterna procura o assassino
  let fx = a * 0.5;
  let fy = b * 0.45 + 0.02;
  for (const s of STATIONS) {
    const w = smooth(s.tReveal - 0.5, s.tReveal + 0.2, t) * (1 - smooth(s.tEnd - 0.3, s.tEnd + 0.3, t));
    fx = lerp(fx, a * 0.12, w);
    fy = lerp(fy, 0.0 + b * 0.08, w);
  }
  return {x: fx, y: fy, z: -1};
};
// lanterna liga/desliga (abertura e fecho em loop)
export const beamOnAt = (t: number) => {
  const on1 = t < 0.13 ? 0 : t < 0.2 ? (Math.floor(t * 60) % 2 ? 1 : 0.2) : 1;
  const offT = 38.16;
  const reT = 38.5;
  if (t >= offT && t < reT) return 0;
  if (t >= reT) return t < reT + 0.07 ? (Math.floor(t * 60) % 2 ? 1 : 0.25) : 1;
  return on1;
};

// névoa vermelha nas revelações (degradê)
export const redAt = (t: number) => {
  let r = 0;
  for (const s of STATIONS) r = Math.max(r, smooth(s.tReveal - 0.35, s.tReveal + 0.25, t) * (1 - smooth(s.tReveal + 1.6, s.tReveal + 3.6, t)));
  r = Math.max(r, 0.65 * smooth(wt('não') - 0.2, wt('não') + 0.2, t) * (1 - smooth(wt('não') + 0.8, wt('não') + 1.8, t)));
  return r;
};

// foco (profundidade de campo)
export const focusAt = (t: number) => {
  let f = 6;
  const z = camZ(t);
  for (const s of STATIONS) {
    const w = stationWeight(s, t);
    f = lerp(f, Math.max(1.5, z - s.killerZ), w);
  }
  return f;
};

export const SAFE = {top: 250, bottom: 420, right: 140, left: 60};
STATIONS[2].killerY = -0.6; // Homem da Montanha (cintura pra cima) um pouco mais baixo
