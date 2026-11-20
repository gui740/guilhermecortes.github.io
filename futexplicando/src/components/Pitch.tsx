import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { TITLE, SANS } from "../lib/fonts";
import { Sfx } from "./Sfx";

type Props = {
  homeLabel: string; awayLabel: string; score: [number, number];
  homeColor: string; awayColor: string; grass: string; grassDark: string; ink: string; paper: string; accent: string;
  enterAwayAt: number; flagAt: number; scoreAt: number; leaveAt: number;
  sfx: { whoosh?: string; crowd?: string; impact?: string };
};

const W = 900, H = 1240;
// 4-3-3 (metade de baixo = casa), coordenadas 0..1 no próprio campo
const HOME = [[0.5, 0.95], [0.15, 0.8], [0.38, 0.83], [0.62, 0.83], [0.85, 0.8], [0.3, 0.68], [0.5, 0.71], [0.7, 0.68], [0.2, 0.56], [0.5, 0.55], [0.8, 0.56]];
const AWAY = HOME.map(([x, y]) => [1 - x, 1 - y]);

const BrazilFlag: React.FC<{ w: number }> = ({ w }) => (
  <svg width={w} height={w * 0.7} viewBox="0 0 100 70">
    <rect width="100" height="70" fill="#009C3B" />
    <polygon points="50,6 94,35 50,64 6,35" fill="#FFDF00" />
    <circle cx="50" cy="35" r="16" fill="#002776" />
    <path d="M35 32 Q50 27 65 38" stroke="#fff" strokeWidth="3" fill="none" />
  </svg>
);

/** Campinho 2D visto de cima + placar estilo TV + time rival saindo do campo. */
export const Pitch: React.FC<Props> = (p) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const homeIn = spring({ frame: f, fps, config: { damping: 14 } });
  const awayIn = spring({ frame: f - p.enterAwayAt, fps, config: { damping: 14 } });
  const flagP = interpolate(f, [p.flagAt, p.flagAt + 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) });
  const board = spring({ frame: f - p.scoreAt, fps, config: { damping: 12, stiffness: 140 } });
  const cnt = (n: number, d: number) => Math.round(interpolate(f, [p.scoreAt + 6 + d, p.scoreAt + 20 + d], [0, n], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const pulse = 1 + 0.06 * Math.max(0, Math.sin((f - p.scoreAt - 20) / 4)) * (f > p.scoreAt + 20 && f < p.scoreAt + 45 ? 1 : 0);

  const dot = (x: number, y: number, color: string, i: number, away: boolean) => {
    const wob = Math.sin(f / 9 + i) * 6;
    let px = x * W, py = y * H;
    let o = 1;
    if (away) {
      const leave = interpolate(f, [p.leaveAt + i * 2, p.leaveAt + 28 + i * 2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
      px = px + leave * (W + 200 - px);
      py = py + leave * (H * 0.35 - py) * 0.3;
      o = 1 - leave * 0.2;
      py = py - (1 - awayIn) * 900;
    } else {
      py = py + (1 - homeIn) * 900;
    }
    return (
      <g key={`${away}-${i}`} transform={`translate(${px + wob * 0.4}, ${py + wob})`} opacity={o}>
        <circle r={30} fill="rgba(0,0,0,0.25)" cx={5} cy={7} />
        <circle r={30} fill={color} stroke={p.ink} strokeWidth={6} />
      </g>
    );
  };

  return (
    <div style={{ position: "relative", width: W, height: H + 140 }}>
      {/* placar TV */}
      <div style={{ position: "absolute", top: -230 + board * 230, left: 0, right: 0, display: "flex", justifyContent: "center", zIndex: 5, opacity: board > 0.02 ? 1 : 0 }}>
        <div style={{ display: "flex", alignItems: "stretch", fontFamily: TITLE, fontSize: 110, boxShadow: "0 12px 0 rgba(0,0,0,0.35)", transform: `scale(${pulse})` }}>
          <div style={{ background: p.homeColor, color: p.paper, padding: "4px 30px" }}>{p.homeLabel}</div>
          <div style={{ background: p.ink, color: p.paper, padding: "4px 34px", minWidth: 260, textAlign: "center" }}>{cnt(p.score[0], 0)} x {cnt(p.score[1], 6)}</div>
          <div style={{ background: p.awayColor, color: p.ink, padding: "4px 30px" }}>{p.awayLabel}</div>
        </div>
      </div>
      <svg width={W} height={H} style={{ position: "absolute", top: 140, borderRadius: 20, boxShadow: `14px 14px 0 ${p.ink}` }}>
        {Array.from({ length: 10 }).map((_, i) => (
          <rect key={i} x={0} y={(i * H) / 10} width={W} height={H / 10} fill={i % 2 ? p.grass : p.grassDark} />
        ))}
        <g stroke={p.paper} strokeWidth={7} fill="none" opacity={0.9}>
          <rect x={30} y={30} width={W - 60} height={H - 60} />
          <line x1={30} y1={H / 2} x2={W - 30} y2={H / 2} />
          <circle cx={W / 2} cy={H / 2} r={110} />
          <rect x={W / 2 - 200} y={30} width={400} height={170} />
          <rect x={W / 2 - 200} y={H - 200} width={400} height={170} />
          <rect x={W / 2 - 80} y={30} width={160} height={60} />
          <rect x={W / 2 - 80} y={H - 90} width={160} height={60} />
        </g>
        {HOME.map(([x, y], i) => dot(x, y, p.homeColor, i, false))}
        {f >= p.enterAwayAt - 2 && AWAY.map(([x, y], i) => dot(x, y, p.awayColor, i, true))}
        {flagP > 0 && (
          <g transform={`translate(${W * 0.5 - 20}, ${H + 120 - flagP * (H * 0.5 + 120)})`}>
            <line x1={0} y1={0} x2={0} y2={-150} stroke={p.ink} strokeWidth={8} />
            <foreignObject x={0} y={-150} width={200} height={140}>
              <div style={{ transform: `skewY(${Math.sin(f / 4) * 6}deg)`, transformOrigin: "0 50%" }}>
                <BrazilFlag w={190} />
              </div>
            </foreignObject>
            <circle r={30} fill={p.homeColor} stroke={p.ink} strokeWidth={6} />
          </g>
        )}
      </svg>
      {f > p.leaveAt + 10 && (
        <div style={{ position: "absolute", right: -20, top: 140 + H * 0.3, fontFamily: SANS, fontWeight: 900, fontSize: 40, background: p.paper, color: p.ink, padding: "8px 18px", border: `5px solid ${p.ink}`, transform: `rotate(6deg) scale(${spring({ frame: f - p.leaveAt - 10, fps, config: { damping: 10 } })})` }}>
          ABANDONOU O CAMPO →
        </div>
      )}
      <Sfx src={p.sfx.whoosh} at={p.scoreAt - 4} volumeDb={-4} />
      <Sfx src={p.sfx.crowd} at={p.scoreAt + 4} volumeDb={-10} durationInFrames={fps * 4} />
      <Sfx src={p.sfx.whoosh} at={p.leaveAt} volumeDb={-6} />
    </div>
  );
};
