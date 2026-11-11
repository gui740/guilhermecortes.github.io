import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Sequence, Series, continueRender, delayRender, Img, staticFile} from 'remotion';
import timeline from './data/timeline.json';
import {Scene, Block} from './Scene';
import {Grain, Star} from './Graphics';
import {C, fontCss} from './theme';

export const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all([
      document.fonts.load('100px Anton'),
      document.fonts.load('italic 900 100px Playfair'),
      document.fonts.load('800 100px Inter'),
    ]).then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};

const blocks = (timeline as any).blocks as Block[];

export const ReelBody: React.FC = () => (
  <AbsoluteFill style={{background: C.G}}>
    {blocks.map((b, i) => (
      <Sequence key={i} from={b.start} durationInFrames={b.end - b.start}>
        <Scene b={b} />
      </Sequence>
    ))}
    <Grain />
  </AbsoluteFill>
);

export const Reel: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill>
      <style>{fontCss}</style>
      <ReelBody />
    </AbsoluteFill>
  );
};

// Versões de gancho: trechos (em frames do Reel) da própria narração, remontados em 3s
export const Hook: React.FC<{segs: [number, number][]}> = ({segs}) => {
  useFonts();
  return (
    <AbsoluteFill>
      <style>{fontCss}</style>
      <Series>
        {segs.map(([a, b], i) => (
          <Series.Sequence key={i} durationInFrames={b - a}>
            <Sequence from={-a}><ReelBody /></Sequence>
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};

// Capa 1080x1920: fundo vermelho, Buddy recortado colorido com textura, título em 5 palavras
export const Capa: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{background: C.R, overflow: 'hidden'}}>
      <style>{fontCss}</style>
      <Star cx={540} cy={1330} r={620} still />
      <Img src={staticFile('cut/buddy_wave.png')} style={{position: 'absolute', left: 120, width: 840, bottom: 0, height: 1060, objectFit: 'contain', objectPosition: 'center bottom'}} />
      <div style={{position: 'absolute', left: 70, width: 870, top: 170, textAlign: 'center', lineHeight: 0.9}}>
        <div style={{fontFamily: 'Playfair', fontStyle: 'italic', fontWeight: 900, fontSize: 330, color: '#FFFFFF', transform: 'scaleX(0.8)', letterSpacing: -6, textShadow: '0 8px 0 #1C1C1C'}}>Buddy</div>
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: 14, marginTop: 0, lineHeight: 1.15}}>
          <span style={{fontFamily: 'Anton', fontSize: 190, color: C.K}}>NÃO</span>
          <span style={{fontFamily: 'Anton', fontSize: 70, color: '#FFFFFF'}}>É</span>
        </div>
        <div style={{fontFamily: 'Anton', fontSize: 150, color: '#FFFFFF', marginTop: -6, letterSpacing: -1}}>FILME INFANTIL</div>
      </div>
      <Grain />
    </AbsoluteFill>
  );
};
