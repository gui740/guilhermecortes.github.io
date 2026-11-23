import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";

const OUT = "#1A110C";

/** Luz quente de lustre vindo de cima + sombra nas bordas (cinematográfico). */
export const LuzQuente: React.FC<{ x?: number; y?: number; forca?: number }> = ({ x = 50, y = 8, forca = 1 }) => {
  const frame = useCurrentFrame();
  const fl = 1 + Math.sin(frame / 5) * 0.03;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 70% 45% at ${x}% ${y}%, rgba(255,214,140,${0.55 * forca * fl}) 0%, rgba(255,190,110,0.12) 45%, rgba(0,0,0,0) 70%)`, mixBlendMode: "screen" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 85% 75% at 50% 42%, rgba(0,0,0,0) 50%, rgba(25,12,4,0.72) 100%)" }} />
    </AbsoluteFill>
  );
};

/** Lustre dourado com lâmpadas acesas. */
export const Lustre: React.FC<{ x: number; y: number; s?: number }> = ({ x, y, s = 1 }) => {
  const frame = useCurrentFrame();
  const g = 0.85 + Math.sin(frame / 6) * 0.1;
  return (
    <div style={{ position: "absolute", left: x - 260 * s, top: y, width: 520 * s, height: 300 * s }}>
      <div style={{ position: "absolute", left: -200 * s, top: -160 * s, width: 920 * s, height: 620 * s, borderRadius: "50%", background: `radial-gradient(circle, rgba(255,230,160,${0.6 * g}) 0%, rgba(255,210,120,0) 60%)` }} />
      <svg width={520 * s} height={300 * s} viewBox="0 0 520 300" style={{ position: "absolute" }}>
        <line x1="260" y1="-200" x2="260" y2="110" stroke={OUT} strokeWidth="6" />
        {[-1, 1].map((d) => (
          <g key={d}>
            <path d={`M260 130 Q${260 + d * 120} 190 ${260 + d * 200} 120`} stroke="#B8902E" strokeWidth="12" fill="none" />
            <path d={`M260 140 Q${260 + d * 70} 210 ${260 + d * 110} 160`} stroke="#B8902E" strokeWidth="10" fill="none" />
          </g>
        ))}
        <ellipse cx="260" cy="135" rx="40" ry="26" fill="#D4AF37" stroke={OUT} strokeWidth="5" />
        {[60, 150, 370, 460].map((cx, i) => (
          <g key={cx}>
            <circle cx={cx} cy={i % 3 === 0 ? 112 : 152} r="22" fill={`rgba(255,240,190,${g})`} stroke="#E8C870" strokeWidth="4" />
          </g>
        ))}
      </svg>
    </div>
  );
};

/** Sala rica: papel de parede, lambri, cortina de veludo, janela com luz, quadros, piso e tapete. */
export const SalaRica: React.FC<{ children?: React.ReactNode; cortina?: boolean; janela?: boolean; tapete?: boolean; lustre?: boolean; parede?: string; quadros?: boolean }> = ({
  children,
  cortina = true,
  janela = true,
  tapete = true,
  lustre = true,
  parede = "#B9946A",
  quadros = true,
}) => (
  <AbsoluteFill style={{ background: parede }}>
    <AbsoluteFill style={{ background: "repeating-linear-gradient(90deg, rgba(255,240,210,0.18) 0 34px, rgba(80,40,10,0.10) 34px 70px)" }} />
    <AbsoluteFill style={{ background: "repeating-linear-gradient(90deg, transparent 0 66px, rgba(70,35,10,0.25) 66px 70px)" }} />
    {janela ? (
      <div style={{ position: "absolute", left: 660, top: 330, width: 340, height: 560, background: "linear-gradient(180deg,#FFF6DA,#F2D9A0)", border: `14px solid #5A341A`, outline: `5px solid ${OUT}`, boxShadow: "0 0 80px 30px rgba(255,230,170,0.45)" }}>
        <div style={{ position: "absolute", inset: 0, background: "repeating-linear-gradient(180deg, rgba(120,80,30,0.35) 0 6px, transparent 6px 26px)" }} />
        <div style={{ position: "absolute", left: "50%", top: 0, bottom: 0, width: 12, background: "#5A341A" }} />
      </div>
    ) : null}
    {cortina ? (
      <>
        <div style={{ position: "absolute", left: 590, top: 250, width: 130, height: 760, background: "repeating-linear-gradient(90deg,#7A1414 0 22px,#9E2020 22px 44px)", borderRight: `5px solid ${OUT}`, borderRadius: "0 0 30px 30px" }} />
        <div style={{ position: "absolute", left: 960, top: 250, width: 130, height: 760, background: "repeating-linear-gradient(90deg,#9E2020 0 22px,#7A1414 22px 44px)", borderLeft: `5px solid ${OUT}`, borderRadius: "0 0 30px 30px" }} />
        <div style={{ position: "absolute", left: 570, top: 230, width: 540, height: 46, background: "#5A341A", border: `5px solid ${OUT}`, borderRadius: 10 }} />
      </>
    ) : null}
    {quadros ? (
      <div style={{ position: "absolute", left: 90, top: 360, width: 300, height: 220, background: "linear-gradient(180deg,#9CC9E8,#7FB069)", border: `16px solid #8A6024`, outline: `5px solid ${OUT}`, boxShadow: "10px 12px 18px rgba(0,0,0,0.4)" }}>
        <div style={{ position: "absolute", left: 30, bottom: 30, width: 120, height: 60, borderRadius: "50% 50% 0 0", background: "#5E8C3A" }} />
        <div style={{ position: "absolute", right: 40, top: 30, width: 40, height: 40, borderRadius: "50%", background: "#F7D774" }} />
      </div>
    ) : null}
    {/* lambri */}
    <div style={{ position: "absolute", left: 0, right: 0, top: 1060, height: 330, background: "repeating-linear-gradient(90deg,#6A3D1E 0 150px,#5A3216 150px 156px)", borderTop: `16px solid #4A2810` }} />
    {/* piso */}
    <div style={{ position: "absolute", left: 0, right: 0, top: 1390, bottom: 0, background: "repeating-linear-gradient(180deg,#7A4A26 0 46px,#6A3E1E 46px 50px)" }} />
    {tapete ? <div style={{ position: "absolute", left: 90, right: 90, top: 1450, height: 400, background: "#8E2A20", border: `10px solid #C9A040`, outline: `5px solid ${OUT}`, clipPath: "polygon(18% 0, 82% 0, 100% 100%, 0 100%)" }} /> : null}
    {lustre ? <Lustre x={540} y={-20} /> : null}
    {children}
    <LuzQuente />
  </AbsoluteFill>
);

