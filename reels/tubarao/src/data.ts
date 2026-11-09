// Todos os dados abaixo foram conferidos em 09/11/2026. Fontes em ../FONTES.md
export const FPS = 30;

export type Pin = {
  lon: number;
  lat: number;
  label: string;
  kind: 'story' | 'filmed';
  labelPos?: 'side' | 'below' | 'above';
};

export type Stream = {logo: string; name: string};

export type Movie = {
  tag: string;
  title: string;
  subtitle?: string;
  year: number;
  poster: string;
  curiosity: string;
  counter: {prefix: string; value: number; decimals: number; suffix: string};
  counterLabel: string;
  counterNote: string;
  map: {
    center: [number, number];
    // escala final do zoom (mercator)
    scale: number;
    pins: Pin[];
    legend: {story: string; filmed: string};
  };
  streams: Stream[];
  // momentos (segundos desde o início do bloco) em que a narração fala de cada coisa
  cues: {curiosity: number; numbers: number; platform: number};
};

export const MOVIES: Movie[] = [
  {
    tag: '1/3 · CULT DOS ANOS 90 · MAR ABERTO',
    title: 'DO FUNDO DO MAR',
    year: 1999,
    poster: 'dofundo.jpg',
    curiosity: 'Gravado nos tanques que James Cameron construiu pra Titanic.',
    counter: {prefix: 'US$ ', value: 164.6, decimals: 1, suffix: ' MI'},
    counterLabel: 'de bilheteria no mundo',
    counterNote: 'custou US$ 60 mi',
    map: {
      center: [-117.3, 32.6],
      scale: 2600,
      pins: [{lon: -117.06, lat: 32.36, label: 'ROSARITO, MÉXICO', kind: 'filmed'}],
      legend: {
        story: 'base isolada no meio do oceano',
        filmed: 'Rosarito, México (tanques de Titanic)',
      },
    },
    cues: {curiosity: 1.75, numbers: 6.65, platform: 10.85},
    streams: [
      {logo: 'max.png', name: 'HBO Max'},
      {logo: 'amazonhbomax.png', name: 'HBO Max · Prime Video Channels'},
    ],
  },
  {
    tag: '2/3 · ANOS 2010 · CIDADE MAIA SUBMERSA',
    title: 'MEDO PROFUNDO',
    subtitle: 'O SEGUNDO ATAQUE',
    year: 2019,
    poster: 'medo2.jpg',
    curiosity: 'A cidade maia submersa? Montada em tanques na Inglaterra.',
    counter: {prefix: 'US$ ', value: 47.6, decimals: 1, suffix: ' MI'},
    counterLabel: 'de bilheteria no mundo',
    counterNote: 'custou US$ 12 mi: quase 4x o orçamento',
    map: {
      center: [-40, 35],
      scale: 400,
      pins: [
        {lon: -89.0, lat: 20.6, label: 'YUCATÁN', kind: 'story', labelPos: 'above'},
        {lon: -0.53, lat: 51.55, label: 'INGLATERRA', kind: 'filmed'},
        {lon: -69.45, lat: 18.43, label: 'REP. DOMINICANA', kind: 'filmed', labelPos: 'below'},
      ],
      legend: {
        story: 'Yucatán, México',
        filmed: 'tanques na Inglaterra e no Caribe',
      },
    },
    cues: {curiosity: 3.25, numbers: 7.85, platform: 10.75},
    streams: [
      {logo: 'amazontelecine.png', name: 'Telecine · Prime Video Channels'},
      {logo: 'amazonlionsgateplus.png', name: 'Lionsgate+ · Prime Video Channels'},
    ],
  },
  {
    tag: '3/3 · RECENTE · NO MEIO DE PARIS',
    title: 'SOB AS ÁGUAS DO SENA',
    year: 2024,
    poster: 'sena.jpg',
    curiosity: 'O triatlo no Sena? Gravado num tanque gigante na Espanha.',
    counter: {prefix: '', value: 102.3, decimals: 1, suffix: ' MI'},
    counterLabel: 'de views na Netflix em 91 dias',
    counterNote: '2º filme não falado em inglês mais visto da Netflix',
    map: {
      center: [1.2, 43.8],
      scale: 3300,
      pins: [
        {lon: 2.35, lat: 48.86, label: 'PARIS', kind: 'story'},
        {lon: -0.48, lat: 38.35, label: 'ALICANTE', kind: 'filmed'},
      ],
      legend: {
        story: 'Paris, no rio Sena',
        filmed: 'tanque em Alicante (Espanha)',
      },
    },
    cues: {curiosity: 4.6, numbers: 7.5, platform: 9.9},
    streams: [{logo: 'netflix.png', name: 'Netflix'}],
  },
];

// Linha do tempo (frames a 30fps) — 45s no total, casada com a narração
import timeline from './timeline.json';
type Block = readonly [number, number];
export const T = timeline as unknown as Record<'hook' | 'data' | 'm1' | 'm2' | 'm3' | 'spielberg' | 'brasil' | 'cta', Block>;
export const TOTAL = timeline.total;
