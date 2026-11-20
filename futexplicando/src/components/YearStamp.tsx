import React from "react";
import { interpolate, useCurrentFrame, Easing } from "remotion";
import { TITLE, SANS } from "../lib/fonts";
import { shake } from "./motion";
import { Sfx } from "./Sfx";

/** Ano gigante entrando como carimbo (borda dupla, tinta irregular). */
export const YearStamp: React.FC<{
  year: string; sub?: string; at?: number; color: string; size?: number; rotate?: number; sound?: string;
}> = ({ year, sub, at = 0, color, size = 380, rotate = -8, sound }) => {
  const frame = useCurrentFrame();
  const t = frame - at;
  const scale = interpolate(t, [0, 5, 8], [2.6, 0.94, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad) });
  const o = interpolate(t, [0, 3], [0, 0.95], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s = shake(frame, at + 5, 14, 8);
  if (t < 0) return null;
  return (
    <div style={{ transform: `translate(${s.x}px,${s.y}px) rotate(${rotate}deg) scale(${scale})`, opacity: o, position: "relative" }}>
      <svg width="0" height="0" style={{ position: "absolute" }}>
        <filter id="ink">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={3} />
          <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.6" />
          <feComposite in="SourceGraphic" operator="in" />
        </filter>
      </svg>
      <div
        style={{
          filter: "url(#ink)", border: `14px solid ${color}`, outline: `5px solid ${color}`, outlineOffset: 12,
          padding: "0 46px 8px", borderRadius: 18, color, textAlign: "center",
        }}
      >
        <div style={{ fontFamily: TITLE, fontSize: size, lineHeight: 1.05, letterSpacing: 6 }}>{year}</div>
        {sub && <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: size * 0.16, letterSpacing: 8, marginTop: -size * 0.06, paddingBottom: 10 }}>{sub}</div>}
      </div>
      <Sfx src={sound} at={at + 3} volumeDb={0} durationInFrames={45} />
    </div>
  );
};
