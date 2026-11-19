import type {Line} from '../content';
export const C = {char: '#1C1C1C', light: '#EDEDED', red: '#F23B3B', yellow: '#F2E63A'};
export type Tex = {canvas: HTMLCanvasElement; w: number; h: number};
const mk = (w: number, h: number) => {
  const c = document.createElement('canvas');
  c.width = Math.ceil(w); c.height = Math.ceil(h);
  return c;
};
// PRNG determinístico
export const rng = (seed: number) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const colorOf = (c?: string) => (c === 'yellow' ? C.yellow : c === 'red' ? C.red : C.light);

// Palavra-chave gigante + conectivo minúsculo encostado nela
export function keywordTex(line: Line, bigPx = 360): Tex {
  const smallPx = Math.round(bigPx * 0.30);
  const pad = Math.round(bigPx * 0.18);
  const m = mk(10, 10).getContext('2d')!;
  m.font = `${bigPx}px Anton`;
  const bw = m.measureText(line.big).width;
  m.font = `${smallPx}px Anton`;
  const sw = line.small ? m.measureText(line.small).width : 0;
  const W = Math.max(bw, sw) + pad * 2;
  const H = bigPx * 1.12 + (line.small ? smallPx * 1.05 : 0) + pad * 2;
  const c = mk(W, H); const g = c.getContext('2d')!;
  g.textBaseline = 'alphabetic';
  g.shadowColor = 'rgba(28,28,28,0.9)'; g.shadowBlur = bigPx * 0.12;
  let y = pad;
  if (line.small) {
    g.font = `${smallPx}px Anton`; g.fillStyle = C.light;
    y += smallPx * 0.95; g.fillText(line.small, pad + bigPx * 0.02, y);
    y += smallPx * 0.02;
  }
  g.font = `${bigPx}px Anton`; g.fillStyle = colorOf(line.color);
  y += bigPx * 1.0; g.fillText(line.big, pad, y);
  return {canvas: c, w: W, h: H};
}

export function titleTex(text: string, color: string, px = 420): Tex {
  const sx = 0.8; // Playfair Display Italic comprimida ~80%
  const m = mk(10, 10).getContext('2d')!;
  m.font = `italic 900 ${px}px "Playfair Display"`;
  const tw = m.measureText(text).width * sx;
  const pad = px * 0.2;
  const c = mk(tw + pad * 2, px * 1.35 + pad); const g = c.getContext('2d')!;
  g.save(); g.translate(pad, px * 1.0 + pad * 0.3); g.scale(sx, 1);
  g.font = `italic 900 ${px}px "Playfair Display"`;
  g.shadowColor = 'rgba(28,28,28,0.95)'; g.shadowBlur = px * 0.1;
  g.fillStyle = color; g.fillText(text, 0, 0);
  g.restore();
  return {canvas: c, w: c.width, h: c.height};
}

export function numberTex(n: string, px = 900): Tex {
  const c = mk(px * 0.95, px * 1.25); const g = c.getContext('2d')!;
  g.font = `italic 900 ${px}px "Playfair Display"`;
  g.textAlign = 'center'; g.fillStyle = C.light;
  g.fillText(n, c.width / 2, px * 1.0);
  return {canvas: c, w: c.width, h: c.height};
}

// Etiqueta de fita de locadora (ano · país)
export function labelTex(text: string, px = 64): Tex {
  const m = mk(10, 10).getContext('2d')!;
  m.font = `${px}px "Special Elite"`;
  const tw = m.measureText(text).width;
  const W = tw + px * 1.2, H = px * 2.0;
  const c = mk(W + 20, H + 20); const g = c.getContext('2d')!;
  const r = rng(7);
  g.translate(10, 10);
  g.fillStyle = C.light;
  g.beginPath(); g.moveTo(0, 0);
  for (let x = 0; x <= W; x += 14) g.lineTo(x, r() * 3);
  for (let y = 0; y <= H; y += 14) g.lineTo(W - r() * 3, y);
  for (let x = W; x >= 0; x -= 14) g.lineTo(x, H - r() * 3);
  for (let y = H; y >= 0; y -= 14) g.lineTo(r() * 3, y);
  g.closePath(); g.fill();
  g.fillStyle = C.yellow; g.fillRect(0, 0, W, px * 0.32);
  g.fillStyle = C.char; g.font = `${px}px "Special Elite"`;
  g.fillText(text, px * 0.6, px * 1.5);
  // textura de papel
  for (let i = 0; i < 2500; i++) { g.fillStyle = `rgba(28,28,28,${r() * 0.08})`; g.fillRect(r() * W, r() * H, 2, 2); }
  return {canvas: c, w: c.width, h: c.height};
}

