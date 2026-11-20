import React from "react";
import { useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Word } from "../lib/episode";
import { SANS } from "../lib/fonts";

/** Legenda palavra por palavra, em blocos curtos, palavra atual destacada. Faixa central-inferior (fora da UI do TikTok/Reels). */
export const Captions: React.FC<{ words: Word[]; highlight: string; color: string; bg: string; maxWords?: number; top?: number }> = ({ words, highlight, color, bg, maxWords = 4, top = 1330 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;

  // agrupa em blocos: quebra por pontuação, mudança de cena ou maxWords
  const groups: Word[][] = [];
  let cur: Word[] = [];
  words.forEach((w, i) => {
    cur.push(w);
    const next = words[i + 1];
    const punct = /[.,:;!?…]$/.test(w.text);
    if (!next || cur.length >= maxWords || next.scene !== w.scene || punct || next.start - w.end > 0.35) {
      // não termina bloco em artigo/preposição curta ("o", "a", "de"): joga para o próximo
      const hard = !next || next.scene !== w.scene || punct;
      if (!hard && cur.length > 1 && w.text.length <= 3) {
        cur.pop();
        groups.push(cur);
        cur = [w];
      } else {
        groups.push(cur);
        cur = [];
      }
    }
  });
  const g = groups.find((gr, i) => t >= gr[0].start - 0.05 && t < (groups[i + 1]?.[0].start ?? gr[gr.length - 1].end + 0.6) - 0.05 && t < gr[gr.length - 1].end + 0.6);
  if (!g) return null;
  const gStart = Math.round(g[0].start * fps);
  const inP = spring({ frame: f - gStart, fps, config: { damping: 14, stiffness: 220 } });
  return (
    <div style={{ position: "absolute", top, left: 90, right: 150, display: "flex", justifyContent: "center", pointerEvents: "none" }}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", rowGap: 4, background: bg, padding: "14px 28px", borderRadius: 18, transform: `scale(${0.85 + inP * 0.15})`, boxShadow: "0 8px 0 rgba(0,0,0,0.3)" }}>
        {g.map((w, i) => {
          const active = t >= w.start && (t < w.end + 0.08 || (i === g.length - 1 && t < w.end + 0.6));
          const said = t >= w.start;
          return (
            <span key={i} style={{ fontFamily: SANS, fontWeight: 900, fontSize: 64, lineHeight: 1.15, color: active ? highlight : color, opacity: said ? 1 : 0.55, transform: `scale(${active ? 1.08 : 1})`, display: "inline-block", textTransform: "uppercase", margin: "0 9px" }}>
              {w.text.replace(/[,;:]$/, "")}
            </span>
          );
        })}
      </div>
    </div>
  );
};
