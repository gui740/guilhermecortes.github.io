import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {prog, rnd} from './util';
import {COR} from './fonts';
import {Easing} from 'remotion';

/** Transição de papel rasgado: a cena atual (children) rasga de cima a baixo e as duas metades
 *  se abrem (girando a partir da base), revelando o que está por baixo. */
export const TornReveal: React.FC<{inicio: number; dur: number; children: React.ReactNode}> = ({inicio, dur, children}) => {
  const f = useCurrentFrame();
  if (f < inicio) return <AbsoluteFill>{children}</AbsoluteFill>;
  const p = prog(f, inicio, inicio + dur, Easing.in(Easing.cubic));
  // linha do rasgo (x por y), irregular
  const N = 28;
  const linha = Array.from({length: N + 1}, (_, i) => ({y: (1920 * i) / N, x: 540 + Math.sin(i * 0.9) * 40 + rnd('rasgo' + i, -38, 38)}));
  const esq = `polygon(0px 0px, ${linha.map((q) => `${q.x.toFixed(0)}px ${q.y.toFixed(0)}px`).join(',')}, 0px 1920px)`;
  const dir = `polygon(1080px 0px, ${linha.map((q) => `${q.x.toFixed(0)}px ${q.y.toFixed(0)}px`).join(',')}, 1080px 1920px)`;
  const fibra = (lado: number) => (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
      <polyline points={linha.map((q, i) => `${(q.x + lado * (5 + rnd('fb' + i, 0, 6))).toFixed(0)},${q.y.toFixed(0)}`).join(' ')} fill="none" stroke={COR.papel} strokeWidth={16} strokeLinejoin="round" />
    </svg>
  );
  const ang = 26 * p, abre = 520 * p;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{clipPath: esq, transform: `translateX(${-abre}px) rotate(${-ang}deg)`, transformOrigin: '0px 1920px', filter: 'drop-shadow(10px 0 18px rgba(0,0,0,0.7))'}}>
        {children}
        {fibra(-1)}
      </AbsoluteFill>
      <AbsoluteFill style={{clipPath: dir, transform: `translateX(${abre}px) rotate(${ang}deg)`, transformOrigin: '1080px 1920px', filter: 'drop-shadow(-10px 0 18px rgba(0,0,0,0.7))'}}>
        {children}
        {fibra(1)}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