export function smallTex(text: string, font: string, px: number, color: string): Tex {
  const m = mk(10, 10).getContext('2d')!; m.font = `${px}px ${font}`;
  const tw = m.measureText(text).width; const pad = px * 0.3;
  const c = mk(tw + pad * 2, px * 1.4 + pad); const g = c.getContext('2d')!;
  g.font = `${px}px ${font}`; g.shadowColor = 'rgba(28,28,28,0.9)'; g.shadowBlur = px * 0.15;
  g.fillStyle = color; g.fillText(text, pad, px * 1.05 + pad * 0.3);
  return {canvas: c, w: c.width, h: c.height};
}

// Pergunta final numa linha, com UMA palavra de destaque
export function questionTex(parts: {t: string; c: string}[], px = 150): Tex {
  const m = mk(10, 10).getContext('2d')!; m.font = `${px}px Anton`;
  const ws = parts.map((p) => m.measureText(p.t).width); const tw = ws.reduce((a, b) => a + b, 0);
  const pad = px * 0.25; const c = mk(tw + pad * 2, px * 1.3 + pad); const g = c.getContext('2d')!;
  g.font = `${px}px Anton`; g.shadowColor = 'rgba(28,28,28,0.9)'; g.shadowBlur = px * 0.12;
  let x = pad; parts.forEach((p, i) => { g.fillStyle = p.c; g.fillText(p.t, x, px * 1.05 + pad * 0.2); x += ws[i]; });
  return {canvas: c, w: c.width, h: c.height};
}

export function starTex(px = 600): Tex {
  const c = mk(px, px); const g = c.getContext('2d')!; const R = px * 0.48, r = R * 0.45;
  g.translate(px / 2, px / 2); g.beginPath();
  for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + (i * Math.PI) / 5; const rr = i % 2 ? r : R; g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); }
  g.closePath(); g.fillStyle = C.yellow; g.fill();
  // retícula leve
  g.globalCompositeOperation = 'destination-out';
  for (let y = -px / 2; y < px / 2; y += 14) for (let x = -px / 2; x < px / 2; x += 14) {
    const d = Math.hypot(x, y) / R; g.beginPath(); g.arc(x + ((y / 14) % 2 ? 7 : 0), y, Math.max(0, d - 0.55) * 7, 0, 7); g.fill();
  }
  return {canvas: c, w: px, h: px};
}

export function dashTex(): Tex {
  const c = mk(512, 24); const g = c.getContext('2d')!;
  g.strokeStyle = C.light; g.lineWidth = 12; g.setLineDash([30, 20]); g.lineCap = 'round';
  g.beginPath(); g.moveTo(8, 12); g.lineTo(504, 12); g.stroke();
  return {canvas: c, w: 512, h: 24};
}

