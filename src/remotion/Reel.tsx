import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, random} from 'remotion';
import {COL, FPS, W, H, SAFE, Scene, SceneView, blockAt, ink, clamp, ein, eout, eio, fontCss, Bg} from './engine';
import {SCENES, TRANSITIONS, LOOP_START, TOTAL, sHook, CAPTION_WORDS, HOOKS} from './timeline';

type Wd = {w: string; s: number; e: number; line: string};
const F = 1 / FPS;

// ---------- legenda secundária (Inter Bold 44px, 1–3 palavras) ----------
const groups = (WL: Wd[]) => {
  const g: Wd[][] = [];
  let cur: Wd[] = [];
  WL.forEach((w, i) => {
    cur.push(w);
    const next = WL[i + 1];
    if (cur.length >= 3 || /[.,?:!]$/.test(w.w) || !next || next.s - w.e > 0.25 || next.line !== w.line) {g.push(cur); cur = [];}
  });
  return g;
};
const Caption: React.FC<{T: number; WL: Wd[]; bg: Bg}> = ({T, WL, bg}) => {
  const G = groups(WL);
  const i = G.findIndex((g, k) => T >= g[0].s && (k === G.length - 1 ? T < g[g.length - 1].e + 0.35 : T < G[k + 1][0].s));
  if (i < 0) return null;
  const g = G[i];
  const p = clamp((T - g[0].s) * FPS / 3);
  return (
    <div style={{position: 'absolute', left: SAFE.left, width: W - SAFE.left - SAFE.right, top: H - SAFE.bottom - 92, display: 'flex', justifyContent: 'center'}}>
      <div style={{font: fontCss('I', 44), color: ink(bg), background: COL[bg], padding: '8px 22px 10px', transform: `scale(${0.92 + 0.08 * p})`, opacity: 0.5 + 0.5 * p, whiteSpace: 'nowrap'}}>
        {g.map((w) => w.w.replace(/[.,:]$/, '')).join(' ')}
      </div>
    </div>
  );
};

// ---------- selo do filme (título + país sempre na tela, funciona sem som) ----------
const Tag: React.FC<{S: Scene; T: number; bg: Bg}> = ({S, T, bg}) => {
  if (!S.tag || T < S.tag.from) return null;
  const p = eout((T - S.tag.from) * FPS / 6);
  return (
    <div style={{position: 'absolute', left: SAFE.left, top: SAFE.top, transform: `translateX(${(1 - p) * -60}px)`, opacity: p}}>
      <div style={{font: fontCss('A', 40), color: COL[bg], background: ink(bg), padding: '4px 14px 6px', letterSpacing: '0.02em'}}>{S.tag.text}</div>
    </div>
  );
};

// ---------- granulado de impressão por cima de tudo ----------
export const Grain: React.FC<{frame: number}> = ({frame}) => (
  <AbsoluteFill style={{backgroundImage: `url(${staticFile('img/grain.png')})`, backgroundPosition: `${Math.floor(random(`gx${frame}`) * 512)}px ${Math.floor(random(`gy${frame}`) * 512)}px`,
    mixBlendMode: 'overlay', opacity: 0.2, pointerEvents: 'none'}} />
);

const WhipFilter: React.FC<{amt: number}> = ({amt}) => (
  <svg width={0} height={0} style={{position: 'absolute'}}>
    <filter id="whip" x="-20%" y="0%" width="140%" height="100%"><feGaussianBlur stdDeviation={`${amt} 0`} /></filter>
  </svg>
);

// ---------- travessia do primeiro plano (máscara cobre a tela por 3–4 frames) ----------
const Crossing: React.FC<{q: number}> = ({q}) => {
  // q em frames relativos ao corte: -4..+2
  if (q < -4 || q > 1) return null;
  const sc = q <= -3 ? 3.2 : q <= -2 ? 7 : 16;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {q >= -2 ? <AbsoluteFill style={{background: COL.black}} /> : null}
      <Img src={staticFile('cut/e_mask.png')} style={{position: 'absolute', left: W / 2 - 537, top: H / 2 - 600, width: 1200 * 1073 / 1198, height: 1200,
        transform: `scale(${sc})`, transformOrigin: '50% 38%', filter: `blur(${q >= -2 ? 4 : 2}px)`}} />
    </AbsoluteFill>
  );
};

