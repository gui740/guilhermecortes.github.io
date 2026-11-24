import React from "react";
import { AbsoluteFill } from "remotion";
import { COR } from "../estilo/tokens";

/** Objetos que os personagens seguram (coordenadas do viewBox 500x900 do Chibi) e o look de arquivo 1951. */
const O = COR.contorno;

/** Taça antiga dourada (estilizada, sem réplica de troféu real). Use dentro do Chibi (pose "comemorando") ou solta. */
export const TacaAntigaG: React.FC<{ x?: number; y?: number; s?: number; brilho?: number }> = ({ x = 250, y = 120, s = 1, brilho = 0 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <defs>
      <linearGradient id="ouroT" x1="0" x2="1">
        <stop offset="0" stopColor="#8A6418" />
        <stop offset="0.35" stopColor="#FFE38A" />
        <stop offset="0.6" stopColor="#E0B13C" />
        <stop offset="1" stopColor="#7A5612" />
      </linearGradient>
      <radialGradient id="glowT" cx="50%" cy="50%" r="50%">
        <stop offset="0" stopColor="#FFF3B0" stopOpacity="0.9" />
        <stop offset="1" stopColor="#FFF3B0" stopOpacity="0" />
      </radialGradient>
    </defs>
    {brilho > 0 && <circle cx={0} cy={-40} r={210} fill="url(#glowT)" opacity={brilho} />}
    <path d="M-92 -150 Q-150 -150 -146 -90 Q-140 -30 -70 -14" stroke={O} strokeWidth={24} fill="none" />
    <path d="M92 -150 Q150 -150 146 -90 Q140 -30 70 -14" stroke={O} strokeWidth={24} fill="none" />
    <path d="M-92 -150 Q-150 -150 -146 -90 Q-140 -30 -70 -14" stroke="url(#ouroT)" strokeWidth={12} fill="none" />
    <path d="M92 -150 Q150 -150 146 -90 Q140 -30 70 -14" stroke="url(#ouroT)" strokeWidth={12} fill="none" />
    <path d="M-100 -170 L100 -170 Q100 -20 0 20 Q-100 -20 -100 -170 Z" fill="url(#ouroT)" stroke={O} strokeWidth={8} />
    <ellipse cx={0} cy={-170} rx={100} ry={18} fill="#FFE9A8" stroke={O} strokeWidth={7} />
    <path d="M-14 20 L14 20 L22 90 L-22 90 Z" fill="url(#ouroT)" stroke={O} strokeWidth={7} />
    <rect x={-60} y={90} width={120} height={50} rx={8} fill="#3A2414" stroke={O} strokeWidth={7} />
    <rect x={-40} y={102} width={80} height={24} rx={4} fill="url(#ouroT)" />
    <path d="M0 -118 L9 -96 L32 -96 L14 -82 L21 -60 L0 -73 L-21 -60 L-14 -82 L-32 -96 L-9 -96 Z" fill="#E1251B" stroke={O} strokeWidth={4} />
    <path d="M-60 -150 Q-50 -80 -24 -30" stroke="#FFF7D6" strokeWidth={10} fill="none" strokeLinecap="round" opacity={0.7} />
  </g>
);

export const MicrofoneAntigo: React.FC = () => (
  <g transform="translate(250 560)">
    <rect x={-8} y={0} width={16} height={130} fill="#8A8F98" stroke={O} strokeWidth={5} />
    <rect x={-44} y={-110} width={88} height={120} rx={36} fill="#C9CED6" stroke={O} strokeWidth={8} />
    {[-80, -60, -40, -20].map((y) => (
      <line key={y} x1={-34} y1={y} x2={34} y2={y} stroke="#7A808A" strokeWidth={5} />
    ))}
    <rect x={-60} y={126} width={120} height={20} rx={8} fill="#5A4A3A" stroke={O} strokeWidth={5} />
  </g>
);

export const Pasta: React.FC = () => (
  <g transform="translate(150 500) rotate(-8)">
    <rect x={0} y={0} width={190} height={150} rx={10} fill="#2E4A7A" stroke={O} strokeWidth={8} />
    <rect x={14} y={-14} width={160} height={30} rx={6} fill="#F4F1E8" stroke={O} strokeWidth={5} />
    <rect x={70} y={60} width={50} height={30} rx={4} fill="#C9D3E6" stroke={O} strokeWidth={4} />
  </g>
);

export const Convite: React.FC = () => (
  <g transform="translate(330 380) rotate(14)">
    <rect x={0} y={0} width={150} height={104} rx={8} fill="#FBF3DC" stroke={O} strokeWidth={7} />
    <path d="M0 0 L75 56 L150 0" stroke={O} strokeWidth={5} fill="none" />
    <circle cx={75} cy={58} r={14} fill="#B3121A" stroke={O} strokeWidth={4} />
  </g>
);

export const Ata: React.FC = () => (
  <g transform="translate(160 470) rotate(-5)">
    <rect x={0} y={0} width={180} height={230} rx={6} fill="#FBF8EE" stroke={O} strokeWidth={7} />
    <rect x={20} y={18} width={140} height={22} fill="#0B6B3A" />
    {[64, 90, 116, 142].map((y) => (
      <line key={y} x1={20} y1={y} x2={160} y2={y} stroke="#9AA0AE" strokeWidth={7} />
    ))}
    <path d="M30 196 Q60 170 80 196 T130 190" stroke="#1C3A8A" strokeWidth={5} fill="none" />
  </g>
);

/** Look de arquivo 1951: sépia/oliva desbotado, papel de jornal, granulação, flicker e vinheta forte. */
export const Look1951: React.FC<{ children: React.ReactNode; frame?: number; borda?: boolean }> = ({ children, frame = 0, borda = false }) => {
  const flicker = 1 + Math.sin(frame * 1.7) * 0.025 + ((frame * 7919) % 13 === 0 ? -0.06 : 0);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ filter: `sepia(0.75) saturate(0.55) hue-rotate(18deg) contrast(1.08) brightness(${0.95 * flicker})` }}>{children}</AbsoluteFill>
      <AbsoluteFill style={{ background: "rgba(120,110,60,0.16)", mixBlendMode: "multiply" }} />
      <AbsoluteFill
        style={{
          backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' seed='${frame % 8}'/><feColorMatrix values='0 0 0 0 0.25  0 0 0 0 0.2  0 0 0 0 0.12  0 0 0 0.9 0'/></filter><rect width='400' height='400' filter='url(%23n)'/></svg>")`,
          opacity: 0.35,
          mixBlendMode: "multiply",
        }}
      />
      {/* riscos de película */}
      {[0, 1].map((i) => {
        const x = ((frame * (37 + i * 53)) % 1080) + i * 211;
        return (frame + i * 5) % 9 < 3 ? <div key={i} style={{ position: "absolute", left: x % 1080, top: 0, width: 2, height: 1920, background: "rgba(40,30,15,0.35)" }} /> : null;
      })}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 75% 62% at 50% 46%, rgba(0,0,0,0) 45%, rgba(30,20,8,0.75) 100%)" }} />
      {borda && <AbsoluteFill style={{ boxShadow: "inset 0 0 0 36px #EFE6CF, inset 0 0 0 42px rgba(60,40,20,0.6)" }} />}
    </AbsoluteFill>
  );
};
