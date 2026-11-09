import React from 'react';
import {AbsoluteFill, Img, random, staticFile, useCurrentFrame} from 'remotion';

/** Granulação de película animada (~8%) + flicker leve de exposição. Fica por cima de tudo. */
export const FilmGrain: React.FC<{opacidade?: number}> = ({opacidade = 0.08}) => {
  const f = useCurrentFrame();
  const q = Math.floor(f / 2) % 8; // troca o grão a cada 2 frames (cara de 12-15fps de película)
  const dx = Math.floor(random(`gx${f}`) * 40) - 20;
  const dy = Math.floor(random(`gy${f}`) * 40) - 20;
  const flick = 0.015 + random(`fl${f}`) * 0.025 + (random(`pk${Math.floor(f / 3)}`) > 0.96 ? 0.04 : 0);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <Img
        src={staticFile(`textura/grao_${q}.png`)}
        style={{position: 'absolute', left: -40 + dx, top: -40 + dy, width: 1160, height: 2000, opacity: opacidade * 1.8, mixBlendMode: 'overlay'}}
      />
      <AbsoluteFill style={{background: '#000', opacity: flick}} />
      <AbsoluteFill style={{boxShadow: 'inset 0 0 200px 40px rgba(0,0,0,0.45)'}} />
    </AbsoluteFill>
  );
};
