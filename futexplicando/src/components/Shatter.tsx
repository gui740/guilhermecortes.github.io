import React, { useMemo } from "react";
import { Img, staticFile } from "remotion";
import { rand } from "./time";

type Tri = { pts: [number, number][]; cx: number; cy: number; seed: number };

const buildTris = (cols: number, rows: number, seed: number): Tri[] => {
  const v: [number, number][][] = [];
  for (let r = 0; r <= rows; r++) {
    v.push([]);
    for (let c = 0; c <= cols; c++) {
      const edge = r === 0 || c === 0 || r === rows || c === cols;
      const jx = edge ? 0 : (rand(seed + r * 31 + c * 7) - 0.5) * (70 / cols);
      const jy = edge ? 0 : (rand(seed + r * 13 + c * 17) - 0.5) * (70 / rows);
      v[r].push([(c / cols) * 100 + jx, (r / rows) * 100 + jy]);
    }
  }
  const tris: Tri[] = [];
  let k = 0;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const a = v[r][c], b = v[r][c + 1], d = v[r + 1][c], e = v[r + 1][c + 1];
      const flip = rand(seed + k * 3) > 0.5;
      const t1 = flip ? [a, b, e] : [a, b, d];
      const t2 = flip ? [a, e, d] : [b, e, d];
      for (const t of [t1, t2]) {
        const cx = (t[0][0] + t[1][0] + t[2][0]) / 3;
        const cy = (t[0][1] + t[1][1] + t[2][1]) / 3;
        tris.push({ pts: t as [number, number][], cx, cy, seed: seed + k++ * 11 });
      }
    }
  }
  return tris;
};

/**
 * Escudo que racha (crack 0..1) e se despedaça (burst 0..1).
 * Para remontar, basta animar burst de 1 -> 0.
 */
export const ShatterCrest: React.FC<{
  src: string;
  size: number;
  crack: number;
  burst: number;
  seed?: number;
  filter?: string;
}> = ({ src, size, crack, burst, seed = 5, filter }) => {
  const tris = useMemo(() => buildTris(4, 5, seed), [seed]);
  const intact = burst <= 0.0001;
  return (
    <div style={{ position: "relative", width: size, height: size, filter }}>
      {intact ? (
        <Img src={staticFile(src)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain" }} />
      ) : (
        tris.map((t, i) => {
          const dx = (t.cx - 50) / 50;
          const dy = (t.cy - 50) / 50;
          const sp = 0.6 + rand(t.seed) * 0.8;
          const tx = dx * burst * 520 * sp;
          const ty = dy * burst * 380 * sp + burst * burst * 1300 * (0.6 + rand(t.seed + 1));
          const rot = (rand(t.seed + 2) - 0.5) * 260 * burst;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                inset: 0,
                clipPath: `polygon(${t.pts.map((p) => `${p[0]}% ${p[1]}%`).join(",")})`,
                translate: `${tx}px ${ty}px`,
                rotate: `${rot}deg`,
                transformOrigin: `${t.cx}% ${t.cy}%`,
              }}
            >
              <Img src={staticFile(src)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain" }} />
            </div>
          );
        })
      )}
      {/* rachaduras */}
      {crack > 0 && burst < 0.05 ? (
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", maskImage: `url(${staticFile(src)})`, maskSize: "contain", maskRepeat: "no-repeat", maskPosition: "center" }}>
          {tris.slice(0, Math.ceil(tris.length * crack)).map((t, i) => (
            <polyline
              key={i}
              points={t.pts.map((p) => p.join(",")).join(" ")}
              fill="none"
              stroke="#111"
              strokeWidth={0.7}
              strokeLinejoin="round"
              opacity={0.85}
            />
          ))}
        </svg>
      ) : null}
    </div>
  );
};
