import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile } from "remotion";
import { COR, FONTE } from "../estilo/tokens";

/** Objetos, textos e efeitos ilustrados. Todos recebem `u` = segundos desde que entram (negativo = ainda não). */

export const O = COR.contorno;
const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
/** Mola amortecida 0→1 com overshoot (damping ~12). */
export const mola = (u: number, f = 2.4, z = 0.42) => {
  if (u <= 0) return 0;
  const w = 2 * Math.PI * f;
  return 1 - Math.exp(-z * w * u) * Math.cos(w * Math.sqrt(1 - z * z) * u);
};
/** Escala de "batida" (2,6 → 1 em 0,16 s + quique). */
export const batida = (u: number) => {
  if (u < 0) return 0;
  if (u < 0.16) return 2.6 - 1.6 * Math.pow(u / 0.16, 2);
  const v = u - 0.16;
  return 1 + 0.07 * Math.exp(-v * 12) * Math.cos(v * 40);
};
const texto = (cor: string, tam: number, extra: React.CSSProperties = {}): React.CSSProperties => ({
  fontFamily: FONTE.titulo,
  fontSize: tam,
  color: cor,
  WebkitTextStroke: `${Math.round(tam / 11)}px #000`,
  paintOrder: "stroke fill",
  textShadow: `0 ${Math.round(tam / 14)}px 0 rgba(0,0,0,0.55)`,
  lineHeight: 1.02,
  ...extra,
});

export const Titulo: React.FC<{ linhas: string[]; y: number; u: number }> = ({ linhas, y, u }) => {
  if (u < 0) return null;
  return (
    <div style={{ position: "absolute", top: y, width: 1080, textAlign: "center", transform: `skewX(-8deg) scale(${batida(u)})`, transformOrigin: "50% 40%", opacity: clamp(u / 0.05) }}>
      {linhas.map((l, i) => (
        <div key={i} style={texto(i === 0 ? "#FFFFFF" : COR.amarelo, l.length > 10 ? 162 : 186)}>
          {l}
        </div>
      ))}
    </div>
  );
};

export const Carimbo: React.FC<{ texto: string; sub?: string; cor: string; x: number; y: number; rot?: number; u: number }> = ({ texto: tx, sub, cor, x, y, rot = -6, u }) => {
  if (u < 0) return null;
  const claro = cor === "#FFD400" || cor === "#9FB4D8";
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${batida(u)})`, opacity: clamp(u / 0.05) }}>
      <div style={{ border: `12px solid ${cor}`, borderRadius: 22, padding: "8px 34px 4px", background: "rgba(255,255,255,0.93)", boxShadow: "10px 14px 0 rgba(0,0,0,0.45)", textAlign: "center" }}>
        <div style={{ fontFamily: FONTE.titulo, fontSize: tx.length > 13 ? 84 : 108, color: claro ? "#111" : cor, lineHeight: 1.05, whiteSpace: "nowrap" }}>{tx}</div>
        {sub && <div style={{ fontFamily: FONTE.titulo, fontSize: 44, color: "#111", marginTop: -4 }}>{sub}</div>}
      </div>
    </div>
  );
};

export const Banner: React.FC<{ texto: string; cor: string; u: number }> = ({ texto: tx, cor, u }) => {
  if (u < 0) return null;
  const p = mola(u, 2, 0.6);
  return (
    <div style={{ position: "absolute", top: 230, left: 0, width: 1080, display: "flex", justifyContent: "center", transform: `translateX(${(1 - p) * -1100}px) rotate(-3deg)` }}>
      <div style={{ background: cor, padding: "14px 60px", border: "8px solid #000", boxShadow: "12px 14px 0 rgba(0,0,0,0.5)" }}>
        <div style={texto("#FFFFFF", 110)}>{tx}</div>
      </div>
    </div>
  );
};

export const Pulsa: React.FC<{ texto: string; x: number; y: number; u: number }> = ({ texto: tx, x, y, u }) => {
  if (u < 0) return null;
  const k = batida(u) * (1 + 0.06 * Math.sin(u * 9));
  return <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) scale(${k})`, ...texto(COR.amarelo, 120), whiteSpace: "nowrap" }}>{tx.replace(" 👇", "")}</div>;
};

