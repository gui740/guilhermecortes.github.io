import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { TITLE } from "../lib/fonts";
import { shake } from "./motion";
import { Sfx } from "./Sfx";

type Props = {
  lines: string[];
  at: number[]; // frame em que cada linha bate
  highlight?: string;
  color: string;
  highlightColor: string;
  highlightBg: string;
  whoosh?: string;
  impact?: string;
  size?: number;
  silent?: boolean;
};

/** Texto gigante batendo na tela com shake leve + whoosh/impacto. */
export const Hook: React.FC<Props> = ({ lines, at, highlight, color, highlightColor, highlightBg, whoosh, impact, size = 250, silent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const last = at.reduce((acc, a) => (frame >= a ? a : acc), -999);
  const s = shake(frame, last, 22, 10);
  return (
    <div
      style={{
        display: "flex", flexDirection: "column", alignItems: "center", gap: 0,
        transform: `translate(${s.x}px, ${s.y}px) rotate(${s.r}deg)`,
      }}
    >
      {lines.map((line, i) => {
        const t = frame - at[i];
        const scale = interpolate(t, [0, 4, 7], [3.2, 0.92, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const o = interpolate(t, [0, 2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const hi = line === highlight;
        return (
          <div
            key={i}
            style={{
              fontFamily: TITLE, fontSize: size, lineHeight: 0.98, color: hi ? highlightColor : color, opacity: o,
              transform: `scale(${scale}) rotate(${i % 2 ? 2 : -2}deg)`, textTransform: "uppercase",
              background: hi ? highlightBg : "transparent", padding: hi ? "0 30px" : 0, marginTop: hi ? 18 : 0,
              textShadow: hi ? "none" : "8px 8px 0 rgba(0,0,0,0.25)",
            }}
          >
            {line}
          </div>
        );
      })}
      {!silent && at.map((a, i) => <Sfx key={`w${i}`} src={whoosh} at={a - 4} volumeDb={-4} />)}
      {!silent && <Sfx src={impact} at={at[at.length - 1]} volumeDb={-2} durationInFrames={fps * 3} />}
    </div>
  );
};
