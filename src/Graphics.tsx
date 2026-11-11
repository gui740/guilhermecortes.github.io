import React from 'react';
import {interpolate, random, useCurrentFrame, Easing, spring, useVideoConfig} from 'remotion';
import {C} from './theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Grade fina desfocada surgindo no fundo (abertura)
export const Grid: React.FC<{color: string}> = ({color}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 12], [0, 0.22], clamp);
  const off = f * 0.8;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: o, filter: 'blur(1.6px)'}}>
      <defs>
        <pattern id="grid" width={90} height={90} patternUnits="userSpaceOnUse" patternTransform={`translate(${off} ${off * 0.5})`}>
          <path d="M 90 0 L 0 0 0 90" fill="none" stroke={color} strokeWidth={2} />
        </pattern>
      </defs>
      <rect width={1080} height={1920} fill="url(#grid)" />
    </svg>
  );
};

// Estrela amarela de pontas atrás do Buddy (revelação do título)
export const Star: React.FC<{cx: number; cy: number; r: number; still?: boolean}> = ({cx, cy, r, still}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = still ? 1 : spring({frame: f, fps, config: {damping: 11, stiffness: 140}});
  const n = 14, pts: string[] = [];
  for (let i = 0; i < n * 2; i++) {
    const rr = i % 2 === 0 ? r : r * 0.62;
    const a = (Math.PI * i) / n - Math.PI / 2;
    pts.push(`${cx + rr * Math.cos(a)},${cy + rr * Math.sin(a)}`);
  }
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
      <g transform={`rotate(${f * 0.9} ${cx} ${cy}) translate(${cx} ${cy}) scale(${s}) translate(${-cx} ${-cy})`}>
        <polygon points={pts.join(' ')} fill={C.Y} stroke={C.K} strokeWidth={6} strokeLinejoin="round" />
      </g>
    </svg>
  );
};

// Chuvisco (ruído animado)
export const Static: React.FC<{opacity: number; w?: number; h?: number; id: string}> = ({opacity, w = 1080, h = 1920, id}) => {
  const f = useCurrentFrame();
  return (
    <svg width={w} height={h} style={{position: 'absolute', inset: 0, opacity, mixBlendMode: 'screen', pointerEvents: 'none'}}>
      <filter id={id}>
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={f % 97} />
        <feColorMatrix type="saturate" values="0" />
        <feComponentTransfer><feFuncA type="linear" slope="1" /></feComponentTransfer>
      </filter>
      <rect width={w} height={h} filter={`url(#${id})`} />
    </svg>
  );
};

// Granulado leve em tela cheia para unificar
export const Grain: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: 0.07, mixBlendMode: 'multiply', pointerEvents: 'none'}}>
      <filter id="grainf"><feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves={1} seed={(f * 7) % 101} /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width={1080} height={1920} filter="url(#grainf)" />
    </svg>
  );
};

// Moldura de TV antiga (tubo) — o conteúdo vai dentro da tela
export const TV: React.FC<{children: React.ReactNode; x: number; y: number; w: number; h: number}> = ({children, x, y, w, h}) => {
  const f = useCurrentFrame();
  const sx = x + 56, sy = y + 56, sw = w - 112 - 150, sh = h - 112;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920}}>
      {/* antenas */}
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <line x1={x + w * 0.42} y1={y} x2={x + w * 0.24} y2={y - 190} stroke={C.K} strokeWidth={12} strokeLinecap="round" />
        <line x1={x + w * 0.46} y1={y} x2={x + w * 0.66} y2={y - 170} stroke={C.K} strokeWidth={12} strokeLinecap="round" />
        <circle cx={x + w * 0.24} cy={y - 190} r={16} fill={C.R} />
        <circle cx={x + w * 0.66} cy={y - 170} r={16} fill={C.R} />
        <rect x={x + 60} y={y + h - 8} width={70} height={46} fill={C.K} />
        <rect x={x + w - 130} y={y + h - 8} width={70} height={46} fill={C.K} />
      </svg>
      <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: C.K, borderRadius: 60, boxShadow: '0 0 0 8px #EDEDED, 0 0 0 14px #1C1C1C'}} />
      {/* botões */}
      <div style={{position: 'absolute', left: x + w - 130, top: y + 120, width: 80, height: 80, borderRadius: 40, background: C.Y}} />
      <div style={{position: 'absolute', left: x + w - 130, top: y + 240, width: 80, height: 80, borderRadius: 40, background: C.R}} />
      {[0, 1, 2, 3].map((i) => <div key={i} style={{position: 'absolute', left: x + w - 135, top: y + 380 + i * 34, width: 90, height: 12, borderRadius: 6, background: '#3a3a3a'}} />)}
      <div style={{position: 'absolute', left: sx, top: sy, width: sw, height: sh, borderRadius: '42px / 60px', overflow: 'hidden', background: '#2a2a2a'}}>
        {children}
        <Static opacity={0.38} w={sw} h={sh} id="tvst" />
        {/* scanlines */}
        <div style={{position: 'absolute', inset: 0, backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.28) 0 3px, transparent 3px 7px)', transform: `translateY(${(f * 3) % 7}px)`}} />
        <div style={{position: 'absolute', inset: 0, boxShadow: 'inset 0 0 90px 30px rgba(0,0,0,0.7)', borderRadius: '42px / 60px'}} />
      </div>
    </div>
  );
};

