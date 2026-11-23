import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import estados from "../data/brasil-estados.json";
import { MiniTorcedor } from "./Personagem";

const OUT = "#2A1A12";
export const ROUND = "'Baloo 2', Nunito, Arial, sans-serif";

/* ---------------------------- PASSADO (sépia) ---------------------------- */

/** Sala vintage: papel de parede listrado, rodapé de madeira, piso, lustre e vinheta. */
export const SalaVintage: React.FC<{ children?: React.ReactNode; lustre?: boolean; quadro?: React.ReactNode }> = ({ children, lustre = true, quadro }) => {
  const frame = useCurrentFrame();
  const glow = 0.85 + Math.sin(frame / 7) * 0.08;
  return (
    <AbsoluteFill style={{ background: "#C9A97A" }}>
      <AbsoluteFill style={{ background: "repeating-linear-gradient(90deg, #D8BC8E 0 46px, #C7A576 46px 92px)" }} />
      <AbsoluteFill style={{ background: "repeating-linear-gradient(90deg, transparent 0 44px, rgba(120,70,30,0.18) 44px 48px)" }} />
      {/* lambri de madeira */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 1180, height: 260, background: "repeating-linear-gradient(90deg, #7A4A26 0 120px, #6B3E1E 120px 124px)", borderTop: "14px solid #5A3216" }} />
      {/* piso */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 1440, bottom: 0, background: "repeating-linear-gradient(180deg, #8A5A30 0 40px, #7A4C26 40px 44px)" }} />
      {quadro ? <div style={{ position: "absolute", left: 640, top: 360 }}>{quadro}</div> : null}
      {lustre ? (
        <div style={{ position: "absolute", left: 540 - 300, top: -80, width: 600, height: 600 }}>
          <div style={{ position: "absolute", inset: 0, borderRadius: "50%", background: `radial-gradient(circle, rgba(255,220,150,${0.55 * glow}) 0%, rgba(255,220,150,0) 65%)` }} />
          <svg width="600" height="420" viewBox="0 0 600 420" style={{ position: "absolute", top: 0 }}>
            <line x1="300" y1="0" x2="300" y2="150" stroke={OUT} strokeWidth="6" />
            <path d="M190 170 Q300 260 410 170" stroke="#9C7A2C" strokeWidth="10" fill="none" />
            <ellipse cx="300" cy="170" rx="120" ry="22" fill="#B8933A" stroke={OUT} strokeWidth="4" />
            {[200, 250, 300, 350, 400].map((x, i) => (
              <g key={x}>
                <rect x={x - 7} y={128} width="14" height="36" fill="#F4E9D0" stroke={OUT} strokeWidth="3" />
                <ellipse cx={x} cy={118} rx="8" ry="14" fill={`rgba(255,${210 + (i % 2) * 20},120,${glow})`} />
              </g>
            ))}
          </svg>
        </div>
      ) : null}
      {children}
    </AbsoluteFill>
  );
};

/** Filtro sépia + vinheta escura nas bordas (passado). */
export const Sepia: React.FC<{ children: React.ReactNode; forca?: number }> = ({ children, forca = 0.55 }) => (
  <AbsoluteFill>
    <AbsoluteFill style={{ filter: `sepia(${forca}) contrast(1.05) saturate(0.85)` }}>{children}</AbsoluteFill>
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(40,20,5,0.62) 100%)", pointerEvents: "none" }} />
  </AbsoluteFill>
);

