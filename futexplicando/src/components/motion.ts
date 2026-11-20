import { random, spring, SpringConfig } from "remotion";

export const pop = (frame: number, fps: number, at: number, config: Partial<SpringConfig> = { damping: 12, stiffness: 180 }) =>
  spring({ frame: frame - at, fps, config });

/** Shake que decai a partir de `at`. */
export const shake = (frame: number, at: number, strength = 18, dur = 12) => {
  const t = frame - at;
  if (t < 0 || t > dur) return { x: 0, y: 0, r: 0 };
  const k = (1 - t / dur) * strength;
  return { x: (random(`x${frame}`) - 0.5) * 2 * k, y: (random(`y${frame}`) - 0.5) * 2 * k, r: (random(`r${frame}`) - 0.5) * k * 0.15 };
};
