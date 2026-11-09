import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CENAS} from '../config/cenas';
import {FPS, ORDEM} from '../config/timing';
import {COR, F} from './fonts';
import {prog} from './util';

/** Palavras-chave que aparecem em vermelho. */
const CHAVE = new Set([
  'tres', 'terror', 'motivo', 'possum', 'mala', 'boneco', 'aranha', 'gente', 'volta', 'pior', 'sujo',
  'calvaire', 'educado', 'demais', 'vila', 'danca', 'esqueceu', 'hagazussa', 'bruxa', 'alpes', 'quinze',
  'enlouquecer', 'sozinha', 'sozinho', 'cabras', 'amigo', 'tudo',
]);
const limpa = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');

type Bloco = {de: number; ate: number; palavras: string[]};
const MAX = 4;

const montar = (): Bloco[] => {
  const blocos: Bloco[] = [];
  for (const id of ORDEM) {
    const c = CENAS[id];
    const base = c.inicio + c.narr0;
    let atual: {s: number; e: number; w: string}[] = [];
    const fecha = () => {
      if (!atual.length) return;
      blocos.push({de: base + Math.round(atual[0].s * FPS), ate: base + Math.round(atual[atual.length - 1].e * FPS) + 8, palavras: atual.map((a) => a.w)});
      atual = [];
    };
    c.palavras.forEach((p) => {
      atual.push(p);
      if (atual.length >= MAX || /[.,?!…:;]$/.test(p.w)) fecha();
    });
    fecha();
  }
  // um bloco fica até o próximo começar (se estiverem perto)
  for (let i = 0; i < blocos.length - 1; i++) {
    const prox = blocos[i + 1].de;
    if (prox - blocos[i].ate < 12) blocos[i].ate = prox;
    blocos[i].ate = Math.min(blocos[i].ate, prox);
  }
  return blocos;
};
const BLOCOS = montar();

/** Legendas sincronizadas: máx. 4 palavras, branco com contorno preto, palavra-chave em vermelho.
 *  Centralizadas no terço inferior, acima da área de UI do Reels (400px de baixo). */
export const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const b = BLOCOS.find((x) => f >= x.de && f < x.ate);
  if (!b) return null;
  const pop = prog(f, b.de, b.de + 4);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', zIndex: 900}}>
      <div style={{position: 'absolute', left: 60, right: 60, top: 1405, transform: `translate(0,-50%) scale(${0.86 + 0.14 * pop})`, opacity: Math.min(1, pop * 2), textAlign: 'center'}}>
        {b.palavras.map((w, i) => {
          const chave = CHAVE.has(limpa(w));
          const txt = w.replace(/[.,;:…]+$/, '');
          return (
            <span key={i} style={{fontFamily: F.legenda, fontWeight: 900, fontSize: 70, lineHeight: 1.15, color: chave ? COR.vermelhoVivo : '#fff', WebkitTextStroke: '12px #000', paintOrder: 'stroke fill', textShadow: '0 6px 14px rgba(0,0,0,0.8)', margin: '0 10px', display: 'inline-block'}}>
              {txt}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
