import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";

export type Palavra = { text: string; start: number; end: number };

/**
 * Legenda de 1 a 3 palavras por vez, centralizada no meio da tela.
 * Fonte branca grossa e arredondada (Baloo 2 ExtraBold), contorno preto ~6px e sombra.
 */
export const Legenda: React.FC<{ palavras: Palavra[]; y?: number; max?: number }> = ({ palavras, y = 900, max = 3 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const grupos: Palavra[][] = [];
  let cur: Palavra[] = [];
  palavras.forEach((w, i) => {
    const prev = palavras[i - 1];
    const quebra = prev && (w.start - prev.end > 0.28 || /[.,!?:;…]$/.test(prev.text));
    if (cur.length && (cur.length >= max || quebra)) {
      grupos.push(cur);
      cur = [];
    }
    cur.push(w);
  });
  if (cur.length) grupos.push(cur);

  const idx = grupos.findIndex((g, i) => {
    const next = grupos[i + 1];
    const fim = next ? Math.min(next[0].start, g[g.length - 1].end + 0.5) : g[g.length - 1].end + 0.6;
    return t >= g[0].start - 0.04 && t < fim;
  });
  if (idx < 0) return null;
  const g = grupos[idx];
  const k = interpolate(t - g[0].start, [-0.04, 0.07], [0.7, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const texto = g.map((w) => w.text).join(" ");
  const longo = texto.length > 16;
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: y, display: "flex", justifyContent: "center", pointerEvents: "none" }}>
      <div
        style={{
          fontFamily: "'Baloo 2', Nunito, Arial, sans-serif",
          fontWeight: 800,
          fontSize: longo ? 96 : 118,
          lineHeight: 1.0,
          color: "#FFFFFF",
          textAlign: "center",
          WebkitTextStroke: "12px #000",
          paintOrder: "stroke fill",
          textShadow: "0 10px 0 rgba(0,0,0,0.55), 0 14px 22px rgba(0,0,0,0.45)",
          scale: `${k}`,
          letterSpacing: 1,
        }}
      >
        {texto}
      </div>
    </div>
  );
};
