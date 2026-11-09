import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useCam} from './Camera';

/**
 * Camada com fator de profundidade.
 *  fator: 0.2 fundo · 0.5 plano médio · 1.0 recortes · 1.1 setas/fita
 *  dolly: quanto a camada acompanha o push-in da câmera.
 *         >0 = zoom-in (fundo), <0 = zoom-out leve (recorte)  => "dolly zoom" sutil
 */
export const ParallaxLayer: React.FC<{fator: number; dolly?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
  fator,
  dolly = 0,
  children,
  style,
}) => {
  const cam = useCam();
  const s = 1 + cam.z * dolly;
  return (
    <AbsoluteFill
      style={{
        transform: `translate3d(${(-cam.x * fator).toFixed(2)}px, ${(-cam.y * fator).toFixed(2)}px, 0) scale(${s.toFixed(4)})`,
        transformOrigin: '540px 960px',
        ...style,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
