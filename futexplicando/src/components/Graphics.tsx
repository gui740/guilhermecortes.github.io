import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ANTON, BEBAS, C, INTER } from "../theme";
import { rand } from "./time";

/** Título grande "Hook": linhas que batem na tela uma a uma. */
export const Hook: React.FC<{
  lines: string[];
  startFrame: number;
  stagger?: number;
  size?: number;
  color?: string;
  accentIndex?: number;
  accent?: string;
  style?: React.CSSProperties;
}> = ({ lines, startFrame, stagger = 6, size = 150, color = C.black, accentIndex = -1, accent = C.red, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", ...style }}>
      {lines.map((l, i) => {
        const p = spring({ frame: frame - startFrame - i * stagger, fps, config: { damping: 11, stiffness: 220, mass: 0.7 } });
        return (
          <div
            key={i}
            style={{
              fontFamily: ANTON,
              fontSize: size,
              lineHeight: 0.98,
              color: i === accentIndex ? accent : color,
              textTransform: "uppercase",
              opacity: p > 0.01 ? 1 : 0,
              scale: `${interpolate(p, [0, 1], [2.2, 1])}`,
              rotate: `${interpolate(p, [0, 1], [i % 2 ? 6 : -6, i % 2 ? 1 : -1.2])}deg`,
              textShadow: i === accentIndex ? "none" : `6px 6px 0 ${i === accentIndex ? C.black : "rgba(227,6,19,0.9)"}`,
              whiteSpace: "nowrap",
            }}
          >
            {l}
          </div>
        );
      })}
    </div>
  );
};

/** Carimbo de ano/data. */
export const YearStamp: React.FC<{ text: string; startFrame: number; color?: string; size?: number; rotate?: number; sub?: string }> = ({
  text,
  startFrame,
  color = C.red,
  size = 170,
  rotate = -8,
  sub,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - startFrame;
  const p = spring({ frame: f, fps, config: { damping: 9, stiffness: 300, mass: 0.6 } });
  if (f < 0) return null;
  return (
    <div
      style={{
        display: "inline-flex",
        flexDirection: "column",
        alignItems: "center",
        border: `${size * 0.06}px solid ${color}`,
        borderRadius: size * 0.08,
        padding: `${size * 0.05}px ${size * 0.18}px`,
        color,
        rotate: `${rotate}deg`,
        scale: `${interpolate(p, [0, 1], [3, 1])}`,
        opacity: interpolate(f, [0, 3], [0, 0.95], { extrapolateRight: "clamp" }),
        maskImage:
          "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.08' numOctaves='3' seed='4'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -3 2.4'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>\")",
        maskSize: "300px 300px",
      }}
    >
      <div style={{ fontFamily: ANTON, fontSize: size, lineHeight: 1.05, letterSpacing: size * 0.02 }}>{text}</div>
      {sub ? <div style={{ fontFamily: BEBAS, fontSize: size * 0.32, letterSpacing: size * 0.04, marginTop: -size * 0.04 }}>{sub}</div> : null}
    </div>
  );
};

/** Campo de futebol desenhado em traço (fundo). */
export const Pitch: React.FC<{ color?: string; opacity?: number; draw?: number }> = ({ color = C.red, opacity = 0.18, draw = 1 }) => {
  const len = 4000;
  const common = { fill: "none", stroke: color, strokeWidth: 6, strokeDasharray: len, strokeDashoffset: len * (1 - draw) } as const;
  return (
    <AbsoluteFill style={{ opacity }}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%">
        <rect x={90} y={160} width={900} height={1600} {...common} />
        <line x1={90} y1={960} x2={990} y2={960} {...common} />
        <circle cx={540} cy={960} r={170} {...common} />
        <rect x={290} y={160} width={500} height={260} {...common} />
        <rect x={290} y={1500} width={500} height={260} {...common} />
        <rect x={420} y={160} width={240} height={100} {...common} />
        <rect x={420} y={1660} width={240} height={100} {...common} />
        <path d="M 420 420 A 150 150 0 0 0 660 420" {...common} />
        <path d="M 420 1500 A 150 150 0 0 1 660 1500" {...common} />
      </svg>
    </AbsoluteFill>
  );
};

/** Linha do tempo horizontal com marcos. */
export const Timeline: React.FC<{
  items: { label: string; sub?: string; at: number }[];
  width?: number;
  color?: string;
  textColor?: string;
}> = ({ items, width = 860, color = C.red, textColor = C.black }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const first = Math.min(...items.map((i) => i.at));
  const lineP = interpolate(frame, [first - 6, first + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "relative", width, height: 230 }}>
      <div style={{ position: "absolute", left: 0, top: 70, height: 10, width: width * lineP, background: color, borderRadius: 5 }} />
      {items.map((it, i) => {
        const x = items.length === 1 ? width / 2 : (i / (items.length - 1)) * (width - 80) + 40;
        const p = spring({ frame: frame - it.at, fps, config: { damping: 10, stiffness: 240 } });
        return (
          <div key={i} style={{ position: "absolute", left: x, top: 0, translate: "-50% 0", textAlign: "center", opacity: p > 0.01 ? 1 : 0 }}>
            <div
              style={{
                width: 46,
                height: 46,
                borderRadius: "50%",
                background: color,
                border: `8px solid ${textColor}`,
                margin: "52px auto 10px",
                scale: `${p}`,
              }}
            />
            <div style={{ fontFamily: ANTON, fontSize: 84, color: textColor, lineHeight: 1, scale: `${interpolate(p, [0, 1], [1.6, 1])}` }}>{it.label}</div>
            {it.sub ? <div style={{ fontFamily: BEBAS, fontSize: 40, color, letterSpacing: 3 }}>{it.sub}</div> : null}
          </div>
        );
      })}
    </div>
  );
};

