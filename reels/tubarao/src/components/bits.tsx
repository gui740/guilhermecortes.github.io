import React from 'react';
import {Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {BODY, C, HEAD, textShadow} from '../theme';
import type {Stream} from '../data';

/** Barbatana de tubarão (silhueta) */
export const Fin: React.FC<{size?: number; color?: string; style?: React.CSSProperties}> = ({
  size = 300,
  color = '#061418',
  style,
}) => (
  <svg width={size} height={size * 0.8} viewBox="0 0 100 80" style={style}>
    <path
      d="M2 78 C 30 70, 46 40, 52 2 C 60 26, 72 52, 98 78 Z"
      fill={color}
      stroke="rgba(160,220,225,0.35)"
      strokeWidth={0.8}
    />
    <path d="M52 2 C 56 30, 64 55, 80 78" stroke="rgba(255,255,255,0.08)" strokeWidth={3} fill="none" />
  </svg>
);

export const useIn = (delay: number, damping = 14, durationInFrames?: number) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - delay, fps, config: {damping, mass: 0.7}, durationInFrames});
};

/** Contador animado (número grande) */
export const Counter: React.FC<{
  from?: number;
  to: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  start: number;
  duration?: number;
  size?: number;
  color?: string;
}> = ({from = 0, to, decimals = 0, prefix = '', suffix = '', start, duration = 40, size = 170, color = C.white}) => {
  const f = useCurrentFrame();
  const v = interpolate(f, [start, start + duration], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const txt = v.toLocaleString('pt-BR', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
  const done = f >= start + duration;
  const punch = done ? interpolate(f, [start + duration, start + duration + 8], [1.12, 1], {extrapolateRight: 'clamp'}) : 1;
  return (
    <div
      style={{
        fontFamily: HEAD,
        fontSize: size,
        lineHeight: 1,
        color,
        textShadow,
        transform: `scale(${punch})`,
        transformOrigin: 'left center',
        whiteSpace: 'nowrap',
        fontVariantNumeric: 'tabular-nums',
      }}
    >
      <span style={{fontSize: size * 0.5, verticalAlign: '0.6em', color: C.foam}}>{prefix}</span>
      {txt}
      <span style={{fontSize: size * 0.55, color: C.bloodBright}}>{suffix}</span>
    </div>
  );
};

/** Pílula vermelha de rótulo */
export const Tag: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div
    style={{
      display: 'inline-block',
      background: C.blood,
      color: C.white,
      fontFamily: BODY,
      fontWeight: 900,
      fontSize: 30,
      letterSpacing: 2,
      padding: '10px 20px 9px',
      borderRadius: 6,
      boxShadow: '0 6px 24px rgba(208,18,27,0.45)',
      ...style,
    }}
  >
    {children}
  </div>
);

/** Selo ONDE ASSISTIR */
export const StreamBadge: React.FC<{streams: Stream[]; start: number}> = ({streams, start}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: f - start, fps, config: {damping: 12, mass: 0.6}});
  const x = interpolate(p, [0, 1], [-900, 0]);
  return (
    <div style={{transform: `translateX(${x}px)`, opacity: p > 0.01 ? 1 : 0}}>
      <div
        style={{
          background: 'rgba(2,10,13,0.82)',
          border: `3px solid ${C.blood}`,
          borderRadius: 22,
          padding: '18px 24px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.6), inset 0 0 40px rgba(208,18,27,0.18)',
        }}
      >
        <div
          style={{
            fontFamily: HEAD,
            fontSize: 52,
            color: C.white,
            letterSpacing: 2,
            marginBottom: 10,
          }}
        >
          ONDE ASSISTIR <span style={{color: C.bloodBright}}>🩸</span>
        </div>
        {streams.map((s, i) => {
          const pi = spring({frame: f - start - 8 - i * 7, fps, config: {damping: 10, mass: 0.5}});
          return (
            <div
              key={s.name}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 22,
                marginTop: i ? 10 : 0,
                transform: `scale(${interpolate(pi, [0, 1], [0.4, 1])})`,
                transformOrigin: 'left center',
                opacity: pi,
              }}
            >
              <Img
                src={staticFile(s.logo)}
                style={{width: 88, height: 88, borderRadius: 16, boxShadow: '0 6px 18px rgba(0,0,0,0.5)'}}
              />
              <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 38, color: C.white, lineHeight: 1.15}}>
                {s.name}
              </div>
            </div>
          );
        })}
        <div style={{fontFamily: BODY, fontWeight: 500, fontSize: 24, color: C.muted, marginTop: 14}}>
          na assinatura · conferido em 09/11/2026
        </div>
      </div>
    </div>
  );
};

/** Texto que entra palavra por palavra */
export const WordsIn: React.FC<{
  text: string;
  start: number;
  every?: number;
  style?: React.CSSProperties;
  highlight?: string[];
}> = ({text, start, every = 3, style, highlight = []}) => {
  const f = useCurrentFrame();
  const words = text.split(' ');
  return (
    <div style={style}>
      {words.map((w, i) => {
        const p = interpolate(f, [start + i * every, start + i * every + 6], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const hl = highlight.includes(w.replace(/[.,?!:]/g, ''));
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              opacity: p,
              transform: `translateY(${(1 - p) * 26}px)`,
              color: hl ? C.bloodBright : undefined,
              marginRight: '0.26em',
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};
