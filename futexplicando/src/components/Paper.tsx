import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C } from "../theme";

/** Fundo de papel: cor base + fibras (feTurbulence) + vinheta nas bordas. */
export const PaperBackground: React.FC<{ color?: string; tint?: string }> = ({ color = C.paper, tint = "rgba(120,90,40,0.10)" }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: color }}>
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
        <filter id="paperFibers">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.04" numOctaves={4} seed={7} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.36  0 0 0 0 0.22  0 0 0 0.1 0" />
        </filter>
        <filter id="paperSpeck">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={1} seed={3} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.2  0 0 0 0 0.15  0 0 0 0 0.1  0 0 0 -2.6 1.55" />
        </filter>
        <rect width="100%" height="100%" filter="url(#paperFibers)" />
        <rect width="100%" height="100%" filter="url(#paperSpeck)" opacity={0.18} />
      </svg>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, ${tint} 100%)`,
        }}
      />
    </AbsoluteFill>
  );
};

/** Granulado animado leve por cima de tudo (troca a semente a cada 2 frames). */
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.13 }) => {
  const frame = useCurrentFrame();
  const seed = Math.floor(frame / 2) % 50;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "multiply", opacity }}>
      <svg width="100%" height="100%">
        <filter id={`grain${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves={2} seed={seed} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#grain${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

/** Rasgo de papel (borda irregular) usado como faixa/etiqueta. */
export const TornStrip: React.FC<{ color?: string; children: React.ReactNode; style?: React.CSSProperties; seed?: number }> = ({
  color = C.black,
  children,
  style,
  seed = 1,
}) => {
  const pts: string[] = [];
  const n = 22;
  for (let i = 0; i <= n; i++) {
    const x = (i / n) * 100;
    const j = (Math.sin(i * 7.3 + seed) * 0.5 + 0.5) * 7;
    pts.push(`${x}% ${j}%`);
  }
  for (let i = n; i >= 0; i--) {
    const x = (i / n) * 100;
    const j = 100 - (Math.sin(i * 5.1 + seed * 3) * 0.5 + 0.5) * 7;
    pts.push(`${x}% ${j}%`);
  }
  return (
    <div style={{ backgroundColor: color, clipPath: `polygon(${pts.join(",")})`, padding: "18px 34px", ...style }}>{children}</div>
  );
};
