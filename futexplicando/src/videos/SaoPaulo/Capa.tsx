import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { Coin } from "../../components/Coin";
import { Rays, Seal } from "../../components/Graphics";
import { Grain, PaperBackground } from "../../components/Paper";
import { ANTON, BEBAS, C } from "../../theme";
import { A, D } from "./data";

/** Capa: moeda em pé + "ONDE A MOEDA CAI EM PÉ". */
export const CapaSaoPaulo: React.FC = () => {
  const size = 620;
  const floorY = 1240;
  return (
    <AbsoluteFill>
      <PaperBackground />
      <div style={{ position: "absolute", left: -60, top: floorY - 640, width: 1200, height: 1200 }}>
        <Rays color={C.red} opacity={0.3} count={24} />
      </div>
      <Img src={staticFile(A.escudoAtual)} style={{ position: "absolute", left: 540 - 360, top: floorY - 860, width: 720, height: 720, opacity: 0.12, rotate: "-8deg" }} />
      <div style={{ position: "absolute", left: 60, right: 60, top: floorY + size / 2 - 4, height: 10, background: C.black, borderRadius: 5 }} />
      <div style={{ position: "absolute", left: 540 - size * 0.3, top: floorY + size / 2 - 22, width: size * 0.6, height: 34, borderRadius: "50%", background: "rgba(17,17,17,0.6)", filter: "blur(12px)" }} />
      <div style={{ position: "absolute", left: 540 - size / 2, top: floorY - size / 2 }}>
        <Coin id="capa" size={size} angle={0.32} tilt={-2} crest={A.escudoAtual} />
      </div>
      <div style={{ position: "absolute", top: 210, width: "100%", textAlign: "center" }}>
        <div style={{ fontFamily: BEBAS, fontSize: 70, letterSpacing: 14, color: C.red }}>CLUBE DA FÉ</div>
        {D.capa.texto.map((l, i) => (
          <div
            key={i}
            style={{
              fontFamily: ANTON,
              fontSize: 168,
              lineHeight: 0.98,
              color: i ? C.red : C.black,
              textShadow: i ? `7px 7px 0 ${C.black}` : `7px 7px 0 ${C.red}`,
              rotate: `${i ? 1 : -1.5}deg`,
            }}
          >
            {l}
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", top: floorY + size / 2 + 70, width: "100%", display: "flex", justifyContent: "center" }}>
        <div style={{ background: C.black, color: C.white, fontFamily: ANTON, fontSize: 72, padding: "10px 40px", boxShadow: `8px 8px 0 ${C.red}`, rotate: "-2deg" }}>
          {D.capa.sub}
        </div>
      </div>
      <Seal handle={D.handle} />
      <Grain opacity={0.1} />
    </AbsoluteFill>
  );
};
