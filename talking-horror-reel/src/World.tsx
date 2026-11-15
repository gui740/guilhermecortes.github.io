import React, {useEffect, useMemo, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import cutMeta from './cutouts.json';
import txtMeta from './texts.json';
import geo from './geo.json';
import {
  FPS, STOPS, Stop, SCALE, K, R, Y, G, W, bgAt, prog, easeInOut, easeOut, backOut, clamp01, wt, WORDS, DURATION, mix,
} from './timeline';
import {cameraAt, toWorld, GONG, O, HOOK_POS, E, END_POS, localCamZ, C0} from './camera';

type V3 = [number, number, number];
const CUT = cutMeta as Record<string, {w: number; h: number; blur?: boolean}>;
const TXT = txtMeta as Record<string, {w: number; h: number; bw?: number; bh?: number}>;

// ---------- texturas (pré-carregadas antes do primeiro frame) ----------
const TEX: Record<string, THREE.Texture> = {};
const texList = () => {
  const l: string[] = ['tex/map.png', 'tex/paper.png'];
  for (const [k, m] of Object.entries(CUT)) { l.push(`tex/${k}.png`, `tex/${k}_sh.png`); if (m.blur) l.push(`tex/${k}_blur.png`); }
  for (const [k, m] of Object.entries(TXT)) { l.push(`tex/txt/${k}.png`); if (m.bw) l.push(`tex/txt/${k}_b.png`); }
  return l;
};
const useTextures = () => {
  const [ok, setOk] = useState(Object.keys(TEX).length > 0);
  const [handle] = useState(() => delayRender('texturas'));
  useEffect(() => {
    if (ok) { continueRender(handle); return; }
    const loader = new THREE.TextureLoader();
    Promise.all(texList().map((p) => loader.loadAsync(staticFile(p)).then((t) => {
      t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 1; t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter;
      if (p.endsWith('paper.png')) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
      TEX[p] = t;
    }))).then(() => { setOk(true); continueRender(handle); });
  }, [handle, ok]);
  return ok;
};
const T = (p: string) => TEX[p];

// ---------- primitivos ----------
const Sprite: React.FC<{tex: string; w: number; h: number; pos?: V3; order: number; opacity?: number; color?: string; fog?: boolean; rotZ?: number; anchor?: 'bottom' | 'center' | 'top'; scale?: number}> =
  ({tex, w, h, pos = [0, 0, 0], order, opacity = 1, color = '#ffffff', fog = false, rotZ = 0, anchor = 'center', scale = 1}) => {
    if (opacity <= 0.001) return null;
    const oy = anchor === 'bottom' ? h / 2 : anchor === 'top' ? -h / 2 : 0;
    return (
      <group position={pos} rotation={[0, 0, rotZ]} scale={scale}>
        <mesh position={[0, oy, 0]} renderOrder={order}>
          <planeGeometry args={[w, h]} />
          <meshBasicMaterial map={T(tex)} transparent opacity={opacity} color={color} depthTest={false} depthWrite={false} fog={fog} side={THREE.DoubleSide} toneMapped={false} />
        </mesh>
      </group>
    );
  };

/** recorte com sombra de papel empilhado, respiração e balanço */
const Cut: React.FC<{name: string; h: number; x: number; y?: number; order: number; t: number; breathe?: number; sway?: number; swayHz?: number; phase?: number; blur?: boolean; hang?: boolean; opacity?: number; flip?: boolean; rot?: number; shadow?: boolean}> =
  ({name, h, x, y = 0, order, t, breathe = 0, sway = 0, swayHz = 0.25, phase = 0, blur = false, hang = false, opacity = 1, flip = false, rot = 0, shadow = true}) => {
    const m = CUT[name]; const w = (h * m.w) / m.h;
    const s = 1 + breathe * Math.sin((t * 2 * Math.PI) / 3.4 + phase);
    const rz = rot + sway * Math.sin(t * 2 * Math.PI * swayHz + phase) + sway * 0.4 * Math.sin(t * 2 * Math.PI * swayHz * 2.3 + phase * 2);
    const pad = blur ? 1.12 : 1;
    return (
      <group position={[x, hang ? y + h : y, 0]} rotation={[0, 0, rz]} scale={[flip ? -s : s, s, 1]}>
        {shadow && !blur ? (
          <mesh position={[0.3, (hang ? -h / 2 : h / 2) - 0.28, -0.25]} renderOrder={order - 1}>
            <planeGeometry args={[w * 1.04, h * 1.04]} />
            <meshBasicMaterial map={T(`tex/${name}_sh.png`)} transparent opacity={0.5 * opacity} color="#000000" depthTest={false} depthWrite={false} fog={false} />
          </mesh>
        ) : null}
        <mesh position={[0, hang ? -h / 2 : h / 2, 0]} renderOrder={order}>
          <planeGeometry args={[w * pad, h * pad]} />
          <meshBasicMaterial map={T(`tex/${name}${blur ? '_blur' : ''}.png`)} transparent opacity={opacity} depthTest={false} depthWrite={false} fog={false} toneMapped={false} side={THREE.DoubleSide} />
        </mesh>
      </group>
    );
  };

/** palavra/placa de texto: entra de trás no eixo Z com blur 12px, 40% de opacidade e escala 0.9; firma em ~5 frames */
const Word: React.FC<{k: string; h: number; x: number; y: number; t: number; at: number; out?: number; order: number; align?: 'left' | 'center' | 'right'; z?: number; rot?: number}> =
  ({k, h, x, y, t, at, out = 1e9, order, align = 'left', z = 0, rot = 0}) => {
    if (t < at - 1 / 60) return null;
    const m = TXT[k]; const w = (h * m.w) / m.h;
    const p = easeOut(prog(t, at, at + 5 / FPS));
    const o = 1 - prog(t, out, out + 0.2);
    if (o <= 0) return null;
    const cx = align === 'left' ? x + w / 2 : align === 'right' ? x - w / 2 : x;
    const sc = 0.9 + 0.1 * p;
    return (
      <group position={[cx, y + h / 2, z - 1.6 * (1 - p)]} scale={sc} rotation={[0, 0, rot]}>
        {m.bw && p < 1 ? (
          <mesh renderOrder={order}>
            <planeGeometry args={[(w * m.bw) / m.w, (h * (m.bh as number)) / m.h]} />
            <meshBasicMaterial map={T(`tex/txt/${k}_b.png`)} transparent opacity={(1 - p) * 0.8 * o} depthTest={false} depthWrite={false} fog={false} toneMapped={false} />
          </mesh>
        ) : null}
        <mesh renderOrder={order + 1}>
          <planeGeometry args={[w, h]} />
          <meshBasicMaterial map={T(`tex/txt/${k}.png`)} transparent opacity={(0.4 + 0.6 * p) * (m.bw ? p : 1) * o + (m.bw ? 0 : 0)} depthTest={false} depthWrite={false} fog={false} toneMapped={false} />
        </mesh>
      </group>
    );
  };

type Line = {h: number; gap?: number; words: {k: string; at: number}[]};
/** bloco de texto flutuando no espaço 3D, virado para um ponto de vista */
const TextBlock: React.FC<{pos: V3; viewer: V3; lines: Line[]; fit: number; t: number; order: number; scale?: number; lineGap?: number; out?: number}> = ({pos, viewer, lines, fit, t, order, scale = 1, lineGap = 0.28, out}) => {
  const quat = useMemo(() => {
    const m = new THREE.Matrix4().lookAt(new THREE.Vector3(...viewer), new THREE.Vector3(...pos), new THREE.Vector3(0, 1, 0));
    return new THREE.Quaternion().setFromRotationMatrix(m);
  }, [pos, viewer]);
  const lay = useMemo(() => {
    const ws = lines.map((l) => l.words.map((w) => (l.h * TXT[w.k].w) / TXT[w.k].h));
    const widths = ws.map((a, i) => a.reduce((s, v) => s + v, 0) + (a.length - 1) * lines[i].h * 0.22);
    const k = fit / Math.max(...widths);
    const total = lines.reduce((s, l) => s + l.h + (l.gap ?? lineGap), 0);
    let y = total / 2; const out: {k: string; at: number; x: number; y: number; h: number}[] = [];
    lines.forEach((l, i) => {
      y -= l.h; let x = -widths[i] / 2;
      l.words.forEach((w, j) => { out.push({k: w.k, at: w.at, x, y, h: l.h}); x += ws[i][j] + l.h * 0.22; });
      y -= l.gap ?? lineGap;
    });
    return {k, out};
  }, [lines, fit, lineGap]);
  return (
    <group position={pos} quaternion={quat} scale={lay.k * scale}>
      {lay.out.map((w, i) => <Word key={i} k={w.k} h={w.h} x={w.x} y={w.y} t={t} at={w.at} order={order} out={out} />)}
    </group>
  );
};

// ---------- mapa ----------
const pieceGeo = (name: 'Thailand' | 'Indonesia') => {
  const shapes = (geo as any)[name].map((ring: number[][]) => new THREE.Shape(ring.map(([x, z]) => new THREE.Vector2(x, -z))));
  const g = new THREE.ExtrudeGeometry(shapes, {depth: 0.5, bevelEnabled: false});
  const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 0.12, uv.getY(i) * 0.12);
  return g;
};
const Piece: React.FC<{name: 'Thailand' | 'Indonesia'; rise: number; color: string; bump?: number}> = ({name, rise, color, bump = 0}) => {
  const g = useMemo(() => pieceGeo(name), [name]);
  const top = mix('#b9b9b9', color, clamp01(rise));
  return (
    <mesh geometry={g} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.03 + 0.5 * rise + bump, 0]} renderOrder={5}>
      <meshBasicMaterial attach="material-0" color={top} map={T('tex/paper.png')} fog={false} toneMapped={false} />
      <meshBasicMaterial attach="material-1" color={mix(top, '#000000', 0.45)} fog={false} toneMapped={false} />
    </mesh>
  );
};

