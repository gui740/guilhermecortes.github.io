import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FAIXA, FONT, MONO, SOMBRA } from "../theme";

export const ease = Easing.bezier(0.22, 1, 0.36, 1);

export const useEntra = (delay = 0, dur = 14) => {
  const f = useCurrentFrame();
  return interpolate(f - delay, [0, dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
};

export const useMola = (delay = 0, damping = 18) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: f - delay, fps, config: { damping, mass: 0.8 } });
};

/** O N oficial: sempre limpo, na cor original, sem efeitos. Nada pode encostar (respiro = largura de uma perna). */
export const NLogo: React.FC<{ altura: number; style?: React.CSSProperties }> = ({ altura, style }) => (
  <Img src={staticFile("media/stills/n_symbol.png")} style={{ height: altura, width: "auto", display: "block", ...style }} />
);

export const Faixa: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ position: "absolute", left: FAIXA.x, width: FAIXA.w, top: 0, bottom: 0, display: "flex", flexDirection: "column",
    justifyContent: "center", alignItems: "center", textAlign: "center", padding: "0 22px", boxSizing: "border-box", ...style }}>{children}</div>
);

export const Mono: React.FC<{ children: React.ReactNode; size?: number; cor?: string; style?: React.CSSProperties }> = ({ children, size = 22, cor = C.secundario, style }) => (
  <div style={{ fontFamily: MONO, fontSize: size, letterSpacing: 2, color: cor, textTransform: "uppercase", ...style }}>{children}</div>
);

/** Texto cinético: palavras entram em camadas, de baixo para cima. */
export const Kinetic: React.FC<{ texto: string; size: number; cor?: string; peso?: number; delay?: number; passo?: number; style?: React.CSSProperties }> =
  ({ texto, size, cor = C.tinta, peso = 800, delay = 0, passo = 3, style }) => {
    const f = useCurrentFrame();
    const palavras = texto.split(" ");
    return (
      <div style={{ fontFamily: FONT, fontWeight: peso, fontSize: size, lineHeight: 1.02, color: cor, letterSpacing: -0.5,
        textTransform: "uppercase", display: "flex", flexWrap: "wrap", justifyContent: "center", gap: `0 ${size * 0.26}px`, ...style }}>
        {palavras.map((p, i) => {
          const k = interpolate(f - delay - i * passo, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
          return <span key={i} style={{ display: "inline-block", opacity: k, transform: `translateY(${(1 - k) * size * 0.45}px)` }}>{p}</span>;
        })}
      </div>
    );
  };

export const Carimbo: React.FC<{ texto: string; delay?: number; style?: React.CSSProperties }> = ({ texto, delay = 16, style }) => {
  const k = useMola(delay, 12);
  return (
    <div style={{ fontFamily: MONO, fontSize: 17, letterSpacing: 2, color: C.tinta, border: `2px solid ${C.tinta}`, padding: "6px 12px",
      textTransform: "uppercase", background: C.branco, transform: `scale(${interpolate(k, [0, 1], [1.6, 1])}) rotate(-1.5deg)`,
      opacity: Math.min(1, k * 2), maxWidth: FAIXA.w - 30, lineHeight: 1.35, ...style }}>{texto}</div>
  );
};

/** Lower third acadêmico: discreto, dentro da faixa central. */
export const Academico: React.FC<{ texto: string }> = ({ texto }) => {
  const k = useEntra(0, 12);
  return (
    <div style={{ position: "absolute", left: FAIXA.x + 8, width: FAIXA.w - 16, bottom: 58, opacity: k, transform: `translateY(${(1 - k) * 12}px)` }}>
      <div style={{ height: 2, width: `${k * 100}%`, background: C.tinta, marginBottom: 8 }} />
      <div style={{ fontFamily: MONO, fontSize: 15, lineHeight: 1.35, color: C.tinta, textAlign: "left" }}>{texto}</div>
    </div>
  );
};

/** Camada de CRT: scanlines, barra de rolagem e cintilação (o P&B, grão e curvatura já vêm do ffmpeg). */
export const CRTOverlay: React.FC = () => {
  const f = useCurrentFrame();
  const barra = ((f * 9) % 1500) - 200;
  const flick = 0.03 * Math.sin(f * 1.7) + 0.02 * Math.sin(f * 0.37);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.20) 0px, rgba(0,0,0,0.20) 1px, transparent 1px, transparent 3px)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: barra, height: 140,
        background: "linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0) 100%)" }} />
      <AbsoluteFill style={{ background: "black", opacity: Math.max(0, flick) }} />
    </AbsoluteFill>
  );
};

