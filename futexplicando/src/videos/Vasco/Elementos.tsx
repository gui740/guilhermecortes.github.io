import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { ROUND } from "../../cartoon/Cenarios";
import { MiniTorcedor } from "../../cartoon/Personagem";
import { OUT } from "../Flamengo/Elementos";

export const CRUZ = "#D7262E";
export const PRETO = "#111111";

/** Cruz de Malta (cruz pátea) do Vasco, desenhada em código. */
export const Cruz: React.FC<{ tam?: number; cor?: string; borda?: string }> = ({ tam = 200, cor = CRUZ, borda = "#fff" }) => (
  <svg width={tam} height={tam} viewBox="0 0 100 100">
    {[0, 90, 180, 270].map((a) => (
      <path key={a} transform={`rotate(${a} 50 50)`} d="M44 50 L30 6 L50 14 L70 6 L56 50 Z" fill={cor} stroke={borda} strokeWidth="3" strokeLinejoin="round" />
    ))}
    <circle cx="50" cy="50" r="7" fill={cor} />
  </svg>
);

/** Caravela de 1498 com a cruz nas velas (elemento recorrente do vídeo). */
export const Caravela: React.FC<{ largura?: number; inclina?: number }> = ({ largura = 820, inclina = 0 }) => {
  const f = useCurrentFrame();
  const v = Math.sin(f / 8) * 4;
  return (
    <div style={{ width: largura, height: largura * 0.95, rotate: `${inclina + Math.sin(f / 10) * 2}deg`, translate: `0 ${Math.sin(f / 7) * 8}px`, transformOrigin: "50% 85%" }}>
      <svg width={largura} height={largura * 0.95} viewBox="0 0 800 760" style={{ overflow: "visible" }}>
        <line x1="400" y1="40" x2="400" y2="560" stroke="#5A341A" strokeWidth="16" />
        <line x1="220" y1="160" x2="220" y2="560" stroke="#5A341A" strokeWidth="12" />
        <line x1="590" y1="200" x2="590" y2="560" stroke="#5A341A" strokeWidth="12" />
        {[
          [400, 90, 230, 300],
          [220, 190, 150, 220],
          [590, 230, 140, 200],
        ].map(([x, y, w, h], i) => (
          <g key={i}>
            <path d={`M${x - w / 2} ${y} Q${x + v} ${y + h * 0.5} ${x - w / 2} ${y + h} L${x + w / 2} ${y + h} Q${x + w / 2 + 30 + v} ${y + h * 0.5} ${x + w / 2} ${y} Z`} fill="#F6EEDC" stroke={OUT} strokeWidth="7" />
            <g transform={`translate(${x - w * 0.28 + v / 2} ${y + h * 0.2}) scale(${(w * 0.56) / 100})`}>
              {[0, 90, 180, 270].map((a) => (
                <path key={a} transform={`rotate(${a} 50 50)`} d="M44 50 L30 6 L50 14 L70 6 L56 50 Z" fill={CRUZ} />
              ))}
            </g>
          </g>
        ))}
        <path d="M400 40 L470 58 L400 76 Z" fill={CRUZ} stroke={OUT} strokeWidth="4" />
        <path d="M40 540 L760 540 Q740 640 640 700 L170 700 Q70 640 40 540 Z" fill="#8A5A30" stroke={OUT} strokeWidth="8" />
        <path d="M60 580 L740 580 M90 630 L710 630" stroke="#5E3818" strokeWidth="7" />
        <path d="M640 540 L640 490 L770 490 L760 540" fill="#8A5A30" stroke={OUT} strokeWidth="7" />
        <path d="M40 540 L40 500 L170 500 L170 540" fill="#8A5A30" stroke={OUT} strokeWidth="7" />
      </svg>
    </div>
  );
};

/** Cruz de Malta gigante girando e varrendo a tela (transição recorrente). */
export const CruzWipe: React.FC<{ dur?: number }> = ({ dur = 13 }) => {
  const f = useCurrentFrame();
  if (f > dur) return null;
  const u = interpolate(f, [0, dur], [0, 1], { extrapolateRight: "clamp" });
  const x = interpolate(u, [0, 1], [-1500, 1300]);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: x, top: 960 - 750, rotate: `${u * 240}deg`, filter: "drop-shadow(20px 24px 0 rgba(0,0,0,0.4))" }}>
        <Cruz tam={1500} borda={OUT} />
      </div>
    </AbsoluteFill>
  );
};

