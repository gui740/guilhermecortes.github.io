// Motor de cena: câmera 3D real (CSS perspective + translateZ), camadas em profundidade,
// texto palavra-por-palavra, gráficos que ilustram a fala.
import React from 'react';
import {AbsoluteFill, Img, staticFile, Easing, random} from 'remotion';
import manifest from '../../public/cut/manifest.json';

export const FPS = 30, W = 1080, H = 1920, P = 1000;
export const COL = {gray: '#EDEDED', red: '#F23B3B', black: '#1C1C1C', yellow: '#F2E63A', white: '#FFFFFF'};
export type Bg = 'gray' | 'red' | 'black';
export const ink = (bg: Bg) => (bg === 'gray' ? COL.black : bg === 'red' ? COL.white : COL.yellow);
export const hlc = (bg: Bg) => (bg === 'gray' ? COL.red : bg === 'red' ? COL.yellow : COL.red);
export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const eio = (x: number) => Easing.inOut(Easing.cubic)(clamp(x));
export const eout = (x: number) => Easing.out(Easing.cubic)(clamp(x));
export const ein = (x: number) => Easing.in(Easing.cubic)(clamp(x));
const backOut = (x: number) => {const c1 = 1.9, c3 = c1 + 1; x = clamp(x); return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);};
const MAN = manifest as Record<string, {w: number; h: number}>;

// ---------- margens de segurança ----------
export const SAFE = {top: 250, bottom: 420, right: 140, left: 90};
export const TEXT_W = W - SAFE.left - SAFE.right; // 850

// ---------- medição de texto (canvas) ----------
let _ctx: CanvasRenderingContext2D | null = null;
export const FONT = {A: 'Anton', P: 'PlayfairI', I: 'InterB'};
export const fontCss = (f: 'A' | 'P' | 'I', s: number) =>
  f === 'A' ? `400 ${s}px Anton` : f === 'P' ? `italic 500 ${s}px PlayfairI` : `700 ${s}px InterB`;
export const measure = (text: string, f: 'A' | 'P' | 'I', s: number) => {
  if (typeof document === 'undefined') return text.length * s * 0.5;
  if (!_ctx) _ctx = document.createElement('canvas').getContext('2d');
  _ctx!.font = fontCss(f, s);
  const w = _ctx!.measureText(text).width;
  return f === 'P' ? w * 0.8 : w; // Playfair a ~80% de largura
};

// ---------- tipos ----------
export type Tok = {t: string; f: 'A' | 'P'; s: number; hl?: boolean; at: number};
export type Block = {
  from: number; to: number; bg: Bg;
  lines?: Tok[][]; textTo?: number; textTop?: number; exit?: 'flip' | 'push';
  layers: Layer[];
};
export type Layer =
  | {k: 'cut'; src: string; x: number; y: number; h: number; z: number; anim?: 'breath' | 'sway' | 'float'; blur?: number; flip?: boolean; rot?: number; from?: number; to?: number; pop?: number; shadow?: boolean}
  | {k: 'star'; x: number; y: number; size: number; z: number; at: number; color?: string}
  | {k: 'flames'; x: number; y: number; w: number; h: number; z: number; n?: number}
  | {k: 'symbol'; x: number; y: number; size: number; z: number; at: number; dur?: number; color?: string; seed?: number}
  | {k: 'grid'; z: number}
  | {k: 'dust'; z: number; n?: number; seed?: number}
  | {k: 'smoke'; z: number; seed?: number}
  | {k: 'num'; text: string; x: number; y: number; size: number; z: number; at: number}
  | {k: 'logo'; x: number; y: number; w: number; z: number; at: number}
  | {k: 'dash'; x1: number; y1: number; x2: number; y2: number; z: number; at: number; dur?: number}
  | {k: 'tent'; x: number; y: number; w: number; z: number}
  | {k: 'forest'; items: {src: string; x: number; y: number; h: number; z: number; flip?: boolean; rot?: number}[]}
  | {k: 'tv'; x: number; y: number; w: number; z: number; until: number; render: () => React.ReactNode}
  | {k: 'text'; z?: number};

export type Scene = {
  id: string; from: number; to: number; dir: 1 | -1; push?: number; drift?: number;
  tag?: {text: string; from: number};
  blocks: Block[];
  opening?: boolean;
};

