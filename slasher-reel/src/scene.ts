// Descrição estática do mundo: corredor infinito (anel reciclável) + estações + textos.
import manifest from './manifest.json';
import txt from './txt.json';
import {ASPECT, STATIONS, Station, WORDS, camAt, camZ, snap, wt, smooth} from './timeline';

type Size = {w: number; h: number};
const KIT = (manifest as {kit: Record<string, Size & {yellow: boolean}>}).kit;
const FILM = (manifest as {film: Record<string, Size>}).film;
const LOGO = (manifest as {logos: Record<string, Size>}).logos;
const TXT = txt as Record<string, Size>;

export type Kind = 'obj' | 'text' | 'smoke' | 'tape' | 'killer' | 'line' | 'star' | 'tag' | 'logo' | 'door' | 'dash' | 'floor';
export type El = {
  key: string;
  tex: string | null;
  w: number;
  h: number;
  x: number;
  y: number;
  z: number;
  rotZ?: number;
  rotY?: number;
  rotX?: number;
  kind: Kind;
  ring?: number; // offset no anel reciclável
  t0?: number; // entrada (texto/pop)
  impact?: boolean;
  emissive?: number;
  shadow?: boolean;
  wave?: number;
  hang?: {top: number; phase: number; amp: number};
  drift?: number;
  opacity?: number;
  station?: Station;
  door?: {side: -1 | 1; hingeX: number};
  rip?: {side: -1 | 1};
  fogMul?: number;
  tint?: string;
  uv?: [number, number, number, number]; // offsetX, offsetY, repeatX, repeatY
  until?: number; // sai (câmera passa) depois deste tempo (s)
  noAnim?: boolean;
  from?: number; // invisível antes deste tempo
  group?: string; // blocos que respeitam a margem juntos
  variant?: 'A' | 'B' | 'C'; // versões do gancho
};

export const RING = 46;
const rng = (() => {
  let s = 1234567;
  return () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296;
  };
})();
const R = (a: number, b: number) => a + (b - a) * rng();
const pick = <T,>(a: T[]) => a[Math.floor(rng() * a.length) % a.length];

const kit = (k: string) => `kit/${k}.png`;
const sizeKit = (k: string, h: number) => ({w: (KIT[k].w / KIT[k].h) * h, h});

export const ELS: El[] = [];
let uid = 0;
const add = (e: Omit<El, 'key'> & {key?: string}) => {
  const el = {key: e.key ?? `e${uid++}`, ...e} as El;
  ELS.push(el);
  return el;
};

// ---------------------------------------------------------------- corredor (anel)
const MASKS = ['k_carnival_4', 'k_carnival_5', 'k_porcelai_2', 'k_porcelai_3', 'k_porcelai_4', 'r2_plaster_2', 'r2_plaster_4', 'r2_hanging_3', 'r2_hanging_4', 'r2_hanging_5', 'k_gas_1'];
const WALL = ['k_knife_2', 'k_knife_5', 'k_hammer_1', 'k_saw_1', 'k_scissors_0', 'r2_kitchen_1', 'r2_kitchen_3', 'r2_screwdri_4', 'k_chain_1', 'k_chain_2', 'r2_padlock_3', 'r2_kerosene_0', 'r2_polaroid_0', 'r2_cassette_0', 'r2_cassette_4', 'k_VHS_2'];
const FLOOR = ['k_VHS_3', 'k_typewrit_2', 'r2_teddy_0', 'k_doll_4', 'k_VHS_2', 'r2_kerosene_0'];