/** TV de tubo de madeira com conteúdo na tela. */
export const TVTubo: React.FC<{ largura?: number; children?: React.ReactNode }> = ({ largura = 640, children }) => {
  const frame = useCurrentFrame();
  const h = largura * 0.78;
  return (
    <div style={{ position: "relative", width: largura, height: h + 90 }}>
      <div style={{ position: "absolute", inset: `0 0 90px 0`, background: "linear-gradient(180deg,#8A5A30,#5E3818)", borderRadius: 36, border: `6px solid ${OUT}`, boxShadow: "12px 14px 0 rgba(0,0,0,0.35)" }} />
      <div style={{ position: "absolute", left: largura * 0.07, top: h * 0.09, width: largura * 0.68, height: h * 0.8, borderRadius: "18% / 22%", background: "#1A2A22", border: `6px solid ${OUT}`, overflow: "hidden", boxShadow: "inset 0 0 40px rgba(0,0,0,0.8)" }}>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>{children}</div>
        <div style={{ position: "absolute", inset: 0, background: `repeating-linear-gradient(0deg, rgba(0,0,0,0.12) 0 2px, transparent 2px 5px)`, translate: `0 ${(frame % 10) * 0.5}px` }} />
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 35% 25%, rgba(255,255,255,0.22), rgba(255,255,255,0) 50%)" }} />
      </div>
      {[0.32, 0.55].map((y) => (
        <div key={y} style={{ position: "absolute", left: largura * 0.81, top: h * y, width: largura * 0.11, height: largura * 0.11, borderRadius: "50%", background: "#3A2414", border: `5px solid ${OUT}` }} />
      ))}
      <div style={{ position: "absolute", left: largura * 0.15, bottom: 0, width: 16, height: 96, background: OUT, rotate: "12deg" }} />
      <div style={{ position: "absolute", right: largura * 0.15, bottom: 0, width: 16, height: 96, background: OUT, rotate: "-12deg" }} />
      <svg width="200" height="120" viewBox="0 0 200 120" style={{ position: "absolute", left: largura / 2 - 100, top: -110 }}>
        <path d="M100 110 L30 10 M100 110 L170 14" stroke={OUT} strokeWidth="6" strokeLinecap="round" />
        <circle cx="30" cy="10" r="8" fill={OUT} />
        <circle cx="170" cy="14" r="8" fill={OUT} />
      </svg>
    </div>
  );
};

/** Jornal impresso com manchete. */
export const Jornal: React.FC<{ manchete: string; sub?: string; ano?: string; largura?: number }> = ({ manchete, sub, ano = "1989", largura = 760 }) => (
  <div style={{ width: largura, background: "#EFE4CC", border: `5px solid ${OUT}`, padding: 28, boxShadow: "14px 16px 0 rgba(0,0,0,0.35)", fontFamily: "Georgia, serif", color: "#2A1A12" }}>
    <div style={{ display: "flex", justifyContent: "space-between", borderBottom: `4px double ${OUT}`, paddingBottom: 8, fontSize: 26 }}>
      <span>Edição esportiva</span>
      <span>{ano}</span>
    </div>
    <div style={{ fontFamily: "Georgia, serif", fontWeight: 900, fontSize: 64, textAlign: "center", letterSpacing: 2, margin: "10px 0", borderBottom: `3px solid ${OUT}` }}>O ESPORTIVO</div>
    <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 92, lineHeight: 0.95, textAlign: "center", margin: "14px 0" }}>{manchete}</div>
    {sub ? <div style={{ fontSize: 30, textAlign: "center", fontStyle: "italic" }}>{sub}</div> : null}
    <div style={{ display: "flex", gap: 16, marginTop: 16 }}>
      {[0, 1, 2].map((i) => (
        <div key={i} style={{ flex: 1, height: 120, background: `repeating-linear-gradient(180deg, rgba(42,26,18,0.55) 0 4px, transparent 4px 14px)` }} />
      ))}
    </div>
  </div>
);

/** Placa de madeira (com texto e/ou escudos). */
export const PlacaMadeira: React.FC<{ children: React.ReactNode; largura?: number; style?: React.CSSProperties }> = ({ children, largura = 520, style }) => (
  <div style={{ width: largura, padding: "22px 30px", background: "linear-gradient(180deg,#A7713F,#7C4E26)", border: `6px solid ${OUT}`, borderRadius: 18, boxShadow: "10px 12px 0 rgba(0,0,0,0.35)", textAlign: "center", fontFamily: ROUND, fontWeight: 800, color: "#FFF4DD", textShadow: `3px 3px 0 ${OUT}`, ...style }}>
    {children}
  </div>
);

