import React from 'react';
import {AbsoluteFill} from 'remotion';
import {CENAS} from '../config/cenas';
import {quando} from '../config/timing';
import {Camera} from '../components/Camera';
import {ParallaxLayer} from '../components/ParallaxLayer';
import {PaperBackground} from '../components/PaperBackground';
import {Cutout} from '../components/Cutout';
import {Tape} from '../components/Tape';
import {RedString} from '../components/RedString';
import {Scribble} from '../components/Scribble';
import {Annotation} from '../components/Annotation';
import {FilmTag} from '../components/FilmTag';
import {Nevoa, Pinheiros} from '../components/Cenario';

const C = CENAS.calvaire;
const MARC = {x: 545, y: 930};
const ALVO = {x: 560, y: 1020}; // peito do Marc: todas as linhas apontam pra ele

export const tlCalvaire = () => ({
  ficha: quando(C, 'calvaire') + 12,
  poster: 22,
  fioEntrada: 4,
  marc: quando(C, 'cantor'),
  van: quando(C, 'van'),
  bartel: quando(C, 'pousada'),
  circBartel: quando(C, 'educado', 1),
  morador1: quando(C, 'homens'),
  morador3: quando(C, 'vila'),
  morador2: quando(C, 'vila') + 7,
  fios: quando(C, 'esperam'),
  nota: quando(C, 'esperam') + 6,
  bar: quando(C, 'danca'),
  xBar: quando(C, 'esqueceu'),
});

export const Calvaire: React.FC = () => {
  const t = tlCalvaire();
  return (
    <AbsoluteFill style={{background: '#0b0d0c', overflow: 'hidden'}}>
      <Camera de={{x: 26, y: -10, z: 0}} ate={{x: -28, y: 24, z: 0.12}} dur={C.duracao}>
        <ParallaxLayer fator={0.2} dolly={1}>
          <PaperBackground img="calvaire/floresta_fundo.jpg" imgOpacity={0.75} tom="#161b1a" imgFiltro="grayscale(0.5) contrast(1.15) brightness(0.7)" />
        </ParallaxLayer>
        <ParallaxLayer fator={0.32} dolly={0.6}>
          <Nevoa y={820} h={520} op={0.28} vel={0.35} />
          <Pinheiros seed="cal1" cor="#121815" escala={0.9} base={1900} />
        </ParallaxLayer>
        <ParallaxLayer fator={0.5} dolly={0.3}>
          <Nevoa y={1250} h={460} op={0.3} vel={-0.5} />
          <Cutout src="calvaire/poster.jpg" tipo="polaroide" aspecto={0.67} x={845} y={480} w={250} rot={7} delay={t.poster} seed="cpos" />
          <Tape x={845} y={300} w={120} rot={-6} delay={t.poster + 7} seed="cpt" />
        </ParallaxLayer>
        <ParallaxLayer fator={0.75} dolly={0}>
          <Pinheiros seed="cal2" cor="#030403" escala={1.1} lado="esq" base={2050} />
        </ParallaxLayer>
        <ParallaxLayer fator={1} dolly={-0.3}>
          <FilmTag titulo="CALVAIRE" ano="2004" pais="Bélgica" diretor="Fabrice Du Welz" x={370} y={330} w={580} delay={t.ficha} rot={2} />
          <Cutout src="calvaire/bartel_recorte.png" x={250} y={640} w={360} rot={-6} delay={t.bartel} />
          <Cutout src="calvaire/morador1_recorte.png" x={850} y={800} w={350} rot={5} delay={t.morador1} />
          <Cutout src="calvaire/morador3_recorte.png" x={150} y={1010} w={210} rot={-9} delay={t.morador3} />
          <Cutout src="calvaire/morador2.jpg" tipo="rasgado" aspecto={1.3} x={930} y={1050} w={220} rot={8} delay={t.morador2} seed="cm2" />
          <Cutout src="calvaire/marc_recorte.png" x={MARC.x} y={MARC.y} w={480} rot={-2} delay={t.marc} />
          <Cutout src="calvaire/van_recorte.png" x={330} y={1225} w={520} rot={-4} delay={t.van} />
          <Cutout src="calvaire/bar.jpg" tipo="polaroide" aspecto={1.45} legenda="a dança" x={800} y={1200} w={320} rot={-5} delay={t.bar} seed="cbar" />
        </ParallaxLayer>
        <ParallaxLayer fator={1.1} dolly={-0.3}>
          {/* barbante que veio do Possum entra pela esquerda */}
          <RedString de={{x: -120, y: 1000}} ate={{x: 345, y: 1190}} delay={t.fioEntrada} dur={14} seed="cfe" />
          <RedString de={{x: 330, y: 690}} ate={ALVO} delay={t.fios} seed="cf1" />
          <RedString de={{x: 830, y: 760}} ate={ALVO} delay={t.fios + 4} seed="cf2" />
          <RedString de={{x: 160, y: 960}} ate={ALVO} delay={t.fios + 8} seed="cf3" />
          <RedString de={{x: 930, y: 1000}} ate={ALVO} delay={t.fios + 12} seed="cf4" />
          <Scribble tipo="circulo" x={250} y={640} w={420} h={330} delay={t.circBartel} seed="cc1" />
          <Annotation texto="ninguém aqui é normal" x={540} y={1300} rot={-3} delay={t.nota} tamanho={54} />
          <Scribble tipo="x" x={800} y={1170} w={150} h={110} delay={t.xBar} dur={10} seed="cx" />
          <Tape x={800} y={1040} w={120} rot={8} delay={t.bar + 8} seed="cbt" />
        </ParallaxLayer>
      </Camera>
    </AbsoluteFill>
  );
};
