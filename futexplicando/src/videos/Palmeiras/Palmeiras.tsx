import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Img, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import raw from "../../data/palmeiras.json";
import { Captions } from "../../components/Captions";
import { Confetti, Cutout, Flash, Hook, Rays, Scoreboard, Seal, StatSlam, Vinheta, YearStamp } from "../../components/Graphics";
import { Grain, PaperBackground, TornStrip } from "../../components/Paper";
import { Pig, SplitFlap } from "../../components/SplitFlap";
import { rand, shake, useSceneClock } from "../../components/time";
import { ANTON, BEBAS, C, INTER } from "../../theme";

const D = raw;
const A = raw.assets as Record<string, string>;
const L = raw.letreiro;
const VERDE = D.paleta.verde;

/** Posição do letreiro no gancho e no loop final (precisam ser idênticas). */
const BOARD = { top: 640, tile: 80 };

const Board: React.FC<{ steps: { at: number; lines: string[] }[]; tile?: number }> = ({ steps, tile = BOARD.tile }) => (
  <SplitFlap steps={steps} cols={11} tile={tile} />
);

const BrazilFlag: React.FC<{ w: number; wave: number }> = ({ w, wave }) => (
  <svg width={w} height={w * 0.7} viewBox="0 0 200 140" style={{ filter: "drop-shadow(10px 10px 0 #111)" }}>
    <defs>
      <clipPath id="fl">
        <path d={`M0 ${10 + wave * 4} Q50 ${0 - wave * 4} 100 ${10 + wave * 4} T200 ${10 + wave * 4} V${130 + wave * 4} Q150 ${140 - wave * 4} 100 ${130 + wave * 4} T0 ${130 + wave * 4} Z`} />
      </clipPath>
    </defs>
    <g clipPath="url(#fl)">
      <rect width="200" height="140" fill="#009739" />
      <polygon points="100,18 182,70 100,122 18,70" fill="#FEDD00" />
      <circle cx="100" cy="70" r="30" fill="#012169" />
      <path d="M72 64 Q100 56 128 74" stroke="#F4EFE6" strokeWidth="5" fill="none" />
    </g>
  </svg>
);

