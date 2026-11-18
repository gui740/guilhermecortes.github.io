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
      concurrency: Number(process.env.CONC || 4), imageFormat: "jpeg", jpegQuality: 92, onProgress: progresso(id), timeoutInMilliseconds: 120000 });
    log(`${id} ok`);
  }
}

// node render.mjs v3a [animatic] [short01] [short02] -> out/v3a/EP01_v3a_animatic_0-3min_raw.mp4, SHORT01_v3a_raw.mp4, SHORT02_v3a_raw.mp4 (540p)
if (modo === "v3a") {
  fs.mkdirSync("out/v3a", { recursive: true });
  const alvos = ids.length ? ids : ["animatic", "short01", "short02"];
  const job = { animatic: ["EpisodioV3", "EP01_v3a_animatic_0-3min_raw.mp4", [0, 180 * 30 - 1]], short01: ["SHORT01-v3a", "SHORT01_v3a_raw.mp4", null],
    short02: ["SHORT02-v3a", "SHORT02_v3a_raw.mp4", null] };
  for (const a of alvos) {
    const [id, arq, fr] = job[a];
    const c = await comp(id);
    ultimo = -1;
    await renderMedia({ composition: c, serveUrl, codec: "h264", crf: 20, scale: 0.5, frameRange: fr ?? undefined, outputLocation: `out/v3a/${arq}`,
      browserExecutable: BROWSER, concurrency: Number(process.env.CONC || 3), imageFormat: "jpeg", jpegQuality: 90, onProgress: progresso(a), timeoutInMilliseconds: 120000 });
    log(`${a} ok`);
  }
}

// node render.mjs partes <escala> <prefixo> -> EpisodioV3 em partes de ~200 s (pula as já prontas); depois junte com concat
if (modo === "partes") {
  const escala = Number(ids[0] || 0.5), pref = ids[1] || "ep540";
  fs.mkdirSync("out/v3a/partes", { recursive: true });
  const props = process.env.SEM_PULSO ? { semPulso: true } : {};
  const c = await comp("EpisodioV3", props);
  const N = c.durationInFrames, passo = 6000;
  for (let i = 0, k = 1; i < N; i += passo, k++) {
    const out = `out/v3a/partes/${pref}_${String(k).padStart(2, "0")}.mp4`;
    if (fs.existsSync(out)) { log(`${out} já existe`); continue; }
    ultimo = -1;
    await renderMedia({ composition: c, serveUrl, inputProps: props, codec: "h264", crf: escala < 1 ? 20 : 17, scale: escala, frameRange: [i, Math.min(N, i + passo) - 1],
      outputLocation: out + ".tmp.mp4", browserExecutable: BROWSER, concurrency: Number(process.env.CONC || 3), imageFormat: "jpeg", jpegQuality: 90,
      onProgress: progresso(`parte ${k}`), timeoutInMilliseconds: 120000, offthreadVideoCacheSizeInBytes: 2 * 1024 ** 3 });
    fs.renameSync(out + ".tmp.mp4", out);
    log(`parte ${k} ok`);
  }
}
