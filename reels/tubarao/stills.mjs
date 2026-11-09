// Uso: node stills.mjs <outdir> frame1 frame2 ...  (gera PNGs de checagem)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
const [out, ...frames] = process.argv.slice(2);
const browserExecutable = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id: 'Reel', browserExecutable});
for (const fr of frames) {
  await renderStill({composition, serveUrl, frame: Number(fr), output: `${out}/f${fr}.png`, browserExecutable, scale: 0.5});
  console.log('ok', fr);
}
