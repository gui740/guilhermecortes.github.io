import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ANTON, BEBAS } from "../../theme";
import { ROUND } from "../../cartoon/Cenarios";
import { Personagem, PersonagemProps, Expressao } from "../../cartoon/Personagem";

export const OUT = "#1A110C";
export const RUBRO = "#C8102E";
export const NEGRO = "#111111";

export const Abs: React.FC<{ x: number; y: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ x, y, children, style }) => (
  <div style={{ position: "absolute", left: x, top: y, ...style }}>{children}</div>
);

export const useSec = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { s: f / fps, f, fps };
};

/* ------------------------------- elenco ------------------------------- */
export type P = Partial<PersonagemProps>;
export const NARRADOR: P = { bigode: true, cabelo: "capacete", corCabelo: "#2B1B10", terno: "#22252B", gravata: RUBRO, pele: "#E8A877" };
export const REMADOR: P = { bigode: true, cabelo: "lados", corCabelo: "#3A2414", terno: "#F1ECE0", gravata: NEGRO, pele: "#F2C29B" };
export const REMADOR2: P = { bigode: true, chapeu: true, terno: "#2E2E36", gravata: RUBRO, pele: "#F8E2CC" };
export const DIRIGENTE: P = { oculos: true, bigode: true, cabelo: "grisalho", terno: "#4E4036", gravata: "#7A1E1E", pele: "#F4E6DC" };
export const LADRAO: P = { chapeu: true, terno: "#3A3A44", gravata: "#555", pele: "#E0B58F" };
export const TRICOLOR: P = { cabelo: "topete", corCabelo: "#2B1B10", terno: "#7B1E3A", gravata: "#1E7B4A", pele: "#F2C29B", cachecol: "#1E7B4A" };
export const fan = (pele = "#F2C29B", cabelo: PersonagemProps["cabelo"] = "capacete"): P => ({ cachecol: RUBRO, gravata: RUBRO, terno: NEGRO, pele, cabelo, corCabelo: "#1E140E" });

/** Personagem posicionado; enquadramentos: "close" (cabeça enche a tela), "medio", "corpo". */
export const Ator: React.FC<{ p: P; e: Expressao; plano?: "close" | "medio" | "corpo"; x?: number; y?: number; fase?: number; espelhar?: boolean; braco?: boolean; pulo?: number; alt?: number }> = ({
  p,
  e,
  plano = "medio",
  x = 540,
  y,
  fase = 0,
  espelhar,
  braco,
  pulo,
  alt,
}) => {
  const h = alt ?? (plano === "close" ? 1850 : plano === "medio" ? 1180 : 720);
  const s = h / 520;
  const top = y ?? (plano === "close" ? 700 - 150 * s : plano === "medio" ? 980 - 150 * s : 1720 - h);
  return (
    <div style={{ position: "absolute", left: x - 150 * s, top, filter: "drop-shadow(24px 18px 22px rgba(20,8,0,0.45))" }}>
      <Personagem {...p} altura={h} expressao={e} fase={fase} espelhar={espelhar} bracoErguido={braco} pulo={pulo} />
    </div>
  );
};

/* ------------------------------- mar / barco ------------------------------- */

/** Mar do Rio com céu, sol e o Pão de Açúcar ao fundo. */
export const Mar: React.FC<{ children?: React.ReactNode; horizonte?: number; tarde?: boolean; pao?: boolean }> = ({ children, horizonte = 1000, tarde = false, pao = true }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: tarde ? "linear-gradient(180deg,#F6B26B 0%,#FCE3B0 70%)" : "linear-gradient(180deg,#6EC1F5 0%,#CBEBFF 75%)" }}>
      <div style={{ position: "absolute", left: 120, top: horizonte - 520, width: 200, height: 200, borderRadius: "50%", background: "#FFE27A", border: `6px solid ${OUT}`, boxShadow: "0 0 90px 40px rgba(255,226,122,0.55)" }} />
      {pao ? (
        <svg width="1080" height="520" viewBox="0 0 1080 520" style={{ position: "absolute", left: 0, top: horizonte - 516 }}>
          <path d="M560 520 Q600 420 660 400 Q700 330 760 300 Q800 110 880 70 Q940 60 960 140 Q990 260 1010 320 Q1050 360 1080 380 L1080 520 Z" fill="#3E7A4A" stroke={OUT} strokeWidth="6" />
          <path d="M300 520 Q360 440 430 430 Q470 380 520 400 Q560 440 600 520 Z" fill="#4E8C58" stroke={OUT} strokeWidth="6" />
          <line x1="880" y1="76" x2="660" y2="398" stroke={OUT} strokeWidth="3" />
        </svg>
      ) : null}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: horizonte,
          bottom: 0,
          background: "linear-gradient(180deg,#1E7FB8,#0F5A8A)",
          borderTop: `6px solid ${OUT}`,
        }}
      >
        {[0, 1, 2, 3, 4, 5, 6].map((r) => (
          <div
            key={r}
            style={{
              position: "absolute",
              top: 40 + r * 120,
              left: -200 + (((f * (2 + r * 0.4)) % 240) - 120) * (r % 2 ? 1 : -1),
              width: 1600,
              height: 28,
              background: "repeating-linear-gradient(90deg, rgba(255,255,255,0.75) 0 70px, transparent 70px 240px)",
              borderRadius: 14,
              opacity: 0.55,
            }}
          />
        ))}
      </div>
      {children}
    </AbsoluteFill>
  );
};