/** Porta de madeira com placa em cima (ex.: "CBF"). */
export const Porta: React.FC<{ placa: string; aberta?: number }> = ({ placa, aberta = 0 }) => (
  <div style={{ position: "relative", width: 560, height: 980 }}>
    <div style={{ position: "absolute", left: 100, top: 0, width: 360, height: 110, background: "linear-gradient(180deg,#F2B33D,#D08A1A)", border: `7px solid ${OUT}`, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Baloo 2', Arial", fontWeight: 800, fontSize: 92, color: OUT, boxShadow: "8px 10px 16px rgba(0,0,0,0.4)" }}>{placa}</div>
    <div style={{ position: "absolute", left: 0, top: 160, width: 560, height: 820, background: "#4A2810", border: `7px solid ${OUT}` }} />
    <div style={{ position: "absolute", left: 40, top: 200, width: 480, height: 780, background: "#FFF2C8", boxShadow: "0 0 60px 20px rgba(255,230,160,0.5)" }} />
    <div style={{ position: "absolute", left: 40, top: 200, width: 480, height: 780, background: "linear-gradient(90deg,#7A4A22,#5A3416)", border: `6px solid ${OUT}`, transformOrigin: "0 50%", rotate: `0 1 0 ${-aberta * 70}deg` }}>
      {[0, 1].map((r) =>
        [0, 1].map((c) => <div key={`${r}${c}`} style={{ position: "absolute", left: 60 + c * 190, top: 60 + r * 200, width: 160, height: 170, background: "#FFF6DA", border: `6px solid ${OUT}` }} />),
      )}
      <div style={{ position: "absolute", left: 70, top: 460, width: 340, height: 250, border: `6px solid ${OUT}`, background: "rgba(0,0,0,0.12)" }} />
      <div style={{ position: "absolute", right: 30, top: 420, width: 26, height: 26, borderRadius: "50%", background: "#D4AF37", border: `4px solid ${OUT}` }} />
    </div>
  </div>
);

/** Rádio antigo com mostrador aceso (conteúdo opcional no mostrador). */
export const Radio: React.FC<{ largura?: number; children?: React.ReactNode }> = ({ largura = 520, children }) => {
  const frame = useCurrentFrame();
  const g = 0.8 + Math.sin(frame / 4) * 0.1;
  const h = largura * 1.05;
  return (
    <div style={{ position: "relative", width: largura, height: h }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: `${largura / 2}px ${largura / 2}px 30px 30px`, background: "linear-gradient(180deg,#9A5426,#5E2E10)", border: `8px solid ${OUT}`, boxShadow: "14px 16px 24px rgba(0,0,0,0.5)" }} />
      <div style={{ position: "absolute", left: largura * 0.14, top: largura * 0.12, width: largura * 0.72, height: h * 0.52, borderRadius: `${largura * 0.36}px ${largura * 0.36}px 16px 16px`, background: `radial-gradient(circle at 50% 70%, rgba(255,200,90,${g}), #C25A10)`, border: `7px solid ${OUT}`, overflow: "hidden", boxShadow: `0 0 60px rgba(255,170,60,${0.6 * g})` }}>
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={i} style={{ position: "absolute", left: `${12 + i * 19}%`, top: 0, bottom: 0, width: 10, background: "rgba(90,40,10,0.8)" }} />
        ))}
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>{children}</div>
      </div>
      <div style={{ position: "absolute", left: largura * 0.3, top: h * 0.7, width: largura * 0.4, height: largura * 0.22, borderRadius: "50% 50% 8px 8px", background: `radial-gradient(circle at 50% 100%, #FFF1B8, #E7B74A)`, border: `6px solid ${OUT}` }}>
        <div style={{ position: "absolute", left: "50%", bottom: 4, width: 6, height: largura * 0.16, background: "#B3261E", transformOrigin: "50% 100%", rotate: `${-40 + (frame % 60)}deg` }} />
      </div>
      {[0.16, 0.74].map((x) => (
        <div key={x} style={{ position: "absolute", left: largura * x, top: h * 0.74, width: largura * 0.1, height: largura * 0.1, borderRadius: "50%", background: "#3A1A08", border: `5px solid ${OUT}` }} />
      ))}
    </div>
  );
};

