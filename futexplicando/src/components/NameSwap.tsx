import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { TITLE, SANS } from "../lib/fonts";
import { shake } from "./motion";
import { Sfx } from "./Sfx";

type Props = {
  first: string; // "PALESTRA ITALIA"
  strikeWord: string; // "ITALIA"
  second: string; // "PALESTRA DE SÃO PAULO"
  final: string; // "PALMEIRAS"
  strikeAt: number; // marcador risca a palavra
  swap1At: number; // entra o 2º nome
  swap2At?: number; // vira o nome final (opcional: pode acontecer em outra cena)
  startStage?: 0 | 1; // 1 = já começa no 2º nome
  crest?: string;
  finalSub?: string;
  colors: { paper: string; ink: string; primary: string; secondary: string; accent: string };
  sfx: { tear?: string; whoosh?: string; impact?: string; stamp?: string };
};

const clip = (side: "l" | "r") => {
  // linha de rasgo irregular
  const pts = [[52, 0], [47, 12], [55, 25], [46, 38], [53, 50], [45, 63], [54, 76], [48, 88], [51, 100]];
  const path = pts.map(([x, y]) => `${x}% ${y}%`).join(",");
  const rev = [...pts].reverse().map(([x, y]) => `${x}% ${y}%`).join(",");
  return side === "l" ? `polygon(0% 0%, ${path}, 0% 100%)` : `polygon(100% 0%, 100% 100%, ${rev})`;
};

/** Cena-assinatura: PALESTRA ITALIA → risca/rasga ITALIA → PALESTRA DE SÃO PAULO → PALMEIRAS. */
export const NameSwap: React.FC<Props> = (p) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { paper, ink, primary, secondary, accent } = p.colors;
  const prefix = p.first.replace(p.strikeWord, "").trim(); // PALESTRA
  const rest = p.second.replace(prefix, "").trim(); // DE SÃO PAULO
  const stage1 = p.startStage === 1;

  // risco de marcador
  const strikeP = stage1 ? 1 : interpolate(f, [p.strikeAt, p.strikeAt + 7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  // rasgo
  const tearAt = p.strikeAt + 16;
  const tt = stage1 ? 999 : f - tearAt;
  const tearOpen = interpolate(tt, [0, 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fall = tt > 4 ? Math.pow((tt - 4) / fps, 2) * 3200 : 0;
  // 2º nome
  const in1 = stage1 ? 1 : spring({ frame: f - p.swap1At, fps, config: { damping: 11, stiffness: 160 } });
  // virada final
  const s2 = p.swap2At ?? 99999;
  const flipOut = interpolate(f, [s2, s2 + 6], [0, 90], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.quad) });
  const flipIn = spring({ frame: f - (s2 + 6), fps, config: { damping: 9, stiffness: 140 } });
  const crestIn = spring({ frame: f - (s2 + 14), fps, config: { damping: 10, stiffness: 120 } });
  const sk = shake(f, p.swap1At, 10, 8);
  const sk2 = shake(f, s2 + 8, 24, 14);

  const board: React.CSSProperties = {
    position: "absolute", left: 70, right: 70, top: 0, background: paper, border: `10px solid ${ink}`, borderRadius: 14,
    boxShadow: `16px 16px 0 ${ink}`, padding: "40px 30px 50px", display: "flex", flexDirection: "column", alignItems: "center",
  };
  const showFinal = f >= s2 + 6;

  return (
    <div style={{ position: "relative", width: 1080, height: 900, perspective: 1600 }}>
      {!showFinal && (
        <div style={{ ...board, transform: `rotateX(${flipOut}deg) translate(${sk.x}px,${sk.y}px)`, transformOrigin: "50% 50%" }}>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 34, letterSpacing: 10, color: ink, opacity: 0.7 }}>NOME DO CLUBE</div>
          <div style={{ fontFamily: TITLE, fontSize: 210, lineHeight: 1.05, color: primary }}>{prefix}</div>
          <div style={{ position: "relative", height: in1 > 0.01 && tt > 10 ? 0 : 230, width: "100%", display: "flex", justifyContent: "center" }}>
            {tt < 60 && (
              <div style={{ position: "relative", fontFamily: TITLE, fontSize: 210, lineHeight: 1.05, color: accent }}>
                {(["l", "r"] as const).map((side) => (
                  <div
                    key={side}
                    style={{
                      position: side === "l" ? "relative" : "absolute", top: 0, left: 0, clipPath: clip(side),
                      transform: `translate(${(side === "l" ? -1 : 1) * tearOpen * 26}px, ${fall}px) rotate(${(side === "l" ? -1 : 1) * (tearOpen * 4 + fall / 40)}deg)`,
                      transformOrigin: side === "l" ? "0% 0%" : "100% 0%",
                    }}
                  >
                    {p.strikeWord}
                    <svg style={{ position: "absolute", left: -30, top: 80, overflow: "visible" }} width="100%" height="80">
                      <path d={`M0 40 C 200 10, 400 70, 720 30`} stroke={ink} strokeWidth={46} strokeLinecap="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - strikeP} />
                    </svg>
                  </div>
                ))}
              </div>
            )}
          </div>
          {in1 > 0.01 && (
            <div style={{ display: "flex", gap: 26, flexWrap: "wrap", justifyContent: "center" }}>
              {rest.split(" ").map((w, i) => {
                const wi = stage1 ? 1 : spring({ frame: f - p.swap1At - i * 3, fps, config: { damping: 10, stiffness: 180 } });
                return (
                  <span key={i} style={{ fontFamily: TITLE, fontSize: 150, lineHeight: 1.05, color: ink, display: "inline-block", transform: `translateY(${(1 - wi) * -260}px) scale(${0.6 + wi * 0.4})`, opacity: Math.min(1, wi * 2) }}>
                    {w}
                  </span>
                );
              })}
            </div>
          )}
        </div>
      )}
      {showFinal && (
        <div style={{ ...board, background: primary, transform: `rotateX(${(1 - flipIn) * -90}deg) translate(${sk2.x}px,${sk2.y}px)`, paddingTop: 230 }}>
          {p.crest && (
            <Img src={staticFile(p.crest)} style={{ position: "absolute", top: -150, width: 340, height: 340, objectFit: "contain", transform: `scale(${crestIn}) rotate(${(1 - crestIn) * -40}deg)`, filter: "drop-shadow(0 12px 0 rgba(0,0,0,0.35))" }} />
          )}
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 34, letterSpacing: 10, color: paper, opacity: 0.85 }}>NOME DO CLUBE</div>
          <div style={{ fontFamily: TITLE, fontSize: 240, lineHeight: 1.05, color: paper, textShadow: `10px 10px 0 ${ink}` }}>{p.final}</div>
          {p.finalSub && <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 40, color: secondary, background: ink, padding: "6px 20px", letterSpacing: 4 }}>{p.finalSub}</div>}
        </div>
      )}
      {!stage1 && <Sfx src={p.sfx.tear} at={tearAt - 2} volumeDb={2} />}
      {!stage1 && <Sfx src={p.sfx.whoosh} at={p.strikeAt - 3} volumeDb={-6} />}
      {!stage1 && <Sfx src={p.sfx.stamp} at={p.swap1At} volumeDb={-4} />}
      {p.swap2At !== undefined && <Sfx src={p.sfx.whoosh} at={s2} volumeDb={-2} />}
      {p.swap2At !== undefined && <Sfx src={p.sfx.impact} at={s2 + 8} volumeDb={-6} durationInFrames={90} />}
    </div>
  );
};