/** Mesa de escritório. */
export const Mesa: React.FC<{ largura?: number; children?: React.ReactNode }> = ({ largura = 860, children }) => (
  <div style={{ position: "relative", width: largura, height: 300 }}>
    <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 60, background: "linear-gradient(180deg,#9A6234,#7A4A22)", border: `6px solid ${OUT}`, borderRadius: 10 }} />
    <div style={{ position: "absolute", left: 30, right: 30, top: 54, bottom: 0, background: "linear-gradient(180deg,#6B3E1E,#4E2C14)", border: `6px solid ${OUT}` }} />
    {children}
  </div>
);

/** Carimbo grande. */
export const Carimbo: React.FC<{ texto: string; cor?: string; size?: number; rot?: number; k?: number }> = ({ texto, cor = "#B3261E", size = 150, rot = -10, k = 1 }) => (
  <div style={{ display: "inline-block", border: `${size * 0.07}px solid ${cor}`, borderRadius: size * 0.12, padding: `${size * 0.04}px ${size * 0.2}px`, color: cor, fontFamily: ROUND, fontWeight: 800, fontSize: size, lineHeight: 1.05, rotate: `${rot}deg`, scale: `${interpolate(k, [0, 1], [2.6, 1])}`, opacity: k > 0 ? 0.92 : 0 }}>
    {texto}
  </div>
);

/* --------------------------------- MAPA --------------------------------- */

type Estado = { sigla: string; nome: string; d: string; cx: number; cy: number };
const E = estados as Estado[];
export const centroEstado = (sigla: string) => {
  const e = E.find((x) => x.sigla === sigla);
  return e ? { x: e.cx, y: e.cy } : { x: 500, y: 500 };
};

/** Mapa do Brasil (estilo antigo em pergaminho ou moderno). */
export const MapaBrasil: React.FC<{
  largura?: number;
  antigo?: boolean;
  destaque?: string[];
  corDestaque?: string;
  piscar?: boolean;
  children?: React.ReactNode;
}> = ({ largura = 900, antigo = true, destaque = [], corDestaque = "#C0392B", piscar = false, children }) => {
  const frame = useCurrentFrame();
  const blink = piscar ? 0.55 + 0.45 * Math.abs(Math.sin(frame / 6)) : 1;
  const fill = antigo ? "#E7D3A6" : "#7BC67B";
  const stroke = antigo ? "#6B4A26" : "#1F5E2E";
  return (
    <div style={{ position: "relative", width: largura, height: largura }}>
      {antigo ? (
        <div style={{ position: "absolute", inset: -40, background: "radial-gradient(ellipse at 50% 50%, #F2E3BF 55%, #CDAE78 100%)", border: `6px solid ${OUT}`, borderRadius: 18, boxShadow: "14px 16px 0 rgba(0,0,0,0.35)" }} />
      ) : null}
      <svg width={largura} height={largura} viewBox="0 0 1000 1000" style={{ position: "absolute", inset: 0 }}>
        {E.map((e) => {
          const on = destaque.includes(e.sigla);
          return <path key={e.sigla} d={e.d} fill={on ? corDestaque : fill} fillOpacity={on ? blink : 1} stroke={stroke} strokeWidth={antigo ? 2.2 : 2.6} strokeLinejoin="round" />;
        })}
        {antigo ? (
          <g opacity="0.55">
            <circle cx="900" cy="860" r="60" fill="none" stroke="#6B4A26" strokeWidth="3" />
            <path d="M900 790 L912 860 L900 930 L888 860 Z" fill="#6B4A26" />
            <text x="900" y="782" fontSize="30" textAnchor="middle" fill="#6B4A26" fontFamily="Georgia">N</text>
          </g>
        ) : null}
      </svg>
      <div style={{ position: "absolute", inset: 0 }}>{children}</div>
    </div>
  );
};

