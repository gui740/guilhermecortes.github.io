import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile } from "remotion";
import { Confetti, Flash, Hook, Rays, YearStamp } from "../../../components/Graphics";
import { PaperBackground, TornStrip } from "../../../components/Paper";
import { ShatterCrest } from "../../../components/Shatter";
import { shake, useSceneClock } from "../../../components/time";
import { ANTON, BEBAS, C } from "../../../theme";
import { A, D } from "../data";
import { CREST_CENTER } from "./Nascimento";

/** CENA 4 – A MORTE: tudo cinza, o escudo racha e se quebra (1935). */
export const SceneMorte: React.FC = () => {
  const s = D.cenas.morte;
  const { abs, since, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const crack = abs < s.frases[0].em ? 0 : abs < s.frases[1].em ? 0.25 : abs < s.anoEm ? 0.55 : interpolate(abs, [s.anoEm, s.quebraEm], [0.7, 1], { extrapolateRight: "clamp" });
  const burst = interpolate(abs, [s.quebraEm, s.quebraEm + 1.0], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => x * x });
  const shA = shake(since(s.frases[0].em), 8, 0.3);
  const shB = shake(since(s.frases[1].em), 8, 0.3);
  const shC = shake(since(s.anoEm), 16, 0.25);
  const shD = shake(since(s.quebraEm), 30, 0.15);
  const push = interpolate(abs, [s.inicio, s.quebraEm], [1, 1.12], { extrapolateRight: "clamp" });
  const tremble = abs > s.anoEm && abs < s.quebraEm ? Math.sin(abs * 70) * 2.5 * ((abs - s.anoEm) / (s.quebraEm - s.anoEm)) : 0;
  return (
    <AbsoluteFill>
      <PaperBackground color="#BDBAB4" tint="rgba(0,0,0,0.35)" />
      <AbsoluteFill
        style={{
          filter: "grayscale(1) contrast(1.15)",
          scale: `${push}`,
          translate: `${shA.x + shB.x + shC.x + shD.x}px ${shA.y + shB.y + shC.y + shD.y}px`,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: CREST_CENTER.x - CREST_CENTER.size / 2 + tremble,
            top: CREST_CENTER.y - CREST_CENTER.size / 2,
            filter: `drop-shadow(16px 20px 0 ${C.black})`,
          }}
        >
          <ShatterCrest src={A.escudo1930} size={CREST_CENTER.size} crack={crack} burst={burst} seed={11} />
        </div>
        {s.frases.map((fr, i) => (
          <div key={i} style={{ position: "absolute", top: 330 + i * 165, left: i ? 380 : 90 }}>
            <YearStamp text={fr.t} startFrame={f(fr.em)} size={92} rotate={i ? 5 : -6} color={C.black} />
          </div>
        ))}
        <div style={{ position: "absolute", top: 1080, width: "100%", textAlign: "center" }}>
          <YearStamp text={s.ano} startFrame={f(s.anoEm)} size={210} rotate={-4} color={C.black} />
        </div>
      </AbsoluteFill>
      {abs >= s.quebraEm + 0.15 ? (
        <div style={{ position: "absolute", top: 760, width: "100%", display: "flex", justifyContent: "center" }}>
          <TornStrip color={C.black} seed={5} style={{ rotate: "-3deg", scale: `${interpolate(since(s.quebraEm + 0.15), [0, 6], [1.5, 1], { extrapolateRight: "clamp" })}` }}>
            <div style={{ fontFamily: ANTON, fontSize: 66, color: C.white }}>{s.rodape}</div>
          </TornStrip>
        </div>
      ) : null}
      <Flash startFrame={f(s.quebraEm)} dur={5} />
    </AbsoluteFill>
  );
};

/** CENA 5 – A FÉ: as peças voltam, a cor volta, nasce o Clube da Fé. */
export const SceneFe: React.FC = () => {
  const s = D.cenas.fe;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const assembled = s.remontaEm + 1.7;
  const burst = interpolate(abs, [s.remontaEm, assembled], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) });
  const gray = interpolate(abs, [assembled, s.refundadoEm], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const swap = interpolate(abs, [assembled, assembled + 0.25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const bump = sp(s.refundadoEm, { damping: 8, stiffness: 200 });
  const sh = shake(since(assembled), 14, 0.25);
  const titleP = sp(s.apelidoEm, { damping: 10 });
  const crestY = interpolate(titleP, [0, 1], [CREST_CENTER.y, CREST_CENTER.y - 60]);
  const crestScale = interpolate(titleP, [0, 1], [1, 0.85]) * (1 + 0.08 * Math.sin(Math.min(1, Math.max(0, since(s.refundadoEm) / 10)) * Math.PI) * bump);
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      <AbsoluteFill style={{ opacity: gray }}>
        <PaperBackground color="#BDBAB4" tint="rgba(0,0,0,0.35)" />
      </AbsoluteFill>
      {abs >= s.refundadoEm ? (
        <div style={{ position: "absolute", left: 0, top: crestY - 540, width: 1080, height: 1080 }}>
          <Rays color={C.red} opacity={0.32 * (1 - gray)} />
        </div>
      ) : null}
      <AbsoluteFill style={{ filter: `grayscale(${gray})` }}>
        <div
          style={{
            position: "absolute",
            left: CREST_CENTER.x - CREST_CENTER.size / 2,
            top: crestY - CREST_CENTER.size / 2,
            scale: `${crestScale}`,
            filter: `drop-shadow(16px 20px 0 ${C.black})`,
          }}
        >
          <div style={{ opacity: 1 - swap }}>
            <ShatterCrest src={A.escudo1930} size={CREST_CENTER.size} crack={0} burst={burst} seed={11} />
          </div>
          <Img
            src={staticFile(A.escudo1935)}
            style={{ position: "absolute", inset: 0, width: CREST_CENTER.size, height: CREST_CENTER.size, objectFit: "contain", opacity: swap }}
          />
        </div>
        <div style={{ position: "absolute", top: 230, width: "100%", textAlign: "center", fontFamily: BEBAS, fontSize: 76, letterSpacing: 8, color: C.black, opacity: interpolate(since(s.inicio + 0.1), [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) * (1 - titleP) }}>
          OS SÓCIOS NÃO DESISTEM
        </div>
        {abs < s.apelidoEm + 0.1 ? (
          <div style={{ position: "absolute", top: 1090, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", gap: 10, opacity: 1 - titleP }}>
            <YearStamp text={s.data} startFrame={f(s.dataEm)} size={140} rotate={-5} color={C.red} sub={s.legenda} />
          </div>
        ) : null}
      </AbsoluteFill>
      {abs >= s.apelidoEm ? (
        <>
          <Hook lines={[s.apelido]} startFrame={f(s.apelidoEm)} size={200} color={C.red} style={{ position: "absolute", top: 1110, width: "100%" }} />
          <Confetti startFrame={f(s.apelidoEm)} count={46} />
        </>
      ) : null}
      <Flash startFrame={f(assembled)} dur={6} />
      <Flash startFrame={f(s.refundadoEm)} dur={10} color={C.white} />
    </AbsoluteFill>
  );
};
