// Frames de amostra para revisão.
//   node --experimental-strip-types scripts/frames.mjs                 -> 5 frames (1 por cena) em out/frames/
//   node --experimental-strip-types scripts/frames.mjs pasta 120 900   -> frames específicos (escala 0.5) em <pasta>
import {readFileSync, mkdirSync} from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {montarTiming, ORDEM} from '../src/config/timing.ts';

const narr = JSON.parse(readFileSync(new URL('../src/data/narracao.json', import.meta.url)));
const {cenas} = montarTiming(narr);
const [pasta, ...lista] = process.argv.slice(2);
let alvos;
if (pasta) {
  alvos = lista.map((f) => ({nome: `f${String(f).padStart(5, '0')}`, frame: +f, escala: 0.5}));
} else {
  // momento "cheio" de cada cena
  alvos = ORDEM.map((id, i) => {
    const c = cenas[id];
    return {nome: `${i}-${id}`, frame: c.inicio + Math.round(c.saida * (id === 'fechamento' ? 0.97 : 0.9)), escala: 1};
  });
}
const out = pasta || 'out/frames';
mkdirSync(out, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('assets'), onProgress: () => {}});
const composition = await selectComposition({serveUrl, id: 'Reel'});
for (const a of alvos) {
  await renderStill({serveUrl, composition, frame: a.frame, output: path.join(out, a.nome + '.png'), scale: a.escala});
  console.log('ok', a.nome, 'frame', a.frame);
}