for (let i = 0; i < 20; i++) {
  const side = i % 2 ? 1 : -1;
  const k = pick(WALL);
  const h = R(0.55, 1.1);
  add({kind: 'obj', tex: kit(k), ...sizeKit(k, h), x: side * R(1.75, 2.7), y: R(-1.6, 1.7), z: 0, ring: (i / 20) * RING + R(-0.8, 0.8), rotZ: R(-0.45, 0.45), shadow: true});
}
for (let i = 0; i < 9; i++) {
  const k = MASKS[i % MASKS.length];
  const h = R(0.55, 0.85);
  const x = (i % 2 ? 1 : -1) * R(0.6, 1.9);
  const y = R(1.25, 2.0);
  add({kind: 'obj', tex: kit(k), ...sizeKit(k, h), x, y, z: 0, ring: (i / 9) * RING + R(0, 3), hang: {top: 4.2, phase: R(0, 6.28), amp: R(0.08, 0.16)}, shadow: true});
}
for (let i = 0; i < 6; i++) {
  const k = FLOOR[i % FLOOR.length];
  const h = R(0.5, 0.8);
  add({kind: 'obj', tex: kit(k), ...sizeKit(k, h), x: (i % 2 ? 1 : -1) * R(0.9, 2.2), y: -2.15 + h / 2, z: 0, ring: (i / 6) * RING + R(1, 4), rotZ: R(-0.1, 0.1), shadow: true});
}
// fitas zebradas em X
for (let i = 0; i < 4; i++) {
  const yc = R(-0.6, 1.3);
  const b = (i / 4) * RING + 5;
  const a = R(0.28, 0.42);
  add({kind: 'tape', tex: 'txt/tape.png', w: 7.5, h: 0.26, x: R(-0.4, 0.4), y: yc, z: 0, ring: b, rotZ: a, wave: 0.03, emissive: 0.15});
  add({kind: 'tape', tex: 'txt/tape.png', w: 7.5, h: 0.26, x: R(-0.4, 0.4), y: yc + R(-0.3, 0.3), z: 0, ring: b + 0.25, rotZ: -a, wave: 0.03, emissive: 0.15, uv: [0.37, 0, 1, 1]});
}
// cartazes de desaparecido e portas nas paredes
for (let i = 0; i < 3; i++) {
  add({kind: 'obj', tex: `txt/missing_${i % 2 ? 'a' : 'b'}.png`, w: 0.75, h: 1.02, x: (i % 2 ? -1 : 1) * R(2.0, 2.6), y: R(-0.4, 1.2), z: 0, ring: (i / 3) * RING + 9, rotZ: R(-0.12, 0.12), shadow: true});
}
for (let i = 0; i < 2; i++) {
  const s = sizeKit('r2_wooden_2', 3.0);
  add({kind: 'obj', tex: kit('r2_wooden_2'), ...s, x: (i ? 1 : -1) * 2.9, y: -0.7, z: 0, ring: i * 23 + 14, rotY: (i ? -1 : 1) * 1.1, shadow: false});
}
// varais com polaroids genéricas
for (let i = 0; i < 2; i++) {
  const b = i * 23 + 2;
  const y = R(2.0, 2.4);
  add({kind: 'line', tex: null, w: 5.2, h: 0.018, x: 0, y: y + 0.42, z: 0, ring: b});
  for (let j = 0; j < 4; j++) {
    const k = j % 2 ? 'txt/missing_a.png' : kit('r2_polaroid_0');
    const isPoster = k.startsWith('txt');
    add({kind: 'obj', tex: k, w: isPoster ? 0.55 : 0.6, h: isPoster ? 0.75 : 0.45, x: -1.9 + j * 1.25 + R(-0.2, 0.2), y, z: 0, ring: b + 0.02, rotZ: R(-0.2, 0.2), hang: {top: y + 0.42, phase: R(0, 6), amp: 0.06}, shadow: true});
  }
}
// pegadas no chão
for (let i = 0; i < 2; i++) {
  add({kind: 'floor', tex: 'txt/footprints.png', w: 1.0, h: 2.6, x: R(-0.6, 0.6), y: -2.14, z: 0, ring: i * 23 + 7, rotX: -Math.PI / 2, rotZ: R(-0.3, 0.3)});
}
// fumaça atravessando entre as camadas
for (let i = 0; i < 8; i++) {
  const s = R(4.5, 7.5);
  add({kind: 'smoke', tex: `txt/smoke_${i % 2 ? 'a' : 'b'}.png`, w: s, h: s * 0.75, x: R(-2.2, 2.2), y: R(-1.6, 1.4), z: 0, ring: (i / 8) * RING + R(0, 4), drift: R(-0.35, 0.35), opacity: R(0.12, 0.22), emissive: 0.05});
}

