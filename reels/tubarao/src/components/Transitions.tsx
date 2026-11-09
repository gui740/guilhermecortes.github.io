import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {C} from '../theme';
import {Fin} from './bits';

const ease = Easing.inOut(Easing.cubic);

/** Barbatana atravessa a tela e "corta" para a próxima cena (20 frames, corte no frame 10) */
export const FinWipe: React.FC = () => {
  const f = useCurrentFrame();
  const lead = interpolate(f, [0, 11], [-200, 1300], {extrapolateRight: 'clamp', easing: ease});
  const tail = interpolate(f, [9, 20], [-200, 1300], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const finX = interpolate(f, [0, 20], [-420, 1180], {easing: Easing.inOut(Easing.quad)});
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <svg width={1080} height={1920} style={{position: 'absolute'}}>
        <path
          d={`M${tail},0 L${lead},0 Q${lead + 80},960 ${lead},1920 L${tail},1920 Q${tail + 80},960 ${tail},0 Z`}
          fill={C.abyss}
        />
        <path
          d={`M${lead},0 Q${lead + 80},960 ${lead},1920`}
          stroke={C.blood}
          strokeWidth={10}
          fill="none"
          opacity={f < 12 ? 1 : 0}
        />
      </svg>
      <div style={{position: 'absolute', left: finX, top: 760}}>
        <Fin size={420} color="#071a1f" />
      </div>
      {/* espuma da barbatana */}
      <div
        style={{
          position: 'absolute',
          left: finX - 260,
          top: 1080,
          width: 600,
          height: 30,
          borderRadius: 30,
          background: 'linear-gradient(90deg, rgba(220,245,245,0) 0%, rgba(220,245,245,0.75) 100%)',
          filter: 'blur(6px)',
        }}
      />
    </AbsoluteFill>
  );
};

/** Mergulho: água escura sobe com bolhas (22 frames, corte no frame 11) */
export const Dive: React.FC = () => {
  const f = useCurrentFrame();
  const top = interpolate(f, [0, 11, 22], [1980, -120, -2200], {easing: ease});
  const bubbles = new Array(40).fill(0).map((_, i) => {
    const x = random(`bx${i}`) * 1080;
    const sp = 60 + random(`bs${i}`) * 90;
    const r = 6 + random(`br${i}`) * 26;
    const y = 2000 - (f + random(`bo${i}`) * 8) * sp;
    return <circle key={i} cx={x + Math.sin(f / 3 + i) * 12} cy={y} r={r} fill="none" stroke="rgba(220,245,245,0.7)" strokeWidth={3} />;
  });
  const wave = (y: number) =>
    `M0,${y} ` +
    new Array(13)
      .fill(0)
      .map((_, i) => `Q${i * 90 + 45},${y + (i % 2 ? -40 : 40) * Math.sin(f / 2)} ${(i + 1) * 90},${y}`)
      .join(' ');
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <svg width={1080} height={1920} style={{position: 'absolute'}}>
        <path d={`${wave(top)} L1080,${top + 2400} L0,${top + 2400} Z`} fill="#01080b" />
        <path d={wave(top)} stroke={C.foam} strokeOpacity={0.5} strokeWidth={6} fill="none" />
        {bubbles}
      </svg>
    </AbsoluteFill>
  );
};

const teeth = (y: number, flip: boolean) => {
  const n = 9;
  const w = 1080 / n;
  let d = flip ? `M0,1920 L0,${y}` : `M0,0 L0,${y}`;
  for (let i = 0; i < n; i++) {
    const h = 130 + (i % 2) * 40;
    d += ` L${i * w + w / 2},${flip ? y - h : y + h} L${(i + 1) * w},${y}`;
  }
  d += flip ? ' L1080,1920 Z' : ' L1080,0 Z';
  return d;
};

/** Mordida + glitch (18 frames, corte no frame 9) */
export const Bite: React.FC = () => {
  const f = useCurrentFrame();
  const close = interpolate(f, [0, 8, 10, 18], [0, 1, 1, 0], {easing: ease});
  const topY = interpolate(close, [0, 1], [-200, 900]);
  const botY = interpolate(close, [0, 1], [2120, 1020]);
  const flash = interpolate(f, [7, 9, 13], [0, 0.85, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const slices = new Array(7).fill(0).map((_, i) => {
    const on = f >= 5 && f <= 15 && random(`g${i}-${f}`) > 0.4;
    if (!on) return null;
    const y = random(`gy${i}-${f}`) * 1920;
    return (
      <div
        key={i}
        style={{
          position: 'absolute',
          left: (random(`gx${i}-${f}`) - 0.5) * 120,
          top: y,
          width: 1200,
          height: 12 + random(`gh${i}-${f}`) * 60,
          background: i % 2 ? 'rgba(255,42,51,0.55)' : 'rgba(120,240,255,0.35)',
          mixBlendMode: 'screen',
        }}
      />
    );
  });
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <svg width={1080} height={1920} style={{position: 'absolute'}}>
        <path d={teeth(topY, false)} fill="#f2efe6" stroke="#2a0507" strokeWidth={6} />
        <path d={teeth(botY, true)} fill="#f2efe6" stroke="#2a0507" strokeWidth={6} />
        <rect x={0} y={0} width={1080} height={Math.max(0, topY - 10)} fill={C.blood} />
        <rect x={0} y={botY + 10} width={1080} height={Math.max(0, 1920 - botY)} fill={C.blood} />
      </svg>
      {slices}
      <AbsoluteFill style={{background: C.bloodBright, opacity: flash, mixBlendMode: 'screen'}} />
    </AbsoluteFill>
  );
};
