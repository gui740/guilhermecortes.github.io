import React from "react";
import { Img, staticFile } from "remotion";
import { ANTON, BEBAS, C } from "../theme";

/**
 * Moeda do Clube da Fé (2D com falsa espessura).
 * angle: rotação no eixo vertical (rad). 0 = escudo de frente. PI = verso.
 * tilt: rotação no plano (graus).
 */
export const Coin: React.FC<{
  size: number;
  angle: number;
  tilt?: number;
  crest: string;
  id: string;
  blur?: number;
  style?: React.CSSProperties;
}> = ({ size: D, angle, tilt = 0, crest, id, blur = 0, style }) => {
  const c = Math.cos(angle);
  const s = Math.sin(angle);
  const T = D * 0.075; // espessura
  const sx = Math.max(Math.abs(c), 0.012);
  const dx = -T * s; // deslocamento da borda
  const front = c >= 0;
  // posição do reflexo (varre a face conforme gira)
  const shine = 50 + s * 60;

  const metal = front
    ? "radial-gradient(circle at 38% 30%, #ffffff 0%, #e9e6df 18%, #b9b4aa 48%, #8e897f 70%, #d8d3c9 88%, #77736b 100%)"
    : "radial-gradient(circle at 62% 30%, #ffffff 0%, #e6e2da 18%, #b5b0a5 48%, #8b867c 70%, #d3cec4 88%, #74706a 100%)";

  return (
    <div style={{ position: "relative", width: D, height: D, rotate: `${tilt}deg`, filter: blur ? `blur(${blur}px)` : undefined, ...style }}>
      {/* borda (serrilha) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: D / 2 - D / 2,
          width: D,
          height: D,
          borderRadius: "50%",
          translate: `${dx}px 0px`,
          scale: `${sx} 1`,
          background: "linear-gradient(90deg,#5d5952,#a7a298 40%,#4c4842)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 0,
          height: D,
          left: D / 2 + Math.min(0, dx),
          width: Math.abs(dx),
          background:
            "repeating-linear-gradient(0deg, #6d685f 0px, #6d685f 3px, #b8b2a6 3px, #b8b2a6 6px), linear-gradient(90deg,#55514a,#c9c3b7,#55514a)",
          backgroundBlendMode: "multiply",
          clipPath: `inset(0 round ${Math.abs(dx) / 2}px)`,
          borderRadius: `${Math.abs(dx) / 2}px / ${D / 2}px`,
        }}
      />
      {/* face */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "50%",
          scale: `${sx} 1`,
          background: metal,
          boxShadow: "inset 0 0 0 3px rgba(255,255,255,0.55), inset 0 0 18px rgba(0,0,0,0.45)",
          overflow: "hidden",
        }}
      >
        {/* aro com relevo */}
        <div
          style={{
            position: "absolute",
            inset: D * 0.06,
            borderRadius: "50%",
            background: front
              ? "radial-gradient(circle at 45% 35%, #f2efe8 0%, #c9c4b9 55%, #9d988e 100%)"
              : "radial-gradient(circle at 55% 35%, #f0ece4 0%, #c6c0b4 55%, #99948a 100%)",
            boxShadow: "inset 0 4px 10px rgba(0,0,0,0.35), 0 -2px 4px rgba(255,255,255,0.6)",
          }}
        />
        <svg viewBox="0 0 200 200" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
          <defs>
            <path id={`rim-${id}`} d="M 100,100 m -80,0 a 80,80 0 1,1 160,0 a 80,80 0 1,1 -160,0" />
          </defs>
          <text fontFamily={BEBAS} fontSize={15} letterSpacing={3.2} fill="#5f5a52" opacity={0.9}>
            <textPath href={`#rim-${id}`} startOffset="0">
              {front ? "SÃO PAULO FUTEBOL CLUBE  ★  1930  ★  " : "CLUBE DA FÉ  ★  CLUBE DA FÉ  ★  1935  ★  "}
            </textPath>
          </text>
          {Array.from({ length: 72 }).map((_, i) => {
            const a = (i / 72) * Math.PI * 2;
            return (
              <line
                key={i}
                x1={100 + Math.cos(a) * 93}
                y1={100 + Math.sin(a) * 93}
                x2={100 + Math.cos(a) * 97}
                y2={100 + Math.sin(a) * 97}
                stroke="#7d786f"
                strokeWidth={1.1}
              />
            );
          })}
        </svg>
        {front ? (
          <Img
            src={staticFile(crest)}
            style={{
              position: "absolute",
              left: D * 0.22,
              top: D * 0.22,
              width: D * 0.56,
              height: D * 0.56,
              objectFit: "contain",
              filter: "drop-shadow(0 3px 2px rgba(0,0,0,0.45)) saturate(1.05)",
            }}
          />
        ) : (
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: "#6a655c",
              textShadow: "0 2px 0 rgba(255,255,255,0.7), 0 -1px 0 rgba(0,0,0,0.35)",
            }}
          >
            <div style={{ fontFamily: BEBAS, fontSize: D * 0.1, letterSpacing: D * 0.01 }}>CLUBE DA</div>
            <div style={{ fontFamily: ANTON, fontSize: D * 0.3, lineHeight: 1, color: C.red, opacity: 0.85 }}>FÉ</div>
            <div style={{ fontFamily: BEBAS, fontSize: D * 0.08, letterSpacing: D * 0.012 }}>★ ★ ★</div>
          </div>
        )}
        {/* reflexo especular */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius: "50%",
            background: `linear-gradient(115deg, rgba(255,255,255,0) ${shine - 22}%, rgba(255,255,255,0.75) ${shine}%, rgba(255,255,255,0) ${shine + 18}%)`,
            mixBlendMode: "screen",
          }}
        />
      </div>
    </div>
  );
};
