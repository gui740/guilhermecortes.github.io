import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile } from "remotion";
import { Timeline } from "../../../components/Graphics";
import { TornStrip } from "../../../components/Paper";
import { shake, useSceneClock } from "../../../components/time";
import { ANTON, C, INTER } from "../../../theme";
import { A, D } from "../data";

/** CENA 6 – MORUMBI: foto com parallax (3 camadas). */
export const SceneMorumbi: React.FC = () => {
  const s = D.cenas.morumbi;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;
  const u = interpolate(abs, [s.inicio, s.fim], [0, 1]);
  const titleP = sp(s.tituloEm, { damping: 9, stiffness: 220 });
  const sh = shake(since(s.tituloEm), 20, 0.22);
  return (
    <AbsoluteFill style={{ backgroundColor: C.black, translate: `${sh.x}px ${sh.y}px` }}>
      {/* camada 1: foto (move devagar) */}
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img
          src={staticFile(A.fotoMorumbi)}
          style={{
            position: "absolute",
            height: 1920 * 1.12,
            width: "auto",
            left: interpolate(u, [0, 1], [-420, -980]),
            top: -100,
            scale: `${interpolate(u, [0, 1], [1.18, 1.04])}`,
            rotate: `${interpolate(u, [0, 1], [-1.5, 1])}deg`,
          }}
        />
      </AbsoluteFill>
      {/* camada 2: duotone vermelho/preto e degradês */}
      <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(17,17,17,0.75) 0%, rgba(17,17,17,0) 30%, rgba(17,17,17,0) 55%, rgba(227,6,19,0.55) 82%, rgba(17,17,17,0.9) 100%)` }} />
      <AbsoluteFill style={{ background: C.red, mixBlendMode: "multiply", opacity: 0.22 }} />
      {/* camada 3: textos (move mais rápido = parallax) */}
      <AbsoluteFill style={{ translate: `${interpolate(u, [0, 1], [30, -30])}px 0` }}>
        {abs >= s.subtituloEm ? (
          <div style={{ position: "absolute", top: 230, left: 50, right: 50, display: "flex", justifyContent: "center", translate: `${interpolate(since(s.subtituloEm), [0, 8], [-1200, 0], { extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) })}px 0` }}>
            <TornStrip color={C.white} seed={2} style={{ rotate: "-2deg" }}>
              <div style={{ fontFamily: ANTON, fontSize: 62, color: C.black, textAlign: "center", lineHeight: 1.05 }}>{s.subtitulo}</div>
            </TornStrip>
          </div>
        ) : null}
        <div
          style={{
            position: "absolute",
            top: 560,
            width: "100%",
            textAlign: "center",
            fontFamily: ANTON,
            fontSize: 250,
            color: C.white,
            letterSpacing: 4,
            textShadow: `12px 12px 0 ${C.red}, 22px 22px 0 ${C.black}`,
            opacity: titleP > 0.01 ? 1 : 0,
            scale: `${interpolate(titleP, [0, 1], [2.4, 1])}`,
          }}
        >
          {s.titulo}
        </div>
        <div style={{ position: "absolute", top: 1010, left: 60, width: 960, background: "rgba(244,239,230,0.94)", padding: "6px 50px 0", boxSizing: "border-box", boxShadow: `10px 10px 0 ${C.red}`, opacity: interpolate(since(s.subtituloEm + 0.5), [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          <Timeline
            width={860}
            items={s.marcos.map((m, i) => ({ label: m.ano, sub: m.txt, at: f(s.subtituloEm + 0.6 + i * 0.7) }))}
          />
        </div>
      </AbsoluteFill>
      <div style={{ position: "absolute", bottom: 300, right: 40, fontFamily: INTER, fontWeight: 500, fontSize: 20, color: "rgba(244,239,230,0.7)" }}>
        Foto: saopaulofc.net
      </div>
    </AbsoluteFill>
  );
};
