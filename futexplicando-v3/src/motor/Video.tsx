import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import { linearTiming, TransitionPresentation, TransitionPresentationComponentProps, TransitionSeries } from "@remotion/transitions";
import { Caption, createTikTokStyleCaptions } from "@remotion/captions";
import { COR, FONTE } from "../estilo/tokens";
import { HistoriaCtx, Plano, PlanoCfg } from "./Plano";
import { iniciosPlanos, TemposCena } from "./tempo";
import { mola } from "./Objetos";

export type Historia = { id: string; titulo: string; cenas: { id: string; texto: string; transicao?: string; clima?: string; planos: PlanoCfg[] }[] };
export const FPS = 30;
export const TRANS = 10;

/* ----------------------------------------------------------- transições */
type Vazio = Record<string, never>;
const WhipComp: React.FC<TransitionPresentationComponentProps<Vazio>> = ({ children, presentationDirection, presentationProgress: p }) => {
  const sai = presentationDirection === "exiting";
  const x = sai ? -p * 1080 : (1 - p) * 1080;
  const blur = Math.sin(Math.PI * p) * 22;
  return <AbsoluteFill style={{ transform: `translateX(${x}px)`, filter: `blur(${blur}px)` }}>{children}</AbsoluteFill>;
};
const whip = (): TransitionPresentation<Vazio> => ({ component: WhipComp, props: {} });

const WipeComp: React.FC<TransitionPresentationComponentProps<Vazio>> = ({ children, presentationDirection, presentationProgress: p }) => {
  if (presentationDirection === "exiting" || p >= 0.999) return <AbsoluteFill>{children}</AbsoluteFill>;
  // faixa diagonal amarelo/preto varre a tela; a cena nova é revelada atrás dela (sai inteira no fim)
  const pos = -0.4 + p * 2.1;
  const clip = `polygon(0 0, ${(pos - 0.25) * 100}% 0, ${(pos - 0.55) * 100}% 100%, 0 100%)`;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ clipPath: clip }}>{children}</AbsoluteFill>
      <AbsoluteFill style={{ clipPath: `polygon(${(pos - 0.25) * 100}% 0, ${(pos - 0.05) * 100}% 0, ${(pos - 0.35) * 100}% 100%, ${(pos - 0.55) * 100}% 100%)`, background: "repeating-linear-gradient(-60deg, #FFD400 0 60px, #111 60px 120px)" }} />
    </AbsoluteFill>
  );
};
const wipe = (): TransitionPresentation<Vazio> => ({ component: WipeComp, props: {} });

const ZoomComp: React.FC<TransitionPresentationComponentProps<Vazio>> = ({ children, presentationDirection, presentationProgress: p }) => {
  const sai = presentationDirection === "exiting";
  const s = sai ? 1 + p * 1.6 : 0.6 + p * 0.4;
  const o = sai ? 1 - p : p;
  return <AbsoluteFill style={{ transform: `scale(${s})`, opacity: o, filter: `blur(${(sai ? p : 1 - p) * 10}px)` }}>{children}</AbsoluteFill>;
};
const zoomThrough = (): TransitionPresentation<Vazio> => ({ component: ZoomComp, props: {} });
const FadeComp: React.FC<TransitionPresentationComponentProps<Vazio>> = ({ children, presentationDirection, presentationProgress: p }) => (
  <AbsoluteFill style={{ opacity: presentationDirection === "exiting" ? 1 : p }}>{children}</AbsoluteFill>
);
const fade = (): TransitionPresentation<Vazio> => ({ component: FadeComp, props: {} });
const apresentacao = (tipo?: string) => (tipo === "wipe" ? wipe() : tipo === "zoom" ? zoomThrough() : tipo === "fade" ? fade() : whip());

