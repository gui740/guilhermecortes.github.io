import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { TITLE } from "../lib/fonts";
import { Sfx } from "../components/Sfx";
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
  const { fps } = useVideoConfig();
  const tSub = useWordFrame(p.subtitle?.word, 0, 4.5);
  const sub = p.subtitle ? spring({ frame: f - tSub, fps, config: { damping: 11, stiffness: 160 } }) : 0;
  const lift = interpolate(sub, [0, 1], [0, 1]);
  return (
    <AbsoluteFill>
      <Background color={palette.primary} photo={scene.image?.src} photoOpacity={0.3} dots="rgba(0,0,0,0.12)" />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 290, transform: `translateY(${lift * -70}px) scale(${1 - lift * 0.12})`, transformOrigin: "50% 0" }}>
        <div style={{ transform: `translate(${s.x}px,${s.y}px) rotate(${s.r * 3}deg)` }}>
          <Crest src={p.crest} size={250} />
        </div>
        <div style={{ marginTop: 40 }}>
          <Hook lines={p.lines} at={at} highlight={p.highlight} color={palette.paper} highlightColor={palette.paper} highlightBg={palette.ink} whoosh={episode.audio.whoosh} impact={episode.audio.impact} size={205} />
        </div>
      </AbsoluteFill>
      {p.subtitle && f >= tSub && (
        <div style={{ position: "absolute", top: 1150, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
          <div style={{ fontFamily: TITLE, fontSize: 92, color: palette.ink, background: palette.secondary, padding: "4px 34px", border: `7px solid ${palette.ink}`, transform: `rotate(-3deg) scale(${sub})`, boxShadow: `10px 10px 0 ${palette.ink}`, whiteSpace: "nowrap" }}>
            {p.subtitle.text}
          </div>
        </div>
      )}
      {p.subtitle && <Sfx src={episode.audio.whoosh} at={tSub - 3} volumeDb={-4} />}
    </AbsoluteFill>
  );
};
