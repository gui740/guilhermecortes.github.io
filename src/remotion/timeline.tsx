import React from 'react';
import words from '../words.json';
import wordsB from '../words_B.json';
import wordsC from '../words_C.json';
import {Scene, Tok, Layer, Block, SceneView} from './engine';

type Wd = {w: string; s: number; e: number; line: string};
const norm = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');

// Cria um "tokenizador" sequencial sobre uma lista de palavras com timestamps.
const mk = (WL: Wd[]) => {
  let ptr = 0;
  // A/P = fonte; texto pode ter várias palavras ("THE RAID") — o tempo é o da 1ª palavra.
  const w = (text: string, f: 'A' | 'P', s: number, hl = false): Tok => {
    const first = norm(text.split(' ')[0]);
    for (let k = ptr; k < Math.min(WL.length, ptr + 10); k++) {
      if (norm(WL[k].w) === first) {
        ptr = k + text.split(' ').length;
        return {t: text, f, s, hl, at: WL[k].s};
      }
    }
    throw new Error(`palavra não encontrada: ${text} (ptr ${ptr} = ${WL[ptr]?.w})`);
  };
  const L = (id: string) => WL.find((x) => x.line === id)!.s;
  const at = (word: string, after = 0) => WL.find((x) => x.s >= after && norm(x.w) === norm(word))!.s;
  return {w, L, at};
};

const A = mk(words as Wd[]);
export const WORDS = words as Wd[];
export const NARR_END = WORDS[WORDS.length - 1].e;

// ---------- floresta de recortes da abertura ----------
const forest: Layer = {k: 'forest', items: [
  {src: 'fg_branches', x: 60, y: 560, h: 1300, z: 420, flip: true},
  {src: 'fg_branches', x: 1040, y: 820, h: 1300, z: 330},
  {src: 'fg_fence', x: 540, y: 1780, h: 520, z: 260},
  {src: 'fg_branches', x: -20, y: 1550, h: 1100, z: 180, rot: 160},
  {src: 'fg_branches', x: 1100, y: 250, h: 1000, z: 120, flip: true, rot: 200},
  {src: 'fg_branches', x: 980, y: 1500, h: 900, z: 40, rot: -20},
]};

// ---------- GANCHO (3 versões) ----------
const hookA = (X: ReturnType<typeof mk>, from: number, to: number, cut: number): Scene => ({
  id: 'hook', from, to, dir: 1, push: 90, opening: true,
  blocks: [
    {from, to: cut, bg: 'gray', exit: 'flip',
      lines: [[X.w('Três', 'A', 330), X.w('filmes', 'P', 130), X.w('de', 'P', 80)], [X.w('RITUAL', 'A', 330, true)], [X.w('que', 'P', 72), X.w('cê', 'P', 72), X.w('NUNCA', 'A', 160), X.w('VIU', 'A', 160)]],
      layers: [
        {k: 'grid', z: -1300},
        {k: 'symbol', x: 540, y: 1180, size: 980, z: -1000, at: 0.37, dur: 1.6},
        {k: 'cut', src: 'p_fence', x: 540, y: 1470, h: 700, z: -760},
        {k: 'smoke', z: -650, seed: 2},
        {k: 'flames', x: 540, y: 1800, w: 1250, h: 520, z: -220},
        {k: 'cut', src: 'a_robed', x: 540, y: 1560, h: 800, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 3},
        forest,
      ]},
    {from: cut, to, bg: 'black', exit: 'push',
      lines: [[X.w('e', 'P', 80), X.w('o', 'P', 80), X.w('último', 'P', 170)], [X.w('AMALDIÇOA', 'A', 300, true)], [X.w('quem', 'P', 90), X.w('ASSISTE', 'A', 170)]],
      layers: [
        {k: 'symbol', x: 540, y: 1180, size: 1000, z: -900, at: cut + 0.05, dur: 1.2, color: '#F2E63A'},
        {k: 'cut', src: 'p_temple', x: 540, y: 1420, h: 760, z: -760},
        {k: 'smoke', z: -600, seed: 5},
        {k: 'cut', src: 'i_face', x: 540, y: 1510, h: 950, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 4},
        {k: 'cut', src: 'fg_branches', x: 1040, y: 1720, h: 1350, z: 260, rot: -25, anim: 'sway'},
      ]},
  ],
});

