import React from 'react';
import {useCurrentFrame} from 'remotion';
import {prog, rnd} from './util';

/** Pedaço de fita adesiva semi-transparente com pontas serrilhadas. Coordenadas absolutas (centro). */
export const Tape: React.FC<{x: number; y: number; w?: number; h?: number; rot?: number; delay?: number; cor?: string; seed?: string}> = ({
  x, y, w = 150, h = 46, rot = 0, delay = 0, cor = 'rgba(232,222,186,0.62)', seed = 't',
}) => {
  const f = useCurrentFrame();
  if (f < delay) return null;
  const p = prog(f, delay, delay + 6);
  const dentes = 7;
  const pts: string[] = [];
  for (let i = 0; i <= dentes; i++) pts.push(`${(i % 2 ? 4 : 0) + rnd(seed + 'a' + i, 0, 2)}% ${(i / dentes) * 100}%`);
  for (let i = dentes; i >= 0; i--) pts.push(`${100 - (i % 2 ? 4 : 0) - rnd(seed + 'b' + i, 0, 2)}% ${(i / dentes) * 100}%`);
  return (
    <div
      style={{
        position: 'absolute', left: x, top: y, width: w, height: h,
        transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${1.15 - 0.15 * p})`,
        opacity: p, background: `linear-gradient(180deg, rgba(255,255,255,0.18), rgba(0,0,0,0.05)), ${cor}`,
        clipPath: `polygon(${pts.join(',')})`, boxShadow: '0 1px 2px rgba(0,0,0,0.25)', zIndex: 50,
      }}
    />
  );
};
