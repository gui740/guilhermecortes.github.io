import React from "react";
import { AbsoluteFill, interpolate, Sequence } from "remotion";
import { Coin } from "../../../components/Coin";
import { Cutout, Flash, Hook, Rays, StatSlam, Vinheta, YearStamp } from "../../../components/Graphics";
import { TornStrip } from "../../../components/Paper";
import { shake, useSceneClock } from "../../../components/time";
import { ANTON, BEBAS, C, INTER } from "../../../theme";
import { A, COIN, D } from "../data";

const Doze: React.FC = () => {
  const s = D.cenas.stat;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const sh = shake(since(s.numeroEm), 26, 0.2);
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      <div style={{ position: "absolute", left: 0, top: 120, width: 1080, height: 900 }}>
        <Rays color={C.red} opacity={0.22} />
      </div>
      <div style={{ position: "absolute", top: 170, width: "100%" }}>
        <StatSlam value={s.numero} startFrame={f(s.numeroEm)} label={s.rotulo} size={470} />
      </div>
      <div style={{ position: "absolute", top: 830, left: 70, right: 70, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
        {s.quebra.map((q, i) => {
          const p = sp(s.numeroEm + 0.5 + i * 0.22, { damping: 12 });
          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                background: i % 3 === 0 ? C.black : C.white,
                border: `5px solid ${C.black}`,
                padding: "8px 18px",
                scale: `${p}`,
                rotate: `${(i % 2 ? 1 : -1) * 1.5}deg`,
              }}
            >
              <div style={{ fontFamily: ANTON, fontSize: 78, color: C.red, lineHeight: 1 }}>{q.n}</div>
              <div style={{ fontFamily: ANTON, fontSize: 40, color: i % 3 === 0 ? C.white : C.black, lineHeight: 1 }}>{q.t}</div>
            </div>
          );
        })}
      </div>
      {abs >= s.subEm ? (
        <div style={{ position: "absolute", top: 1150, width: "100%", display: "flex", justifyContent: "center" }}>
          <TornStrip color={C.red} seed={9} style={{ rotate: "-2deg", scale: `${interpolate(since(s.subEm), [0, 6], [1.5, 1], { extrapolateRight: "clamp" })}` }}>
            <div style={{ fontFamily: ANTON, fontSize: 56, color: C.white }}>{s.sub}</div>
          </TornStrip>
        </div>
      ) : null}
      <div style={{ position: "absolute", bottom: 330, width: "100%", textAlign: "center", fontFamily: INTER, fontWeight: 600, fontSize: 24, color: "#444" }}>
        {s.nota} · OUTROS: 2 RECOPAS, SUPERCOPA, CONMEBOL E MASTER
      </div>
    </AbsoluteFill>
  );
};

const Ceni: React.FC = () => {
  const c = D.cenas.stat.ceni;
  const { abs, since, fps } = useSceneClock(c.em);
  const f = (t: number) => (t - c.em) * fps;
  const sh = shake(since(c.golsEm + 1.3), 22, 0.25);
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      <div style={{ position: "absolute", right: -60, top: 330 }}>
        <Cutout src={A.fotoCeni} width={720} height={1060} startFrame={0} from={{ x: 600, y: 0, r: 10, s: 1 }} outline />
      </div>
      <div style={{ position: "absolute", left: 50, top: 200, translate: `${interpolate(since(c.em), [0, 8], [-900, 0], { extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) })}px 0` }}>
        <TornStrip color={C.black} seed={12} style={{ rotate: "-2deg" }}>
          <div style={{ fontFamily: BEBAS, fontSize: 40, color: C.red, letterSpacing: 6 }}>O GOLEIRO ARTILHEIRO</div>
          <div style={{ fontFamily: ANTON, fontSize: 96, color: C.white, lineHeight: 1 }}>{c.nome}</div>
        </TornStrip>
      </div>
      <div style={{ position: "absolute", left: 30, top: 520, width: 600 }}>
        <StatSlam value={c.gols} startFrame={f(c.golsEm)} countFrames={Math.round(1.3 * fps)} label={c.rotulo} size={300} />
      </div>
      {abs >= c.punchEm ? (
        <div style={{ position: "absolute", left: 50, top: 1040 }}>
          <YearStamp text={c.punch} startFrame={f(c.punchEm)} size={110} rotate={-7} color={C.red} />
        </div>
      ) : null}
      <Flash startFrame={f(c.golsEm) + Math.round(1.3 * fps)} dur={5} />
    </AbsoluteFill>
  );
};

/** CENA 8 – STAT FINAL */
export const SceneStat: React.FC = () => {
  const s = D.cenas.stat;
  const { fps } = useSceneClock(s.inicio);
  const cut = Math.round((s.ceni.em - s.inicio) * fps);
  return (
    <AbsoluteFill>
      <Sequence name="12 títulos" from={0} durationInFrames={cut} layout="none">
        <Doze />
      </Sequence>
      <Sequence name="Rogério Ceni" from={cut} layout="none">
        <Ceni />
      </Sequence>
    </AbsoluteFill>
  );
};

/** CENA 9 – CTA + LOOP: pergunta, selo e a moeda voltando a girar no ar (emenda com o início). */
export const SceneCta: React.FC = () => {
  const s = D.cenas.cta;
  const { abs, since, sp } = useSceneClock(s.inicio);
  const out = interpolate(abs, [s.moedaSobeEm + 0.6, s.fim - 0.35], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // moeda sobe desacelerando até o ápice exato do primeiro frame
  const u = interpolate(abs, [s.moedaSobeEm, s.fim], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const y = COIN.apexY + (2250 - COIN.apexY) * (1 - u) * (1 - u);
  const ang = COIN.omega * (abs - s.fim);
  const tilt = Math.sin((abs - s.fim) * 3) * 10;
  const arrow = sp(s.acaoEm, { damping: 9 });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: out }}>
        <div style={{ position: "absolute", top: 230, width: "100%" }}>
          <Vinheta handle={D.handle} startFrame={0} />
        </div>
        <Hook lines={s.pergunta} startFrame={4} stagger={8} size={118} accentIndex={1} style={{ position: "absolute", top: 560, width: "100%" }} />
        {abs >= s.acaoEm ? (
          <div style={{ position: "absolute", top: 960, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", scale: `${interpolate(arrow, [0, 1], [0.3, 1])}` }}>
            <div style={{ background: C.red, color: C.white, fontFamily: ANTON, fontSize: 110, padding: "6px 50px", rotate: "-3deg", boxShadow: `10px 10px 0 ${C.black}` }}>{s.acao}</div>
            <svg width="120" height="140" viewBox="0 0 120 140" style={{ marginTop: 20, translate: `0 ${Math.sin(since(s.acaoEm) / 3) * 12}px` }}>
              <path d="M60 0 V105 M18 68 L60 120 L102 68" stroke={C.black} strokeWidth="18" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        ) : null}
      </AbsoluteFill>
      {abs >= s.moedaSobeEm ? (
        <div style={{ position: "absolute", left: COIN.x - COIN.size / 2, top: y - COIN.size / 2 }}>
          <Coin id="loop" size={COIN.size} angle={ang} tilt={tilt} crest={A.escudoAtual} blur={1.5} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
