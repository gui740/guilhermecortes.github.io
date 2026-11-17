import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {World} from './World';

const ff = `@font-face{font-family:'Anton';src:url(${staticFile('fonts/Anton.ttf')});}`;
// capa: corredor + silhueta do assassino ao fundo + fita zebrada em X na frente + título em 4 palavras
export const Capa: React.FC = () => (
  <AbsoluteFill style={{background: '#1C1C1C'}}>
    <style>{ff}</style>
    <ThreeCanvas width={1080} height={1920} frameloop="never" gl={{antialias: true, preserveDrawingBuffer: true}} camera={{fov: 50, near: 0.05, far: 200, position: [0, 0, 0]}}>
      <World cameraOnly atFrame={128} />
    </ThreeCanvas>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0) 40%, rgba(8,8,8,0.75) 100%)'}} />
    <AbsoluteFill style={{boxShadow: 'inset 0 0 260px 50px rgba(242,59,59,0.18)'}} />
    {/* silhueta do assassino no fundo do corredor, com contraluz vermelha */}
    <div style={{position: 'absolute', left: 340, top: 880, width: 400, height: 560, background: 'radial-gradient(ellipse at 50% 45%, rgba(242,59,59,0.55) 0%, rgba(242,59,59,0.18) 45%, rgba(0,0,0,0) 70%)', filter: 'blur(8px)'}} />
    <Img src={staticFile('film/f3_killer.png')} style={{position: 'absolute', left: 405, top: 930, height: 500, filter: 'brightness(0.02) blur(0.6px) drop-shadow(0 0 22px rgba(242,59,59,0.65))'}} />
    {/* título: 4 palavras enormes, dentro da margem (topo 250 / direita 140) */}
    <div style={{position: 'absolute', top: 270, left: 70, right: 150, fontFamily: 'Anton', lineHeight: 0.92, textAlign: 'left', textShadow: '0 10px 30px rgba(0,0,0,.85)'}}>
      <div style={{fontSize: 250, color: '#F2E63A'}}>SLASHERS</div>
      <div style={{fontSize: 210, color: '#EDEDED'}}>QUE CÊ</div>
      <div style={{fontSize: 210, color: '#EDEDED'}}>NUNCA <span style={{color: '#F23B3B'}}>VIU</span></div>
    </div>
    {/* fita zebrada em X, em primeiro plano (levemente desfocada) */}
    {[{r: 24, y: 1240}, {r: -21, y: 1300}].map((o, i) => (
      <Img key={i} src={staticFile('txt/tape.png')} style={{position: 'absolute', left: -320, top: o.y, width: 1720, height: 132, transform: `rotate(${o.r}deg)`, filter: `blur(${i ? 2.5 : 1.2}px) drop-shadow(0 14px 18px rgba(0,0,0,.7))`}} />
    ))}
  </AbsoluteFill>
);
