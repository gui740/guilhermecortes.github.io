import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {CENAS} from '../config/cenas';
import {quando} from '../config/timing';
import {Camera} from '../components/Camera';
import {ParallaxLayer} from '../components/ParallaxLayer';
import {PaperBackground} from '../components/PaperBackground';
import {KidnapTitle} from '../components/KidnapTitle';
import {HandArrow} from '../components/HandArrow';
import {Tape} from '../components/Tape';
import {Scribble} from '../components/Scribble';
import {Jornal, VersoPolaroide} from '../components/Cenario';
import {rnd} from '../components/util';

const C = CENAS.gancho;
export const POLAROIDES = [
  {x: 250, y: 1060, rot: -9, marca: '1'},
  {x: 545, y: 1135, rot: 4, marca: '2'},
  {x: 835, y: 1050, rot: 10, marca: '3'},
];
export const PW = 280;

export const tlGancho = () => {
  const p0 = 6;
  return {
    polas: [p0, p0 + 11, p0 + 22],
    titulo: 34,
    seta: Math.max(70, quando(C, 'ninguem')),
    circulo: quando(C, 'motivo'),
    saida: C.saida,
  };
};

const PolaroideCaindo: React.FC<{i: number; delay: number}> = ({i, delay}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < delay) return null;
  const p = POLAROIDES[i];
  const sp = spring({frame: f - delay, fps, config: {damping: 14, stiffness: 120, mass: 0.8}});
  const queda = interpolate(sp, [0, 1], [-260, 0]);
  const r = p.rot + (1 - sp) * rnd('pg' + i, -25, 25);
  return (
    <div style={{position: 'absolute', left: p.x, top: p.y, transform: `translate(-50%,-50%) translateY(${queda}px) rotate(${r}deg) scale(${1.25 - 0.25 * sp})`, filter: `drop-shadow(${6 + 18 * (1 - sp)}px ${10 + 30 * (1 - sp)}px ${10 + 14 * (1 - sp)}px rgba(0,0,0,0.65))`}}>
      <VersoPolaroide w={PW} marca={p.marca} />
    </div>
  );
};

export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const t = tlGancho();
  // saída: câmera mergulha na polaroide 1 (ela vira a abertura do Possum)
  const ps = interpolate(f, [t.saida, C.duracao], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});
  const alvo = POLAROIDES[0];
  return (
    <AbsoluteFill style={{background: '#120b07', overflow: 'hidden'}}>
      <AbsoluteFill style={{transformOrigin: `${alvo.x}px ${alvo.y}px`, transform: `translate(${(540 - alvo.x) * ps}px, ${(960 - alvo.y) * ps}px) scale(${1 + ps * 2.7}) rotate(${-alvo.rot * ps}deg)`}}>
        <Camera de={{x: -40, y: 30, z: 0}} ate={{x: 36, y: -36, z: 0.12}} dur={C.duracao} punches={[t.titulo + 4]}>
          <ParallaxLayer fator={0.2} dolly={1}>
            <PaperBackground tom="#46321f" />
          </ParallaxLayer>
          <ParallaxLayer fator={0.5} dolly={0.3}>
            <Jornal x={170} y={300} w={330} h={420} rot={-12} manchete="DESAPARECIDO" op={0.32} />
            <Jornal x={940} y={1560} w={360} h={380} rot={9} manchete="NINGUÉM VIU" op={0.32} />
            <Jornal x={900} y={330} w={260} h={300} rot={14} manchete="1987" op={0.25} />
            <Jornal x={150} y={1620} w={300} h={300} rot={-7} manchete="CASO" op={0.25} />
          </ParallaxLayer>
          <ParallaxLayer fator={1} dolly={-0.3}>
            {POLAROIDES.map((_, i) => <PolaroideCaindo key={i} i={i} delay={t.polas[i]} />)}
            <KidnapTitle linhas={['3 FILMES', 'QUE NINGUÉM', 'TE INDICOU']} x={540} y={560} delay={t.titulo} tamanho={110} passo={1.3} seed="titulo" />
          </ParallaxLayer>
          <ParallaxLayer fator={1.1} dolly={-0.3}>
            {POLAROIDES.map((p, i) => (
              <Tape key={i} x={p.x + rnd('tx' + i, -20, 20)} y={p.y - PW * 0.6 - 4} w={130} h={42} rot={p.rot + rnd('tr' + i, -12, 12)} delay={t.polas[i] + 9} seed={'tg' + i} />
            ))}
            <HandArrow de={{x: 930, y: 790}} ate={{x: 650, y: 960}} curva={-70} delay={t.seta} dur={16} seed="hk" />
            <Scribble tipo="sublinhado" x={540} y={800} w={560} delay={t.circulo} dur={12} seed="hs" />
          </ParallaxLayer>
        </Camera>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
