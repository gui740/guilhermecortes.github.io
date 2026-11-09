import React from 'react';
import {AbsoluteFill, random, useCurrentFrame} from 'remotion';
import {C} from '../theme';

const PARTICLES = new Array(70).fill(0).map((_, i) => ({
  x: random(`px${i}`) * 1080,
  y: random(`py${i}`) * 1920,
  r: 1 + random(`pr${i}`) * 3.2,
  speed: 0.25 + random(`ps${i}`) * 0.9,
  drift: random(`pd${i}`) * Math.PI * 2,
  alpha: 0.15 + random(`pa${i}`) * 0.45,
}));

const RAYS = new Array(6).fill(0).map((_, i) => ({
  x: 80 + i * 190 + random(`rx${i}`) * 80,
  w: 60 + random(`rw${i}`) * 140,
  phase: random(`rp${i}`) * 10,
}));

/** Fundo do mar: gradiente petróleo, cáusticas, raios de luz, partículas e vinheta. */
export const Ocean: React.FC<{tint?: number}> = ({tint = 0}) => {
  const f = useCurrentFrame();
  const t = f / 30;
  return (
    <AbsoluteFill style={{backgroundColor: C.abyss, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(120% 70% at 50% -5%, ${C.teal} 0%, ${C.petrol} 32%, ${C.deep} 62%, ${C.abyss} 100%)`,
        }}
      />
      {/* raios de luz */}
      <AbsoluteFill style={{mixBlendMode: 'screen', opacity: 0.55}}>
        {RAYS.map((r, i) => {
          const sway = Math.sin(t * 0.6 + r.phase) * 50;
          const op = 0.08 + 0.07 * Math.sin(t * 0.9 + r.phase * 2);
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                top: -200,
                left: r.x + sway,
                width: r.w,
                height: 1500,
                transform: `rotate(${12 + Math.sin(r.phase) * 6}deg)`,
                transformOrigin: 'top center',
                background: `linear-gradient(180deg, rgba(160,230,235,${op}) 0%, rgba(160,230,235,0) 100%)`,
                filter: 'blur(18px)',
              }}
            />
          );
        })}
      </AbsoluteFill>
      {/* cáusticas */}
      <svg
        width={1080}
        height={1920}
        style={{position: 'absolute', inset: 0, mixBlendMode: 'screen', opacity: 0.16}}
      >
        <defs>
          <filter id="caustic" x="0" y="0" width="100%" height="100%">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.022 0.04"
              numOctaves={2}
              seed={(Math.floor(f / 2) % 40) + 1}
              result="n"
            />
            <feColorMatrix
              type="matrix"
              values="0 0 0 0 0.55  0 0 0 0 0.9  0 0 0 0 0.92  0 0 0 9 -4.6"
            />
            <feGaussianBlur stdDeviation="1.4" />
          </filter>
          <linearGradient id="cfade" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#fff" stopOpacity="1" />
            <stop offset="0.55" stopColor="#fff" stopOpacity="0.15" />
            <stop offset="1" stopColor="#fff" stopOpacity="0" />
          </linearGradient>
          <mask id="cmask">
            <rect width="1080" height="1920" fill="url(#cfade)" />
          </mask>
        </defs>
        <rect width="1080" height="1920" filter="url(#caustic)" mask="url(#cmask)" />
      </svg>
      {/* partículas */}
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        {PARTICLES.map((p, i) => {
          const y = (((p.y - f * p.speed * 1.4) % 1920) + 1920) % 1920;
          const x = p.x + Math.sin(t * 0.7 + p.drift) * 18;
          return <circle key={i} cx={x} cy={y} r={p.r} fill={`rgba(210,240,240,${p.alpha})`} />;
        })}
      </svg>
      {tint > 0 ? (
        <AbsoluteFill style={{background: C.blood, mixBlendMode: 'multiply', opacity: tint}} />
      ) : null}
      {/* vinheta */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(90% 60% at 50% 45%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.75) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};
