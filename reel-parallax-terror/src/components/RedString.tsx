import React from 'react';
import {useCurrentFrame} from 'remotion';
import {prog, Pt, rnd} from './util';
import {COR} from './fonts';

const Alfinete: React.FC<{p: Pt; s: number}> = ({p, s}) =>
  s <= 0 ? null : (
    <g transform={`translate(${p.x} ${p.y}) scale(${s})`}>
      <ellipse cx={3} cy={5} rx={13} ry={9} fill="rgba(0,0,0,0.45)" />
      <circle r={12} fill={COR.vermelho} />
      <circle r={12} fill="url(#brilhoPino)" />
    </g>
  );

/** Barbante vermelho entre dois alfinetes, com caimento (gravidade). Se desenha em `dur` frames. */
export const RedString: React.FC<{de: Pt; ate: Pt; delay?: number; dur?: number; caimento?: number; seed?: string; pinos?: boolean}> = ({
  de, ate, delay = 0, dur = 15, caimento, seed = 'b', pinos = true,
}) => {
  const f = useCurrentFrame();
  if (f < delay - 4) return null;
  const p = prog(f, delay, delay + dur);
  const len = Math.hypot(ate.x - de.x, ate.y - de.y);
  const sag = caimento ?? len * 0.09 + rnd(seed, 0, 14);
  const c = {x: (de.x + ate.x) / 2, y: (de.y + ate.y) / 2 + sag};
  const d = `M ${de.x} ${de.y} Q ${c.x} ${c.y} ${ate.x} ${ate.y}`;
  const p1 = prog(f, delay - 4, delay + 2);
  const p2 = prog(f, delay + dur - 2, delay + dur + 4);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', zIndex: 55}}>
      <defs>
        <radialGradient id="brilhoPino" cx="35%" cy="30%" r="60%">
          <stop offset="0%" stopColor="rgba(255,255,255,0.75)" />
          <stop offset="40%" stopColor="rgba(255,255,255,0)" />
          <stop offset="100%" stopColor="rgba(0,0,0,0.35)" />
        </radialGradient>
      </defs>
      <path d={d} fill="none" stroke="rgba(0,0,0,0.4)" strokeWidth={6} transform="translate(3,6)" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} />
      <path d={d} fill="none" stroke={COR.sangue} strokeWidth={5.5} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} />
      <path d={d} fill="none" stroke="#d0303a" strokeWidth={2} strokeDasharray="5 7" strokeLinecap="round" opacity={p > 0.99 ? 0.8 : 0} />
      {pinos ? (
        <>
          <Alfinete p={de} s={p1} />
          <Alfinete p={ate} s={p2} />
        </>
      ) : null}
    </svg>
  );
};
