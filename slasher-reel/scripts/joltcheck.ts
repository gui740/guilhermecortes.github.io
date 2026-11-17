import {camZ, STRONG, FPS} from '../src/timeline';
// avanço por frame; tranco = frame com avanço > 1,25x a mediana local
const N = Math.round(39.56 * FPS);
const adv: number[] = [];
for (let f = 1; f < N; f++) adv.push(camZ((f - 1) / FPS) - camZ(f / FPS));
const jolts: number[] = [];
for (let i = 3; i < adv.length - 3; i++) {
  const loc = [...adv.slice(i - 6, i - 1), ...adv.slice(i + 3, i + 8)].sort((a, b) => a - b);
  const med = loc[Math.floor(loc.length / 2)];
  if (adv[i] > med + 0.08 && adv[i] >= adv[i - 1] && adv[i] >= adv[i + 1]) jolts.push((i + 1) / FPS);
}
const offs = STRONG.map((b) => Math.min(...jolts.map((j) => Math.abs(j - b))));
console.log(JSON.stringify({beats: STRONG.length, jolts: jolts.length, maxOffsetMs: Math.round(Math.max(...offs) * 1000), meanOffsetMs: Math.round((offs.reduce((a, b) => a + b, 0) / offs.length) * 1000), within2frames: offs.filter((o) => o <= 2 / FPS + 1e-6).length}));
