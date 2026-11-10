import React, { createContext, useContext } from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from "remotion";
import { measureText } from "@remotion/layout-utils";
import { C, FAM, SX, SAFE, SAFE_W, W, H, Bg, INK } from "./theme";
import { CUT } from "./timeline";

export const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const outCubic = (p: number) => 1 - Math.pow(1 - p, 3);
const backOut = Easing.out(Easing.back(1.8));

/** Contexto da cena: início, fim, fundo e tipo de saída do texto */
export const SceneCtx = createContext<{ s: number; e: number; bg: Bg; exit: boolean }>({ s: 0, e: 9999, bg: "gray", exit: true });
export const useScene = () => useContext(SceneCtx);

/** Palavra: entra desfocada (12px), 40% de opacidade, escala 0.9 e firma em 5 frames; sai girando em 3D */
export const Word: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties; noExit?: boolean; ghost?: boolean }> = ({ at, children, style, noExit, ghost }) => {
  const f = useCurrentFrame();
  const { e, exit } = useScene();
  const p = clamp01((f - at + 1) / 5);
  const o = exit && !noExit ? clamp01((f - (e - 4)) / 3) : 0;
  const visible = f >= at || !!ghost;
  return (
    <span
      style={{
        display: "inline-block",
        transformOrigin: "50% 60%",
        visibility: visible ? "visible" : "hidden",
        opacity: (0.4 + 0.6 * p) * (1 - o),
        filter: p < 1 ? `blur(${12 * (1 - p)}px) grayscale(${1 - p})` : undefined,
        transform: `perspective(900px) scale(${0.9 + 0.1 * outCubic(p)}) rotateX(${o * 85}deg) translateY(${-o * 40}px)`,
        ...style,
      }}
    >
      {children}
    </span>
  );
};

export type Tok = { t: string; at: number; ghost?: boolean; font?: "anton" | "serif" | "inter"; rel?: number; color?: string; hi?: boolean; small?: boolean; dy?: number };
const tokText = (k: Tok) => ((k.font ?? "anton") === "anton" ? k.t.toUpperCase() : k.t);
const tokW = (k: Tok, size: number) => {
  const font = k.font ?? "anton";
  return measureText({ text: tokText(k), fontFamily: FAM[font], fontSize: size, fontWeight: "400", validateFontIsLoaded: true }).width * SX[font];
};
/** Linha de texto ajustada à largura: palavra-chave gigante + conectivos minúsculos encostados */
const StackW = createContext(SAFE_W);
export const Row: React.FC<{ toks: Tok[]; width?: number; max?: number; gap?: number; mt?: number; lh?: number; align?: "left" | "center" }> = ({ toks, width: widthProp, max = 420, gap = 0.07, mt = 0, lh = 0.98, align = "left" }) => {
  const { bg } = useScene();
  const sw = useContext(StackW);
  const width = Math.min(widthProp ?? sw, sw);
  const ink = INK[bg];
  const rel = (k: Tok) => k.rel ?? (k.small ? 0.3 : 1);
  const unit = toks.reduce((a, k) => a + tokW(k, 100 * rel(k)), 0) + gap * 100 * (toks.length - 1);
  const base = Math.min(max, (width / unit) * 100);
  return (
    <div style={{ display: "flex", alignItems: "baseline", justifyContent: align === "center" ? "center" : "flex-start", gap: base * gap, marginTop: mt, whiteSpace: "nowrap", lineHeight: lh, height: base * lh }}>
      {toks.map((k, i) => {
        const font = k.font ?? "anton";
        const size = base * rel(k);
        const w = tokW(k, size);
        const color = k.color ?? (k.hi ? ink.hi : k.small ? ink.small : ink.main);
        return (
          <Word key={i} at={k.at} ghost={k.ghost} style={{ width: w, height: base * lh, lineHeight: `${base * lh}px` }}>
            <span style={{ display: "inline-block", fontFamily: FAM[font], fontSize: size, color, transform: `scaleX(${SX[font]}) translateY(${(k.dy ?? 0) * base}px)`, transformOrigin: "0 50%", letterSpacing: font === "anton" ? "-0.005em" : "-0.01em" }}>{tokText(k)}</span>
          </Word>
        );
      })}
    </div>
  );
};
/** Bloco de título no terço superior, dentro das margens de segurança */
export const Stack: React.FC<{ children: React.ReactNode; top?: number; left?: number; width?: number }> = ({ children, top = SAFE.top, left = SAFE.left, width = SAFE_W }) => (
  <StackW.Provider value={width}><div style={{ position: "absolute", top, left, width, display: "flex", flexDirection: "column", zIndex: 5 }}>{children}</div></StackW.Provider>
);

