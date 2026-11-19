// Plano-sequência: posição da câmera é função pura do tempo (determinística para render paralelo).
import type {TL} from '../content';

export const CAM_Y = 1.55;
export const VHS_START = 0.32; // distância do close inicial na fita (e do close final do loop)
export const PULLBACK_END = 2.4;
export const PULLBACK_Z = 3.2;
export const TRAV_DIST = 11.0;
export const TRAV_DUR = 1.5;
export const FOCAL = 5.6;
export const OUTRO_DIST = 7.0;
export const OUTRO_DUR = 1.3;

const ss = (a: number, b: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};
const easeOutCubic = (x: number) => 1 - Math.pow(1 - x, 3);
const easeInCubic = (x: number) => x * x * x;

export class CamPath {
  tl: TL; dt = 1 / 600; zs: number[] = []; lastT: number; zD = 0; vhs2Z = 0; keys: [number, number][];
  constructor(tl: TL, fps = 30) {
    this.tl = tl;
    this.lastT = (tl.durationInFrames - 1) / fps;
    const st = tl.stations;
    this.keys = [[PULLBACK_END, 0], [PULLBACK_END + 0.8, 0.3], [tl.hookEnd, 0.3]];
    for (const s of st) { this.keys.push([s.start + 0.2, 0.05]); this.keys.push([s.end, 0.05]); }
    this.keys.push([tl.outroStart + 1.2, 0.08]);
    // integra a velocidade
    let z = PULLBACK_Z; const n = Math.ceil((this.lastT + 1) / this.dt);
    for (let i = 0; i <= n; i++) {
      const t = PULLBACK_END + i * this.dt;
      this.zs.push(z);
      z -= this.speed(t) * this.dt;
    }
    this.zD = this.zAdv(tl.diveStart);
    this.vhs2Z = this.zD - PULLBACK_Z;
  }
  base(t: number) {
    const k = this.keys;
    if (t <= k[0][0]) return k[0][1];
    for (let i = 0; i < k.length - 1; i++) {
      if (t <= k[i + 1][0]) return k[i][1] + (k[i + 1][1] - k[i][1]) * ss(k[i][0], k[i + 1][0], t);
    }
    return k[k.length - 1][1];
  }
  bump(t: number) {
    let v = 0;
    for (const tr of this.tl.travs) {
      const u = (t - tr.start) / TRAV_DUR;
      if (u > 0 && u < 1) v += (TRAV_DIST / TRAV_DUR) * (1 - Math.cos(2 * Math.PI * u));
    }
    // fecho: a câmera avança e passa pelo último filme antes dos 3 títulos
    const uo = (t - (this.tl.outroStart - 0.05)) / OUTRO_DUR;
    if (uo > 0 && uo < 1) v += (OUTRO_DIST / OUTRO_DUR) * (1 - Math.cos(2 * Math.PI * uo));
    return v;
  }
  speed(t: number) { return this.base(t) + this.bump(t); }
  zAdv(t: number) {
    const i = (t - PULLBACK_END) / this.dt; const i0 = Math.max(0, Math.min(this.zs.length - 2, Math.floor(i))); const f = Math.min(1, Math.max(0, i - i0));
    return this.zs[i0] * (1 - f) + this.zs[i0 + 1] * f;
  }
  // z da câmera sem órbita
  z(t: number) {
    if (t <= PULLBACK_END) return VHS_START + (PULLBACK_Z - VHS_START) * easeOutCubic(Math.max(0, t) / PULLBACK_END);
    if (t >= this.tl.diveStart) {
      const u = Math.min(1, (t - this.tl.diveStart) / (this.lastT - this.tl.diveStart));
      return this.zD - (this.zD - (this.vhs2Z + VHS_START)) * easeInCubic(u);
    }
    return this.zAdv(t);
  }
  vel(t: number) { return (this.z(t - 0.01) - this.z(t + 0.01)) / 0.02; }
  // ângulo de órbita (rad) e janela da estação
  orbit(t: number) {
    let a = 0;
    for (const s of this.tl.stations) {
      const w = ss(s.start - 0.4, s.start + 1.2, t) * (1 - ss(s.end - 0.5, s.end + 0.3, t));
      a += w * ((-2.7 + 5.4 * ss(s.start, s.end, t)) * Math.PI) / 180;
    }
    return a;
  }
  pose(t: number) {
    const z = this.z(t); const a = this.orbit(t);
    const breathe = t > 0.2 && t < this.tl.diveStart ? 1 : 0;
    const x = Math.sin(a) * FOCAL;
    const dz = (1 - Math.cos(a)) * FOCAL;
    const y = CAM_Y + breathe * 0.018 * Math.sin(t * 1.15);
    const roll = breathe * 0.004 * Math.sin(t * 0.7 + 1.0);
    return {x, y, z: z + dz, lookX: 0, lookY: CAM_Y + breathe * 0.01 * Math.sin(t * 0.9), lookZ: z - FOCAL, roll};
  }
}
export {ss, easeOutCubic, easeInCubic};
