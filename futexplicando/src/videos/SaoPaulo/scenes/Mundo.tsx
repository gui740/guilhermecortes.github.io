import React from "react";
import { AbsoluteFill, Img, interpolate, Sequence, staticFile } from "remotion";
import { Cutout, Flash, Pitch, Scoreboard, Timeline, YearStamp } from "../../../components/Graphics";
import { TornStrip } from "../../../components/Paper";
import { shake, useSceneClock } from "../../../components/time";
import { ANTON, BEBAS, C } from "../../../theme";
import { A, D } from "../data";

const s = D.cenas.mundo;

const Tele: React.FC = () => {
  const t = s.tele;
  const { abs, since, sp, fps } = useSceneClock(t.em);
  const f = (x: number) => (x - t.em) * fps;
  const lib = sp(t.biLibertaEm, { damping: 11 });
  const mun = sp(t.biMundialEm, { damping: 11 });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: -40, top: 560 }}>
        <Cutout src={A.fotoTele} width={700} height={860} startFrame={0} from={{ x: -600, y: 100, r: -8, s: 0.9 }} outline />
      </div>
      <div style={{ position: "absolute", left: 50, top: 210, translate: `${interpolate(since(t.em + 0.1), [0, 8], [-900, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) })}px 0` }}>
        <TornStrip color={C.black} seed={4} style={{ rotate: "-2deg" }}>
          <div style={{ fontFamily: BEBAS, fontSize: 40, color: C.red, letterSpacing: 6 }}>A ERA</div>
          <div style={{ fontFamily: ANTON, fontSize: 100, color: C.white, lineHeight: 1 }}>{t.nome}</div>
        </TornStrip>
      </div>
      {abs >= t.biLibertaEm ? (
        <div style={{ position: "absolute", right: 50, top: 520, width: 430, display: "flex", flexDirection: "column", alignItems: "center", scale: `${interpolate(lib, [0, 1], [0.3, 1])}`, rotate: `${interpolate(lib, [0, 1], [20, 3])}deg` }}>
          <div style={{ background: C.white, border: `6px solid ${C.black}`, boxShadow: `10px 10px 0 ${C.red}`, padding: 20, width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Img src={staticFile(A.logoLibertadores)} style={{ height: 150, objectFit: "contain" }} />
            <div style={{ fontFamily: ANTON, fontSize: 64, color: C.black, lineHeight: 1.1 }}>BI DA LIBERTA</div>
            <div style={{ fontFamily: BEBAS, fontSize: 52, color: C.red, letterSpacing: 4 }}>1992 · 1993</div>
          </div>
        </div>
      ) : null}
      {abs >= t.biMundialEm ? (
        <div style={{ position: "absolute", right: 60, top: 930, width: 430, display: "flex", flexDirection: "column", alignItems: "center", scale: `${interpolate(mun, [0, 1], [0.3, 1])}`, rotate: `${interpolate(mun, [0, 1], [-20, -3])}deg` }}>
          <div style={{ background: C.black, border: `6px solid ${C.white}`, boxShadow: `10px 10px 0 ${C.red}`, padding: "18px 20px", width: "100%", textAlign: "center" }}>
            <div style={{ fontFamily: ANTON, fontSize: 70, color: C.white, lineHeight: 1.05 }}>BI MUNDIAL</div>
            <div style={{ fontFamily: BEBAS, fontSize: 40, color: C.red, letterSpacing: 3 }}>INTERCONTINENTAL 92 · 93</div>
          </div>
        </div>
      ) : null}
      <Flash startFrame={f(t.biLibertaEm)} dur={4} />
    </AbsoluteFill>
  );
};

const Placar: React.FC<{ i: number }> = ({ i }) => {
  const p = s.placares[i];
  const { since } = useSceneClock(p.em);
  const sh = shake(since(p.em + 0.2), 14, 0.3);
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      {"foto" in p && p.foto ? (
        <div style={{ position: "absolute", right: -80, top: 160, opacity: 0.95 }}>
          <Cutout src={A[p.foto as string]} width={620} height={760} startFrame={0} from={{ x: 500, y: 0, r: 10, s: 1 }} float={0.5} />
        </div>
      ) : null}
      <div style={{ position: "absolute", top: 230, left: 60 }}>
        <YearStamp text={p.ano} startFrame={0} size={120} rotate={-6} color={C.red} />
      </div>
      <div style={{ position: "absolute", top: 640, left: 60 }}>
        <Scoreboard
          startFrame={2}
          crestA={A.escudoAtual}
          crestB={A[p.escudoAdv]}
          nameA="SÃO PAULO"
          nameB={p.adv}
          a={p.golsSP}
          b={p.golsAdv}
          top={p.torneio}
          bottom={p.destaque}
          year={p.ano}
        />
      </div>
    </AbsoluteFill>
  );
};