/* ----------------------------------------------------------- cena */
export const Cena: React.FC<{ cena: Historia["cenas"][number]; tempos: TemposCena }> = ({ cena, tempos }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const ini = iniciosPlanos(tempos.palavras, cena.planos);
  const i = Math.max(0, ini.findIndex((s, k) => t >= s && (k === ini.length - 1 || t < ini[k + 1])));
  const fim = i < ini.length - 1 ? ini[i + 1] : tempos.dur;
  // corte interno com micro-crossfade de 4 quadros
  const tPrev = i > 0 ? t - ini[i - 1] : 0;
  const fade = i > 0 ? Math.min(1, (t - ini[i]) / (4 / FPS)) : 1;
  return (
    <AbsoluteFill>
      {i > 0 && fade < 1 && <Plano p={cena.planos[i - 1]} pal={tempos.palavras} tIni={ini[i - 1]} tFim={ini[i]} t={tPrev} audio={tempos.audio} />}
      <AbsoluteFill style={{ opacity: fade }}>
        <Plano p={cena.planos[i]} pal={tempos.palavras} tIni={ini[i]} tFim={fim} t={t - ini[i]} audio={tempos.audio} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ----------------------------------------------------------- legenda karaokê */
export const inicioCenas = (tempos: TemposCena[]) => {
  const ini: number[] = [];
  let acc = 0;
  tempos.forEach((c) => {
    ini.push(acc);
    acc += Math.round(c.dur * FPS) - TRANS;
  });
  return ini;
};
export const duracaoTotal = (tempos: TemposCena[]) => tempos.reduce((a, c) => a + Math.round(c.dur * FPS), 0) - TRANS * (tempos.length - 1);

const paginas = (tempos: TemposCena[]) => {
  const ini = inicioCenas(tempos);
  const caps: Caption[] = [];
  tempos.forEach((c, k) =>
    c.palavras.forEach((p) => {
      const off = (ini[k] / FPS) * 1000;
      caps.push({ text: ` ${p.w}`, startMs: off + p.t * 1000, endMs: off + p.f * 1000, timestampMs: off + p.t * 1000, confidence: 1 });
    }),
  );
  const { pages } = createTikTokStyleCaptions({ captions: caps, combineTokensWithinMilliseconds: 700 });
  // no máximo 3 palavras por página; quebra também em pontuação
  const out: { startMs: number; endMs: number; tokens: { text: string; fromMs: number; toMs: number }[] }[] = [];
  pages.forEach((pg) => {
    let cur: typeof pg.tokens = [];
    pg.tokens.forEach((tk, j) => {
      cur.push(tk);
      const fimFrase = /[.,!?:…]$/.test(tk.text.trim());
      if (cur.length === 3 || fimFrase || j === pg.tokens.length - 1) {
        out.push({ startMs: cur[0].fromMs, endMs: cur[cur.length - 1].toMs, tokens: cur });
        cur = [];
      }
    });
  });
  return out;
};

export const Legenda: React.FC<{ tempos: TemposCena[] }> = ({ tempos }) => {
  const frame = useCurrentFrame();
  const ms = (frame / FPS) * 1000;
  const pgs = React.useMemo(() => paginas(tempos), [tempos]);
  const pg = pgs.find((p, i) => ms >= p.startMs - 30 && (i === pgs.length - 1 ? ms < p.endMs + 400 : ms < pgs[i + 1].startMs - 30));
  if (!pg) return null;
  return (
    <div style={{ position: "absolute", left: 50, right: 50, top: 1330, transform: "translateY(-50%)", display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: 42, rowGap: 0 }}>
      {pg.tokens.map((tk, i) => {
        const ativo = ms >= tk.fromMs - 20 && ms < tk.toMs;
        const k = ativo ? 1 + 0.12 * Math.min(1, mola((ms - tk.fromMs) / 1000, 3, 0.5)) : 1;
        const tx = tk.text.trim().toUpperCase();
        return (
          <span key={i} style={{ fontFamily: FONTE.titulo, fontSize: tx.length > 11 ? 84 : 96, color: ativo ? COR.amarelo : "#FFFFFF", WebkitTextStroke: "10px #000", paintOrder: "stroke fill", textShadow: "0 8px 0 rgba(0,0,0,0.5)", display: "inline-block", transform: `scale(${k})`, lineHeight: 1.1 }}>
            {tx}
          </span>
        );
      })}
    </div>
  );
};

/* ----------------------------------------------------------- vídeo */
const Acabamento: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ backgroundImage: "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' seed='" + (f % 6) + "'/></filter><rect width='300' height='300' filter='url(%23n)' opacity='0.55'/></svg>\")", opacity: 0.07, mixBlendMode: "overlay" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 90% 75% at 50% 45%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.35) 100%)" }} />
    </AbsoluteFill>
  );
};

