import React from "react";
import { useCurrentFrame } from "remotion";
import { ANTON, C } from "../theme";
import { rand } from "./time";

const CHARS = " ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÉÍÓÚÇ0123456789";

/**
 * Letreiro de placas giratórias (split-flap). Cada linha troca de `from` para `to`
 * a partir de `flipAt` (frame relativo), com cada placa girando por letras aleatórias.
 * `steps` define uma sequência de textos: [{at, lines}] (frames relativos).
 */
export const SplitFlap: React.FC<{
  steps: { at: number; lines: string[] }[];
  cols?: number;
  tile?: number;
  color?: string;
  textColor?: string;
  style?: React.CSSProperties;
}> = ({ steps, cols = 15, tile = 62, color = C.black, textColor = C.white, style }) => {
  const frame = useCurrentFrame();
  const rows = Math.max(...steps.map((s) => s.lines.length));
  const pad = (s: string) => {
    const left = Math.floor((cols - s.length) / 2);
    return (" ".repeat(Math.max(0, left)) + s).padEnd(cols, " ").slice(0, cols);
  };
  const stepIdx = steps.reduce((acc, s, i) => (frame >= s.at ? i : acc), 0);
  const cur = steps[stepIdx];
  const prev = steps[Math.max(0, stepIdx - 1)];
  const h = tile * 1.38;
  return (
    <div style={{ display: "inline-flex", flexDirection: "column", gap: tile * 0.12, padding: tile * 0.22, background: "#1d1d1d", borderRadius: tile * 0.18, boxShadow: `12px 14px 0 ${C.red}`, ...style }}>
      {Array.from({ length: rows }).map((_, r) => {
        const target = pad(cur.lines[r] ?? "");
        const before = pad(prev.lines[r] ?? "");
        return (
          <div key={r} style={{ display: "flex", gap: tile * 0.08 }}>
            {target.split("").map((ch, c) => {
              const delay = Math.floor(rand(r * 31 + c * 7 + stepIdx) * 10) + c * 0.6;
              const spins = 4 + Math.floor(rand(c * 13 + r + stepIdx * 3) * 6);
              const t = frame - cur.at - delay; // frames desde o início desta placa
              let shown = ch;
              let flip = 0;
              if (stepIdx > 0 && before[c] !== ch) {
                if (t < 0) shown = before[c];
                else if (t < spins * 2) {
                  shown = CHARS[Math.floor(rand(c * 97 + r * 11 + Math.floor(t / 2)) * CHARS.length)];
                  flip = (t % 2) / 2;
                }
              }
              return (
                <div
                  key={c}
                  style={{
                    position: "relative",
                    width: tile,
                    height: h,
                    background: `linear-gradient(180deg, #2b2b2b 0%, ${color} 49%, #000 50%, #262626 51%, #1a1a1a 100%)`,
                    borderRadius: tile * 0.1,
                    overflow: "hidden",
                    boxShadow: "inset 0 2px 0 rgba(255,255,255,0.08), inset 0 -3px 6px rgba(0,0,0,0.6)",
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      inset: 0,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontFamily: ANTON,
                      fontSize: tile * 1.02,
                      color: textColor,
                      lineHeight: 1,
                      scale: `1 ${1 - flip * 0.9}`,
                    }}
                  >
                    {shown}
                  </div>
                  <div style={{ position: "absolute", left: 0, right: 0, top: h / 2 - 1, height: 2, background: "rgba(0,0,0,0.85)" }} />
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

/** Porco estilizado (desenho próprio) usado na cena do mascote. */
export const Pig: React.FC<{ size: number; color?: string }> = ({ size, color = "#F2A7B5" }) => (
  <svg width={size} height={size} viewBox="0 0 200 200">
    <path d="M45 62 L30 18 L78 44 Z" fill={color} stroke="#111" strokeWidth="6" strokeLinejoin="round" />
    <path d="M155 62 L170 18 L122 44 Z" fill={color} stroke="#111" strokeWidth="6" strokeLinejoin="round" />
    <circle cx="100" cy="105" r="78" fill={color} stroke="#111" strokeWidth="7" />
    <ellipse cx="100" cy="128" rx="36" ry="26" fill="#E98A9E" stroke="#111" strokeWidth="6" />
    <ellipse cx="88" cy="128" rx="6" ry="10" fill="#111" />
    <ellipse cx="112" cy="128" rx="6" ry="10" fill="#111" />
    <circle cx="70" cy="88" r="9" fill="#111" />
    <circle cx="130" cy="88" r="9" fill="#111" />
    <circle cx="73" cy="85" r="3" fill="#fff" />
    <circle cx="133" cy="85" r="3" fill="#fff" />
    <path d="M60 70 Q70 62 82 68" stroke="#111" strokeWidth="5" fill="none" strokeLinecap="round" />
    <path d="M118 68 Q130 62 140 70" stroke="#111" strokeWidth="5" fill="none" strokeLinecap="round" />
  </svg>
);
