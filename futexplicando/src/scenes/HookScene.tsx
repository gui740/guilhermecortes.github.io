import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { episode, palette } from "../lib/episode";
import { useWordFrame } from "../lib/scene";
import { Background } from "../components/Background";
import { Hook } from "../components/Hook";
import { Crest } from "../components/Crest";
import { shake } from "../components/motion";

export const HookScene: React.FC<{ scene: any }> = ({ scene }) => {
  const f = useCurrentFrame();
  const p = scene.props;
  const at = [useWordFrame(p.sync?.[0], 0, 0.5), useWordFrame(p.sync?.[1], 0, 1.4), useWordFrame(p.sync?.[2], 0, 2.6)];
  const s = shake(f, at[2], 30, 14);
  return (
    <AbsoluteFill>
      <Background color={palette.primary} photo={scene.image?.src} photoOpacity={0.3} dots="rgba(0,0,0,0.12)" />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 290 }}>
        <div style={{ transform: `translate(${s.x}px,${s.y}px) rotate(${s.r * 3}deg)` }}>
          <Crest src={p.crest} size={250} />
        </div>
        <div style={{ marginTop: 40 }}>
          <Hook lines={p.lines} at={at} highlight={p.highlight} color={palette.paper} highlightColor={palette.paper} highlightBg={palette.ink} whoosh={episode.audio.whoosh} impact={episode.audio.impact} size={205} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