export const Logo: React.FC<{ x: number; y: number; u: number }> = ({ x, y, u }) => {
  if (u < 0) return null;
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) scale(${mola(u)})` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, background: "#fff", borderRadius: 999, border: "7px solid #138A44", padding: "12px 40px 12px 14px", boxShadow: "8px 10px 0 rgba(0,0,0,0.4)" }}>
        <svg width={86} height={86} viewBox="0 0 100 100">
          <circle cx={50} cy={50} r={44} fill="#fff" stroke="#111" strokeWidth={6} />
          <path d="M50 30 L66 42 L60 62 L40 62 L34 42 Z" fill="#111" />
        </svg>
        <div style={{ fontFamily: FONTE.redondo, fontWeight: 800, fontSize: 64, color: "#138A44" }}>@futexplicando</div>
      </div>
    </div>
  );
};

export const Relogio: React.FC<{ x: number; y: number; tam: number; minuto: number; u: number }> = ({ x, y, tam, minuto, u }) => {
  if (u < 0) return null;
  const giro = interpolate(u, [0, 0.9], [minuto + 120, minuto], { extrapolateRight: "clamp", easing: (v) => 1 - Math.pow(1 - v, 3) });
  const a = (giro / 60) * Math.PI * 2;
  return (
    <div style={{ position: "absolute", left: x - tam / 2, top: y - tam / 2, transform: `scale(${mola(u)})` }}>
      <svg width={tam} height={tam} viewBox="0 0 380 380">
        <defs>
          <radialGradient id="mostr" cx="45%" cy="40%" r="65%">
            <stop offset="0" stopColor="#FFFFFF" />
            <stop offset="1" stopColor="#DCE4F4" />
          </radialGradient>
        </defs>
        <circle cx={190} cy={196} r={176} fill="rgba(0,0,0,0.35)" />
        <circle cx={190} cy={190} r={176} fill="#E1251B" stroke={O} strokeWidth={10} />
        <circle cx={190} cy={190} r={146} fill="url(#mostr)" stroke={O} strokeWidth={7} />
        {Array.from({ length: 12 }).map((_, i) => {
          const b = (i / 12) * Math.PI * 2;
          return <line key={i} x1={190 + Math.sin(b) * 120} y1={190 - Math.cos(b) * 120} x2={190 + Math.sin(b) * 136} y2={190 - Math.cos(b) * 136} stroke={O} strokeWidth={i % 3 ? 5 : 10} strokeLinecap="round" />;
        })}
        <text x={190} y={150} textAnchor="middle" fontFamily={FONTE.titulo} fontSize={64} fill="#E1251B">{`${minuto}'`}</text>
        <line x1={190} y1={190} x2={190 + Math.sin(a) * 100} y2={190 - Math.cos(a) * 100} stroke={O} strokeWidth={12} strokeLinecap="round" />
        <circle cx={190} cy={190} r={14} fill={O} />
      </svg>
    </div>
  );
};

export const RelogioParede: React.FC<{ x: number; y: number; u: number }> = ({ x, y, u }) => {
  if (u < 0) return null;
  const a = u * 3;
  return (
    <svg width={220} height={220} viewBox="0 0 220 220" style={{ position: "absolute", left: x - 110, top: y - 110 }}>
      <circle cx={110} cy={110} r={96} fill="#F4F1E8" stroke={O} strokeWidth={10} />
      <line x1={110} y1={110} x2={110 + Math.sin(a) * 70} y2={110 - Math.cos(a) * 70} stroke={O} strokeWidth={7} strokeLinecap="round" />
      <line x1={110} y1={110} x2={110 + Math.sin(a / 12) * 45} y2={110 - Math.cos(a / 12) * 45} stroke={O} strokeWidth={10} strokeLinecap="round" />
      <circle cx={110} cy={110} r={9} fill="#E1251B" />
    </svg>
  );
};

