import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";
import { TITLE } from "../lib/fonts";

/** Vinheta de 0,5s (15 frames): faixas cruzam a tela com a marca e abrem a cena. */
export const Intro: React.FC<{ handle: string; colors: string[]; ink: string; paper: string; reverse?: boolean; length?: number }> = ({ handle, colors, ink, paper, reverse, length = 16 }) => {
  const raw = useCurrentFrame();
  // reverse = mesma vinheta tocada de trás pra frente (fecha o vídeo e emenda no loop)
  const f = reverse ? length - 1 - raw : raw;
  if (f > 16 || f < 0) return null;
  const out = interpolate(f, [8, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
  const textIn = interpolate(f, [0, 5], [1.4, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.back(2)) });
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {colors.map((c, i) => (
        <div
          key={i}
          style={{
            position: "absolute", left: -200, width: 1480, height: 700, top: 260 + i * 470, background: c,
            transform: `rotate(-12deg) translateX(${out * (i % 2 ? -1 : 1) * 1600}px)`,
          }}
        />
      ))}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: 1 - out }}>
        <div
          style={{
            fontFamily: TITLE, fontSize: 130, color: paper, background: ink, padding: "10px 40px",
            transform: `rotate(-6deg) scale(${textIn})`, letterSpacing: 2,
          }}
        >
          {handle.toUpperCase()}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
