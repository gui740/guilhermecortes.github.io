import React from 'react';
import {AbsoluteFill, Audio, Easing, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {CENAS, TIMING} from './config/cenas';
import {ORDEM, TRANSICAO, CenaId} from './config/timing';
import {Hook} from './scenes/Hook';
import {Possum} from './scenes/Possum';
import {Calvaire} from './scenes/Calvaire';
import {Hagazussa} from './scenes/Hagazussa';
import {Outro, CARDS, ESC, estiloCard} from './scenes/Outro';
import {TornReveal} from './components/TornReveal';
import {Captions} from './components/Captions';
import {FilmGrain} from './components/FilmGrain';
import {listaSfx} from './sfx';
import {prog} from './components/util';

const io = Easing.inOut(Easing.cubic);

/** Transições feitas pelos próprios elementos da colagem (nada de fade). */
const Transicao: React.FC<{id: CenaId; children: React.ReactNode}> = ({id, children}) => {
  const f = useCurrentFrame();
  const c = CENAS[id];
  if (id === 'possum') {
    // câmera "corre" seguindo a seta para a direita
    const p = prog(f, c.saida, c.duracao, io);
    return <AbsoluteFill style={{transform: `translateX(${-1080 * p}px)`}}>{children}</AbsoluteFill>;
  }
  if (id === 'calvaire') {
    // chega da direita (continuação do movimento) e sai rasgando o papel
    const p = prog(f, 0, TRANSICAO, io);
    return (
      <AbsoluteFill style={{transform: `translateX(${1080 * (1 - p)}px)`}}>
        <TornReveal inicio={c.saida} dur={TRANSICAO}>{children}</TornReveal>
      </AbsoluteFill>
    );
  }
  if (id === 'hagazussa') {
    // câmera se afasta: a cena encolhe e vira o 3º quadro do mural
    const p = prog(f, c.saida, c.duracao, io);
    if (p <= 0) return <AbsoluteFill>{children}</AbsoluteFill>;
    const k = CARDS.hagazussa;
    const s = 1 + (ESC - 1) * p;
    return (
      <AbsoluteFill style={{transform: `translate(${(k.x - 540) * p}px, ${(k.y - 960) * p}px) rotate(${k.rot * p}deg) scale(${s})`, transformOrigin: '540px 960px', overflow: 'hidden', ...estiloCard(p)}}>
        {children}
      </AbsoluteFill>
    );
  }
  return <AbsoluteFill>{children}</AbsoluteFill>;
};

const CENA: Record<CenaId, React.FC> = {gancho: Hook, possum: Possum, calvaire: Calvaire, hagazussa: Hagazussa, fechamento: Outro};

// intervalos (frames absolutos) com voz, para o ducking da trilha
const VOZ = ORDEM.map((id) => {
  const c = CENAS[id];
  const a = c.inicio + c.narr0;
  return [a, a + Math.round(c.narrDur * 30)] as const;
});
// Trilha: "Hitman" — Kevin MacLeod (incompetech.com), CC BY 4.0. Começa no trecho com groove (50s).
const TRILHA_INICIO_S = 50;
const VOL_TRILHA = 0.34;  // sem voz (respiros/transições): a música aparece
const VOL_DUCK = 0.17;    // com voz: fica por baixo (~-6 dB)
const volumeTrilha = (f: number) => {
  let duck = 0;
  for (const [a, b] of VOZ) {
    const d = f < a ? a - f : f > b ? f - b : 0;
    duck = Math.max(duck, interpolate(d, [0, 12], [1, 0], {extrapolateRight: 'clamp'}));
  }
  const fade = interpolate(f, [0, 12, TIMING.total - 40, TIMING.total], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (VOL_TRILHA + (VOL_DUCK - VOL_TRILHA) * duck) * fade;
};

const SFX = listaSfx();

export const Reel: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    {ORDEM.map((id, i) => {
      const c = CENAS[id];
      const Comp = CENA[id];
      return (
        <Sequence key={id} from={c.inicio} durationInFrames={c.duracao} name={id} style={{zIndex: 10 - i}}>
          <Transicao id={id}>
            <Comp />
          </Transicao>
        </Sequence>
      );
    })}
    <Captions />
    <FilmGrain opacidade={0.08} />

    {/* ÁUDIO: narração na frente, trilha por baixo com ducking, SFX nas entradas */}
    {ORDEM.map((id) => (
      <Sequence key={'n' + id} from={CENAS[id].inicio + CENAS[id].narr0} name={'voz ' + id}>
        <Audio src={staticFile(`narracao/${id}.wav`)} volume={1} />
      </Sequence>
    ))}
    <Audio src={staticFile('trilha/hitman.mp3')} startFrom={TRILHA_INICIO_S * 30} volume={volumeTrilha} />
    {SFX.map((s, i) => (
      <Sequence key={'s' + i} from={s.f} durationInFrames={60} name={'sfx ' + s.s}>
        <Audio src={staticFile(`sfx/${s.s}.wav`)} volume={s.v * 0.8} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
