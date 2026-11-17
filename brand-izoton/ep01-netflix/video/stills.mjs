// Renderiza quadros isolados com um único bundle: node stills.mjs <saida_dir> <frame> [frame...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [out, ...frames] = process.argv.slice(2);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const comp = await selectComposition({ serveUrl, id: process.env.COMP || "Episodio", browserExecutable: "/opt/pw-browsers/chromium" });
for (const f of frames) {
  try { await renderStill({ composition: comp, serveUrl, frame: Number(f), output: `${out}/f${String(f).padStart(6, "0")}.png`, browserExecutable: "/opt/pw-browsers/chromium", scale: 0.5 });
  console.log("ok", f); } catch (e) { console.log("ERRO", f, String(e.message).slice(0, 160)); }
}