/** Bandeirinha espetada no mapa (cor ou escudo). Coordenadas no espaço 0..1000 do mapa. */
export const Bandeirinha: React.FC<{ x: number; y: number; largura: number; cor?: string; escudo?: string; k?: number }> = ({ x, y, largura, cor = "#C0392B", escudo, k = 1 }) => {
  const s = largura / 1000;
  const h = escudo ? 92 : 58;
  return (
    <div style={{ position: "absolute", left: x * s, top: y * s, scale: `${k}`, transformOrigin: "0 100%", translate: `0 ${-h - 30}px` }}>
      <div style={{ width: 5, height: h + 30, background: OUT, position: "absolute", left: 0, top: 0 }} />
      {escudo ? (
        <div style={{ position: "absolute", left: 5, top: 0, width: 84, height: 84, background: "#FFF8E8", border: `4px solid ${OUT}`, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Img src={staticFile(escudo)} style={{ width: 66, height: 66, objectFit: "contain" }} />
        </div>
      ) : (
        <svg width="56" height="40" viewBox="0 0 56 40" style={{ position: "absolute", left: 5, top: 0 }}>
          <path d="M0 0 L56 14 L0 30 Z" fill={cor} stroke={OUT} strokeWidth="3" />
        </svg>
      )}
    </div>
  );
};

/** Vareta de madeira apontando para um ponto (ponta em x,y). */
export const Vareta: React.FC<{ x: number; y: number; largura: number; ang?: number }> = ({ x, y, largura, ang = -35 }) => {
  const s = largura / 1000;
  return (
    <div style={{ position: "absolute", left: x * s, top: y * s, width: 700, height: 18, transformOrigin: "0 50%", rotate: `${ang + 180}deg`, translate: "0 -9px" }}>
      <div style={{ width: "100%", height: "100%", background: "linear-gradient(180deg,#B57D44,#7A4A22)", border: `4px solid ${OUT}`, borderRadius: 9 }} />
      <div style={{ position: "absolute", left: -6, top: -2, width: 26, height: 22, background: "#F4E9D0", border: `4px solid ${OUT}`, borderRadius: 6 }} />
    </div>
  );
};

/* -------------------------------- PRESENTE -------------------------------- */

/** Céu azul + gramado listrado. */
export const Gramado: React.FC<{ horizonte?: number; children?: React.ReactNode }> = ({ horizonte = 900, children }) => (
  <AbsoluteFill style={{ background: "linear-gradient(180deg,#4FA9F0 0%,#9AD4FF 100%)" }}>
    <div style={{ position: "absolute", left: 0, right: 0, top: horizonte, bottom: 0, background: "repeating-linear-gradient(180deg,#3FA548 0 90px,#36953F 90px 180px)" }} />
    <div style={{ position: "absolute", left: 0, right: 0, top: horizonte, height: 8, background: "rgba(255,255,255,0.85)" }} />
    {children}
  </AbsoluteFill>
);

/** Nuvens cartoon que passam devagar. */
export const Nuvens: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {[
        [120, 160, 1],
        [640, 260, 0.7],
        [900, 120, 0.85],
      ].map(([x, y, s], i) => (
        <div key={i} style={{ position: "absolute", left: ((x + frame * (0.4 + i * 0.15)) % 1300) - 200, top: y, scale: `${s}` }}>
          <svg width="260" height="110" viewBox="0 0 260 110">
            <path d="M30 90 Q0 90 10 64 Q20 40 50 48 Q60 10 110 18 Q150 0 170 34 Q220 24 230 60 Q260 66 248 90 Z" fill="#FFFFFF" stroke="#2A1A12" strokeWidth="4" />
          </svg>
        </div>
      ))}
    </>
  );
};

