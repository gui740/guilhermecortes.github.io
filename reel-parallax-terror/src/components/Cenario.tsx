import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {rnd} from './util';
import {F} from './fonts';
import {staticFile} from 'remotion';

/** Faixa de névoa que desliza devagar (barata de renderizar: só gradientes). */
export const Nevoa: React.FC<{y: number; h?: number; op?: number; vel?: number; cor?: string}> = ({y, h = 380, op = 0.35, vel = 0.4, cor = '215,220,225'}) => {
  const f = useCurrentFrame();
  const dx = ((f * vel) % 1600) - 800;
  const faixa = (off: number) => (
    <div style={{position: 'absolute', left: -1200 + dx + off, top: y - h / 2, width: 2600, height: h,
      background: `radial-gradient(ellipse 30% 50% at 25% 50%, rgba(${cor},${op}) 0%, rgba(${cor},0) 70%), radial-gradient(ellipse 35% 45% at 70% 55%, rgba(${cor},${op * 0.8}) 0%, rgba(${cor},0) 70%), linear-gradient(180deg, rgba(${cor},0) 0%, rgba(${cor},${op * 0.55}) 50%, rgba(${cor},0) 100%)`}} />
  );
  return <AbsoluteFill style={{pointerEvents: 'none'}}>{faixa(0)}{faixa(1600)}</AbsoluteFill>;
};

/** Cordilheira procedural (silhueta) para o parallax dos Alpes. */
export const Montanhas: React.FC<{base: number; altura: number; cor: string; neve?: string; seed: string; picos?: number}> = ({base, altura, cor, neve, seed, picos = 5}) => {
  const W = 1700, x0 = -310;
  const pts: [number, number][] = [];
  const n = 90;
  const fases = [rnd(seed + 'a', 0, 6), rnd(seed + 'b', 0, 6), rnd(seed + 'c', 0, 6)];
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const h = 0.55 * Math.abs(Math.sin(t * Math.PI * picos * 0.5 + fases[0])) + 0.28 * Math.sin(t * Math.PI * picos * 1.7 + fases[1]) + 0.12 * Math.sin(t * Math.PI * picos * 4.3 + fases[2]) + rnd(seed + i, -0.03, 0.03);
    pts.push([x0 + t * W, base - altura * (0.35 + 0.65 * Math.max(0, h))]);
  }
  const d = `M ${x0} 2400 L ${pts.map((p) => `${p[0].toFixed(0)} ${p[1].toFixed(0)}`).join(' L ')} L ${x0 + W} 2400 Z`;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
      <defs>
        <linearGradient id={`m${seed}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={neve ?? cor} />
          <stop offset="18%" stopColor={cor} />
          <stop offset="100%" stopColor="#07090b" />
        </linearGradient>
      </defs>
      <path d={d} fill={`url(#m${seed})`} transform={`translate(0 ${-0})`} style={{}} />
    </svg>
  );
};

/** Silhuetas de pinheiros nas bordas (camada próxima da floresta). */
export const Pinheiros: React.FC<{seed: string; cor?: string; escala?: number; lado?: 'ambos' | 'esq' | 'dir'; base?: number}> = ({seed, cor = '#050605', escala = 1, lado = 'ambos', base = 2000}) => {
  const arvores: React.ReactNode[] = [];
  const xs = lado === 'esq' ? [-80, 60, 150] : lado === 'dir' ? [930, 1030, 1150] : [-90, 70, 990, 1130];
  xs.forEach((x, i) => {
    const h = (1200 + rnd(seed + i, -200, 300)) * escala;
    const w = h * 0.32;
    const camadas = 9;
    let d = `M ${x - 10} ${base} L ${x - 10} ${base - h * 0.15} `;
    for (let c = 0; c < camadas; c++) {
      const yy = base - h * 0.12 - (h * 0.88 * c) / camadas;
      const ww = (w * (camadas - c)) / camadas;
      d += `M ${x - ww / 2} ${yy} L ${x} ${yy - h * 0.2} L ${x + ww / 2} ${yy} Z `;
    }
    arvores.push(<path key={i} d={d} fill={cor} stroke={cor} strokeWidth={14} />);
  });
  return <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>{arvores}</svg>;
};

/** Recorte de jornal velho (texto falso em barras + manchete). */
export const Jornal: React.FC<{x: number; y: number; w: number; h: number; rot: number; manchete: string; op?: number}> = ({x, y, w, h, rot, manchete, op = 0.55}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, transform: `translate(-50%,-50%) rotate(${rot}deg)`, background: `url(${staticFile('textura/papel.jpg')}) center/cover`, opacity: op, padding: 16, boxSizing: 'border-box', boxShadow: '4px 8px 10px rgba(0,0,0,0.5)', overflow: 'hidden'}}>
    <div style={{fontFamily: F.titulo, fontSize: w * 0.12, color: '#1c1610', lineHeight: 1, marginBottom: 10}}>{manchete}</div>
    {Array.from({length: Math.floor((h - w * 0.12 - 30) / 16)}, (_, i) => (
      <div key={i} style={{height: 7, marginBottom: 9, background: 'rgba(30,24,18,0.45)', width: `${70 + ((i * 37) % 30)}%`}} />
    ))}
  </div>
);

/** Verso de polaroide (papel), para as polaroides "viradas pra baixo". */
export const VersoPolaroide: React.FC<{w: number; marca?: string}> = ({w, marca}) => (
  <div style={{width: w, height: w * 1.2, background: `linear-gradient(135deg, rgba(217,205,176,0.35), rgba(170,145,100,0.45)), url(${staticFile('textura/papel.jpg')}) center/cover`, position: 'relative', boxShadow: 'inset 0 0 30px rgba(80,50,20,0.35)'}}>
    <div style={{position: 'absolute', inset: 14, border: '2px dashed rgba(90,60,30,0.25)'}} />
    {marca ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.marker, fontSize: w * 0.42, color: 'rgba(139,0,0,0.85)', transform: 'rotate(-8deg)'}}>{marca}</div> : null}
  </div>
);
