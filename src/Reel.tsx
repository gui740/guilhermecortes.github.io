import React from "react";
import { AbsoluteFill, Freeze, useCurrentFrame } from "remotion";
import { C, Bg, W, H } from "./theme";
import { TLS, EVENTS, makeW, sceneStart } from "./timeline";
import { SceneCtx, Phone, clamp01, outCubic } from "./kit";
import * as S from "./scenes";

const tl = TLS.main;
const A = makeW(tl);
const w = A.w;
type Def = { id: string; line: string; bg: Bg; whipIn?: boolean; whipOut?: boolean; zoomOut?: boolean; exit?: boolean; render: (ctx: { s: number; e: number }) => React.ReactNode };
const defs: Def[] = [
  { id: "h1", line: "h1", bg: "black", render: () => <S.H1 fr={[0, 1, 2, 3, 4, 5, 6].map((i) => w("h1", i))} /> },
  { id: "h2", line: "h2", bg: "red", zoomOut: true, exit: false, render: () => <S.H2 rows={S.h2Rows(w)} qAt={w("h2", 1)} /> },
  { id: "f3", line: "f3a", bg: "gray", render: () => null },
  { id: "f3c", line: "f3c", bg: "black", render: () => <S.F3c w={w} /> },
  { id: "f3d", line: "f3d", bg: "red", whipOut: true, exit: false, render: () => <S.F3d w={w} /> },
  { id: "m1", line: "m1", bg: "gray", whipIn: true, whipOut: true, exit: false, render: () => <S.M1 w={w} /> },
  { id: "f2", line: "f2a", bg: "black", whipIn: true, render: () => <S.F2 w={w} /> },
  { id: "f2c", line: "f2c", bg: "gray", render: () => <S.F2c w={w} /> },
  { id: "f2d", line: "f2d", bg: "red", whipOut: true, exit: false, render: () => <S.F2d w={w} /> },
  { id: "s1", line: "s1", bg: "black", whipIn: true, whipOut: true, exit: false, render: () => <S.S1 w={w} /> },
  { id: "f1", line: "f1a", bg: "red", whipIn: true, render: () => <S.F1 w={w} /> },
  { id: "f1c", line: "f1c", bg: "gray", render: () => <S.F1c w={w} /> },
  { id: "f1d", line: "f1d", bg: "black", render: () => <S.F1d w={w} /> },
  { id: "c1", line: "c1", bg: "red", render: () => <S.C1 w={w} /> },
  { id: "c2", line: "c2", bg: "gray", render: () => <S.C2 w={w} /> },
  { id: "c3", line: "c3", bg: "black", render: () => <S.C3 w={w} /> },
];
export const REEL_FRAMES = EVENTS.main.frames;
const starts = defs.map((d, i) => (i === 0 ? 0 : sceneStart(A.line(d.line).t)));
const scenes = defs.map((d, i) => ({ ...d, s: starts[i], e: i + 1 < defs.length ? starts[i + 1] : REEL_FRAMES }));
const H2S = scenes[1];
// a cena f3 recebe a cena anterior congelada dentro de um celular (transição zoom)
scenes[2].render = ({ s }) => (
  <S.F3
    w={w}
    phone={
      <Phone at={s} tx={590} ty={1330} w={440} leave={w("f3b", 0) - 4}>
        <Freeze frame={H2S.e - 5}>
          <SceneCtx.Provider value={{ s: H2S.s, e: H2S.e, bg: "red", exit: false }}>
            <AbsoluteFill style={{ background: C.red }}>{H2S.render(H2S)}</AbsoluteFill>
          </SceneCtx.Provider>
        </Freeze>
      </Phone>
    }
  />
);

export const Filters: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <defs>
      <filter id="hblur" x="-60%" width="220%"><feGaussianBlur stdDeviation="46 0" /></filter>
      <filter id="hblur2" x="-30%" width="160%"><feGaussianBlur stdDeviation="90 0" /></filter>
    </defs>
  </svg>
);

export const Reel: React.FC = () => {
  const f = useCurrentFrame();
  const i = Math.max(0, scenes.findIndex((sc) => f >= sc.s && f < sc.e));
  const sc = scenes[i];
  const local = f - sc.s, rem = sc.e - f;
  let tx = 0, scale = 1, filter: string | undefined;
  let under: string = C[sc.bg];
  if (sc.whipIn && local < 4) { const p = outCubic((local + 1) / 5); tx = (1 - p) * W; filter = "url(#hblur2)"; under = C[scenes[i - 1].bg]; }
  if (sc.whipOut && rem <= 3) { const p = Math.pow((4 - rem) / 4, 2); tx = -p * W; filter = "url(#hblur2)"; under = C[scenes[i + 1].bg]; }
  if (sc.zoomOut && rem <= 5) { scale = 1 + Math.pow((6 - rem) / 6, 2) * 1.6; }
  return (
    <AbsoluteFill style={{ background: under, overflow: "hidden" }}>
      <Filters />
      <SceneCtx.Provider value={{ s: sc.s, e: sc.e, bg: sc.bg, exit: sc.exit !== false }}>
        <AbsoluteFill style={{ background: C[sc.bg], transform: `translateX(${tx}px) scale(${scale})`, transformOrigin: "50% 62%", filter }}>
          {sc.render(sc)}
        </AbsoluteFill>
      </SceneCtx.Provider>
    </AbsoluteFill>
  );
};
