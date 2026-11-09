import React from 'react';
import {useCurrentFrame} from 'remotion';
import {caminhoMao, prog, Pt} from './util';
import {COR} from './fonts';

/** Seta desenhada à mão que se desenha na tela (stroke-dashoffset). Traço com tremor. */
export const HandArrow: React.FC<{de: Pt; ate: Pt; curva?: number; delay?: number; dur?: number; cor?: string; espessura?: number; seed?: string; cabeca?: boolean}> = ({
  de, ate, curva = 60, delay = 0, dur = 15, cor = COR.vermelho, espessura = 10, seed = 'seta', cabeca = true,
}) => {
  const f = useCurrentFrame();
  if (f < delay) return null;
  const p = prog(f, delay, delay + dur);
  const {pts, d} = caminhoMao(de, ate, curva, seed);
  const a = pts[pts.length - 1], b = pts[pts.length - 3];
  const ang = Math.atan2(a.y - b.y, a.x - b.x);
  const L = 44;
  const ponta = (da: number) => `M ${a.x} ${a.y} L ${a.x - L * Math.cos(ang + da)} ${a.y - L * Math.sin(ang + da)}`;
  const pc = prog(f, delay + dur * 0.85, delay + dur + 5);
  const common = {fill: 'none', stroke: cor, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const};
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', zIndex: 60}}>
      <g style={{filter: 'drop-shadow(2px 3px 2px rgba(0,0,0,0.5))'}}>
        <path d={d} {...common} strokeWidth={espessura} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} />
        <path d={d} {...common} strokeWidth={espessura * 0.35} stroke="rgba(255,120,120,0.35)" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} transform="translate(-1.5,-1.5)" />
        {cabeca && pc > 0 ? (
          <>
            <path d={ponta(0.5)} {...common} strokeWidth={espessura} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - pc} />
            <path d={ponta(-0.55)} {...common} strokeWidth={espessura} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - pc} />
          </>
        ) : null}
      </g>
    </svg>
  );
};
