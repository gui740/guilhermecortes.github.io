// renderiza vários frames (uma só bundle/browser) -> out/<dir>/f####.jpg
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition, openBrowser} from '@remotion/renderer';
import path from 'path';
const [,, comp='Reel', dir='out/test', framesArg='0', scaleArg='0.5'] = process.argv;
const frames = framesArg.split(',').map(Number);
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const browser = await openBrowser('chrome', {browserExecutable: '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell', chromiumOptions: {gl: 'swangle'}});
const composition = await selectComposition({serveUrl, id: comp, puppeteerInstance: browser, chromiumOptions: {gl: 'swangle'}});
for (const f of frames) {
  const t0 = Date.now();
  await renderStill({composition, serveUrl, frame: f, output: `${dir}/f${String(f).padStart(4,'0')}.jpg`, imageFormat: 'jpeg', jpegQuality: 88, scale: Number(scaleArg), puppeteerInstance: browser, chromiumOptions: {gl: 'swangle'}});
  console.log('frame', f, Date.now()-t0, 'ms');
}
await browser.close({silent: true});
