import React from 'react';
import {AbsoluteFill, Freeze, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {CENAS} from '../config/cenas';
import {quando, TRANSICAO} from '../config/timing';
import {PaperBackground} from '../components/PaperBackground';
import {RedString} from '../components/RedString';
import {Tape} from '../components/Tape';
import {COR, F} from '../components/fonts';
import {EASE, prog} from '../components/util';
import {Possum} from './Possum';
import {Calvaire} from './Calvaire';
import {Hagazussa} from './Hagazussa';

const C = CENAS.fechamento;
/** posição de cada cena no mural final (escala ESC, centro x/y, rotação) */
export const ESC = 0.3;
export const BORDA_CARD = 70; // borda branca (em px da cena, antes da escala)
export const CARDS = {
  possum: {x: 205, y: 640, rot: -4},
  calvaire: {x: 540, y: 600, rot: 2},
  hagazussa: {x: 875, y: 655, rot: 5},
};

export const tlFechamento = () => ({
  fios: TRANSICAO + 4,
  arroba: TRANSICAO + 16,
  cta: Math.max(TRANSICAO + 30, quando(C, 'qual')),
});

export const estiloCard = (p = 1): React.CSSProperties => ({
  boxShadow: `0 0 0 ${BORDA_CARD * p}px ${COR.branco}, ${30 * p}px ${50 * p}px ${60 * p}px ${20 * p}px rgba(0,0,0,0.6)`,
});

const Card: React.FC<{id: keyof typeof CARDS; frame: number; children: React.ReactNode}> = ({id, frame, children}) => {
  const c = CARDS[id];
  return (
    <div style={{position: 'absolute', left: c.x - 540, top: c.y - 960, width: 1080, height: 1920, transform: `rotate(${c.rot}deg) scale(${ESC})`, transformOrigin: '540px 960px', overflow: 'hidden', ...estiloCard()}}>
      <Freeze frame={frame}>{children}</Freeze>
    </div>
  );
};

const Faixa: React.FC<{texto: React.ReactNode; y: number; delay: number; rot: number; cor?: string; fundo?: string; tam?: number}> = ({texto, y, delay, rot, cor = COR.preto, fundo = COR.papel, tam = 66}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < delay) return null;
  const sp = spring({frame: f - delay, fps, config: {damping: 14, stiffness: 160, mass: 0.6}});
  return (
    <div style={{position: 'absolute', left: 540, top: y, transform: `translate(-50%,-50%) rotate(${rot + (1 - sp) * 6}deg) scale(${0.85 + 0.15 * sp})`, opacity: Math.min(1, sp * 2), background: fundo, color: cor, fontFamily: F.titulo, fontSize: tam, lineHeight: 1, padding: '10px 26px 6px', whiteSpace: 'nowrap', boxShadow: '4px 7px 8px rgba(0,0,0,0.6)', clipPath: 'polygon(1% 4%, 99% 0, 100% 96%, 0 100%)', zIndex: 80}}>
      {texto}
    </div>
  );
};

export const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = tlFechamento();
  // depois que o Hagazussa encaixa no mural, a câmera continua se afastando devagar
  const z = interpolate(prog(f, TRANSICAO, C.duracao, EASE), [0, 1], [1, 0.93]);
  const dy = interpolate(prog(f, TRANSICAO, C.duracao, EASE), [0, 1], [0, -20]);
  const spA = f >= t.arroba ? spring({frame: f - t.arroba, fps, config: {damping: 14, stiffness: 130, mass: 0.8}}) : 0;
  return (
    <AbsoluteFill style={{background: '#0d0907', overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `translateY(${dy}px) scale(${z})`, transformOrigin: '540px 760px'}}>
        <PaperBackground tom="#3d2b1d" escala={1.3} />
        <Card id="possum" frame={CENAS.possum.saida - 1}><Possum /></Card>
        <Card id="calvaire" frame={CENAS.calvaire.saida - 1}><Calvaire /></Card>
        {f >= TRANSICAO ? <Card id="hagazussa" frame={CENAS.hagazussa.duracao - 1}><Hagazussa /></Card> : null}
        <Tape x={205} y={330} w={140} rot={-10} delay={t.fios - 4} seed="ot1" />
        <Tape x={545} y={292} w={140} rot={6} delay={t.fios - 2} seed="ot2" />
        <Tape x={890} y={345} w={140} rot={12} delay={t.fios} seed="ot3" />
        <RedString de={{x: 250, y: 420}} ate={{x: 520, y: 400}} delay={t.fios} seed="of1" />
        <RedString de={{x: 570, y: 420}} ate={{x: 850, y: 450}} delay={t.fios + 5} seed="of2" />
        <RedString de={{x: 200, y: 860}} ate={{x: 880, y: 890}} delay={t.fios + 10} caimento={120} seed="of3" />
        <RedString de={{x: 540, y: 820}} ate={{x: 540, y: 990}} delay={t.arroba + 6} caimento={10} seed="of4" pinos={false} />
        {spA > 0 ? (
          <div style={{position: 'absolute', left: 540, top: 1010, transform: `translate(-50%,-50%) translateY(${(1 - spA) * -60}px) rotate(${-3 + (1 - spA) * 8}deg) scale(${0.9 + 0.1 * spA})`, filter: 'drop-shadow(6px 10px 10px rgba(0,0,0,0.7))', zIndex: 85}}>
            <div style={{background: COR.preto, color: COR.branco, fontFamily: F.titulo, fontSize: 78, padding: '14px 34px 8px', border: `8px solid ${COR.branco}`, letterSpacing: 1}}>
              @talking_horror
            </div>
            <Tape x={40} y={6} w={120} rot={-30} delay={t.arroba + 5} seed="oat1" />
            <Tape x={520} y={6} w={120} rot={26} delay={t.arroba + 7} seed="oat2" />
          </div>
        ) : null}
        <Faixa texto="QUAL VOCÊ TERIA" y={1150} delay={t.cta} rot={-2} />
        <Faixa texto="CORAGEM DE VER" y={1228} delay={t.cta + 5} rot={1.5} />
        <Faixa texto={<>SOZINHO? <span style={{fontSize: 56}}>🩸</span></>} y={1306} delay={t.cta + 10} rot={-1} fundo={COR.vermelho} cor={COR.branco} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