export const Placar: React.FC<{ a: string; b: string; siglaA: string; siglaB: string; ga: number; gb: number; rotulo?: string; x: number; y: number; escala?: number; u: number }> = ({ a, b, siglaA, siglaB, ga, gb, rotulo, x, y, escala = 1, u }) => {
  if (u < 0) return null;
  const p = mola(u, 2.2, 0.38);
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) translateY(${(1 - p) * -900}px) scale(${escala})` }}>
      <div style={{ width: 900, borderRadius: 34, background: "linear-gradient(180deg,#1A2240,#0B1022)", border: "8px solid #000", boxShadow: `0 0 0 6px ${COR.amarelo}, 16px 20px 0 rgba(0,0,0,0.45)`, padding: "26px 30px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        {[
          [a, siglaA],
          [b, siglaB],
        ].map(([esc, sig], i) => (
          <div key={i} style={{ order: i === 0 ? 0 : 2, display: "flex", flexDirection: "column", alignItems: "center", width: 230 }}>
            <Img src={staticFile(`escudos/${esc}.png`)} style={{ height: 170, objectFit: "contain", filter: "drop-shadow(0 6px 8px rgba(0,0,0,0.6))" }} />
            <div style={{ fontFamily: FONTE.titulo, fontSize: 58, color: "#fff", marginTop: 6 }}>{sig}</div>
          </div>
        ))}
        <div style={{ order: 1, fontFamily: FONTE.titulo, fontSize: 210, color: "#fff", lineHeight: 1 }}>
          {ga}
          <span style={{ color: COR.amarelo, fontSize: 130, margin: "0 18px" }}>×</span>
          {gb}
        </div>
      </div>
      {rotulo && (
        <div style={{ display: "flex", justifyContent: "center", marginTop: -6 }}>
          <div style={{ background: COR.amarelo, border: "6px solid #000", padding: "6px 30px", fontFamily: FONTE.titulo, fontSize: 52, color: "#111" }}>{rotulo}</div>
        </div>
      )}
    </div>
  );
};

export const Jornal: React.FC<{ manchete: string; linha: string; x: number; y: number; u: number }> = ({ manchete, linha, x, y, u }) => {
  if (u < 0) return null;
  const p = mola(u, 1.8, 0.5);
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) rotate(${-4 + (1 - p) * 30}deg) scale(${0.4 + p * 0.6})` }}>
      <div style={{ width: 860, background: "#EFE6CF", border: "6px solid #2B1A10", boxShadow: "20px 24px 0 rgba(0,0,0,0.4)", padding: 34, fontFamily: "Georgia, serif", color: "#22180F" }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 26, borderBottom: "4px double #2B1A10", paddingBottom: 8 }}>
          <span>EDIÇÃO DE SÁBADO</span>
          <span>07/12/2013</span>
        </div>
        <div style={{ fontWeight: 900, fontSize: 60, textAlign: "center", letterSpacing: 2, margin: "8px 0", borderBottom: "3px solid #2B1A10" }}>DIÁRIO DA BOLA</div>
        <div style={{ fontFamily: FONTE.titulo, fontSize: 190, textAlign: "center", color: "#B3121A", lineHeight: 1 }}>{manchete}</div>
        <div style={{ fontSize: 36, textAlign: "center", fontStyle: "italic", margin: "8px 0 14px" }}>{linha}</div>
        <div style={{ display: "flex", gap: 18 }}>
          <div style={{ width: 300, height: 200, background: "linear-gradient(135deg,#9C8F7A,#6B604F)", border: "4px solid #2B1A10" }} />
          <div style={{ flex: 1, background: "repeating-linear-gradient(180deg, rgba(34,24,15,0.55) 0 5px, transparent 5px 18px)" }} />
        </div>
      </div>
    </div>
  );
};

