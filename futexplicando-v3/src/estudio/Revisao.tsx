import React from "react";
import { AbsoluteFill } from "remotion";
import { COR, FONTE } from "../estilo/tokens";
import { Chibi, ELENCO, Expressao } from "../personagens/Chibi";
import { EstadioNoite } from "../cenarios/EstadioNoite";

/** Telas de revisão: ficha de expressões do LUSA, elenco completo e cena-teste. */

const Rotulo: React.FC<{ t: string }> = ({ t }) => (
  <div style={{ fontFamily: FONTE.titulo, fontSize: 30, color: "#fff", textAlign: "center", letterSpacing: 1, textShadow: "0 2px 0 #000" }}>{t}</div>
);

const EXPRS: Expressao[] = ["neutro", "boca_aberta", "olhos_fechados", "bravo", "triste", "chocado", "convencido", "comemorando", "apontando", "bracos_cruzados"];

export const FichaLusa: React.FC = () => (
  <AbsoluteFill style={{ background: "#1B2547" }}>
    <div style={{ fontFamily: FONTE.titulo, fontSize: 72, color: COR.amarelo, textAlign: "center", marginTop: 40, WebkitTextStroke: "3px #000" }}>LUSA · FICHA DE EXPRESSÕES</div>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", rowGap: 18, padding: "30px 30px", justifyItems: "center" }}>
      {EXPRS.map((e) => (
        <div key={e} style={{ display: "flex", flexDirection: "column", alignItems: "center", background: "rgba(0,255,0,0.0)" }}>
          <div style={{ background: "#00FF00", borderRadius: 18, padding: "10px 30px 0" }}>
            <Chibi {...ELENCO.LUSA} expressao={e} altura={380} />
          </div>
          <Rotulo t={e.toUpperCase()} />
        </div>
      ))}
    </div>
  </AbsoluteFill>
);

export const Elenco: React.FC = () => (
  <AbsoluteFill style={{ background: "#1B2547" }}>
    <div style={{ fontFamily: FONTE.titulo, fontSize: 72, color: COR.amarelo, textAlign: "center", marginTop: 40, WebkitTextStroke: "3px #000" }}>ELENCO · CAIU POR 15 MINUTOS</div>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", rowGap: 40, padding: "60px 20px", justifyItems: "center" }}>
      {(
        [
          ["LUSA", "convencido"],
          ["FLU", "convencido"],
          ["FLA", "comemorando"],
          ["GREMIO", "neutro"],
          ["JUIZ", "bravo"],
          ["ADVOGADO", "triste"],
        ] as [string, Expressao][]
      ).map(([k, e]) => (
        <div key={k} style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <Chibi {...ELENCO[k]} expressao={e} altura={640} pose={k === "JUIZ" ? "martelo" : undefined} />
          <Rotulo t={k} />
        </div>
      ))}
    </div>
  </AbsoluteFill>
);

/** Cena 1 (plano A) estática: LUSA chocado x FLU convencido, relógio 32' e título. */
export const CenaTeste: React.FC = () => (
  <AbsoluteFill>
    <EstadioNoite />
    {/* relógio gigante */}
    <div style={{ position: "absolute", left: 540 - 190, top: 660, width: 380, height: 380 }}>
      <svg width={380} height={380} viewBox="0 0 380 380">
        <defs>
          <radialGradient id="mostr" cx="45%" cy="40%" r="65%">
            <stop offset="0" stopColor="#FFFFFF" />
            <stop offset="1" stopColor="#DCE4F4" />
          </radialGradient>
        </defs>
        <circle cx={190} cy={190} r={176} fill="#E1251B" stroke={COR.contorno} strokeWidth={10} />
        <circle cx={190} cy={190} r={146} fill="url(#mostr)" stroke={COR.contorno} strokeWidth={7} />
        {Array.from({ length: 12 }).map((_, i) => {
          const a = (i / 12) * Math.PI * 2;
          return <line key={i} x1={190 + Math.sin(a) * 120} y1={190 - Math.cos(a) * 120} x2={190 + Math.sin(a) * 136} y2={190 - Math.cos(a) * 136} stroke={COR.contorno} strokeWidth={i % 3 ? 5 : 10} strokeLinecap="round" />;
        })}
        {/* 32 minutos */}
        <line x1={190} y1={190} x2={190 + Math.sin((32 / 60) * Math.PI * 2) * 100} y2={190 - Math.cos((32 / 60) * Math.PI * 2) * 100} stroke={COR.contorno} strokeWidth={12} strokeLinecap="round" />
        <circle cx={190} cy={190} r={14} fill={COR.contorno} />
        <text x={190} y={150} textAnchor="middle" fontFamily={FONTE.titulo} fontSize={64} fill="#E1251B">32'</text>
      </svg>
    </div>
    <div style={{ position: "absolute", left: -40, top: 860, filter: "drop-shadow(0 30px 24px rgba(0,0,0,0.45))" }}>
      <Chibi {...ELENCO.LUSA} expressao="chocado" altura={980} />
    </div>
    <div style={{ position: "absolute", left: 560, top: 880, filter: "drop-shadow(0 30px 24px rgba(0,0,0,0.45))" }}>
      <Chibi {...ELENCO.FLU} expressao="convencido" altura={960} espelhar />
    </div>
    {/* título */}
    <div style={{ position: "absolute", top: 250, width: 1080, textAlign: "center", fontFamily: FONTE.titulo, lineHeight: 1.02, transform: "skewX(-8deg)" }}>
      <div style={{ fontSize: 190, color: "#fff", WebkitTextStroke: "16px #000", paintOrder: "stroke fill", textShadow: "0 14px 0 rgba(0,0,0,0.55)" }}>CAIU POR</div>
      <div style={{ fontSize: 172, color: COR.amarelo, WebkitTextStroke: "16px #000", paintOrder: "stroke fill", textShadow: "0 14px 0 rgba(0,0,0,0.55)" }}>15 MINUTOS?!</div>
    </div>
  </AbsoluteFill>
);
