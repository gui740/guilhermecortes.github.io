import React from 'react';
import {Img, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const PAPEL = `url(${staticFile('textura/papel.jpg')})`;
/** vinco de dobra atravessando uma foto (luz + sombra) */
const Vinco: React.FC<{seed: string}> = ({seed}) => {
  const ang = rnd(seed + 'vang', -25, 25) + (rnd(seed + 'vh') > 0.5 ? 90 : 0);
  const pos = rnd(seed + 'vpos', 35, 65);
  return <div style={{position: 'absolute', inset: 0, pointerEvents: 'none', mixBlendMode: 'soft-light', background: `linear-gradient(${ang}deg, rgba(0,0,0,0) ${pos - 1.2}%, rgba(255,255,255,0.55) ${pos}%, rgba(0,0,0,0.45) ${pos + 0.6}%, rgba(0,0,0,0) ${pos + 2}%)`}} />;
};
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
  // depois de assentar o papel continua "vivo": balança muito de leve (corrente de ar)
  const vivo = Math.sin((f + rnd(s + 'ph', 0, 200)) / 38) * 0.7 * sp;
  const r = rot + giro * (1 - sp) + vivo;
  const queda = (1 - sp) * -34 + Math.sin((f + rnd(s + 'py', 0, 200)) / 51) * 2.5 * sp;
  const op = Math.min(1, (f - delay) / 3);
  // sombra cresce quando assenta (papel encostando na mesa)
  const sombra = `drop-shadow(${(7 + 8 * (1 - sp)).toFixed(1)}px ${(12 + 16 * (1 - sp)).toFixed(1)}px ${(10 + 10 * (1 - sp)).toFixed(1)}px rgba(0,0,0,0.55))`;

  let corpo: React.ReactNode;
  if (tipo === 'sticker') {
    corpo = <Img src={staticFile(src)} style={{width: w, display: 'block', filter: filtro}} />;
  } else if (tipo === 'polaroide') {
    const pad = w * 0.055;
    const iw = w - pad * 2;
    corpo = (
      <div style={{width: w, padding: pad, paddingBottom: legenda ? pad * 4.2 : pad * 3.2, background: `${PAPEL} center/cover, ${COR.branco}`, position: 'relative', boxSizing: 'border-box', boxShadow: 'inset 0 0 18px rgba(120,90,50,0.25)'}}>
        <div style={{width: iw, height: iw / aspecto, overflow: 'hidden', background: '#111'}}>
          <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: filtro}} />
        </div>
        <Vinco seed={s} />
        {legenda ? (
          <div style={{position: 'absolute', left: 0, right: 0, bottom: pad * 0.9, textAlign: 'center', fontFamily: F.caveat, fontSize: w * 0.105, color: '#2a2a2a', transform: `rotate(${rnd(s + 'l', -3, 3)}deg)`}}>
            {legenda}
          </div>
        ) : null}
      </div>
    );
  } else {
    corpo = (
      <div style={{width: w, padding: w * 0.025, background: `${PAPEL} center/cover, ${COR.papel}`, clipPath: bordaRasgada(s, 1.8), boxSizing: 'border-box', position: 'relative'}}>
        <div style={{width: '100%', height: (w * 0.95) / aspecto, overflow: 'hidden', clipPath: bordaRasgada(s + 'i', 1.2)}}>
          <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: filtro}} />
        </div>
        <Vinco seed={s} />
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
