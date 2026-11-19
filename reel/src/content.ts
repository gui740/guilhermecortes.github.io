// Conteúdo e agenda de textos (tudo derivado da timeline e dos timestamps por palavra do Whisper)
import tlG from './timeline.json';
import tlB from './timeline_gB.json';
import tlC from './timeline_gC.json';
import wG from './words.json';
import wB from './words_gB.json';
import wC from './words_gC.json';

export type Word = {key: string; w: string; s: number; e: number};
export type TL = typeof tlG;
export const HOOKS: Record<string, {tl: TL; words: Word[]}> = {
  g: {tl: tlG as TL, words: wG as Word[]},
  gB: {tl: tlB as TL, words: wB as Word[]},
  gC: {tl: tlC as TL, words: wC as Word[]},
  cover: {tl: tlG as TL, words: wG as Word[]},
};
const norm = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');
export const wordAt = (words: Word[], key: string, w: string, fallback: number) => {
  const x = words.find((q) => q.key === key && norm(q.w).startsWith(norm(w)));
  return x ? x.s : fallback;
};

export type Line = {small?: string; big: string; color?: 'white' | 'yellow' | 'red'};
export type HookCue = {line: Line; word: string};
export const HOOK_LINES: Record<string, HookCue[]> = {
  g: [
    {line: {big: '3 TERRORES'}, word: 'tres'},
    {line: {big: 'ESCONDIDOS', color: 'yellow'}, word: 'escondidos'},
    {line: {small: 'no seu', big: 'PRIME'}, word: 'prime'},
  ],
  gB: [
    {line: {small: 'paga', big: 'PRIME?'}, word: 'prime'},
    {line: {small: 'e só vê as', big: 'MESMAS COISAS', color: 'yellow'}, word: 'mesmas'},
    {line: {small: 'anota esses', big: '3'}, word: 'anota'},
  ],
  gC: [
    {line: {small: 'a gente achou', big: '3 TERRORES'}, word: 'tres'},
    {line: {big: 'ESCONDIDOS', color: 'yellow'}, word: 'escondidos'},
    {line: {small: 'no seu', big: 'PRIME'}, word: 'prime'},
  ],
};

export type Film = {
  n: '3' | '2' | '1'; id: 'ghost' | 'medium' | 'huesera';
  title: string; label: string; red?: boolean;
  kwA: Line & {word: string}; kwB: Line & {word: string};
  main: string; set: string; fg: string; fgKit?: boolean;
};
export const FILMS: Film[] = [
  {n: '3', id: 'ghost', title: 'Ghostland', label: '2018 · FRANÇA / CANADÁ',
    kwA: {small: 'cheia de', big: 'BONECAS', color: 'yellow', word: 'bonecas'},
    kwB: {small: 'e ele vira', big: 'DO AVESSO', color: 'yellow', word: 'vira'},
    main: 'films/ghost_main.png', set: 'films/ghost_set.png', fg: 'films/ghost_fg.png'},
  {n: '2', id: 'medium', title: 'A Médium', label: '2021 · TAILÂNDIA / COREIA',
    kwA: {small: 'uma', big: 'XAMÃ', color: 'yellow', word: 'xama'},
    kwB: {small: 'documentário', big: 'REAL DEMAIS', color: 'yellow', word: 'documentario'},
    main: 'films/medium_main.png', set: 'films/medium_set.png', fg: 'films/medium_fg.png'},
  {n: '1', id: 'huesera', title: 'Huesera', label: '2022 · MÉXICO / PERU', red: true,
    kwA: {small: 'ouvir', big: 'OSSOS', color: 'yellow', word: 'ossos'},
    kwB: {small: 'estalamos o dedo', big: 'NUNCA MAIS', color: 'yellow', word: 'mais'},
    main: 'films/huesera_main.png', set: 'films/huesera_set.png', fg: 'kit/vhs_kaseta.png', fgKit: true},
];
// chave de áudio usada nos timestamps (Whisper ouviu "chamã" para "xamã")
export const KW_ALIASES: Record<string, string[]> = {xama: ['xama', 'chama', 'machama'], mais: ['mais']};