const bez = (a: [number, number], c: [number, number], b: [number, number], u: number): [number, number] =>
  [(1 - u) * (1 - u) * a[0] + 2 * u * (1 - u) * c[0] + u * u * b[0], (1 - u) * (1 - u) * a[1] + 2 * u * (1 - u) * c[1] + u * u * b[1]];
/** linha tracejada vermelha que se desenha enquanto a câmera voa por cima */
const Route: React.FC<{a: [number, number]; c: [number, number]; b: [number, number]; p: number; n: number; color: string}> = ({a, c, b, p, n, color}) => {
  const dashes = useMemo(() => Array.from({length: n}, (_, i) => {
    const u = (i + 0.5) / n; const P = bez(a, c, b, u), Q = bez(a, c, b, u + 0.01);
    return {u, x: P[0], z: P[1], ang: Math.atan2(-(Q[1] - P[1]), Q[0] - P[0])};
  }), [a, c, b, n]);
  return (
    <group>
      {dashes.filter((d) => d.u <= p).map((d, i) => (
        <mesh key={i} position={[d.x, 0.62, d.z]} rotation={[-Math.PI / 2, 0, d.ang]} renderOrder={7}>
          <planeGeometry args={[0.62, 0.2]} />
          <meshBasicMaterial color={color} depthTest={false} depthWrite={false} fog={false} toneMapped={false} />
        </mesh>
      ))}
    </group>
  );
};