/** Lower third retrofuturista (terminal âmbar) para falas de arquivo. */
export const LowerThird: React.FC<{ nome: string; cargo: string; fonte: string; delay?: number }> = ({ nome, cargo, fonte, delay = 8 }) => {
  const f = useCurrentFrame();
  const k = useEntra(delay, 12);
  const linha = `${nome} · ${cargo}`;
  const chars = Math.floor(interpolate(f - delay, [0, 26], [0, linha.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const cursor = Math.floor(f / 8) % 2 === 0;
  return (
    <div style={{ position: "absolute", left: FAIXA.x + 14, width: FAIXA.w - 28, top: 640, opacity: k }}>
      <div style={{ background: "rgba(20,20,20,0.88)", borderLeft: `4px solid ${C.ambar}`, padding: "10px 14px", textAlign: "left" }}>
        <div style={{ fontFamily: MONO, fontSize: 19, color: C.ambar, letterSpacing: 1.5, fontWeight: 600 }}>
          {linha.slice(0, chars)}<span style={{ opacity: cursor ? 1 : 0 }}>▌</span>
        </div>
        <div style={{ fontFamily: MONO, fontSize: 15, color: "#E8E8E8", letterSpacing: 1.5, marginTop: 4 }}>{fonte}</div>
      </div>
    </div>
  );
};

/** Legenda PT-BR das falas em inglês: blocos sequenciais, proporcionais ao tamanho do texto. */
export const Legenda: React.FC<{ linhas: string[]; dur: number; inicio?: number }> = ({ linhas, dur, inicio = 0 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps - inicio;
  const pesos = linhas.map((l) => Math.max(8, l.length));
  const tot = pesos.reduce((a, b) => a + b, 0);
  let acc = 0, idx = -1;
  for (let i = 0; i < linhas.length; i++) {
    const a = (acc / tot) * dur; acc += pesos[i];
    const b = (acc / tot) * dur;
    if (t >= a && t < b) idx = i;
  }
  if (t >= dur) idx = linhas.length - 1;
  if (idx < 0) return null;
  return (
    <div style={{ position: "absolute", left: FAIXA.x + 10, width: FAIXA.w - 20, top: 790, display: "flex", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 34, lineHeight: 1.18, color: "white", textAlign: "center",
        textShadow: "0 0 3px #000, 0 2px 10px rgba(0,0,0,0.9)", padding: "0 10px" }}>{linhas[idx]}</div>
    </div>
  );
};

/** Medidor analógico de argumento (semicírculo, ponteiro, escala). */
export const Medidor: React.FC<{ rotulo: string; marcas: string[]; de: number; ate: number; delay?: number; size?: number }> =
  ({ rotulo, marcas, de, ate, delay = 6, size = 540 }) => {
    const f = useCurrentFrame();
    const { fps } = useVideoConfig();
    const s = spring({ frame: f - delay, fps, config: { damping: 9, mass: 1.4, stiffness: 60 } });
    const tremor = s > 0.97 ? Math.sin(f * 2.3) * 0.006 : 0;
    const v = de + (ate - de) * s + tremor;
    const ang = -180 + 180 * v;
    const r = size / 2 - 30;
    const cx = size / 2, cy = size / 2;
    const ticks = Array.from({ length: 21 }, (_, i) => i / 20);
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <svg width={size} height={size / 2 + 40} viewBox={`0 0 ${size} ${size / 2 + 40}`}>
          <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`} fill="none" stroke={C.tinta} strokeWidth={3} />
          <path d={`M ${cx - r + 26} ${cy} A ${r - 26} ${r - 26} 0 0 1 ${cx + r - 26} ${cy}`} fill="none" stroke={C.ambar} strokeWidth={8} opacity={0.85}
            strokeDasharray={`${Math.PI * (r - 26) * v} 4000`} />
          {ticks.map((tk, i) => {
            const a = Math.PI * (1 - tk);
            const l = i % 5 === 0 ? 22 : 11;
            return <line key={i} x1={cx + Math.cos(a) * r} y1={cy - Math.sin(a) * r} x2={cx + Math.cos(a) * (r - l)} y2={cy - Math.sin(a) * (r - l)} stroke={C.tinta} strokeWidth={i % 5 === 0 ? 3 : 1.5} />;
          })}
          {marcas.map((m, i) => {
            if (!m) return null;
            const a = Math.PI * (1 - i / (marcas.length - 1));
            const x = cx + Math.cos(a) * (r + 2), y = cy - Math.sin(a) * (r + 2) - 12;
            const anchor = i === 0 ? "start" : i === marcas.length - 1 ? "end" : "middle";
            return <text key={i} x={x} y={y} textAnchor={anchor} fontFamily={MONO} fontSize={15} fill={C.tinta} letterSpacing={1}>{m}</text>;
          })}
          <g transform={`rotate(${ang} ${cx} ${cy})`}>
            <line x1={cx} y1={cy} x2={cx + r - 34} y2={cy} stroke={C.tinta} strokeWidth={5} strokeLinecap="round" />
          </g>
          <circle cx={cx} cy={cy} r={14} fill={C.tinta} />
          <circle cx={cx} cy={cy} r={5} fill={C.ambar} />
        </svg>
        <Mono size={22} cor={C.tinta} style={{ marginTop: 6, fontWeight: 600 }}>{rotulo}</Mono>
      </div>
    );
  };

export const Sombra: React.CSSProperties = { boxShadow: SOMBRA };

/** Pictogramas retrô originais, em linha. */
export const Picto: React.FC<{ nome: string; size?: number; cor?: string }> = ({ nome, size = 90, cor = C.tinta }) => {
  const sw = 4;
  const p = { fill: "none", stroke: cor, strokeWidth: sw, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  const d: Record<string, React.ReactNode> = {
    "CONTROLE REMOTO": <><rect x="34" y="8" width="32" height="84" rx="8" {...p} /><circle cx="50" cy="26" r="6" {...p} /><line x1="42" y1="48" x2="58" y2="48" {...p} /><line x1="42" y1="60" x2="58" y2="60" {...p} /><line x1="42" y1="72" x2="58" y2="72" {...p} /></>,
    VIDEOCASSETE: <><rect x="8" y="26" width="84" height="50" rx="4" {...p} /><circle cx="32" cy="51" r="11" {...p} /><circle cx="68" cy="51" r="11" {...p} /><line x1="43" y1="51" x2="57" y2="51" {...p} /></>,
    DVD: <><circle cx="50" cy="50" r="40" {...p} /><circle cx="50" cy="50" r="10" {...p} /><path d="M 50 18 A 32 32 0 0 1 80 40" {...p} /></>,
    STREAMING: <><rect x="8" y="16" width="84" height="54" rx="4" {...p} /><line x1="36" y1="86" x2="64" y2="86" {...p} /><line x1="50" y1="70" x2="50" y2="86" {...p} /><path d="M 43 32 L 62 43 L 43 54 Z" {...p} /></>,
    MARATONA: <><rect x="10" y="20" width="56" height="38" rx="3" {...p} /><rect x="22" y="32" width="56" height="38" rx="3" {...p} /><rect x="34" y="44" width="56" height="38" rx="3" {...p} /></>,
    ATOMO: <><ellipse cx="50" cy="50" rx="40" ry="14" {...p} /><ellipse cx="50" cy="50" rx="40" ry="14" transform="rotate(60 50 50)" {...p} /><ellipse cx="50" cy="50" rx="40" ry="14" transform="rotate(120 50 50)" {...p} /><circle cx="50" cy="50" r="5" fill={cor} /></>,
    PESSOA: <><circle cx="50" cy="26" r="14" {...p} /><path d="M 22 90 L 22 68 Q 22 48 50 48 Q 78 48 78 68 L 78 90" {...p} /></>,
  };
  return <svg width={size} height={size} viewBox="0 0 100 100">{d[nome] ?? d.ATOMO}</svg>;
};