// ---------- planos 3D ----------
// Cada plano é uma folha 1080x1920 em translateZ(z) escalada para aparecer em tamanho de tela
// quando a câmera está em repouso; o conteúdo é posicionado em coordenadas de tela.
const Plane: React.FC<{z: number; camZ: number; spread: number; blur?: number; children: React.ReactNode; zOverride?: number}> = ({z, camZ, spread, blur = 0, children, zOverride}) => {
  const zz = zOverride ?? z * spread;
  if (zz + camZ > P - 15) return null; // já passou da câmera
  const s = (P - z) / P;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, transform: `translateZ(${zz}px) scale(${s})`, transformOrigin: '50% 50%', filter: blur ? `blur(${blur}px)` : undefined, transformStyle: 'flat'}}>
      {children}
    </div>
  );
};

// ---------- recorte ----------
const Cut: React.FC<{L: Extract<Layer, {k: 'cut'}>; t: number; blurred?: boolean}> = ({L, t, blurred}) => {
  const src = blurred && MAN[L.src + '_b'] ? L.src + '_b' : L.src;
  const m = MAN[src];
  if (!m) return null;
  const h = L.h, w = (h * m.w) / m.h;
  let sc = 1, r = L.rot ?? 0, dy = 0;
  const seed = L.x * 0.01;
  if (L.anim === 'breath') sc = 1 + 0.016 * Math.sin((t * 2 * Math.PI) / 2.6 + seed);
  if (L.anim === 'sway') r += 1.7 * Math.sin((t * 2 * Math.PI) / 3.2 + seed);
  if (L.anim === 'float') dy = 10 * Math.sin((t * 2 * Math.PI) / 4 + seed);
  let op = 1;
  if (L.pop !== undefined) {
    const p = clamp((t - L.pop) * FPS / 7);
    if (t < L.pop) return null;
    sc *= 0.85 + 0.15 * backOut(p); op = clamp(p * 2);
  }
  return (
    <Img src={staticFile(`cut/${src}.png`)} style={{position: 'absolute', left: L.x - w / 2, top: L.y - h / 2 + dy, width: w, height: h,
      transform: `scale(${L.flip ? -sc : sc}, ${sc}) rotate(${L.flip ? -r : r}deg)`, transformOrigin: L.anim === 'sway' ? '50% 0%' : '50% 100%',
      opacity: op}} />
  );
};

// ---------- estrela de pontas ----------
const Star: React.FC<{L: Extract<Layer, {k: 'star'}>; t: number}> = ({L, t}) => {
  if (t < L.at) return null;
  const p = clamp((t - L.at) * FPS / 9);
  const sc = backOut(p);
  const n = 16, pts: string[] = [];
  for (let i = 0; i < n * 2; i++) {
    const a = (i / (n * 2)) * Math.PI * 2, r = i % 2 ? 0.6 : 1;
    pts.push(`${50 + 50 * r * Math.cos(a)},${50 + 50 * r * Math.sin(a)}`);
  }
  return (
    <svg viewBox="0 0 100 100" style={{position: 'absolute', left: L.x - L.size / 2, top: L.y - L.size / 2, width: L.size, height: L.size,
      transform: `scale(${sc}) rotate(${(t - L.at) * 14}deg)`}}>
      <polygon points={pts.join(' ')} fill={L.color ?? COL.yellow} />
    </svg>
  );
};

// ---------- chamas chapadas ----------
const Flames: React.FC<{L: Extract<Layer, {k: 'flames'}>; t: number}> = ({L, t}) => {
  const n = L.n ?? 9;
  const paths: string[] = [];
  for (let i = 0; i < n; i++) {
    const cx = (i + 0.5) / n * 100 + Math.sin(t * 3 + i) * 1.5;
    const hw = 100 / n * (0.9 + 0.3 * random(`fw${i}`));
    const hh = 60 + 35 * random(`fh${i}`) + 14 * Math.sin(t * 9 + i * 1.7) + 8 * Math.sin(t * 13.3 + i);
    const sway = 7 * Math.sin(t * 5 + i * 2.1);
    const top = 100 - hh;
    paths.push(`M${cx - hw},100 Q${cx - hw * 0.9},${top + hh * 0.45} ${cx + sway},${top} Q${cx + hw * 0.9},${top + hh * 0.45} ${cx + hw},100 Z`);
  }
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{position: 'absolute', left: L.x - L.w / 2, top: L.y - L.h, width: L.w, height: L.h}}>
      {paths.map((d, i) => <path key={i} d={d} fill={COL.yellow} />)}
    </svg>
  );
};

