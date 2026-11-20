import React from "react";
import { AbsoluteFill } from "remotion";
import "./lib/fonts";
import { episode, palette } from "./lib/episode";
import { TITLE, SANS } from "./lib/fonts";
import { Background } from "./components/Background";
import { Crest } from "./components/Crest";
import { PaperGrain } from "./components/PaperGrain";
import { Badge } from "./components/Badge";

/** Capa (still): frame forte com o texto do JSON (cover.lines). */
export const Cover: React.FC = () => {
  const c = episode.cover;
  const hook = episode.scenes.find((s) => s.id === c.frameScene)!;
  return (
    <AbsoluteFill>
      <Background color={palette.primary} photo={hook.image?.src} photoOpacity={0.35} dots="rgba(0,0,0,0.12)" />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 330 }}>
        <Crest src={hook.props.crest as string} size={360} />
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 46, color: palette.paper, letterSpacing: 4, marginTop: 50 }}>{c.kicker}</div>
        <div style={{ fontFamily: TITLE, fontSize: 172, lineHeight: 1, color: palette.paper, textAlign: "center", whiteSpace: "nowrap", marginTop: 30, transform: "rotate(-3deg)", textShadow: `10px 10px 0 ${palette.ink}` }}>{c.lines[0]}</div>
        <div style={{ fontFamily: TITLE, fontSize: 200, lineHeight: 1.05, color: palette.paper, background: palette.ink, padding: "0 40px", whiteSpace: "nowrap", marginTop: 20, transform: "rotate(2deg)" }}>{c.lines[1]}</div>
      </AbsoluteFill>
      <Badge still handle={episode.handle} ink={palette.ink} paper={palette.paper} accent={palette.primary} />
      <PaperGrain />
    </AbsoluteFill>
  );
};
