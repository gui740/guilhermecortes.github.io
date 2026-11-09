import React from 'react';
import {useCurrentFrame} from 'remotion';
import {prog, rnd, suave, Pt} from './util';
import {COR} from './fonts';

/** Rabiscos à mão: círculo (com sobreposição), X, sublinhado ondulado. */
export const Scribble: React.FC<{tipo: 'circulo' | 'x' | 'sublinhado'; x: number; y: number; w: number; h?: number; delay?: number; dur?: number; cor?: string; espessura?: number; seed?: string; rot?: number}> = ({
  tipo, x, y, w, h = w * 0.6, delay = 0, dur = 14, cor = COR.vermelho, espessura = 8, seed = 's', rot = 0,
}) => {
  const f = useCurrentFrame();
  if (f < delay) return null;
  const p = prog(f, delay, delay + dur);
  let ds: string[] = [];
  if (tipo === 'circulo') {
    const pts: Pt[] = [];
    const voltas = 1.18, n = 48;
    for (let i = 0; i <= n; i++) {
      const t = (i / n) * voltas * Math.PI * 2 - 2.2;
      const k = 1 + (rnd(`${seed}${i}`) - 0.5) * 0.06 + i * 0.0012;
      pts.push({x: x + Math.cos(t) * (w / 2) * k, y: y + Math.sin(t) * (h / 2) * k});
    }
    ds = [suave(pts)];
  } else if (tipo === 'x') {
    const a = w / 2, b = h / 2;
    ds = [
      `M ${x - a} ${y - b} Q ${x + rnd(seed + 'q', -10, 10)} ${y + rnd(seed + 'w', -10, 10)} ${x + a} ${y + b}`,
      `M ${x + a} ${y - b * 0.9} Q ${x + rnd(seed + 'e', -10, 10)} ${y + rnd(seed + 'r', -10, 10)} ${x - a * 0.95} ${y + b}`,
    ];
  } else {
    const pts: Pt[] = [];
    for (let i = 0; i <= 12; i++) pts.push({x: x - w / 2 + (w * i) / 12, y: y + Math.sin(i * 1.3) * 5 + rnd(seed + i, -3, 3)});
    ds = [suave(pts)];
  }
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', zIndex: 58, transform: rot ? `rotate(${rot}deg)` : undefined, transformOrigin: `${x}px ${y}px`}}>
      <g style={{filter: 'drop-shadow(1px 2px 1px rgba(0,0,0,0.45))'}}>
        {ds.map((d, i) => {
          const pi = Math.max(0, Math.min(1, p * ds.length - i));
          return <path key={i} d={d} fill="none" stroke={cor} strokeWidth={espessura} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - pi} />;
        })}
      </g>
    </svg>
  );
};