const hookB = (X: ReturnType<typeof mk>, from: number, to: number, cut: number): Scene => ({
  id: 'hook', from, to, dir: 1, push: 90, opening: true,
  blocks: [
    {from, to: cut, bg: 'gray', exit: 'flip',
      lines: [[X.w('Se', 'P', 90), X.w('cê', 'P', 90), X.w('achou', 'P', 130)], [X.w('MIDSOMMAR', 'A', 300, true)], [X.w('PESADO,', 'A', 200)]],
      layers: [
        {k: 'grid', z: -1300},
        {k: 'symbol', x: 540, y: 1180, size: 980, z: -1000, at: 0.37, dur: 1.4},
        {k: 'cut', src: 'p_fence', x: 540, y: 1470, h: 700, z: -760},
        {k: 'flames', x: 540, y: 1800, w: 1250, h: 520, z: -220},
        {k: 'cut', src: 'a_robed', x: 540, y: 1560, h: 800, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 3}, forest,
      ]},
    {from: cut, to, bg: 'red', exit: 'push',
      lines: [[X.w('a', 'P', 80), X.w('gente', 'P', 110), X.w('separou', 'P', 150)], [X.w('COISA', 'A', 300)], [X.w('PIOR', 'A', 330, true)]],
      layers: [
        {k: 'star', x: 540, y: 1330, size: 1050, z: -600, at: cut + 0.05},
        {k: 'cut', src: 'p_village', x: 540, y: 1420, h: 640, z: -850},
        {k: 'cut', src: 'e_mask', x: 600, y: 1640, h: 900, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 6},
        {k: 'cut', src: 'fg_branches', x: 1040, y: 1720, h: 1350, z: 260, rot: -25, anim: 'sway'},
      ]},
  ],
});

const hookC = (X: ReturnType<typeof mk>, from: number, to: number, cut: number): Scene => ({
  id: 'hook', from, to, dir: 1, push: 90, opening: true,
  blocks: [
    {from, to: cut, bg: 'gray', exit: 'flip',
      lines: [[X.w('Três', 'A', 330), X.w('VILAS', 'A', 330, true)], [X.w('onde', 'P', 80), X.w('cê', 'P', 80), X.w('NUNCA', 'A', 200)], [X.w('devia', 'P', 110), X.w('ENTRAR,', 'A', 200)]],
      layers: [
        {k: 'grid', z: -1300},
        {k: 'cut', src: 'p_village', x: 540, y: 1450, h: 720, z: -800},
        {k: 'smoke', z: -650, seed: 2},
        {k: 'cut', src: 'a_hill', x: 560, y: 1480, h: 820, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 3}, forest,
      ]},
    {from: cut, to, bg: 'black', exit: 'push',
      lines: [[X.w('e', 'P', 80), X.w('a', 'P', 80), X.w('última', 'P', 170)], [X.w('te', 'P', 100), X.w('LEVA', 'A', 300, true)], [X.w('JUNTO', 'A', 250)]],
      layers: [
        {k: 'symbol', x: 540, y: 1180, size: 1000, z: -900, at: cut + 0.05, dur: 1.2, color: '#F2E63A'},
        {k: 'cut', src: 'p_village', x: 540, y: 1420, h: 640, z: -800},
        {k: 'flames', x: 540, y: 1800, w: 1250, h: 480, z: -220},
        {k: 'cut', src: 'a_preacher', x: 540, y: 1560, h: 900, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 4},
      ]},
  ],
});

export const HOOK_CUT = A.at('e', 1.33) - 0.06;
export const sHook = hookA(A, 0, 4.46, HOOK_CUT);

