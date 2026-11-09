import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {BODY, C, HEAD, textShadow} from '../theme';
import {Counter, useIn, WordsIn} from '../components/bits';

/** 2,5–7s: mini-gráfico de contraste (ISAF 2025 x Worm et al. 2024) */
export const DataScene: React.FC = () => {
  const f = useCurrentFrame();
  const b1 = useIn(50, 14);
  const b2 = useIn(172, 18);
  const w2 = interpolate(f, [178, 214], [0, 850], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.exp),
  });
  const shake = f > 212 && f < 226 ? (random(`s${f}`) - 0.5) * 16 : 0;
  const end = useIn(232, 10);
  return (
    <AbsoluteFill style={{padding: '300px 150px 0 60px'}}>
      <WordsIn
        text="VILÃO, É? OLHA OS NÚMEROS:"
        start={0}
        every={2}
        highlight={['VILÃO']}
        style={{fontFamily: HEAD, fontSize: 118, lineHeight: 1, color: C.white, textShadow}}
      />

      <div style={{marginTop: 70, opacity: b1, transform: `translateX(${(1 - b1) * -60}px)`}}>
        <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 40, color: C.foam, lineHeight: 1.2}}>
          Pessoas mordidas por tubarão
          <br />
          no MUNDO INTEIRO em 2025*
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 22, marginTop: 14}}>
          <div style={{width: 14, height: 80, background: C.white, borderRadius: 4}} />
          <Counter to={65} start={56} duration={24} size={140} />
        </div>
      </div>

      <div style={{marginTop: 46, opacity: b2}}>
        <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 40, color: C.foam, lineHeight: 1.2}}>
          Tubarões mortos por humanos
          <br />
          POR ANO (pesca)
        </div>
        <div style={{position: 'relative', marginTop: 14, height: 80, transform: `translateX(${shake}px)`}}>
          <div
            style={{
              width: w2,
              height: 80,
              background: `linear-gradient(90deg, ${C.blood}, ${C.bloodBright})`,
              borderRadius: 4,
              boxShadow: '0 0 40px rgba(255,42,51,0.55)',
            }}
          />
        </div>
        <div style={{marginTop: 12}}>
          <Counter to={80} start={178} duration={36} size={140} prefix="~" suffix=" MILHÕES" />
        </div>
      </div>

      <div
        style={{
          marginTop: 40,
          fontFamily: HEAD,
          fontSize: 92,
          color: C.white,
          lineHeight: 1,
          opacity: end,
          transform: `scale(${interpolate(end, [0, 1], [1.4, 1])})`,
          transformOrigin: 'left center',
          textShadow,
        }}
      >
        QUEM DEVIA TER MEDO DE QUEM? 💀
      </div>

      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 150,
          top: 1500,
          fontFamily: BODY,
          fontWeight: 500,
          fontSize: 22,
          color: C.muted,
        }}
      >
        *mordidas não provocadas. Fontes: ISAF/Florida Museum (relatório 2025) · Worm et al., Science (2024)
      </div>
    </AbsoluteFill>
  );
};
