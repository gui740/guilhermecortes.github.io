import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";

/** Fundo chapado com padrão de meio-tom e (opcional) foto histórica em multiply. */
export const Background: React.FC<{ color: string; dots?: string; photo?: string; photoOpacity?: number }> = ({ color, dots = "rgba(0,0,0,0.08)", photo, photoOpacity = 0.25 }) => {
  const f = useCurrentFrame();
  const zoom = interpolate(f, [0, 300], [1.1, 1.25], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: color }}>
      {photo && (
        <Img src={staticFile(photo)} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(1) contrast(1.3)", mixBlendMode: "multiply", opacity: photoOpacity, transform: `scale(${zoom})` }} />
      )}
      <AbsoluteFill style={{ backgroundImage: `radial-gradient(${dots} 3px, transparent 3.5px)`, backgroundSize: "26px 26px" }} />
    </AbsoluteFill>
  );
};