/** Transição: grade de placas que viram cobrindo a tela. */
const FlapWipe: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps; // 0 .. 0.7
  const cols = 6, rows = 10, w = 1080 / cols, h = 1920 / rows;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: cols * rows }).map((_, i) => {
        const c = i % cols, r = Math.floor(i / cols);
        const delay = (r + c) * 0.014 + rand(i) * 0.03;
        const inP = interpolate(t, [delay, delay + 0.12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const outP = interpolate(t, [0.38 + delay, 0.5 + delay], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const s = inP * (1 - outP);
        if (s <= 0) return null;
        return (
          <div key={i} style={{ position: "absolute", left: c * w, top: r * h, width: w + 1, height: h + 1, scale: `1 ${s}`, background: (r + c) % 2 ? "#1a1a1a" : VERDE, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ANTON, fontSize: h * 0.6, color: "rgba(244,239,230,0.12)" }}>
            P
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/* ------------------------- CENAS ------------------------- */

const SceneHook: React.FC = () => {
  const s = D.cenas.gancho;
  const { abs, since, fps } = useSceneClock(s.inicio);
  const sh = shake(since(s.carimboEm), 16, 0.25);
  const zoom = interpolate(abs, [0, s.fim], [1, 1.08]);
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      <div style={{ position: "absolute", top: 230, width: "100%", textAlign: "center", fontFamily: BEBAS, fontSize: 64, letterSpacing: 10, color: C.red, opacity: interpolate(abs, [0.25, 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        {s.kicker}
      </div>
      <div style={{ position: "absolute", top: BOARD.top, width: "100%", display: "flex", justifyContent: "center", scale: `${zoom}` }}>
        <Board steps={[{ at: -999, lines: L.inicial }, { at: (s.trocaEm - s.inicio) * fps, lines: L.final }]} />
      </div>
      <div style={{ position: "absolute", top: 980, width: "100%", textAlign: "center" }}>
        <YearStamp text={s.carimbo} startFrame={(s.carimboEm - s.inicio) * fps} size={200} rotate={-8} color={C.black} sub="2ª GUERRA MUNDIAL" />
      </div>
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
        <Rays opacity={0.3} count={22} />
      </div>
      <div style={{ position: "absolute", left: 540 - 330, top: 480, width: 660, height: 660, scale: `${interpolate(p, [0, 1], [3.5, 1])}`, opacity: interpolate(p, [0, 0.15], [0, 1], { extrapolateRight: "clamp" }), rotate: `${interpolate(p, [0, 1], [-25, 0]) + Math.sin(abs * 2) * 1.5}deg` }}>
        <Img src={staticFile(A.escudoAtual)} style={{ width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(18px 22px 0 ${C.black})` }} />
      </div>
      <div style={{ position: "absolute", top: 160, width: "100%", textAlign: "center" }}>
        <div style={{ fontFamily: BEBAS, fontSize: 78, letterSpacing: 10, color: C.black }}>{s.linha1}</div>
        <Hook lines={[s.linha2]} startFrame={6} size={190} color={C.red} />
      </div>
      <div style={{ position: "absolute", top: 1230, width: "100%", display: "flex", justifyContent: "center" }}>
        <div style={{ background: C.black, color: C.white, fontFamily: ANTON, fontSize: 70, padding: "10px 40px", rotate: "-2deg", boxShadow: `8px 8px 0 ${C.red}`, clipPath: `inset(0 ${interpolate(since(s.inicio + 0.7), [0, 8], [100, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}% 0 0)` }}>
          {s.linha3}
        </div>
      </div>
      <Flash startFrame={0} dur={7} />
    </AbsoluteFill>
  );
};

const SceneNascimento: React.FC = () => {
  const s = D.cenas.nascimento;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const titleP = sp(s.nomeEm, { damping: 11 });
  return (
    <AbsoluteFill>
      {/* faixas da bandeira italiana em papel rasgado */}
      {["#0B7A3E", "#F4EFE6", "#CE2B37"].map((c, i) => (
        <div key={i} style={{ position: "absolute", top: 0, bottom: 0, left: i * 360, width: 360, background: c, opacity: 0.16 * interpolate(since(s.inicio + i * 0.1), [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), translate: `0 ${interpolate(since(s.inicio + i * 0.1), [0, 12], [-1920, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) })}px` }} />
      ))}
      <div style={{ position: "absolute", top: 210, width: "100%", textAlign: "center" }}>
        <YearStamp text={s.data} startFrame={f(s.dataEm)} size={150} rotate={-5} color={C.red} />
      </div>
      <div style={{ position: "absolute", left: 540 - 230, top: 480, scale: `${interpolate(titleP, [0, 1], [1, 0.85])}` }}>
        <Cutout src={A.escudo1915} width={460} height={460} startFrame={f(s.inicio + 0.35)} from={{ x: 0, y: 500, r: -20, s: 0.4 }} />
        <div style={{ textAlign: "center", fontFamily: INTER, fontWeight: 700, fontSize: 26, color: "#444", marginTop: 10 }}>{s.legendaEscudo}</div>
      </div>
      {abs >= s.notaEm && abs < s.nomeEm + 0.2 ? (
        <div style={{ position: "absolute", top: 1100, width: "100%", display: "flex", justifyContent: "center", translate: `${interpolate(since(s.notaEm), [0, 8], [-1100, 0], { extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) })}px 0`, opacity: 1 - titleP }}>
          <TornStrip color={C.black} seed={3} style={{ rotate: "-2deg" }}>
            <div style={{ fontFamily: ANTON, fontSize: 72, color: C.white }}>
              <span style={{ color: "#CE2B37" }}>■</span> {s.nota} <span style={{ color: "#0B7A3E" }}>■</span>
            </div>
          </TornStrip>
        </div>
      ) : null}
      {abs >= s.nomeEm ? <Hook lines={[s.nome]} startFrame={f(s.nomeEm)} size={150} color={C.red} style={{ position: "absolute", top: 1110, width: "100%" }} /> : null}
    </AbsoluteFill>
  );
};

const SceneGuerra: React.FC = () => {
  const s = D.cenas.guerra;
  const { abs, since, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const swap = interpolate(abs, [s.trocaFinalEm + 0.5, s.trocaFinalEm + 0.8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const shA = shake(since(s.anoEm), 14, 0.25);
  const shB = shake(since(s.trocaFinalEm + 0.6), 18, 0.25);
  const push = interpolate(abs, [s.inicio, s.fim], [1, 1.07]);
  return (
    <AbsoluteFill>
      <PaperBackground color="#BDBAB4" tint="rgba(0,0,0,0.35)" />
      <AbsoluteFill style={{ filter: "grayscale(1) contrast(1.15)", scale: `${push}`, translate: `${shA.x + shB.x}px ${shA.y + shB.y}px` }}>
        <div style={{ position: "absolute", top: 170, width: "100%", textAlign: "center" }}>
          <YearStamp text={s.ano} startFrame={f(s.anoEm)} size={150} rotate={-4} color={C.black} />
        </div>
        {s.frases.map((fr, i) => (
          <div key={i} style={{ position: "absolute", top: 390 + i * 120, ...(i ? { right: 50 } : { left: 60 }) }}>
            <YearStamp text={fr.t} startFrame={f(fr.em)} size={i ? 62 : 80} rotate={i ? 4 : -3} color={C.black} />
          </div>
        ))}
        <div style={{ position: "absolute", left: 540 - 170, top: 620, width: 340, height: 340 }}>
          <Img src={staticFile(A.escudo1937)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", opacity: 1 - swap, filter: `drop-shadow(12px 14px 0 ${C.black})` }} />
          <Img src={staticFile(A.escudo1942)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", opacity: swap, scale: `${1 + 0.15 * Math.max(0, 1 - Math.abs(swap - 0.5) * 2)}`, filter: `drop-shadow(12px 14px 0 ${C.black})` }} />
        </div>
        <div style={{ position: "absolute", top: 1010, width: "100%", display: "flex", justifyContent: "center" }}>
          <Board tile={66} steps={[{ at: -999, lines: L.inicial }, { at: f(s.trocaMeioEm), lines: L.meio }, { at: f(s.trocaFinalEm), lines: L.final }]} />
        </div>
        {abs >= s.trocaFinalEm + 0.6 ? (
          <div style={{ position: "absolute", top: 870, right: 70 }}>
            <YearStamp text={s.data} startFrame={f(s.trocaFinalEm + 0.6)} size={64} rotate={6} color={C.black} />
          </div>
        ) : null}
      </AbsoluteFill>
      <div style={{ position: "absolute", bottom: 330, left: 80, right: 80, textAlign: "center", fontFamily: INTER, fontWeight: 600, fontSize: 24, color: "#333", opacity: interpolate(since(s.frases[1].em + 0.3), [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        {s.nota}
      </div>
    </AbsoluteFill>
  );
};

const SceneArrancada: React.FC = () => {
  const s = D.cenas.arrancada;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const photoIn = sp(s.inicio, { damping: 14 });
  const flagP = sp(s.bandeiraEm, { damping: 11 });
  const titleP = sp(s.tituloEm, { damping: 9, stiffness: 220 });
  const sh = shake(since(s.tituloEm), 22, 0.22);
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      <div style={{ position: "absolute", left: 80, top: 200, width: 920, background: C.white, padding: "22px 22px 70px", boxShadow: `14px 16px 0 ${C.black}`, rotate: `${interpolate(photoIn, [0, 1], [10, -2.5])}deg`, translate: `${interpolate(photoIn, [0, 1], [900, 0])}px ${titleP * -40}px`, opacity: 1 - titleP * 0.25 }}>
        <div style={{ width: "100%", height: 470, overflow: "hidden" }}>
          <Img src={staticFile(A.fotoArrancada)} style={{ width: "100%", height: "100%", objectFit: "cover", scale: `${interpolate(abs, [s.inicio, s.fim], [1.04, 1.18])}` }} />
        </div>
        <div style={{ fontFamily: INTER, fontWeight: 700, fontSize: 28, color: "#555", marginTop: 14 }}>O time entra com a bandeira do Brasil, 20/09/1942</div>
      </div>
      <div style={{ position: "absolute", top: 150, left: 60 }}>
        <TornStrip color={C.red} seed={2} style={{ rotate: "-3deg", scale: `${interpolate(since(s.inicio + 0.1), [0, 6], [1.6, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}` }}>
          <div style={{ fontFamily: ANTON, fontSize: 56, color: C.white }}>{s.kicker}</div>
        </TornStrip>
      </div>
      {abs < s.tituloEm + 0.25 ? (
        <div style={{ position: "absolute", top: 840, left: 60, opacity: 1 - titleP }}>
          <Scoreboard startFrame={f(s.placarEm)} crestA={A.escudo1942} crestB={A.escudoSaoPaulo} nameA="PALMEIRAS" nameB="SÃO PAULO" a={s.golsPal} b={s.golsAdv} top={s.torneio} bottom={s.data} year="1942" />
        </div>
      ) : null}
      {abs >= s.bandeiraEm ? (
        <div style={{ position: "absolute", right: 40, top: 560, rotate: `${interpolate(flagP, [0, 1], [30, 8])}deg`, scale: `${flagP}` }}>
          <BrazilFlag w={300} wave={Math.sin(abs * 6)} />
        </div>
      ) : null}
      {abs >= s.tituloEm ? (
        <>
          <Hook lines={s.titulo} startFrame={f(s.tituloEm)} stagger={6} size={185} color={C.black} accentIndex={1} style={{ position: "absolute", top: 860, width: "100%" }} />
          <Confetti startFrame={f(s.tituloEm)} count={40} colors={[VERDE, C.white, "#FEDD00"]} />
        </>
      ) : null}
      <Flash startFrame={0} dur={6} />
    </AbsoluteFill>
  );
};

const ScenePorco: React.FC = () => {
  const s = D.cenas.porco;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const pigIn = sp(s.inicio + 0.2, { damping: 10 });
  const insult = sp(s.insultoEm, { damping: 8, stiffness: 260 });
  const turn = sp(s.ano2Em + 0.4, { damping: 9 });
  const mascot = abs >= s.ano2Em + 0.4;
  return (
    <AbsoluteFill>
      {mascot ? (
        <div style={{ position: "absolute", left: 0, top: 260, width: 1080, height: 1080 }}>
          <Rays opacity={0.3 * turn} />
        </div>
      ) : null}
      <div style={{ position: "absolute", top: 180, left: 70 }}>
        <YearStamp text={s.ano1} startFrame={f(s.ano1Em)} size={140} rotate={-6} color={C.black} sub="RIVAIS" />
      </div>
      {abs >= s.ano2Em ? (
        <div style={{ position: "absolute", top: 180, right: 70 }}>
          <YearStamp text={s.ano2} startFrame={f(s.ano2Em)} size={140} rotate={5} color={C.red} sub="TORCIDA" />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: 540 - 240, top: 560, scale: `${pigIn * (1 + 0.1 * turn * Math.sin(Math.min(1, since(s.ano2Em + 0.4) / 12) * Math.PI))}`, rotate: `${Math.sin(abs * 3) * 3}deg`, filter: mascot ? "none" : "grayscale(0.8)" }}>
        <Pig size={480} />
        {mascot ? (
          <div style={{ position: "absolute", left: 90, right: 90, bottom: 40, height: 70, background: VERDE, border: `6px solid ${C.black}`, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ANTON, fontSize: 44, color: C.white, scale: `${turn}` }}>
            PORCO
          </div>
        ) : null}
      </div>
      {abs >= s.insultoEm && !mascot ? (
        <div style={{ position: "absolute", right: 70, top: 480, scale: `${insult}`, rotate: "8deg", background: C.white, border: `7px solid ${C.black}`, borderRadius: 30, padding: "10px 34px", fontFamily: ANTON, fontSize: 90, color: C.black, boxShadow: `8px 8px 0 ${C.black}` }}>
          {s.insulto}
        </div>
      ) : null}
      {abs >= s.viradaEm ? (
        <>
          <div style={{ position: "absolute", top: 1110, width: "100%", display: "flex", justifyContent: "center" }}>
            <TornStrip color={C.red} seed={6} style={{ rotate: "-2deg", scale: `${interpolate(since(s.viradaEm), [0, 6], [1.6, 1], { extrapolateRight: "clamp" })}` }}>
              <div style={{ fontFamily: ANTON, fontSize: 70, color: C.white }}>{s.virada}</div>
            </TornStrip>
          </div>
          <Confetti startFrame={f(s.viradaEm)} count={34} colors={[VERDE, C.white, "#F2A7B5"]} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};

const ScoreRow: React.FC<{ p: (typeof D.cenas.glorias.placares)[number]; startFrame: number }> = ({ p, startFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const k = interpolate(frame - startFrame, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
  void fps;
  return (
    <div style={{ width: 600, translate: `${(1 - k) * -700}px 0`, marginBottom: 18, position: "relative", zIndex: 2 }}>
      <div style={{ display: "flex", alignItems: "center", background: C.black, border: `5px solid ${C.white}`, boxShadow: `8px 8px 0 ${C.red}`, padding: "8px 16px", gap: 12 }}>
        <div style={{ fontFamily: ANTON, fontSize: 44, color: C.red, width: 110 }}>{p.ano}</div>
        <Img src={staticFile(A.escudoAtual)} style={{ height: 70, width: 70, objectFit: "contain" }} />
        <div style={{ fontFamily: ANTON, fontSize: 64, color: C.white }}>{p.golsPal}</div>
        <div style={{ fontFamily: ANTON, fontSize: 40, color: C.red }}>×</div>
        <div style={{ fontFamily: ANTON, fontSize: 64, color: C.white }}>{p.golsAdv}</div>
        <Img src={staticFile(A[p.escudoAdv])} style={{ height: 70, width: 70, objectFit: "contain" }} />
        <div style={{ fontFamily: ANTON, fontSize: 36, color: C.white }}>{p.adv}</div>
      </div>
      <div style={{ fontFamily: BEBAS, fontSize: 30, letterSpacing: 2, color: C.black, background: C.white, display: "inline-block", padding: "2px 12px", border: `4px solid ${C.black}`, borderTop: "none" }}>{p.detalhe}</div>
    </div>
  );
};

const SceneGlorias: React.FC = () => {
  const s = D.cenas.glorias;
  const { fps } = useSceneClock(s.inicio);
  const fr = (t: number) => Math.round((t - s.inicio) * fps);
  return (
    <AbsoluteFill>
      <Sequence name="Academias"  durationInFrames={fr(s.liberta99.em)} layout="none">
        <Academia />
      </Sequence>
      <Sequence name="Libertadores 99" from={fr(s.liberta99.em)} durationInFrames={fr(s.quedas.em) - fr(s.liberta99.em)} layout="none">
        <Liberta99 />
      </Sequence>
      <Sequence name="Série B" from={fr(s.quedas.em)} durationInFrames={fr(s.abel.em) - fr(s.quedas.em)} layout="none">
        <Quedas />
      </Sequence>
      <Sequence name="Abel" from={fr(s.abel.em)} layout="none">
        <AbelBi />
      </Sequence>
    </AbsoluteFill>
  );
};

const NameTag: React.FC<{ kicker: string; name: string; startFrame: number; seed?: number }> = ({ kicker, name, startFrame, seed = 4 }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ translate: `${interpolate(frame - startFrame, [0, 8], [-900, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) })}px 0` }}>
      <TornStrip color={C.black} seed={seed} style={{ rotate: "-2deg" }}>
        <div style={{ fontFamily: BEBAS, fontSize: 40, color: C.red, letterSpacing: 6 }}>{kicker}</div>
        <div style={{ fontFamily: ANTON, fontSize: 96, color: C.white, lineHeight: 1 }}>{name}</div>
      </TornStrip>
    </div>
  );
};

const Academia: React.FC = () => {
  const s = D.cenas.glorias.academia;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", right: -40, top: 360 }}>
        <Cutout src={A.fotoAdemir} width={640} height={980} startFrame={0} from={{ x: 600, y: 60, r: 8, s: 0.9 }} outline />
      </div>
      <div style={{ position: "absolute", left: 50, top: 200 }}>
        <NameTag kicker={s.titulo} name={s.nome} startFrame={2} />
      </div>
      <div style={{ position: "absolute", left: 70, top: 560 }}>
        <YearStamp text={s.sub} startFrame={8} size={64} rotate={-5} color={C.red} />
      </div>
    </AbsoluteFill>
  );
};

const Liberta99: React.FC = () => {
  const s = D.cenas.glorias.liberta99;
  const { sp } = useSceneClock(s.em);
  const p = sp(s.em, { damping: 13 });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 70, top: 470, width: 940, background: C.white, padding: "20px 20px 60px", boxShadow: `14px 16px 0 ${C.black}`, rotate: `${interpolate(p, [0, 1], [-10, 2])}deg`, translate: `${interpolate(p, [0, 1], [-900, 0])}px 0` }}>
        <div style={{ width: "100%", height: 600, overflow: "hidden" }}>
          <Img src={staticFile(A.fotoMarcos)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </div>
        <div style={{ fontFamily: ANTON, fontSize: 52, color: C.black, marginTop: 8 }}>{s.nome} · <span style={{ color: C.red }}>{s.sub}</span></div>
      </div>
      <div style={{ position: "absolute", left: 60, top: 190 }}>
        <YearStamp text={s.ano} startFrame={2} size={150} rotate={-6} color={C.red} />
      </div>
      <div style={{ position: "absolute", right: 70, top: 200, background: C.white, border: `6px solid ${C.black}`, boxShadow: `10px 10px 0 ${C.red}`, padding: 16, display: "flex", flexDirection: "column", alignItems: "center", scale: `${p}` }}>
        <Img src={staticFile(A.logoLibertadores)} style={{ height: 130, objectFit: "contain" }} />
        <div style={{ fontFamily: ANTON, fontSize: 40, color: C.black }}>{s.titulo}</div>
      </div>
    </AbsoluteFill>
  );
};

const Quedas: React.FC = () => {
  const s = D.cenas.glorias.quedas;
  const { abs, sp, fps } = useSceneClock(s.em);
  const p = sp(s.em, { damping: 10 });
  return (
    <AbsoluteFill>
      <PaperBackground color="#BDBAB4" tint="rgba(0,0,0,0.35)" />
      <div style={{ position: "absolute", top: 420, width: "100%", textAlign: "center", fontFamily: ANTON, fontSize: 260, color: C.black, translate: `0 ${interpolate(p, [0, 1], [-600, 0])}px` }}>
        {s.titulo}
      </div>
      <svg width="220" height="300" viewBox="0 0 220 300" style={{ position: "absolute", left: 430, top: 760, translate: `0 ${(abs - s.em) * 40}px` }}>
        <path d="M110 10 V250 M30 170 L110 270 L190 170" stroke={C.black} strokeWidth="34" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      {s.anos.map((y, i) => (
        <div key={y} style={{ position: "absolute", top: 820 + i * 180, left: i ? 640 : 70 }}>
          <YearStamp text={y} startFrame={Math.round((0.2 + i * 0.5) * fps)} size={120} rotate={i ? 6 : -6} color={C.black} />
        </div>
      ))}
    </AbsoluteFill>
  );
};

const AbelBi: React.FC = () => {
  const s = D.cenas.glorias;
  const { abs, fps } = useSceneClock(s.abel.em);
  const f = (t: number) => (t - s.abel.em) * fps;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", right: -90, top: 420 }}>
        <Cutout src={A.fotoAbel} width={560} height={860} startFrame={0} from={{ x: 600, y: 60, r: 8, s: 0.9 }} outline />
      </div>
      <div style={{ position: "absolute", left: 50, top: 200 }}>
        <NameTag kicker="A VOLTA POR CIMA" name={s.abel.nome} startFrame={2} seed={9} />
      </div>
      {abs >= s.abel.biEm ? (
        <div style={{ position: "absolute", left: 40, top: 620 }}>
          <div style={{ fontFamily: ANTON, fontSize: 84, color: C.red, textShadow: `5px 5px 0 ${C.black}`, marginBottom: 14, scale: `${interpolate(abs - s.abel.biEm, [0, 0.2], [1.6, 1], { extrapolateRight: "clamp" })}`, transformOrigin: "left" }}>BI DA LIBERTADORES</div>
          {s.placares.map((p, i) => (
            <ScoreRow key={p.ano} p={p} startFrame={f(s.abel.biEm + 0.15 + i * 0.3)} />
          ))}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const SceneStat: React.FC = () => {
  const s = D.cenas.stat;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const sh = shake(since(s.numeroEm), 26, 0.2);
  const abel = sp(s.abel.em, { damping: 12 });
  return (
    <AbsoluteFill style={{ backgroundColor: C.black, translate: `${sh.x}px ${sh.y}px` }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img src={staticFile(A.fotoAllianz)} style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", scale: `${interpolate(abs, [s.inicio, s.fim], [1.25, 1.05])}`, rotate: `${interpolate(abs, [s.inicio, s.fim], [-4, 2])}deg` }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(0,40,20,0.85) 0%, rgba(0,60,30,0.55) 45%, rgba(0,30,15,0.92) 100%)` }} />
      <div style={{ position: "absolute", top: 170, width: "100%" }}>
        <StatSlam value={s.numero} startFrame={f(s.numeroEm)} label={s.rotulo} size={470} color={C.white} labelColor={C.white} />
      </div>
      {abs >= s.subEm ? (
        <div style={{ position: "absolute", top: 860, width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
          <TornStrip color={C.white} seed={8} style={{ rotate: "-2deg", scale: `${interpolate(since(s.subEm), [0, 6], [1.5, 1], { extrapolateRight: "clamp" })}` }}>
            <div style={{ fontFamily: ANTON, fontSize: 68, color: VERDE }}>{s.sub}</div>
          </TornStrip>
          <div style={{ fontFamily: BEBAS, fontSize: 36, letterSpacing: 3, color: C.white, marginTop: 14 }}>{s.anos}</div>
        </div>
      ) : null}
      {abs >= s.abel.em ? (
        <div style={{ position: "absolute", top: 1110, left: 90, right: 90, background: C.white, border: `6px solid ${C.black}`, boxShadow: `10px 10px 0 ${VERDE}`, padding: "12px 24px", textAlign: "center", scale: `${abel}`, rotate: "1.5deg" }}>
          <div style={{ fontFamily: ANTON, fontSize: 70, color: VERDE, lineHeight: 1 }}>{s.abel.titulo}</div>
          <div style={{ fontFamily: ANTON, fontSize: 34, color: C.black }}>{s.abel.sub}</div>
        </div>
      ) : null}
      <div style={{ position: "absolute", bottom: 300, width: "100%", textAlign: "center", fontFamily: INTER, fontWeight: 600, fontSize: 22, color: "rgba(244,239,230,0.75)" }}>{s.estadio} · foto: palmeiras.com.br</div>
    </AbsoluteFill>
  );
};

const SceneCta: React.FC = () => {
  const s = D.cenas.cta;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const out = interpolate(abs, [s.letreiroVoltaEm - 0.7, s.letreiroVoltaEm - 0.2], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const boardIn = interpolate(abs, [s.letreiroVoltaEm - 0.6, s.letreiroVoltaEm - 0.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const arrow = sp(s.acaoEm, { damping: 9 });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: out }}>
        <div style={{ position: "absolute", top: 230, width: "100%" }}>
          <Vinheta handle={D.handle} startFrame={0} />
        </div>
        <Hook lines={s.pergunta} startFrame={4} stagger={8} size={118} accentIndex={1} style={{ position: "absolute", top: 560, width: "100%" }} />
        <div style={{ position: "absolute", top: 860, width: "100%", textAlign: "center", fontFamily: BEBAS, fontSize: 44, letterSpacing: 4, color: C.black, opacity: interpolate(since(s.inicio + 0.6), [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{s.extra}</div>
        {abs >= s.acaoEm ? (
          <div style={{ position: "absolute", top: 960, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", scale: `${interpolate(arrow, [0, 1], [0.3, 1])}` }}>
            <div style={{ background: C.red, color: C.white, fontFamily: ANTON, fontSize: 110, padding: "6px 50px", rotate: "-3deg", boxShadow: `10px 10px 0 ${C.black}` }}>{s.acao}</div>
            <svg width="120" height="140" viewBox="0 0 120 140" style={{ marginTop: 20, translate: `0 ${Math.sin(since(s.acaoEm) / 3) * 12}px` }}>
              <path d="M60 0 V105 M18 68 L60 120 L102 68" stroke={C.black} strokeWidth="18" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        ) : null}
      </AbsoluteFill>
      {boardIn > 0 ? (
        <div style={{ position: "absolute", top: BOARD.top, width: "100%", display: "flex", justifyContent: "center", opacity: boardIn, translate: `0 ${(1 - boardIn) * 80}px` }}>
          <Board steps={[{ at: -999, lines: L.final }, { at: (s.letreiroVoltaEm - s.inicio) * fps, lines: L.inicial }]} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/* ------------------------- COMPOSIÇÃO ------------------------- */

const scenes = [
  { key: "gancho", C: SceneHook },
  { key: "virada", C: SceneVirada },
  { key: "nascimento", C: SceneNascimento },
  { key: "guerra", C: SceneGuerra },
  { key: "arrancada", C: SceneArrancada },
  { key: "porco", C: ScenePorco },
  { key: "glorias", C: SceneGlorias },
  { key: "stat", C: SceneStat },
  { key: "cta", C: SceneCta },
] as const;

const words = D.legendas;

const CaptionsAt: React.FC<{ offset: number; dark?: boolean }> = ({ offset, dark }) => (
  <Captions words={words.map((w) => ({ ...w, start: w.start - offset, end: w.end - offset }))} dark={dark} />
);

export const Palmeiras: React.FC = () => {
  const { fps } = useVideoConfig();
  const fr = (t: number) => Math.round(t * fps);
  const c = D.cenas;
  return (
    <AbsoluteFill style={{ backgroundColor: D.paleta.branco, ["--accent" as string]: VERDE } as React.CSSProperties}>
      <PaperBackground />
      {scenes.map(({ key, C: Scene }) => (
        <Sequence key={key} name={key} from={fr(c[key].inicio)} durationInFrames={fr(c[key].fim) - fr(c[key].inicio)}>
          <Scene />
        </Sequence>
      ))}
      {D.transicoesLetreiro.map((at, i) => (
        <Sequence key={at} name={`letreiro-transicao-${i}`} from={fr(at - 0.35)} durationInFrames={fr(0.75)}>
          <FlapWipe />
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

/** Capa: letreiro trocando de nome + "MUDOU DE NOME NA MARRA". */
export const CapaPalmeiras: React.FC = () => (
  <AbsoluteFill style={{ ["--accent" as string]: VERDE } as React.CSSProperties}>
    <PaperBackground />
    <div style={{ position: "absolute", left: -60, top: 520, width: 1200, height: 1200 }}>
      <Rays opacity={0.25} count={24} />
    </div>
    <Img src={staticFile(A.escudoAtual)} style={{ position: "absolute", left: 540 - 300, top: 1050, width: 600, height: 600, filter: `drop-shadow(16px 18px 0 ${C.black})` }} />
    <div style={{ position: "absolute", top: 210, width: "100%", textAlign: "center" }}>
      <div style={{ fontFamily: BEBAS, fontSize: 70, letterSpacing: 14, color: C.red }}>1914 → 1942</div>
      {D.capa.texto.map((l, i) => (
        <div key={i} style={{ fontFamily: ANTON, fontSize: 168, lineHeight: 0.98, color: i ? C.red : C.black, textShadow: i ? `7px 7px 0 ${C.black}` : `7px 7px 0 ${C.red}`, rotate: `${i ? 1 : -1.5}deg` }}>{l}</div>
      ))}
    </div>
    <div style={{ position: "absolute", top: 640, width: "100%", display: "flex", justifyContent: "center", rotate: "-2deg" }}>
      <SplitFlap steps={[{ at: -999, lines: ["PALESTRA", "ITÁLIA"] }]} cols={11} tile={70} />
    </div>
    <div style={{ position: "absolute", top: 930, width: "100%", textAlign: "center", fontFamily: ANTON, fontSize: 120, color: C.red }}>↓</div>
    <div style={{ position: "absolute", bottom: 150, width: "100%", display: "flex", justifyContent: "center" }}>
      <div style={{ background: C.black, color: C.white, fontFamily: ANTON, fontSize: 72, padding: "10px 40px", boxShadow: `8px 8px 0 ${C.red}`, rotate: "-2deg" }}>{D.capa.sub}</div>
    </div>
    <Seal handle={D.handle} />
    <Grain opacity={0.1} />
  </AbsoluteFill>
);