export const PlacaSubst: React.FC<{ texto: string; x: number; y: number; u: number }> = ({ texto: tx, x, y, u }) => {
  if (u < 0) return null;
  const p = mola(u, 2, 0.5);
  const glitch = u < 0.45 ? (Math.floor(u * 40) % 3 === 0 ? 0.25 : 1) : 1;
  const dx = u < 0.45 ? Math.sin(u * 120) * 10 : 0;
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) translateY(${(1 - p) * 700}px)` }}>
      <div style={{ width: 640, height: 420, borderRadius: 30, background: "#121418", border: "10px solid #000", boxShadow: "0 0 0 8px #3A3F4A, 16px 20px 0 rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(circle, rgba(255,40,40,0.08) 1px, transparent 2px) 0 0/14px 14px" }} />
        <div style={{ fontFamily: FONTE.titulo, fontSize: 300, color: "#FF3B30", textShadow: "0 0 30px #FF3B30, 0 0 60px rgba(255,59,48,0.6)", opacity: glitch, transform: `translateX(${dx}px)` }}>{tx}</div>
      </div>
      <div style={{ width: 90, height: 260, background: "#2A2E36", margin: "0 auto", border: "6px solid #000" }} />
    </div>
  );
};

export const Martelo: React.FC<{ x: number; y: number; batidas: number; u: number }> = ({ x, y, batidas, u }) => {
  if (u < 0) return null;
  const per = 0.36;
  const k = Math.min(batidas - 1, Math.floor(u / per));
  const v = u - k * per;
  const ang = v < 0.12 ? -50 + (v / 0.12) * 50 : u > batidas * per ? -10 : -50 * Math.min(1, (v - 0.12) / 0.2);
  return (
    <div style={{ position: "absolute", left: x - 170, top: y - 170, transform: `rotate(${ang}deg)`, transformOrigin: "80% 80%" }}>
      <svg width={340} height={340} viewBox="0 0 340 340">
        <line x1={110} y1={110} x2={290} y2={290} stroke={O} strokeWidth={34} strokeLinecap="round" />
        <line x1={110} y1={110} x2={290} y2={290} stroke="#A4652E" strokeWidth={20} strokeLinecap="round" />
        <g transform="rotate(45 110 110)">
          <rect x={30} y={70} width={160} height={80} rx={18} fill="#7A4420" stroke={O} strokeWidth={9} />
          <rect x={20} y={64} width={26} height={92} rx={8} fill="#D9B060" stroke={O} strokeWidth={7} />
          <rect x={174} y={64} width={26} height={92} rx={8} fill="#D9B060" stroke={O} strokeWidth={7} />
        </g>
      </svg>
    </div>
  );
};
export const impactosMartelo = (t0: number, n: number) => Array.from({ length: n }).map((_, i) => t0 + i * 0.36 + 0.12);

export const Bloco: React.FC<{ texto: string; x: number; y: number; u: number }> = ({ texto: tx, x, y, u }) => {
  if (u < 0) return null;
  const queda = 0.32;
  const yy = u < queda ? -1100 * Math.pow(1 - u / queda, 2) : 0;
  const v = u - queda;
  const sq = v > 0 ? 0.22 * Math.exp(-v * 7) * Math.cos(v * 22) : 0;
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-100%) translateY(${yy}px) scale(${1 + sq}, ${1 - sq})`, transformOrigin: "50% 100%" }}>
      <div style={{ width: 300, height: 230, background: "linear-gradient(180deg,#E1251B,#A8160F)", border: "10px solid #000", borderRadius: 26, boxShadow: "14px 18px 0 rgba(0,0,0,0.45), inset 0 -18px 0 rgba(0,0,0,0.25)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={texto("#FFFFFF", 170)}>{tx}</div>
      </div>
    </div>
  );
};
export const impactoBloco = (t0: number) => t0 + 0.32;

