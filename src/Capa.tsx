import React from 'react';
import {AbsoluteFill, staticFile, Img} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {World} from './world/World';
// Capa: túnel de folhas em perspectiva; ano mais antigo pequeno lá no fundo, 2026 enorme na frente
const camStatic = (t: number) => ({x: 0, y: 0, z: 30, lx: 0, ly: 0, lz: 10, w: 0, k: 0, speed: 0});
export const Capa: React.FC = () => (
  <AbsoluteFill style={{background: '#EDEDED'}}>
    <style>{`@font-face{font-family:'Anton';src:url(${staticFile('fonts/Anton-normal-400.ttf')})}
@font-face{font-family:'PF';font-style:italic;font-weight:900;src:url(${staticFile('fonts/PlayfairDisplay-italic-900.ttf')})}`}</style>
    <ThreeCanvas width={1080} height={1920} camera={{fov: 50, near: 0.05, far: 120, position: [0, 0, 30]}} gl={{antialias: true, preserveDrawingBuffer: true}}>
      <World frame={0} fps={30} stations={false} tOverride={8} camOverride={camStatic} />
    </ThreeCanvas>
    <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, fontFamily: 'Anton', color: '#1C1C1C'}}>
      <div style={{position: 'absolute', top: 905, width: 1080, textAlign: 'center', fontSize: 64, opacity: 0.55, letterSpacing: '0.02em'}}>10.000 a.C.</div>
      <div style={{position: 'absolute', top: 990, width: 1080, textAlign: 'center', fontSize: 30, opacity: 0.4, fontFamily: 'PF', fontStyle: 'italic'}}>· · · 1830 · · · 1937 · · ·</div>
      <div style={{position: 'absolute', top: 270, left: 70, width: 870, fontSize: 168, lineHeight: 0.9, transform: 'rotate(-3deg)', transformOrigin: '0 0'}}>
        <div>12 MIL ANOS</div>
        <div style={{fontFamily: 'PF', fontStyle: 'italic', fontSize: 92, lineHeight: 1.25, marginBottom: 6}}>de</div>
        <div style={{color: '#F23B3B', fontSize: 230}}>MACONHA</div>
      </div>
      <div style={{position: 'absolute', top: 1140, width: 1080, textAlign: 'center', fontSize: 420, lineHeight: 1, color: '#1C1C1C', letterSpacing: '-0.01em'}}>2026</div>
    </div>
    <Img src={staticFile('tex/grain3.png')} style={{position: 'absolute', inset: 0, width: 1080, height: 1920, mixBlendMode: 'overlay', opacity: 0.32}} />
  </AbsoluteFill>
);
