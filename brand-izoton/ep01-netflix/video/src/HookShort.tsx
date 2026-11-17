import React from "react";
import { AbsoluteFill } from "remotion";
import { C, FONT, MONO } from "./theme";

/** Título-gancho dos Shorts (PNG transparente 1080x1920, sobreposto nos 2,5 s iniciais). */
export const HookShort: React.FC<{ texto: string; num: string }> = ({ texto, num }) => (
  <AbsoluteFill style={{ backgroundColor: "transparent" }}>
    <div style={{ position: "absolute", top: 150, left: 60, right: 60, background: "rgba(255,255,255,0.96)", padding: "34px 40px 38px",
      boxShadow: "18px 18px 30px rgba(0,0,0,0.22)" }}>
      <div style={{ fontFamily: MONO, fontSize: 26, letterSpacing: 3, color: C.secundario }}>BRAND BY IZOTON · NETFLIX · {num}</div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: texto.length > 34 ? 70 : 86, lineHeight: 1.0, color: C.tinta, marginTop: 18,
        textTransform: "uppercase", letterSpacing: -0.5 }}>{texto}</div>
    </div>
  </AbsoluteFill>
);
