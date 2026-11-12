// Renderiza frames avulsos (bundle único): node src/stills.mjs Reel outdir t1 t2 ... (tempos em segundos)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'path'; import fs from 'fs';
const [comp, out, ...ts] = process.argv.slice(2);
fs.mkdirSync(out, {recursive: true});
const exe = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const serveUrl = process.env.BUNDLE || await bundle({entryPoint: path.resolve('src/remotion/index.tsx'), publicDir: path.resolve('public')});
const composition = await selectComposition({serveUrl, id: comp, browserExecutable: exe});
for (const t of ts) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(parseFloat(t) * 30));
  await renderStill({composition, serveUrl, frame, output: `${out}/${comp}_${String(frame).padStart(4, '0')}.png`, browserExecutable: exe, chromiumOptions: {gl: 'swiftshader'}});
  process.stdout.write(`${frame} `);
}
console.log('ok');