export const Video: React.FC<{ historia: Historia; tempos: TemposCena[]; trilha?: string }> = ({ historia, tempos, trilha }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: "#000", filter: "contrast(1.04) saturate(1.06)" }}>
      <HistoriaCtx.Provider value={{ cenas: historia.cenas, tempos }}>
      <TransitionSeries>
        {historia.cenas.map((c, k) => (
          <React.Fragment key={c.id}>
            {k > 0 && <TransitionSeries.Transition presentation={apresentacao(c.transicao)} timing={linearTiming({ durationInFrames: TRANS })} />}
            <TransitionSeries.Sequence durationInFrames={Math.round(tempos[k].dur * fps)} name={`${k + 1} ${c.id}`}>
              <Cena cena={c} tempos={tempos[k]} />
            </TransitionSeries.Sequence>
          </React.Fragment>
        ))}
      </TransitionSeries>
      </HistoriaCtx.Provider>
      <Acabamento />
      <Legenda tempos={tempos} />
      {trilha && <Audio src={staticFile(trilha)} />}
    </AbsoluteFill>
  );
};

/* ----------------------------------------------------------- folha de contato */
export const ContatoCena: React.FC<{ historia: Historia; tempos: TemposCena[]; cena: number }> = ({ historia, tempos, cena }) => {
  const c = historia.cenas[cena];
  const tp = tempos[cena];
  const ini = iniciosPlanos(tp.palavras, c.planos);
  return (
    <HistoriaCtx.Provider value={{ cenas: historia.cenas, tempos }}>
    <AbsoluteFill style={{ background: "#111", display: "flex", flexDirection: "row", gap: 12, padding: 12 }}>
      {c.planos.map((p, i) => {
        const fim = i < ini.length - 1 ? ini[i + 1] : tp.dur;
        const t = Math.max(0.1, fim - ini[i] - 0.12);
        return (
          <div key={i} style={{ width: 352, height: 626, overflow: "hidden", position: "relative", borderRadius: 10 }}>
            <div style={{ width: 1080, height: 1920, transform: "scale(0.326)", transformOrigin: "0 0", position: "absolute" }}>
              <Plano p={p} pal={tp.palavras} tIni={ini[i]} tFim={fim} t={t} audio={tp.audio} />
            </div>
            <div style={{ position: "absolute", left: 8, top: 6, fontFamily: FONTE.titulo, fontSize: 26, color: COR.amarelo, textShadow: "0 2px 0 #000" }}>{`${cena + 1}${"ABC"[i]} · ${c.id}`}</div>
          </div>
        );
      })}
    </AbsoluteFill>
    </HistoriaCtx.Provider>
  );
};

/* ----------------------------------------------------------- capa */
export const Capa: React.FC<{ historia: Historia; tempos: TemposCena[]; cena?: number; plano?: number; t?: number }> = ({ historia, tempos, cena = 0, plano = 0, t = 3 }) => {
  const c = historia.cenas[cena];
  const tp = tempos[cena];
  const ini = iniciosPlanos(tp.palavras, c.planos);
  const fim = plano < ini.length - 1 ? ini[plano + 1] : tp.dur;
  return (
    <AbsoluteFill>
      <Plano p={c.planos[plano]} pal={tp.palavras} tIni={ini[plano]} tFim={fim} t={Math.min(t, fim - ini[plano] - 0.05)} />
    </AbsoluteFill>
  );
};
