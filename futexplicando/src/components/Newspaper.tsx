import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { TITLE, SANS } from "../lib/fonts";

/** Recorte de jornal genérico (manchete). */
export const Newspaper: React.FC<{ at: number; date: string; headline: string; paper: string; ink: string; rotate?: number; outAt?: number }> = ({ at, date, headline, paper, ink, rotate = -3, outAt }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - at, fps, config: { damping: 13, stiffness: 150 } });
  const o = outAt ? spring({ frame: f - outAt, fps, config: { damping: 16 } }) : 0;
  if (f < at) return null;
  return (
    <div style={{ width: 900, background: paper, color: ink, padding: "26px 40px 40px", boxShadow: "0 30px 50px rgba(0,0,0,0.5)", transform: `translateY(${(1 - p) * -1300 - o * 1600}px) rotate(${rotate + (1 - p) * -10}deg) scale(${1 + (1 - p) * 0.4})`, clipPath: "polygon(0 2%, 4% 0, 30% 1.5%, 55% 0, 80% 1.2%, 100% 0, 99% 50%, 100% 98%, 70% 100%, 40% 98.5%, 10% 100%, 0 97%, 1% 50%)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: SANS, fontWeight: 800, fontSize: 26, borderBottom: `4px solid ${ink}`, paddingBottom: 8, letterSpacing: 3 }}>
        <span>EDIÇÃO EXTRA</span>
        <span>{date}</span>
      </div>
      <div style={{ fontFamily: TITLE, fontSize: 118, lineHeight: 1.0, marginTop: 18, textTransform: "uppercase" }}>{headline}</div>
      <div style={{ marginTop: 20, display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} style={{ height: 12, background: ink, opacity: 0.25, width: `${70 + ((i * 37) % 30)}%` }} />
        ))}
      </div>
    </div>
  );
};