/** Barco a remo com remadores de cabeça redonda; remos batem no ritmo. */
export const Barco: React.FC<{ largura?: number; nome?: string; remadores?: number; inclina?: number; ritmo?: number; cores?: [string, string] }> = ({ largura = 860, nome = "PHERUSA", remadores = 4, inclina = 0, ritmo = 1, cores = [RUBRO, NEGRO] }) => {
  const f = useCurrentFrame();
  const peles = ["#F2C29B", "#E8A877", "#F8E2CC", "#D9A27A", "#C68B5F"];
  const bob = Math.sin(f / 7) * 6;
  return (
    <div style={{ width: largura, height: largura * 0.52, rotate: `${inclina + Math.sin(f / 9) * 1.5}deg`, translate: `0 ${bob}px`, transformOrigin: "50% 80%" }}>
      <svg width={largura} height={largura * 0.52} viewBox="0 0 800 416" style={{ overflow: "visible" }}>
        {Array.from({ length: remadores }).map((_, i) => {
          const x = 190 + i * (430 / Math.max(1, remadores - 1));
          const a = Math.sin(f / (5 / ritmo) + i * 0.2);
          return (
            <g key={i}>
              {/* remo */}
              <g transform={`rotate(${a * 22} ${x} 250)`}>
                <line x1={x} y1={250} x2={x - 70} y2={400} stroke="#8A5A30" strokeWidth="10" strokeLinecap="round" />
                <path d={`M${x - 64} 380 L${x - 96} 446 L${x - 66} 452 L${x - 50} 388 Z`} fill={i % 2 ? cores[1] : cores[0]} stroke={OUT} strokeWidth="4" />
              </g>
              {/* corpo listrado */}
              <path d={`M${x - 34} 236 Q${x} 196 ${x + 34} 236 L${x + 30} 276 L${x - 30} 276 Z`} fill="#fff" stroke={OUT} strokeWidth="5" />
              <path d={`M${x - 32} 246 L${x + 32} 246 M${x - 31} 262 L${x + 31} 262`} stroke={cores[0]} strokeWidth="8" />
              <circle cx={x} cy={168} r={44} fill={peles[i % peles.length]} stroke={OUT} strokeWidth="5" />
              <path d={`M${x - 42} 158 Q${x} 104 ${x + 42} 158 Q${x} 136 ${x - 42} 158 Z`} fill="#2B1B10" />
              <circle cx={x - 15} cy={170} r={6} fill={OUT} />
              <circle cx={x + 15} cy={170} r={6} fill={OUT} />
              <path d={`M${x - 16} 190 Q${x} ${200 + a * 4} ${x + 16} 190`} stroke={OUT} strokeWidth="5" fill="none" strokeLinecap="round" />
            </g>
          );
        })}
        <path d="M20 250 Q400 230 780 250 L720 352 Q400 392 80 352 Z" fill="#9A6234" stroke={OUT} strokeWidth="7" />
        <path d="M40 276 Q400 258 760 276" stroke="#6E4020" strokeWidth="6" fill="none" />
        <path d="M60 318 Q400 300 740 318" stroke="#6E4020" strokeWidth="6" fill="none" />
        <rect x="290" y="282" width="220" height="56" rx="8" fill="#F4E9D0" stroke={OUT} strokeWidth="5" />
        <text x="400" y="326" textAnchor="middle" fontFamily={ROUND} fontWeight={800} fontSize="44" fill={OUT}>
          {nome}
        </text>
      </svg>
    </div>
  );
};