/** Mesa de reunião em perspectiva com papéis espalhados (primeiro plano). */
export const MesaReuniao: React.FC<{ top?: number }> = ({ top = 1300 }) => (
  <div style={{ position: "absolute", left: -60, right: -60, top, height: 700 }}>
    <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg,#8A5226,#5E3214)", borderTop: `10px solid ${OUT}`, clipPath: "polygon(8% 0, 92% 0, 100% 100%, 0 100%)" }} />
    {[
      [200, 60, -8],
      [430, 40, 6],
      [640, 90, -14],
      [820, 50, 10],
      [330, 180, 4],
    ].map(([x, y, r], i) => (
      <div key={i} style={{ position: "absolute", left: x, top: y, width: 150, height: 90, background: "#F6EED8", border: `4px solid ${OUT}`, rotate: `${r}deg`, boxShadow: "4px 6px 0 rgba(0,0,0,0.25)" }}>
        <div style={{ margin: 14, height: 54, background: "repeating-linear-gradient(180deg, rgba(26,17,12,0.45) 0 4px, transparent 4px 12px)" }} />
      </div>
    ))}
  </div>
);

/** Quadro emoldurado na parede com texto (como o "TORNEIO INTERNACIONAL..." da referência). */
export const QuadroTexto: React.FC<{ linhas: string[]; largura?: number; children?: React.ReactNode }> = ({ linhas, largura = 520, children }) => (
  <div style={{ width: largura, background: "#3A1F0E", border: `18px solid #7A4A1E`, outline: `5px solid ${OUT}`, padding: "26px 20px", textAlign: "center", boxShadow: "12px 14px 22px rgba(0,0,0,0.45)" }}>
    {children}
    {linhas.map((l, i) => (
      <div key={i} style={{ fontFamily: "'Baloo 2', Arial", fontWeight: 800, fontSize: 58, lineHeight: 1.0, color: "#F0B23C" }}>{l}</div>
    ))}
  </div>
);

/** Vareta em primeira pessoa (vem de baixo, ponta de bola preta), como na referência. */
export const VaretaPOV: React.FC<{ x: number; y: number }> = ({ x, y }) => {
  const baseX = 640;
  const baseY = 2100;
  const ang = Math.atan2(y - baseY, x - baseX);
  const len = Math.hypot(x - baseX, y - baseY);
  return (
    <div style={{ position: "absolute", left: baseX, top: baseY, width: len, height: 0, transformOrigin: "0 0", rotate: `${ang}rad` }}>
      <div style={{ position: "absolute", left: 0, top: -70, width: len - 40, height: 140, background: "linear-gradient(180deg,#9A6A3A,#5A3416)", border: `6px solid ${OUT}`, clipPath: "polygon(0 0, 100% 36%, 100% 64%, 0 100%)" }} />
      <div style={{ position: "absolute", left: len * 0.18, top: -80, width: 70, height: 160, background: "#F2EAD8", border: `6px solid ${OUT}`, borderRadius: 10, clipPath: "polygon(0 0, 100% 10%, 100% 90%, 0 100%)" }} />
      <div style={{ position: "absolute", left: len - 70, top: -46, width: 92, height: 92, borderRadius: "50%", background: "radial-gradient(circle at 35% 30%, #555, #0A0A0A)", border: `5px solid ${OUT}` }} />
    </div>
  );
};

/** Escudo numa placa dourada (para aparecer na mesa/parede). */
export const PlacaEscudo: React.FC<{ src: string; tam?: number }> = ({ src, tam = 260 }) => (
  <div style={{ width: tam, height: tam, background: "radial-gradient(circle at 40% 30%, #FFF6DA, #E8D3A0)", border: `10px solid #B8902E`, outline: `5px solid ${OUT}`, borderRadius: 24, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "12px 14px 22px rgba(0,0,0,0.45)" }}>
    <Img src={staticFile(src)} style={{ width: tam * 0.78, height: tam * 0.78, objectFit: "contain" }} />
  </div>
);
