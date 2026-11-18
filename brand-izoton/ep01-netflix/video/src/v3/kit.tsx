// Kit de motion v3 · Brand by Izoton
// Regra: todo componente tem entrada, vida e saída. Nada parado por mais de 2,5 s.
import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FAIXA, FONT, MONO } from "../theme";

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

/** Converte segundos (tempo de palavra) em quadro. */
/**
 * Mapa de tempo (ressincronização): converte os segundos escritos na cena (tempos da voz antiga) para os tempos da voz nova.
 * Pares [antigo, novo] em ordem; entre os pares, linear; fora deles, inclinação 1.
 */
export const WarpCtx = React.createContext<[number, number][] | null>(null);
export const warp = (pares: [number, number][] | null, s: number) => {
  if (!pares || pares.length === 0) return s;
  if (s <= pares[0][0]) return pares[0][1] + (s - pares[0][0]);
  for (let i = 1; i < pares.length; i++) {
    const [a0, b0] = pares[i - 1], [a1, b1] = pares[i];
    if (s <= a1) return b0 + ((s - a0) * (b1 - b0)) / (a1 - a0);
  }
  const [aN, bN] = pares[pares.length - 1];
  return bN + (s - aN);
};
export const useS = () => {
  const { fps } = useVideoConfig();
  const pares = React.useContext(WarpCtx);
  return (s: number) => Math.round(warp(pares, s) * fps);
};

/** Quadro "em três": a animação anda em degraus de 3 quadros (10 poses/s a 30 fps), como stop-motion. */
export const useStepFrame = (passo = 3) => {
  const f = useCurrentFrame();
  return Math.floor(f / passo) * passo;
};

/** Tremor de 1–2 px que muda a cada pose (determinístico). */
export const jitter = (seed: string, f: number, amp = 1.5) => {
  const k = Math.floor(f / 3);
  return { x: (random(`${seed}x${k}`) - 0.5) * 2 * amp, y: (random(`${seed}y${k}`) - 0.5) * 2 * amp, r: (random(`${seed}r${k}`) - 0.5) * 0.6 };
};

/** Progresso de entrada em degraus (stop-motion) a partir de um quadro. */
export const useQueda = (inicio: number, dur = 9) => {
  const fs = useStepFrame();
  return interpolate(fs - inicio, [0, dur], [0, 1], { ...clamp, easing: easeOut });
};

/** Entrada lisa (para texto e interface). */
export const useEntrada = (inicio: number, dur = 8) => {
  const f = useCurrentFrame();
  return interpolate(f - inicio, [0, dur], [0, 1], { ...clamp, easing: easeOut });
};

/** Saída (1 → 0) nos últimos quadros do trecho. */
export const useSaida = (fim: number, dur = 8) => {
  const f = useCurrentFrame();
  return interpolate(f, [fim - dur, fim], [1, 0], { ...clamp, easing: easeInOut });
};

/* ------------------------------------------------------------------ texturas */
export const Grao: React.FC<{ opacidade?: number }> = ({ opacidade = 0.55 }) => {
  const f = useCurrentFrame();
  const i = Math.floor(f / 2) % 4;
  const ox = Math.floor(random(`g${f}`) * 400), oy = Math.floor(random(`h${f}`) * 400);
  // As 4 texturas ficam montadas como <Img> (o Remotion espera carregar); sem isso, o fundo CSS às vezes
  // não chega a tempo e o quadro sai claro (defeito de "pisca" visto na rodada 1).
  return (
    <>
      <div style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", opacity: 0 }}>
        {[0, 1, 2, 3].map((k) => <Img key={k} src={staticFile(`media/v3tex/grao_${k}.png`)} style={{ width: 1, height: 1 }} />)}
      </div>
      <AbsoluteFill style={{ pointerEvents: "none", opacity: opacidade, mixBlendMode: "multiply",
        backgroundImage: `url(${staticFile(`media/v3tex/grao_${i}.png`)})`, backgroundPosition: `${ox}px ${oy}px`, backgroundSize: "512px 512px" }} />
    </>
  );
};

