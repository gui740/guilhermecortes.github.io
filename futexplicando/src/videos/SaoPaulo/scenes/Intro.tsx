import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile } from "remotion";
import { Coin } from "../../../components/Coin";
import { Flash, Hook, Rays } from "../../../components/Graphics";
import { shake, useSceneClock } from "../../../components/time";
import { ANTON, BEBAS, C } from "../../../theme";
import { A, COIN, D, coinAngleAt, coinYAt } from "../data";

const Floor: React.FC<{ opacity?: number }> = ({ opacity = 1 }) => (
  <div
    style={{
      position: "absolute",
      left: 80,
      right: 80,
      top: COIN.floorY + COIN.size / 2 - 2,
      height: 8,
      background: C.black,
      borderRadius: 4,
      opacity,
    }}
  />
);

const Shadow: React.FC<{ y: number; spread?: number }> = ({ y, spread = 1 }) => {
  const h = COIN.floorY - y; // altura acima do chão
  const k = Math.max(0, 1 - h / 600);
  return (
    <div
      style={{
        position: "absolute",
        left: COIN.x - (COIN.size * 0.55 * spread) / 2,
        top: COIN.floorY + COIN.size / 2 - 16,
        width: COIN.size * 0.55 * spread,
        height: 30,
        borderRadius: "50%",
        background: "rgba(17,17,17,0.55)",
        filter: "blur(10px)",
        opacity: 0.2 + 0.8 * k,
        scale: `${0.5 + 0.5 * k} 1`,
      }}
    />
  );
};

/** CENA 1 – GANCHO: moeda girando em câmera lenta, quica e para EM PÉ. */
export const SceneHook: React.FC = () => {
  const s = D.cenas.gancho;
  const { abs, since, fps } = useSceneClock(s.inicio);
  const y = coinYAt(abs);
  const ang = coinAngleAt(abs);
  const standF = since(s.moeda.emPe);
  const sh = shake(since(s.moeda.quiques[0]), 10, 0.35);
  const zoom = interpolate(abs, [0, s.moeda.emPe, s.moeda.emPe + 0.5, s.fim], [1.12, 1.0, 1.06, 1.1], { extrapolateRight: "clamp" });
  const tilt = abs < s.moeda.emPe ? Math.sin(abs * 3) * 10 * (1 - abs / s.moeda.emPe) : Math.sin(standF / 2.2) * 3 * Math.exp(-standF / 8);
  const blur = abs < s.moeda.quiques[0] ? 1.5 : 0;
  const textF = since(s.moeda.textoEm);
  return (
    <AbsoluteFill style={{ scale: `${zoom}`, translate: `${sh.x}px ${sh.y}px` }}>
      {/* brilho de "milagre" quando para em pé */}
      <AbsoluteFill style={{ opacity: interpolate(standF, [0, 6, 30], [0, 0.9, 0.35], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        <div style={{ position: "absolute", left: COIN.x - 450, top: COIN.floorY - 450, width: 900, height: 900 }}>
          <Rays color={C.red} opacity={0.35} />
        </div>
      </AbsoluteFill>
      <Floor opacity={interpolate(abs, [0.6, 1.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
      <Shadow y={y} />
      <div style={{ position: "absolute", left: COIN.x - COIN.size / 2, top: y - COIN.size / 2 }}>
        <Coin id="hook" size={COIN.size} angle={ang} tilt={tilt} crest={A.escudoAtual} blur={blur} />
      </div>
      {/* kicker */}
      <div
        style={{
          position: "absolute",
          top: 250,
          width: "100%",
          textAlign: "center",
          fontFamily: BEBAS,
          fontSize: 64,
          letterSpacing: 14,
          color: C.red,
          opacity: interpolate(abs, [0.15, 0.35, 2.3, 2.5], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        {s.kicker}
      </div>
      {textF >= 0 ? <Hook lines={s.texto} startFrame={(s.moeda.textoEm - s.inicio) * fps} stagger={14} size={128} accentIndex={1} style={{ position: "absolute", top: 300, width: "100%" }} /> : null}
    </AbsoluteFill>
  );
};

/** CENA 2 – VIRADA: escudo surge atrás da moeda com impacto. */
export const SceneVirada: React.FC = () => {
  const s = D.cenas.virada;
  const { abs, since, sp } = useSceneClock(s.inicio);
  const p = sp(s.inicio, { damping: 9, stiffness: 180, mass: 0.9 });
  const sh = shake(since(s.inicio), 26, 0.22);
  // a moeda volta a girar e sai voando para cima (transição para a cena 3)
  const lift = interpolate(abs, [6.25, 6.95], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => x * x });
  const coinY = COIN.floorY - lift * 1900;
  const coinAng = interpolate(abs, [6.1, 6.95], [0, 18], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (x) => x * x });
  return (
    <AbsoluteFill style={{ translate: `${sh.x}px ${sh.y}px` }}>
      <div style={{ position: "absolute", left: 0, top: 260, width: 1080, height: 1080 }}>
        <Rays color={C.red} opacity={0.3} count={22} />
      </div>
      <div
        style={{
          position: "absolute",
          left: 540 - 340,
          top: 520,
          width: 680,
          height: 680,
          scale: `${interpolate(p, [0, 1], [3.5, 1])}`,
          opacity: interpolate(p, [0, 0.15], [0, 1], { extrapolateRight: "clamp" }),
          rotate: `${interpolate(p, [0, 1], [-25, 0]) + Math.sin(abs * 2) * 1.5}deg`,
        }}
      >
        <Img src={staticFile(A.escudoAtual)} style={{ width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(18px 22px 0 ${C.black})` }} />
      </div>
      <div style={{ position: "absolute", left: COIN.x - COIN.size / 2, top: coinY - COIN.size / 2 + 80 * (1 - lift), scale: "0.62" }}>
        <Coin id="virada" size={COIN.size} angle={coinAng} crest={A.escudoAtual} blur={lift > 0 ? 3 : 0} />
      </div>
      <div style={{ position: "absolute", top: 150, width: "100%", textAlign: "center" }}>
        <div
          style={{
            fontFamily: BEBAS,
            fontSize: 78,
            letterSpacing: 10,
            color: C.black,
            opacity: interpolate(since(s.inicio + 0.15), [0, 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          {s.linha1}
        </div>
        <Hook lines={[s.linha2]} startFrame={since(s.inicio) - since(s.inicio + 0.2)} size={190} color={C.red} accentIndex={-1} />
      </div>
      <div style={{ position: "absolute", top: 1240, width: "100%", display: "flex", justifyContent: "center" }}>
        <div
          style={{
            background: C.black,
            color: C.white,
            fontFamily: ANTON,
            fontSize: 70,
            padding: "10px 40px",
            rotate: "-2deg",
            boxShadow: `8px 8px 0 ${C.red}`,
            clipPath: `inset(0 ${interpolate(since(5.3), [0, 8], [100, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}% 0 0)`,
          }}
        >
          {s.linha3}
        </div>
      </div>
      <Flash startFrame={0} dur={7} />
    </AbsoluteFill>
  );
};