/** Recorte P&B com retícula. Ancorado pelo centro-x e pela base. Micro-movimento em "stop motion" + zoom lento. */
export const Cut: React.FC<{ name: string; h: number; cx: number; bottom: number; at?: number; from?: "pop" | "left" | "right" | "bottom"; rot?: number; z?: number; sil?: boolean; drift?: number; opacity?: number; flip?: boolean }> = ({ name, h, cx, bottom, at, from = "pop", rot = 0, z, sil, drift = 0.07, opacity = 1, flip }) => {
  const f = useCurrentFrame();
  const { s, e, bg } = useScene();
  const start = at ?? s;
  if (f < start) return null;
  const m = CUT[name];
  const w = (h * m.w) / m.h;
  const p = clamp01((f - start + 1) / 6);
  const k = backOut(p);
  const step = Math.floor(f / 4);
  const jx = Math.sin(step * 12.9898) * 4, jy = Math.cos(step * 78.233) * 3, jr = Math.sin(step * 3.7) * 0.7;
  const life = clamp01((f - start) / Math.max(1, e - start));
  const sc = (from === "pop" ? 0.82 + 0.18 * k : 1) * (1 + drift * life);
  const dx = from === "left" ? (1 - outCubic(p)) * -900 : from === "right" ? (1 - outCubic(p)) * 900 : 0;
  const dy = from === "bottom" ? (1 - outCubic(p)) * 700 : 0;
  const mb = from === "left" || from === "right" ? (1 - p) * 40 : 0;
  return (
    <Img
      src={staticFile(`cut/${name}.png`)}
      style={{
        position: "absolute", left: cx - w / 2, top: bottom - h, width: w, height: h, zIndex: z, opacity,
        transformOrigin: "50% 100%",
        transform: `translate(${dx + jx}px, ${dy + jy}px) rotate(${rot + jr}deg) scale(${sc}) ${flip ? "scaleX(-1)" : ""}`,
        filter: `${sil ? `brightness(0) invert(${bg === "black" ? 0.93 : 0.11})` : ""} ${p < 1 ? `blur(${(1 - p) * 10 + mb}px)` : ""}`.trim() || undefined,
      }}
    />
  );
};

/** Estrela de pontas amarela (atrás do recorte, na revelação do título) */
export const Star: React.FC<{ cx: number; cy: number; r: number; at: number; points?: number; color?: string }> = ({ cx, cy, r, at, points = 18, color = C.yellow }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = backOut(clamp01((f - at + 1) / 7));
  const pts: string[] = [];
  for (let i = 0; i < points * 2; i++) {
    const a = (Math.PI * i) / points, rr = i % 2 ? r * 0.74 : r;
    pts.push(`${Math.cos(a) * rr},${Math.sin(a) * rr}`);
  }
  const step = Math.floor(f / 3);
  return (
    <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
      <polygon points={pts.join(" ")} fill={color} transform={`translate(${cx} ${cy}) rotate(${step * 4}) scale(${p})`} />
    </svg>
  );
};

/** Número gigante da contagem (serifada itálica) */
export const BigNum: React.FC<{ n: string; at: number; size: number; x: number; y: number; color: string }> = ({ n, at, size, x, y, color }) => (
  <div style={{ position: "absolute", left: x, top: y, lineHeight: 1 }}>
    <Word at={at}>
      <span style={{ fontFamily: FAM.serif, fontSize: size, color, display: "inline-block", transform: "scaleX(0.8)", transformOrigin: "0 50%", lineHeight: 0.9 }}>{n}</span>
    </Word>
  </div>
);

