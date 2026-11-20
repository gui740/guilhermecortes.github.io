import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { SANS } from "../lib/fonts";

/** Foto em "polaroid" de papel com fita adesiva, entrada com spring e zoom lento (Ken Burns). */
export const PhotoCard: React.FC<{
  src: string; at?: number; width: number; height: number; rotate?: number; caption?: string; credit?: string;
  paper: string; ink: string; tint?: string; grayscale?: boolean; objectPosition?: string; from?: "left" | "right" | "bottom" | "top";
}> = ({ src, at = 0, width, height, rotate = -3, caption, credit, paper, ink, tint, grayscale, objectPosition = "center", from = "bottom" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: { damping: 14, stiffness: 120 } });
  const dist = 1400;
  const dx = from === "left" ? -dist : from === "right" ? dist : 0;
  const dy = from === "bottom" ? dist : from === "top" ? -dist : 0;
  const zoom = interpolate(frame - at, [0, 240], [1.08, 1.22], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  if (frame < at - 1) return null;
  return (
    <div
      style={{
        width: width + 36, background: paper, padding: "18px 18px 0", boxShadow: "0 24px 40px rgba(0,0,0,0.35)",
        transform: `translate(${(1 - p) * dx}px, ${(1 - p) * dy}px) rotate(${rotate + (1 - p) * 12}deg)`, position: "relative",
      }}
    >
      <div style={{ position: "absolute", top: -26, left: "50%", width: 190, height: 56, marginLeft: -95, background: "rgba(244,239,230,0.75)", transform: "rotate(-4deg)", boxShadow: "0 2px 4px rgba(0,0,0,0.15)" }} />
      <div style={{ width, height, overflow: "hidden", position: "relative", background: ink }}>
        <Img
          src={staticFile(src)}
          style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition, transform: `scale(${zoom})`, filter: grayscale ? "grayscale(1) contrast(1.15) sepia(0.25)" : "contrast(1.05) saturate(1.05)" }}
        />
        {tint && <div style={{ position: "absolute", inset: 0, background: tint, mixBlendMode: "multiply", opacity: 0.35 }} />}
      </div>
      <div style={{ minHeight: caption ? 92 : 30, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", paddingBottom: 6 }}>
        {caption && <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 38, color: ink, letterSpacing: 1 }}>{caption}</div>}
        {credit && <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 16, color: ink, opacity: 0.6 }}>{credit}</div>}
      </div>
    </div>
  );
};
