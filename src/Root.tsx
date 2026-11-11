import React from 'react';
import {Composition, Still} from 'remotion';
import timeline from './data/timeline.json';
import {Reel, Hook, Capa} from './Reel';

const T = timeline as any;
const f = (s: number) => Math.round(s * 30);

// Ganchos alternativos usam trechos reais da narração (sem TTS)
export const HOOKS: Record<string, [number, number][]> = {
  A: [[0, 90]],                                     // "Pais levaram os filhos pequenos pra ver esse unicórnio no cinema…"
  B: [[T.blocks[4].start, T.blocks[4].start + 87]], // "É Buddy, um dos filmes de terror mais comentados do ano"
  C: [[T.blocks[12].start, T.blocks[12].end], [T.blocks[13].start, T.blocks[13].start + (90 - (T.blocks[12].end - T.blocks[12].start))]], // "Parecia infantil. Não era." + "Resultado: criançada chorando…"
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Reel" component={Reel} durationInFrames={T.total} fps={30} width={1080} height={1920} />
    {Object.entries(HOOKS).map(([k, segs]) => (
      <Composition key={k} id={`Gancho${k}`} component={Hook as any} defaultProps={{segs}} durationInFrames={segs.reduce((a, [x, y]) => a + y - x, 0)} fps={30} width={1080} height={1920} />
    ))}
    <Still id="Capa" component={Capa} width={1080} height={1920} />
  </>
);