/** Número gigante que "bate" na tela e (opcionalmente) conta. */
export const StatSlam: React.FC<{
  value: number;
  startFrame: number;
  countFrames?: number;
  label: string;
  size?: number;
  color?: string;
  labelColor?: string;
  suffix?: string;
}> = ({ value, startFrame, countFrames = 0, label, size = 520, color = C.red, labelColor = C.black, suffix = "" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - startFrame;
  const p = spring({ frame: f, fps, config: { damping: 9, stiffness: 260, mass: 0.7 } });
  const n = countFrames
    ? Math.round(value * interpolate(f, [0, countFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) }))
    : value;
  if (f < 0) return null;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div
        style={{
          fontFamily: ANTON,
          fontSize: size,
          lineHeight: 0.9,
          color,
          scale: `${interpolate(p, [0, 1], [2.6, 1])}`,
          textShadow: `14px 14px 0 ${C.black}`,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {n}
        {suffix}
      </div>
      <div
        style={{
          fontFamily: ANTON,
          fontSize: size * 0.17,
          color: labelColor,
          letterSpacing: 2,
          marginTop: size * 0.03,
          opacity: interpolate(f, [4, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          translate: `0 ${interpolate(f, [4, 12], [40, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px`,
        }}
      >
        {label}
      </div>
    </div>
  );
};

/** Selo @futexplicando (canto superior esquerdo). */
export const Seal: React.FC<{ handle: string; dark?: boolean }> = ({ handle, dark }) => {
  return (
    <div
      style={{
        position: "absolute",
        left: 48,
        top: 96,
        display: "flex",
        alignItems: "center",
        gap: 14,
        background: dark ? C.white : C.black,
        color: dark ? C.black : C.white,
        padding: "12px 24px 12px 14px",
        borderRadius: 999,
        rotate: "-2deg",
        boxShadow: `5px 5px 0 ${C.red}`,
      }}
    >
      <div
        style={{
          width: 46,
          height: 46,
          borderRadius: "50%",
          background: C.red,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: ANTON,
          fontSize: 28,
          color: C.white,
        }}
      >
        FE
      </div>
      <div style={{ fontFamily: INTER, fontWeight: 800, fontSize: 34, letterSpacing: -0.5 }}>{handle}</div>
    </div>
  );
};

/** Vinheta de marca @futexplicando (usada no CTA). */
export const Vinheta: React.FC<{ handle: string; startFrame: number }> = ({ handle, startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - startFrame;
  const p = spring({ frame: f, fps, config: { damping: 12, stiffness: 200 } });
  const bars = [C.red, C.black, C.white];
  return (
    <div style={{ position: "relative", display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ display: "flex", gap: 10, marginBottom: 18 }}>
        {bars.map((b, i) => (
          <div
            key={i}
            style={{
              width: 90,
              height: 18,
              background: b,
              border: `3px solid ${C.black}`,
              scale: `${spring({ frame: f - i * 3, fps, config: { damping: 12 } })} 1`,
            }}
          />
        ))}
      </div>
      <div
        style={{
          fontFamily: ANTON,
          fontSize: 120,
          color: C.black,
          scale: `${interpolate(p, [0, 1], [0.6, 1])}`,
          opacity: p,
          letterSpacing: 1,
        }}
      >
        {handle}
      </div>
    </div>
  );
};

/** Recorte (escudo/foto) com entrada em spring, parallax e leve rotação. */
export const Cutout: React.FC<{
  src: string;
  width: number;
  height?: number;
  startFrame: number;
  from?: { x?: number; y?: number; r?: number; s?: number };
  float?: number;
  shadow?: boolean;
  outline?: boolean;
  style?: React.CSSProperties;
  imgStyle?: React.CSSProperties;
  damping?: number;
}> = ({ src, width, height, startFrame, from = {}, float = 1, shadow = true, outline = false, style, imgStyle, damping = 12 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - startFrame;
  const p = spring({ frame: f, fps, config: { damping, stiffness: 170, mass: 0.8 } });
  const fx = Math.sin(frame / 22 + width) * 6 * float;
  const fr = Math.sin(frame / 31 + width) * 1.2 * float;
  return (
    <div
      style={{
        width,
        height,
        opacity: f < 0 ? 0 : 1,
        translate: `${interpolate(p, [0, 1], [from.x ?? 0, 0])}px ${interpolate(p, [0, 1], [from.y ?? 300, 0]) + fx}px`,
        rotate: `${interpolate(p, [0, 1], [from.r ?? -12, 0]) + fr}deg`,
        scale: `${interpolate(p, [0, 1], [from.s ?? 0.6, 1])}`,
        ...style,
      }}
    >
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: height ?? "auto",
          objectFit: "contain",
          filter: [
            outline ? `drop-shadow(0 0 0 ${C.white}) drop-shadow(5px 0 0 ${C.white}) drop-shadow(-5px 0 0 ${C.white}) drop-shadow(0 5px 0 ${C.white}) drop-shadow(0 -5px 0 ${C.white})` : "",
            shadow ? "drop-shadow(14px 18px 0 rgba(17,17,17,0.85))" : "",
          ].join(" "),
          ...imgStyle,
        }}
      />
    </div>
  );
};

/** Placar estilo TV. */
export const Scoreboard: React.FC<{
  startFrame: number;
  crestA: string;
  crestB: string;
  nameA: string;
  nameB: string;
  a: number;
  b: number;
  top: string;
  bottom: string;
  year: string;
}> = ({ startFrame, crestA, crestB, nameA, nameB, a, b, top, bottom, year }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - startFrame;
  const p = spring({ frame: f, fps, config: { damping: 13, stiffness: 220 } });
  const cell = (crest: string, name: string, side: number) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 300 }}>
      <div
        style={{
          width: 210,
          height: 210,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          translate: `${interpolate(p, [0, 1], [side * 260, 0])}px 0`,
          rotate: `${interpolate(p, [0, 1], [side * 30, 0])}deg`,
        }}
      >
        <Img src={staticFile(crest)} style={{ maxWidth: "100%", maxHeight: "100%", filter: "drop-shadow(0 8px 10px rgba(0,0,0,0.5))" }} />
      </div>
      <div style={{ fontFamily: ANTON, fontSize: 50, color: C.white, marginTop: 14, letterSpacing: 1 }}>{name}</div>
    </div>
  );
  const digit = (v: number, d: number) => (
    <div
      style={{
        fontFamily: ANTON,
        fontSize: 200,
        color: C.white,
        width: 140,
        textAlign: "center",
        lineHeight: 1,
        translate: `0 ${interpolate(spring({ frame: f - 5 - d, fps, config: { damping: 12 } }), [0, 1], [-140, 0])}px`,
        opacity: f - 5 - d > 0 ? 1 : 0,
      }}
    >
      {v}
    </div>
  );
  return (
    <div style={{ width: 960, scale: `${interpolate(p, [0, 1], [0.7, 1])}`, opacity: f < 0 ? 0 : 1 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "stretch" }}>
        <div style={{ background: C.red, color: C.white, fontFamily: BEBAS, fontSize: 46, padding: "8px 26px", letterSpacing: 3 }}>{top}</div>
        <div style={{ background: C.white, color: C.black, fontFamily: ANTON, fontSize: 46, padding: "6px 26px" }}>{year}</div>
      </div>
      <div
        style={{
          background: `linear-gradient(180deg, #2a2a2a, ${C.black})`,
          border: `6px solid ${C.white}`,
          padding: "36px 20px 30px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: `16px 16px 0 ${C.red}`,
        }}
      >
        {cell(crestA, nameA, -1)}
        <div style={{ display: "flex", alignItems: "center" }}>
          {digit(a, 0)}
          <div style={{ fontFamily: ANTON, fontSize: 90, color: C.red }}>×</div>
          {digit(b, 4)}
        </div>
        {cell(crestB, nameB, 1)}
      </div>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <div
          style={{
            background: C.white,
            color: C.black,
            fontFamily: ANTON,
            fontSize: 52,
            padding: "8px 34px",
            marginTop: -2,
            letterSpacing: 1,
            border: `6px solid ${C.black}`,
            clipPath: `inset(0 ${interpolate(f, [10, 20], [50, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}% 0 ${interpolate(f, [10, 20], [50, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}%)`,
          }}
        >
          {bottom}
        </div>
      </div>
    </div>
  );
};

