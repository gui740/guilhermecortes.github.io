import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, FONT, MONO } from "./theme";
import { NLogo } from "./cenas/bits";

/** Capa 1280x720: arquivo de Hastings em P&B à esquerda, tese à direita, N limpo com respiro. */
export const Capa: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.branco }}>
    <div style={{ position: "absolute", left: 0, top: 0, width: 620, height: 720, overflow: "hidden", background: "black" }}>
      <Img src={staticFile("media/stills/capa_hastings.jpg")} style={{ height: 720, marginLeft: -330 }} />
      <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.22) 0px, rgba(0,0,0,0.22) 1px, transparent 1px, transparent 3px)" }} />
      <div style={{ position: "absolute", left: 24, bottom: 26, background: "rgba(20,20,20,0.9)", borderLeft: `4px solid ${C.ambar}`, padding: "8px 12px",
        fontFamily: MONO, fontSize: 17, color: C.ambar, letterSpacing: 1.5 }}>REED HASTINGS · CEO DA NETFLIX</div>
    </div>
    <div style={{ position: "absolute", left: 670, top: 70, width: 560 }}>
      <NLogo altura={120} />
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 82, lineHeight: 0.98, color: C.tinta, marginTop: 50, letterSpacing: -1 }}>
        ELA COMPETE COM O SEU SONO.
      </div>
      <div style={{ fontFamily: MONO, fontSize: 20, color: C.secundario, letterSpacing: 2, marginTop: 30 }}>BRAND BY IZOTON · EP01</div>
    </div>
  </AbsoluteFill>
);
