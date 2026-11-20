import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { episode, palette } from "../lib/episode";
import { useWordFrame } from "../lib/scene";
import { SANS } from "../lib/fonts";
import { Background } from "../components/Background";
import { Hook } from "../components/Hook";
import { Sfx } from "../components/Sfx";

export const CtaScene: React.FC<{ scene: any }> = ({ scene }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = scene.props;
  const tQ = useWordFrame(p.sync?.question, 0, 0.1);
  const tBtn = useWordFrame(p.sync?.button, 0, 2.7);
  const btn = spring({ frame: f - tBtn, fps, config: { damping: 8, stiffness: 180 } });
  const bob = Math.sin((f - tBtn) / 5) * 10 * (f > tBtn + 10 ? 1 : 0);
  return (
    <AbsoluteFill>
      <Background color={palette.primary} dots="rgba(0,0,0,0.12)" />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 330 }}>
        <Hook lines={p.lines} at={p.lines.map((_: string, i: number) => tQ + i * 6)} highlight={p.highlight} color={palette.paper} highlightColor={palette.ink} highlightBg={palette.secondary} size={170} whoosh={episode.audio.whoosh} silent={false} impact={undefined} />
      </AbsoluteFill>
      {f >= tBtn && (
        <div style={{ position: "absolute", top: 1000, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 24, fontFamily: SANS, fontWeight: 900, fontSize: 80, color: palette.ink, background: palette.paper, padding: "24px 50px", borderRadius: 999, border: `8px solid ${palette.ink}`, boxShadow: `12px 12px 0 ${palette.ink}`, transform: `scale(${btn}) translateY(${bob}px)` }}>
            <svg width="90" height="90" viewBox="0 0 100 100"><path d="M10 15h80v55H45L22 90V70H10z" fill={palette.secondary} stroke={palette.ink} strokeWidth="7" strokeLinejoin="round" /><circle cx="32" cy="42" r="6" fill={palette.ink} /><circle cx="50" cy="42" r="6" fill={palette.ink} /><circle cx="68" cy="42" r="6" fill={palette.ink} /></svg>
            {p.button}
          </div>
        </div>
      )}
      <Sfx src={episode.audio.stamp} at={tBtn} volumeDb={-4} />
    </AbsoluteFill>
  );
};