const Flat: React.FC<{k: string; h: number; x: number; z: number; order: number; opacity?: number; scale?: number; rot?: number}> = ({k, h, x, z, order, opacity = 1, scale = 1, rot = 0}) => {
  const m = TXT[k];
  if (opacity <= 0) return null;
  return (
    <mesh position={[x, 0.66, z]} rotation={[-Math.PI / 2, 0, rot]} scale={scale} renderOrder={order}>
      <planeGeometry args={[(h * m.w) / m.h, h]} />
      <meshBasicMaterial map={T(`tex/txt/${k}.png`)} transparent opacity={opacity} depthTest={false} depthWrite={false} fog={false} toneMapped={false} />
    </mesh>
  );
};

// ---------- dioramas ----------
type CutDef = {name: string; h: number; x: number; y?: number; breathe?: number; sway?: number; swayHz?: number; phase?: number; blur?: boolean; hang?: boolean; flip?: boolean; rot?: number; z?: number; flicker?: boolean};
type DioDef = {
  sky: CutDef[]; mid: CutDef[]; arch: CutDef[]; legend: CutDef[]; figure: CutDef; fg: CutDef[]; cross: CutDef[];
  country: string; small: [string, number][]; smallB: [string, number]; keyword: [string, number]; kwH: number; kwY: number;
  title: string; titleH: number; pill: string; pillAt: number; countryAt: number; stamp: string; num: string;
};
const [S1, S2, S3] = STOPS;
const DIO: Record<string, DioDef> = {
  th: {
    sky: [{name: 'moon', h: 4.6, x: 3.5, y: 12.6, sway: 0.02, swayHz: 0.05}],
    mid: [{name: 'th_mount', h: 7.8, x: 0.5}, {name: 'th_bamboo', h: 6.2, x: -6.4, sway: 0.012, swayHz: 0.12}],
    arch: [{name: 'th_house', h: 7.4, x: 4.4}],
    legend: [{name: 'th_spirit', h: 6.6, x: -4.9, sway: 0.006}, {name: 'th_ghost', h: 7.9, x: 5.6, breathe: 0.01, phase: 1.7, sway: 0.008, swayHz: 0.1}],
    figure: {name: 'th_fig', h: 9.9, x: -0.5, breathe: 0.014, sway: 0.004, swayHz: 0.09},
    fg: [{name: 'th_lamp', h: 4.4, x: 5.2, z: 4.2, sway: 0.05, swayHz: 0.3}, {name: 'th_bamboo', h: 8.5, x: -12.2, y: 4, z: 9, blur: true, sway: 0.015, swayHz: 0.1, phase: 2}, {name: 'th_leaf', h: 4.2, x: 8.6, y: -1.6, z: 11, blur: true, sway: 0.05, swayHz: 0.16, flip: true}],
    cross: [{name: 'th_leaf', h: 6.5, x: -5.6, y: 2.0, blur: true, sway: 0.06, swayHz: 0.18, rot: 0.25}, {name: 'th_leaf', h: 5.5, x: 5.4, y: 10.5, blur: true, sway: 0.05, swayHz: 0.14, rot: 2.6, phase: 1}],
    country: 'c1', small: [['k1a', wt('th2', 0)]], smallB: ['k1b', wt('th2', 12)], keyword: ['k1', wt('th2', 9)], kwH: 2.9, kwY: 8.0,
    title: 't1', titleH: 2.4, pill: 'nfK', pillAt: wt('th3', 4), countryAt: wt('th1', 2), stamp: 'st1', num: 'n1',
  },
  fm: {
    sky: [{name: 'moon2', h: 4.6, x: 4.3, y: 13.2, sway: 0.02, swayHz: 0.05}],
    mid: [{name: 'fm_palm', h: 4.4, x: -4.6, y: 14.2, sway: 0.03, swayHz: 0.14, flip: true}, {name: 'th_mount', h: 6.2, x: -1, flip: true}],
    arch: [{name: 'fm_house', h: 7.8, x: -2.9}],
    legend: [{name: 'fm_ghost', h: 8.4, x: 5.3, breathe: 0.01, phase: 1.1, sway: 0.007, swayHz: 0.1}, {name: 'fm_candles', h: 3.1, x: -5.6, breathe: 0.02, phase: 0.4}],
    figure: {name: 'fm_fig', h: 10.3, x: 0, breathe: 0.014, sway: 0.004, swayHz: 0.09},
    fg: [{name: 'fm_candles', h: 3.4, x: 7.4, y: -0.8, z: 7, blur: true, flicker: true}, {name: 'fm_palm', h: 5.2, x: -8.5, y: 13.5, z: 10, blur: true, sway: 0.05, swayHz: 0.15, flip: true}],
    cross: [{name: 'fm_palm', h: 5, x: 6.5, y: 11.5, blur: true, sway: 0.05, swayHz: 0.16}, {name: 'th_leaf', h: 6, x: -5.4, y: 2.0, blur: true, sway: 0.05, swayHz: 0.18, rot: 0.2}],
    country: 'c2', small: [['k2a', wt('fm2', 0)]], smallB: ['k2b', wt('fm2', 6)], keyword: ['k2', wt('fm2', 3)], kwH: 3.1, kwY: 8.6,
    title: 't2', titleH: 2.75, pill: 'nfK', pillAt: wt('fm3', 2), countryAt: wt('fm1', 5), stamp: 'st2', num: 'n2',
  },
  imp: {
    sky: [{name: 'moon', h: 3.2, x: 5.2, y: 15.2, sway: 0.02, swayHz: 0.05, flip: true}],
    mid: [{name: 'imp_gunungan', h: 10.5, x: -5.2, sway: 0.015, swayHz: 0.11}, {name: 'th_bamboo', h: 5.4, x: 6.6, sway: 0.012, swayHz: 0.12, flip: true}],
    arch: [{name: 'imp_house', h: 7.2, x: 1.2}],
    legend: [{name: 'imp_shadow', h: 7.6, x: 5.4, sway: 0.008, swayHz: 0.2}, {name: 'imp_woman', h: 7.6, x: -5.3, breathe: 0.01, phase: 2.2, sway: 0.006, swayHz: 0.1}],
    figure: {name: 'imp_fig', h: 10.2, x: 0.3, breathe: 0.014, sway: 0.004, swayHz: 0.09},
    fg: [{name: 'imp_frond', h: 5.5, x: 9.2, y: -1.8, z: 8, blur: true, sway: 0.05, swayHz: 0.15}, {name: 'fm_candles', h: 3.0, x: -7.6, y: -0.8, z: 6, blur: true, flicker: true}],
    cross: [{name: 'imp_frond', h: 7, x: -5.6, y: 2, blur: true, sway: 0.06, swayHz: 0.17, flip: true}, {name: 'fm_palm', h: 5, x: 6.5, y: 11.5, blur: true, sway: 0.05, swayHz: 0.15}],
    country: 'c3', small: [['k3a', wt('im3', 0)]], smallB: ['k3b', wt('im3', 6)], keyword: ['k3', wt('im3', 5)], kwH: 3.05, kwY: 8.5,
    title: 't3', titleH: 2.3, pill: 'atv', pillAt: wt('im4', 1), countryAt: S3.ta - 0.15, stamp: 'st3', num: 'n3',
  },
};