const SPINE_WORDS = ['TERROR', 'SUSPENSE', 'FITA 042', 'DUBLADO', 'LEGENDADO', 'CLÁSSICO', 'TERROR', '1987', 'VHS', 'A NOITE', 'O PORÃO', 'ESPELHO', 'NÉVOA', 'A CASA', 'TERROR', 'FITA 13', 'O POÇO', 'SOMBRAS'];
// Prateleira cheia de lombadas de VHS (tile horizontal = 1 módulo)
export function shelfTex(seed: number, W = 1024, H = 1280, rows = 5): Tex {
  const c = mk(W, H); const g = c.getContext('2d')!; const r = rng(seed);
  g.fillStyle = '#141414'; g.fillRect(0, 0, W, H);
  const rowH = H / rows;
  for (let row = 0; row < rows; row++) {
    const y0 = row * rowH; const boardH = rowH * 0.07;
    let x = 4;
    while (x < W - 10) {
      const w = 26 + r() * 22; const h = rowH * (0.7 + r() * 0.16);
      if (r() < 0.06) { x += w * (1 + r() * 2); continue; } // vão
      const shade = 26 + Math.floor(r() * 92);
      const tone = r() < 0.022 ? C.yellow : r() < 0.5 ? `rgb(${shade},${shade},${shade})` : `rgb(${shade * 0.55},${shade * 0.55},${shade * 0.55})`;
      const yb = y0 + rowH - boardH;
      g.fillStyle = tone; g.fillRect(x, yb - h, w - 3, h);
      g.fillStyle = 'rgba(237,237,237,0.10)'; g.fillRect(x, yb - h, 3, h);
      g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(x + w - 6, yb - h, 3, h);
      if (r() < 0.75) { // etiqueta branca da lombada
        g.fillStyle = r() < 0.5 ? '#b5b5b5' : '#8a8a8a'; const lh = h * (0.25 + r() * 0.3); g.fillRect(x + 4, yb - h + h * 0.12, w - 11, lh);
        g.save(); g.translate(x + w / 2 - 1, yb - h + h * 0.12 + lh - 6); g.rotate(-Math.PI / 2);
        g.fillStyle = C.char; g.font = `${Math.floor(w * 0.55)}px ${r() < 0.5 ? 'Anton' : '"Special Elite"'}`;
        g.fillText(SPINE_WORDS[Math.floor(r() * SPINE_WORDS.length)], 0, 0); g.restore();
      }
      if (r() < 0.04) { g.fillStyle = C.yellow; g.beginPath(); g.arc(x + w / 2, yb - h * 0.12, w * 0.3, 0, 7); g.fill(); }
      x += w;
    }
    // tábua
    g.fillStyle = '#5a5a5a'; g.fillRect(0, y0 + rowH - boardH, W, boardH);
    g.fillStyle = '#8a8a8a'; g.fillRect(0, y0 + rowH - boardH, W, boardH * 0.25);
  }
  // grão
  for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '0,0,0' : '237,237,237'},${r() * 0.06})`; g.fillRect(r() * W, r() * H, 2, 2); }
  return {canvas: c, w: W, h: H};
}

export function floorTex(): Tex {
  const S = 512; const c = mk(S, S); const g = c.getContext('2d')!; const r = rng(3);
  const t = S / 4;
  for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { g.fillStyle = (i + j) % 2 ? '#222222' : '#191919'; g.fillRect(i * t, j * t, t, t); }
  for (let k = 0; k < 6000; k++) { g.fillStyle = `rgba(${r() < 0.5 ? '0,0,0' : '237,237,237'},${r() * 0.07})`; g.fillRect(r() * S, r() * S, 2, 2); }
  g.strokeStyle = 'rgba(0,0,0,0.5)'; g.lineWidth = 2;
  for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * t, 0); g.lineTo(i * t, S); g.stroke(); g.beginPath(); g.moveTo(0, i * t); g.lineTo(S, i * t); g.stroke(); }
  return {canvas: c, w: S, h: S};
}

export function cloudTex(seed: number): Tex {
  const S = 512; const c = mk(S, S / 2); const g = c.getContext('2d')!; const r = rng(seed);
  for (let i = 0; i < 70; i++) {
    const x = S * (0.1 + r() * 0.8), y = (S / 2) * (0.25 + r() * 0.5), rad = 30 + r() * 90;
    const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, 'rgba(237,237,237,0.22)'); gr.addColorStop(1, 'rgba(237,237,237,0)');
    g.fillStyle = gr; g.fillRect(0, 0, S, S / 2);
  }
  return {canvas: c, w: S, h: S / 2};
}

export function glowTex(color = '237,237,237'): Tex {
  const S = 256; const c = mk(S, S); const g = c.getContext('2d')!;
  const gr = g.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S / 2); gr.addColorStop(0, `rgba(${color},0.9)`); gr.addColorStop(0.25, `rgba(${color},0.35)`); gr.addColorStop(1, `rgba(${color},0)`);
  g.fillStyle = gr; g.fillRect(0, 0, S, S); return {canvas: c, w: S, h: S};
}

export function stripTex(): Tex {
  const c = mk(64, 512); const g = c.getContext('2d')!; const r = rng(21);
  g.fillStyle = 'rgba(237,237,237,0.55)'; g.fillRect(0, 0, 64, 512);
  for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(237,237,237,${r() * 0.4})`; g.fillRect(r() * 64, 0, 1 + r() * 3, 512); }
  g.fillStyle = 'rgba(237,237,237,0.9)'; g.fillRect(0, 0, 3, 512); g.fillRect(61, 0, 3, 512);
  return {canvas: c, w: 64, h: 512};
}

export function signTex(text: string, yellow: boolean): Tex {
  const W = 900, H = 260; const c = mk(W, H); const g = c.getContext('2d')!;
  g.fillStyle = yellow ? C.yellow : C.light; g.fillRect(0, 0, W, H);
  g.strokeStyle = C.char; g.lineWidth = 12; g.strokeRect(14, 14, W - 28, H - 28);
  g.fillStyle = C.char; g.font = '170px Anton'; g.textAlign = 'center'; g.fillText(text, W / 2, 200);
  return {canvas: c, w: W, h: H};
}

// Neon (ícone, sem texto): seta de "PLAY" e estrela, em tubo
export function neonTex(kind: 'play' | 'star', lit: boolean): Tex {
  const S = 512; const c = mk(S, S); const g = c.getContext('2d')!;
  g.lineJoin = 'round'; g.lineCap = 'round';
  const path = () => {
    g.beginPath();
    if (kind === 'play') { g.moveTo(150, 110); g.lineTo(400, 256); g.lineTo(150, 402); g.closePath(); }
    else { for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + (i * Math.PI) / 5; const rr = i % 2 ? 90 : 200; g.lineTo(256 + Math.cos(a) * rr, 266 + Math.sin(a) * rr); } g.closePath(); }
  };
  if (lit) { g.shadowColor = C.yellow; g.shadowBlur = 40; g.strokeStyle = C.yellow; g.lineWidth = 22; path(); g.stroke(); g.shadowBlur = 0; g.strokeStyle = '#fbf6c0'; g.lineWidth = 8; path(); g.stroke(); }
  else { g.strokeStyle = '#4a4a4a'; g.lineWidth = 18; path(); g.stroke(); g.strokeStyle = '#6a6a6a'; g.lineWidth = 5; path(); g.stroke(); }
  return {canvas: c, w: S, h: S};
}
