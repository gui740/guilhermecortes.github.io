// Renderiza frames avulsos com um único bundle: node scripts/stills.mjs <comp> <outdir> <scale> f1 f2 ...
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
const [comp, outdir, scale, ...frames] = process.argv.slice(2);
fs.mkdirSync(outdir, {recursive: true});
const exe = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id: comp, browserExecutable: exe});
for (const f of frames) {
  await renderStill({serveUrl, composition, frame: Number(f), output: `${outdir}/f${String(f).padStart(4, '0')}.png`, browserExecutable: exe, scale: Number(scale)});
}
console.log('ok', frames.length);