// ---------------------------------------------------------------- posicionamento relativo à câmera
// sx, sy em NDC (-1..1) no instante t, a uma profundidade D (ou relativa ao assassino).
export const place = (t: number, sx: number, sy: number, D: number, widthFrac: number, aspectWH: number) => {
  const c = camAt(t);
  const tanH = Math.tan(((c.fov / 2) * Math.PI) / 180);
  // base da câmera
  const fx = c.tx - c.x, fy = c.ty - c.y, fz = c.tz - c.z;
  const fl = Math.hypot(fx, fy, fz);
  const f = [fx / fl, fy / fl, fz / fl];
  let r = [f[1] * 0 - f[2] * 1, f[2] * 0 - f[0] * 0, f[0] * 1 - f[1] * 0]; // f x up(0,1,0)
  r = [-f[2], 0, f[0]];
  const rl = Math.hypot(r[0], r[1], r[2]);
  r = [r[0] / rl, r[1] / rl, r[2] / rl];
  const u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]];
  const hx = sx * D * tanH * ASPECT;
  const hy = sy * D * tanH;
  const x = c.x + f[0] * D + r[0] * hx + u[0] * hy;
  const y = c.y + f[1] * D + r[1] * hx + u[1] * hy;
  const z = c.z + f[2] * D + r[2] * hx + u[2] * hy;
  const w = widthFrac * 2 * D * tanH * ASPECT;
  return {x, y, z, w, h: w / aspectWH, rotY: Math.atan2(c.x - x, c.z - z) * 0.6};
};
const depthAt = (t: number, z: number) => camZ(t) - z;

type TSpec = {variant?: 'A' | 'B' | 'C'; group?: string; from?: number; noAnim?: boolean; id: string; t: number; sx: number; sy: number; D?: number; dzk?: number; st?: Station; w: number; impact?: boolean; until?: number; tex?: string; size?: Size; emissive?: number};
export const TEXTS: Record<string, El> = {};
const T = (s: TSpec) => {
  const sz = s.size ?? TXT[s.id];
  const t0 = s.impact ? snap(s.t) : s.t;
  let D = s.D ?? 6;
  if (s.dzk !== undefined && s.st) D = depthAt(t0, s.st.killerZ + s.dzk);
  // largura pedida vale ~0,8s depois da entrada (compensa a aproximação da câmera)
  const zEst = camZ(t0) - D;
  const D1 = camZ(t0 + 0.8) - zEst;
  const comp = Math.min(1, Math.max(0.6, D1 / D));
  const p = place(t0, s.sx * (0.85 + 0.15 * comp), s.sy * (0.85 + 0.15 * comp), D, s.w * comp, sz.w / sz.h);
  let until = s.until;
  if (until === undefined) {
    const w = WORDS.find((x) => Math.abs(x.s - s.t) < 0.02);
    const ph = w ? WORDS.filter((x) => x.phrase === w.phrase) : [];
    const nextStart = ph.length ? WORDS.find((x) => x.phrase === ph[0].phrase + 1)?.s ?? 99 : 99;
    until = ph.length ? Math.max(t0 + 0.6, Math.min(ph[ph.length - 1].e + 0.4, nextStart - 0.12)) : t0 + 1.6;
  }
  const el = add({key: s.id + '_' + Math.round(t0 * 100), kind: 'text', noAnim: s.noAnim, from: s.from, group: s.group, variant: s.variant, tex: s.tex ?? `txt/${s.id}.png`, w: p.w, h: p.h, x: p.x, y: p.y, z: p.z, rotY: p.rotY, t0, impact: s.impact, emissive: s.emissive ?? 0.93, shadow: true, fogMul: 0.35, until});
  TEXTS[s.id] = el;
  return el;
};