export const Papel: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.branco }}>
    <Img src={staticFile("media/v3tex/papel.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.9 }} />
  </AbsoluteFill>
);

/** Câmera virtual: deriva lenta e contínua (3–8%) por cima de tudo. */
export const Camera: React.FC<{ children: React.ReactNode; de?: number; ate?: number; dx?: number; dy?: number; dur: number; degrau?: boolean }> =
  ({ children, de = 1.0, ate = 1.06, dx = 0, dy = 0, dur, degrau = false }) => {
    const f0 = useCurrentFrame();
    const f = degrau ? Math.floor(f0 / 3) * 3 : f0; // degrau: pose a cada 3 quadros (stop-motion)
    const k = interpolate(f, [0, dur], [0, 1], clamp);
    const s = de + (ate - de) * k;
    // degrau: além da aproximação, um vaivém lateral de 36 px a cada 4 s, para cena longa não parecer parada
    const vai = degrau ? 36 * (Math.abs(((f / 120) % 2) - 1) * 2 - 1) : 0;
    return <AbsoluteFill style={{ transform: `translate(${dx * k + vai}px, ${dy * k}px) scale(${s})`, transformOrigin: "50% 45%" }}>{children}</AbsoluteFill>;
  };

/** Camada com parallax: cada camada desliza numa velocidade. */
export const Camada: React.FC<{ children: React.ReactNode; vel: number; dur: number; z?: number }> = ({ children, vel, dur, z }) => {
  const f = useCurrentFrame();
  const k = interpolate(f, [0, dur], [0, 1], clamp);
  return <AbsoluteFill style={{ transform: `translateX(${-vel * 60 * k}px) translateY(${-vel * 14 * k}px)`, zIndex: z }}>{children}</AbsoluteFill>;
};

/* ------------------------------------------------------------------ recortes e cards */
/** Recorte que cai em degraus, com sombra real, inclinação e tremor; flutua depois. */
export const Recorte: React.FC<{ src: string; x: number; y: number; w: number; inicio: number; rot?: number; seed: string;
  sombra?: boolean; de?: "cima" | "baixo" | "esq" | "dir"; fim?: number; filtro?: string }> =
  ({ src, x, y, w, inicio, rot = 0, seed, sombra = true, de = "cima", fim, filtro }) => {
    const f = useCurrentFrame();
    const k = useQueda(inicio, 9);
    const sai = useSaida(fim ?? 1e9, 9);
    if (f < inicio) return null;
    const j = jitter(seed, f, 1.5);
    const off = (1 - k) * 160;
    const dx = de === "esq" ? -off : de === "dir" ? off : 0;
    const dy = de === "cima" ? -off : de === "baixo" ? off : 0;
    const flut = Math.sin((f - inicio) / 22 + random(seed) * 6) * 10;
    return (
      <div style={{ position: "absolute", left: x + dx + j.x, top: y + dy + j.y + flut, width: w, opacity: Math.min(1, k * 1.6) * sai,
        transform: `rotate(${rot + j.r + (1 - k) * 6}deg) scale(${0.92 + 0.08 * k})`,
        filter: `${sombra ? "drop-shadow(16px 18px 14px rgba(0,0,0,0.30)) drop-shadow(2px 3px 2px rgba(0,0,0,0.25))" : ""} ${filtro ?? ""}` }}>
        <Img src={staticFile(src)} style={{ width: "100%", display: "block" }} />
      </div>
    );
  };

/** Card com sombra suave e perspectiva 3D leve; entra subindo, flutua, sai. */
export const Card: React.FC<{ children: React.ReactNode; x: number; y: number; w: number; h?: number; inicio: number; fim?: number;
  rotY?: number; rotZ?: number; seed: string; fundo?: string; borda?: boolean }> =
  ({ children, x, y, w, h, inicio, fim, rotY = 0, rotZ = 0, seed, fundo = C.branco, borda = false }) => {
    const f = useCurrentFrame();
    const k = useEntrada(inicio, 9);
    const sai = useSaida(fim ?? 1e9, 8);
    if (f < inicio) return null;
    const flut = Math.sin((f - inicio) / 26 + random(seed) * 6) * 12;
    return (
      <div style={{ position: "absolute", left: x, top: y + (1 - k) * 40 + flut, width: w, height: h, opacity: k * sai, background: fundo,
        borderRadius: 10, overflow: "hidden", border: borda ? `1px solid ${C.apoio}` : "none",
        boxShadow: "0 30px 60px rgba(0,0,0,0.18), 0 6px 14px rgba(0,0,0,0.12)",
        transform: `perspective(1400px) rotateY(${rotY * (0.6 + 0.4 * k) + Math.sin((f - inicio) / 40) * 3}deg) rotateZ(${rotZ}deg) scale(${0.94 + 0.06 * k})` }}>
        {children}
      </div>
    );
  };

/* ------------------------------------------------------------------ tipografia */
/** Palavra-chave com caixa chapada que entra no tempo exato da fala. tom: tinta | ambar | netflix */
export const Destaque: React.FC<{ texto: string; inicio: number; tom?: "tinta" | "ambar" | "netflix"; size?: number; style?: React.CSSProperties }> =
  ({ texto, inicio, tom = "tinta", size = 64, style }) => {
    const f = useCurrentFrame();
    const caixa = interpolate(f - inicio, [0, 6], [0, 1], clamp);
    const sobe = interpolate(f - inicio, [0, 7], [18, 0], { ...clamp, easing: easeOut });
    if (f < inicio) return null;
    const bg = tom === "netflix" ? C.netflix : tom === "ambar" ? C.ambar : C.tinta;
    const fg = tom === "ambar" ? C.tinta : C.branco;
    return (
      <span style={{ display: "inline-block", fontFamily: FONT, fontWeight: 800, fontSize: size, lineHeight: 1, textTransform: "uppercase",
        padding: `${size * 0.12}px ${size * 0.22}px ${size * 0.08}px`, color: caixa > 0.4 ? fg : C.tinta,
        background: `color-mix(in srgb, ${bg} ${Math.round(caixa * 100)}%, transparent)`, transform: `translateY(${sobe}px)`, ...style }}>
        {texto}
      </span>
    );
  };

/** Título em dois pesos: primeira parte em tinta, segunda em cinza claro e fina. Cada parte entra na sua palavra. */
export const TituloDoisPesos: React.FC<{ a: string; b: string; ta: number; tb: number; size?: number; alinhar?: "left" | "center" }> =
  ({ a, b, ta, tb, size = 92, alinhar = "left" }) => {
    const ka = useEntrada(ta, 8), kb = useEntrada(tb, 8);
    return (
      <div style={{ fontFamily: FONT, fontSize: size, lineHeight: 0.98, letterSpacing: -1.5, textAlign: alinhar }}>
        <div style={{ fontWeight: 700, color: C.tinta, opacity: ka, transform: `translateY(${(1 - ka) * 24}px)` }}>{a}</div>
        <div style={{ fontWeight: 400, color: "#A6A6A6", opacity: kb, transform: `translateY(${(1 - kb) * 24}px)` }}>{b}</div>
      </div>
    );
  };

/** Número que conta até o valor, com dígitos tabulares. */
export const Contador: React.FC<{ valor: number; inicio: number; dur?: number; size?: number; sufixo?: string; cor?: string }> =
  ({ valor, inicio, dur = 24, size = 120, sufixo = "", cor = C.tinta }) => {
    const f = useCurrentFrame();
    const k = interpolate(f - inicio, [0, dur], [0, 1], { ...clamp, easing: easeOut });
    if (f < inicio) return null;
    // o número verdadeiro é datilografado; as casas que faltam aparecem como traço (nunca um número intermediário falso)
    const txt = valor.toLocaleString("pt-BR") + sufixo;
    const nVis = Math.max(1, Math.ceil(txt.length * k));
    return (
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, color: cor, letterSpacing: -2, fontVariantNumeric: "tabular-nums", lineHeight: 1, whiteSpace: "nowrap" }}>
        {txt.split("").map((ch, i) => i < nVis ? <span key={i}>{ch}</span>
          : <span key={i} style={{ color: "transparent", borderBottom: `${Math.round(size * 0.06)}px solid ${C.apoio}`, margin: "0 0.04em" }}>{ch}</span>)}
      </div>
    );
  };