/** Moldura de visor de câmera + REC piscando */
export const Viewfinder: React.FC<{ at: number; color?: string; inset?: { t: number; b: number; l: number; r: number } }> = ({ at, color = C.gray, inset = { t: 200, b: 380, l: 40, r: 110 } }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = outCubic(clamp01((f - at + 1) / 5));
  const L = 110, sw = 8;
  const x0 = inset.l, y0 = inset.t, x1 = W - inset.r, y1 = H - inset.b;
  const grow = (1 - p) * 60;
  const blink = Math.floor((f - at) / 8) % 2 === 0;
  const corner = (x: number, y: number, dx: number, dy: number, k: number) => <polyline key={k} points={`${x + dx * L},${y} ${x},${y} ${x},${y + dy * L}`} fill="none" stroke={color} strokeWidth={sw} />;
  const tc = f - at;
  const pad = (n: number) => String(n).padStart(2, "0");
  return (
    <AbsoluteFill style={{ opacity: p }}>
      <svg width={W} height={H}>
        {corner(x0 - grow, y0 - grow, 1, 1, 0)}
        {corner(x1 + grow, y0 - grow, -1, 1, 1)}
        {corner(x0 - grow, y1 + grow, 1, -1, 2)}
        {corner(x1 + grow, y1 + grow, -1, -1, 3)}
      </svg>
      <div style={{ position: "absolute", left: SAFE.left + 6, top: H - SAFE.bottom - 72, display: "flex", alignItems: "center", gap: 16, fontFamily: FAM.inter, fontSize: 44, color }}>
        <div style={{ width: 34, height: 34, borderRadius: 17, background: C.red, opacity: blink ? 1 : 0.15 }} />
        REC
        <span style={{ marginLeft: 18, fontVariantNumeric: "tabular-nums" }}>00:{pad(Math.floor(tc / 30))}:{pad(tc % 30)}</span>
      </div>
    </AbsoluteFill>
  );
};

/** Grade fina desfocada no fundo */
export const Grid: React.FC<{ at: number; color: string; max?: number }> = ({ at, color, max = 0.3 }) => {
  const f = useCurrentFrame();
  const p = clamp01((f - at + 1) / 14);
  const lines: React.ReactNode[] = [];
  for (let x = 0; x <= W; x += 90) lines.push(<line key={"x" + x} x1={x} y1={0} x2={x} y2={H} />);
  for (let y = 0; y <= H; y += 90) lines.push(<line key={"y" + y} x1={0} y1={y} x2={W} y2={y} />);
  return (
    <svg width={W} height={H} style={{ position: "absolute", opacity: p * max, filter: "blur(1.6px)", transform: `scale(${1.25 - 0.25 * outCubic(p)})` }}>
      <g stroke={color} strokeWidth={2}>{lines}</g>
    </svg>
  );
};

/** Linha tracejada que se desenha ligando filme -> logo */
export const DashedLink: React.FC<{ d: string; at: number; dur?: number; color: string; id: string }> = ({ d, at, dur = 10, color, id }) => {
  const f = useCurrentFrame();
  const p = outCubic(clamp01((f - at + 1) / dur));
  return (
    <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
      <defs>
        <mask id={id} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
          <path d={d} fill="none" stroke="white" strokeWidth={30} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
        </mask>
      </defs>
      <path d={d} fill="none" stroke={color} strokeWidth={9} strokeDasharray="26 18" strokeDashoffset={-f * 2} strokeLinecap="round" mask={`url(#${id})`} />
    </svg>
  );
};

/** Logo do streaming em uma cor só (para ficar dentro da paleta) */
const LOGO_AR: Record<string, number> = { netflix: 1024 / 276.742, primevideo: 84.6 / 26.6, hbomax: 1240 / 894.5 };
export const Logo: React.FC<{ name: "netflix" | "primevideo" | "hbomax"; w: number; x: number; y: number; color: string; at: number }> = ({ name, w, x, y, color, at }) => {
  const f = useCurrentFrame();
  const url = staticFile(`logos/${name}.svg`);
  const h = w / LOGO_AR[name];
  const p = backOut(clamp01((f - at + 1) / 6));
  return (
    <>
      <Img src={url} style={{ position: "absolute", width: 4, height: 4, opacity: 0 }} />
      {f >= at ? (
        <div style={{ position: "absolute", left: x, top: y, width: w, height: h, background: color, WebkitMaskImage: `url(${url})`, WebkitMaskSize: "100% 100%", WebkitMaskRepeat: "no-repeat", maskImage: `url(${url})`, maskSize: "100% 100%", maskRepeat: "no-repeat", transform: `scale(${0.6 + 0.4 * p}) rotate(${(1 - p) * -6}deg)`, opacity: clamp01(p * 2) }} />
      ) : null}
    </>
  );
};

