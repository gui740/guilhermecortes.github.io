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

/** Capa v3 (1280x720), na linguagem do episódio: papel, recorte de Hastings em P&B com borda e sombra, envelope da marca em cor,
 *  carimbo do arquivo e o N limpo (sem grão por cima). Foto: Reed Hastings, re:publica 2015 (cellanr, CC BY-SA 2.0); envelope: BlueMint (CC BY 2.5). */
export const CapaV3: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.branco }}>
    <Img src={staticFile("media/v3tex/papel.jpg")} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.9 }} />
    {/* recorte de Hastings, P&B, contorno branco e sombra real, levemente inclinado */}
    <Img src={staticFile("media/v3img/rec_hastings_2015.png")} style={{ position: "absolute", left: 30, top: 70, height: 700, transform: "rotate(-3deg)",
      filter: "grayscale(1) contrast(1.1) drop-shadow(0 0 0 white) drop-shadow(5px 0 0 white) drop-shadow(-5px 0 0 white) drop-shadow(0 5px 0 white) drop-shadow(0 -5px 0 white) drop-shadow(14px 18px 16px rgba(0,0,0,0.35))" }} />
    <div style={{ position: "absolute", left: 40, top: 40, fontFamily: MONO, fontSize: 18, letterSpacing: 3, color: C.tinta, border: `3px solid ${C.tinta}`, padding: "6px 12px",
      background: "rgba(255,255,255,0.9)", transform: "rotate(-4deg)" }}>REED HASTINGS · CEO DA NETFLIX</div>
    {/* grão só no fundo e no recorte */}
    <AbsoluteFill style={{ backgroundImage: `url(${staticFile("media/v3tex/grao_1.png")})`, opacity: 0.35, mixBlendMode: "multiply" }} />
    <div style={{ position: "absolute", left: 600, top: 64, width: 640 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
        <NLogo altura={110} />
        <div style={{ fontFamily: MONO, fontSize: 18, letterSpacing: 3, color: C.secundario, lineHeight: 1.5 }}>ARQUIVO 01<br />BRAND BY IZOTON · EP01</div>
      </div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 88, lineHeight: 0.98, color: C.tinta, marginTop: 42, letterSpacing: -1 }}>
        ELA COMPETE COM O SEU{" "}
        <span style={{ background: C.tinta, color: C.branco, padding: "0 14px", display: "inline-block", transform: "rotate(-1.5deg)", marginTop: 8 }}>SONO.</span>
      </div>
      <div style={{ fontFamily: MONO, fontSize: 18, letterSpacing: 2.5, color: C.secundario, marginTop: 30 }}>ENTREVISTA DE RESULTADOS · 17 ABR. 2017</div>
    </div>
    <Img src={staticFile("media/v3img/rec_envelope.png")} style={{ position: "absolute", right: 40, bottom: 22, width: 230, transform: "rotate(5deg)",
      filter: "drop-shadow(4px 0 0 white) drop-shadow(-4px 0 0 white) drop-shadow(0 4px 0 white) drop-shadow(0 -4px 0 white) drop-shadow(10px 14px 12px rgba(0,0,0,0.3))" }} />
  </AbsoluteFill>
);