const Dust: React.FC<{t: number; color: string; order: number; seed: number; n: number}> = ({t, color, order, seed, n}) => {
  if (OFF.has('dust')) return null;
  const base = useMemo(() => { let s = seed; const r = () => { s = (s * 16807) % 2147483647; return s / 2147483647; }; return Array.from({length: n}, () => [r() * 20 - 10, r() * 18, r() * 30 - 7, r() * 6.28, 0.3 + r()]); }, [seed, n]);
  const geom = useMemo(() => new THREE.BufferGeometry(), []);
  const arr = new Float32Array(n * 3);
  base.forEach((b, i) => { arr[i * 3] = b[0] + 0.7 * Math.sin(t * 0.4 * b[4] + b[3]); arr[i * 3 + 1] = (b[1] + t * 0.35 * b[4]) % 18; arr[i * 3 + 2] = b[2] + 0.5 * Math.cos(t * 0.3 * b[4] + b[3]); });
  geom.setAttribute('position', new THREE.BufferAttribute(arr, 3));
  return (
    <points geometry={geom} renderOrder={order} frustumCulled={false}>
      <pointsMaterial color={color} size={0.11} sizeAttenuation transparent opacity={0.55} depthTest={false} depthWrite={false} fog={false} />
    </points>
  );
};