// ---------- símbolo de ritual desenhado à mão (traço a traço) ----------
const wobblyCircle = (r: number, seed: string, n = 48) => {
  let d = '';
  for (let i = 0; i <= n; i++) {
    const a = (i / n) * Math.PI * 2 + 0.3;
    const rr = r * (1 + (random(`${seed}${i % n}`) - 0.5) * 0.035);
    d += `${i ? 'L' : 'M'}${(50 + rr * Math.cos(a)).toFixed(2)},${(50 + rr * Math.sin(a)).toFixed(2)} `;
  }
  return d;
};
const SYMBOL_PATHS = (seed: string) => {
  const p: string[] = [wobblyCircle(46, seed + 'a'), wobblyCircle(38, seed + 'b')];
  // triângulo + linha vertical + runas genéricas
  const tri = [0, 1, 2].map((i) => {const a = -Math.PI / 2 + (i * 2 * Math.PI) / 3; return [50 + 36 * Math.cos(a), 50 + 36 * Math.sin(a)];});
  p.push(`M${tri[0]} L${tri[1]} L${tri[2]} Z`.replace(/,/g, ' ').replace(/(\d) (\d)/g, '$1,$2'));
  p.push('M50,10 L50,90');
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2, cx = 50 + 42 * Math.cos(a), cy = 50 + 42 * Math.sin(a), s = 2.6;
    const kind = i % 4;
    if (kind === 0) p.push(`M${cx - s},${cy - s} L${cx},${cy + s} L${cx + s},${cy - s}`);
    else if (kind === 1) p.push(`M${cx},${cy - s} L${cx},${cy + s} M${cx - s},${cy} L${cx + s},${cy - s}`);
    else if (kind === 2) p.push(`M${cx - s},${cy + s} L${cx},${cy - s} L${cx + s},${cy + s} M${cx - s * 0.6},${cy + s * 0.2} L${cx + s * 0.6},${cy + s * 0.2}`);
    else p.push(`M${cx - s},${cy - s} L${cx + s},${cy + s} M${cx + s},${cy - s} L${cx - s},${cy + s}`);
  }
  return p;
};
export const RitualSymbol: React.FC<{x: number; y: number; size: number; t: number; at: number; dur?: number; color: string; seed?: number}> = ({x, y, size, t, at, dur = 1.4, color, seed = 1}) => {
  if (t < at) return null;
  const paths = SYMBOL_PATHS(`s${seed}`);
  return (
    <svg viewBox="0 0 100 100" style={{position: 'absolute', left: x - size / 2, top: y - size / 2, width: size, height: size, transform: `rotate(${(t - at) * 6}deg)`}}>
      {paths.map((d, i) => {
        const p0 = at + (i / paths.length) * dur * 0.75;
        const p = clamp((t - p0) / (dur * 0.3));
        return <path key={i} d={d} pathLength={1} fill="none" stroke={color} strokeWidth={i < 2 ? 0.9 : 0.75} strokeLinecap="round" strokeLinejoin="round"
          strokeDasharray="1 1" strokeDashoffset={1 - p} />;
      })}
    </svg>
  );
};

// ---------- grade fina ----------
const Grid: React.FC<{color: string; t: number}> = ({color, t}) => (
  <svg width={W * 1.6} height={H * 1.6} style={{position: 'absolute', left: -W * 0.3, top: -H * 0.3, opacity: 0.35}}>
    {Array.from({length: 30}).map((_, i) => <line key={'v' + i} x1={i * 60 + (t * 10) % 60} y1={0} x2={i * 60 + (t * 10) % 60} y2={H * 1.6} stroke={color} strokeWidth={2} />)}
    {Array.from({length: 52}).map((_, i) => <line key={'h' + i} x1={0} y1={i * 60} x2={W * 1.6} y2={i * 60} stroke={color} strokeWidth={2} />)}
  </svg>
);

