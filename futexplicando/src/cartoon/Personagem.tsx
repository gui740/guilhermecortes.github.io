import React, { useId } from "react";
import { useCurrentFrame } from "remotion";

export type Expressao = "sorriso" | "espanto" | "dentes" | "triste" | "desconfiado";

export type PersonagemProps = {
  /** altura total em px */
  altura?: number;
  expressao?: Expressao;
  terno?: string;
  gravata?: string;
  pele?: string;
  oculos?: boolean;
  bigode?: boolean;
  chapeu?: boolean;
  cabelo?: "careca" | "lados" | "topete";
  corCabelo?: string;
  /** cachecol com cor de time */
  cachecol?: string;
  /** espelhar horizontalmente */
  espelhar?: boolean;
  /** fase do balanço (para vários personagens não balançarem iguais) */
  fase?: number;
  /** braço levantado (comemorando / batendo na mesa) */
  bracoErguido?: boolean;
  /** pulo de alegria (px de amplitude) */
  pulo?: number;
  style?: React.CSSProperties;
};

const OUTLINE = "#2A1A12";

/**
 * Personagem cartoon: cabeça redonda enorme, corpinho de terno, pernas de palito.
 * Emoção pela troca de expressão; movimento só no balanço leve de cabeça e braço.
 */
export const Personagem: React.FC<PersonagemProps> = ({
  altura = 520,
  expressao = "sorriso",
  terno = "#3B4A6B",
  gravata = "#B23A2E",
  pele = "#F2C29B",
  oculos = false,
  bigode = false,
  chapeu = false,
  cabelo = "careca",
  corCabelo = "#3A2618",
  cachecol,
  espelhar = false,
  fase = 0,
  bracoErguido = false,
  pulo = 0,
  style,
}) => {
  const frame = useCurrentFrame();
  const id = useId().replace(/:/g, "");
  const t = frame / 30 + fase;
  const bob = Math.sin(t * 3.2) * 2.5; // graus
  const arm = Math.sin(t * 2.6) * 7;
  const jump = pulo ? Math.abs(Math.sin(t * 6)) * pulo : 0;
  const s = altura / 520;

  const eyes = () => {
    switch (expressao) {
      case "espanto":
        return (
          <>
            <circle cx="108" cy="150" r="11" fill={OUTLINE} />
            <circle cx="192" cy="150" r="11" fill={OUTLINE} />
            <path d="M86 112 Q108 96 128 108" stroke={OUTLINE} strokeWidth="6" fill="none" strokeLinecap="round" />
            <path d="M172 108 Q192 96 214 112" stroke={OUTLINE} strokeWidth="6" fill="none" strokeLinecap="round" />
          </>
        );
      case "triste":
        return (
          <>
            <path d="M94 154 Q108 164 122 154" stroke={OUTLINE} strokeWidth="6" fill="none" strokeLinecap="round" />
            <path d="M178 154 Q192 164 206 154" stroke={OUTLINE} strokeWidth="6" fill="none" strokeLinecap="round" />
            <path d="M90 128 L124 120" stroke={OUTLINE} strokeWidth="6" strokeLinecap="round" />
            <path d="M176 120 L210 128" stroke={OUTLINE} strokeWidth="6" strokeLinecap="round" />
          </>
        );
      case "desconfiado":
        return (
          <>
            <path d="M96 152 L122 152" stroke={OUTLINE} strokeWidth="8" strokeLinecap="round" />
            <circle cx="192" cy="152" r="8" fill={OUTLINE} />
            <path d="M88 136 L126 140" stroke={OUTLINE} strokeWidth="6" strokeLinecap="round" />
            <path d="M174 124 Q194 110 214 122" stroke={OUTLINE} strokeWidth="6" fill="none" strokeLinecap="round" />
          </>
        );
      case "dentes":
        return (
          <>
            <circle cx="108" cy="152" r="8" fill={OUTLINE} />
            <circle cx="192" cy="152" r="8" fill={OUTLINE} />
            <path d="M88 122 L126 136" stroke={OUTLINE} strokeWidth="7" strokeLinecap="round" />
            <path d="M174 136 L212 122" stroke={OUTLINE} strokeWidth="7" strokeLinecap="round" />
          </>
        );
      default:
        return (
          <>
            <circle cx="108" cy="150" r="8" fill={OUTLINE} />
            <circle cx="192" cy="150" r="8" fill={OUTLINE} />
            <path d="M90 126 Q108 116 126 124" stroke={OUTLINE} strokeWidth="5" fill="none" strokeLinecap="round" />
            <path d="M174 124 Q192 116 210 126" stroke={OUTLINE} strokeWidth="5" fill="none" strokeLinecap="round" />
          </>
        );
    }
  };

  const mouth = () => {
    const y = bigode ? 212 : 204;
    switch (expressao) {
      case "espanto":
        return <ellipse cx="150" cy={y + 6} rx="17" ry="22" fill="#5A1E14" stroke={OUTLINE} strokeWidth="4" />;
      case "dentes":
        return (
          <g>
            <rect x="112" y={y - 8} width="76" height="30" rx="10" fill="#FFFDF6" stroke={OUTLINE} strokeWidth="4" />
            <line x1="112" y1={y + 7} x2="188" y2={y + 7} stroke={OUTLINE} strokeWidth="3" />
            {[127, 142, 158, 173].map((x) => (
              <line key={x} x1={x} y1={y - 8} x2={x} y2={y + 22} stroke={OUTLINE} strokeWidth="2.5" />
            ))}
          </g>
        );
      case "triste":
        return <path d={`M124 ${y + 14} Q150 ${y - 4} 176 ${y + 14}`} stroke={OUTLINE} strokeWidth="6" fill="none" strokeLinecap="round" />;
      case "desconfiado":
        return <path d={`M128 ${y + 6} L172 ${y}`} stroke={OUTLINE} strokeWidth="6" strokeLinecap="round" />;
      default:
        return <path d={`M118 ${y - 4} Q150 ${y + 26} 182 ${y - 4}`} stroke={OUTLINE} strokeWidth="6" fill="#7A2A1C" strokeLinecap="round" />;
    }
  };

  return (
    <div style={{ width: 300 * s, height: altura, scale: espelhar ? "-1 1" : undefined, translate: `0 ${-jump}px`, ...style }}>
      <svg width={300 * s} height={altura} viewBox="0 0 300 520" style={{ overflow: "visible" }}>
        <defs>
          <radialGradient id={`pele${id}`} cx="0.42" cy="0.28" r="0.8">
            <stop offset="0" stopColor="#FFE8CF" />
            <stop offset="0.35" stopColor={pele} />
            <stop offset="1" stopColor="#B9785A" />
          </radialGradient>
          <linearGradient id={`terno${id}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={terno} />
            <stop offset="1" stopColor="#1C2233" />
          </linearGradient>
        </defs>
        {/* sombra no chão */}
        <ellipse cx="150" cy="512" rx="78" ry="9" fill="rgba(0,0,0,0.25)" />
        {/* pernas de palito */}
        <path d="M134 400 L128 496" stroke={OUTLINE} strokeWidth="7" strokeLinecap="round" />
        <path d="M166 400 L172 496" stroke={OUTLINE} strokeWidth="7" strokeLinecap="round" />
        <path d="M112 500 Q122 488 134 496 L134 504 L110 504 Z" fill={OUTLINE} />
        <path d="M188 500 Q178 488 166 496 L166 504 L190 504 Z" fill={OUTLINE} />
        {/* braços */}
        <g style={{ transformOrigin: "106px 300px", rotate: `${bracoErguido ? -130 + arm * 0.6 : 18 + arm}deg` }}>
          <path d="M106 300 L74 372" stroke={OUTLINE} strokeWidth="7" strokeLinecap="round" />
          <circle cx="72" cy="377" r="9" fill={pele} stroke={OUTLINE} strokeWidth="3" />
        </g>
        <g style={{ transformOrigin: "194px 300px", rotate: `${-18 - arm}deg` }}>
          <path d="M194 300 L226 372" stroke={OUTLINE} strokeWidth="7" strokeLinecap="round" />
          <circle cx="228" cy="377" r="9" fill={pele} stroke={OUTLINE} strokeWidth="3" />
        </g>
        {/* corpo de terno */}
        <path d="M104 282 Q150 268 196 282 L190 406 L110 406 Z" fill={`url(#terno${id})`} stroke={OUTLINE} strokeWidth="3.5" strokeLinejoin="round" />
        <path d="M134 280 L150 316 L166 280 Z" fill="#F7F2E8" stroke={OUTLINE} strokeWidth="2.5" />
        <path d="M150 292 L143 304 L150 352 L157 304 Z" fill={gravata} stroke={OUTLINE} strokeWidth="2" />
        <path d="M134 280 L150 330 L128 300 Z" fill="rgba(0,0,0,0.18)" />
        <path d="M166 280 L150 330 L172 300 Z" fill="rgba(0,0,0,0.18)" />
        {cachecol ? (
          <g>
            <path d="M112 276 Q150 300 188 276 L188 292 Q150 316 112 292 Z" fill={cachecol} stroke={OUTLINE} strokeWidth="3" />
            <rect x="170" y="292" width="16" height="48" fill={cachecol} stroke={OUTLINE} strokeWidth="3" />
          </g>
        ) : null}
        {/* cabeça (balança levemente) */}
        <g style={{ transformOrigin: "150px 270px", rotate: `${bob}deg` }}>
          <circle cx="150" cy="150" r="128" fill={`url(#pele${id})`} stroke={OUTLINE} strokeWidth="4" />
          {/* orelhas */}
          <circle cx="24" cy="160" r="16" fill={pele} stroke={OUTLINE} strokeWidth="3.5" />
          <circle cx="276" cy="160" r="16" fill={pele} stroke={OUTLINE} strokeWidth="3.5" />
          {/* cabelo */}
          {cabelo === "lados" ? (
            <>
              <path d="M30 120 Q34 80 60 64 Q50 100 52 140 Z" fill={corCabelo} stroke={OUTLINE} strokeWidth="3" />
              <path d="M270 120 Q266 80 240 64 Q250 100 248 140 Z" fill={corCabelo} stroke={OUTLINE} strokeWidth="3" />
            </>
          ) : null}
          {cabelo === "topete" ? <path d="M70 70 Q120 0 210 40 Q240 60 236 80 Q190 40 120 66 Q90 74 70 70 Z" fill={corCabelo} stroke={OUTLINE} strokeWidth="3" /> : null}
          {/* brilho quente no topo */}
          <ellipse cx="118" cy="58" rx="54" ry="22" fill="rgba(255,248,230,0.55)" />
          {eyes()}
          {oculos ? (
            <g fill="none" stroke={OUTLINE} strokeWidth="5">
              <circle cx="108" cy="151" r="26" />
              <circle cx="192" cy="151" r="26" />
              <path d="M134 150 Q150 142 166 150" />
              <path d="M82 148 L28 140" />
              <path d="M218 148 L272 140" />
            </g>
          ) : null}
          {/* nariz */}
          <path d="M150 168 Q160 184 146 190" stroke={OUTLINE} strokeWidth="4" fill="none" strokeLinecap="round" />
          {bigode ? <path d="M108 200 Q130 184 150 196 Q170 184 192 200 Q172 206 150 202 Q128 206 108 200 Z" fill="#3A2618" stroke={OUTLINE} strokeWidth="2.5" /> : null}
          {mouth()}
          {/* bochechas */}
          <circle cx="82" cy="196" r="14" fill="rgba(230,110,90,0.25)" />
          <circle cx="218" cy="196" r="14" fill="rgba(230,110,90,0.25)" />
          {chapeu ? (
            <g>
              <ellipse cx="150" cy="44" rx="122" ry="20" fill="#1E1A18" stroke={OUTLINE} strokeWidth="3" />
              <path d="M78 44 Q76 -40 150 -42 Q224 -40 222 44 Z" fill="#26201D" stroke={OUTLINE} strokeWidth="3" />
              <path d="M80 30 Q150 40 220 30 L221 40 Q150 50 79 40 Z" fill="#7A1F1A" />
            </g>
          ) : null}
        </g>
      </svg>
    </div>
  );
};

/** Mini torcedor para a torcida (cabeça redonda + corpinho com a cor do time). */
export const MiniTorcedor: React.FC<{ cor: string; pele?: string; tam?: number; fase?: number; bracos?: boolean }> = ({ cor, pele = "#F2C29B", tam = 60, fase = 0, bracos = true }) => {
  const frame = useCurrentFrame();
  const up = bracos ? Math.max(0, Math.sin(frame / 5 + fase)) : 0;
  return (
    <svg width={tam} height={tam * 1.4} viewBox="0 0 60 84" style={{ translate: `0 ${-up * tam * 0.12}px` }}>
      <path d="M14 50 Q30 42 46 50 L44 84 L16 84 Z" fill={cor} stroke={OUTLINE} strokeWidth="2" />
      {bracos ? (
        <>
          <path d={`M16 54 L${6 - up * 2} ${40 - up * 18}`} stroke={OUTLINE} strokeWidth="3" strokeLinecap="round" />
          <path d={`M44 54 L${54 + up * 2} ${40 - up * 18}`} stroke={OUTLINE} strokeWidth="3" strokeLinecap="round" />
        </>
      ) : null}
      <circle cx="30" cy="26" r="21" fill={pele} stroke={OUTLINE} strokeWidth="2" />
      <ellipse cx="25" cy="14" rx="9" ry="4" fill="rgba(255,248,230,0.55)" />
      <circle cx="23" cy="27" r="2.4" fill={OUTLINE} />
      <circle cx="37" cy="27" r="2.4" fill={OUTLINE} />
      <path d={up > 0.5 ? "M24 34 Q30 40 36 34" : "M25 35 L35 35"} stroke={OUTLINE} strokeWidth="2" fill="none" strokeLinecap="round" />
    </svg>
  );
};
