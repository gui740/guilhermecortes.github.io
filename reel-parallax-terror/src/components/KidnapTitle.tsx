import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {rnd} from './util';
import {COR, F} from './fonts';

const ESTILOS = [
  {bg: COR.papel, c: COR.preto, f: 'titulo'},
  {bg: '#f4f0e6', c: COR.preto, f: 'bebas'},
  {bg: COR.preto, c: COR.branco, f: 'titulo'},
  {bg: COR.vermelho, c: COR.branco, f: 'bebas'},
  {bg: '#d9c9a3', c: COR.sangue, f: 'maquina'},
  {bg: COR.branco, c: COR.vermelho, f: 'titulo'},
] as const;

/** Título estilo bilhete de sequestro: cada letra num pedacinho de papel recortado. */
export const KidnapTitle: React.FC<{linhas: string[]; x: number; y: number; delay?: number; tamanho?: number; passo?: number; seed?: string}> = ({
  linhas, x, y, delay = 0, tamanho = 96, passo = 1.6, seed = 'k',
}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  let k = 0;
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: 'translate(-50%,-50%)', zIndex: 70, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: tamanho * 0.12}}>
      {linhas.map((linha, li) => (
        <div key={li} style={{display: 'flex', gap: tamanho * 0.06, alignItems: 'center'}}>
          {[...linha].map((ch, ci) => {
            const i = k++;
            if (ch === ' ') return <div key={ci} style={{width: tamanho * 0.32}} />;
            const d = delay + i * passo;
            if (f < d) return <div key={ci} style={{width: tamanho * 0.62, visibility: 'hidden'}} />;
            const sp = spring({frame: f - d, fps, config: {damping: 13, stiffness: 180, mass: 0.6}});
            const e = ESTILOS[Math.floor(rnd(`${seed}${i}`) * ESTILOS.length)];
            const fam = e.f === 'titulo' ? F.titulo : e.f === 'bebas' ? F.bebas : F.maquina;
            const rot = rnd(`${seed}r${i}`, -7, 7);
            return (
              <div key={ci} style={{
                background: e.bg, color: e.c, fontFamily: fam, fontSize: tamanho * (e.f === 'maquina' ? 0.82 : rnd(`${seed}s${i}`, 0.88, 1.08)),
                lineHeight: 1.18, padding: `${tamanho * 0.04}px ${tamanho * 0.09}px 0px`, minWidth: tamanho * 0.46, textAlign: 'center',
                transform: `translateY(${rnd(`${seed}y${i}`, -8, 8)}px) rotate(${rot + (1 - sp) * 12}deg) scale(${0.6 + 0.4 * sp})`, opacity: Math.min(1, sp * 2),
                boxShadow: '3px 5px 6px rgba(0,0,0,0.55)', clipPath: `polygon(${rnd(seed + 'a' + i, 0, 6)}% 0, 100% ${rnd(seed + 'b' + i, 0, 6)}%, ${100 - rnd(seed + 'c' + i, 0, 6)}% 100%, 0 ${100 - rnd(seed + 'd' + i, 0, 6)}%)`,
              }}>
                {ch}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
};
