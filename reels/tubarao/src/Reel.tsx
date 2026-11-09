import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {MOVIES, T} from './data';
import {Ocean} from './components/Ocean';
import {Bite, Dive, FinWipe} from './components/Transitions';
import {Hook} from './scenes/Hook';
import {DataScene} from './scenes/DataScene';
import {MovieScene} from './scenes/MovieScene';
import {Brasil, CTA, Spielberg} from './scenes/Closing';
import {BODY, C} from './theme';

const S: React.FC<{at: readonly [number, number]; children: React.ReactNode}> = ({at, children}) => (
  <Sequence from={at[0]} durationInFrames={at[1]} premountFor={10}>
    {children}
  </Sequence>
);

/** Leve distorção ("lente d'água") em toda a imagem */
const Wobble: React.FC<{children: React.ReactNode}> = ({children}) => {
  const f = useCurrentFrame();
  const sx = 1 + Math.sin(f / 23) * 0.004;
  const sy = 1 + Math.cos(f / 19) * 0.004;
  const r = Math.sin(f / 37) * 0.15;
  return <AbsoluteFill style={{transform: `scale(${sx},${sy}) rotate(${r}deg)`}}>{children}</AbsoluteFill>;
};

export const Reel: React.FC = () => {
  return (
    <AbsoluteFill style={{background: C.abyss, fontFamily: BODY}}>
      <Ocean />
      <Wobble>
        <S at={T.hook}>
          <Hook />
        </S>
        <S at={T.data}>
          <DataScene />
        </S>
        <S at={T.m1}>
          <MovieScene m={MOVIES[0]} />
        </S>
        <S at={T.m2}>
          <MovieScene m={MOVIES[1]} />
        </S>
        <S at={T.m3}>
          <MovieScene m={MOVIES[2]} />
        </S>
        <S at={T.spielberg}>
          <Spielberg />
        </S>
        <S at={T.brasil}>
          <Brasil />
        </S>
        <S at={T.cta}>
          <CTA />
        </S>
      </Wobble>

      {/* transições centradas nos cortes */}
      <Sequence from={T.data[0] - 10} durationInFrames={20}>
        <FinWipe />
      </Sequence>
      <Sequence from={T.m1[0] - 11} durationInFrames={22}>
        <Dive />
      </Sequence>
      <Sequence from={T.m2[0] - 9} durationInFrames={18}>
        <Bite />
      </Sequence>
      <Sequence from={T.m3[0] - 10} durationInFrames={20}>
        <FinWipe />
      </Sequence>
      <Sequence from={T.spielberg[0] - 11} durationInFrames={22}>
        <Dive />
      </Sequence>
      <Sequence from={T.brasil[0] - 9} durationInFrames={18}>
        <Bite />
      </Sequence>
      <Sequence from={T.cta[0] - 10} durationInFrames={20}>
        <FinWipe />
      </Sequence>
    </AbsoluteFill>
  );
};
