import React from 'react';
import {AbsoluteFill} from 'remotion';
import {SceneView, Scene, COL} from './engine';
import {Grain} from './Reel';

// Capa 1080x1920: fundo vermelho, recortes em camadas, título em 5 palavras enormes.
const capa: Scene = {
  id: 'capa', from: 0, to: 10, dir: 1, push: 0, drift: 0,
  blocks: [{from: 0, to: 10, bg: 'red', textTop: 300,
    lines: [
      [{t: 'FOLK', f: 'A', s: 360, at: 0}, {t: 'HORROR', f: 'A', s: 360, at: 0, hl: true}],
      [{t: 'escondido', f: 'P', s: 210, at: 0}],
      [{t: 'na', f: 'P', s: 120, at: 0}, {t: 'NETFLIX', f: 'A', s: 300, at: 0}],
    ],
    layers: [
      {k: 'star', x: 540, y: 1260, size: 1150, z: -600, at: -5},
      {k: 'cut', src: 'p_village', x: 540, y: 1300, h: 640, z: -900},
      {k: 'cut', src: 'e_mask', x: 230, y: 1450, h: 760, z: -200, rot: -6},
      {k: 'cut', src: 'i_face', x: 860, y: 1450, h: 760, z: -200, rot: 6},
      {k: 'flames', x: 540, y: 1920, w: 1300, h: 420, z: -150},
      {k: 'cut', src: 'a_robed', x: 540, y: 1560, h: 820, z: -90},
      {k: 'cut', src: 'fg_branches', x: 1010, y: 1750, h: 1300, z: 260, rot: -25},
      {k: 'cut', src: 'fg_branches', x: 40, y: 300, h: 1200, z: 260, flip: true},
    ]}],
};

export const Capa: React.FC = () => (
  <AbsoluteFill style={{background: COL.red}}>
    <SceneView S={capa} T={1} />
    
  </AbsoluteFill>
);