// ---------- FILME 3: ERREMENTARI ----------
const sE: Scene = {
  id: 'e', from: 4.46, to: 10.54, dir: -1, push: 90,
  tag: {text: 'Nº3 · ERREMENTARI · 2017 · ESPANHA', from: A.at('Errementari')},
  blocks: [
    {from: 4.46, to: 5.84, bg: 'red', exit: 'flip', textTop: 360,
      lines: [[A.w('Errementari', 'P', 210)]],
      layers: [
        {k: 'cut', src: 'p_village', x: 540, y: 1430, h: 640, z: -900},
        {k: 'smoke', z: -750, seed: 7},
        {k: 'star', x: 540, y: 1330, size: 1080, z: -600, at: A.at('Errementari')},
        {k: 'num', text: '3', x: 760, y: 760, size: 900, z: -480, at: A.L('t3')},
        {k: 'cut', src: 'e_smith', x: 580, y: 1430, h: 1000, z: -90, anim: 'breath'},
        {k: 'dust', z: -200, seed: 8},
        {k: 'cut', src: 'fg_branches', x: 1040, y: 1720, h: 1350, z: 260, rot: -25, anim: 'sway'},
      ]},
    {from: 5.84, to: 8.08, bg: 'gray', exit: 'push',
      lines: [[A.w('um', 'P', 80), A.w('FERREIRO', 'A', 240)], [A.w('basco', 'P', 120), A.w('mantém', 'P', 120), A.w('o', 'P', 80)], [A.w('DIABO', 'A', 330, true), A.w('preso.', 'P', 110)]],
      layers: [
        {k: 'grid', z: -1300},
        {k: 'cut', src: 'p_forest', x: 540, y: 1350, h: 720, z: -850},
        {k: 'flames', x: 540, y: 1780, w: 1250, h: 480, z: -200},
        {k: 'cut', src: 'e_mask', x: 560, y: 1460, h: 980, z: -90, anim: 'breath'},
        {k: 'dust', z: -180, seed: 9},
        {k: 'cut', src: 'fg_fence', x: 540, y: 1830, h: 620, z: 280, anim: 'sway'},
      ]},
    {from: 8.08, to: 10.54, bg: 'black', exit: 'flip', textTo: A.at('Netflix', 8.98) - 0.02,
      lines: [[A.w('falado', 'P', 110), A.w('num', 'P', 80)], [A.w('DIALETO', 'A', 300, true)], [A.w('que', 'P', 80), A.w('nem', 'P', 80), A.w('existe', 'P', 110), A.w('MAIS.', 'A', 190)]],
      layers: [
        {k: 'cut', src: 'p_fence', x: 540, y: 1370, h: 760, z: -850},
        {k: 'smoke', z: -700, seed: 10},
        {k: 'cut', src: 'e_girl', x: 740, y: 1470, h: 940, z: -90, anim: 'breath'},
        {k: 'logo', x: 540, y: 470, w: 760, z: -300, at: A.at('Netflix', 8.98)},
        {k: 'cut', src: 'poster_e', x: 250, y: 1240, h: 380, z: -300, pop: A.at('Netflix', 8.98), rot: -5},
        {k: 'dash', x1: 300, y1: 1040, x2: 560, y2: 700, z: -300, at: A.at('Netflix', 8.98) + 0.08},
        {k: 'dust', z: -150, seed: 11},
        {k: 'cut', src: 'fg_branches', x: 40, y: 1720, h: 1350, z: 260, flip: true, rot: 25, anim: 'sway'},
      ]},
  ],
};

// ---------- ponte: "Estranho? O dois é pior." ----------
const sTwo: Scene = {
  id: 'two', from: 10.54, to: 12.52, dir: 1, push: 80,
  blocks: [
    {from: 10.54, to: 12.52, bg: 'gray', exit: 'flip',
      lines: [[A.w('ESTRANHO?', 'A', 250)], [A.w('o', 'P', 90), A.w('DOIS', 'A', 260)], [A.w('é', 'P', 90), A.w('PIOR.', 'A', 330, true)]],
      layers: [
        {k: 'symbol', x: 540, y: 1200, size: 980, z: -1000, at: 10.69, dur: 1.4},
        {k: 'cut', src: 'p_village', x: 540, y: 1400, h: 650, z: -850},
        {k: 'num', text: '2', x: 760, y: 900, size: 950, z: -480, at: A.at('dois', 9.79)},
        {k: 'cut', src: 'a_preacher', x: 540, y: 1560, h: 900, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 12},
        {k: 'cut', src: 'fg_branches', x: 1040, y: 1720, h: 1350, z: 260, rot: -25, anim: 'sway'},
      ]},
  ],
};

