import React from "react";
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import timeline from "./timeline.json";
import { C } from "./theme";
import { Cena } from "./cenas/Cenas";
import { Academico } from "./cenas/bits";

type Cn = { tipo: string; t: number; [k: string]: any };
type Tr = { tipo: string; id: string; start: number; dur: number; pre?: number; cenas: Cn[] };

const Trecho: React.FC<{ tr: Tr }> = ({ tr }) => {
  const { fps } = useVideoConfig();
  const total = Math.round(tr.dur * fps);
  const principais = tr.cenas.filter((c) => c.tipo !== "academico");
  const overlays = tr.cenas.filter((c) => c.tipo === "academico");
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      {principais.map((c, i) => {
        const from = Math.round(c.t * fps);
        const next = i + 1 < principais.length ? Math.round(principais[i + 1].t * fps) : total;
        return (
          <Sequence key={i} from={from} durationInFrames={Math.max(1, next - from)} layout="none">
            <AbsoluteFill>
              <Cena c={c} dur={(next - from) / fps} trecho={tr} />
            </AbsoluteFill>
          </Sequence>
        );
      })}
      {overlays.map((c, i) => (
        <Sequence key={"o" + i} from={Math.round(c.t * fps)} layout="none">
          <Academico texto={c.texto} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const Episodio: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: C.branco }}>
      {(timeline.trechos as Tr[]).map((tr) => (
        <Sequence key={tr.id} from={Math.round(tr.start * fps)} durationInFrames={Math.round(tr.dur * fps)}>
          <Trecho tr={tr} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
