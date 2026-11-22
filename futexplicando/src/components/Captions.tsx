import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { C, INTER } from "../theme";

export type CaptionWord = { text: string; start: number; end: number };

/**
 * Legendas palavra por palavra (Inter). Agrupa em blocos de até `maxWords` palavras
 * e destaca a palavra falada com caixa vermelha.
 */
export const Captions: React.FC<{
  words: CaptionWord[];
  hide?: [number, number][];
  maxWords?: number;
  y?: number;
  dark?: boolean;
}> = ({ words, hide = [], maxWords = 3, y = 1395, dark = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (hide.some(([a, b]) => t >= a && t < b)) return null;

  // monta páginas: quebra em pausas > 0.35s, pontuação ou maxWords
  const pages: CaptionWord[][] = [];
  let cur: CaptionWord[] = [];
  words.forEach((w, i) => {
    const prev = words[i - 1];
    const gap = prev ? w.start - prev.end : 0;
    const punct = prev ? /[.,!?:;…]$/.test(prev.text) : false;
    if (cur.length && (cur.length >= maxWords || gap > 0.35 || punct)) {
      pages.push(cur);
      cur = [];
    }
    cur.push(w);
  });
  if (cur.length) pages.push(cur);

  const page = pages.find((p, i) => {
    const next = pages[i + 1];
    const endT = next ? Math.min(next[0].start, p[p.length - 1].end + 0.6) : p[p.length - 1].end + 0.6;
    return t >= p[0].start - 0.05 && t < endT;
  });
  if (!page) return null;
  const pageStart = page[0].start;
  const pop = interpolate(t - pageStart, [-0.05, 0.08], [0.85, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        top: y,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: "6px 14px",
        scale: `${pop}`,
      }}
    >
      {page.map((w, i) => {
        const active = t >= w.start - 0.03 && t < (page[i + 1]?.start ?? w.end + 0.6);
        return (
          <span
            key={i}
            style={{
              fontFamily: INTER,
              fontWeight: 900,
              fontSize: 66,
              letterSpacing: -1,
              textTransform: "uppercase",
              padding: "2px 16px 6px",
              borderRadius: 14,
              color: active ? C.white : dark ? C.white : C.black,
              background: active ? C.red : "transparent",
              rotate: active ? "-2deg" : "0deg",
              textShadow: active
                ? `3px 3px 0 ${C.black}`
                : dark
                  ? `0 0 12px rgba(0,0,0,0.9), 3px 3px 0 ${C.black}`
                  : `0 0 10px ${C.white}, 0 0 4px ${C.white}`,
              boxShadow: active ? `5px 5px 0 ${C.black}` : "none",
            }}
          >
            {w.text}
          </span>
        );
      })}
    </div>
  );
};
