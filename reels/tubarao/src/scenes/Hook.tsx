import React from 'react';
import {AbsoluteFill, interpolate, random, useCurrentFrame} from 'remotion';
import {BODY, C, HEAD, textShadow} from '../theme';
import {Fin, useIn} from '../components/bits';

/** 0–2,5s: gancho com sonar pulsando e barbatana rondando */
export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const p2 = useIn(40, 12);
  const p3 = useIn(80, 12);
  const p4 = useIn(112, 9);
  const jitter = f > 114 && f < 134 ? (random(`j${f}`) - 0.5) * 14 : 0;
  const finX = interpolate(f, [0, 180], [1100, -380]);
  return (
    <AbsoluteFill>
      {/* sonar */}
      <svg width={1080} height={1920} style={{position: 'absolute'}}>
        {[0, 1, 2].map((i) => {
          const q = ((f + i * 12) % 36) / 36;
          return (
            <circle
              key={i}
              cx={540}
              cy={900}
              r={60 + q * 640}
              fill="none"
              stroke={C.bloodBright}
              strokeWidth={4}
              opacity={(1 - q) * 0.55}
            />
          );
        })}
        <line x1={540} y1={900} x2={540 + Math.cos(f / 6) * 700} y2={900 + Math.sin(f / 6) * 700} stroke="rgba(255,42,51,0.25)" strokeWidth={3} />
      </svg>
      {/* linha d'água + barbatana rondando */}
      <div style={{position: 'absolute', left: finX, top: 1300, transform: 'scaleX(-1)'}}>
        <Fin size={260} />
      </div>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 1500,
          height: 6,
          background: 'linear-gradient(90deg, transparent, rgba(207,233,236,0.5), transparent)',
        }}
      />
      <div style={{position: 'absolute', left: 60, right: 150, top: 380, textShadow}}>
        <div style={{display: 'flex', alignItems: 'flex-end', gap: 24}}>
          <div style={{fontFamily: HEAD, fontSize: 400, lineHeight: 0.82, color: C.bloodBright}}>3</div>
          <div style={{fontFamily: HEAD, fontSize: 150, lineHeight: 0.9, color: C.white, paddingBottom: 6}}>
            FILMES
          </div>
        </div>
        <div
          style={{
            fontFamily: BODY,
            fontWeight: 900,
            fontSize: 66,
            lineHeight: 1.05,
            color: C.white,
            marginTop: 34,
            opacity: p2,
            transform: `translateY(${(1 - p2) * 40}px)`,
          }}
        >
          PRA VOCÊ NUNCA MAIS
        </div>
        <div
          style={{
            fontFamily: BODY,
            fontWeight: 900,
            fontSize: 66,
            lineHeight: 1.05,
            color: C.white,
            opacity: p3,
            transform: `translateY(${(1 - p3) * 40}px)`,
          }}
        >
          ENTRAR NO MAR
        </div>
        <div
          style={{
            fontFamily: HEAD,
            fontSize: 172,
            whiteSpace: 'nowrap',
            lineHeight: 1,
            marginTop: 10,
            color: C.white,
            opacity: p4,
            transform: `scale(${interpolate(p4, [0, 1], [1.6, 1])}) translateX(${jitter}px)`,
            transformOrigin: 'left center',
            position: 'relative',
          }}
        >
          <span style={{position: 'relative'}}>
            TRANQUILO
            <span
              style={{
                position: 'absolute',
                left: -10,
                right: -10,
                top: '52%',
                height: 18,
                background: C.blood,
                transform: `scaleX(${interpolate(f, [126, 134], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}) rotate(-3deg)`,
                transformOrigin: 'left',
              }}
            />
          </span>
          <span style={{fontSize: 96, marginLeft: 12}}>🩸</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
