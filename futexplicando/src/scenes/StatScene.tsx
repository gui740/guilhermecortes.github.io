import React from "react";
import { AbsoluteFill } from "remotion";
import { episode, palette } from "../lib/episode";
import { useWordFrame } from "../lib/scene";
import { Background } from "../components/Background";
import { StatSlam } from "../components/StatSlam";

export const StatScene: React.FC<{ scene: any }> = ({ scene }) => {
  const p = scene.props;
  const tStart = useWordFrame(p.countFromWord, 0, 1);
  const tLand = useWordFrame(p.landWord, 0, 2.4);
  return (
    <AbsoluteFill>
      <Background color={palette.primary} photo={scene.image?.src} photoOpacity={0.35} dots="rgba(0,0,0,0.12)" />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 300 }}>
        <StatSlam value={p.value} label={p.label} kicker={p.kicker} at={tStart} countFrames={Math.max(12, tLand - tStart)} colors={palette} impact={episode.audio.impact} whoosh={episode.audio.whoosh} />
      </AbsoluteFill>
      {scene.image?.credit && <div style={{ position: "absolute", bottom: 420, right: 40, fontSize: 18, color: palette.paper, opacity: 0.6, fontFamily: "Inter" }}>{scene.image.credit}</div>}
    </AbsoluteFill>
  );
};
