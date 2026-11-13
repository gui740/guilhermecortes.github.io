/* Renderiza quadros do Reel com o Chromium (Playwright).
 *   node tools/render.js stills            → out/frames/cena_XX_<id>.png (um quadro por cena, para aprovação)
 *   node tools/render.js stills 12.3 30.1  → quadros nos tempos indicados
 *   node tools/render.js video             → out/teodora_mudo.mp4 (1080x1920, 30 fps, H.264)
 *   node tools/render.js video --audio out/audio_mix.wav → out/teodora_reel.mp4
 */
const { chromium } = require("playwright");
const http = require("http"), fs = require("fs"), path = require("path"), { spawn } = require("child_process");
const ROOT = path.resolve(__dirname, "..");
const MIME = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg", ".ttf": "font/ttf", ".wav": "audio/wav" };
function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split("?")[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { "Content-Type": MIME[path.extname(p)] || "application/octet-stream" }); fs.createReadStream(p).pipe(rsp);
    }).listen(0, "127.0.0.1", () => res(srv));
  });
}
(async () => {
  const mode = process.argv[2] || "stills";
  const srv = await serve(); const port = srv.address().port;
  const browser = await chromium.launch({ args: ["--disable-web-security"] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("console", m => { if (m.type() === "error" || m.type() === "warning") console.log("[page]", m.text()); });
  await page.goto(`http://127.0.0.1:${port}/src/index.html?render`);
  await page.evaluate(() => window.READY);
  const T = JSON.parse(fs.readFileSync(path.join(ROOT, "src/timings.json"), "utf8"));
  const grab = async t => {
    const b64 = await page.evaluate(tt => { window.renderFrame(tt); return document.getElementById("c").toDataURL("image/png").split(",")[1]; }, t);
    return Buffer.from(b64, "base64");
  };
  fs.mkdirSync(path.join(ROOT, "out/frames"), { recursive: true });
  if (mode === "stills") {
    let times = process.argv.slice(3).map(Number);
    const jobs = times.length ? times.map(t => [t, `t_${t.toFixed(2)}`]) :
      T.lines.map((l, i) => [l.start + (l.end - l.start) * (l.scene === "prancha" ? .92 : l.scene === "fuga" ? .55 : .88), `cena_${String(i + 1).padStart(2, "0")}_${l.scene}`]);
    for (const [t, name] of jobs) { fs.writeFileSync(path.join(ROOT, "out/frames", name + ".png"), await grab(t)); console.log("ok", name, t.toFixed(2)); }
  } else if (mode === "video") {
    const ai = process.argv.indexOf("--audio"); const audio = ai > 0 ? process.argv[ai + 1] : null;
    const out = path.join(ROOT, audio ? "out/teodora_reel.mp4" : "out/teodora_mudo.mp4");
    const fps = T.fps, n = Math.round(T.duration * fps);
    const args = ["-y", "-f", "image2pipe", "-framerate", String(fps), "-i", "-"];
    if (audio) args.push("-i", path.resolve(ROOT, audio));
    args.push("-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", String(fps), "-movflags", "+faststart");
    if (audio) args.push("-c:a", "aac", "-b:a", "192k", "-shortest");
    args.push(out);
    const ff = spawn("ffmpeg", args, { stdio: ["pipe", "ignore", "inherit"] });
    const t0 = Date.now();
    for (let f = 0; f < n; f++) {
      const buf = await grab(f / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
      if (f % 30 === 0) process.stdout.write(`\r${f}/${n} quadros (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
    }
    ff.stdin.end(); await new Promise(r => ff.on("close", r));
    console.log("\n→", out);
  }
  await browser.close(); srv.close();
})();