const Diorama: React.FC<{s: Stop; idx: number; t: number; cover?: boolean; mul?: number}> = ({s, idx, t, cover = false, mul = 1}) => {
  const d = DIO[s.id];
  const base = 100 + idx * 100;
  // pop-up: cada camada gira de deitada para em pé, em cascata (3 frames de atraso); na saída, cascata inversa
  const up = (i: number) => {
    if (cover) return 1;
    const a = s.ta - 0.55 + i * 0.1, b = s.td + 0.05 + (7 - i) * 0.1;
    if (t < b) return backOut(prog(t, a, a + 0.45));
    return 1 - easeInOut(prog(t, b, b + 0.42));
  };
  const crossZ = useMemo(() => localCamZ(s, s.tt - 0.08), [s]);
  if (!cover && (t < s.ta - 0.6 || t > s.td + 1.3)) return null;
  const layer = (i: number, z: number, children: React.ReactNode) => {
    const p = up(i); if (p <= 0.001) return null;
    return (
      <group position={[0, 0.9 + i * 0.03, z]} rotation={[(-Math.PI / 2) * (1 - p), 0, 0]} scale={0.25 + 0.75 * clamp01(p)}>{children}</group>
    );
  };
  const cuts = (list: CutDef[], order: number) => OFF.has('cuts') ? null : list.map((c, i) => <Cut key={i} {...c} order={order + i * 2} t={t} />);
  const mist = (z: number, y: number, ph: number, order: number, op: number) => OFF.has('mist') ? null : (
    <Sprite tex="tex/cloud.png" w={22} h={8} pos={[3 * Math.sin(t * 0.22 + ph), y + 0.3 * Math.sin(t * 0.5 + ph), z]} order={order} opacity={op} color={s.bg === K ? '#9a9a9a' : '#ffffff'} />
  );
  const star = prog(t, s.tt, s.tt + 0.3);
  const tm = TXT[d.title]; const tw = (d.titleH * tm.w) / tm.h;
  const pm = TXT[d.pill]; const ph = 1.4, pw = (ph * pm.w) / pm.h;
  const titleX = -4.75, titleY = 3.0, pillX = 4.0 - pw, pillY = 2.45;
  const pillOn = t >= d.pillAt;
  const dashP = prog(t, d.pillAt - 0.25, d.pillAt + 0.1);
  const dashPts: [number, number][] = [];
  for (let i = 0; i < 9; i++) { const u = i / 8; dashPts.push([titleX + 0.6 + u * (pillX - titleX - 0.9), titleY - 0.25 - (titleY - pillY - ph / 2 - 0.25) * Math.min(1, u * 2.2)]); }
  return (
    <group position={[s.anchor[0], 0, s.anchor[1]]} scale={SCALE * mul}>
      {layer(0, -8, <mesh position={[0, 13, 0]} renderOrder={base}><planeGeometry args={[21, 26]} /><meshBasicMaterial color={s.bg} map={T('tex/paper.png')} depthTest={false} depthWrite={false} fog={false} toneMapped={false} /></mesh>)}
      {layer(1, -6.6, cuts(d.sky, base + 4))}
      {layer(2, -5.4, <>{cuts(d.mid, base + 10)}{mist(0.6, 3.5, idx, base + 18, 0.28)}</>)}
      {layer(3, -3.6, cuts(d.arch, base + 20))}
      {layer(4, -2.0, cuts(d.legend, base + 30))}
      {layer(5, -0.9, <>
        {!cover ? <Word k={d.country} h={s.id === 'imp' ? 1.7 : 2.0} x={-4.75} y={d.kwY + d.kwH + 0.95} t={t} at={d.countryAt} order={base + 40} /> : null}
        {!cover ? d.small.map(([k, at], i) => <Word key={i} k={k} h={1.05} x={-4.7} y={d.kwY + d.kwH - 0.05} t={t} at={at} out={d.smallB[1] - 0.1} order={base + 42} />) : null}
        {!cover ? <Word k={d.smallB[0]} h={1.05} x={-4.7} y={d.kwY + d.kwH - 0.05} t={t} at={d.smallB[1]} order={base + 42} /> : null}
        {!cover ? <Word k={d.keyword[0]} h={d.kwH} x={-0.35} y={d.kwY} t={t} at={d.keyword[1]} order={base + 44} align="center" /> : null}
      </>)}
      {layer(6, 0, <>
        {star > 0 || cover ? <Sprite tex="tex/txt/star.png" w={9.4} h={9.4} pos={[0.2, 5.3, -0.45]} order={base + 48} scale={cover ? 1.25 : 0.3 + 0.7 * backOut(star)} rotZ={t * 0.12} /> : null}
        <Dust t={t} color={s.fg} order={base + 49} seed={7 + idx} n={70} />
        <Cut {...d.figure} order={base + 52} t={t} />
      </>)}
      {!cover ? layer(7, 1.5, <>
        <Word k={d.title} h={d.titleH} x={titleX} y={titleY} t={t} at={s.tt} order={base + 60} />
        {dashPts.map((p, i) => (i / 8 <= dashP && t >= d.pillAt - 0.25 ? <mesh key={i} position={[p[0], p[1], 0.2]} renderOrder={base + 63}><planeGeometry args={[0.26, 0.11]} /><meshBasicMaterial color={s.accent} depthTest={false} depthWrite={false} fog={false} toneMapped={false} /></mesh> : null))}
        {pillOn ? <Word k={d.pill} h={ph} x={pillX} y={pillY} t={t} at={d.pillAt} order={base + 64} z={0.4} /> : null}
        {mist(1.4, 1.2, idx + 2, base + 58, 0.16)}
      </>) : null}
      {cover ? null : layer(7, 0, d.fg.map((c, i) => (
        <group key={i} position={[0, 0, c.z ?? 5]}><Cut {...c} order={base + 70 + i * 2} t={t} opacity={c.flicker ? 0.82 + 0.18 * Math.sin(t * 23 + i) * Math.sin(t * 7.1) : 1} /></group>
      )))}
      {!cover && t > s.tt - 0.95 && t < s.tt + 0.6 ? <group position={[0, 0.9, crossZ]} rotation={[(-Math.PI / 2) * (1 - backOut(prog(t, s.tt - 0.9, s.tt - 0.5))), 0, 0]}>
        {d.cross.map((c, i) => <Cut key={i} {...c} order={base + 80 + i} t={t} opacity={1} />)}
      </group> : null}
    </group>
  );
};