// ---------------------------------------------------------------- abertura (máscara colada na câmera) e fecho
const MASK0 = 'r2_plaster_3';
const openMask = (t: number, key: string, from?: number) => {
  const sz = sizeKit(MASK0, 1);
  const p = place(t, 0.0, 0.18, 1.55, 0.95, sz.w / sz.h);
  add({key, kind: 'obj', tex: kit(MASK0), w: p.w, h: p.h, x: p.x, y: p.y, z: p.z, hang: {top: p.y + 3, phase: 0.4, amp: 0.02}, shadow: true, emissive: 0.05, from});
};
openMask(0, 'mask_open');
openMask(38.5, 'mask_end', 38.16);
T({variant: 'A', id: 'h_tres', t: 0, sx: 0, sy: -0.36, D: 1.3, w: 0.62, until: 3.0});
T({from: 38.16, id: 'h_tres', t: 38.5, sx: 0, sy: -0.36, D: 1.3, w: 0.62, tex: 'txt/h_tres.png', noAnim: true, until: 99});
// gancho
T({variant: 'A', id: 'h_assassinos', t: wt('assassinos', 0), sx: 0, sy: -0.06, D: 4.4, w: 0.86});
T({variant: 'A', id: 'h_mascarados', t: wt('mascarados'), sx: 0, sy: -0.2, D: 5.2, w: 0.86});
T({variant: 'A', id: 'h_quece', t: wt('que', 0), sx: -0.42, sy: 0.12, D: 6, w: 0.22});
T({variant: 'A', id: 'h_nunca', t: wt('nunca'), sx: 0.0, sy: 0.0, D: 6.5, w: 0.6, impact: true});
T({variant: 'A', group: 'hook2', id: 'h_eoultimo', t: wt('último'), sx: -0.05, sy: 0.14, D: 7.5, w: 0.46});
T({variant: 'A', group: 'hook2', id: 'h_filho', t: wt('filho'), sx: 0, sy: 0.02, D: 8, w: 0.72, impact: true, until: 4.85});

// ganchos alternativos B e C (mesma abertura, outro texto/voz)
import hookWords from './hook_words.json';
const HW = hookWords as Record<'B' | 'C', {w: string; s: number}[]>;
const hw = (v: 'B' | 'C', i: number) => HW[v][i].s + 0.4;
T({variant: 'B', id: 'hb_slasher', t: 0, sx: 0, sy: -0.36, D: 1.3, w: 0.66, until: 2.2});
T({variant: 'B', group: 'hb', id: 'hb_ceacha', t: hw('B', 0), sx: -0.2, sy: 0.12, D: 4.6, w: 0.34});
T({variant: 'B', group: 'hb', id: 'hb_javiu', t: hw('B', 3), sx: 0, sy: -0.02, D: 4.8, w: 0.8, impact: true});
T({variant: 'B', id: 'hb_duvido', t: hw('B', 7), sx: 0, sy: 0.0, D: 6.5, w: 0.7, impact: true, until: 99});
T({variant: 'C', id: 'hc_cansou', t: 0, sx: 0, sy: -0.36, D: 1.3, w: 0.66, until: 1.9});
T({variant: 'C', group: 'hc', id: 'hc_de', t: hw('C', 1), sx: -0.3, sy: 0.14, D: 4.5, w: 0.08});
T({variant: 'C', group: 'hc', id: 'hc_halloween', t: hw('C', 2), sx: 0, sy: 0.02, D: 4.7, w: 0.8, impact: true});
T({variant: 'C', group: 'hc', id: 'hc_panico', t: hw('C', 4), sx: 0, sy: -0.14, D: 4.7, w: 0.72, impact: true});
T({variant: 'C', id: 'hc_olha', t: hw('C', 5), sx: 0, sy: 0.0, D: 6.5, w: 0.82, until: 99});

