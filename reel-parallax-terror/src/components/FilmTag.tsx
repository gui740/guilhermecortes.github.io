import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {bordaRasgada} from './util';
import {COR, F} from './fonts';
import {Tape} from './Tape';
import {staticFile} from 'remotion';

/** Etiqueta de ficha técnica: papel envelhecido colado com fita. (x,y) = centro. */
export const FilmTag: React.FC<{titulo: string; ano: string; pais: string; diretor: string; x: number; y: number; delay?: number; rot?: number; w?: number}> = ({
  titulo, ano, pais, diretor, x, y, delay = 0, rot = -2, w = 600,
}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < delay) return null;
  const sp = spring({frame: f - delay, fps, config: {damping: 15, stiffness: 150, mass: 0.7}});
  return (
    <div style={{position: 'absolute', left: x, top: y, zIndex: 40, transform: `translate(-50%,-50%) translateY(${(1 - sp) * -30}px) rotate(${rot + (1 - sp) * 3}deg) scale(${0.92 + 0.08 * sp})`, opacity: Math.min(1, (f - delay) / 3), filter: 'drop-shadow(5px 9px 8px rgba(0,0,0,0.6))'}}>
      <div style={{minWidth: w, width: 'max-content', background: `repeating-linear-gradient(0deg, rgba(0,0,0,0) 0 38px, rgba(120,60,40,0.18) 38px 40px), url(${staticFile('textura/papel.jpg')}) center/cover, ${COR.papel}`, clipPath: bordaRasgada('tag' + titulo, 1.4, 16), padding: '18px 30px 20px', boxSizing: 'border-box', position: 'relative'}}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 18}}>
          <span style={{fontFamily: F.titulo, fontSize: 78, color: COR.preto, letterSpacing: 2, lineHeight: 1}}>{titulo}</span>
          <span style={{fontFamily: F.titulo, fontSize: 44, color: COR.vermelho, lineHeight: 1}}>{ano}</span>
        </div>
        <div style={{fontFamily: F.maquina, fontSize: 27, color: '#2b211a', marginTop: 6, whiteSpace: 'nowrap'}}>
          {pais} • dir. {diretor}
        </div>
      </div>
      <Tape x={44} y={10} w={120} h={40} rot={-32} delay={delay + 4} seed={titulo + 'f1'} />
      <Tape x={w - 40} y={12} w={110} h={38} rot={28} delay={delay + 6} seed={titulo + 'f2'} />
    </div>
  );
};