const Ano2005: React.FC = () => {
  const a = s.ano2005;
  const { sp } = useSceneClock(a.em);
  const l1 = sp(a.em + 0.1, { damping: 11 });
  const l2 = sp(a.em + 0.9, { damping: 11 });
  const logos = [A.logoLibertadores, A.logoMundial];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 200, width: "100%", textAlign: "center" }}>
        <div style={{ fontFamily: BEBAS, fontSize: 70, letterSpacing: 10, color: C.black }}>DE NOVO!</div>
      </div>
      <div style={{ position: "absolute", top: 300, width: "100%", textAlign: "center" }}>
        <YearStamp text={a.ano} startFrame={0} size={260} rotate={-4} color={C.red} />
      </div>
      <div style={{ position: "absolute", top: 760, left: 0, width: "100%", display: "flex", justifyContent: "center", gap: 50 }}>
        {[l1, l2].map((p, i) => (
          <div
            key={i}
            style={{
              width: 420,
              background: i ? C.black : C.white,
              border: `6px solid ${i ? C.white : C.black}`,
              boxShadow: `10px 10px 0 ${C.red}`,
              padding: 22,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              scale: `${interpolate(p, [0, 1], [0.2, 1])}`,
              rotate: `${interpolate(p, [0, 1], [i ? 25 : -25, i ? 3 : -3])}deg`,
              opacity: p > 0.01 ? 1 : 0,
            }}
          >
            <div style={{ height: 220, display: "flex", alignItems: "center", justifyContent: "center", background: i ? C.white : "transparent", borderRadius: 12, padding: i ? 14 : 0 }}>
              <Img src={staticFile(logos[i])} style={{ maxHeight: 190, maxWidth: 330, objectFit: "contain" }} />
            </div>
            <div style={{ fontFamily: ANTON, fontSize: 56, color: i ? C.white : C.black, marginTop: 12 }}>{a.titulos[i]}</div>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Tri: React.FC = () => {
  const t = s.tri;
  const { abs, sp, fps } = useSceneClock(t.em);
  const f = (x: number) => (x - t.em) * fps;
  const crestP = sp(t.em, { damping: 12 });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 190, left: 60, right: 60, display: "flex", justifyContent: "center" }}>
        <TornStrip color={C.red} seed={6} style={{ rotate: "-1.5deg" }}>
          <div style={{ fontFamily: ANTON, fontSize: 70, color: C.white, textAlign: "center", lineHeight: 1.05 }}>{t.titulo}</div>
        </TornStrip>
      </div>
      <div style={{ position: "absolute", left: 540 - 210, top: 460, width: 420, height: 420, scale: `${crestP}` }}>
        <Img src={staticFile(A.escudoAtual)} style={{ width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(14px 16px 0 ${C.black})` }} />
      </div>
      <div style={{ position: "absolute", top: 370, width: "100%", display: "flex", justifyContent: "center", gap: 30 }}>
        {t.anosEm.map((at, i) => {
          const p = sp(at, { damping: 8, stiffness: 260 });
          return (
            <div key={i} style={{ fontSize: 90, color: C.red, scale: `${p}`, rotate: `${(i - 1) * 12}deg`, translate: `0 ${i === 1 ? -20 : 0}px`, fontFamily: ANTON, textShadow: `4px 4px 0 ${C.black}`, opacity: abs >= at ? 1 : 0 }}>
              ★
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: 960, left: 110 }}>
        <Timeline width={860} items={t.anos.map((y, i) => ({ label: y, at: f(t.anosEm[i]) }))} />
      </div>
      <div style={{ position: "absolute", top: 1180, width: "100%", textAlign: "center", fontFamily: BEBAS, fontSize: 44, letterSpacing: 6, color: C.black, opacity: interpolate(abs, [t.anosEm[2] + 0.3, t.anosEm[2] + 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        {t.totalBrasileiros}
      </div>
      {abs >= t.extraEm ? (
        <div
          style={{
            position: "absolute",
            top: 1240,
            left: 110,
            right: 110,
            display: "flex",
            alignItems: "center",
            gap: 18,
            background: C.black,
            padding: "10px 20px",
            boxShadow: `8px 8px 0 ${C.red}`,
            rotate: "-1.5deg",
            scale: `${sp(t.extraEm, { damping: 11 })}`,
          }}
        >
          <Img src={staticFile(A.logoCopaDoBrasil)} style={{ height: 70, width: 110, objectFit: "contain", background: C.white, borderRadius: 8, padding: 4 }} />
          <div style={{ flex: 1, fontFamily: ANTON, fontSize: 38, color: C.white, lineHeight: 1.05 }}>{t.extra}</div>
          <Img src={staticFile(A.escudoFlamengo)} style={{ height: 76, width: 64, objectFit: "contain" }} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/** CENA 7 – O MUNDO */
export const SceneMundo: React.FC = () => {
  const { abs, fps } = useSceneClock(s.inicio);
  const fr = (x: number) => Math.round((x - s.inicio) * fps);
  const p = s.placares;
  return (
    <AbsoluteFill>
      <Pitch draw={interpolate(abs, [s.inicio, s.inicio + 1.2], [0, 1], { extrapolateRight: "clamp" })} />
      <Sequence name="Telê"  durationInFrames={fr(p[0].em)} layout="none">
        <Tele />
      </Sequence>
      <Sequence name="Barcelona 92" from={fr(p[0].em)} durationInFrames={fr(p[0].ate) - fr(p[0].em)} layout="none">
        <Placar i={0} />
      </Sequence>
      <Sequence name="Milan 93" from={fr(p[1].em)} durationInFrames={fr(p[1].ate) - fr(p[1].em)} layout="none">
        <Placar i={1} />
      </Sequence>
      <Sequence name="2005" from={fr(s.ano2005.em)} durationInFrames={fr(p[2].em) - fr(s.ano2005.em)} layout="none">
        <Ano2005 />
      </Sequence>
      <Sequence name="Liverpool 05" from={fr(p[2].em)} durationInFrames={fr(p[2].ate) - fr(p[2].em)} layout="none">
        <Placar i={2} />
      </Sequence>
      <Sequence name="Tri" from={fr(s.tri.em)} layout="none">
        <Tri />
      </Sequence>
    </AbsoluteFill>
  );
};