type Linha = [string, string, number];
export const Tabela: React.FC<{ antes: Linha[]; depois: Linha[]; y: number; u: number; tLusa: number; tFlu: number }> = ({ antes, depois, y, u, tLusa, tFlu }) => {
  if (u < 0) return null;
  const H = 128;
  const nomes = antes.map((l) => l[1]);
  const posAntes = (n: string) => antes.findIndex((l) => l[1] === n);
  const posDepois = (n: string) => depois.findIndex((l) => l[1] === n);
  const ptsAntes = (n: string) => antes[posAntes(n)][2];
  const ptsDepois = (n: string) => depois[posDepois(n)][2];
  // todos trocam quando a Lusa despenca; o Flu "sobe" junto (destaque verde no tFlu)
  const p = mola(u - tLusa, 1.6, 0.55);
  const destaque = (n: string) => (n === "PORTUGUESA" ? "#D7262E" : n === "FLUMINENSE" ? "#7A1A34" : n === "FLAMENGO" ? "#1A1A1A" : "#1C2A55");
  return (
    <div style={{ position: "absolute", left: 60, top: y, width: 960, transform: `scale(${mola(u)})`, transformOrigin: "50% 0" }}>
      <div style={{ ...texto(COR.amarelo, 84), textAlign: "center", marginBottom: 16 }}>BRASILEIRÃO 2013</div>
      <div style={{ position: "relative", height: H * nomes.length + 20 }}>
        {nomes.map((n) => {
          const yy = interpolate(clamp(p, 0, 1.08), [0, 1], [posAntes(n) * H, posDepois(n) * H]);
          const pts = Math.round(interpolate(clamp(p), [0, 1], [ptsAntes(n), ptsDepois(n)]));
          const pos = p > 0.5 ? depois[posDepois(n)][0] : antes[posAntes(n)][0];
          const flu = n === "FLUMINENSE" && u > tFlu;
          const lusa = n === "PORTUGUESA";
          return (
            <div key={n} style={{ position: "absolute", top: yy, left: 0, right: 0, height: H - 14, display: "flex", alignItems: "center", gap: 20, background: destaque(n), border: `6px solid ${flu ? "#1FB35A" : lusa ? "#FFD400" : "#000"}`, borderRadius: 18, padding: "0 26px", boxShadow: lusa ? "0 0 30px rgba(255,212,0,0.6)" : "6px 8px 0 rgba(0,0,0,0.4)", zIndex: lusa || flu ? 2 : 1 }}>
              <div style={{ ...texto("#FFFFFF", 66), width: 90 }}>{pos}º</div>
              <div style={{ ...texto("#FFFFFF", 64), flex: 1 }}>{n}</div>
              <div style={{ ...texto(COR.amarelo, 70) }}>{pts}</div>
            </div>
          );
        })}
        {/* linha do Z4 (entre 16º e 17º) */}
        <div style={{ position: "absolute", top: 6 * H - 7, left: -20, right: -20, height: 0, borderTop: "8px dashed #FF3B30" }} />
        <div style={{ position: "absolute", top: 6 * H - 40, right: -10, ...texto("#FF3B30", 46) }}>Z4</div>
      </div>
    </div>
  );
};

