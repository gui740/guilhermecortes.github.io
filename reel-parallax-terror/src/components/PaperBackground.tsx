import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';

/** Cartolina/kraft queimado escuro: cor base + manchas (feTurbulence baixa freq.) + fibra/grão (alta freq.) + vinheta. */
export const PaperBackground: React.FC<{tom?: string; img?: string; imgOpacity?: number; imgFiltro?: string; escala?: number}> = ({
  tom = '#3d2b1d',
  img,
  imgOpacity = 0.5,
  imgFiltro = 'grayscale(0.25) sepia(0.25) contrast(1.08) brightness(0.8)',
  escala = 1.25,
}) => (
  <AbsoluteFill style={{background: tom, transform: `scale(${escala})`}}>
    {img ? (
      <Img src={staticFile(img)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: imgOpacity, filter: imgFiltro}} />
    ) : null}
    <svg width="100%" height="100%" viewBox="0 0 1080 1920" preserveAspectRatio="none" style={{position: 'absolute', inset: 0, mixBlendMode: img ? 'overlay' : 'normal'}}>
      <filter id="manchas" x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.006 0.009" numOctaves={4} seed={3} result="n" />
        <feColorMatrix type="matrix" values="0 0 0 0 0.10  0 0 0 0 0.06  0 0 0 0 0.03  0 0 0 -2.2 1.35" />
      </filter>
      <filter id="fibra" x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={9} result="g" />
        <feColorMatrix type="matrix" values="0 0 0 0 0.85  0 0 0 0 0.72  0 0 0 0 0.55  0 0 0 0.16 0" />
      </filter>
      <rect width="1080" height="1920" filter="url(#manchas)" />
      <rect width="1080" height="1920" filter="url(#fibra)" />
    </svg>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 60% at 50% 45%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.3) 78%, rgba(0,0,0,0.65) 100%)'}} />
  </AbsoluteFill>
);
