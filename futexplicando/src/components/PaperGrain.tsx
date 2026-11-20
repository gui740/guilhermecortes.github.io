import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";

/** Textura de papel + grão animado por cima de tudo. */
export const PaperGrain: React.FC<{ opacity?: number }> = ({ opacity = 0.22 }) => {
  const frame = useCurrentFrame();
  const seed = Math.floor(frame / 2) % 12;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="100%" height="100%" style={{ position: "absolute", mixBlendMode: "multiply", opacity }}>
        <filter id={`paper-${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={3} seed={seed} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
          <feComponentTransfer>
            <feFuncA type="table" tableValues="0 0.9" />
          </feComponentTransfer>
        </filter>
        <rect width="100%" height="100%" filter={`url(#paper-${seed})`} />
      </svg>
      <svg width="100%" height="100%" style={{ position: "absolute", mixBlendMode: "multiply", opacity: 0.18 }}>
        <filter id="fibers">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.04" numOctaves={4} seed={7} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#fibers)" />
      </svg>
      <AbsoluteFill
        style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.35) 100%)" }}
      />
    </AbsoluteFill>
  );
};