export const Buraco: React.FC<{ texto: string; x: number; y: number; u: number }> = ({ texto: tx, x, y, u }) => {
  if (u < 0) return null;
  const p = mola(u, 2, 0.6);
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) scale(${p})` }}>
      <svg width={900} height={300} viewBox="0 0 900 300">
        <ellipse cx={450} cy={150} rx={430} ry={130} fill="#06070C" stroke={O} strokeWidth={12} />
        <ellipse cx={450} cy={170} rx={360} ry={90} fill="#000" />
      </svg>
      <div style={{ position: "absolute", left: 600, top: -150, transform: "rotate(8deg)" }}>
        <div style={{ background: "#F2E6C8", border: "8px solid #000", padding: "6px 26px", ...texto("#D7262E", 84, { textShadow: "none" }) }}>{tx}</div>
        <div style={{ width: 22, height: 170, background: "#7A4A2A", border: "5px solid #000", margin: "0 auto" }} />
      </div>
    </div>
  );
};

export const Gordura: React.FC<{ y: number; u: number }> = ({ y, u }) => {
  if (u < 0) return null;
  const barras: [string, number, string, string][] = [
    ["FLAMENGO", 45, "#1A1A1A", "flamengo"],
    ["PORTUGUESA", 44, "#D7262E", "portuguesa"],
  ];
  return (
    <div style={{ position: "absolute", left: 90, top: y, width: 900 }}>
      <div style={{ ...texto(COR.amarelo, 80), textAlign: "center" }}>PONTOS FINAIS</div>
      <div style={{ display: "flex", justifyContent: "space-around", alignItems: "flex-end", height: 760, position: "relative", marginTop: 40 }}>
        {barras.map(([n, pts, cor, esc], i) => {
          const h = (pts - 38) * 62 * mola(u - i * 0.15, 1.6, 0.5);
          return (
            <div key={n} style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 300 }}>
              <div style={{ ...texto("#fff", 90) }}>{pts}</div>
              <div style={{ width: 240, height: h, background: cor, border: "8px solid #000", borderRadius: "20px 20px 0 0", boxShadow: "10px 0 0 rgba(0,0,0,0.35)" }} />
              <Img src={staticFile(`escudos/${esc}.png`)} style={{ height: 130, marginTop: 14, objectFit: "contain" }} />
            </div>
          );
        })}
        <div style={{ position: "absolute", left: -30, right: -30, bottom: 144 + 6.5 * 62, borderTop: "8px dashed #FF3B30" }} />
        <div style={{ position: "absolute", left: 300, width: 300, textAlign: "center", bottom: 144 + 6.5 * 62 + 14, ...texto("#FF3B30", 44) }}>ZONA DE QUEDA</div>
      </div>
    </div>
  );
};

export const Papel: React.FC<{ texto: string; x: number; y: number; u: number; uRasga: number }> = ({ texto: tx, x, y, u, uRasga }) => {
  if (u < 0) return null;
  const r = clamp(uRasga / 0.5);
  const conteudo = (
    <div style={{ width: 700, height: 900, background: "#FBF8EE", border: "8px solid #2B1A10", padding: 50, boxShadow: "18px 22px 0 rgba(0,0,0,0.4)" }}>
      <div style={{ fontFamily: FONTE.titulo, fontSize: 130, color: "#1C3A8A", textAlign: "center" }}>{tx}</div>
      <div style={{ height: 520, marginTop: 30, background: "repeating-linear-gradient(180deg, rgba(40,30,20,0.45) 0 6px, transparent 6px 40px)" }} />
      <div style={{ position: "absolute", right: 70, bottom: 60, width: 160, height: 160, borderRadius: "50%", border: "10px solid #1FB35A", transform: "rotate(-12deg)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONTE.titulo, fontSize: 40, color: "#1FB35A" }}>DEFERIDA</div>
    </div>
  );
  const metade = (lado: -1 | 1) => (
    <div style={{ position: "absolute", left: 0, top: 0, clipPath: lado === -1 ? "polygon(0 0, 52% 0, 46% 30%, 54% 55%, 47% 80%, 52% 100%, 0 100%)" : "polygon(52% 0, 100% 0, 100% 100%, 52% 100%, 47% 80%, 54% 55%, 46% 30%)", transform: `translate(${lado * r * 160}px, ${r * r * 260}px) rotate(${lado * r * 14}deg)`, opacity: 1 - clamp((uRasga - 0.6) / 0.5) }}>
      {conteudo}
    </div>
  );
  return (
    <div style={{ position: "absolute", left: x - 350, top: y - 450, width: 700, height: 900, transform: `scale(${mola(u)})` }}>
      {uRasga < 0 ? conteudo : [metade(-1), metade(1)]}
    </div>
  );
};

export const Placa: React.FC<{ texto: string; x: number; y: number; u: number }> = ({ texto: tx, x, y, u }) => {
  if (u < 0) return null;
  const p = mola(u, 2, 0.4);
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,0) translateY(${(1 - p) * 900}px) rotate(${-4 + Math.sin(u * 2) * 1.5}deg)`, transformOrigin: "50% 100%" }}>
      <div style={{ background: "#3A3F4A", border: "9px solid #000", padding: "14px 40px", boxShadow: "12px 14px 0 rgba(0,0,0,0.5)" }}>
        <div style={{ ...texto("#FFD400", 120), whiteSpace: "nowrap" }}>{tx}</div>
      </div>
      <div style={{ width: 34, height: 600, background: "#555B68", border: "6px solid #000", margin: "0 auto" }} />
    </div>
  );
};