// ---------------------------------------------------------------- estações
const [S3, S2, S1] = STATIONS;
type StationCfg = {s: Station; killer: string; tag: string; tTag: number; logo: string; tLogo: number; tTana: number; tanaId: string; placardSide: number};
const stationEls = (c: StationCfg) => {
  const s = c.s;
  const kk = FILM[`${s.id}_killer`];
  const kh = s.killerH;
  const kw = (kk.w / kk.h) * kh;
  const killer = add({key: `${s.id}_killer`, kind: 'killer', tex: `film/${s.id}_killer.png`, w: kw, h: kh, x: 0, y: s.killerY, z: s.killerZ, station: s, shadow: true, emissive: 0.22});
  add({key: `${s.id}_star`, kind: 'star', tex: 'txt/star.png', w: 3.6, h: 3.6, x: 0.1, y: s.killerY + 0.45, z: s.killerZ - 0.45, t0: s.tTitle, emissive: 0.75, fogMul: 0.5});
  const tg = TXT[c.tag];
  add({key: `${s.id}_tag`, kind: 'tag', tex: `txt/${c.tag}.png`, w: 1.15, h: (1.15 * tg.h) / tg.w, x: kw * 0.42 + 0.35, y: s.killerY + 0.15, z: s.killerZ + 0.25, t0: c.tTag, shadow: true, emissive: 0.6, hang: {top: s.killerY + 0.95, phase: 1, amp: 0.05}, fogMul: 0.4});
  add({key: `${s.id}_tagstring`, kind: 'line', tex: null, w: 0.7, h: 0.012, x: kw * 0.3 + 0.1, y: s.killerY + 0.55, z: s.killerZ + 0.2, rotZ: -0.5, t0: c.tTag});
  // polaroids da estação (stills), em profundidades diferentes
  const pos: [number, number, number, number][] = [
    [-1.35, 1.05, 1.5, 1.25], [1.5, 1.15, 0.9, 1.0], [-1.65, -0.55, 0.3, 1.0], [1.55, -0.75, -0.3, 0.95], [-1.15, 1.85, -1.1, 0.9], [1.25, 2.0, -1.6, 0.9],
  ];
  pos.forEach(([x, y, dz, h], i) => {
    const P = FILM[`${s.id}_pol${i}`];
    add({key: `${s.id}_pol${i}`, kind: 'obj', tex: `film/${s.id}_pol${i}.png`, w: (P.w / P.h) * h, h, x, y, z: s.killerZ + dz, rotZ: (i % 2 ? 1 : -1) * (0.08 + 0.05 * i), shadow: true, emissive: 0.18, hang: {top: y + 1.4, phase: i, amp: 0.03}});
  });
  // varal ligando as polaroids de cima
  add({key: `${s.id}_varal`, kind: 'line', tex: null, w: 3.4, h: 0.016, x: 0.05, y: 1.75, z: s.killerZ + 1.2, rotZ: 0.06});
  // número (placa de evidência)
  const pl = TXT[`placard_${s.num}`];
  T({id: `placard_${s.num}`, t: s.t0, sx: c.placardSide * 0.5, sy: -0.2, D: 9, w: 0.34, impact: true, size: pl, emissive: 0.85, until: s.tTitle + 0.9});
  // logo do streaming + "tá na"
  const L = LOGO[c.logo];
  T({group: 'logo' + s.id, id: c.tanaId, t: c.tTana, sx: -0.36, sy: -0.13, dzk: 1.6, st: s, w: 0.17, until: s.tEnd - 0.1});
  T({group: 'logo' + s.id, until: s.tEnd, id: `logo_${c.logo}`, t: c.tLogo, sx: 0.06, sy: -0.28, dzk: 1.6, st: s, w: c.logo === 'hbomax' ? 0.38 : 0.56, impact: true, tex: `logos/${c.logo}.png`, size: L, emissive: 1});
  return killer;
};

stationEls({s: S3, killer: 'f3', tag: 'tag_3', tTag: S3.tTitle, logo: 'hbomax', tLogo: wt('hbo'), tTana: wt('tá', 0), tanaId: 'tana', placardSide: -1});
T({group: 't3', id: 'f3_title_a', t: wt('palhaço'), sx: -0.02, sy: 0.44, dzk: 0.5, st: S3, w: 0.6, until: S3.tEnd + 0.4});
T({group: 't3', id: 'f3_title_b', t: wt('milharal'), sx: 0.06, sy: 0.3, dzk: 0.5, st: S3, w: 0.5, until: S3.tEnd + 0.4});
T({group: 'k3', id: 'f3_virou', t: wt('virou'), sx: -0.4, sy: 0.33, dzk: -0.75, st: S3, w: 0.16});
T({group: 'k3', id: 'f3_cacador', t: wt('caçador'), sx: 0, sy: 0.2, dzk: -0.75, st: S3, w: 0.82, impact: true});
T({group: 'k3', id: 'f3_deadol', t: wt('adolescente'), sx: 0.3, sy: 0.05, dzk: -0.75, st: S3, w: 0.34});
T({group: 'm3', id: 'f3_custou', t: wt('custou'), sx: -0.3, sy: 0.24, dzk: 1.0, st: S3, w: 0.24});
T({group: 'm3', id: 'f3_milhao', t: wt('milhão'), sx: 0.0, sy: 0.1, dzk: 1.0, st: S3, w: 0.66, impact: true});
T({group: 'm3', id: 'f3_dolares', t: wt('dólares'), sx: 0.3, sy: -0.03, dzk: 1.0, st: S3, w: 0.28});
// ponte
T({group: 'bridge', id: 'b_insano', t: wt('esse'), sx: 0, sy: 0.1, D: 8.5, w: 0.86});
T({group: 'bridge', id: 'b_proximo', t: wt('próximo'), sx: 0.05, sy: -0.06, D: 7, w: 0.52});