const sceneAt = (T: number) => SCENES.find((s) => T >= s.from && T < s.to) ?? SCENES[SCENES.length - 1];

export const ReelFrame: React.FC<{T: number; frame: number}> = ({T, frame}) => {
  // ---- loop final: câmera recua, camadas se afastam, remonta o primeiro quadro ----
  if (T >= LOOP_START) {
    const mid = LOOP_START + 0.5;
    if (T < mid) {
      const u = (T - LOOP_START) / 0.5;
      const S = SCENES[SCENES.length - 1];
      return <><SceneView S={S} T={S.to - 7 * F} camOff={{z: -700 * ein(u)}} spread={1 + 1.2 * ein(u)} /></>;
    }
    const u = clamp((T - mid) / (TOTAL - mid));
    const Th = -(TOTAL - T); // tempo negativo do gancho (remontagem)
    return <><SceneView S={sHook} T={Th} camOff={{z: -700 * (1 - eout(u))}} spread={1 + 1.2 * (1 - eout(u))} /></>;
  }
  const S = sceneAt(T);
  const B = blockAt(S, T);
  let view: React.ReactNode = <SceneView S={S} T={T} />;
  let overlay: React.ReactNode = null;
  let whipAmt = 0;
  for (const tr of TRANSITIONS) {
    const q = Math.round((T - tr.at) * FPS); // frames em relação ao corte
    if (tr.kind === 'whip' && q >= -5 && q <= 4) {
      const prev = SCENES.find((s) => Math.abs(s.to - tr.at) < 0.01)!;
      const next = SCENES.find((s) => Math.abs(s.from - tr.at) < 0.01)!;
      const sgn = prev.dir;
      if (q < 0) {const u = (q + 6) / 6; whipAmt = 70 * ein(u); view = <SceneView S={prev} T={T} camOff={{x: sgn * 1700 * ein(u)}} extraFilter="url(#whip)" />;}
      else {const u = (q + 1) / 5; whipAmt = 70 * (1 - eout(u)); view = <SceneView S={next} T={T} camOff={{x: -sgn * 1700 * (1 - eout(u))}} extraFilter="url(#whip)" />;}
    }
    if (tr.kind === 'cross' && q >= -4 && q <= 1) overlay = <Crossing q={q} />;
    if (tr.kind === 'tv' && q >= -6 && q < 0) {
      // zoom até estourar o quadro; a cena seguinte mostra a anterior dentro de uma TV
      const prev = SCENES.find((s) => Math.abs(s.to - tr.at) < 0.01)!;
      const u = (q + 7) / 7;
      view = <SceneView S={prev} T={T} camOff={{z: 520 * ein(u)}} scale={1 + 0.6 * ein(u)} />;
    }
  }
  return (
    <>
      <WhipFilter amt={whipAmt} />
      {view}
      <Tag S={S} T={T} bg={B.bg} />
      <Caption T={T} WL={CAPTION_WORDS.A} bg={B.bg} />
      {overlay}
      
    </>
  );
};

export const Reel: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background: COL.gray}}><ReelFrame T={f / FPS} frame={f} /></AbsoluteFill>;
};

export const Gancho: React.FC<{v: 'A' | 'B' | 'C'}> = ({v}) => {
  const f = useCurrentFrame(); const T = f / FPS;
  const S = HOOKS[v].scene; const B = blockAt(S, T);
  return (
    <AbsoluteFill style={{background: COL.gray}}>
      <SceneView S={S} T={T} />
      <Caption T={T} WL={CAPTION_WORDS[v]} bg={B.bg} />
      
    </AbsoluteFill>
  );
};
