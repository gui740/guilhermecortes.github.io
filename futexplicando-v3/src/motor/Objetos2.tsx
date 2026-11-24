import React from "react";
import { Img, interpolate, staticFile } from "remotion";
import { COR, FONTE } from "../estilo/tokens";
import { TacaAntigaG } from "../personagens/Props";
import mapa from "../data/mapa-mundi.json";
import { batida, Carimbo, mola } from "./Objetos";

/** Objetos do vídeo "O Palmeiras tem Mundial?!" (reutilizáveis). `u` = segundos desde que entram. */
const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const txt = (cor: string, tam: number, extra: React.CSSProperties = {}): React.CSSProperties => ({
  fontFamily: FONTE.titulo,
  fontSize: tam,
  color: cor,
  WebkitTextStroke: `${Math.round(tam / 11)}px #000`,
  paintOrder: "stroke fill",
  textShadow: `0 ${Math.round(tam / 14)}px 0 rgba(0,0,0,0.55)`,
  lineHeight: 1.02,
  ...extra,
});

/** Carimbo que troca de texto com glitch (ex.: SIM → NÃO). */
export const CarimboTroca: React.FC<{ de: string; para: string; corDe: string; corPara: string; x: number; y: number; u: number; uTroca: number }> = ({ de, para, corDe, corPara, x, y, u, uTroca }) => {
  if (u < 0) return null;
  const trocou = uTroca >= 0;
  const g = uTroca >= 0 && uTroca < 0.3;
  const dx = g ? Math.sin(uTroca * 140) * 18 : 0;
  const mostra = g ? (Math.floor(uTroca * 40) % 2 ? de : para) : trocou ? para : de;
  const cor = mostra === para ? corPara : corDe;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, transform: `translateX(${dx}px)`, filter: g ? "drop-shadow(8px 0 0 rgba(255,0,60,0.7)) drop-shadow(-8px 0 0 rgba(0,220,255,0.7))" : undefined }}>
      <Carimbo texto={mostra} cor={cor} x={x} y={y} rot={mostra === para ? 8 : -8} u={trocou && !g ? Math.max(0.16, uTroca - 0.3 + 0.16) : u} />
    </div>
  );
};

/** Ano datilografado (máquina de escrever) num papel. */
export const Datilografa: React.FC<{ texto: string; x: number; y: number; u: number }> = ({ texto, x, y, u }) => {
  if (u < 0) return null;
  const n = Math.min(texto.length, Math.floor(u / 0.16) + 1);
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: "translate(-50%,-50%) rotate(-2deg)" }}>
      <div style={{ background: "#F3EAD3", border: "6px solid #2B1A10", padding: "20px 60px", boxShadow: "16px 20px 0 rgba(0,0,0,0.4)" }}>
        <div style={{ fontFamily: "'Courier New', Courier, monospace", fontWeight: 900, fontSize: 240, color: "#1A120A", letterSpacing: 6 }}>
          {texto.slice(0, n)}
          <span style={{ opacity: Math.floor(u * 4) % 2 ? 0 : 1 }}>_</span>
        </div>
      </div>
    </div>
  );
};
export const teclasDatilografa = (t0: number, texto: string) => Array.from({ length: texto.length }).map((_, i) => t0 + i * 0.16);

/** Mapa-múndi vintage com pinos acendendo um a um. */
export const MapaPinos: React.FC<{ y: number; u: number; ritmo?: number }> = ({ y, u, ritmo = 0.32 }) => {
  if (u < 0) return null;
  const M = mapa as unknown as { w: number; h: number; paths: string[]; cidades: Record<string, [number, number]> };
  const cid = Object.entries(M.cidades);
  const s = 1000 / M.w;
  return (
    <div style={{ position: "absolute", left: 40, top: y, width: 1000, transform: `scale(${mola(u, 1.6, 0.6)})`, transformOrigin: "50% 50%" }}>
      <svg width={1000} height={M.h * s} viewBox={`0 0 ${M.w} ${M.h}`} style={{ background: "#E6D6A8", border: "10px solid #5A3A1E", boxShadow: "18px 22px 0 rgba(0,0,0,0.45)" }}>
        <defs>
          <pattern id="mar" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M0 20 Q10 14 20 20 T40 20" stroke="#B9A57A" strokeWidth="2" fill="none" />
          </pattern>
        </defs>
        <rect width={M.w} height={M.h} fill="url(#mar)" opacity={0.6} />
        {M.paths.map((d, i) => (
          <path key={i} d={d} fill="#C9B07A" stroke="#6B4A26" strokeWidth={1.6} strokeLinejoin="round" />
        ))}
        {cid.map(([n, [cx, cy]], i) => {
          const v = u - 0.4 - i * ritmo;
          if (v < 0) return null;
          const k = mola(v, 2.6, 0.4);
          return (
            <g key={n} transform={`translate(${cx} ${cy}) scale(${k})`}>
              <circle r={26} fill="#FFD400" opacity={0.35 * Math.max(0, 1 - v)} />
              <path d="M0 0 C-12 -18 -14 -30 0 -38 C14 -30 12 -18 0 0 Z" fill="#C8102E" stroke="#2B1A10" strokeWidth={3} />
              <circle cy={-27} r={5} fill="#fff" />
            </g>
          );
        })}
      </svg>
      <div style={{ ...txt(COR.amarelo, 58), textAlign: "center", marginTop: 14 }}>{`${Math.min(8, Math.max(0, Math.floor((u - 0.4) / ritmo) + 1))} CLUBES`}</div>
    </div>
  );
};
export const popsMapa = (t0: number, n = 8, ritmo = 0.32) => Array.from({ length: n }).map((_, i) => t0 + 0.4 + i * ritmo);

