import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { SANS } from "../lib/fonts";

/** Selo fixo @futexplicando no canto superior. */
export const Badge: React.FC<{ handle: string; ink: string; paper: string; accent: string; still?: boolean }> = ({ handle, ink, paper, accent, still }) => {
  const frame = useCurrentFrame();
  const o = still ? 1 : interpolate(frame, [12, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute", top: 150, left: 60, opacity: o, display: "flex", alignItems: "center", gap: 14,
        background: ink, color: paper, padding: "12px 24px 12px 14px", borderRadius: 999,
        fontFamily: SANS, fontWeight: 800, fontSize: 34, letterSpacing: 0.5, transform: "rotate(-2deg)",
        boxShadow: "0 6px 0 rgba(0,0,0,0.25)",
      }}
    >
      <svg width="40" height="40" viewBox="0 0 40 40">
        <circle cx="20" cy="20" r="18" fill={paper} />
        <path d="M20 6 l6 5 -2 8 h-8 l-2 -8z M8 18 l6 1 2 7 -4 6 -5 -4z M32 18 l-6 1 -2 7 4 6 5 -4z" fill={accent} />
      </svg>
      {handle}
    </div>
  );
};
