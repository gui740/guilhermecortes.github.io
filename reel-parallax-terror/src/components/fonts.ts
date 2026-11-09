import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Fontes do Google Fonts (OFL) baixadas em assets/fonts/ — carregadas localmente (render offline).
const FONTES: [string, string, string][] = [
  ['Anton', '400', 'Anton-400.ttf'],
  ['Bebas Neue', '400', 'BebasNeue-400.ttf'],
  ['Permanent Marker', '400', 'PermanentMarker-400.ttf'],
  ['Caveat', '700', 'Caveat-700.ttf'],
  ['Inter', '800', 'Inter-800.ttf'],
  ['Inter', '900', 'Inter-900.ttf'],
  ['Special Elite', '400', 'SpecialElite-400.ttf'],
];
FONTES.forEach(([family, weight, file]) => {
  loadFont({family, weight, url: staticFile(`fonts/${file}`)});
});

export const F = {
  titulo: 'Anton',
  bebas: 'Bebas Neue',
  marker: 'Permanent Marker',
  caveat: 'Caveat',
  legenda: 'Inter',
  maquina: 'Special Elite',
};

export const COR = {
  preto: '#0b0806',
  papel: '#e8dcc0',
  papelEscuro: '#cdbb94',
  branco: '#f6f2e8',
  sangue: '#8B0000',
  vermelho: '#B3001B',
  vermelhoVivo: '#E01530',
};