// ---------- cena ----------
const HOOKS: Record<string, Line[]> = {
  A: [
    {h: 3.2, words: [{k: 'hk1', at: wt('hook', 0)}, {k: 'hk2', at: wt('hook', 1)}]},
    {h: 3.2, words: [{k: 'hk3', at: wt('hook', 2)}, {k: 'hk4', at: wt('hook', 3)}]},
    {h: 2.0, gap: 0.1, words: [{k: 'hk5', at: wt('hook', 4)}]},
    {h: 3.2, words: [{k: 'hk6', at: wt('hook', 7)}, {k: 'hk7', at: wt('hook', 8)}, {k: 'hk8', at: wt('hook', 9)}]},
    {h: 3.2, words: [{k: 'hk9', at: wt('hook', 10)}]},
  ],
  B: [
    {h: 3.4, words: [{k: 'hb1', at: 1.17}]}, {h: 3.4, words: [{k: 'hb2', at: 1.39}]},
    {h: 2.1, gap: 0.1, words: [{k: 'hb3', at: 1.93}]}, {h: 3.4, words: [{k: 'hb4', at: 2.44}]},
  ],
  C: [
    {h: 3.4, words: [{k: 'hc1', at: 0.2}, {k: 'hc2', at: 0.5}]}, {h: 3.4, words: [{k: 'hc3', at: 0.68}]},
    {h: 2.1, gap: 0.1, words: [{k: 'hc4', at: 1.1}]}, {h: 3.4, words: [{k: 'hc5', at: 1.66}]},
  ],
};
const SEND: Line[] = [
  {h: 1.5, words: [{k: 'sd1', at: wt('send', 0)}]}, {h: 0.85, gap: 0.0, words: [{k: 'sd2', at: wt('send', 1)}]},
  {h: 1.5, words: [{k: 'sd3', at: wt('send', 5)}]}, {h: 0.85, gap: 0.0, words: [{k: 'sd4', at: wt('send', 7)}]},
  {h: 1.5, words: [{k: 'sd5', at: wt('send', 10)}]},
];
const ENDQ: Line[] = [
  {h: 3, words: [{k: 'q1', at: wt('q', 0)}]}, {h: 3, words: [{k: 'q2', at: wt('q', 2)}]},
  {h: 2.0, gap: 0.0, words: [{k: 'q3', at: wt('q', 3)}]}, {h: 3, gap: 1.2, words: [{k: 'q4', at: wt('q', 5)}]},
  {h: 1.9, gap: 0.0, words: [{k: 'f1', at: wt('cta', 0)}]}, {h: 2.6, words: [{k: 'f2', at: wt('cta', 2)}]},
];
const CLOUDS: [number, number, number, number, number][] = [
  [-17, 40, 30, 12, 0], [17, 46, 36, 11, 1], [-9, 26, 20, 9, 2],
  [-10, 13, 13, 7, 4], [6, 15, 16, 8, 5], [-7, 11, 31, 6, 6], [9, 17, 30, 8, 7], [14, 13, 37, 7, 9],
  [-12, 40, 46, 11, 10], [17, 44, 42, 12, 11], [-18, 28, 22, 10, 13],
];
const routeA = {a: S1.anchor, c: [S1.anchor[0] + 7.5, (S1.anchor[1] + S2.anchor[1]) / 2 - 1] as [number, number], b: S2.anchor};
const routeB = {a: S2.anchor, c: [(S2.anchor[0] + S3.anchor[0]) / 2, S2.anchor[1] + 2.4] as [number, number], b: S3.anchor};
const pinPos = (s: Stop): [number, number] => [s.anchor[0], s.anchor[1]];

