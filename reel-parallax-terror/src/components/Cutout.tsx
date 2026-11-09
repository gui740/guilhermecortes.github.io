import React from 'react';
import {Img, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {bordaRasgada, rnd} from './util';
import {COR, F} from './fonts';

export type CutoutProps = {
  src: string;
  x: number; // centro
  y: number;
  w: number; // largura na tela
  rot?: number;
  delay?: number;
  /** sticker = PNG recortado (borda branca já vem do recortar.py)
   *  polaroide = foto com moldura branca e base larga
   *  rasgado = foto impressa com borda de papel rasgado */
  tipo?: 'sticker' | 'polaroide' | 'rasgado';
  aspecto?: number; // largura/altura da área da foto (polaroide/rasgado)
  legenda?: string; // texto manuscrito na base da polaroide
  filtro?: string;
  seed?: string;
  z?: number;
  children?: React.ReactNode; // extras desenhados por cima (ex.: fita)
};

/** Imagem colada: entra como papel caindo na mesa (pop 0.92→1, rotação -4°..4° assentando, sombra suave). */
export const Cutout: React.FC<CutoutProps> = ({
  src, x, y, w, rot = 0, delay = 0, tipo = 'sticker', aspecto = 1, legenda, filtro, seed, z, children,
}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < delay) return null;
  const s = seed ?? src;
  const sp = spring({frame: f - delay, fps, config: {damping: 16, stiffness: 140, mass: 0.7}});
  const giro = rnd(`${s}-g`, -4, 4);
  const escala = 0.92 + 0.08 * sp;
  const r = rot + giro * (1 - sp);
  const queda = (1 - sp) * -34;
  const op = Math.min(1, (f - delay) / 3);
  // sombra cresce quando assenta (papel encostando na mesa)
  const sombra = `drop-shadow(${(4 + 6 * (1 - sp)).toFixed(1)}px ${(8 + 14 * (1 - sp)).toFixed(1)}px ${(8 + 10 * (1 - sp)).toFixed(1)}px rgba(0,0,0,0.6))`;

  let corpo: React.ReactNode;
  if (tipo === 'sticker') {
    corpo = <Img src={staticFile(src)} style={{width: w, display: 'block', filter: filtro}} />;
  } else if (tipo === 'polaroide') {
    const pad = w * 0.055;
    const iw = w - pad * 2;
    corpo = (
      <div style={{width: w, padding: pad, paddingBottom: legenda ? pad * 4.2 : pad * 3.2, background: COR.branco, position: 'relative', boxSizing: 'border-box'}}>
        <div style={{width: iw, height: iw / aspecto, overflow: 'hidden', background: '#111'}}>
          <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: filtro ?? 'contrast(1.05) saturate(0.85)'}} />
        </div>
        {legenda ? (
          <div style={{position: 'absolute', left: 0, right: 0, bottom: pad * 0.9, textAlign: 'center', fontFamily: F.caveat, fontSize: w * 0.105, color: '#2a2a2a', transform: `rotate(${rnd(s + 'l', -3, 3)}deg)`}}>
            {legenda}
          </div>
        ) : null}
      </div>
    );
  } else {
    corpo = (
      <div style={{width: w, padding: w * 0.025, background: COR.papel, clipPath: bordaRasgada(s, 1.8), boxSizing: 'border-box'}}>
        <div style={{width: '100%', height: (w * 0.95) / aspecto, overflow: 'hidden', clipPath: bordaRasgada(s + 'i', 1.2)}}>
          <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: filtro ?? 'contrast(1.08) saturate(0.8) sepia(0.15)'}} />
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        position: 'absolute', left: x, top: y, zIndex: z,
        transform: `translate(-50%, -50%) translateY(${queda.toFixed(1)}px) rotate(${r.toFixed(2)}deg) scale(${escala.toFixed(4)})`,
        opacity: op, filter: sombra,
      }}
    >
      <div style={{position: 'relative'}}>
        {corpo}
        {children}
      </div>
    </div>
  );
};