/** Letreiro manual de placar (placas de madeira penduradas). */
export const PlacarManual: React.FC<{ a: string; b: string; ga: number; gb: number; escA: string; escB: string; x: number; y: number; u: number }> = ({ a, b, ga, gb, escA, escB, x, y, u }) => {
  if (u < 0) return null;
  const q = 0.32;
  const yy = u < q ? -1200 * Math.pow(1 - u / q, 2) : 0;
  const v = u - q;
  const sq = v > 0 ? 0.18 * Math.exp(-v * 7) * Math.cos(v * 22) : 0;
  const placa = (t: string, cor = "#F2E6C8") => (
    <div style={{ width: 150, height: 170, background: cor, border: "8px solid #2B1A10", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONTE.titulo, fontSize: 130, color: "#1A120A", boxShadow: "inset 0 -10px 0 rgba(0,0,0,0.15)" }}>{t}</div>
  );
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) translateY(${yy}px) scale(${1 + sq}, ${1 - sq})`, transformOrigin: "50% 100%" }}>
      <div style={{ background: "#3A4A2A", border: "12px solid #2B1A10", padding: "26px 30px", boxShadow: "18px 22px 0 rgba(0,0,0,0.5)", display: "flex", alignItems: "center", gap: 18 }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
          <Img src={staticFile(`escudos/${escA}.png`)} style={{ height: 120, objectFit: "contain" }} />
          <div style={txt("#F2E6C8", 54)}>{a}</div>
        </div>
        {placa(String(ga))}
        <div style={txt("#F2E6C8", 90)}>×</div>
        {placa(String(gb))}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
          <Img src={staticFile(`escudos/${escB}.png`)} style={{ height: 120, objectFit: "contain" }} />
          <div style={txt("#F2E6C8", 54)}>{b}</div>
        </div>
      </div>
    </div>
  );
};

/** Recorte de jornal antigo com manchete (texto sempre pelo Remotion). */
export const Recorte: React.FC<{ manchete: string; sub?: string; x: number; y: number; rot?: number; u: number; destaque?: string }> = ({ manchete, sub, x, y, rot = -4, u, destaque }) => {
  if (u < 0) return null;
  const k = batida(u);
  const partes = destaque ? manchete.split(destaque) : [manchete];
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${k})` }}>
      <div style={{ background: "#EDE2C4", padding: "22px 34px", boxShadow: "14px 18px 0 rgba(0,0,0,0.45)", clipPath: "polygon(0 4%, 6% 0, 20% 3%, 40% 0, 60% 4%, 80% 1%, 100% 3%, 98% 50%, 100% 97%, 82% 100%, 60% 96%, 40% 100%, 18% 97%, 0 100%, 2% 50%)" }}>
        <div style={{ fontFamily: "Georgia, serif", fontSize: 24, color: "#3A2A18", borderBottom: "3px solid #3A2A18", marginBottom: 6 }}>JULHO DE 1951</div>
        <div style={{ fontFamily: FONTE.titulo, fontSize: 110, color: "#1A120A", lineHeight: 1, whiteSpace: "nowrap" }}>
          {destaque ? (
            <>
              {partes[0]}
              <span style={{ background: "#FFD400", padding: "0 10px" }}>{destaque}</span>
              {partes[1]}
            </>
          ) : (
            manchete
          )}
        </div>
        {sub && <div style={{ fontFamily: "Georgia, serif", fontStyle: "italic", fontSize: 34, color: "#3A2A18", marginTop: 6 }}>{sub}</div>}
      </div>
    </div>
  );
};

/** Taça antiga solta (com brilho e estrela). */
export const Taca: React.FC<{ x: number; y: number; s?: number; u: number }> = ({ x, y, s = 1.6, u }) => {
  if (u < 0) return null;
  const k = mola(u, 2, 0.5);
  return (
    <svg width={700} height={700} viewBox="-350 -400 700 700" style={{ position: "absolute", left: x - 350, top: y - 400, overflow: "visible", transform: `scale(${k}) rotate(${Math.sin(u * 2) * 3}deg)` }}>
      <TacaAntigaG x={0} y={0} s={s} brilho={0.6 + 0.3 * Math.sin(u * 5)} />
    </svg>
  );
};

