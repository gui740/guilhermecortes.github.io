// Orquestra os renders com um único bundle.
// node render.mjs episodio            -> out/episodio_mudo.mp4 (16:9, sem áudio)
// node render.mjs capa                -> out/capa.png
// node render.mjs shorts [SHORT01...] -> out/shorts/<id>_parteN_raw.mp4 (1,5x) + out/shorts/<id>_hook.png
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const BROWSER = "/opt/pw-browsers/chromium";
const [modo, ...ids] = process.argv.slice(2);
const tl = JSON.parse(fs.readFileSync("src/timeline.json", "utf8"));
fs.mkdirSync("out/shorts", { recursive: true });

const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const comp = async (id, inputProps = {}) => selectComposition({ serveUrl, id, inputProps, browserExecutable: BROWSER });
const log = (msg) => process.stdout.write(msg + "\n");
let ultimo = -1;
const progresso = (rotulo) => ({ progress }) => {
  const p = Math.floor(progress * 100);
  if (p >= ultimo + 5) { ultimo = p; log(`${rotulo} ${p}%`); }
};

if (modo === "episodio") {
  const c = await comp("Episodio");
  await renderMedia({
    composition: c, serveUrl, codec: "h264", crf: 17, muted: true, outputLocation: "out/episodio_mudo.mp4",
    browserExecutable: BROWSER, concurrency: 4, imageFormat: "jpeg", jpegQuality: 92, onProgress: progresso("episodio"),
    offthreadVideoCacheSizeInBytes: 2 * 1024 ** 3, timeoutInMilliseconds: 120000,
  });
  log("episodio ok");
}

if (modo === "capa") {
  await renderStill({ composition: await comp("Capa"), serveUrl, frame: 0, output: "out/capa.png", browserExecutable: BROWSER });
  log("capa ok");
}

if (modo === "shorts") {
  const c = await comp("Episodio");
  const fps = tl.fps;
  for (const s of tl.shorts) {
    if (ids.length && !ids.includes(s.id)) continue;
    const hook = await comp("HookShort", { texto: s.hook, num: s.id.replace("SHORT", "SHORT ") });
    await renderStill({ composition: hook, serveUrl, frame: 0, output: `out/shorts/${s.id}_hook.png`, imageFormat: "png",
      inputProps: { texto: s.hook, num: s.id.replace("SHORT", "SHORT ") }, browserExecutable: BROWSER });
    for (let i = 0; i < s.trechos.length; i++) {
      const [a, b] = s.trechos[i];
      const fr = [Math.round(a * fps), Math.min(c.durationInFrames - 1, Math.round(b * fps) - 1)];
      ultimo = -1;
      await renderMedia({
        composition: c, serveUrl, codec: "h264", crf: 16, muted: true, scale: 1.5, frameRange: fr,
        outputLocation: `out/shorts/${s.id}_parte${i}_raw.mp4`, browserExecutable: BROWSER, concurrency: 4,
        imageFormat: "jpeg", jpegQuality: 94, onProgress: progresso(`${s.id}/${i}`), timeoutInMilliseconds: 120000,
      });
    }
    log(`${s.id} ok`);
  }
}

// node render.mjs faixas a-b c-d ... -> out/fix_<a>_<b>.mp4 (trechos do episódio, 1920x1080, para emenda)
if (modo === "faixas") {
  const c = await comp("Episodio");
  for (const r of ids) {
    const [a, b] = r.split("-").map(Number);
    ultimo = -1;
    await renderMedia({ composition: c, serveUrl, codec: "h264", crf: 17, muted: true, frameRange: [a, b], outputLocation: `out/fix_${a}_${b}.mp4`,
      browserExecutable: BROWSER, concurrency: 4, imageFormat: "jpeg", jpegQuality: 92, onProgress: progresso(`faixa ${r}`), timeoutInMilliseconds: 120000 });
    log(`faixa ${r} ok`);
  }
}

// node render.mjs amostra [ID...] -> out/v3a/<ID>.mp4 (cenas da amostra v3, com áudio)
if (modo === "amostra") {
  fs.mkdirSync("out/v3a", { recursive: true });
  const lista = ids.length ? ids : ["V3ColdOpen", "V3Colagem", "V3FalaT04", "V3TransicaoCap", "V3Short02Hook"];
  for (const id of lista) {
    const c = await comp(id);
    ultimo = -1;
    await renderMedia({ composition: c, serveUrl, codec: "h264", crf: 18, outputLocation: `out/v3a/${id}.mp4`, browserExecutable: BROWSER,
      concurrency: 4, imageFormat: "jpeg", jpegQuality: 92, onProgress: progresso(id), timeoutInMilliseconds: 120000 });
    log(`${id} ok`);
  }
}
