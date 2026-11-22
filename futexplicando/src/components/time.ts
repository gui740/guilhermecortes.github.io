import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

/** Converte tempo absoluto (s) do vídeo em frame relativo à cena atual. */
export const useSceneClock = (sceneStart: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const abs = sceneStart + frame / fps;
  return {
    frame,
    fps,
    abs,
    /** frames desde o instante absoluto t */
    since: (t: number) => frame - (t - sceneStart) * fps,
    /** spring iniciando no instante absoluto t */
    sp: (t: number, cfg: { damping?: number; stiffness?: number; mass?: number } = {}, dur?: number) =>
      spring({ frame: frame - (t - sceneStart) * fps, fps, config: { damping: 14, stiffness: 160, mass: 0.8, ...cfg }, durationInFrames: dur }),
    /** progresso 0..1 entre instantes absolutos a e b */
    prog: (a: number, b: number, easing: (n: number) => number = Easing.bezier(0.16, 1, 0.3, 1)) =>
      interpolate(abs, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing }),
  };
};

export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));

/** Pseudo-aleatório determinístico */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};

/** Tremor de câmera que decai após o instante t (em frames relativos) */
export const shake = (framesSince: number, amp = 18, decay = 0.18) => {
  if (framesSince < 0) return { x: 0, y: 0 };
  const k = Math.exp(-framesSince * decay);
  return { x: Math.sin(framesSince * 2.7) * amp * k, y: Math.cos(framesSince * 3.3) * amp * k };
};