/** Terminal que digita (âmbar sobre preto), com cursor piscando. */
export const Terminal: React.FC<{ texto: string; inicio: number; cps?: number; size?: number; w: number }> = ({ texto, inicio, cps = 18, size = 40, w }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = Math.max(0, Math.floor(((f - inicio) / fps) * cps));
  const cursor = Math.floor(f / 8) % 2 === 0;
  return (
    <div style={{ width: w, background: "#111", border: "2px solid #333", borderRadius: 8, padding: "22px 26px", boxSizing: "border-box",
      fontFamily: MONO, fontSize: size, color: C.ambar, letterSpacing: 2, textTransform: "uppercase", minHeight: size * 2.4 }}>
      <span style={{ opacity: 0.6 }}>&gt; </span>{texto.slice(0, n)}<span style={{ opacity: cursor ? 1 : 0 }}>▌</span>
    </div>
  );
};

/** Cursor de mouse que vai até um ponto e clica (com anel). */
export const Cursor: React.FC<{ de: [number, number]; para: [number, number]; inicio: number; clique: number }> = ({ de, para, inicio, clique }) => {
  const f = useCurrentFrame();
  const k = interpolate(f, [inicio, clique - 2], [0, 1], { ...clamp, easing: easeInOut });
  const x = de[0] + (para[0] - de[0]) * k, y = de[1] + (para[1] - de[1]) * k;
  const anel = interpolate(f - clique, [0, 10], [0, 1], clamp);
  const aperta = interpolate(f - clique, [0, 2, 5], [1, 0.85, 1], clamp);
  return (
    <>
      {f >= clique && anel < 1 && <div style={{ position: "absolute", left: para[0] - 40 * anel, top: para[1] - 40 * anel, width: 80 * anel, height: 80 * anel,
        borderRadius: "50%", border: `4px solid ${C.ambar}`, opacity: 1 - anel }} />}
      <svg width="54" height="64" viewBox="0 0 24 28" style={{ position: "absolute", left: x, top: y, transform: `scale(${aperta})`, transformOrigin: "0 0",
        filter: "drop-shadow(3px 5px 4px rgba(0,0,0,0.35))" }}>
        <path d="M2 1 L2 22 L7.5 17 L11 25 L14.5 23.5 L11 15.5 L18.5 15.5 Z" fill="#fff" stroke={C.tinta} strokeWidth="1.6" strokeLinejoin="round" />
      </svg>
    </>
  );
};

