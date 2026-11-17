import React from 'react';
import {AbsoluteFill, staticFile, useCurrentFrame} from 'remotion';
import {ASPECT, FPS, SAFE, WORDS, VO, beamAt, beamOnAt, camAt, clamp, redAt, smooth} from './timeline';
import hookWords from './hook_words.json';

const fontFaces = `
@font-face{font-family:'Anton';src:url(${staticFile('fonts/Anton.ttf')});}
@font-face{font-family:'InterB';src:url(${staticFile('fonts/InterBold.ttf')});font-weight:700;}
@font-face{font-family:'Elite';src:url(${staticFile('fonts/SpecialElite.ttf')});}
`;

// legenda secundária: blocos de 1 a 3 palavras
type Chunk = {text: string; s: number; e: number};
const mkChunks = (WORDS: {w: string; s: number; e: number; phrase: number}[]): Chunk[] => {
  const out: Chunk[] = [];
  let cur: typeof WORDS = [];
  const flush = () => {
    if (!cur.length) return;
    out.push({text: cur.map((w) => w.w).join(' '), s: cur[0].s, e: cur[cur.length - 1].e});
    cur = [];
  };
  WORDS.forEach((w, i) => {
    const next = WORDS[i + 1];
    cur.push(w);
    const punct = /[.,!?:…]$/.test(w.w);
    const phraseEnd = !next || next.phrase !== w.phrase;
    if (cur.length >= 3 || punct || phraseEnd || (cur.length >= 2 && w.w.length > 7)) flush();
  });
  flush();
  for (let i = 0; i < out.length; i++) out[i].e = Math.min(out[i].e + 0.25, out[i + 1] ? out[i + 1].s : out[i].e + 0.4);
  return out;
};
const CH: Record<string, Chunk[]> = {
  A: mkChunks(WORDS),
  B: mkChunks((hookWords as any).B.map((w: any) => ({...w, s: w.s + VO, e: w.e + VO}))),
  C: mkChunks((hookWords as any).C.map((w: any) => ({...w, s: w.s + VO, e: w.e + VO}))),
};

export const Overlay: React.FC<{captions?: boolean; hud?: boolean; variant?: 'A' | 'B' | 'C'}> = ({captions = true, hud = true, variant = 'A'}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const on = beamOnAt(t);
  const red = redAt(t);
  const c = camAt(t);
  const tanH = Math.tan(((c.fov / 2) * Math.PI) / 180);
  const b = beamAt(t);
  const bx = 50 + (b.x / (tanH * ASPECT)) * 50;
  const by = 50 - (b.y / tanH) * 50;
  const siren = 0.1 + 0.06 * Math.sin(t * 5.5) + 0.32 * red;
  const chunk = CH[variant].find((k) => t >= k.s && t < k.e);
  const tc = `${String(Math.floor(t / 60)).padStart(2, '0')}:${String(Math.floor(t % 60)).padStart(2, '0')}:${String(frame % FPS).padStart(2, '0')}`;
  const recOn = Math.floor(t * 1.6) % 2 === 0;
  const dark = t >= 38.16 && t < 38.5 ? 1 : t < 0.13 ? 0.15 : 0;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <style>{fontFaces}</style>
      {/* glow do facho da lanterna */}
      <AbsoluteFill style={{background: `radial-gradient(circle at ${bx}% ${by}%, rgba(237,237,237,${0.13 * on}) 0%, rgba(237,237,237,${0.05 * on}) 18%, rgba(0,0,0,0) 42%)`, mixBlendMode: 'screen'}} />
      {/* vinheta escura */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 45%, rgba(10,10,10,0.55) 82%, rgba(5,5,5,0.85) 100%)'}} />
      {/* sirene vermelha pulsando nas bordas */}
      <AbsoluteFill style={{boxShadow: `inset 0 0 260px 40px rgba(242,59,59,${siren})`}} />
      {/* granulado animado */}
      <AbsoluteFill style={{opacity: 0.16, mixBlendMode: 'overlay'}}>
        <svg width="100%" height="100%">
          <filter id={`g${frame}`}>
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={frame % 97} stitchTiles="stitch" />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width="100%" height="100%" filter={`url(#g${frame})`} />
        </svg>
      </AbsoluteFill>
      {/* linhas de varredura VHS leves */}
      <AbsoluteFill style={{background: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.10) 0px, rgba(0,0,0,0.10) 2px, rgba(0,0,0,0) 3px, rgba(0,0,0,0) 5px)', opacity: 0.5}} />
      {/* apagão da lanterna */}
      {dark > 0 && <AbsoluteFill style={{background: '#000', opacity: dark}} />}
      {hud && (
        <>
          <div style={{position: 'absolute', left: SAFE.left + 10, top: SAFE.top + 6, display: 'flex', alignItems: 'center', gap: 16, fontFamily: 'InterB', fontSize: 40, color: '#EDEDED', letterSpacing: 2, textShadow: '0 2px 6px rgba(0,0,0,.8)'}}>
            <div style={{width: 30, height: 30, borderRadius: 15, background: '#F23B3B', opacity: recOn ? 1 : 0.15}} />
            REC
          </div>
          <div style={{position: 'absolute', left: SAFE.left + 10, top: SAFE.top + 62, fontFamily: 'Elite', fontSize: 38, color: '#EDEDED', letterSpacing: 3, textShadow: '0 2px 6px rgba(0,0,0,.8)'}}>
            {tc}
          </div>
          <div style={{position: 'absolute', right: SAFE.right + 10, top: SAFE.top + 6, fontFamily: 'Elite', fontSize: 38, color: '#EDEDED', letterSpacing: 3, textShadow: '0 2px 6px rgba(0,0,0,.8)'}}>
            PLAY ▶
          </div>
        </>
      )}
      {captions && chunk && (
        <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1920 - SAFE.bottom - 96, textAlign: 'center', fontFamily: 'InterB', fontSize: 46, color: '#EDEDED', textShadow: '0 0 14px rgba(0,0,0,1), 0 3px 4px rgba(0,0,0,1)', transform: `scale(${0.94 + 0.06 * clamp((t - chunk.s) / 0.1)})`}}>
          <span style={{background: 'rgba(28,28,28,0.72)', padding: '6px 18px', borderRadius: 6}}>{chunk.text}</span>
        </div>
      )}
    </AbsoluteFill>
  );
};
export const _unused = smooth;