stationEls({s: S2, killer: 'f2', tag: 'tag_2', tTag: S2.tTitle, logo: 'looke', tLogo: wt('looke'), tTana: wt('tá', 1), tanaId: 'tana', placardSide: 1});
T({group: 't2', id: 'f2_title_a', t: wt('massacre'), sx: -0.04, sy: 0.44, dzk: 0.5, st: S2, w: 0.56, until: S2.tEnd + 0.4});
T({group: 't2', id: 'f2_title_b', t: wt('festa'), sx: 0.02, sy: 0.31, dzk: 0.5, st: S2, w: 0.6, until: S2.tEnd + 0.4});
T({group: 'k2', id: 'f2_chega', t: wt('chega'), sx: -0.36, sy: 0.32, dzk: -0.75, st: S2, w: 0.2});
T({group: 'k2', id: 'f2_furadeira', t: wt('furadeira'), sx: 0, sy: 0.19, dzk: -0.75, st: S2, w: 0.84, impact: true});
T({group: 'm2', id: 'f2_meninas', t: wt('meninas'), sx: -0.18, sy: 0.26, dzk: 1.0, st: S2, w: 0.38});
T({group: 'm2', id: 'f2_viram', t: wt('viram'), sx: -0.16, sy: 0.13, dzk: 1.0, st: S2, w: 0.46});
T({group: 'm2', id: 'f2_jogo', t: wt('jogo'), sx: 0.26, sy: 0.06, dzk: 1.0, st: S2, w: 0.42, impact: true});
// envio
T({group: 'send', id: 's_manda', t: wt('manda'), sx: 0, sy: 0.22, D: 9, w: 0.86});
T({group: 'send', id: 's_jura', t: wt('jura'), sx: 0, sy: 0.06, D: 10, w: 0.62});
T({group: 'send', id: 's_slasher', t: wt('slasher'), sx: 0, sy: -0.04, D: 8.5, w: 0.8, impact: true, until: 25.55});

stationEls({s: S1, killer: 'f1', tag: 'tag_1', tTag: wt('noruega'), logo: 'primevideo', tLogo: wt('prime'), tTana: wt('tá', 2), tanaId: 'tano', placardSide: -1});
T({group: 't1', id: 'f1_title_a', t: wt('presos'), sx: -0.05, sy: 0.45, dzk: 0.5, st: S1, w: 0.48, until: S1.tEnd + 0.4});
T({group: 't1', id: 'f1_title_b', t: wt('gelo'), sx: 0.12, sy: 0.32, dzk: 0.5, st: S1, w: 0.42, until: S1.tEnd + 0.4});
T({id: 'f1_noruega', t: wt('noruega'), sx: -0.38, sy: 0.27, dzk: 1.4, st: S1, w: 0.34});
T({group: 'k1', id: 'f1_hotel', t: wt('hotel'), sx: 0, sy: 0.2, dzk: -0.75, st: S1, w: 0.8});
T({group: 'k1', id: 'f1_neve', t: wt('neve'), sx: 0.32, sy: 0.06, dzk: -0.75, st: S1, w: 0.2});
T({group: 'm1', id: 'f1_oculos', t: wt('óculos'), sx: -0.18, sy: 0.12, dzk: -0.75, st: S1, w: 0.42});
T({group: 'm1', id: 'f1_picareta', t: wt('picareta'), sx: 0, sy: 0.0, dzk: -0.75, st: S1, w: 0.8, impact: true});
// fecho
T({group: 'q', id: 'c_qual', t: wt('qual'), sx: 0, sy: 0.3, D: 11, w: 0.8});
T({group: 'q', id: 'c_ce', t: wt('cê', 1), sx: -0.36, sy: 0.12, D: 8, w: 0.1});
T({group: 'q', id: 'c_nao', t: wt('não'), sx: 0, sy: 0.05, D: 7, w: 0.56, impact: true});
T({group: 'q', id: 'c_queria', t: wt('queria'), sx: 0.02, sy: -0.14, D: 7, w: 0.5});
T({group: 'cta', id: 'c_segue', t: wt('segue'), sx: -0.28, sy: 0.22, D: 8, w: 0.22, until: 38.1});
T({group: 'cta', id: 'c_talking', t: wt('talking'), sx: 0, sy: 0.08, D: 8, w: 0.72, impact: true, until: 38.1});
T({group: 'cta', id: 'c_horror', t: wt('horror'), sx: 0, sy: -0.09, D: 8.2, w: 0.64, until: 38.1});

