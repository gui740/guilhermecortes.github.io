import React from 'react';
import {AbsoluteFill, Sequence, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, Bg} from './theme';
import {Headline, Caption, Word} from './Headline';
import {Grid, Star, TV, Hand, Scissors, DashLine, Static} from './Graphics';

export type Block = {
  bg: Bg; cut: string; scale: string; enter: string; start: number; end: number; words: Word[];
  grid?: boolean; cap?: boolean; fx?: string; dup?: boolean; burst?: boolean; title?: boolean; handle?: boolean;
  swap?: {at: number; atLocal: number; cut: string; scale: string; dup?: boolean};
};

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const BOX: Record<string, React.CSSProperties> = {
  close: {left: -110, width: 1300, bottom: -80, height: 1280},
  medium: {left: 30, width: 1020, bottom: 70, height: 1060},
  small: {left: 170, width: 740, top: 930, height: 620},
};

// Recorte colorido texturizado (com contorno branco quando o fundo pede)
const Cutout: React.FC<{name: string; scale: string; enter: string; bg: Bg; dur: number; dup?: boolean; burst?: boolean; seed?: number}> = ({name, scale, enter, bg, dur, dup, burst, seed = 0}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const outline = bg !== 'G' || name === 'bunny';
  const src = staticFile(`cut/${name}${outline ? '' : '_n'}.png`);
  const WIDE = ['kids_forest', 'kids_scared', 'buddy_group'];
  const box = name === 'kids_forest' ? {left: -160, width: 1400, bottom: -20, height: 1000} : scale === 'medium' && WIDE.includes(name) ? {left: -70, width: 1220, bottom: 60, height: 980} : (BOX[scale] ?? BOX.medium);
  // movimento contínuo (nenhum quadro parado)
  const drift = 1 + 0.06 * (f / Math.max(1, dur));
  const floatY = Math.sin((f + seed * 13) / 9) * 6;
  let tx = 0, sc = 1, blurX = 0, op = 1;
  if (enter === 'cross') {
    // atravessa a tela com motion blur e volta pro lugar
    const p = interpolate(f, [0, 7], [0, 1], clamp);
    tx = interpolate(p, [0, 0.55, 1], [-1300, 380, 0]);
    blurX = interpolate(f, [0, 3, 7, 9], [70, 90, 25, 0], clamp);
  } else if (enter === 'whip') {
    tx = interpolate(f, [0, 6], [760, 0], {...clamp, easing: Easing.out(Easing.cubic)});
    blurX = interpolate(f, [0, 6], [80, 0], clamp);
  } else if (enter === 'zoomout') {
    sc = interpolate(f, [0, 8], [2.7, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  } else {
    sc = 0.86 + 0.14 * spring({frame: f, fps, config: {damping: 12, stiffness: 170}});
  }
  if (burst) {
    // zoom até estourar o quadro
    const b = interpolate(f, [dur - 6, dur], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
    sc *= 1 + b * 3.2;
  }
  const fid = `mb_${name}_${seed}`;
  const img = (extra: React.CSSProperties, key: string) => (
    <div key={key} style={{position: 'absolute', ...box, ...extra}}>
      <Img src={src} style={{width: '100%', height: '100%', objectFit: 'contain', objectPosition: scale === 'small' ? 'center center' : 'center bottom', filter: blurX > 0.5 ? `url(#${fid})` : undefined}} />
    </div>
  );
  return (
    <AbsoluteFill style={{opacity: op}}>
      <svg width={0} height={0} style={{position: 'absolute'}}>
        <filter id={fid} x="-50%" width="200%"><feGaussianBlur stdDeviation={`${blurX} 0`} /></filter>
      </svg>
      {dup && img({transform: `translate(${300 + tx * 0.6}px, ${-560 + floatY}px) scale(${0.42 * sc}) rotate(8deg)`, transformOrigin: '50% 50%', opacity: 0.95}, 'dup')}
      {img({transform: `translate(${tx}px, ${floatY}px) scale(${sc * drift})`, transformOrigin: scale === 'small' ? '50% 50%' : '50% 100%'}, 'main')}
    </AbsoluteFill>
  );
};

export const Scene: React.FC<{b: Block}> = ({b}) => {
  const f = useCurrentFrame();
  const dur = b.end - b.start;
  const lineColor = b.bg === 'K' ? C.Y : b.bg === 'R' ? '#FFFFFF' : C.K;
  const swapAt = b.swap ? b.words[b.swap.atLocal].f : 9999;
  const swapped = f >= swapAt;
  const glitch = b.swap && f >= swapAt && f < swapAt + 5;
  const strikeIdx = b.fx === 'strike' ? b.words.length - 1 : -1;
  const eraseIdx = b.fx === 'eraser' ? 4 : -1;
  const hiddenHeadline = b.fx === 'tv';
  return (
    <AbsoluteFill style={{background: C[b.bg], overflow: 'hidden', transform: glitch ? `translate(${(f % 2 ? 1 : -1) * 18}px, ${(f % 3) * 6}px)` : undefined}}>
      {b.grid && <Grid color={C.K} />}
      {b.fx === 'star' && <Star cx={540} cy={1250} r={560} />}
      {b.fx === 'tv' ? (
        <TV x={60} y={860} w={960} h={780}>
          <div style={{position: 'absolute', inset: 0, background: C.R}} />
          <div style={{position: 'absolute', inset: 0, transform: `scale(${interpolate(f, [0, 8], [2.7, 1], {...clamp, easing: Easing.out(Easing.cubic)}) * (1 + 0.05 * f / dur)})`}}>
            <Img src={staticFile('cut/buddy_tvpo_n.png')} style={{position: 'absolute', left: '8%', width: '84%', bottom: -10, height: '100%', objectFit: 'contain', objectPosition: 'center bottom'}} />
          </div>
        </TV>
      ) : !swapped ? (
        <Cutout name={b.cut} scale={b.scale} enter={b.enter} bg={b.bg} dur={dur} dup={b.dup} burst={b.burst} seed={b.start} />
      ) : (
        <Sub from={swapAt}><Cutout name={b.swap!.cut} scale={b.swap!.scale} enter="pop" bg={b.bg} dur={dur - swapAt} dup={b.swap!.dup} seed={b.start + 1} /></Sub>
      )}
      {b.fx === 'scissors' && <ScissorsFx w={b.words} color={lineColor} />}
      {b.fx === 'dash' && <DashFx w={b.words} color={C.R} />}
      {b.fx === 'cursor' && <CursorFx w={b.words} />}
      {!hiddenHeadline && <Headline words={b.words} bg={b.bg} end={dur} strikeIdx={strikeIdx} eraseIdx={eraseIdx} maxH={b.fx === 'scissors' || b.handle ? 500 : 560} />}
      {hiddenHeadline && <Headline words={b.words} bg={b.bg} end={dur} maxH={430} />}
      {b.cap && <Caption words={b.words} />}
      {b.handle && <HandleFx w={b.words} />}
      {glitch && <Static opacity={0.5} id="gl" />}
    </AbsoluteFill>
  );
};

const Sub: React.FC<{from: number; children: React.ReactNode}> = ({from, children}) => (
  <Sequence from={from} layout="none">{children}</Sequence>
);

const ScissorsFx: React.FC<{w: Word[]; color: string}> = ({w, color}) => {
  const f = useCurrentFrame();
  const t0 = w[2]?.f ?? 10; // "curtinhos"
  const p = interpolate(f, [t0 - 4, t0 + 16], [0, 1], clamp);
  const y = 820, x0 = 80, x1 = 1000;
  const x = x0 + (x1 - x0) * p;
  return (
    <>
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <line x1={x0} y1={y} x2={x1} y2={y} stroke={color} strokeWidth={6} strokeDasharray="22 16" opacity={0.85} />
        {/* parte já cortada se abre */}
        <line x1={x0} y1={y + 10} x2={x} y2={y + 26} stroke={color} strokeWidth={6} strokeDasharray="22 16" opacity={p > 0 ? 0.5 : 0} />
      </svg>
      <Scissors x={x} y={y} open={(Math.sin(f * 1.4) + 1) / 2} />
    </>
  );
};

const DashFx: React.FC<{w: Word[]; color: string}> = ({w, color}) => {
  const f = useCurrentFrame();
  const t0 = w[0].f;
  const p = interpolate(f, [t0 + 2, w[w.length - 1].f + 4], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const d = 'M 300 1270 C 120 1060, 260 860, 560 900 S 900 820, 860 700';
  return (
    <>
      <DashLine d={d} progress={p} color={color} />
      <div style={{position: 'absolute', left: 820, top: 660, width: 80, height: 80, borderRadius: 40, border: `10px solid ${color}`, transform: `scale(${p > 0.97 ? 1 : 0})`}} />
    </>
  );
};

const CursorFx: React.FC<{w: Word[]}> = ({w}) => {
  const f = useCurrentFrame();
  const tClick = w[3].f; // "volta"
  const p = interpolate(f, [0, tClick], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const press = interpolate(f, [tClick, tClick + 2, tClick + 6], [0, 1, 0], clamp);
  return <Hand x={interpolate(p, [0, 1], [930, 700])} y={interpolate(p, [0, 1], [1560, 640])} press={press} scale={1.1} />;
};

const HandleFx: React.FC<{w: Word[]}> = ({w}) => {
  const f = useCurrentFrame();
  const tSeg = w[3].f; // "segue"
  const show = interpolate(f, [tSeg - 2, tSeg + 3], [0, 1], clamp);
  const press = interpolate(f, [tSeg + 8, tSeg + 10, tSeg + 14], [0, 1, 0], clamp);
  const followed = f > tSeg + 10;
  return (
    <div style={{position: 'absolute', left: 80, width: 860, top: 1270, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: show, transform: `scale(${0.9 + 0.1 * show})`}}>
      <div style={{fontFamily: 'Inter', fontWeight: 800, fontSize: 56, color: C.Y, background: C.K, padding: '8px 26px 12px', borderRadius: 14, letterSpacing: -1}}>@talking_horror</div>
      <div style={{position: 'relative', marginTop: 16, background: followed ? C.K : C.R, color: followed ? C.Y : '#FFFFFF', fontFamily: 'Inter', fontWeight: 800, fontSize: 46, padding: '14px 48px', borderRadius: 14, transform: `scale(${1 - press * 0.08})`}}>
        {followed ? 'SEGUINDO' : 'SEGUIR'}
        <div style={{position: 'absolute', left: '62%', top: '55%'}}>
          <Hand x={0} y={0} press={press} scale={0.8} />
        </div>
      </div>
    </div>
  );
};
