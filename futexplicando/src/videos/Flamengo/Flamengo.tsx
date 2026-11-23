import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Legenda } from "../../cartoon/Legenda";
import { Grain } from "../../components/Paper";
import { CENAS, D } from "./Cenas";
import { RemoWipe } from "./Elementos";

const XF = 6; // crossfade entre cenas (frames)
const COM_REMO = ["fundacao", "futebol", "zico", "gabigol", "nacao"]; // remo varre a tela nas viradas de época

const Entra: React.FC<{ children: React.ReactNode; primeira: boolean }> = ({ children, primeira }) => {
  const f = useCurrentFrame();
  const o = primeira ? 1 : interpolate(f, [0, XF], [0, 1], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

/** "A história do Flamengo" — mistura do estilo papel/fotos (1) com o cartoon explicativo (2). */
export const Flamengo: React.FC = () => {
  const { fps } = useVideoConfig();
  const fr = (t: number) => Math.round(t * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: "#111", ["--accent" as string]: "#C8102E", ["--accent2" as string]: "#C8102E" } as React.CSSProperties}>
      {D.cenas.map((c, i) => {
        const Cena = CENAS[c.id];
        const from = Math.max(0, fr(c.inicio) - (i ? XF : 0));
        const dur = fr(c.fim) - from;
        return (
          <Sequence key={c.id} name={`${String(i + 1).padStart(2, "0")} ${c.id}`} from={from} durationInFrames={dur}>
            <Entra primeira={i === 0}>
              <Cena />
            </Entra>
          </Sequence>
        );
      })}
      {D.cenas
        .filter((c) => COM_REMO.includes(c.id))
        .map((c) => (
          <Sequence key={`remo-${c.id}`} name={`remo ${c.id}`} from={fr(c.inicio) - 8} durationInFrames={14}>
            <RemoWipe dur={13} />
          </Sequence>
        ))}
      <Grain opacity={0.08} />
      <Legenda palavras={D.legendas} y={1160} />
      <Audio src={staticFile(D.audio.mix)} />
    </AbsoluteFill>
  );
};