/** Legenda secundária: sans bold ~44px, 1–3 palavras por vez, centralizada */
export const Caption: React.FC<{ chunks: { t: string; at: number }[]; y?: number; color: string; bg: string }> = ({ chunks, y = H - SAFE.bottom - 80, color, bg }) => {
  const f = useCurrentFrame();
  let cur: { t: string; at: number } | null = null;
  for (const c of chunks) if (f >= c.at) cur = c;
  if (!cur) return null;
  const p = outCubic(clamp01((f - cur.at + 1) / 4));
  return (
    <div style={{ position: "absolute", left: SAFE.left, width: SAFE_W, top: y, display: "flex", justifyContent: "center" }}>
      <div style={{ fontFamily: FAM.inter, fontSize: 46, color, background: bg, padding: "10px 26px", transform: `scale(${0.9 + 0.1 * p})`, opacity: 0.4 + 0.6 * p, filter: p < 1 ? `blur(${(1 - p) * 8}px)` : undefined }}>{cur.t}</div>
    </div>
  );
};

/** Celular recortado: a cena anterior vira a tela dele (transição zoom) */
export const Phone: React.FC<{ at: number; children: React.ReactNode; tx: number; ty: number; w: number; rot?: number; leave?: number }> = ({ at, children, tx, ty, w, rot = 8, leave }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = outCubic(clamp01((f - at + 1) / 9));
  const bez = 0.07;
  const full = W / (1 - 2 * bez) / w; // escala em que a tela do celular cobre o quadro
  const sc = interpolate(p, [0, 1], [full * 1.02, 1]);
  const h = (w * H) / W + w * bez * 2;
  const cx = interpolate(p, [0, 1], [W / 2, tx]), cy = interpolate(p, [0, 1], [H / 2, ty]);
  const out = leave !== undefined ? Easing.in(Easing.cubic)(clamp01((f - leave) / 6)) : 0;
  const inner = w * (1 - 2 * bez);
  return (
    <div style={{ position: "absolute", left: cx - w / 2, top: cy - h / 2, width: w, height: h, transform: `translate(${out * 1500}px, ${out * 500}px) scale(${sc}) rotate(${p * rot + out * 30}deg)`, background: C.black, borderRadius: w * 0.13, boxShadow: `0 0 0 ${w * 0.012}px ${C.black}` }}>
      <div style={{ position: "absolute", left: w * bez, top: w * bez, width: inner, height: (inner * H) / W, overflow: "hidden", borderRadius: w * 0.07 }}>
        <div style={{ width: W, height: H, transform: `scale(${inner / W})`, transformOrigin: "0 0", position: "relative" }}>{children}</div>
      </div>
      <div style={{ position: "absolute", left: w * 0.36, top: w * 0.1, width: w * 0.28, height: w * 0.055, borderRadius: w * 0.03, background: C.black }} />
    </div>
  );
};

/** Ícones literais */
export const Bookmark: React.FC<{ x: number; y: number; h: number; at: number; fillAt: number; stroke: string; fill: string }> = ({ x, y, h, at, fillAt, stroke, fill }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = backOut(clamp01((f - at + 1) / 6));
  const q = clamp01((f - fillAt + 1) / 4);
  const w = h * 0.72;
  return (
    <svg width={w} height={h} viewBox="0 0 72 100" style={{ position: "absolute", left: x, top: y, transform: `scale(${p * (1 + 0.25 * Math.sin(q * Math.PI))})`, overflow: "visible" }}>
      <path d="M8 6 H64 V94 L36 70 L8 94 Z" fill={fill} fillOpacity={q} stroke={stroke} strokeWidth={9} strokeLinejoin="round" />
    </svg>
  );
};
export const Plane: React.FC<{ x: number; y: number; s: number; at: number; color: string }> = ({ x, y, s, at, color }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = outCubic(clamp01((f - at + 1) / 8));
  const fly = (f - at) * 3;
  return (
    <svg width={s} height={s} viewBox="0 0 100 100" style={{ position: "absolute", left: x - (1 - p) * 500 + fly, top: y + (1 - p) * 300 - fly * 0.6, overflow: "visible", transform: `rotate(${(1 - p) * -25}deg)` }}>
      <path d="M6 12 L94 50 L6 88 L22 50 Z M22 50 L94 50" fill="none" stroke={color} strokeWidth={8} strokeLinejoin="round" />
    </svg>
  );
};
export const fill = (bg: Bg) => C[bg];
export { outCubic, backOut };
