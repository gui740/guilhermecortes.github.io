import {staticFile} from 'remotion';

export const W = 1080;
export const H = 1920;
// Margens de segurança (UI do Instagram)
export const SAFE = {top: 250, bottom: 420, right: 140, left: 80};

export const C = {
  G: '#EDEDED', // cinza-claro
  R: '#F23B3B', // vermelho
  K: '#1C1C1C', // preto-carvão
  Y: '#F2E63A', // amarelo de destaque
};

export type Bg = 'G' | 'R' | 'K';
// Texto preto no cinza, branco no vermelho, amarelo no preto
export const TEXT: Record<Bg, string> = {G: C.K, R: '#FFFFFF', K: C.Y};
// Uma palavra de destaque por bloco
export const HL: Record<Bg, string> = {G: C.R, R: C.K, K: C.R};

export const fontCss = `
@font-face{font-family:'Anton';src:url('${staticFile('fonts/Anton.woff2')}') format('woff2');font-weight:400;}
@font-face{font-family:'Playfair';src:url('${staticFile('fonts/PlayfairDisplay-Italic.woff2')}') format('woff2');font-style:italic;font-weight:400 900;}
@font-face{font-family:'Inter';src:url('${staticFile('fonts/Inter.woff2')}') format('woff2');font-weight:100 900;}
`;