/** Arquibancada 2D com dezenas de mini-torcedores. */
export const Arquibancada: React.FC<{ cores: string[]; linhas?: number; tam?: number; top?: number; faixa?: React.ReactNode }> = ({ cores, linhas = 5, tam = 62, top = 0, faixa }) => {
  const peles = ["#F2C29B", "#D9A27A", "#A86F4C", "#7A4B30", "#F6D0B0"];
  const porLinha = Math.ceil(1080 / (tam * 0.82)) + 1;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top, height: linhas * tam * 1.05 + 40 }}>
      <div style={{ position: "absolute", inset: 0, background: "repeating-linear-gradient(180deg,#8E99A8 0 8px,#B9C2CE 8px 66px)" }} />
      {Array.from({ length: linhas }).map((_, r) => (
        <div key={r} style={{ position: "absolute", top: r * tam * 1.02, left: (r % 2) * (tam * 0.4) - tam * 0.4, display: "flex", gap: tam * -0.18 }}>
          {Array.from({ length: porLinha }).map((__, c) => (
            <MiniTorcedor key={c} tam={tam} cor={cores[(r * 3 + c) % cores.length]} pele={peles[(r * 7 + c * 3) % peles.length]} fase={r * 0.9 + c * 0.6} />
          ))}
        </div>
      ))}
      {faixa ? <div style={{ position: "absolute", left: 0, right: 0, bottom: -20, display: "flex", justifyContent: "center" }}>{faixa}</div> : null}
    </div>
  );
};

/** Faixa da torcida com escudo e texto. */
export const Faixa: React.FC<{ texto: string; escudo?: string; cor?: string; corTexto?: string; largura?: number }> = ({ texto, escudo, cor = "#FFFFFF", corTexto = "#111", largura = 820 }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ width: largura, display: "flex", alignItems: "center", justifyContent: "center", gap: 18, background: cor, border: `6px solid ${OUT}`, padding: "10px 24px", rotate: `${Math.sin(frame / 9) * 1.5}deg`, boxShadow: "8px 10px 0 rgba(0,0,0,0.3)" }}>
      {escudo ? <Img src={staticFile(escudo)} style={{ width: 96, height: 96, objectFit: "contain" }} /> : null}
      <div style={{ fontFamily: ROUND, fontWeight: 800, fontSize: 62, color: corTexto, lineHeight: 1 }}>{texto}</div>
    </div>
  );
};

/** Troféu da Copa do Brasil (desenho próprio, estilizado). */
export const Trofeu: React.FC<{ altura?: number; brilho?: number }> = ({ altura = 500, brilho = 1 }) => {
  const frame = useCurrentFrame();
  const sh = 30 + ((frame * 3) % 160);
  return (
    <svg width={altura * 0.62} height={altura} viewBox="0 0 310 500" style={{ overflow: "visible", filter: `drop-shadow(0 0 ${30 * brilho}px rgba(255,214,90,0.8))` }}>
      <defs>
        <linearGradient id="ouro" x1="0" x2="1">
          <stop offset="0" stopColor="#8A6418" />
          <stop offset="0.35" stopColor="#FFE38A" />
          <stop offset="0.55" stopColor="#E0B13C" />
          <stop offset="1" stopColor="#7A5612" />
        </linearGradient>
        <linearGradient id="brilhoT" x1="0" x2="1">
          <stop offset="0" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.5" stopColor="#fff" stopOpacity="0.7" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d="M70 60 Q20 60 22 120 Q26 190 100 210" stroke="url(#ouro)" strokeWidth="18" fill="none" />
      <path d="M240 60 Q290 60 288 120 Q284 190 210 210" stroke="url(#ouro)" strokeWidth="18" fill="none" />
      <path d="M60 40 L250 40 Q250 210 155 250 Q60 210 60 40 Z" fill="url(#ouro)" stroke={OUT} strokeWidth="5" />
      <ellipse cx="155" cy="40" rx="95" ry="18" fill="#FFE9A8" stroke={OUT} strokeWidth="5" />
      <path d="M140 250 L170 250 L180 330 L130 330 Z" fill="url(#ouro)" stroke={OUT} strokeWidth="5" />
      <circle cx="155" cy="125" r="42" fill="#0B6E3A" stroke={OUT} strokeWidth="4" />
      <path d="M155 92 L163 116 L188 116 L168 131 L176 156 L155 141 L134 156 L142 131 L122 116 L147 116 Z" fill="#FEDD00" />
      <rect x="90" y="330" width="130" height="40" rx="6" fill="#3A2414" stroke={OUT} strokeWidth="5" />
      <rect x="70" y="370" width="170" height="70" rx="8" fill="#2A1A10" stroke={OUT} strokeWidth="5" />
      <rect x="96" y="388" width="118" height="30" rx="4" fill="url(#ouro)" />
      <rect x={sh} y="40" width="30" height="210" fill="url(#brilhoT)" opacity="0.6" style={{ mixBlendMode: "screen" }} />
    </svg>
  );
};

