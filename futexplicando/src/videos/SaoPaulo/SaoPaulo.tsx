import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Captions } from "../../components/Captions";
import { Coin } from "../../components/Coin";
import { Seal } from "../../components/Graphics";
import { Grain, PaperBackground } from "../../components/Paper";
import { A, D } from "./data";
import { SceneHook, SceneVirada } from "./scenes/Intro";
import { SceneFe, SceneMorte } from "./scenes/MorteFe";
import { SceneMorumbi } from "./scenes/Morumbi";
import { SceneMundo } from "./scenes/Mundo";
import { SceneNascimento } from "./scenes/Nascimento";
import { SceneCta, SceneStat } from "./scenes/StatCta";

/** Moeda girando que atravessa a tela cobrindo o corte entre cenas. */
const CoinWipe: React.FC<{ at: number; i: number }> = ({ at, i }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps; // relativo ao início da Sequence (at - 0.35)
  const u = t / 0.7;
  const y = interpolate(u, [0, 1], [2350, -650]);
  const x = 540 + (i % 2 ? -1 : 1) * interpolate(u, [0, 1], [-260, 260]);
  const size = 780;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {[0.12, 0.06, 0].map((lag, k) => {
        const yy = interpolate(u - lag / 0.7, [0, 1], [2350, -650]);
        return (
          <div key={k} style={{ position: "absolute", left: x - size / 2, top: (k === 2 ? y : yy) - size / 2, opacity: k === 2 ? 1 : 0.25 }}>
            <Coin id={`wipe${i}-${k}`} size={size} angle={u * 16 + at} tilt={interpolate(u, [0, 1], [-25, 25])} crest={A.escudoAtual} blur={k === 2 ? 4 : 10} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const scenes = [
  { key: "gancho", C: SceneHook },
  { key: "virada", C: SceneVirada },
  { key: "nascimento", C: SceneNascimento },
  { key: "morte", C: SceneMorte },
  { key: "fe", C: SceneFe },
  { key: "morumbi", C: SceneMorumbi },
  { key: "mundo", C: SceneMundo },
  { key: "stat", C: SceneStat },
  { key: "cta", C: SceneCta },
] as const;

export const SaoPaulo: React.FC = () => {
  const { fps } = useVideoConfig();
  const fr = (t: number) => Math.round(t * fps);
  const cenas = D.cenas;
  const darkCaptions = [cenas.morumbi.inicio, cenas.morumbi.fim] as const;
  return (
    <AbsoluteFill style={{ backgroundColor: D.paleta.branco }}>
      <PaperBackground />
      {scenes.map(({ key, C }) => {
        const sc = cenas[key];
        return (
          <Sequence key={key} name={key} from={fr(sc.inicio)} durationInFrames={fr(sc.fim) - fr(sc.inicio)}>
            <C />
          </Sequence>
        );
      })}
      {D.transicoesMoeda.map((at, i) => (
        <Sequence key={at} name={`moeda-transicao-${i}`} from={fr(at - 0.35)} durationInFrames={fr(0.7)}>
          <CoinWipe at={at} i={i} />
        </Sequence>
      ))}
      <Sequence name="legendas (escuro)" from={fr(darkCaptions[0])} durationInFrames={fr(darkCaptions[1]) - fr(darkCaptions[0])}>
        <CaptionsAt offset={darkCaptions[0]} dark />
      </Sequence>
      <CaptionsLayer />
      <Seal handle={D.handle} />
      <Grain />
      <Audio src={staticFile(D.audio.mix)} />
    </AbsoluteFill>
  );
};

const words = D.legendas;

/** Legendas claras no vídeo inteiro (exceto gancho, virada, Morumbi e CTA). */
const CaptionsLayer: React.FC = () => {
  const c = D.cenas;
  return (
    <Captions
      words={words}
      hide={[
        [0, c.nascimento.inicio],
        [c.morumbi.inicio, c.morumbi.fim],
        [c.cta.inicio, 999],
      ]}
    />
  );
};

/** Legendas brancas (sobre a foto do Morumbi). */
const CaptionsAt: React.FC<{ offset: number; dark?: boolean }> = ({ offset, dark }) => {
  const shifted = words.map((w) => ({ ...w, start: w.start - offset, end: w.end - offset }));
  return <Captions words={shifted} dark={dark} />;
};