// ---------- FILME 2: APÓSTOLO ----------
const sA: Scene = {
  id: 'a', from: 12.52, to: 17.68, dir: -1, push: 90,
  tag: {text: 'Nº2 · APÓSTOLO · 2018 · REINO UNIDO', from: A.at('Apóstolo')},
  blocks: [
    {from: 12.52, to: 13.80, bg: 'red', exit: 'push',
      lines: [[A.w('Apóstolo', 'P', 230)], [A.w('um', 'P', 80), A.w('cara', 'P', 80), A.w('INVADE', 'A', 210, true), A.w('uma', 'P', 80)]],
      layers: [
        {k: 'cut', src: 'p_moor', x: 540, y: 1420, h: 640, z: -900},
        {k: 'star', x: 540, y: 1330, size: 1080, z: -600, at: A.at('Apóstolo')},
        {k: 'cut', src: 'a_dan', x: 560, y: 1450, h: 980, z: -90, anim: 'breath'},
        {k: 'dust', z: -180, seed: 13},
        {k: 'cut', src: 'fg_branches', x: 40, y: 1720, h: 1350, z: 260, flip: true, rot: 25, anim: 'sway'},
      ]},
    {from: 13.80, to: 15.88, bg: 'gray', exit: 'flip',
      lines: [[A.w('ILHA', 'A', 300)], [A.w('pra', 'P', 80), A.w('resgatar', 'P', 110), A.w('a', 'P', 80), A.w('irmã', 'P', 110)], [A.w('de', 'P', 75), A.w('uma', 'P', 75), A.w('SEITA.', 'A', 300, true)]],
      layers: [
        {k: 'grid', z: -1300},
        {k: 'cut', src: 'p_moor', x: 540, y: 1390, h: 760, z: -820},
        {k: 'cut', src: 'a_walkers', x: 250, y: 1320, h: 300, z: -480, anim: 'float'},
        {k: 'smoke', z: -600, seed: 14},
        {k: 'cut', src: 'a_hill', x: 760, y: 1500, h: 820, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 15},
        {k: 'cut', src: 'fg_branches', x: 1040, y: 1720, h: 1350, z: 260, rot: -25, anim: 'sway'},
      ]},
    {from: 15.88, to: 17.68, bg: 'black', exit: 'flip', textTo: A.at('Netflix', 16.39) - 0.02,
      lines: [[A.w('do', 'P', 90), A.w('diretor', 'P', 130), A.w('de', 'P', 90)], [A.w('THE RAID.', 'A', 280, true)]],
      layers: [
        {k: 'symbol', x: 600, y: 1200, size: 1000, z: -1000, at: 15.97, dur: 1.4},
        {k: 'smoke', z: -700, seed: 16},
        {k: 'flames', x: 620, y: 1850, w: 1300, h: 640, z: -220},
        {k: 'cut', src: 'a_robed', x: 660, y: 1440, h: 860, z: -90, anim: 'breath'},
        {k: 'logo', x: 540, y: 470, w: 760, z: -300, at: A.at('Netflix', 16.39)},
        {k: 'cut', src: 'poster_a', x: 250, y: 1240, h: 380, z: -300, pop: A.at('Netflix', 16.39), rot: 4},
        {k: 'dash', x1: 300, y1: 1040, x2: 560, y2: 700, z: -300, at: A.at('Netflix', 16.39) + 0.08},
        {k: 'dust', z: -150, seed: 17},
      ]},
  ],
};

