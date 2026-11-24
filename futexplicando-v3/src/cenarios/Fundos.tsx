import React, { useMemo } from "react";
import { AbsoluteFill } from "remotion";
import { COR } from "../estilo/tokens";
import { Arquibancada, Ceu, Gramado, Refletor } from "./EstadioNoite";

/** Fundos em camadas de profundidade: cada fundo devolve [longe, meio, chao] para o parallax. */
export type CamadasFundo = { longe: React.ReactNode; meio?: React.ReactNode; chao?: React.ReactNode };

const rnd = (s: number) => {
  const x = Math.sin(s * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};

const Refletores: React.FC<{ forca?: number }> = ({ forca = 1 }) => (
  <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0, opacity: forca }}>
    <Refletor x={110} y={170} s={0.85} lado={-1} />
    <Refletor x={970} y={170} s={0.85} lado={1} />
  </svg>
);

const Madeira: React.FC<{ cor1: string; cor2: string; ripas?: number; vertical?: boolean }> = ({ cor1, cor2, ripas = 8, vertical = true }) => (
  <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
    {Array.from({ length: ripas }).map((_, i) =>
      vertical ? (
        <g key={i}>
          <rect x={(i * 1080) / ripas} y={0} width={1080 / ripas} height={1920} fill={i % 2 ? cor1 : cor2} />
          <path d={`M${(i * 1080) / ripas + 20} 0 Q${(i * 1080) / ripas + 60} 900 ${(i * 1080) / ripas + 30} 1920`} stroke="rgba(0,0,0,0.12)" strokeWidth={4} fill="none" />
        </g>
      ) : (
        <g key={i}>
          <rect x={0} y={(i * 1920) / ripas} width={1080} height={1920 / ripas} fill={i % 2 ? cor1 : cor2} />
          <path d={`M0 ${(i * 1920) / ripas + 40} Q540 ${(i * 1920) / ripas + 80} 1080 ${(i * 1920) / ripas + 30}`} stroke="rgba(0,0,0,0.13)" strokeWidth={5} fill="none" />
        </g>
      ),
    )}
  </svg>
);

