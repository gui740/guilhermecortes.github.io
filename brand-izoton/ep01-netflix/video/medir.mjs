// node medir.mjs <de_s> <ate_s> [semPulso] -> out/v3a/medida.mp4 (escala 0,25, só para medir movimento)
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";
const BROWSER = "/opt/pw-browsers/chromium";
const [de, ate, sp] = process.argv.slice(2);
const props = sp ? { semPulso: true } : {};
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const c = await selectComposition({ serveUrl, id: "EpisodioV3", inputProps: props, browserExecutable: BROWSER });
await renderMedia({ composition: c, serveUrl, inputProps: props, codec: "h264", crf: 24, scale: 0.25, muted: true, frameRange: [Math.round(de * 30), Math.round(ate * 30) - 1],
  outputLocation: "out/v3a/medida.mp4", browserExecutable: BROWSER, concurrency: 4, imageFormat: "jpeg", jpegQuality: 80, timeoutInMilliseconds: 120000 });
console.log("ok");
