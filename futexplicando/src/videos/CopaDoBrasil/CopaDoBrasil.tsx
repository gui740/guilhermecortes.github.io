import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Legenda } from "../../cartoon/Legenda";
import { CENAS, D } from "./Cenas";

const XF = 6; // crossfade entre cenas (frames)

const Entra: React.FC<{ children: React.ReactNode; primeira: boolean }> = ({ children, primeira }) => {
  const f = useCurrentFrame();
  const o = primeira ? 1 : interpolate(f, [0, XF], [0, 1], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

/** "A história da Copa do Brasil" — cartoon explicativo. */
export const CopaDoBrasil: React.FC = () => {
  const { fps } = useVideoConfig();
  const fr = (t: number) => Math.round(t * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: "#111" }}>
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
      <Legenda palavras={D.legendas} y={1160} />
      <Audio src={staticFile(D.audio.mix)} />
    </AbsoluteFill>
  );
};