const Vinheta: React.FC<{ forca?: number }> = ({ forca = 0.6 }) => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse 85% 70% at 50% 45%, rgba(0,0,0,0) 50%, rgba(5,8,25,${forca}) 100%)` }} />
);

export const fundo = (tipo: string): CamadasFundo => {
  switch (tipo) {
    case "contraluz":
      return {
        longe: (
          <AbsoluteFill>
            <Ceu />
            <AbsoluteFill style={{ background: "radial-gradient(ellipse 55% 40% at 50% 46%, rgba(255,238,190,0.95), rgba(255,210,130,0.35) 45%, rgba(0,0,0,0) 75%)" }} />
          </AbsoluteFill>
        ),
        meio: <Arquibancada />,
        chao: (
          <AbsoluteFill>
            <Gramado />
            <AbsoluteFill style={{ background: "radial-gradient(ellipse 60% 30% at 50% 60%, rgba(255,230,170,0.35), rgba(0,0,0,0) 70%)" }} />
          </AbsoluteFill>
        ),
      };
    case "chuva":
      return {
        longe: (
          <AbsoluteFill style={{ filter: "saturate(0.25) brightness(0.7)" }}>
            <Ceu estrelas={false} />
          </AbsoluteFill>
        ),
        meio: (
          <AbsoluteFill style={{ filter: "saturate(0.15) brightness(0.65)" }}>
            <Arquibancada cores={["#4A5470", "#3C4560", "#56607E"]} />
          </AbsoluteFill>
        ),
        chao: (
          <AbsoluteFill style={{ filter: "saturate(0.35) brightness(0.75)" }}>
            <Gramado />
          </AbsoluteFill>
        ),
      };
    case "tribunal":
      return {
        longe: (
          <AbsoluteFill>
            <Madeira cor1="#5A3220" cor2="#4E2B1B" ripas={7} />
            <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
              <defs>
                <radialGradient id="brasao" cx="50%" cy="40%" r="60%">
                  <stop offset="0" stopColor="#F2D27A" />
                  <stop offset="1" stopColor="#B58A2E" />
                </radialGradient>
              </defs>
              <circle cx={540} cy={330} r={150} fill="url(#brasao)" stroke={COR.contorno} strokeWidth={8} />
              <path d="M470 330 L540 260 L610 330 L540 400 Z" fill="#8A6420" opacity={0.6} />
              <rect x={0} y={1420} width={1080} height={500} fill="#3A2014" />
            </svg>
            <AbsoluteFill style={{ background: "radial-gradient(ellipse 60% 40% at 50% 10%, rgba(255,214,140,0.45), rgba(0,0,0,0) 70%)" }} />
          </AbsoluteFill>
        ),
        chao: (
          <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
            <rect x={40} y={1380} width={1000} height={300} rx={18} fill="#6B3B22" stroke={COR.contorno} strokeWidth={9} />
            <rect x={40} y={1380} width={1000} height={40} rx={10} fill="#8A4E2E" />
          </svg>
        ),
      };
    case "mesa":
      return {
        longe: (
          <AbsoluteFill>
            <Madeira cor1="#8A5A34" cor2="#7C4F2D" ripas={9} vertical={false} />
            <AbsoluteFill style={{ background: "radial-gradient(ellipse 60% 45% at 50% 40%, rgba(255,226,170,0.5), rgba(0,0,0,0) 75%)" }} />
            <Vinheta forca={0.75} />
          </AbsoluteFill>
        ),
      };
    case "escritorio":
      return {
        longe: (
          <AbsoluteFill style={{ background: "linear-gradient(180deg,#3B4A6B,#2B3550)" }}>
            <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
              <rect x={90} y={220} width={420} height={560} rx={14} fill="#0F1A3A" stroke={COR.contorno} strokeWidth={10} />
              {Array.from({ length: 40 }).map((_, i) => (
                <rect key={i} x={110 + rnd(i) * 380} y={420 + rnd(i + 3) * 340} width={14} height={20} fill="#FFD98A" opacity={0.5 + rnd(i + 9) * 0.5} />
              ))}
              <line x1={300} y1={220} x2={300} y2={780} stroke={COR.contorno} strokeWidth={8} />
              {[0, 1, 2].map((r) => (
                <g key={r}>
                  <rect x={600} y={300 + r * 200} width={400} height={20} fill="#6B4A2E" />
                  {Array.from({ length: 8 }).map((_, i) => (
                    <rect key={i} x={612 + i * 46} y={200 + r * 200} width={36} height={100} fill={["#8A2A2A", "#2A4A8A", "#2A7A4A", "#B8902E"][(i + r) % 4]} stroke={COR.contorno} strokeWidth={3} />
                  ))}
                </g>
              ))}
            </svg>
            <Vinheta />
          </AbsoluteFill>
        ),
        chao: (
          <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
            <rect x={0} y={1400} width={1080} height={520} fill="#22283C" />
          </svg>
        ),
      };
    case "escuro":
      return {
        longe: (
          <AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 60% at 50% 35%, #213A78, #0B1433 75%)" }}>
            <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0, opacity: 0.18 }}>
              {Array.from({ length: 24 }).map((_, i) => (
                <line key={i} x1={0} y1={i * 80} x2={1080} y2={i * 80} stroke="#8FB0FF" strokeWidth={2} />
              ))}
              {Array.from({ length: 14 }).map((_, i) => (
                <line key={i} x1={i * 80} y1={0} x2={i * 80} y2={1920} stroke="#8FB0FF" strokeWidth={2} />
              ))}
            </svg>
          </AbsoluteFill>
        ),
      };
    case "estadio":
    default:
      return {
        longe: (
          <AbsoluteFill>
            <Ceu />
            <Refletores />
          </AbsoluteFill>
        ),
        meio: <Arquibancada />,
        chao: <Gramado />,
      };
  }
};

/** Torcida de flashes de câmera (cintilando). */
export const useFlashes = (n: number) => useMemo(() => Array.from({ length: n }).map((_, i) => ({ x: rnd(i + 1) * 1080, y: 520 + rnd(i + 50) * 260, ph: rnd(i + 7) * 30 })), [n]);