// ---------- ENVIO ----------
const sShare: Scene = {
  id: 'share', from: 17.68, to: 20.52, dir: 1, push: 90,
  blocks: [
    {from: 17.68, to: 18.96, bg: 'red', exit: 'push',
      lines: [[A.w('MANDA', 'A', 300)], [A.w('pro', 'P', 100), A.w('AMIGO', 'A', 300, true)], [A.w('que', 'P', 90), A.w('vive', 'P', 90), A.w('querendo', 'P', 120)]],
      layers: [
        {k: 'cut', src: 'p_village', x: 540, y: 1420, h: 640, z: -880},
        {k: 'smoke', z: -700, seed: 18},
        {k: 'cut', src: 'a_book', x: 560, y: 1470, h: 980, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 19},
        {k: 'cut', src: 'fg_branches', x: 40, y: 1720, h: 1350, z: 260, flip: true, rot: 25, anim: 'sway'},
      ]},
    {from: 18.96, to: 20.52, bg: 'gray', exit: 'flip',
      lines: [[A.w('ACAMPAR', 'A', 290)], [A.w('no', 'P', 75), A.w('meio', 'P', 75), A.w('do', 'P', 75), A.w('NADA.', 'A', 300, true)]],
      layers: [
        {k: 'grid', z: -1300},
        {k: 'cut', src: 'p_forest', x: 540, y: 1370, h: 720, z: -850},
        {k: 'tent', x: 250, y: 1560, w: 330, z: -380},
        {k: 'flames', x: 420, y: 1600, w: 170, h: 170, z: -380, n: 4},
        {k: 'cut', src: 'a_hill', x: 760, y: 1520, h: 780, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 20},
        {k: 'cut', src: 'fg_fence', x: 540, y: 1840, h: 620, z: 280, anim: 'sway'},
      ]},
  ],
};

// ---------- FILME 1: MARCAS DA MALDIÇÃO ----------
const sI: Scene = {
  id: 'i', from: 20.52, to: 26.70, dir: -1, push: 90,
  tag: {text: 'Nº1 · MARCAS DA MALDIÇÃO · 2022 · TAIWAN', from: A.at('Marcas')},
  blocks: [
    {from: 20.52, to: 22.92, bg: 'black', exit: 'push',
      lines: [[A.w('Marcas', 'P', 200), A.w('da', 'P', 110)], [A.w('Maldição,', 'P', 220)], [A.w('de', 'P', 80), A.w('TAIWAN.', 'A', 180, true)]],
      layers: [
        {k: 'cut', src: 'p_temple', x: 540, y: 1420, h: 760, z: -900},
        {k: 'smoke', z: -700, seed: 21},
        {k: 'star', x: 540, y: 1330, size: 1050, z: -600, at: A.at('Marcas')},
        {k: 'num', text: '1', x: 790, y: 820, size: 950, z: -480, at: A.at('um', 20.07)},
        {k: 'tv', x: 540, y: 1080, w: 700, z: -150, until: 21.12, render: () => <SceneView S={sShare} T={20.20} />},
        {k: 'cut', src: 'i_flash', x: 560, y: 1500, h: 1000, z: -90, anim: 'breath', pop: 21.16},
        {k: 'dust', z: -150, seed: 22},
      ]},
    {from: 22.92, to: 24.16, bg: 'gray', exit: 'flip',
      lines: [[A.w('baseado', 'P', 130), A.w('num', 'P', 90)], [A.w('CASO', 'A', 300)], [A.w('REAL,', 'A', 330, true)]],
      layers: [
        {k: 'grid', z: -1300},
        {k: 'cut', src: 'p_temple', x: 540, y: 1390, h: 800, z: -850},
        {k: 'cut', src: 'i_woman', x: 560, y: 1590, h: 980, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 23},
        {k: 'cut', src: 'fg_branches', x: 1040, y: 1720, h: 1350, z: 260, rot: -25, anim: 'sway'},
      ]},
    {from: 24.16, to: 26.70, bg: 'red', exit: 'flip', textTo: A.at('Netflix', 24.90) - 0.02,
      lines: [[A.w('e', 'P', 80), A.w('ele', 'P', 80), A.w('te', 'P', 80), A.w('pede', 'P', 80), A.w('pra', 'P', 80)], [A.w('REPETIR', 'A', 280)], [A.w('a', 'P', 90), A.w('REZA.', 'A', 330, true)]],
      layers: [
        {k: 'symbol', x: 560, y: 1230, size: 980, z: -560, at: 24.26, dur: 1.6, color: '#FFFFFF'},
        {k: 'cut', src: 'i_hands', x: 600, y: 1580, h: 900, z: -90, anim: 'breath'},
        {k: 'logo', x: 540, y: 470, w: 760, z: -300, at: A.at('Netflix', 24.90)},
        {k: 'cut', src: 'poster_i', x: 250, y: 1240, h: 380, z: -300, pop: A.at('Netflix', 24.90), rot: -4},
        {k: 'dash', x1: 300, y1: 1040, x2: 560, y2: 700, z: -300, at: A.at('Netflix', 24.90) + 0.08},
        {k: 'dust', z: -150, seed: 24},
        {k: 'cut', src: 'fg_branches', x: 40, y: 1720, h: 1350, z: 260, flip: true, rot: 25, anim: 'sway'},
      ]},
  ],
};