/** Contador de ano girando de A até B. */
export const ContadorAno: React.FC<{ de: number; ate: number; x: number; y: number; u: number; dur?: number }> = ({ de, ate, x, y, u, dur = 1.1 }) => {
  if (u < 0) return null;
  const n = Math.round(interpolate(u, [0, dur], [de, ate], { extrapolateRight: "clamp", easing: (v) => 1 - Math.pow(1 - v, 3) }));
  const fim = u >= dur;
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) scale(${fim ? batida(u - dur + 0.001) * 0.95 + 0.05 : 1})` }}>
      <div style={{ background: "#0E1430", border: "8px solid #000", borderRadius: 26, padding: "10px 46px", boxShadow: `0 0 0 6px ${COR.amarelo}, 14px 18px 0 rgba(0,0,0,0.45)` }}>
        <div style={txt(fim ? COR.amarelo : "#FFFFFF", 200, { fontVariantNumeric: "tabular-nums" })}>{n}</div>
      </div>
    </div>
  );
};

/** Lista de campeões mundiais (escudos acendendo) com a linha da Copa Rio sendo riscada. */
export const ListaCampeoes: React.FC<{ y: number; u: number; uRisco: number; itens: [string, string][] }> = ({ y, u, uRisco, itens }) => {
  if (u < 0) return null;
  const risco = clamp(uRisco / 0.5);
  return (
    <div style={{ position: "absolute", left: 90, top: y, width: 900 }}>
      <div style={{ ...txt(COR.amarelo, 70), textAlign: "center", marginBottom: 16 }}>CAMPEÕES MUNDIAIS · FIFA</div>
      {itens.map(([esc, nome], i) => {
        const v = u - 0.2 - i * 0.28;
        const on = v > 0;
        return (
          <div key={nome} style={{ display: "flex", alignItems: "center", gap: 24, height: 118, marginBottom: 12, padding: "0 26px", background: on ? "#1C2A55" : "#121833", border: `6px solid ${on ? COR.amarelo : "#000"}`, borderRadius: 18, opacity: on ? 1 : 0.35, transform: `scale(${on ? 1 + 0.06 * Math.exp(-v * 8) : 1})` }}>
            <Img src={staticFile(`escudos/${esc}.png`)} style={{ height: 90, width: 90, objectFit: "contain", filter: on ? "none" : "grayscale(1)" }} />
            <div style={txt("#FFFFFF", 60)}>{nome}</div>
          </div>
        );
      })}
      <div style={{ position: "relative", display: "flex", alignItems: "center", gap: 24, height: 118, padding: "0 26px", background: "#3A1414", border: "6px solid #000", borderRadius: 18, opacity: 1 - risco * 0.55, filter: `grayscale(${risco})` }}>
        <Img src={staticFile("escudos/palmeiras.png")} style={{ height: 90, width: 90, objectFit: "contain" }} />
        <div style={txt("#FFFFFF", 60)}>COPA RIO 1951</div>
        <div style={{ position: "absolute", left: 20, top: 52, height: 14, width: `${risco * 92}%`, background: "#FF2A2A", borderRadius: 7, boxShadow: "0 0 12px #FF2A2A" }} />
      </div>
    </div>
  );
};
export const dingsLista = (t0: number, n: number) => Array.from({ length: n }).map((_, i) => t0 + 0.2 + i * 0.28);

/** Relatório moderno com "COPA RIO" destacado e lupa passando. */
export const Relatorio: React.FC<{ x: number; y: number; u: number }> = ({ x, y, u }) => {
  if (u < 0) return null;
  const k = mola(u, 1.8, 0.55);
  const lx = interpolate(u, [0.5, 2.2], [-260, 120], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) scale(${k}) rotate(-3deg)` }}>
      <div style={{ width: 760, background: "#FFFFFF", border: "8px solid #1A1F2B", borderRadius: 14, padding: 40, boxShadow: "18px 22px 0 rgba(0,0,0,0.45)", position: "relative" }}>
        <div style={{ fontFamily: FONTE.texto, fontWeight: 700, fontSize: 30, color: "#5A6478" }}>RELATÓRIO 2025 · TORNEIOS HISTÓRICOS</div>
        <div style={{ height: 8, width: 300, background: "#2A6BD8", margin: "16px 0 26px" }} />
        {["COPAS ENTRE CONFEDERAÇÕES", "", "COPA RIO 1951 — PALMEIRAS", "COPA RIO 1952 — FLUMINENSE"].map((l, i) => (
          <div key={i} style={{ fontFamily: FONTE.titulo, fontSize: i === 0 ? 46 : 52, color: i >= 2 ? "#111" : "#2A6BD8", background: i === 2 && u > 1.2 ? "#FFE36A" : "transparent", padding: "4px 10px", marginBottom: 10, minHeight: i === 1 ? 10 : undefined }}>{l}</div>
        ))}
        {[0, 1, 2].map((i) => (
          <div key={i} style={{ height: 14, background: "#D6DBE6", margin: "18px 0", width: `${90 - i * 18}%` }} />
        ))}
        <svg width={260} height={260} viewBox="0 0 260 260" style={{ position: "absolute", left: 300 + lx, top: 120 }}>
          <circle cx={100} cy={100} r={78} fill="rgba(200,230,255,0.25)" stroke="#1A1F2B" strokeWidth={14} />
          <line x1={156} y1={156} x2={240} y2={240} stroke="#1A1F2B" strokeWidth={26} strokeLinecap="round" />
        </svg>
      </div>
    </div>
  );
};