// ---------- poeira / partículas ----------
const Dust: React.FC<{n: number; seed: number; t: number; color: string}> = ({n, seed, t, color}) => (
  <>
    {Array.from({length: n}).map((_, i) => {
      const x0 = random(`dx${seed}${i}`) * W, y0 = random(`dy${seed}${i}`) * H, s = 3 + random(`ds${seed}${i}`) * 6;
      const vy = 20 + random(`dv${seed}${i}`) * 40;
      const x = x0 + Math.sin(t * 0.8 + i) * 18, y = ((y0 - t * vy) % H + H) % H;
      return <div key={i} style={{position: 'absolute', left: x, top: y, width: s, height: s, background: color, opacity: 0.55 + 0.4 * Math.sin(t * 2 + i), borderRadius: i % 3 ? 0 : s}} />;
    })}
  </>
);

// ---------- fumaça ----------
const Smoke: React.FC<{seed: number; t: number; bg: Bg}> = ({seed, t, bg}) => {
  const c = bg === 'gray' ? '28,28,28' : '237,237,237';
  return (
    <>
      {Array.from({length: 6}).map((_, i) => {
        const x = random(`sx${seed}${i}`) * W + t * (18 + 10 * i) * (i % 2 ? 1 : -1), y = 900 + random(`sy${seed}${i}`) * 900 - t * 22;
        const r = 380 + random(`sr${seed}${i}`) * 300;
        return <div key={i} style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%',
          background: `radial-gradient(circle, rgba(${c},0.22) 0%, rgba(${c},0.0) 65%)`}} />;
      })}
    </>
  );
};

// ---------- número gigante / logo / linha tracejada / barraca ----------
const BigNum: React.FC<{L: Extract<Layer, {k: 'num'}>; t: number; bg: Bg}> = ({L, t, bg}) => {
  if (t < L.at) return null;
  const p = clamp((t - L.at) * FPS / 5);
  return (
    <div style={{position: 'absolute', left: L.x, top: L.y, transform: `translate(-50%,-50%) scale(${0.9 + 0.1 * p}, ${0.9 + 0.1 * p})`, filter: `blur(${12 * (1 - p)}px)`, opacity: 0.6 + 0.4 * p}}>
      <div style={{font: fontCss('P', L.size), color: ink(bg), lineHeight: 0.8, transform: 'scaleX(0.8)'}}>{L.text}</div>
    </div>
  );
};
const Logo: React.FC<{L: Extract<Layer, {k: 'logo'}>; t: number; bg: Bg}> = ({L, t, bg}) => {
  if (t < L.at) return null;
  const p = clamp((t - L.at) * FPS / 7);
  const file = bg === 'red' ? 'netflix_light.svg' : 'netflix_red.svg';
  return <Img src={staticFile(`img/${file}`)} style={{position: 'absolute', left: L.x - L.w / 2, top: L.y, width: L.w, transform: `scale(${0.6 + 0.4 * backOut(p)})`, filter: `blur(${10 * (1 - p)}px)`}} />;
};
const Dash: React.FC<{L: Extract<Layer, {k: 'dash'}>; t: number; bg: Bg}> = ({L, t, bg}) => {
  if (t < L.at) return null;
  const p = eout((t - L.at) / (L.dur ?? 0.4));
  const mx = (L.x1 + L.x2) / 2 - 160, my = (L.y1 + L.y2) / 2;
  const d = `M${L.x1},${L.y1} Q${mx},${my} ${L.x2},${L.y2}`;
  const id = `m${Math.round(L.at * 100)}`;
  return (
    <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
      <defs><mask id={id}><path d={d} pathLength={1} stroke="#fff" strokeWidth={30} fill="none" strokeDasharray="1 1" strokeDashoffset={1 - p} /></mask></defs>
      <path d={d} stroke={ink(bg)} strokeWidth={9} fill="none" strokeDasharray="26 18" strokeLinecap="round" mask={`url(#${id})`} />
      {p > 0.98 ? <circle cx={L.x2} cy={L.y2} r={14} fill={ink(bg)} /> : null}
    </svg>
  );
};
const Tent: React.FC<{L: Extract<Layer, {k: 'tent'}>}> = ({L}) => (
  <svg viewBox="0 0 100 70" style={{position: 'absolute', left: L.x - L.w / 2, top: L.y - L.w * 0.7, width: L.w}}>
    <polygon points="50,2 98,68 2,68" fill={COL.black} />
    <polygon points="50,22 62,68 38,68" fill={COL.yellow} />
  </svg>
);

