// Todos os dados abaixo foram conferidos em 09/11/2026. Fontes em ../FONTES.md
export const FPS = 30;

export type Pin = {
  lon: number;
  lat: number;
  label: string;
  kind: 'story' | 'filmed';
};

export type Stream = {logo: string; name: string};

export type Movie = {
  tag: string;
  title: string;
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
};

export const MOVIES: Movie[] = [
  {
    tag: '1/3 · O CLÁSSICO · PRAIA',
    title: 'TUBARÃO',
    year: 1975,
    poster: 'tubarao.jpg',
    curiosity:
      'O tubarão mecânico vivia quebrando. Spielberg teve que esconder o bicho.',
    counter: {prefix: 'US$ ', value: 490, decimals: 0, suffix: ' MI'},
    counterLabel: 'de bilheteria no mundo',
    counterNote: 'custou cerca de US$ 7 mi',
    map: {
      center: [-71.2, 41.6],
      scale: 5200,
      pins: [{lon: -70.61, lat: 41.39, label: "MARTHA'S VINEYARD", kind: 'filmed'}],
      legend: {
        story: 'Amity: a ilha não existe',
        filmed: "Martha's Vineyard (EUA)",
      },
    },
    streams: [{logo: 'amazontelecine.png', name: 'Telecine · Prime Video Channels'}],
  },
  {
    tag: '2/3 · ANOS 2010 · MAR ABERTO',
    title: 'MEGATUBARÃO',
    year: 2018,
    poster: 'meg.jpg',
    curiosity:
      'A Warner construiu tanques gigantes na Nova Zelândia só pra ele.',
    counter: {prefix: 'US$ ', value: 529, decimals: 0, suffix: ' MI'},
    counterLabel: 'de bilheteria no mundo',
    counterNote: 'mais que Tubarão (sem contar a inflação) 💀',
    map: {
      center: [142, -9],
      scale: 640,
      pins: [
        {lon: 109.5, lat: 18.25, label: 'SANYA, CHINA', kind: 'story'},
        {lon: 174.76, lat: -36.85, label: 'AUCKLAND, NZ', kind: 'filmed'},
      ],
      legend: {
        story: 'costa da China (Sanya)',
        filmed: '94% na Nova Zelândia',
      },
    },
    streams: [
      {logo: 'max.png', name: 'HBO Max'},
      {logo: 'amazonuniversalplus.png', name: 'Universal+ · Prime Video Channels'},
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
    streams: [{logo: 'netflix.png', name: 'Netflix'}],
  },
];

// Linha do tempo (frames a 30fps) — 43s no total
export const T = {
  hook: [0, 75],
  data: [75, 135],
  m1: [210, 255],
  m2: [465, 255],
  m3: [720, 255],
  spielberg: [975, 90],
  brasil: [1065, 90],
  cta: [1155, 135],
} as const;
export const TOTAL = 1290;
