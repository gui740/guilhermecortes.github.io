import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Img, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import raw from "../../data/corinthians.json";
import { Captions } from "../../components/Captions";
import { Confetti, Cutout, Flash, Hook, Rays, Scoreboard, Seal, StatSlam, Vinheta, YearStamp } from "../../components/Graphics";
import { Grain, PaperBackground, TornStrip } from "../../components/Paper";
import { rand, shake, useSceneClock } from "../../components/time";
import { ANTON, BEBAS, C, INTER } from "../../theme";

const D = raw;
const A = raw.assets as Record<string, string>;
const LUZ = D.paleta.luz;
const ACCENT_VARS = { ["--accent" as string]: "#111111", ["--accent2" as string]: "#F4EFE6" } as React.CSSProperties;

/* ----------------------- elementos desenhados ----------------------- */

/** Lampião de rua (desenho próprio). `on` 0..1 = brilho. */
const Lamp: React.FC<{ on: number; scale?: number }> = ({ on, scale = 1 }) => {
  const glass = `rgba(255, 210, 122, ${0.15 + 0.85 * on})`;
  return (
    <svg width={260 * scale} height={1000 * scale} viewBox="0 0 260 1000" style={{ overflow: "visible" }}>
      <defs>
        <radialGradient id="halo">
          <stop offset="0" stopColor={LUZ} stopOpacity={0.9 * on} />
          <stop offset="1" stopColor={LUZ} stopOpacity={0} />
        </radialGradient>
      </defs>
      <circle cx="130" cy="150" r="230" fill="url(#halo)" />
      {/* lanterna */}
      <path d="M95 60 L165 60 L180 85 L80 85 Z" fill="#111" />
      <path d="M118 30 Q130 12 142 30 L142 60 L118 60 Z" fill="#111" />
      <path d="M88 85 L172 85 L160 215 L100 215 Z" fill={glass} stroke="#111" strokeWidth="8" strokeLinejoin="round" />
      <line x1="130" y1="85" x2="130" y2="215" stroke="#111" strokeWidth="5" />
      <path d="M92 215 L168 215 L150 245 L110 245 Z" fill="#111" />
      {/* poste */}
      <rect x="121" y="245" width="18" height="700" fill="#111" />
      <path d="M100 300 Q130 270 160 300" stroke="#111" strokeWidth="8" fill="none" />
      <path d="M95 945 L165 945 L180 1000 L80 1000 Z" fill="#111" />
    </svg>
  );
};

/** Silhueta de operário (desenho próprio). */
const Worker: React.FC<{ h: number; hat?: boolean; seed?: number }> = ({ h, hat = true, seed = 1 }) => {
  const lean = (rand(seed) - 0.5) * 6;
  return (
    <svg width={h * 0.42} height={h} viewBox="0 0 84 200" style={{ rotate: `${lean}deg` }}>
      <circle cx="42" cy="28" r="17" fill="#111" />
      {hat ? <path d="M18 20 L66 20 L60 8 L24 8 Z" fill="#111" /> : null}
      <path d="M14 58 Q42 44 70 58 L66 120 L58 120 L56 196 L44 196 L42 132 L40 196 L28 196 L26 120 L18 120 Z" fill="#111" />
    </svg>
  );
};

/** Placa de rua azul de São Paulo (desenho próprio). */
const StreetSign: React.FC<{ text: string; rotate?: number }> = ({ text, rotate = 0 }) => (
  <div style={{ background: "#1F3F8F", border: "5px solid #F4EFE6", outline: "4px solid #111", borderRadius: 8, padding: "6px 18px", fontFamily: BEBAS, fontSize: 40, color: "#F4EFE6", letterSpacing: 2, rotate: `${rotate}deg`, boxShadow: "6px 6px 0 #111", whiteSpace: "nowrap" }}>{text}</div>
);

/** Brilho do lampião piscando a partir de `start` (frames). */
const flicker = (f: number, start: number) => {
  const t = f - start;
  if (t < 0) return 0;
  const pattern = [1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1];
  if (t < pattern.length) return pattern[t] * 0.8;
  return Math.min(1, 0.8 + (t - pattern.length) * 0.03);
};