/** Zebra de pelúcia (desenho próprio). */
export const Zebra: React.FC<{ tam?: number }> = ({ tam = 260 }) => (
  <svg width={tam} height={tam} viewBox="0 0 200 200">
    <ellipse cx="100" cy="128" rx="64" ry="46" fill="#fff" stroke={OUT} strokeWidth="5" />
    {[70, 92, 114, 136].map((x) => (
      <path key={x} d={`M${x} 86 Q${x + 8} 128 ${x} 170`} stroke={OUT} strokeWidth="9" fill="none" />
    ))}
    <circle cx="146" cy="78" r="34" fill="#fff" stroke={OUT} strokeWidth="5" />
    <path d="M128 52 Q134 64 128 80 M150 46 Q156 60 150 76" stroke={OUT} strokeWidth="7" />
    <ellipse cx="166" cy="92" rx="14" ry="10" fill="#555" stroke={OUT} strokeWidth="4" />
    <circle cx="148" cy="74" r="5" fill={OUT} />
    <path d="M132 48 L126 26 L140 40 Z M154 44 L156 22 L166 40 Z" fill="#fff" stroke={OUT} strokeWidth="4" />
    {[60, 84, 116, 140].map((x) => (
      <rect key={x} x={x} y={160} width="14" height="32" rx="6" fill="#fff" stroke={OUT} strokeWidth="4" />
    ))}
  </svg>
);

/** Selo de clube sem escudo baixável (nome + cores), deixado explícito na documentação. */
export const SeloClube: React.FC<{ nome: string; cor1: string; cor2: string; tam?: number }> = ({ nome, cor1, cor2, tam = 120 }) => (
  <div style={{ width: tam, height: tam, borderRadius: "50%", background: `linear-gradient(90deg, ${cor1} 50%, ${cor2} 50%)`, border: `5px solid ${OUT}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
    <div style={{ background: "#fff", border: `3px solid ${OUT}`, borderRadius: 8, padding: "2px 6px", fontFamily: ROUND, fontWeight: 800, fontSize: tam * 0.16, color: OUT, textAlign: "center", lineHeight: 1 }}>{nome}</div>
  </div>
);

/** Escudo numa placa/moldura (para placares). */
export const Escudo: React.FC<{ src?: string; selo?: { nome: string; cor1: string; cor2: string }; tam?: number }> = ({ src, selo, tam = 150 }) => (
  <div style={{ width: tam, height: tam, background: "#FFF8E8", border: `5px solid ${OUT}`, borderRadius: 18, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "6px 8px 0 rgba(0,0,0,0.3)" }}>
    {src ? <Img src={staticFile(src)} style={{ width: tam * 0.8, height: tam * 0.8, objectFit: "contain" }} /> : selo ? <SeloClube {...selo} tam={tam * 0.84} /> : null}
  </div>
);