/** Silhueta genérica de jogador em contraluz (sem rosto, nenhuma pessoa real). */
export const Silhueta: React.FC<{ x: number; pe: number; alt: number; u: number; children: React.ReactNode }> = ({ x, pe, alt, u, children }) => {
  if (u < 0) return null;
  const p = clamp(u / 1.4);
  const s = 0.75 + 0.25 * p;
  return (
    <div style={{ position: "absolute", left: x - (alt * 0.555 * s) / 2, top: pe - alt * s + (1 - p) * 60, opacity: clamp(u / 0.3), filter: "brightness(0) drop-shadow(0 0 14px rgba(255,226,160,0.95)) drop-shadow(0 0 40px rgba(255,200,120,0.6))", transform: `scale(${s})`, transformOrigin: "50% 100%" }}>
      {children}
    </div>
  );
};

/* ----------------------------------------------------------- partículas */
const rnd = (s: number) => {
  const v = Math.sin(s * 12.9898) * 43758.5453;
  return v - Math.floor(v);
};

export const Confete: React.FC<{ u: number }> = ({ u }) => {
  if (u < 0) return null;
  const cores = ["#FFD400", "#D7262E", "#1FB35A", "#FFFFFF", "#2A6BD8"];
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: 80 }).map((_, i) => {
        const x = rnd(i) * 1080 + Math.sin(u * 3 + i) * 40;
        const y = -100 + u * (420 + rnd(i + 3) * 380) - rnd(i + 9) * 500;
        return <div key={i} style={{ position: "absolute", left: x, top: y, width: 26, height: 14, background: cores[i % 5], border: "2px solid rgba(0,0,0,0.5)", transform: `rotate(${u * 400 + i * 40}deg) scaleY(${Math.cos(u * 8 + i)})` }} />;
      })}
    </AbsoluteFill>
  );
};

export const Poeira: React.FC<{ u: number; y?: number }> = ({ u, y = 1820 }) => {
  if (u < 0 || u > 1.2) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: 16 }).map((_, i) => {
        const a = (i / 16) * Math.PI;
        const d = u * (300 + rnd(i) * 300);
        const r = 40 + u * 120 * (0.6 + rnd(i + 4));
        return <div key={i} style={{ position: "absolute", left: 540 + Math.cos(a) * d * (i % 2 ? 1 : -1) - r, top: y - Math.sin(a) * d * 0.25 - r, width: r * 2, height: r * 2, borderRadius: "50%", background: "rgba(235,225,205,0.55)", opacity: 1 - u / 1.2, filter: "blur(4px)" }} />;
      })}
    </AbsoluteFill>
  );
};

