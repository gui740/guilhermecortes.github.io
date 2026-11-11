import React from 'react';
import {interpolate, useCurrentFrame, Easing} from 'remotion';
import {Bg, C, HL, SAFE, TEXT, W} from './theme';
import {Eraser} from './Graphics';

export type Word = {text: string; f: number; role: string; hl: boolean};

const MAXW = W - SAFE.left - SAFE.right; // 860
const ANTON_EM = 0.5; // largura média de um caractere maiúsculo Anton (em)
const PLAY_EM = 0.5 * 0.8; // Playfair itálico comprimido a 80%

const isAnton = (r: string) => r === 'B' || r === 'b' || r === 's';

function baseSize(w: Word) {
  const n = Math.max(2, w.text.length);
  switch (w.role) {
    case 'B': return Math.min(330, (MAXW * 0.86) / (n * ANTON_EM));
    case 'b': return Math.min(175, (MAXW * 0.62) / (n * ANTON_EM));
    case 's': return 54;
    case 'P': return Math.min(290, (MAXW * 0.8) / (n * PLAY_EM));
    case 'p': return Math.min(160, (MAXW * 0.62) / (n * PLAY_EM));
    case 'T': return Math.min(380, (MAXW * 0.92) / (n * PLAY_EM));
    default: return 80;
  }
}
const est = (w: Word, s: number) => w.text.length * s * (isAnton(w.role) ? ANTON_EM : PLAY_EM);

// Simula a quebra de linha para garantir que o título caiba no terço superior
export function layoutScale(words: Word[], maxH: number) {
  let k = 1;
  for (let it = 0; it < 30; it++) {
    let lineW = 0, lineH = 0, total = 0;
    for (const w of words) {
      const s = baseSize(w) * k;
      const ww = est(w, s) + 14;
      if ((lineW + ww > MAXW || w.role === 'T') && lineW > 0) { total += lineH; lineW = 0; lineH = 0; }
      lineW += ww;
      lineH = Math.max(lineH, s * (isAnton(w.role) ? 0.98 : 1.05));
    }
    total += lineH;
    if (total <= maxH) return k;
    k *= 0.93;
  }
  return k;
}

export const Headline: React.FC<{
  words: Word[];
  bg: Bg;
  end: number; // frame (local) de fim do bloco
  maxH?: number;
  top?: number;
  strikeIdx?: number;
  eraseIdx?: number;
}> = ({words, bg, end, maxH = 560, top = SAFE.top, strikeIdx = -1, eraseIdx = -1}) => {
  const frame = useCurrentFrame();
  const shown = words.filter((w) => w.role !== 'x');
  const k = layoutScale(shown, maxH);
  return (
    <div
      style={{
        position: 'absolute', left: SAFE.left, top, width: MAXW,
        display: 'flex', flexWrap: 'wrap', justifyContent: 'center', alignItems: 'baseline',
        alignContent: 'flex-start', columnGap: 14, rowGap: 0, perspective: 900,
      }}
    >
      {words.map((w, oi) => {
        if (w.role === 'x') return null;
        const i = shown.indexOf(w);
        const s = baseSize(w) * k;
        const t = frame - w.f;
        // Entrada: desfocado 12px, cinza 40%, escala 0.9 → firma em 5 frames
        const p = interpolate(t, [0, 5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        // Saída: gira em 3D e some nos últimos frames do bloco (escalonado)
        const outStart = end - 5 + Math.min(i, 3) * 0.6;
        const q = interpolate(frame, [outStart, end], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad)});
        const visible = t >= 0;
        const color = w.hl ? HL[bg] : TEXT[bg];
        const anton = isAnton(w.role);
        const txt = anton ? w.text.toUpperCase() : w.text;
        const estW = est(w, s);
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              fontFamily: anton ? 'Anton' : 'Playfair',
              fontStyle: anton ? 'normal' : 'italic',
              fontWeight: anton ? 400 : 900,
              fontSize: s,
              lineHeight: anton ? 0.98 : 1.05,
              letterSpacing: anton ? (w.role === 's' ? 1 : -1) : -2,
              color: visible ? mix('#8a8a8a', color, p) : 'transparent',
              opacity: visible ? (0.4 + 0.6 * p) * (1 - q) : 0,
              filter: `blur(${(1 - p) * 12}px)`,
              transform: `${anton ? '' : 'scaleX(0.8)'} scale(${0.9 + 0.1 * p}) rotateX(${q * 85}deg)`,
              transformOrigin: anton ? '50% 50%' : '0% 50%',
              marginRight: anton ? 0 : -estW * 0.2 - 4,
              whiteSpace: 'nowrap',
              position: 'relative',
              ...(w.role === 'T' ? {flexBasis: '100%', textAlign: 'center', marginRight: 0, transform: `scaleX(0.8) scale(${0.9 + 0.1 * p}) rotateX(${q * 85}deg)`, transformOrigin: '50% 50%'} : {}),
            }}
          >
            <span style={{position: 'relative', display: 'inline-block', clipPath: oi === eraseIdx ? `inset(0 0 0 ${interpolate(t, [8, 20], [0, 55], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}%)` : undefined}}>{txt}</span>
            {oi === strikeIdx && (
              <span style={{position: 'absolute', left: '-4%', top: '46%', height: Math.max(10, s * 0.11), background: C.R, borderRadius: 4,
                width: `${interpolate(t, [4, 10], [0, 108], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}%`, transform: 'rotate(-4deg)'}} />
            )}
            {oi === eraseIdx && t >= 6 && t <= 24 && (
              <span style={{position: 'absolute', top: 0, left: `${interpolate(t, [8, 20], [0, 55], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}%`}}>
                <Eraser x={0} y={s * 0.55} rot={Math.sin(t * 1.3) * 10} />
              </span>
            )}
          </span>
        );
      })}
    </div>
  );
};

function mix(a: string, b: string, t: number) {
  const pa = hex(a), pb = hex(b);
  const r = pa.map((v, i) => Math.round(v + (pb[i] - v) * t));
  return `rgb(${r[0]},${r[1]},${r[2]})`;
}
function hex(h: string) {
  const n = parseInt(h.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

// Legenda secundária: Inter Bold ~44px, 1–3 palavras por vez, centralizada
export const Caption: React.FC<{words: Word[]; y?: number}> = ({words, y = 1395}) => {
  const frame = useCurrentFrame();
  const chunks: Word[][] = [];
  let cur: Word[] = [];
  words.forEach((w) => {
    cur.push(w);
    if (cur.length === 3 || /[?]$/.test(w.text)) { chunks.push(cur); cur = []; }
  });
  if (cur.length) chunks.push(cur);
  let active = -1;
  chunks.forEach((c, i) => { if (frame >= c[0].f) active = i; });
  if (active < 0) return null;
  const c = chunks[active];
  return (
    <div style={{position: 'absolute', left: SAFE.left, width: MAXW, top: y, display: 'flex', justifyContent: 'center'}}>
      <div style={{background: '#1C1C1C', padding: '10px 22px 12px', borderRadius: 10, fontFamily: 'Inter', fontWeight: 800, fontSize: 44, color: '#FFFFFF', letterSpacing: -0.5}}>
        {c.filter((w) => frame >= w.f).map((w, i) => (
          <span key={i} style={{color: w.hl ? '#F2E63A' : '#FFFFFF', marginRight: 12}}>{w.text.toUpperCase()}</span>
        ))}
      </div>
    </div>
  );
};
