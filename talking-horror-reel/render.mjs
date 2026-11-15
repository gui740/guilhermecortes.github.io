// Uso: node render.mjs <comp> <saida> [--scale=0.5] [--frames=a-b] [--props='{"hook":"B"}'] [--still=frame] [--seq=dir (png)]
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, renderFrames, selectComposition} from '@remotion/renderer';
import path from 'path';
const [comp, out, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => a.replace(/^--/, '').split(/=(.*)/s).slice(0, 2)));
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public')});
const inputProps = opt.props ? JSON.parse(opt.props) : {};
const browserExecutable = process.env.CHROME_BIN || '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const chromiumOptions = {gl: 'swangle', enableMultiProcessOnLinux: true};
const composition = await selectComposition({serveUrl, id: comp, inputProps, browserExecutable, chromiumOptions});
const scale = opt.scale ? Number(opt.scale) : 1;
const common = {serveUrl, composition, inputProps, browserExecutable, chromiumOptions, scale, timeoutInMilliseconds: 180000};
if (opt.still !== undefined) {
  await renderStill({...common, output: out, frame: Number(opt.still)});
} else if (opt.list) {
  for (const f of opt.list.split(',')) await renderStill({...common, output: path.join(out, `f${String(f).padStart(4, '0')}.png`), frame: Number(f)});
} else {
  const frameRange = opt.frames ? opt.frames.split('-').map(Number) : null;
  let last = 0;
  await renderMedia({...common, codec: 'h264', outputLocation: out, frameRange, crf: opt.crf ? Number(opt.crf) : 14, pixelFormat: 'yuv420p', muted: true,
    concurrency: opt.concurrency ? Number(opt.concurrency) : 4,
    onProgress: ({renderedFrames, progress}) => { if (renderedFrames - last >= 60) { last = renderedFrames; console.log('frames', renderedFrames, (progress * 100).toFixed(0) + '%'); } }});
}
console.log('ok', out);
