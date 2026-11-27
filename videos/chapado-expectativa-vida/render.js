// Captura os frames do index.html com o Chromium (Playwright) e monta o MP4 com ffmpeg.
//
//   node render.js                               -> vídeo inteiro (out/video.mp4)
//   node render.js --cena cena1 --dur 10         -> só a cena 1, 10 s (out/preview_cena1.mp4)
//   node render.js --cena cena1 --frames 0,3.5,7 -> PNGs de frames-chave em out/frames/
//   --workers 4  (páginas em paralelo)   --inicio 2  (começa no segundo 2)
//
// O MP4 sai com uma faixa de áudio VAZIA (silêncio) para a narração entrar depois.
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, arr) => {
  if (a.startsWith("--")) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : true]);
  return acc;
}, []));
const OUT = path.join(__dirname, "out");
fs.mkdirSync(OUT, { recursive: true });

async function openPage(browser) {
  const page = await browser.newPage();
  const url = "file://" + path.join(__dirname, "index.html") + (args.cena ? `?cena=${args.cena}` : "");
  await page.goto(url);
  const info = await page.evaluate(() => window.setup());
  await page.setViewportSize({ width: info.w, height: info.h });
  return { page, info };
}

function ffmpegWriter(file, fps) {
  const p = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "png", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", file], { stdio: ["pipe", "inherit", "inherit"] });
  return p;
}

async function renderRange(browser, a, b, file, fps) {
  const { page } = await openPage(browser);
  const ff = ffmpegWriter(file, fps);
  for (let f = a; f < b; f++) {
    await page.evaluate((t) => window.renderFrame(t), f / fps);
    const buf = await page.screenshot({ type: "png" });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    if ((f - a) % 60 === 0) console.log(`  frame ${f}`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  await page.close();
}

(async () => {
  const browser = await chromium.launch();
  const { page, info } = await openPage(browser);
  const fps = info.fps;
  if (args.frames) {
    fs.mkdirSync(path.join(OUT, "frames"), { recursive: true });
    for (const ts of String(args.frames).split(",")) {
      await page.evaluate((t) => window.renderFrame(t), parseFloat(ts));
      await page.screenshot({ path: path.join(OUT, "frames", `${args.cena || "video"}_${ts}.png`) });
    }
    console.log("frames ok");
    await browser.close();
    return;
  }
  await page.close();
  const inicio = parseFloat(args.inicio || 0);
  const dur = parseFloat(args.dur || (info.total - inicio));
  const a = Math.round(inicio * fps), b = Math.round((inicio + dur) * fps);
  const workers = parseInt(args.workers || 4);
  const step = Math.ceil((b - a) / workers);
  const segs = [];
  const jobs = [];
  for (let k = 0; k < workers; k++) {
    const sa = a + k * step, sb = Math.min(b, sa + step);
    if (sa >= sb) break;
    const file = path.join(OUT, `seg_${k}.mp4`);
    segs.push(file);
    jobs.push(renderRange(browser, sa, sb, file, fps));
  }
  const t0 = Date.now();
  await Promise.all(jobs);
  await browser.close();
  fs.writeFileSync(path.join(OUT, "segs.txt"), segs.map((s) => `file '${s}'`).join("\n"));
  const name = args.out || (args.cena ? `preview_${args.cena}.mp4` : "video.mp4");
  // com out/audio.wav (narração + trilha, gerado por audio.py) ele entra no vídeo; sem ele, faixa de áudio vazia
  const audio = path.join(OUT, "audio.wav");
  const useAudio = !args.cena && !args.mudo && fs.existsSync(audio);
  const ain = useAudio ? ["-i", audio] : ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"];
  const af = useAudio ? ["-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000"] : [];
  await new Promise((r) => spawn("ffmpeg", ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", path.join(OUT, "segs.txt"),
    ...ain, "-map", "0:v", "-map", "1:a", "-c:v", "copy", ...af, "-c:a", "aac", "-b:a", "192k", "-shortest",
    "-movflags", "+faststart", path.join(OUT, name)], { stdio: "inherit" }).on("close", r));
  console.log(`pronto: out/${name}  (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
})();