// ---------- TV antiga recortada ----------
const TV: React.FC<{L: Extract<Layer, {k: 'tv'}>; t: number}> = ({L, t}) => {
  if (t > L.until + 0.12) return null;
  const off = clamp((t - L.until) / 0.12); // desliga: tela colapsa numa linha
  const sw = L.w * 0.78, sh = sw * 1.25;
  return (
    <div style={{position: 'absolute', left: L.x - L.w / 2, top: L.y - L.w * 0.75, width: L.w, height: L.w * 1.5}}>
      <svg viewBox="0 0 100 150" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
        <line x1="40" y1="16" x2="22" y2="0" stroke={COL.black} strokeWidth={2.4} /><line x1="60" y1="16" x2="80" y2="1" stroke={COL.black} strokeWidth={2.4} />
        <rect x="2" y="15" width="96" height="128" rx="9" fill={COL.black} />
        <rect x="6" y="19" width="88" height="120" rx="7" fill={COL.gray} />
        <circle cx="30" cy="146" r="0" />
      </svg>
      <div style={{position: 'absolute', left: (L.w - sw) / 2, top: L.w * 0.27, width: sw, height: sh, overflow: 'hidden', borderRadius: 26, background: COL.black,
        transform: `scale(${1 - off * 0.02}, ${1 - off * 0.985})`}}>
        <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, transform: `scale(${sw / W})`, transformOrigin: '0 0'}}>{L.render()}</div>
        <div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(0deg, rgba(28,28,28,.28) 0px, rgba(28,28,28,.28) 3px, transparent 3px, transparent 7px)'}} />
      </div>
    </div>
  );
};

