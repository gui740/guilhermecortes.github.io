import React from "react";
import { AbsoluteFill } from "remotion";
import { COR, FONTE } from "../estilo/tokens";
import { Chibi, ELENCO, Expressao, Pose } from "../personagens/Chibi";
import { Ata, Convite, Look1951, MicrofoneAntigo, Pasta, TacaAntigaG } from "../personagens/Props";

const Rot: React.FC<{ t: string }> = ({ t }) => <div style={{ fontFamily: FONTE.titulo, fontSize: 30, color: "#fff", textAlign: "center", textShadow: "0 2px 0 #000" }}>{t}</div>;
const Titulo: React.FC<{ t: string }> = ({ t }) => <div style={{ fontFamily: FONTE.titulo, fontSize: 66, color: COR.amarelo, textAlign: "center", marginTop: 34, WebkitTextStroke: "3px #000" }}>{t}</div>;

const EXP: [Expressao, Pose | undefined, string][] = [
  ["neutro", undefined, "NEUTRO"],
  ["boca_aberta", undefined, "BOCA_ABERTA"],
  ["olhos_fechados", undefined, "OLHOS_FECHADOS"],
  ["comemorando", "taca_alto", "COMEMORANDO (TAÇA)"],
  ["chocado", undefined, "CHOCADO"],
  ["convencido", "segurando", "FALANDO (ATA)"],
  ["triste", undefined, "ESPERANDO"],
  ["bravo", "apontando", "APONTANDO"],
  ["convencido", undefined, "CONVENCIDO"],
];

export const FichaPal: React.FC = () => (
  <AbsoluteFill style={{ background: "#14361F" }}>
    <Titulo t="PAL (ATUAL) · FICHA DE EXPRESSÕES" />
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", rowGap: 16, padding: "24px 30px", justifyItems: "center" }}>
      {EXP.map(([e, p, r], i) => (
        <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div style={{ background: "#00FF00", borderRadius: 18, padding: "8px 26px 0", overflow: "visible" }}>
            <Chibi {...ELENCO.PAL} expressao={e} pose={p} altura={480} objeto={p === "taca_alto" ? <TacaAntigaG x={436} y={126} s={0.5} /> : p === "segurando" ? <Ata /> : undefined} />
          </div>
          <Rot t={r} />
        </div>
      ))}
    </div>
  </AbsoluteFill>
);

const Cel: React.FC<{ k: string; e: Expressao; pose?: Pose; obj?: React.ReactNode; rot: string; antigo?: boolean; acessorio?: boolean }> = ({ k, e, pose, obj, rot, antigo }) => {
  const ch = <Chibi {...ELENCO[k]} expressao={e} pose={pose} altura={600} objeto={obj} />;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ position: "relative", width: 340, height: 640, borderRadius: 16, overflow: "hidden", background: antigo ? "#8C8460" : "#1B2547" }}>
        {antigo ? (
          <Look1951 frame={3}>
            <AbsoluteFill style={{ background: "linear-gradient(180deg,#A89E78,#6E6A4A)" }} />
            <div style={{ position: "absolute", left: 3, top: 30 }}>{ch}</div>
          </Look1951>
        ) : (
          <div style={{ position: "absolute", left: 3, top: 30 }}>{ch}</div>
        )}
      </div>
      <Rot t={rot} />
    </div>
  );
};

export const ElencoPalmeiras: React.FC = () => (
  <AbsoluteFill style={{ background: "#14361F" }}>
    <Titulo t="ELENCO · O PALMEIRAS TEM MUNDIAL?!" />
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", rowGap: 20, padding: "30px 10px", justifyItems: "center" }}>
      <Cel k="PAL1951" e="comemorando" pose="taca_alto" obj={<TacaAntigaG x={436} y={126} s={0.5} />} rot="PAL 1951" antigo />
      <Cel k="JUV1951" e="convencido" rot="JUV 1951" antigo />
      <Cel k="LOCUTOR" e="boca_aberta" pose="segurando" obj={<MicrofoneAntigo />} rot="LOCUTOR DE RÁDIO 1951" antigo />
      <Cel k="COR" e="bravo" pose="segurando" obj={<Convite />} rot="RIVAL (COR)" />
      <Cel k="DIRIGENTE" e="neutro" pose="segurando" obj={<Pasta />} rot="DIRIGENTE (GENÉRICO)" />
      <Cel k="FLU" e="convencido" rot="FLU (PONTA)" />
    </div>
  </AbsoluteFill>
);
