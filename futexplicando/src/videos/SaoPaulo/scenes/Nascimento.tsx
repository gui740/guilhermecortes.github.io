import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile } from "remotion";
import { Cutout, Flash, Rays, YearStamp } from "../../../components/Graphics";
import { TornStrip } from "../../../components/Paper";
import { shake, useSceneClock } from "../../../components/time";
import { ANTON, BEBAS, C, INTER } from "../../../theme";
import { A, D } from "../data";

export const CREST_CENTER = { x: 540, y: 800, size: 600 };

/** CENA 3 – NASCIMENTO: 25/01/1930, fusão Paulistano + AA das Palmeiras. */
export const SceneNascimento: React.FC = () => {
  const s = D.cenas.nascimento;
  const { abs, since, sp, fps } = useSceneClock(s.inicio);
  const f = (t: number) => (t - s.inicio) * fps;

  // parte A: foto de 1930 + carimbo (6.95 → 11.0)
  const photoOut = interpolate(abs, [s.paulistanoEm - 0.25, s.paulistanoEm + 0.25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => x * x });
  const photoIn = sp(s.inicio, { damping: 15 });
  // parte B: fusão
  const fuse = interpolate(abs, [s.fusaoEm - 0.45, s.fusaoEm], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => x * x * x });
  const born = sp(s.fusaoEm, { damping: 10, stiffness: 170 });
  const sh = shake(since(s.fusaoEm), 22, 0.2);
  const sh2 = shake(since(s.dataEm), 12, 0.3);

  return (
    <AbsoluteFill style={{ translate: `${sh.x + sh2.x}px ${sh.y + sh2.y}px` }}>
      {/* ---- A: foto + data ---- */}
      {abs < s.paulistanoEm + 0.3 ? (
        <AbsoluteFill style={{ translate: `0 ${-photoOut * 1400}px`, rotate: `${photoOut * -8}deg` }}>
          <div
            style={{
              position: "absolute",
              left: 70,
              top: 240,
              width: 940,
              background: C.white,
              padding: "26px 26px 90px",
              boxShadow: `14px 16px 0 ${C.black}`,
              rotate: `${interpolate(photoIn, [0, 1], [12, -3])}deg`,
              translate: `${interpolate(photoIn, [0, 1], [900, 0])}px ${Math.sin(abs) * 8}px`,
            }}
          >
            <div style={{ width: "100%", height: 520, overflow: "hidden" }}>
              <Img
                src={staticFile(A.fotoTime1930)}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  scale: `${interpolate(abs, [s.inicio, s.paulistanoEm], [1.05, 1.22])}`,
                  translate: `${interpolate(abs, [s.inicio, s.paulistanoEm], [20, -30])}px 0`,
                }}
              />
            </div>
            <div style={{ fontFamily: INTER, fontWeight: 700, fontSize: 30, color: "#555", marginTop: 18 }}>Primeiro elenco do São Paulo, 1930</div>
          </div>
          <div style={{ position: "absolute", left: 300, top: 760 }}>
            <YearStamp text={s.data} startFrame={f(s.dataEm)} size={150} rotate={-7} color={C.red} />
          </div>
          {abs >= s.notaEm ? (
            <div
              style={{
                position: "absolute",
                left: 120,
                top: 1080,
                translate: `${interpolate(since(s.notaEm), [0, 8], [-1100, 0], { extrapolateRight: "clamp", easing: (x) => 1 - Math.pow(1 - x, 3) })}px 0`,
              }}
            >
              <TornStrip color={C.black} seed={3} style={{ rotate: "-2deg" }}>
                <div style={{ fontFamily: ANTON, fontSize: 72, color: C.white, letterSpacing: 2 }}>{s.nota}</div>
              </TornStrip>
            </div>
          ) : null}
        </AbsoluteFill>
      ) : null}

      {/* ---- B: escudos de origem ---- */}
      {abs >= s.paulistanoEm - 0.1 ? (
        <AbsoluteFill>
          {fuse < 1 ? (
            <>
              <div
                style={{
                  position: "absolute",
                  left: interpolate(fuse, [0, 1], [70, 540 - 190]),
                  top: 600 + fuse * 20,
                  scale: `${1 - fuse * 0.5}`,
                  rotate: `${fuse * 30}deg`,
                }}
              >
                <Cutout src={A.escudoPaulistano} width={380} height={380} startFrame={f(s.paulistanoEm)} from={{ x: -700, y: 0, r: -40, s: 0.4 }} />
              </div>
              <div
                style={{
                  position: "absolute",
                  left: interpolate(fuse, [0, 1], [630, 540 - 190]),
                  top: 600 + fuse * 20,
                  scale: `${1 - fuse * 0.5}`,
                  rotate: `${-fuse * 30}deg`,
                }}
              >
                <Cutout src={A.escudoPalmeiras} width={380} height={380} startFrame={f(s.palmeirasEm)} from={{ x: 700, y: 0, r: 40, s: 0.4 }} />
              </div>
              {/* rótulos */}
              <div style={{ position: "absolute", top: 1020, left: 60, width: 440, textAlign: "center", opacity: (1 - fuse) * interpolate(since(s.paulistanoEm + 0.15), [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
                <div style={{ fontFamily: ANTON, fontSize: 58, color: C.black }}>{s.nomes.a}</div>
                <div style={{ fontFamily: BEBAS, fontSize: 34, color: C.red, letterSpacing: 3 }}>CLUB ATHLETICO PAULISTANO</div>
              </div>
              <div style={{ position: "absolute", top: 1020, left: 580, width: 440, textAlign: "center", opacity: (1 - fuse) * interpolate(since(s.palmeirasEm + 0.15), [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
                <div style={{ fontFamily: ANTON, fontSize: 58, color: C.black }}>{s.nomes.b}</div>
                <div style={{ fontFamily: BEBAS, fontSize: 34, color: C.red, letterSpacing: 3 }}>ASSOCIAÇÃO ATLÉTICA</div>
              </div>
              <div
                style={{
                  position: "absolute",
                  left: 0,
                  width: "100%",
                  top: 680,
                  textAlign: "center",
                  fontFamily: ANTON,
                  fontSize: 160,
                  color: C.red,
                  opacity: (1 - fuse) * interpolate(since(s.palmeirasEm + 0.3), [0, 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
                  scale: `${interpolate(since(s.palmeirasEm + 0.3), [0, 6], [2, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}`,
                }}
              >
                +
              </div>
              <div style={{ position: "absolute", top: 300, width: "100%", textAlign: "center", fontFamily: BEBAS, fontSize: 70, letterSpacing: 8, color: C.black, opacity: 1 - fuse }}>
                1930 · A FUSÃO
              </div>
            </>
          ) : null}

          {/* ---- C: nasce o São Paulo ---- */}
          {abs >= s.fusaoEm ? (
            <>
              <div style={{ position: "absolute", left: 0, top: CREST_CENTER.y - 540, width: 1080, height: 1080 }}>
                <Rays color={C.red} opacity={0.28 * born} />
              </div>
              <div
                style={{
                  position: "absolute",
                  left: CREST_CENTER.x - CREST_CENTER.size / 2,
                  top: CREST_CENTER.y - CREST_CENTER.size / 2,
                  width: CREST_CENTER.size,
                  height: CREST_CENTER.size,
                  scale: `${interpolate(born, [0, 1], [0.2, 1])}`,
                  rotate: `${interpolate(born, [0, 1], [-200, 0])}deg`,
                }}
              >
                <Img src={staticFile(A.escudo1930)} style={{ width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(16px 20px 0 ${C.black})` }} />
              </div>
              <div style={{ position: "absolute", top: 250, width: "100%", textAlign: "center", fontFamily: BEBAS, fontSize: 80, letterSpacing: 10, color: C.black, opacity: born }}>
                NASCE O SÃO PAULO
              </div>
              {abs >= s.nomeEm ? (
                <div style={{ position: "absolute", top: 1140, width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
                  <TornStrip color={C.red} seed={8} style={{ rotate: "2deg", scale: `${interpolate(since(s.nomeEm), [0, 6], [1.6, 1], { extrapolateRight: "clamp" })}` }}>
                    <div style={{ fontFamily: ANTON, fontSize: 76, color: C.white, letterSpacing: 1 }}>{s.resultado}*</div>
                  </TornStrip>
                </div>
              ) : null}
              <div
                style={{
                  position: "absolute",
                  bottom: 330,
                  width: "100%",
                  textAlign: "center",
                  fontFamily: INTER,
                  fontWeight: 600,
                  fontSize: 26,
                  color: "#444",
                  opacity: interpolate(since(s.nomeEm + 0.2), [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
                }}
              >
                *apelido popularizado depois (anos 70), segundo o próprio clube
              </div>
              <Flash startFrame={f(s.fusaoEm)} dur={9} />
            </>
          ) : null}
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