// ---------- texto grande palavra-por-palavra ----------
const TextBlock: React.FC<{B: Block; T: number}> = ({B, T}) => {
  if (!B.lines) return null;
  const end = B.textTo ?? B.to;
  if (T >= end) return null;
  const exitP = clamp((T - (end - 5 / FPS)) * FPS / 5);
  let idx = 0;
  return (
    <div style={{position: 'absolute', left: SAFE.left, top: B.textTop ?? 362, width: TEXT_W, perspective: exitP > 0 ? 900 : undefined}}>
      {B.lines.map((line, li) => {
        // auto-ajuste: a linha nunca passa da largura útil
        const widths = line.map((k) => measure(k.t, k.f, k.s));
        const gap = 18;
        const total = widths.reduce((a, b) => a + b, 0) + gap * (line.length - 1);
        const fit = Math.min(1, TEXT_W / total);
        const maxS = Math.max(...line.map((k) => k.s)) * fit;
        return (
          <div key={li} style={{display: 'flex', alignItems: 'baseline', gap: gap * fit, whiteSpace: 'nowrap', marginTop: li ? (line.some((k) => k.f === 'A') ? maxS * 0.05 : -maxS * 0.04) : 0}}>
            {line.map((k, ki) => {
              const i = idx++;
              const s = k.s * fit, w = widths[ki] * fit;
              const shown = T >= k.at;
              const p = k.at <= 0.001 && T >= 0 ? 1 : clamp((T - k.at) * FPS / 4.5);
              const color = k.hl ? hlc(B.bg) : ink(B.bg);
              const ex = eio(clamp(exitP * 1.6 - i * 0.08));
              const exitTf = ex <= 0 ? '' : B.exit === 'push' ? `translateX(${-ex * 1300}px)` : `rotateX(${ex * 90}deg)`;
              return (
                <div key={ki} style={{width: w, flex: 'none', opacity: shown ? 0.6 + 0.4 * p : 0, filter: shown && p < 1 ? `blur(${12 * (1 - p)}px) grayscale(${0.4 * (1 - p)})` : undefined,
                  transform: `${exitTf} scale(${0.9 + 0.1 * p})`, transformOrigin: '50% 100%', backfaceVisibility: ex > 0 ? 'hidden' : undefined}}>
                  <div style={{font: fontCss(k.f, s), color, lineHeight: k.f === 'A' ? 1.08 : 1.0, transform: k.f === 'P' ? 'scaleX(0.8)' : undefined, transformOrigin: '0 0', letterSpacing: k.f === 'A' ? '-0.005em' : '-0.01em',
                    textTransform: k.f === 'A' ? 'uppercase' : undefined}}>{k.t}</div>
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

// ---------- render de uma cena ----------
export type Cam = {x: number; y: number; z: number};
export const sceneCam = (S: Scene, T: number): Cam => {
  const u = clamp((T - S.from) / (S.to - S.from));
  const push = S.push ?? 85, drift = S.drift ?? 46;
  return {x: S.dir * (-drift + 2 * drift * eio(u)), y: -S.dir * 18 * eio(u), z: push * eio(u)};
};
export const blockAt = (S: Scene, T: number) => (T < S.blocks[0].from ? S.blocks[0] : S.blocks.find((b) => T >= b.from && T < b.to) ?? S.blocks[S.blocks.length - 1]);

export const SceneView: React.FC<{S: Scene; T: number; camOff?: Partial<Cam>; spread?: number; extraFilter?: string; scale?: number}> = ({S, T, camOff = {}, spread = 1, extraFilter, scale = 1}) => {
  const B = blockAt(S, T);
  const c = sceneCam(S, T);
  const cam = {x: c.x + (camOff.x ?? 0), y: c.y + (camOff.y ?? 0), z: c.z + (camOff.z ?? 0)};
  const t = T; // tempo global (animações contínuas)
  const ord = (L: Layer) => ('z' in L ? (L as any).z : -300);
  const layers = [...B.layers];
  if (!layers.some((l) => l.k === 'text')) layers.push({k: 'text'});
  layers.sort((a, b) => ord(a) - ord(b));
  return (
    <AbsoluteFill style={{background: COL[B.bg], perspective: P, perspectiveOrigin: '50% 50%', overflow: 'hidden', filter: extraFilter, transform: scale !== 1 ? `scale(${scale})` : undefined}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, transformStyle: 'preserve-3d', transform: `translate3d(${-cam.x}px, ${-cam.y}px, ${cam.z}px)`}}>
        {layers.map((L, i) => {
          const pl = (z: number, child: React.ReactNode, blur = 0) => <Plane key={i} z={z} camZ={cam.z} spread={spread} blur={blur}>{child}</Plane>;
          switch (L.k) {
            case 'cut':
              if ((L.from !== undefined && T < L.from) || (L.to !== undefined && T >= L.to)) return null;
              return pl(L.z, <Cut L={L} t={t} blurred={L.z > 100} />, L.blur ?? (L.z > 100 && !MAN[L.src + '_b'] ? 8 : 0));
            case 'star': return pl(L.z, <Star L={L} t={t} />);
            case 'flames': return pl(L.z, <Flames L={L} t={t} />);
            case 'symbol': return pl(L.z, <RitualSymbol x={L.x} y={L.y} size={L.size} t={t} at={L.at} dur={L.dur} color={L.color ?? ink(B.bg)} seed={L.seed} />);
            case 'grid': return pl(L.z, <Grid color={ink(B.bg)} t={t} />);
            case 'dust': return pl(L.z, <Dust n={L.n ?? 26} seed={L.seed ?? 1} t={t} color={B.bg === 'gray' ? COL.black : COL.gray} />);
            case 'smoke': return pl(L.z, <Smoke seed={L.seed ?? 1} t={t} bg={B.bg} />);
            case 'num': return pl(L.z, <BigNum L={L} t={t} bg={B.bg} />);
            case 'logo': return pl(L.z, <Logo L={L} t={t} bg={B.bg} />);
            case 'dash': return pl(L.z, <Dash L={L} t={t} bg={B.bg} />);
            case 'tent': return pl(L.z, <Tent L={L} />);
            case 'tv': return pl(L.z, <TV L={L} t={t} />);
            case 'text': return pl(L.z ?? -300, <TextBlock B={B} T={T} />);
            case 'forest': {
              // abertura: a câmera voa por dentro de uma floresta de recortes (as folhas passam pela câmera)
              const tt = T - S.from;
              const g = tt >= 0 ? eout(tt / 0.95) : ein(-tt / 0.6) * -0.0; // t<0: remontagem (ver loop)
              return <React.Fragment key={i}>{L.items.map((it, j) => {
                const zt = it.z + 1100 * eout(tt / 0.6);
                const zz = tt < 0 ? it.z + 1100 * ein(clamp(-tt / 0.5)) : zt;
                return <Plane key={j} z={it.z} camZ={cam.z} spread={spread} zOverride={zz}>
                  <Cut L={{k: 'cut', src: it.src, x: it.x, y: it.y, h: it.h, z: it.z, flip: it.flip, rot: it.rot, anim: 'sway'}} t={t} blurred />
                </Plane>;
              })}</React.Fragment>;
            }
          }
        })}
      </div>
    </AbsoluteFill>
  );
};
