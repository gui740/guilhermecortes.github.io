// node stills.mjs <saida_dir> <s1> <s2> ... -> PNGs de EpisodioV3 em escala 0,5 (conferência visual)
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path"; import fs from "node:fs";
const BROWSER = "/opt/pw-browsers/chromium";
const [out, ...ts] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const c = await selectComposition({ serveUrl, id: "EpisodioV3", browserExecutable: BROWSER });
for (const t of ts) {
  await renderStill({ composition: c, serveUrl, frame: Math.round(Number(t) * 30), output: path.join(out, `s_${String(t).padStart(7, "0")}.png`), scale: 0.5, browserExecutable: BROWSER });
}
console.log("ok");