/** Transição: a luz cai, o lampião pisca e volta. */
const LampWipe: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const dark = interpolate(t, [0, 0.2, 0.42, 0.7], [0, 0.95, 0.95, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const on = [0, 1, 0, 1, 1, 0, 1][Math.min(6, Math.floor(t * 18))] ?? 1;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: "#0b0b0b", opacity: dark }} />
      <div style={{ position: "absolute", left: 540 - 130 * 0.7, top: 520, opacity: dark, scale: "1" }}>
        <Lamp on={on} scale={0.7} />
      </div>
    </AbsoluteFill>
  );
};

/** Linha de placar compacta. */
const ScoreRow: React.FC<{ p: { ano: string; adv: string; escudoAdv: string; golsCor: number; golsAdv: number; detalhe: string }; startFrame: number; width?: number }> = ({ p, startFrame, width = 940 }) => {
  const frame = useCurrentFrame();
  const k = interpolate(frame - startFrame, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
  if (frame < startFrame) return null;
  return (
    <div style={{ width, translate: `${(1 - k) * -1100}px 0`, marginBottom: 20 }}>
      <div style={{ display: "flex", alignItems: "center", background: C.black, border: `5px solid ${C.white}`, boxShadow: "9px 9px 0 #8A8A8A", padding: "10px 18px", gap: 16 }}>
        <div style={{ fontFamily: ANTON, fontSize: 42, color: C.white, width: 250 }}>{p.ano}</div>
        <Img src={staticFile(A.escudoAtual)} style={{ height: 84, width: 84, objectFit: "contain" }} />
        <div style={{ fontFamily: ANTON, fontSize: 76, color: C.white }}>{p.golsCor}</div>
        <div style={{ fontFamily: ANTON, fontSize: 44, color: "#8A8A8A" }}>×</div>
        <div style={{ fontFamily: ANTON, fontSize: 76, color: C.white }}>{p.golsAdv}</div>
        <Img src={staticFile(A[p.escudoAdv])} style={{ height: 84, width: 84, objectFit: "contain" }} />
        <div style={{ fontFamily: ANTON, fontSize: 40, color: C.white }}>{p.adv}</div>
      </div>
      <div style={{ fontFamily: BEBAS, fontSize: 32, letterSpacing: 2, color: C.black, background: C.white, display: "inline-block", padding: "2px 14px", border: `4px solid ${C.black}`, borderTop: "none" }}>{p.detalhe}</div>
    </div>
  );
};

const Polaroid: React.FC<{ src: string; w: number; h: number; caption: string; startFrame: number; rot?: number; fromX?: number }> = ({ src, w, h, caption, startFrame, rot = -3, fromX = 900 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const k = interpolate(frame - startFrame, [0, 0.4 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
  if (frame < startFrame) return null;
  return (
    <div style={{ width: w, background: C.white, padding: "16px 16px 54px", boxShadow: `12px 14px 0 ${C.black}`, rotate: `${interpolate(k, [0, 1], [rot * 4, rot])}deg`, translate: `${(1 - k) * fromX}px 0` }}>
      <div style={{ width: "100%", height: h, overflow: "hidden" }}>
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </div>
      <div style={{ fontFamily: INTER, fontWeight: 700, fontSize: 24, color: "#555", marginTop: 10 }}>{caption}</div>
    </div>
  );
};

/* ------------------------------ CENAS ------------------------------ */

const LAMP = { left: 540 - 130, top: 330 };

const SceneHook: React.FC = () => {
  const s = D.cenas.gancho;
  const { abs, fps, frame } = useSceneClock(s.inicio);
  const on = flicker(frame, Math.round(s.acendeEm * fps));
  const wk = interpolate(abs, [s.operariosEm, s.operariosEm + 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: "#0b0b0b", opacity: 0.94 - on * 0.5 }} />
      {/* cone de luz */}
      <div style={{ position: "absolute", left: 540 - 420, top: LAMP.top + 200, width: 840, height: 1100, background: `linear-gradient(180deg, rgba(255,210,122,${0.35 * on}) 0%, rgba(255,210,122,0) 85%)`, clipPath: "polygon(42% 0, 58% 0, 100% 100%, 0 100%)" }} />
      <div style={{ position: "absolute", left: LAMP.left, top: LAMP.top }}>
        <Lamp on={on} />
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 1180, display: "flex", justifyContent: "center", gap: 26, opacity: wk, translate: `0 ${(1 - wk) * 40}px` }}>
        {[0, 1, 2, 3, 4].map((i) => (
          <Worker key={i} h={i === 2 ? 250 : 220 + (i % 2) * 15} seed={i + 3} hat={i !== 1} />
        ))}
      </div>
      <div style={{ position: "absolute", top: 190, width: "100%", textAlign: "center", fontFamily: BEBAS, fontSize: 62, letterSpacing: 8, color: LUZ, opacity: interpolate(abs, [s.operariosEm - 0.2, s.operariosEm + 0.1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        {s.linhas[0]}
      </div>
      {abs >= s.lampiaoEm ? <Hook lines={[s.linhas[1]]} startFrame={(s.lampiaoEm - s.inicio) * fps} size={112} color={C.white} style={{ position: "absolute", top: 260, width: "100%" }} /> : null}
    </AbsoluteFill>
  );
};

const SceneVirada: React.FC = () => {
  const s = D.cenas.virada;
  const { abs, since, sp } = useSceneClock(s.inicio);
  const p = sp(s.inicio, { damping: 9, stiffness: 180, mass: 0.9 });
  const sh = shake(since(s.inicio), 26, 0.22);
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      <div style={{ position: "absolute", left: 0, top: 300, width: 1080, height: 1080 }}>
        <Rays opacity={0.18} count={22} />
      </div>
      <div style={{ position: "absolute", left: 540 - 330, top: 470, width: 660, height: 660, scale: `${interpolate(p, [0, 1], [3.5, 1])}`, opacity: interpolate(p, [0, 0.15], [0, 1], { extrapolateRight: "clamp" }), rotate: `${interpolate(p, [0, 1], [-25, 0]) + Math.sin(abs * 2) * 1.5}deg` }}>
        <Img src={staticFile(A.escudoAtual)} style={{ width: "100%", height: "100%", objectFit: "contain", filter: "drop-shadow(18px 22px 0 #8A8A8A)" }} />
      </div>
      <div style={{ position: "absolute", top: 160, width: "100%", textAlign: "center" }}>
        <div style={{ fontFamily: BEBAS, fontSize: 78, letterSpacing: 10, color: C.black }}>{s.linha1}</div>
        <Hook lines={[s.linha2]} startFrame={6} size={160} color={C.black} />
      </div>
      <div style={{ position: "absolute", top: 1230, width: "100%", display: "flex", justifyContent: "center" }}>
        <div style={{ background: C.black, color: C.white, fontFamily: ANTON, fontSize: 70, padding: "10px 40px", rotate: "-2deg", boxShadow: "8px 8px 0 #8A8A8A", clipPath: `inset(0 ${interpolate(since(s.inicio + 0.6), [0, 8], [100, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}% 0 0)` }}>
          {s.linha3}
        </div>
      </div>
      <Flash startFrame={0} dur={7} color={LUZ} />
    </AbsoluteFill>
  );
};

const SceneNascimento: React.FC = () => {
  const s = D.cenas.nascimento;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const ing = sp(s.inglesEm, { damping: 11 });
  const wk = sp(s.operariosEm, { damping: 12 });
  const names = ["J. AMBRÓSIO", "A. PEREIRA", "R. PERRONE", "A. CORRÊA", "C. SILVA"];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 190, width: "100%", textAlign: "center" }}>
        <YearStamp text={s.data} startFrame={f(s.dataEm)} size={150} rotate={-5} color={C.black} />
      </div>
      <div style={{ position: "absolute", left: 40, top: 430 }}>
        <Lamp on={1} scale={0.62} />
      </div>
      {abs >= s.lugarEm ? (
        <div style={{ position: "absolute", left: 150, top: 560, translate: `${interpolate(since(s.lugarEm), [0, 8], [-900, 0], { extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) })}px 0` }}>
          <StreetSign text="R. JOSÉ PAULINO" rotate={-3} />
          <div style={{ height: 14 }} />
          <StreetSign text="R. CÔNEGO MARTINS" rotate={2} />
          <div style={{ fontFamily: BEBAS, fontSize: 40, letterSpacing: 4, color: C.black, marginTop: 14 }}>{s.lugar}</div>
        </div>
      ) : null}
      {abs >= s.inglesEm ? (
        <div style={{ position: "absolute", right: 50, top: 520, width: 420, background: C.white, border: `6px solid ${C.black}`, boxShadow: "10px 10px 0 #8A8A8A", padding: "16px 18px", textAlign: "center", scale: `${ing}`, rotate: `${interpolate(ing, [0, 1], [20, 3])}deg` }}>
          <svg width="150" height="90" viewBox="0 0 60 36" style={{ border: "3px solid #111" }}>
            <rect width="60" height="36" fill="#012169" />
            <path d="M0 0 L60 36 M60 0 L0 36" stroke="#fff" strokeWidth="7" />
            <path d="M0 0 L60 36 M60 0 L0 36" stroke="#C8102E" strokeWidth="3" />
            <path d="M30 0 V36 M0 18 H60" stroke="#fff" strokeWidth="11" />
            <path d="M30 0 V36 M0 18 H60" stroke="#C8102E" strokeWidth="6" />
          </svg>
          <div style={{ fontFamily: ANTON, fontSize: 52, color: C.black, lineHeight: 1.05, marginTop: 8 }}>{s.ingles}</div>
          <div style={{ fontFamily: BEBAS, fontSize: 28, color: "#555", letterSpacing: 2 }}>{s.inglesSub}</div>
        </div>
      ) : null}
      {abs >= s.operariosEm ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 950, display: "flex", justifyContent: "center", gap: 18, opacity: wk, translate: `0 ${(1 - wk) * 60}px` }}>
          {names.map((n, i) => (
            <div key={n} style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 180 }}>
              <Worker h={190} seed={i + 9} hat={i % 2 === 0} />
              <div style={{ fontFamily: BEBAS, fontSize: 24, color: C.black, letterSpacing: 1 }}>{n}</div>
            </div>
          ))}
        </div>
      ) : null}
      {abs >= s.tituloEm ? (
        <div style={{ position: "absolute", top: 1190, width: "100%", display: "flex", justifyContent: "center" }}>
          <TornStrip color={C.black} seed={5} style={{ rotate: "-2deg", scale: `${interpolate(since(s.tituloEm), [0, 6], [1.6, 1], { extrapolateRight: "clamp" })}` }}>
            <div style={{ fontFamily: ANTON, fontSize: 92, color: C.white }}>{s.titulo}</div>
          </TornStrip>
        </div>
      ) : null}
      <div style={{ position: "absolute", bottom: 330, width: "100%", textAlign: "center", fontFamily: INTER, fontWeight: 600, fontSize: 24, color: "#444", opacity: interpolate(since(s.lugarEm + 0.3), [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{s.nota}</div>
    </AbsoluteFill>
  );
};

const SceneFila: React.FC = () => {
  const s = D.cenas.fila;
  const { abs, since, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const gray = interpolate(abs, [s.basilioEm - 0.1, s.basilioEm + 0.5], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const year = Math.round(interpolate(abs, [s.contadorEm, s.basilioEm - 0.3], [s.anos[0], s.anos[1]], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const counterOut = interpolate(abs, [s.basilioEm - 0.2, s.basilioEm + 0.2], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const sh = shake(since(s.fimFilaEm), 26, 0.2);
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      <AbsoluteFill style={{ opacity: gray }}>
        <PaperBackground color="#BDBAB4" tint="rgba(0,0,0,0.35)" />
      </AbsoluteFill>
      {counterOut > 0 ? (
        <div style={{ position: "absolute", top: 330, width: "100%", textAlign: "center", opacity: counterOut }}>
          <div style={{ fontFamily: BEBAS, fontSize: 70, letterSpacing: 8, color: C.black }}>{s.anos[0]} →</div>
          <div style={{ fontFamily: ANTON, fontSize: 380, lineHeight: 1, color: C.black, fontVariantNumeric: "tabular-nums", rotate: `${Math.sin(abs * 8) * 0.6}deg` }}>{year}</div>
          <TornStrip color={C.black} seed={4} style={{ display: "inline-block", rotate: "-2deg" }}>
            <div style={{ fontFamily: ANTON, fontSize: 64, color: C.white }}>{s.rotulo}</div>
          </TornStrip>
        </div>
      ) : null}
      {abs >= s.basilioEm ? (
        <>
          <div style={{ position: "absolute", left: 50, top: 190 }}>
            <Polaroid src={A.quadroGol1977} w={640} h={360} caption="O gol de Basílio em quadro (Agência Corinthians)" startFrame={f(s.basilioEm)} rot={-3} fromX={-900} />
          </div>
          <div style={{ position: "absolute", right: 30, top: 300 }}>
            <Cutout src={A.fotoBasilio} width={330} height={720} startFrame={f(s.basilioEm + 0.15)} from={{ x: 500, y: 0, r: 8, s: 0.9 }} outline />
            <div style={{ fontFamily: ANTON, fontSize: 54, color: C.black, textAlign: "center", marginTop: -40, position: "relative" }}>BASÍLIO</div>
          </div>
        </>
      ) : null}
      {abs >= s.placarEm ? (
        <div style={{ position: "absolute", top: 700, left: 60 }}>
          <Scoreboard startFrame={f(s.placarEm)} crestA={A.escudoAtual} crestB={A.escudoPonte} nameA="CORINTHIANS" nameB="PONTE PRETA" a={s.golsCor} b={s.golsAdv} top={s.torneio} bottom={s.data} year="1977" />
        </div>
      ) : null}
      {abs >= s.fimFilaEm ? (
        <>
          <Hook lines={[s.fimFila]} startFrame={f(s.fimFilaEm)} size={130} color={C.black} style={{ position: "absolute", top: 1200, width: "100%" }} />
          <Confetti startFrame={f(s.fimFilaEm)} count={44} colors={[C.black, C.white, "#8A8A8A"]} />
          <Flash startFrame={f(s.fimFilaEm)} dur={6} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};

const SceneDemocracia: React.FC = () => {
  const s = D.cenas.democracia;
  const { abs, since, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const gray = interpolate(abs, [s.socratesEm - 0.1, s.socratesEm + 0.6], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: gray }}>
        <PaperBackground color="#A9A6A0" tint="rgba(0,0,0,0.45)" />
      </AbsoluteFill>
      {abs < s.tituloEm + 0.2 ? (
        <div style={{ position: "absolute", top: 640, width: "100%", textAlign: "center", opacity: interpolate(abs, [s.tituloEm - 0.2, s.tituloEm + 0.2], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          <YearStamp text="ANOS 80" startFrame={f(s.inicio + 0.3)} size={130} rotate={-4} color={C.black} />
          <div style={{ height: 30 }} />
          <YearStamp text={s.ditadura} startFrame={f(s.ditaduraEm)} size={96} rotate={3} color={C.black} />
        </div>
      ) : null}
      {abs >= s.socratesEm ? (
        <div style={{ position: "absolute", left: -10, top: 470 }}>
          <Cutout src={A.fotoSocrates} width={470} height={1000} startFrame={f(s.socratesEm)} from={{ x: -600, y: 60, r: -8, s: 0.9 }} outline />
        </div>
      ) : null}
      {abs >= s.tituloEm ? <Hook lines={s.titulo} startFrame={f(s.tituloEm)} stagger={6} size={128} color={C.black} accentIndex={1} accent={C.black} style={{ position: "absolute", top: 180, width: "100%" }} /> : null}
      {abs >= s.fotoEm ? (
        <div style={{ position: "absolute", right: 40, top: 560 }}>
          <Polaroid src={A.fotoDemocracia} w={560} h={340} caption={'"Dia 15 vote" nas costas (1982)'} startFrame={f(s.fotoEm)} rot={3} />
        </div>
      ) : null}
      {abs >= s.votoEm ? (
        <div style={{ position: "absolute", right: 50, top: 1060 }}>
          <YearStamp text={s.voto} startFrame={f(s.votoEm)} size={60} rotate={-4} color={C.black} />
        </div>
      ) : null}
      <div style={{ position: "absolute", bottom: 330, width: "100%", textAlign: "center", fontFamily: INTER, fontWeight: 600, fontSize: 24, color: "#444", opacity: interpolate(since(s.fotoEm), [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{s.nota}</div>
    </AbsoluteFill>
  );
};

const SceneMundo: React.FC = () => {
  const s = D.cenas.mundo;
  const { fps } = useSceneClock(s.inicio);
  const fr = (t: number) => Math.round((t - s.inicio) * fps);
  return (
    <AbsoluteFill>
      <Sequence name="Mundial 2000"  durationInFrames={fr(s.queda.em)} layout="none">
        <M2000 />
      </Sequence>
      <Sequence name="Série B 2007" from={fr(s.queda.em)} durationInFrames={fr(s.volta.em) - fr(s.queda.em)} layout="none">
        <Queda />
      </Sequence>
      <Sequence name="2012" from={fr(s.volta.em)} layout="none">
        <Volta />
      </Sequence>
    </AbsoluteFill>
  );
};

const M2000: React.FC = () => {
  const m = D.cenas.mundo.m2000;
  const { fps } = useSceneClock(m.em);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 50, top: 190 }}>
        <YearStamp text={m.ano} startFrame={2} size={150} rotate={-6} color={C.black} />
      </div>
      <div style={{ position: "absolute", right: 50, top: 230, width: 520, fontFamily: ANTON, fontSize: 60, color: C.black, lineHeight: 1.02, textAlign: "right", opacity: interpolate(useCurrentFrame(), [4, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{m.titulo}</div>
      <div style={{ position: "absolute", left: 140, top: 460 }}>
        <Polaroid src={A.fotoMundial2000} w={800} h={520} caption="Rincón ergue a taça no Maracanã, 14/01/2000" startFrame={4} rot={-2} />
      </div>
      <div style={{ position: "absolute", left: 70, top: 1150 }}>
        <ScoreRow p={{ ano: "FINAL", ...m.placar }} startFrame={Math.round(0.6 * fps)} />
      </div>
    </AbsoluteFill>
  );
};

const Queda: React.FC = () => {
  const q = D.cenas.mundo.queda;
  const { abs, sp, fps } = useSceneClock(q.em);
  const p = sp(q.em, { damping: 10 });
  return (
    <AbsoluteFill>
      <PaperBackground color="#BDBAB4" tint="rgba(0,0,0,0.35)" />
      <div style={{ position: "absolute", top: 420, width: "100%", textAlign: "center", fontFamily: ANTON, fontSize: 260, color: C.black, translate: `0 ${interpolate(p, [0, 1], [-600, 0])}px` }}>{q.titulo}</div>
      <svg width="220" height="300" viewBox="0 0 220 300" style={{ position: "absolute", left: 430, top: 760, translate: `0 ${(abs - q.em) * 40}px` }}>
        <path d="M110 10 V250 M30 170 L110 270 L190 170" stroke={C.black} strokeWidth="34" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <div style={{ position: "absolute", top: 860, left: 90 }}>
        <YearStamp text={q.ano} startFrame={Math.round(0.15 * fps)} size={140} rotate={-6} color={C.black} />
      </div>
    </AbsoluteFill>
  );
};

const Volta: React.FC = () => {
  const s = D.cenas.mundo;
  const { abs, sp, fps } = useSceneClock(s.volta.em);
  const f = (t: number) => (t - s.volta.em) * fps;
  const lib = sp(s.placares[0].em, { damping: 11 });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 0, top: 120, width: 1080, height: 900 }}>
        <Rays opacity={0.15} />
      </div>
      <div style={{ position: "absolute", top: 180, width: "100%", textAlign: "center" }}>
        <div style={{ fontFamily: BEBAS, fontSize: 64, letterSpacing: 10, color: C.black }}>A VOLTA</div>
        <YearStamp text={s.volta.ano} startFrame={2} size={240} rotate={-4} color={C.black} />
      </div>
      {abs >= s.placares[0].em ? (
        <div style={{ position: "absolute", right: 70, top: 220, background: C.white, border: `6px solid ${C.black}`, boxShadow: "10px 10px 0 #8A8A8A", padding: 12, scale: `${lib}`, rotate: "6deg" }}>
          <Img src={staticFile(A.logoLibertadores)} style={{ height: 110, objectFit: "contain" }} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: 70, top: 760 }}>
        {s.placares.map((p) => (
          <ScoreRow key={p.ano} p={p} startFrame={f(p.em)} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

const SceneStat: React.FC = () => {
  const s = D.cenas.stat;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const sh = shake(since(s.numeroEm), 26, 0.2);
  const fiel = sp(s.fielEm, { damping: 9, stiffness: 220 });
  return (
    <AbsoluteFill style={{ backgroundColor: C.black, translate: `${sh.x}px ${sh.y}px` }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img src={staticFile(A.fotoArena)} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", scale: `${interpolate(abs, [s.inicio, s.fim], [1.3, 1.1])}`, filter: "grayscale(1) contrast(1.2)" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(10,10,10,0.88) 0%, rgba(10,10,10,0.55) 45%, rgba(10,10,10,0.92) 100%)" }} />
      <div style={{ position: "absolute", top: 160, width: "100%", opacity: 1 - fiel }}>
        <StatSlam value={s.numero} startFrame={f(s.numeroEm)} label={s.rotulo} size={440} color={C.white} labelColor={C.white} />
        <div style={{ textAlign: "center", fontFamily: BEBAS, fontSize: 38, letterSpacing: 3, color: C.white, marginTop: 6, opacity: interpolate(since(s.numeroEm + 0.4), [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{s.anos}</div>
      </div>
      {abs >= s.mundiaisEm ? (
        <div style={{ position: "absolute", top: 900, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", gap: 18, opacity: 1 - fiel }}>
          <TornStrip color={C.white} seed={3} style={{ rotate: "-2deg" }}>
            <div style={{ fontFamily: ANTON, fontSize: 62, color: C.black }}>{s.mundiais}</div>
          </TornStrip>
          {abs >= s.torcidaEm ? (
            <TornStrip color={C.white} seed={7} style={{ rotate: "1.5deg", scale: `${interpolate(since(s.torcidaEm), [0, 6], [1.5, 1], { extrapolateRight: "clamp" })}` }}>
              <div style={{ fontFamily: ANTON, fontSize: 62, color: C.black }}>{s.torcida}</div>
            </TornStrip>
          ) : null}
        </div>
      ) : null}
      {abs >= s.fielEm ? (
        <div style={{ position: "absolute", top: 520, width: "100%", textAlign: "center", fontFamily: ANTON, fontSize: 300, color: C.white, scale: `${interpolate(fiel, [0, 1], [2.4, 1])}`, textShadow: "14px 14px 0 #8A8A8A" }}>{s.fiel}</div>
      ) : null}
      <div style={{ position: "absolute", bottom: 300, width: "100%", textAlign: "center", fontFamily: INTER, fontWeight: 600, fontSize: 22, color: "rgba(244,239,230,0.75)" }}>
        {s.extra} · {s.estadio}
      </div>
    </AbsoluteFill>
  );
};

const SceneCta: React.FC = () => {
  const s = D.cenas.cta;
  const { abs, since, sp, fps, frame } = useSceneClock(s.inicio);
  const out = interpolate(abs, [s.apagaEm, s.apagaEm + 0.4], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const darkIn = interpolate(abs, [s.apagaEm, s.apagaEm + 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // o lampião pisca e apaga, voltando ao estado do primeiro frame
  const t = frame - Math.round((s.apagaEm - s.inicio) * fps);
  const on = t < 0 ? 1 : [1, 0, 1, 0, 0, 1, 0][Math.min(6, t)] ?? 0;
  const lampOn = t > 6 ? 0 : on;
  const arrow = sp(s.acaoEm, { damping: 9 });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: out }}>
        <div style={{ position: "absolute", top: 230, width: "100%" }}>
          <Vinheta handle={D.handle} startFrame={0} />
        </div>
        <Hook lines={s.pergunta} startFrame={4} stagger={8} size={118} accentIndex={1} style={{ position: "absolute", top: 560, width: "100%" }} />
        {abs >= s.acaoEm ? (
          <div style={{ position: "absolute", top: 940, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", scale: `${interpolate(arrow, [0, 1], [0.3, 1])}` }}>
            <div style={{ background: C.black, color: C.white, fontFamily: ANTON, fontSize: 110, padding: "6px 50px", rotate: "-3deg", boxShadow: "10px 10px 0 #8A8A8A" }}>{s.acao}</div>
            <svg width="120" height="140" viewBox="0 0 120 140" style={{ marginTop: 20, translate: `0 ${Math.sin(since(s.acaoEm) / 3) * 12}px` }}>
              <path d="M60 0 V105 M18 68 L60 120 L102 68" stroke={C.black} strokeWidth="18" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        ) : null}
      </AbsoluteFill>
      {darkIn > 0 ? (
        <>
          <AbsoluteFill style={{ background: "#0b0b0b", opacity: darkIn * (0.94 - lampOn * 0.5) }} />
          <div style={{ position: "absolute", left: LAMP.left, top: LAMP.top, opacity: darkIn }}>
            <Lamp on={lampOn} />
          </div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};

/* --------------------------- COMPOSIÇÃO --------------------------- */

const scenes = [
  { key: "gancho", C: SceneHook },
  { key: "virada", C: SceneVirada },
  { key: "nascimento", C: SceneNascimento },
  { key: "fila", C: SceneFila },
  { key: "democracia", C: SceneDemocracia },
  { key: "mundo", C: SceneMundo },
  { key: "stat", C: SceneStat },
  { key: "cta", C: SceneCta },
] as const;

const words = D.legendas;
const CaptionsAt: React.FC<{ offset: number; dark?: boolean }> = ({ offset, dark }) => (
  <Captions words={words.map((w) => ({ ...w, start: w.start - offset, end: w.end - offset }))} dark={dark} />
);

export const Corinthians: React.FC = () => {
  const { fps } = useVideoConfig();
  const fr = (t: number) => Math.round(t * fps);
  const c = D.cenas;
  return (
    <AbsoluteFill style={{ backgroundColor: D.paleta.branco, ...ACCENT_VARS }}>
      <PaperBackground />
      {scenes.map(({ key, C: Scene }) => (
        <Sequence key={key} name={key} from={fr(c[key].inicio)} durationInFrames={fr(c[key].fim) - fr(c[key].inicio)}>
          <Scene />
        </Sequence>
      ))}
      {D.transicoesLampiao.map((at, i) => (
        <Sequence key={at} name={`lampiao-transicao-${i}`} from={fr(at - 0.35)} durationInFrames={fr(0.75)}>
          <LampWipe />
        </Sequence>
      ))}
      <Captions words={words} hide={[[0, c.nascimento.inicio], [c.stat.inicio, 999]]} />
      <Sequence name="legendas (escuro)" from={fr(c.stat.inicio)} durationInFrames={fr(c.stat.fim) - fr(c.stat.inicio)}>
        <CaptionsAt offset={c.stat.inicio} dark />
      </Sequence>
      <Seal handle={D.handle} />
      <Grain />
      <Audio src={staticFile(D.audio.mix)} />
    </AbsoluteFill>
  );
};

/** Capa: lampião aceso + "DEBAIXO DE UM LAMPIÃO". */
export const CapaCorinthians: React.FC = () => (
  <AbsoluteFill style={ACCENT_VARS}>
    <PaperBackground />
    <AbsoluteFill style={{ background: "#0b0b0b", opacity: 0.88 }} />
    <div style={{ position: "absolute", left: 540 - 420, top: 760, width: 840, height: 1100, background: "linear-gradient(180deg, rgba(255,210,122,0.4) 0%, rgba(255,210,122,0) 85%)", clipPath: "polygon(42% 0, 58% 0, 100% 100%, 0 100%)" }} />
    <div style={{ position: "absolute", left: 540 - 130, top: 560 }}>
      <Lamp on={1} />
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 1400, display: "flex", justifyContent: "center", gap: 26 }}>
      {[0, 1, 2, 3, 4].map((i) => (
        <Worker key={i} h={i === 2 ? 250 : 220 + (i % 2) * 15} seed={i + 3} hat={i !== 1} />
      ))}
    </div>
    <div style={{ position: "absolute", top: 190, width: "100%", textAlign: "center" }}>
      <div style={{ fontFamily: BEBAS, fontSize: 68, letterSpacing: 14, color: LUZ }}>01/09/1910</div>
      {D.capa.texto.map((l, i) => (
        <div key={i} style={{ fontFamily: ANTON, fontSize: 168, lineHeight: 0.98, color: C.white, textShadow: "7px 7px 0 #555", rotate: `${i ? 1 : -1.5}deg` }}>{l}</div>
      ))}
    </div>
    <Img src={staticFile(A.escudoAtual)} style={{ position: "absolute", right: 60, top: 1180, width: 220, height: 220, objectFit: "contain" }} />
    <div style={{ position: "absolute", bottom: 120, width: "100%", display: "flex", justifyContent: "center" }}>
      <div style={{ background: C.white, color: C.black, fontFamily: ANTON, fontSize: 72, padding: "10px 40px", boxShadow: "8px 8px 0 #555", rotate: "-2deg" }}>{D.capa.sub}</div>
    </div>
    <Seal handle={D.handle} dark />
    <Grain opacity={0.1} />
  </AbsoluteFill>
);
