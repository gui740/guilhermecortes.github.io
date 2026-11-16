// Trajetória da câmera (plano-sequência) e utilidades de tempo. JS puro: usado pelo Remotion e pelo script de áudio.
export const FPS = 30, FOV = 50, ASPECT = 9 / 16, D = 24, H0 = 6.2, H1 = 5.0, HM = H1;   // layout dimensionado no ponto mais próximo
export const TANH = Math.tan((FOV / 2) * Math.PI / 180);
export const LEAD = 0.03, TRAVEL_BEFORE = 0.06, TRAVEL_AFTER = 0.92;
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const smooth = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
export const eOut = (p) => 1 - Math.pow(1 - clamp(p), 3);
export const eIn = (p) => Math.pow(clamp(p), 3);
export const eIO = (p) => { p = clamp(p); return p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; };
export const eBack = (p) => { p = clamp(p); const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };

/** "s1:3" início da palavra 3 · "s1:3e" fim · "s1" início da frase · "s1$" fim · "+0.2" offset · número = segundos */
export function makeT(TL) {
  const by = {}; TL.frases.forEach((f) => (by[f.id] = f));
  return (ref) => {
    if (typeof ref === 'number') return ref;
    const m = String(ref).trim().match(/^([a-z0-9]+?)(?::(\d+)(e)?|(\$))?([+-][\d.]+)?$/i);
    if (!m) throw new Error('ref inválida: ' + ref);
    if (/^-?[\d.]+$/.test(ref)) return +ref;
    const f = by[m[1]]; if (!f) throw new Error('frase desconhecida: ' + ref);
    let b;
    if (m[2] != null) { const w = f.palavras[+m[2]]; if (!w) throw new Error('palavra inexistente: ' + ref); b = m[3] ? w.e : w.t; }
    else b = m[4] ? f.t1 : f.palavras[0].t;
    return b + (m[5] ? +m[5] : 0);
  };
}

/** starts: instante de início de cada parada (s). total: duração do vídeo. Retorna cam(t). */
export function buildCamera(starts, total, opts = {}) {
  const n = starts.length, Z = (k) => -k * D;
  const arrive = starts.map((b, k) => (k === 0 ? 0 : b + TRAVEL_AFTER));
  const depart = starts.map((b, k) => (k === n - 1 ? total + 0.5 : starts[k + 1] - TRAVEL_BEFORE));
  const vel = arrive.map((a, k) => (H0 - H1) / Math.max(0.4, depart[k] - a));       // velocidade (u/s) no trecho lento
  function z(t) {
    for (let k = 0; k < n; k++) {
      if (t <= depart[k] || k === n - 1) {
        if (t >= arrive[k] || k === 0) {               // trecho lento: push-in
          const u = (t - arrive[k]) * vel[k];
          return Z(k) + H0 - u;
        }
        // travessia k-1 -> k (Hermite com velocidades contínuas)
        const T0 = depart[k - 1], T1 = arrive[k], T = T1 - T0, s = clamp((t - T0) / T);
        const p0 = Z(k - 1) + H0 - (depart[k - 1] - arrive[k - 1]) * vel[k - 1], p1 = Z(k) + H0;
        const m0 = -vel[k - 1] * T, m1 = -vel[k] * T;
        const s2 = s * s, s3 = s2 * s;
        return (2 * s3 - 3 * s2 + 1) * p0 + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * p1 + (s3 - s2) * m1;
      }
    }
    return Z(n - 1);
  }
  function stopAt(t) { let k = 0; for (let i = 0; i < n; i++) if (t >= starts[i] - TRAVEL_BEFORE * 0.5) k = i; return k; }
  function holdW(t) {  // 1 parado na estação, 0 em travessia
    let w = 0;
    for (let k = 0; k < n; k++) {
      const a = arrive[k], d = depart[k];
      if (t >= a - 0.2 && t <= d + 0.2) w = Math.max(w, smooth((t - a + 0.2) / 0.55) * smooth((d + 0.2 - t) / 0.55));
    }
    return w;
  }
  const k0 = (t) => stopAt(t);
  const recoil = (t) => (opts.noOpening ? 0 : 2.2 * (1 - eOut(t / 0.55)));       // abertura: câmera recua rápido
  return function cam(t) {
    const k = stopAt(t), zz = z(t) - recoil(t), w = holdW(t);
    const a = arrive[k], d = depart[k], u = clamp((t - a) / Math.max(0.3, d - a));
    const sgn = k % 2 ? -1 : 1, phi = ((-4 + 8 * u) * sgn * Math.PI) / 180 * w;      // órbita de 8°
    const zf = Z(k) - 0.4, dist = Math.max(0.5, zz - zf);
    const x = Math.sin(phi) * dist * 0.75, y = 0.06 * Math.sin(t * 0.9) + 0.12 * Math.sin(phi) * w;
    const look = [x * (1 - w), y * (1 - w), zz - 12];
    const lw = [0, 0, zf];
    const lx = look[0] * (1 - w) + lw[0] * w, ly = look[1] * (1 - w) + lw[1] * w, lz = Math.min(look[2] * (1 - w) + lw[2] * w, zz - 3);
    const dt = 1 / 120, sp = Math.abs(z(t + dt) - z(t - dt)) / (2 * dt);
    return { x, y, z: zz, lx, ly, lz, w, k, speed: sp };
  };
}
