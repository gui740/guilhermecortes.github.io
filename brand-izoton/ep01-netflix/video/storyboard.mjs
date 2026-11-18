// node storyboard.mjs -> out/storyboard_v3a/NNN.jpg (um quadro por cena do EpisodioV3) + out/storyboard_v3a/lista.json
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
const BROWSER = "/opt/pw-browsers/chromium";
const tl = JSON.parse(fs.readFileSync("src/timeline_v3.json", "utf8"));
const OUT = process.env.TESTE ? "out/sb_teste" : "out/storyboard_v3a"; fs.mkdirSync(OUT, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "EpisodioV3", browserExecutable: BROWSER });
const lista = [];
for (const tr of tl.trechos) {
  const princ = tr.cenas.filter((c) => c.tipo !== "academico");
  princ.forEach((c, i) => {
    const t0 = c.t, t1 = i + 1 < princ.length ? princ[i + 1].t : tr.dur;
    const dt = Math.min(Math.max(0.6, (t1 - t0) * 0.55), t1 - t0 - 0.1);
    lista.push({ trecho: tr.id, tipo: tr.tipo, cena: c.tipo, nome: c.nome, t: +(tr.start + t0 + dt).toFixed(2), ini: +(tr.start + t0).toFixed(2), fim: +(tr.start + t1).toFixed(2) });
  });
}
// as cenas v3 longas ganham quadros extras (meio e fim)
const extra = [];
for (const tr of tl.trechos.filter((t) => t.tipo === "v3")) for (const k of [0.35, 0.7, 0.92]) extra.push({ trecho: tr.id, tipo: "v3", cena: "v3", t: +(tr.start + tr.dur * k).toFixed(2), ini: tr.start, fim: tr.start + tr.dur });
let todos = [...lista, ...extra].sort((a, b) => a.t - b.t);
if (process.env.TESTE) todos = process.env.TESTE.split(",").map((t) => ({ trecho: "teste", t: +t }));
let n = 0;
for (const q of todos) {
  q.arq = `${String(++n).padStart(3, "0")}.jpg`;
  await renderStill({ composition, serveUrl, frame: Math.round(q.t * 30), output: `${OUT}/${q.arq}`, imageFormat: "jpeg", jpegQuality: 82, browserExecutable: BROWSER });
  if (n % 20 === 0) console.log(n, "/", todos.length);
}
fs.writeFileSync(`${OUT}/lista.json`, JSON.stringify(todos, null, 1));
console.log("ok", todos.length);