// Cursor de mãozinha
export const Hand: React.FC<{x: number; y: number; press: number; scale?: number}> = ({x, y, press, scale = 1}) => (
  <svg width={150} height={170} viewBox="0 0 32 36" style={{position: 'absolute', left: x - 30 * scale, top: y - 6 * scale, transform: `scale(${scale * (1 - press * 0.15)})`, transformOrigin: '30% 5%', overflow: 'visible'}}>
    <path d="M11 2.5c1.4 0 2.5 1.1 2.5 2.5v9.2l1-.1V12c0-1.4 1.1-2.4 2.4-2.4s2.4 1 2.4 2.4v2.2l.9-.1c.3-1.1 1.3-1.9 2.4-1.9 1.4 0 2.4 1.1 2.4 2.4v1.4c.4-.2.9-.3 1.4-.3 1.4 0 2.4 1.1 2.4 2.4v6.4c0 5.4-4 9.5-9.4 9.5h-1.6c-3 0-5.7-1.5-7.4-4l-5.5-8c-.7-1.1-.5-2.6.6-3.3 1-.7 2.4-.5 3.2.4l1.3 1.6V5c0-1.4 1.1-2.5 2.5-2.5z" fill="#FFFFFF" stroke="#1C1C1C" strokeWidth={1.8} strokeLinejoin="round" />
    {press > 0.05 && (
      <g stroke="#F2E63A" strokeWidth={2} strokeLinecap="round" opacity={press}>
        <line x1={11} y1={-1} x2={11} y2={-5} /><line x1={5} y1={1} x2={2.5} y2={-2} /><line x1={17} y1={1} x2={19.5} y2={-2} />
      </g>
    )}
  </svg>
);

// Tesoura
export const Scissors: React.FC<{x: number; y: number; open: number}> = ({x, y, open}) => (
  <svg width={190} height={140} viewBox="-50 -35 100 70" style={{position: 'absolute', left: x - 95, top: y - 70, overflow: 'visible'}}>
    <g transform={`rotate(${-open * 14})`}>
      <path d="M-4 -3 L46 -10 L46 -6 L-2 3 Z" fill="#EDEDED" stroke="#1C1C1C" strokeWidth={2.5} strokeLinejoin="round" />
      <circle cx={-22} cy={14} r={11} fill="none" stroke={C.R} strokeWidth={6} />
      <line x1={-14} y1={7} x2={-2} y2={0} stroke={C.R} strokeWidth={7} strokeLinecap="round" />
    </g>
    <g transform={`rotate(${open * 14})`}>
      <path d="M-4 3 L46 10 L46 6 L-2 -3 Z" fill="#EDEDED" stroke="#1C1C1C" strokeWidth={2.5} strokeLinejoin="round" />
      <circle cx={-22} cy={-14} r={11} fill="none" stroke={C.R} strokeWidth={6} />
      <line x1={-14} y1={-7} x2={-2} y2={0} stroke={C.R} strokeWidth={7} strokeLinecap="round" />
    </g>
    <circle cx={0} cy={0} r={3.5} fill="#1C1C1C" />
  </svg>
);

// Borracha
export const Eraser: React.FC<{x: number; y: number; rot: number}> = ({x, y, rot}) => (
  <svg width={200} height={120} viewBox="0 0 100 60" style={{position: 'absolute', left: x - 30, top: y - 90, transform: `rotate(${rot}deg)`, transformOrigin: '15% 100%', overflow: 'visible'}}>
    <g transform="rotate(-25 50 30)">
      <rect x={10} y={14} width={78} height={32} rx={6} fill={C.R} stroke="#1C1C1C" strokeWidth={3} />
      <rect x={10} y={14} width={30} height={32} rx={6} fill="#EDEDED" stroke="#1C1C1C" strokeWidth={3} />
    </g>
  </svg>
);

// Linha tracejada que se desenha
export const DashLine: React.FC<{d: string; progress: number; color: string; len?: number}> = ({d, progress, color, len = 1400}) => (
  <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
    <defs>
      <mask id="dlm"><path d={d} fill="none" stroke="#fff" strokeWidth={30} strokeDasharray={len} strokeDashoffset={len * (1 - progress)} /></mask>
    </defs>
    <path d={d} fill="none" stroke={color} strokeWidth={10} strokeDasharray="28 20" strokeLinecap="round" mask="url(#dlm)" />
  </svg>
);

export const useEase = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
export const rnd = random;
