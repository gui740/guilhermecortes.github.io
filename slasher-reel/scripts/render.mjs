// render de vídeo (sem áudio; o áudio é mixado no ffmpeg)
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import path from 'path';
const [,, comp='Reel', out='out/reel_video.mp4', scale='1', conc='4', range=''] = process.argv;
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const chromiumOptions = {gl: 'swangle'};
const browserExecutable = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const composition = await selectComposition({serveUrl, id: comp, chromiumOptions, browserExecutable});
const frameRange = range ? range.split('-').map(Number) : null;
let last = 0;
await renderMedia({composition, serveUrl, codec: 'h264', outputLocation: out, scale: Number(scale), concurrency: Number(conc), chromiumOptions, browserExecutable,
  crf: 14, pixelFormat: 'yuv420p', muted: true, frameRange, timeoutInMilliseconds: 240000,
  onProgress: ({renderedFrames, encodedFrames}) => { if (renderedFrames - last >= 30) { last = renderedFrames; console.log(new Date().toISOString(), 'rendered', renderedFrames, 'encoded', encodedFrames); } }});
console.log('DONE', out);