/* ------------------------------------------------------------------ página editorial */
/** Camada fixa: etiqueta de capítulo (faixa central), contador de arquivo e marca. */
export const PaginaEditorial: React.FC<{ capitulo: string; arquivo: string; escura?: boolean }> = ({ capitulo, arquivo, escura }) => {
  const k = useEntrada(0, 10);
  const cor = escura ? "#E6E6E6" : C.tinta;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: k }}>
      <div style={{ position: "absolute", left: FAIXA.x + 24, top: 44, display: "flex", alignItems: "center", gap: 10, fontFamily: MONO, fontSize: 17,
        letterSpacing: 2.5, color: cor, textTransform: "uppercase" }}>
        <span style={{ width: 9, height: 9, borderRadius: 5, background: C.ambar, display: "inline-block" }} />{capitulo}
      </div>
      <div style={{ position: "absolute", left: FAIXA.x + FAIXA.w - 24 - 200, width: 200, top: 44, textAlign: "right", fontFamily: MONO, fontSize: 15,
        letterSpacing: 2, color: escura ? "#AAA" : C.secundario }}>{arquivo}</div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 1020, textAlign: "center", fontFamily: MONO, fontSize: 13, letterSpacing: 4,
        color: escura ? "#777" : "#B0B0B0" }}>BRAND BY IZOTON</div>
    </AbsoluteFill>
  );
};

/** Dossiê lateral: código, data e fonte do bloco, escrevendo-se linha a linha. */
export const Dossie: React.FC<{ linhas: string[]; lado: "esq" | "dir"; inicio: number; escuro?: boolean; top?: number }> = ({ linhas, lado, inicio, escuro, top = 300 }) => {
  const f = useCurrentFrame();
  const x = lado === "esq" ? 90 : 1920 - 90 - 380;
  return (
    <div style={{ position: "absolute", left: x, top, width: 380, fontFamily: MONO, fontSize: 17, lineHeight: 1.7, letterSpacing: 1.5,
      color: escuro ? "#CFCFCF" : C.tinta, textAlign: lado === "esq" ? "left" : "right" }}>
      {linhas.map((l, i) => {
        const n = Math.max(0, Math.floor((f - inicio - i * 10) * 1.6));
        return <div key={i} style={{ opacity: n > 0 ? 1 : 0, borderBottom: `1px solid ${escuro ? "#444" : C.apoio}`, paddingBottom: 4, marginBottom: 6 }}>{l.slice(0, n)}</div>;
      })}
    </div>
  );
};

/** Carimbo seco que cai com escala. */
export const Carimbo3: React.FC<{ texto: string; inicio: number; x: number; y: number; rot?: number; size?: number; cor?: string }> =
  ({ texto, inicio, x, y, rot = -4, size = 22, cor = C.tinta }) => {
    const f = useCurrentFrame();
    const { fps } = useVideoConfig();
    if (f < inicio) return null;
    const s = spring({ frame: f - inicio, fps, config: { damping: 11, mass: 0.6 } });
    return (
      <div style={{ position: "absolute", left: x, top: y, fontFamily: MONO, fontWeight: 600, fontSize: size, letterSpacing: 3, color: cor,
        border: `3px solid ${cor}`, padding: "6px 14px", textTransform: "uppercase", transform: `rotate(${rot}deg) scale(${interpolate(s, [0, 1], [1.8, 1])})`,
        opacity: Math.min(1, s * 2), background: "rgba(255,255,255,0.85)", whiteSpace: "nowrap" }}>{texto}</div>
    );
  };
