import React from "react";
import { Img, staticFile } from "remotion";

export const Crest: React.FC<{ src: string; size: number; style?: React.CSSProperties }> = ({ src, size, style }) => (
  <Img src={staticFile(src)} style={{ width: size, height: size, objectFit: "contain", filter: "drop-shadow(0 10px 0 rgba(0,0,0,0.35))", ...style }} />
);
