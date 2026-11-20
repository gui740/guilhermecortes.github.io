import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { episode, palette } from "../lib/episode";
import { useWordFrame } from "../lib/scene";
import { TITLE } from "../lib/fonts";
import { Background } from "../components/Background";
import { Timeline } from "../components/Timeline";
import { Sfx } from "../components/Sfx";

export const TimelineScene: React.FC<{ scene: any }> = ({ scene }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = scene.props;
  const items = p.items.map((it: any, i: number) => ({ ...it, at: useWordFrame(it.word, 0, 1 + i * 2.5) })); // eslint-disable-line
  const tStamp = useWordFrame(p.stampWord, 0, 9.5);
  const head = spring({ frame: f, fps, config: { damping: 12 } });
  const st = spring({ frame: f - tStamp, fps, config: { damping: 9, stiffness: 200 } });
  return (
    <AbsoluteFill>
      <Background color={palette.paper} />
      <div style={{ position: "absolute", top: 225, left: 0, right: 0, textAlign: "center", fontFamily: TITLE, fontSize: 80, color: palette.primary, transform: `translateY(${(1 - head) * -300}px)` }}>{p.title}</div>
      <Timeline items={items} colors={palette} whoosh={episode.audio.whoosh} />
      {f >= tStamp && (
        <div style={{ position: "absolute", top: 640, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
          <div style={{ fontFamily: TITLE, fontSize: 80, lineHeight: 1.05, textAlign: "center", whiteSpace: "pre-line", color: palette.paper, background: palette.primary, border: `8px solid ${palette.ink}`, padding: "10px 30px", transform: `rotate(-5deg) scale(${2 - st})`, opacity: Math.min(1, st * 1.5), boxShadow: `12px 12px 0 ${palette.ink}` }}>
            {p.stampText}
          </div>
        </div>
      )}
      <Sfx src={episode.audio.stamp} at={tStamp} volumeDb={-2} />
    </AbsoluteFill>
  );
};