/** Raios de luz atrás de um elemento (girando lentamente). */
export const Rays: React.FC<{ color?: string; opacity?: number; count?: number }> = ({ color = C.red, opacity = 0.25, count = 18 }) => {
  const frame = useCurrentFrame();
  const stops: string[] = [];
  for (let i = 0; i < count; i++) {
    const a = (i / count) * 360;
    stops.push(`${color} ${a}deg ${a + 360 / count / 2}deg`, `transparent ${a + 360 / count / 2}deg ${a + 360 / count}deg`);
  }
  return (
    <AbsoluteFill
      style={{
        background: `conic-gradient(from ${frame * 0.4}deg at 50% 50%, ${stops.join(",")})`,
        opacity,
        maskImage: "radial-gradient(circle at 50% 50%, black 0%, transparent 65%)",
      }}
    />
  );
};

/** Faísca/flash branco de impacto. */
export const Flash: React.FC<{ startFrame: number; dur?: number; color?: string }> = ({ startFrame, dur = 8, color = "#fff" }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - startFrame, [0, 1, dur], [0, 0.9, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ background: color, opacity: o, pointerEvents: "none" }} />;
};

/** Pedaços de papel/confete caindo. */
export const Confetti: React.FC<{ startFrame: number; count?: number; colors?: string[] }> = ({ startFrame, count = 40, colors = [C.red, C.black, C.white] }) => {
  const frame = useCurrentFrame();
  const f = frame - startFrame;
  if (f < 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: count }).map((_, i) => {
        const x = rand(i) * 1080;
        const vy = 9 + rand(i + 50) * 10;
        const y = -100 + f * vy - rand(i + 9) * 400;
        const r = f * (rand(i + 3) * 14 - 7);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x + Math.sin(f / 8 + i) * 30,
              top: y,
              width: 18 + rand(i + 1) * 18,
              height: 10 + rand(i + 2) * 10,
              background: colors[i % colors.length],
              border: `2px solid ${C.black}`,
              rotate: `${r}deg`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
