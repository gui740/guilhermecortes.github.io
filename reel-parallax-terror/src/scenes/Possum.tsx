import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {CENAS} from '../config/cenas';
import {quando, TRANSICAO} from '../config/timing';
import {Camera} from '../components/Camera';
import {ParallaxLayer} from '../components/ParallaxLayer';
import {PaperBackground} from '../components/PaperBackground';
import {Cutout} from '../components/Cutout';
import {Tape} from '../components/Tape';
import {RedString} from '../components/RedString';
import {HandArrow} from '../components/HandArrow';
import {Scribble} from '../components/Scribble';
import {Annotation} from '../components/Annotation';
import {FilmTag} from '../components/FilmTag';
import {VersoPolaroide} from '../components/Cenario';
import {COR, F} from '../components/fonts';
import {prog} from '../components/util';
import {PW} from './Hook';

const C = CENAS.possum;

export const tlPossum = () => ({
  // o gancho ainda está por cima nos primeiros TRANSICAO frames (zoom na polaroide)
  flip: TRANSICAO,
  poster: TRANSICAO + 30,
  ficha: quando(C, 'possum') + 14,
  casa: quando(C, 'casa'),
  philip: quando(C, 'titereiro'),
  mala: quando(C, 'mala'),
  fioMala: quando(C, 'mala') + 12,
  nota: quando(C, 'dentro'),
  boneco: quando(C, 'boneco'),
  fioBoneco: quando(C, 'aranha'),
  circMala: quando(C, 'livrar'),
  circBoneco: quando(C, 'sempre'),
  maurice: quando(C, 'sujo'),
  philip2: quando(C, 'representa'),
  pior: quando(C, 'pior'),
  setaSaida: C.saida - 14,
});

// polaroide do pôster: chega gigante (vinda do gancho), vira e vai pro canto do mural
const POSTER = {x: 835, y: 505, w: 290, rot: 6};
const FlipPoster: React.FC = () => {
  const f = useCurrentFrame();
  const t = tlPossum();
  const giro = interpolate(f, [t.flip, t.flip + 14], [0, 180], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const m = prog(f, t.flip + 12, t.poster);
  const W0 = PW * 3.7;
  const w = W0 + (POSTER.w - W0) * m;
  const x = 540 + (POSTER.x - 540) * m;
  const y = 960 + (POSTER.y - 960) * m;
  const r = POSTER.rot * m;
  const pad = w * 0.055;
  const face: React.CSSProperties = {position: 'absolute', left: 0, top: 0, backfaceVisibility: 'hidden'};
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: w * 1.2, transform: `translate(-50%,-50%) rotate(${r}deg)`, perspective: 2400, filter: `drop-shadow(${6 + 20 * (1 - m)}px ${10 + 30 * (1 - m)}px ${12 + 20 * (1 - m)}px rgba(0,0,0,0.65))`, zIndex: 30}}>
      <div style={{position: 'relative', width: '100%', height: '100%', transformStyle: 'preserve-3d', transform: `rotateY(${giro}deg)`}}>
        <div style={{...face, transform: 'scale(' + w / PW + ')', transformOrigin: '0 0'}}>
          <VersoPolaroide w={PW} marca="1" />
        </div>
        <div style={{...face, width: w, height: w * 1.2, transform: 'rotateY(180deg)', background: COR.branco, padding: pad, paddingBottom: pad * 2.6, boxSizing: 'border-box'}}>
          <Img src={staticFile('possum/poster.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'contrast(1.05)'}} />
          <div style={{position: 'absolute', left: 0, right: 0, bottom: pad * 0.3, textAlign: 'center', fontFamily: F.caveat, fontSize: w * 0.1, color: '#222'}}>nº 1</div>
        </div>
      </div>
    </div>
  );
};

export const Possum: React.FC = () => {
  const t = tlPossum();
  return (
    <AbsoluteFill style={{background: '#100a07', overflow: 'hidden'}}>
      <Camera de={{x: -55, y: 36, z: 0}} ate={{x: 50, y: -40, z: 0.16}} dur={C.duracao} punches={[t.ficha]}>
        <ParallaxLayer fator={0.2} dolly={1}>
          <PaperBackground img="possum/campo_fundo.jpg" imgOpacity={0.85} tom="#3a2a1c" imgFiltro="sepia(0.2) contrast(1.08) brightness(0.95)" />
        </ParallaxLayer>
        <ParallaxLayer fator={0.5} dolly={0.3}>
          <Cutout src="possum/casa.jpg" tipo="rasgado" aspecto={1.6} x={300} y={612} w={500} rot={-4} delay={t.casa} seed="pcasa" />
          <Tape x={300} y={455} w={150} rot={3} delay={t.casa + 7} seed="pct" />
        </ParallaxLayer>
        <ParallaxLayer fator={1} dolly={-0.3}>
          <FilmTag titulo="POSSUM" ano="2018" pais="Reino Unido" diretor="Matthew Holness" x={350} y={330} w={560} delay={t.ficha} rot={-2} />
          <Cutout src="possum/maurice_recorte.png" x={880} y={800} w={290} rot={7} delay={t.maurice} />
          <Cutout src="possum/philip_recorte.png" x={560} y={1000} w={640} rot={-1} delay={t.philip} />
          <Cutout src="possum/boneco.jpg" tipo="polaroide" aspecto={1.5} legenda="o boneco" x={815} y={1130} w={330} rot={6} delay={t.boneco} seed="pbon" />
          <Cutout src="possum/mala_recorte.png" x={255} y={1120} w={330} rot={-7} delay={t.mala} />
          <Cutout src="possum/philip2_recorte.png" x={585} y={985} w={600} rot={3} delay={t.philip2} />
        </ParallaxLayer>
        <ParallaxLayer fator={1.1} dolly={-0.3}>
          <Tape x={790} y={975} w={130} rot={-14} delay={t.boneco + 8} seed="pbt" />
          <RedString de={{x: 300, y: 1010}} ate={{x: 520, y: 1170}} delay={t.fioMala} seed="pf1" />
          <RedString de={{x: 740, y: 1060}} ate={{x: 330, y: 1060}} delay={t.fioBoneco} caimento={70} seed="pf2" />
          <Annotation texto="não abre a mala" x={290} y={905} rot={-8} delay={t.nota} tamanho={54} />
          <Scribble tipo="circulo" x={255} y={1120} w={400} h={360} delay={t.circMala} seed="pc1" />
          <Scribble tipo="circulo" x={815} y={1125} w={420} h={360} delay={t.circBoneco} seed="pc2" />
          <Scribble tipo="sublinhado" x={290} y={950} w={380} delay={t.pior} dur={10} seed="ps1" />
          <HandArrow de={{x: 420, y: 1190}} ate={{x: 1260, y: 1010}} curva={-110} delay={t.setaSaida} dur={18} seed="psaida" />
        </ParallaxLayer>
        {/* a polaroide que vira fica fora do parallax (ela vem "colada" na câmera do gancho) */}
        <FlipPoster />
      </Camera>
    </AbsoluteFill>
  );
};
export const POSSUM_ENTRADA = TRANSICAO;
