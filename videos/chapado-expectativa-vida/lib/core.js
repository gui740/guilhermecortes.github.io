// Núcleo: easing orgânico, aleatório determinístico, stop-motion e helpers de SVG.
// Tudo é função do tempo t (segundos) -> qualquer frame pode ser renderizado em qualquer ordem.
const NS = "http://www.w3.org/2000/svg";

const K = {
  clamp: (x, a = 0, b = 1) => Math.max(a, Math.min(b, x)),
  lerp: (a, b, t) => a + (b - a) * t,
  ease: {
    out: (x) => 1 - Math.pow(1 - x, 3),
    in: (x) => x * x * x,
    inOut: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    smooth: (x) => x * x * x * (x * (x * 6 - 15) + 10),
    outBack: (x, k = 1.7) => 1 + (k + 1) * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2),
    outElastic: (x) => (x <= 0 ? 0 : x >= 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * (2 * Math.PI) / 3) + 1),
  },
  // número pseudo-aleatório estável a partir de uma semente
  hash(n) {
    const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
    return x - Math.floor(x);
  },
  rng(seed) {
    let s = (seed * 9301 + 49297) % 233280 || 1;
    return () => {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
  },
  // tempo "quantizado" a 12 fps: dá o tremido de stop-motion
  step12: (t) => Math.floor(t * 12 + 1e-6) / 12,
  // tremida que muda a cada quadro de 12 fps
  boil(t, id, amp) {
    const f = Math.floor(t * 12 + 1e-6);
    return (K.hash(id * 13.37 + f * 7.11) - 0.5) * 2 * amp;
  },
  // escala de entrada estilo papel posto na mesa: 0 -> 1.1 -> 1 (em 12 fps)
  pop(t, t0, dur = 0.42) {
    const u = (K.step12(t) - t0) / dur;
    if (u <= 0) return 0;
    if (u >= 1) return 1;
    if (u < 0.55) return 1.12 * K.ease.out(u / 0.55);
    return 1.12 - 0.12 * K.ease.inOut((u - 0.55) / 0.45);
  },
  // balanço ("respirar") com período e fase
  sway: (t, period, amp, phase = 0) => amp * Math.sin((2 * Math.PI * t) / period + phase),
  // svg
  el(tag, attrs = {}, parent = null) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  },
  g(markup, parent) {
    const e = K.el("g", {}, parent);
    if (markup) e.innerHTML = markup;
    return e;
  },
  fmt(v, dec = 0) {
    return v.toFixed(dec).replace(".", ",");
  },
  // instante (relógio da cena) em que a narração diz uma palavra; fallback se não houver narração
  quando(cfg, frag, fallback, nth = 0) {
    const ws = (cfg.palavras || []).filter((w) => w[0].startsWith(frag));
    return ws.length > nth ? ws[nth][1] : fallback;
  },
};