// linha tracejada vermelha (barbante de investigação) título -> logo
const dashes = (a: El, b: El, t0: number, key: string) => {
  const ax = a.x + a.w * 0.3, ay = a.y - a.h * 0.45, az = a.z;
  const bx = b.x - b.w * 0.3, by = b.y + b.h * 0.45, bz = b.z;
  const L = Math.hypot(bx - ax, by - ay);
  const n = Math.max(4, Math.floor(L / 0.22));
  const ang = Math.atan2(by - ay, bx - ax);
  for (let i = 0; i < n; i++) {
    const f = (i + 0.5) / n;
    add({key: `${key}_${i}`, kind: 'dash', tex: null, w: (L / n) * 0.55, h: 0.035, x: ax + (bx - ax) * f, y: ay + (by - ay) * f, z: az + (bz - az) * f, rotZ: ang, t0: t0 + f * 0.35, emissive: 1});
  }
};
dashes(TEXTS['f3_title_b'] ?? TEXTS['f3_title_a'], ELS.find((e) => e.key.startsWith('logo_hbomax'))!, wt('hbo'), 'dash3');
dashes(TEXTS['f2_title_b'], ELS.find((e) => e.key.startsWith('logo_looke'))!, wt('looke'), 'dash2');
dashes(TEXTS['f1_title_b'], ELS.find((e) => e.key.startsWith('logo_primevideo'))!, wt('prime'), 'dash1');

// ---------------------------------------------------------------- travessias
// 1) a câmera rasga uma fita zebrada logo depois da estação 3
{
  const z = S3.killerZ - 2.4;
  for (const side of [-1, 1] as const) {
    add({key: `rip_a${side}`, kind: 'tape', tex: 'txt/tape.png', w: 3.4, h: 0.3, x: side * 1.6, y: 0.25 + side * 0.55, z, rotZ: 0.32, wave: 0.02, emissive: 0.3, rip: {side}, uv: [side < 0 ? 0 : 0.5, 0, 0.5, 1]});
    add({key: `rip_b${side}`, kind: 'tape', tex: 'txt/tape.png', w: 3.4, h: 0.3, x: side * 1.6, y: 0.25 - side * 0.55, z: z - 0.05, rotZ: -0.32, wave: 0.02, emissive: 0.3, rip: {side}, uv: [side < 0 ? 0.25 : 0.75, 0, 0.5, 1]});
  }
}
// 2) porta que se abre antes do envio/estação 1
export const DOOR_Z = S2.killerZ - 2.8;
{
  const s = sizeKit('r2_wooden_2', 3.6);
  for (const side of [-1, 1] as const) {
    add({key: `door${side}`, kind: 'door', tex: kit('r2_wooden_2'), w: s.w / 2, h: s.h, x: side * (s.w / 4), y: -0.35, z: DOOR_Z, door: {side, hingeX: side * (s.w / 2)}, uv: [side < 0 ? 0 : 0.5, 0, 0.5, 1], shadow: false, emissive: 0.4});
  }
}

export const doorOpenAt = (t: number, depth: number) => smooth(10, 4.2, depth);
