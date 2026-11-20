import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { TITLE, SANS } from "../lib/fonts";
import { shake } from "./motion";
import { Sfx } from "./Sfx";

/** Número gigante com contador subindo de 0 até o valor + impacto. */
export const StatSlam: React.FC<{
  value: number; label: string; kicker?: string; at: number; countFrames?: number;
  colors: { paper: string; ink: string; primary: string; secondary: string }; impact?: string; whoosh?: string;
}> = ({ value, label, kicker, at, countFrames = 24, colors, impact, whoosh }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = Math.round(interpolate(f, [at, at + countFrames], [0, value], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }));
  const land = at + countFrames;
  const slam = interpolate(f, [land - 2, land + 2, land + 6], [1, 1.25, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s = shake(f, land, 26, 12);
  const kin = spring({ frame: f, fps, config: { damping: 12 } });
  const lin = spring({ frame: f - land, fps, config: { damping: 10, stiffness: 160 } });
  const ring = interpolate(f, [land, land + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", transform: `translate(${s.x}px,${s.y}px)` }}>
      {kicker && (
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 52, color: colors.ink, background: colors.paper, padding: "8px 24px", transform: `translateY(${(1 - kin) * -200}px) rotate(-2deg)`, opacity: kin }}>{kicker}</div>
      )}
      <div style={{ position: "relative" }}>
        <div style={{ position: "absolute", left: "50%", top: "50%", width: 900, height: 900, marginLeft: -450, marginTop: -450, borderRadius: 999, border: `16px solid ${colors.secondary}`, transform: `scale(${0.4 + ring * 0.9})`, opacity: 1 - ring }} />
        <div style={{ fontFamily: TITLE, fontSize: 720, lineHeight: 1, color: colors.paper, transform: `scale(${slam})`, textShadow: `22px 22px 0 ${colors.ink}`, fontVariantNumeric: "tabular-nums" }}>{n}</div>
      </div>
      <div style={{ fontFamily: TITLE, fontSize: 150, color: colors.ink, background: colors.secondary, padding: "0 34px", transform: `scale(${lin}) rotate(2deg)`, marginTop: -40 }}>{label}</div>
      <Sfx src={whoosh} at={at - 4} volumeDb={-4} />
      <Sfx src={impact} at={land - 1} volumeDb={0} durationInFrames={fps * 3} />
    </div>
  );
};