export const Interrogacao: React.FC<{ x: number; y: number; u: number }> = ({ x, y, u }) => {
  if (u < 0) return null;
  const k = batida(u) * (1 + 0.07 * Math.sin(u * 7));
  return <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) scale(${k})`, ...txt(COR.amarelo, 420) }}>?</div>;
};

/** Ata com assinatura e carimbo "BANIDO" estilizado por cima (sem desenhar a pessoa). */
export const AtaBanida: React.FC<{ x: number; y: number; u: number; uCarimbo: number }> = ({ x, y, u, uCarimbo }) => {
  if (u < 0) return null;
  const k = mola(u, 1.8, 0.55);
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,-50%) scale(${k}) rotate(2deg)` }}>
      <div style={{ width: 760, background: "#FBF8EE", border: "8px solid #2B1A10", padding: 44, boxShadow: "18px 22px 0 rgba(0,0,0,0.45)", position: "relative" }}>
        <div style={{ fontFamily: "Georgia, serif", fontWeight: 900, fontSize: 52, textAlign: "center", color: "#1A120A" }}>ATA · 07/06/2014</div>
        <div style={{ fontFamily: "Georgia, serif", fontSize: 30, textAlign: "center", color: "#3A2A18", marginBottom: 20 }}>Comitê Executivo · São Paulo</div>
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={i} style={{ height: 12, background: "rgba(40,30,20,0.4)", margin: "20px 0", width: `${96 - (i % 2) * 14}%` }} />
        ))}
        <svg width={420} height={120} viewBox="0 0 420 120" style={{ display: "block", margin: "30px auto 0" }}>
          <path d="M10 80 Q60 20 100 70 T190 60 Q230 30 260 80 T400 50" stroke="#1C3A8A" strokeWidth={6} fill="none" />
          <line x1={10} y1={100} x2={410} y2={100} stroke="#2B1A10" strokeWidth={3} />
        </svg>
        <div style={{ fontFamily: "Georgia, serif", fontSize: 26, textAlign: "center", color: "#3A2A18" }}>Secretário-geral</div>
        {uCarimbo >= 0 && (
          <div style={{ position: "absolute", left: 380, top: 470 }}>
            <Carimbo texto="BANIDO" cor="#C8102E" x={0} y={0} rot={-14} u={uCarimbo} />
          </div>
        )}
      </div>
    </div>
  );
};

/** Carimbo de mão batendo (dirigente carimbando). */
export const Carimbador: React.FC<{ x: number; y: number; u: number; batidas?: number }> = ({ x, y, u, batidas = 1 }) => {
  if (u < 0) return null;
  const per = 0.5;
  const k = Math.min(batidas - 1, Math.floor(u / per));
  const v = u - k * per;
  const dy = v < 0.14 ? -160 + (v / 0.14) * 160 : u > batidas * per ? -60 : -160 * Math.min(1, (v - 0.14) / 0.3);
  return (
    <svg width={260} height={340} viewBox="0 0 260 340" style={{ position: "absolute", left: x - 130, top: y - 300 + dy }}>
      <rect x={100} y={20} width={60} height={150} rx={26} fill="#7A4420" stroke="#2B1A10" strokeWidth={8} />
      <ellipse cx={130} cy={30} rx={50} ry={26} fill="#9A5A2E" stroke="#2B1A10" strokeWidth={8} />
      <rect x={40} y={170} width={180} height={50} rx={10} fill="#3A3F4A" stroke="#2B1A10" strokeWidth={8} />
      <rect x={30} y={220} width={200} height={40} rx={8} fill="#C8102E" stroke="#2B1A10" strokeWidth={8} />
    </svg>
  );
};
export const impactosCarimbador = (t0: number, n: number) => Array.from({ length: n }).map((_, i) => t0 + i * 0.5 + 0.14);