/** Carta datilografada letra a letra (Resposta Histórica). */
export const Carta: React.FC<{ linhas: string[]; inicio?: number; cps?: number; assinatura?: string }> = ({ linhas, inicio = 4, cps = 1.4, assinatura }) => {
  const f = useCurrentFrame();
  let resto = Math.max(0, (f - inicio) * cps);
  const total = linhas.join("").length;
  return (
    <div style={{ width: 880, minHeight: 1000, background: "#F3EAD3", border: `5px solid ${OUT}`, boxShadow: "18px 22px 0 rgba(0,0,0,0.45)", padding: "60px 64px", fontFamily: "'Courier New', Courier, monospace", color: "#22180F", rotate: "-1.5deg" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: `3px solid ${OUT}`, paddingBottom: 14, marginBottom: 30 }}>
        <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 40, lineHeight: 1.1 }}>
          CLUB DE REGATAS
          <br />
          VASCO DA GAMA
        </div>
        <Cruz tam={110} borda={OUT} />
      </div>
      {linhas.map((l, i) => {
        const n = Math.min(l.length, Math.floor(resto));
        resto -= l.length;
        return (
          <div key={i} style={{ fontSize: i === 0 ? 34 : 50, fontWeight: 700, lineHeight: 1.25, minHeight: i === 0 ? 46 : 64, marginBottom: 10 }}>
            {l.slice(0, Math.max(0, n))}
            {n > 0 && n < l.length ? <span style={{ opacity: f % 10 < 5 ? 1 : 0 }}>▌</span> : null}
          </div>
        );
      })}
      {assinatura && (f - inicio) * cps > total ? (
        <div style={{ marginTop: 40, textAlign: "right", fontFamily: "'Brush Script MT', cursive", fontStyle: "italic", fontSize: 64, opacity: interpolate((f - inicio) * cps - total, [0, 10], [0, 1], { extrapolateRight: "clamp" }) }}>{assinatura}</div>
      ) : null}
    </div>
  );
};

/** Trem a vapor do "Expresso da Vitória". */
export const Trem: React.FC<{ largura?: number }> = ({ largura = 1500 }) => {
  const f = useCurrentFrame();
  const roda = f * 12;
  const vag = (x: number, txt: string) => (
    <g key={x}>
      <rect x={x} y={120} width={330} height={190} rx={18} fill="#fff" stroke={OUT} strokeWidth="8" />
      <path d={`M${x + 4} 262 L${x + 326} 124 L${x + 326} 172 L${x + 4} 306 Z`} fill={PRETO} />
      <text x={x + 165} y={230} textAnchor="middle" fontFamily={ROUND} fontWeight={800} fontSize="54" fill={CRUZ} stroke={OUT} strokeWidth="2">{txt}</text>
      {[x + 70, x + 260].map((cx) => (
        <g key={cx} transform={`rotate(${roda} ${cx} 330)`}>
          <circle cx={cx} cy={330} r={42} fill="#333" stroke={OUT} strokeWidth="7" />
          <line x1={cx - 38} y1={330} x2={cx + 38} y2={330} stroke="#999" strokeWidth="6" />
        </g>
      ))}
    </g>
  );
  return (
    <svg width={largura} height={largura * 0.27} viewBox="0 0 1500 400" style={{ overflow: "visible" }}>
      {[0, 1, 2].map((i) => {
        const t = ((f + i * 9) % 27) / 27;
        return <circle key={i} cx={1290 - t * 160} cy={40 - t * 120} r={30 + t * 50} fill="#EEE" stroke={OUT} strokeWidth="5" opacity={1 - t} />;
      })}
      {vag(0, "1948")}
      {vag(350, "VASCO")}
      <rect x={720} y={90} width={300} height={220} rx={16} fill={PRETO} stroke={OUT} strokeWidth="8" />
      <rect x={1000} y={170} width={330} height={140} rx={60} fill="#2A2A2A" stroke={OUT} strokeWidth="8" />
      <rect x={1240} y={60} width={60} height={120} fill="#2A2A2A" stroke={OUT} strokeWidth="8" />
      <rect x={760} y={120} width={110} height={90} fill="#FFE9A8" stroke={OUT} strokeWidth="6" />
      <g transform="translate(905 125) scale(0.9)">
        {[0, 90, 180, 270].map((a) => (
          <path key={a} transform={`rotate(${a} 50 50)`} d="M44 50 L30 6 L50 14 L70 6 L56 50 Z" fill={CRUZ} />
        ))}
      </g>
      {[800, 960, 1120, 1270].map((cx) => (
        <g key={cx} transform={`rotate(${roda} ${cx} 330)`}>
          <circle cx={cx} cy={330} r={48} fill="#333" stroke={OUT} strokeWidth="7" />
          <line x1={cx - 44} y1={330} x2={cx + 44} y2={330} stroke="#999" strokeWidth="6" />
        </g>
      ))}
    </svg>
  );
};

/** Arquibancada sendo erguida degrau a degrau, com mini-torcedores carregando tijolos. */
export const Obra: React.FC<{ prog: number }> = ({ prog }) => {
  const degraus = 7;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 360, height: 900 }}>
      {Array.from({ length: degraus }).map((_, i) => {
        const p = Math.max(0, Math.min(1, prog * degraus - i));
        return (
          <div
            key={i}
            style={{ position: "absolute", left: 60 + i * 40, right: 60 + i * 40, bottom: i * 100, height: 100 * p, background: i % 2 ? "#C9C2B4" : "#B6AE9E", border: p > 0 ? `5px solid ${OUT}` : "none", transformOrigin: "50% 100%" }}
          />
        );
      })}
      <div style={{ position: "absolute", left: 40, right: 40, bottom: -150, display: "flex", justifyContent: "space-between" }}>
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} style={{ position: "relative" }}>
            <div style={{ position: "absolute", left: 18, top: -36, width: 70, height: 34, background: "#B5532D", border: `4px solid ${OUT}` }} />
            <MiniTorcedor cor={i % 2 ? PRETO : "#fff"} tam={110} fase={i * 0.8} />
          </div>
        ))}
      </div>
    </div>
  );
};