export const Faiscas: React.FC<{ x: number; y: number; u: number }> = ({ x, y, u }) => {
  if (u < 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: 34 }).map((_, i) => {
        const ciclo = (u * 1.6 + rnd(i)) % 1;
        const a = rnd(i + 2) * Math.PI * 2;
        const d = ciclo * (180 + rnd(i + 5) * 220);
        return <div key={i} style={{ position: "absolute", left: x + Math.cos(a) * d, top: y + Math.sin(a) * d * 0.7, width: 34, height: 8, borderRadius: 4, background: i % 3 ? "#FFE27A" : "#FFFFFF", boxShadow: "0 0 14px #FFB300", opacity: 1 - ciclo, transform: `rotate(${(a * 180) / Math.PI}deg)` }} />;
      })}
      <div style={{ position: "absolute", left: x - 90, top: y - 90, width: 180, height: 180, borderRadius: "50%", background: "radial-gradient(circle, rgba(255,240,180,0.9), rgba(255,200,80,0) 70%)", transform: `scale(${1 + 0.2 * Math.sin(u * 20)})` }} />
    </AbsoluteFill>
  );
};

export const Chuva: React.FC<{ t: number }> = ({ t }) => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    {Array.from({ length: 140 }).map((_, i) => {
      const x = rnd(i) * 1200 - 60;
      const y = ((rnd(i + 7) * 2100 + t * (1500 + rnd(i + 3) * 500)) % 2100) - 120;
      return <div key={i} style={{ position: "absolute", left: x - (y / 2100) * 80, top: y, width: 4, height: 70, background: "rgba(200,215,240,0.55)", transform: "rotate(12deg)" }} />;
    })}
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(40,55,85,0.35), rgba(20,30,50,0.2))" }} />
  </AbsoluteFill>
);

export const Flashes: React.FC<{ t: number }> = ({ t }) => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    {Array.from({ length: 26 }).map((_, i) => {
      const per = 0.7 + rnd(i) * 1.1;
      const f = ((t + rnd(i + 3) * per) % per) / per;
      const on = f < 0.08 ? 1 - f / 0.08 : 0;
      if (!on) return null;
      const x = rnd(i + 11) * 1080;
      const y = 470 + rnd(i + 21) * 280;
      return <div key={i} style={{ position: "absolute", left: x - 60, top: y - 60, width: 120, height: 120, borderRadius: "50%", background: "radial-gradient(circle, rgba(255,255,255,1), rgba(255,255,255,0) 65%)", opacity: on }} />;
    })}
  </AbsoluteFill>
);

/** Objetos que o personagem segura. */
export const Regulamento: React.FC = () => (
  <g transform="translate(170 470) rotate(-6)">
    <rect x={0} y={0} width={170} height={220} rx={8} fill="#FBF8EE" stroke={O} strokeWidth={7} />
    <rect x={20} y={20} width={130} height={26} fill="#1C3A8A" />
    {[70, 100, 130, 160, 190].map((y) => (
      <line key={y} x1={22} y1={y} x2={148} y2={y} stroke="#9AA0AE" strokeWidth={8} />
    ))}
  </g>
);
export const Maleta: React.FC = () => (
  <g transform="translate(160 520)">
    <rect x={40} y={-30} width={100} height={40} rx={14} fill="none" stroke={O} strokeWidth={10} />
    <rect x={0} y={0} width={180} height={130} rx={14} fill="#6B3E1E" stroke={O} strokeWidth={8} />
    <rect x={80} y={50} width={20} height={26} fill="#D9B060" stroke={O} strokeWidth={4} />
  </g>
);
export const Telefone: React.FC = () => (
  <g transform="translate(392 214) rotate(14)">
    <rect x={0} y={0} width={56} height={110} rx={12} fill="#1B1E26" stroke={O} strokeWidth={6} />
    <rect x={8} y={12} width={40} height={70} rx={4} fill="#3A3F4A" />
  </g>
);
export const Suor: React.FC<{ t: number }> = ({ t }) => (
  <g>
    {[0, 1].map((i) => {
      const f = (t * 0.9 + i * 0.5) % 1;
      return <path key={i} d={`M${120 + i * 260} ${200 + f * 120} q-12 22 0 34 q12 -12 0 -34 Z`} fill="#8FD0FF" stroke={O} strokeWidth={4} opacity={1 - f} />;
    })}
  </g>
);