/** Remo gigante que varre a tela (elemento recorrente usado como transição). */
export const RemoWipe: React.FC<{ dur?: number }> = ({ dur = 12 }) => {
  const f = useCurrentFrame();
  if (f > dur) return null;
  const u = interpolate(f, [0, dur], [0, 1], { extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 2) });
  const r = interpolate(u, [0, 1], [-70, 70]);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: 540 - 140, top: -1500, width: 280, height: 3000, transformOrigin: "50% 0%", rotate: `${r}deg` }}>
        <svg width="280" height="3000" viewBox="0 0 280 3000" style={{ position: "absolute", left: 0, top: 0 }}>
          <rect x="118" y="0" width="44" height="2300" fill="#9A6234" stroke={OUT} strokeWidth="8" />
          <path d="M100 2280 Q140 2240 180 2280 L250 2960 Q140 3010 30 2960 Z" fill={RUBRO} stroke={OUT} strokeWidth="10" />
          <path d="M70 2620 L210 2620 L232 2820 L48 2820 Z" fill={NEGRO} />
        </svg>
      </div>
    </AbsoluteFill>
  );
};

/** Bola de futebol simples. */
export const Bola: React.FC<{ tam?: number }> = ({ tam = 300 }) => (
  <svg width={tam} height={tam} viewBox="0 0 200 200">
    <circle cx="100" cy="100" r="92" fill="#fff" stroke={OUT} strokeWidth="7" />
    <path d="M100 66 L132 89 L120 126 L80 126 L68 89 Z" fill={OUT} />
    {[0, 72, 144, 216, 288].map((a) => (
      <g key={a} transform={`rotate(${a} 100 100)`}>
        <line x1="100" y1="66" x2="100" y2="22" stroke={OUT} strokeWidth="5" />
        <path d="M86 12 Q100 6 114 12 L110 24 L90 24 Z" fill={OUT} />
      </g>
    ))}
  </svg>
);

/** Polaroid com foto real, legenda manuscrita e crédito. */
export const Polaroid: React.FC<{ src: string; largura: number; altura: number; legenda?: string; credito?: string; rot?: number; pos?: string }> = ({ src, largura, altura, legenda, credito, rot = -3, pos = "50% 40%" }) => (
  <div style={{ width: largura + 40, background: "#FBF8F1", padding: "20px 20px 18px", rotate: `${rot}deg`, boxShadow: "18px 22px 0 rgba(17,17,17,0.55)", border: `4px solid ${OUT}` }}>
    <div style={{ width: largura, height: altura, overflow: "hidden", position: "relative", background: "#222" }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: pos }} />
      {credito ? (
        <div style={{ position: "absolute", right: 8, bottom: 6, fontFamily: "Inter, Arial", fontSize: 20, color: "rgba(255,255,255,0.9)", textShadow: "0 1px 3px #000" }}>{credito}</div>
      ) : null}
    </div>
    {legenda ? <div style={{ fontFamily: BEBAS, fontSize: 64, color: OUT, textAlign: "center", marginTop: 10, letterSpacing: 2 }}>{legenda}</div> : null}
  </div>
);

/** Foto em tela cheia com Ken Burns, papel envelhecido e crédito. */
export const FotoCheia: React.FC<{ src: string; credito: string; pos?: string; de?: number; ate?: number; sepia?: number }> = ({ src, credito, pos = "50% 50%", de = 1.08, ate = 1.22, sepia = 0 }) => {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const z = interpolate(f, [0, durationInFrames], [de, ate]);
  return (
    <AbsoluteFill style={{ background: NEGRO, overflow: "hidden" }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: pos, scale: `${z}`, filter: `sepia(${sepia}) contrast(1.05)` }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 70% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.6) 100%)" }} />
      <div style={{ position: "absolute", right: 24, bottom: 24, fontFamily: "Inter, Arial", fontSize: 22, color: "rgba(255,255,255,0.85)", textShadow: "0 1px 4px #000" }}>{credito}</div>
    </AbsoluteFill>
  );
};

/** Etiqueta de papel rasgado (estilo 1). */
export const Etiqueta: React.FC<{ children: React.ReactNode; cor?: string; corTexto?: string; size?: number; rot?: number }> = ({ children, cor = NEGRO, corTexto = "#fff", size = 80, rot = -2 }) => {
  const pts: string[] = [];
  const n = 22;
  for (let i = 0; i <= n; i++) pts.push(`${(i / n) * 100}% ${(Math.sin(i * 7.3 + 1) * 0.5 + 0.5) * 8}%`);
  for (let i = n; i >= 0; i--) pts.push(`${(i / n) * 100}% ${100 - (Math.sin(i * 5.1 + 3) * 0.5 + 0.5) * 8}%`);
  return (
    <div style={{ display: "inline-block", rotate: `${rot}deg`, filter: "drop-shadow(10px 12px 0 rgba(0,0,0,0.45))" }}>
      <div style={{ background: cor, clipPath: `polygon(${pts.join(",")})`, padding: "22px 40px", fontFamily: ANTON, fontSize: size, color: corTexto, lineHeight: 1.05, letterSpacing: 1, textAlign: "center" }}>{children}</div>
    </div>
  );
};