// ---------- FECHO ----------
export const END_CTA_TO = 30.00;
const sEnd: Scene = {
  id: 'end', from: 26.70, to: END_CTA_TO, dir: 1, push: 90,
  blocks: [
    {from: 26.70, to: 28.04, bg: 'black', exit: 'push',
      lines: [[A.w('cê', 'P', 120), A.w('REPETIRIA', 'A', 230, true)], [A.w('ou', 'P', 110), A.w('FUGIA?', 'A', 330)]],
      layers: [
        {k: 'symbol', x: 540, y: 1200, size: 1000, z: -900, at: 26.75, dur: 1.2},
        {k: 'smoke', z: -700, seed: 25},
        {k: 'cut', src: 'i_face', x: 540, y: 1590, h: 940, z: -90, anim: 'breath'},
        {k: 'dust', z: -150, seed: 26},
        {k: 'cut', src: 'fg_branches', x: 1040, y: 1720, h: 1350, z: 260, rot: -25, anim: 'sway'},
      ]},
    {from: 28.04, to: END_CTA_TO, bg: 'gray', exit: 'flip', textTo: 99,
      lines: [[A.w('SEGUE', 'A', 260), A.w('a', 'P', 90)], [A.w('TALKING', 'A', 290)], [A.w('HORROR.', 'A', 300, true)]],
      layers: [
        {k: 'grid', z: -1300},
        {k: 'symbol', x: 540, y: 1250, size: 1000, z: -1000, at: 28.06, dur: 1.4},
        {k: 'flames', x: 540, y: 1800, w: 1250, h: 460, z: -400},
        {k: 'cut', src: 'poster_e', x: 230, y: 1520, h: 400, z: -260, rot: -8, pop: 28.11},
        {k: 'cut', src: 'poster_i', x: 850, y: 1520, h: 400, z: -260, rot: 8, pop: 28.23},
        {k: 'cut', src: 'poster_a', x: 540, y: 1560, h: 450, z: -90, anim: 'breath', pop: 28.16},
        {k: 'dust', z: -150, seed: 27},
        {k: 'cut', src: 'fg_fence', x: 540, y: 1840, h: 620, z: 280, anim: 'sway'},
      ]},
  ],
};

export const SCENES: Scene[] = [sHook, sE, sTwo, sA, sShare, sI, sEnd];
export const TRANSITIONS: {at: number; kind: 'cross' | 'whip' | 'tv'}[] = [
  {at: 4.46, kind: 'cross'}, {at: 10.54, kind: 'whip'}, {at: 12.52, kind: 'cross'}, {at: 17.68, kind: 'whip'}, {at: 20.52, kind: 'tv'},
  {at: 26.70, kind: 'whip'},
];
export const LOOP_START = END_CTA_TO, TOTAL = +(END_CTA_TO + 1.05).toFixed(2);

// ganchos alternativos (3s cada)
const XB = mk(wordsB as Wd[]), XC = mk(wordsC as Wd[]);
const XA = mk(words as Wd[]);
export const HOOKS = {
  A: {dur: 4.1, scene: hookA(XA, 0, 4.1, XA.at('e', 1.33) - 0.06), audio: 'audio/narracao.wav'},
  B: {dur: 3.95, scene: hookB(XB, 0, 3.95, XB.at('a', 1.2) - 0.06), audio: 'audio/narracao_B.wav'},
  C: {dur: 3.9, scene: hookC(XC, 0, 3.9, XC.at('e', 1.5) - 0.06), audio: 'audio/narracao_C.wav'},
};
export const CAPTION_WORDS = {A: words as Wd[], B: wordsB as Wd[], C: wordsC as Wd[]};
