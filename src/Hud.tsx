import React from 'react';
import {Img, staticFile} from 'remotion';
import {STOPS} from './data/stops.mjs';
import {T, STARTS, palette, cssColor} from './world/World';
import {clamp, eOut, eIO} from './lib/path.mjs';
// contador de ano: única camada sem parallax (presa à câmera), gira como odômetro entre as estações
export const COUNTER: [number, string][] = (() => {
  const out: [number, string][] = [[-1, '1830']];
  STOPS.forEach((s: any, k: number) => {
    if (s.counterAt) s.counterAt.forEach(([r, l]: any) => out.push([T(r) - 0.25, l]));
    else if (s.counter) out.push([STARTS[k] - 0.25, s.counter]);
  });
  return out;
})();
const ROLL = 0.55;
const Slot: React.FC<{a: string; b: string; p: number; color: string; h: number}> = ({a, b, p, color, h}) => {
  const isD = (c: string) => /[0-9]/.test(c);
  let strip: string[] = [a, b];
  if (isD(a) && isD(b) && a !== b) { strip = []; let d = +a; strip.push(String(d)); while (String(d) !== b) { d = (d + 1) % 10; strip.push(String(d)); } }
  const n = strip.length - 1, off = n * eIO(p);
  return (
    <span style={{display: 'inline-block', height: h, overflow: 'hidden', verticalAlign: 'top', position: 'relative'}}>
      <span style={{display: 'block', transform: `translateY(${-off * h}px)`}}>
        {strip.map((c, i) => <span key={i} style={{display: 'block', height: h, lineHeight: `${h}px`, color, textAlign: 'center', minWidth: c === ' ' ? h * 0.18 : undefined}}>{c === ' ' ? ' ' : c}</span>)}
      </span>
    </span>
  );
};
export const Counter: React.FC<{t: number}> = ({t}) => {
  let i = 0; while (i < COUNTER.length - 1 && COUNTER[i + 1][0] <= t) i++;
  const cur = COUNTER[i][1], prev = i > 0 ? COUNTER[i - 1][1] : cur, p = clamp((t - COUNTER[i][0]) / ROLL);
  const P = palette(t), color = cssColor(P.text), h = 150;
  const len = Math.max(cur.length, prev.length);
  const A = prev.padStart(len, ' '), B = cur.padStart(len, ' ');
  return (
    <div style={{position: 'absolute', top: 262, left: 0, width: 1080 - 140, display: 'flex', justifyContent: 'center', paddingLeft: 140, lineHeight: '150px', height: 150, overflow: 'hidden',
      fontFamily: 'Anton', fontSize: h * 0.92, letterSpacing: '-0.01em', textShadow: '0 0 0 transparent'}}>
      {[...B].map((c, k) => { const q = p < 1 ? clamp((p * 1.4) - k * 0.06) : 1; return q >= 1 || A[k] === c ? <span key={k} style={{color, whiteSpace: 'pre'}}>{c}</span> : <Slot key={k} a={A[k]} b={c} p={q} color={color} h={h} />; })}
    </div>
  );
};
export const Grain: React.FC<{frame: number}> = ({frame}) => (
  <Img src={staticFile(`tex/grain${Math.floor(frame / 2) % 6}.png`)} style={{position: 'absolute', inset: 0, width: 1080, height: 1920, mixBlendMode: 'overlay', opacity: 0.32, imageRendering: 'auto'}} />
);
