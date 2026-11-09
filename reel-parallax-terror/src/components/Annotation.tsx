import React from 'react';
import {useCurrentFrame} from 'remotion';
import {prog} from './util';
import {COR, F} from './fonts';

/** Anotação manuscrita que "se escreve" da esquerda pra direita. (x,y) = centro. */
export const Annotation: React.FC<{texto: string; x: number; y: number; delay?: number; rot?: number; tamanho?: number; cor?: string; fonte?: 'marker' | 'caveat'; fundo?: boolean}> = ({
  texto, x, y, delay = 0, rot = -4, tamanho = 58, cor = COR.branco, fonte = 'marker', fundo = false,
}) => {
  const f = useCurrentFrame();
  if (f < delay) return null;
  const dur = Math.min(26, Math.max(10, texto.length * 1.3));
  const p = prog(f, delay, delay + dur, (t) => t);
  return (
    <div
      style={{
        position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) rotate(${rot}deg)`, zIndex: 65,
        fontFamily: fonte === 'marker' ? F.marker : F.caveat, fontSize: tamanho, color: cor, whiteSpace: 'nowrap', lineHeight: 1.1,
        clipPath: `inset(-20% ${(100 - p * 100).toFixed(1)}% -20% -5%)`,
        textShadow: '2px 3px 3px rgba(0,0,0,0.7)',
        background: fundo ? 'rgba(232,220,192,0.92)' : undefined, padding: fundo ? '4px 18px' : undefined,
      }}
    >
      {texto}
    </div>
  );
};