export const OFF = new Set<string>();
const Scene: React.FC<{t: number; hook: string; cover: boolean}> = ({t, hook, cover}) => {
  const {camera, scene} = useThree();
  const cam = camera as THREE.PerspectiveCamera;
  const c = cover ? {p: [2.2, 27, 47] as V3, q: [0.6, 2.5, -3] as V3, fov: 50} : cameraAt(t);
  cam.position.set(...c.p); cam.fov = c.fov; cam.near = 0.15; cam.far = 900; cam.up.set(0, 1, 0); cam.lookAt(...c.q); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  const bg = cover ? G : bgAt(t);
  scene.background = new THREE.Color(bg);
  scene.fog = new THREE.Fog(bg, 70, 420);
  const gongQ = useMemo(() => new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().lookAt(new THREE.Vector3(...O), new THREE.Vector3(...GONG), new THREE.Vector3(0, 1, 0))), []);
  const riseTH = cover ? 1 : backOut(prog(t, S1.ta - 0.75, S1.ta - 0.25));
  const riseID = cover ? 0 : backOut(prog(t, S2.ta - 0.75, S2.ta - 0.25));
  const bumpID = cover ? 0 : 0.35 * Math.sin(Math.PI * prog(t, S3.ta - 0.6, S3.ta - 0.1));
  const sendScale = 1 + 1.3 * easeInOut(prog(t, 13.5, 16.2));
  const mapFg = bg;
  return (
    <>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]} renderOrder={0}><planeGeometry args={[3000, 3000]} /><meshBasicMaterial color={mapFg} depthWrite={false} toneMapped={false} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, -6]} renderOrder={1}>
        <planeGeometry args={[97, 72]} />
        <meshBasicMaterial map={T('tex/map.png')} transparent depthTest={false} depthWrite={false} toneMapped={false} />
      </mesh>
      <Piece name="Thailand" rise={riseTH} color={S1.pieceColor} />
      <Piece name="Indonesia" rise={riseID} color={S2.pieceColor} bump={bumpID} />
      {!cover ? <>
        <Route {...routeA} p={easeInOut(prog(t, 13.0, 17.3))} n={34} color={R === bg ? K : R} />
        <Route {...routeB} p={easeInOut(prog(t, 24.0, 25.6))} n={9} color={t > 24.8 ? R : K} />
      </> : null}
      {STOPS.map((s, i) => {
        const d = DIO[s.id]; const [x, z] = pinPos(s);
        const arrive = cover ? 1 : prog(t, s.ta - 0.45, s.ta + 0.1);
        const jump = cover ? 0 : 1.6 * Math.sin(Math.PI * prog(t, s.ta - 0.5, s.ta)) * (1 - 0.0);
        const hideAtStop = cover ? 1 : 1 - prog(t, s.ta - 0.2, s.ta + 0.2) * (1 - prog(t, s.td + 0.3, s.td + 0.9));
        const stampP = prog(t, s.ta - 0.42, s.ta - 0.3);
        const ox = [4.6, -4.4, 4.6][i], oz = [3.2, 3.6, 3.4][i];
        return (
          <group key={s.id}>
            <Flat k={d.num} h={3.4} x={x + ox * 0.62} z={z + oz * 0.5} order={8} opacity={0.95} rot={0.05} />
            {stampP > 0 || cover ? <Flat k={d.stamp} h={2.3} x={x - ox * 0.7} z={z + oz + 0.6} order={9} opacity={cover ? 1 : stampP} scale={cover ? 1 : 2.4 - 1.4 * easeOut(stampP)} rot={-0.1} /> : null}
            <group position={[x + ox * 0.18, 0.6 + jump, z + oz * 0.22]}>
              <Sprite tex="tex/txt/pin.png" w={1.5} h={2.08} order={95 + i * 100 + (hideAtStop < 1 ? 0 : 0)} anchor="bottom" opacity={hideAtStop} scale={1 + 0.15 * Math.sin(Math.PI * arrive)} />
            </group>
          </group>
        );
      })}
      {STOPS.map((s, i) => (OFF.has('dio') || (cover && i > 0) ? null : <Diorama key={s.id} s={s} idx={i} t={t} cover={cover} mul={cover ? 2.3 : 1} />))}
      {!cover ? <>
        {t < 6 ? <TextBlock pos={HOOK_POS} viewer={O} lines={HOOKS[hook]} fit={hook === 'A' ? 18.6 : 17} t={t} order={960} lineGap={-0.3} /> : null}
        {t > 13 && t < 16.9 ? <TextBlock pos={[-0.6, 3 + 0.8 * (sendScale - 1), 12.5]} viewer={[-1.5, 24, 34]} out={16.5} lines={SEND} fit={4.4} t={t} order={975} scale={sendScale} lineGap={-0.2} /> : null}
        {t > 31 ? <TextBlock pos={[END_POS[0], END_POS[1] + 5.2, END_POS[2] - 7.4]} viewer={E} lines={ENDQ} fit={18.5} t={t} order={965} lineGap={-0.5} /> : null}
        {CLOUDS.map(([x, y, z, w, i]) => (
          <Sprite key={i} tex="tex/cloud.png" w={w} h={w * 0.467} pos={[x + 1.6 * Math.sin(t * 0.13 + i), y + 0.3 * Math.sin(t * 0.4 + i * 2), z]} order={Math.round(Math.max(20, 990 - Math.hypot(x - c.p[0], y - c.p[1], z - c.p[2])))} opacity={0.9} />
        ))}
        <group position={GONG} quaternion={gongQ}>
          <Sprite tex="tex/gong.png" w={3.75} h={4.2} order={990} rotZ={0.035 * Math.sin(t * 1.3)} pos={[0, 0.25, 0]} />
        </group>
      </> : (
        <TextBlock pos={[1.5, 23.2, 27.6]} viewer={[2.2, 27, 47]} t={1} order={960} fit={6.3} lineGap={-0.35}
          lines={[{h: 1.9, words: [{k: 'cv1', at: 0}]}, {h: 1.9, words: [{k: 'cv2', at: 0}]}, {h: 1.25, gap: 0, words: [{k: 'cv3', at: 0}]}]} />
      )}
    </>
  );
};

