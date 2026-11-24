import React, { useMemo } from "react";
import { AbsoluteFill } from "remotion";
import { COR } from "../estilo/tokens";

/** Estádio à noite em camadas (para parallax): céu, arquibancada, gramado, luz da frente. 1080x1920. */

const rnd = (s: number) => {
  const x = Math.sin(s * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};

export const Ceu: React.FC<{ estrelas?: boolean }> = ({ estrelas = true }) => {
  const pts = useMemo(() => Array.from({ length: 70 }).map((_, i) => ({ x: rnd(i) * 1080, y: rnd(i + 99) * 700, r: 1 + rnd(i + 7) * 2.4, o: 0.3 + rnd(i + 3) * 0.7 })), []);
  return (
    <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
      <defs>
        <linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={COR.ceuTopo} />
          <stop offset="0.35" stopColor={COR.ceuMeio} />
          <stop offset="0.6" stopColor={COR.ceuBase} />
          <stop offset="1" stopColor="#2A4E92" />
        </linearGradient>
      </defs>
      <rect width={1080} height={1920} fill="url(#ceu)" />
      {estrelas && pts.map((p, i) => <circle key={i} cx={p.x} cy={p.y} r={p.r} fill="#fff" opacity={p.o} />)}
    </svg>
  );
};

/** Torre de refletor com halo (bloom). */
export const Refletor: React.FC<{ x: number; y: number; s?: number; lado?: -1 | 1 }> = ({ x, y, s = 1, lado = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <defs>
      <radialGradient id={`halo${lado}`} cx="50%" cy="50%" r="50%">
        <stop offset="0" stopColor="#FFF6DA" stopOpacity="0.95" />
        <stop offset="0.25" stopColor={COR.luzQuente} stopOpacity="0.55" />
        <stop offset="1" stopColor={COR.luzQuente} stopOpacity="0" />
      </radialGradient>
    </defs>
    <path d="M-10 60 L-30 900 L30 900 L10 60 Z" fill="#141A33" />
    <rect x={-120} y={-70} width={240} height={140} rx={16} fill="#1B2140" stroke={COR.contorno} strokeWidth={6} />
    {Array.from({ length: 12 }).map((_, i) => (
      <circle key={i} cx={-84 + (i % 4) * 56} cy={-36 + Math.floor(i / 4) * 36} r={17} fill="#FFFBEA" />
    ))}
    <circle cx={0} cy={0} r={420} fill={`url(#halo${lado})`} style={{ mixBlendMode: "screen" }} />
  </g>
);

export const Arquibancada: React.FC<{ topo?: number; cores?: string[] }> = ({ topo = 760, cores = ["#E1251B", "#FFFFFF", "#1E7A46", "#FFD400", "#2A6BD8", "#F2F2F2"] }) => {
  const dots = useMemo(
    () =>
      Array.from({ length: 900 }).map((_, i) => {
        const fila = Math.floor(i / 75);
        return { x: (i % 75) * 14.6 + (fila % 2) * 7 + rnd(i) * 4, y: topo - 230 + fila * 26 + rnd(i + 5) * 6, c: cores[Math.floor(rnd(i + 11) * cores.length)], r: 6 + rnd(i + 2) * 3 };
      }),
    [topo, cores],
  );
  return (
    <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
      <defs>
        <linearGradient id="arq" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0F1838" />
          <stop offset="1" stopColor="#1C2A55" />
        </linearGradient>
        <filter id="bok" x="-10%" y="-10%" width="120%" height="120%">
          <feGaussianBlur stdDeviation="2.2" />
        </filter>
        <linearGradient id="neblina" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#5E7FC4" stopOpacity="0" />
          <stop offset="1" stopColor="#7E9BD8" stopOpacity="0.35" />
        </linearGradient>
      </defs>
      <path d={`M0 ${topo - 260} Q540 ${topo - 330} 1080 ${topo - 260} L1080 ${topo + 70} L0 ${topo + 70} Z`} fill="url(#arq)" />
      <g filter="url(#bok)">
        {dots.map((d, i) => (
          <circle key={i} cx={d.x} cy={d.y} r={d.r} fill={d.c} opacity={0.82} />
        ))}
      </g>
      <rect x={0} y={topo - 280} width={1080} height={350} fill="url(#neblina)" />
      {/* placas de LED */}
      <rect x={0} y={topo + 40} width={1080} height={44} fill="#0B1022" />
      <rect x={0} y={topo + 46} width={1080} height={32} fill="#173A7A" />
      {Array.from({ length: 6 }).map((_, i) => (
        <rect key={i} x={20 + i * 180} y={topo + 52} width={150} height={20} rx={6} fill={i % 2 ? COR.amarelo : "#E9EEF8"} opacity={0.75} />
      ))}
    </svg>
  );
};

export const Gramado: React.FC<{ topo?: number }> = ({ topo = 844 }) => (
  <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
    <defs>
      <linearGradient id="grama" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#2A8C47" />
        <stop offset="1" stopColor="#1F6E37" />
      </linearGradient>
      <radialGradient id="luzGrama" cx="50%" cy="20%" r="70%">
        <stop offset="0" stopColor="#FFF1C4" stopOpacity="0.35" />
        <stop offset="1" stopColor="#FFF1C4" stopOpacity="0" />
      </radialGradient>
    </defs>
    <rect x={0} y={topo} width={1080} height={1920 - topo} fill="url(#grama)" />
    {Array.from({ length: 9 }).map((_, i) => {
      const y0 = topo + Math.pow(i / 9, 1.6) * (1920 - topo);
      const y1 = topo + Math.pow((i + 0.5) / 9, 1.6) * (1920 - topo);
      return <rect key={i} x={0} y={y0} width={1080} height={y1 - y0} fill={COR.grama2} opacity={0.35} />;
    })}
    <ellipse cx={540} cy={topo + 420} rx={460} ry={150} fill="none" stroke="rgba(255,255,255,0.75)" strokeWidth={9} />
    <line x1={0} y1={topo + 420} x2={1080} y2={topo + 420} stroke="rgba(255,255,255,0.75)" strokeWidth={9} />
    <rect x={0} y={topo} width={1080} height={1920 - topo} fill="url(#luzGrama)" />
  </svg>
);

/** Luz de primeiro plano: vinheta, vazamento quente dos refletores. */
export const LuzFrente: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill style={{ background: "radial-gradient(ellipse 60% 30% at 8% 6%, rgba(255,226,168,0.45), rgba(255,226,168,0) 70%), radial-gradient(ellipse 60% 30% at 92% 6%, rgba(255,226,168,0.45), rgba(255,226,168,0) 70%)", mixBlendMode: "screen" }} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse 85% 70% at 50% 45%, rgba(0,0,0,0) 55%, rgba(5,8,25,0.6) 100%)" }} />
  </AbsoluteFill>
);

/** Estádio completo (sem parallax), para estáticos. */
export const EstadioNoite: React.FC<{ cores?: string[] }> = ({ cores }) => (
  <AbsoluteFill>
    <Ceu />
    <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: "absolute", inset: 0 }}>
      <Refletor x={110} y={170} s={0.85} lado={-1} />
      <Refletor x={970} y={170} s={0.85} lado={1} />
    </svg>
    <Arquibancada cores={cores} />
    <Gramado />
    <LuzFrente />
  </AbsoluteFill>
);
