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
import {Annotation} from '../components/Annotation';
import {FilmTag} from '../components/FilmTag';
import {Montanhas, Nevoa} from '../components/Cenario';
import {Pt} from '../components/util';

const C = CENAS.hagazussa;

// pontas do pentagrama torto (cada uma num recorte)
const P: Pt[] = [
  {x: 560, y: 600},  // Albrun
  {x: 860, y: 640},  // caveira
  {x: 840, y: 1170}, // cabra 2
  {x: 250, y: 1160}, // cabra
  {x: 290, y: 690},  // cabana
];
const ESTRELA = [0, 2, 4, 1, 3, 0];

export const tlHagazussa = () => {
  const ini = quando(C, 'peso');
  const fim = C.saida - 30;
  const passo = Math.max(16, Math.floor((fim - ini) / 5));
  return {
    ficha: quando(C, 'hagazussa') + 10,
    seculo: quando(C, 'seculo'),
    cabana: quando(C, 'alpes'),
    albrun: quando(C, 'mulher'),
    cabra: quando(C, 'cabras'),
    cabra2: quando(C, 'cabras') + 8,
    caveira: quando(C, 'bruxa'),
    poster: quando(C, 'dialogo'),
    albrun2: quando(C, 'enlouquecer'),
    estrela: Array.from({length: 5}, (_, i) => ini + i * passo),
  };
};

export const Hagazussa: React.FC = () => {
  const t = tlHagazussa();
  return (
    <AbsoluteFill style={{background: '#0c1014', overflow: 'hidden'}}>
      <Camera de={{x: -45, y: 45, z: 0}} ate={{x: 50, y: -35, z: 0.17}} dur={C.duracao} punches={[t.ficha]}>
        <ParallaxLayer fator={0.12} dolly={1}>
          <PaperBackground img="hagazussa/neve_fundo.jpg" imgOpacity={0.55} tom="#1a2026" imgFiltro="grayscale(0.4) contrast(1.05) brightness(0.75)" />
        </ParallaxLayer>
        <ParallaxLayer fator={0.25} dolly={0.8}>
          <Montanhas base={1180} altura={520} cor="#5b6875" neve="#c9d1d8" seed="m1" picos={4} />
          <Nevoa y={1050} h={360} op={0.35} vel={0.3} />
        </ParallaxLayer>
        <ParallaxLayer fator={0.42} dolly={0.55}>
          <Montanhas base={1450} altura={520} cor="#3a4550" neve="#9aa6b0" seed="m2" picos={5} />
          <Nevoa y={1330} h={340} op={0.3} vel={-0.4} />
        </ParallaxLayer>
        <ParallaxLayer fator={0.6} dolly={0.3}>
          <Montanhas base={1800} altura={480} cor="#1f262d" seed="m3" picos={6} />
          <Cutout src="hagazussa/cabana.jpg" tipo="rasgado" aspecto={1.4} x={295} y={660} w={440} rot={-4} delay={t.cabana} seed="hcab" />
          <Tape x={295} y={515} w={140} rot={5} delay={t.cabana + 7} seed="hct" />
          <Cutout src="hagazussa/poster.jpg" tipo="polaroide" aspecto={0.67} x={175} y={930} w={210} rot={-8} delay={t.poster} seed="hpos" />
        </ParallaxLayer>
        <ParallaxLayer fator={1} dolly={-0.3}>
          <FilmTag titulo="HAGAZUSSA" ano="2017" pais="Áustria/Alemanha" diretor="Lukas Feigelfeld" x={560} y={320} w={640} delay={t.ficha} rot={-1.5} />
          <Cutout src="hagazussa/caveira_recorte.png" x={860} y={660} w={260} rot={8} delay={t.caveira} />
          <Cutout src="hagazussa/albrun_recorte.png" x={560} y={930} w={560} rot={-2} delay={t.albrun} />
          <Cutout src="hagazussa/cabra_recorte.png" x={250} y={1170} w={360} rot={-5} delay={t.cabra} />
          <Cutout src="hagazussa/cabra2_recorte.png" x={840} y={1185} w={360} rot={6} delay={t.cabra2} />
          <Cutout src="hagazussa/albrun2_recorte.png" x={600} y={1010} w={360} rot={5} delay={t.albrun2} />
        </ParallaxLayer>
        <ParallaxLayer fator={1.1} dolly={-0.3}>
          <Annotation texto="século XV" x={290} y={470} rot={-7} delay={t.seculo} tamanho={60} />
          {ESTRELA.slice(0, -1).map((a, i) => (
            <RedString key={i} de={P[a]} ate={P[ESTRELA[i + 1]]} delay={t.estrela[i]} dur={16} caimento={18} seed={'hs' + i} pinos />
          ))}
        </ParallaxLayer>
      </Camera>
    </AbsoluteFill>
  );
};