// legenda secundária: Inter Bold 44px, 1 a 3 palavras, centralizada na área segura
const CAPS = (() => {
  const out: {s: number; e: number; text: string}[] = []; let cur: typeof WORDS = [];
  const flush = () => { if (cur.length) { out.push({s: cur[0].s, e: cur[cur.length - 1].e, text: cur.map((w) => w.w).join(' ')}); cur = []; } };
  WORDS.forEach((w, i) => {
    const prev = cur[cur.length - 1];
    if (prev && (prev.seg !== w.seg || cur.length >= 3 || cur.map((x) => x.w).join(' ').length + w.w.length > 17 || /[.,:?]$/.test(prev.w))) flush();
    cur.push(w); if (i === WORDS.length - 1) flush();
  });
  return out.map((c, i) => ({...c, e: Math.min(out[i + 1]?.s ?? c.e + 0.5, c.e + 0.5)}));
})();

export const World: React.FC<{hook?: string; cover?: boolean; captions?: boolean; off?: string}> = ({hook = 'A', cover = false, captions = true, off = ''}) => {
  off.split(',').filter(Boolean).forEach((o) => OFF.add(o));
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const t = frame / FPS;
  const ok = useTextures();
  const [fontHandle] = useState(() => delayRender('fonte'));
  useEffect(() => {
    const f = new FontFace('InterCap', `url(${staticFile('fonts/Inter.ttf')})`, {weight: '100 900'});
    f.load().then((l) => { (document as any).fonts.add(l); continueRender(fontHandle); }).catch(() => continueRender(fontHandle));
  }, [fontHandle]);
  const cap = CAPS.find((c) => t >= c.s - 0.02 && t < c.e);
  const bg = bgAt(t);
  const capColor = bg === G || t < 13.6 ? K : W;
  return (
    <AbsoluteFill style={{backgroundColor: cover ? G : bg}}>
      {ok ? (
        <ThreeCanvas width={width} height={height} linear flat gl={{antialias: false, preserveDrawingBuffer: true, powerPreference: "high-performance"}} dpr={1} camera={{fov: 50, near: 0.15, far: 900, position: C0}}>
          <Scene t={t} hook={hook} cover={cover} />
        </ThreeCanvas>
      ) : null}
      {captions && !cover && cap && hook === 'A' && !(t > 13.3 && t < 16.25) ? (
        <div style={{position: 'absolute', top: 252 * (height / 1920), left: 70 * (width / 1080), width: 870 * (width / 1080), textAlign: 'center', fontFamily: 'InterCap', fontWeight: 700, fontSize: 44 * (height / 1920), color: capColor, letterSpacing: '-0.01em'}}>
          {cap.text.replace(/[.,:]$/, '')}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
export {DURATION};
