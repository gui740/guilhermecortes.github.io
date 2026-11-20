// Ponto único de troca de episódio: aponte para outro JSON nos próximos.
import data from "../data/ep01.json";

export type Word = { text: string; key: string; start: number; end: number; scene: string };
export type SceneTiming = { id: string; start: number; end: number; voiceStart: number; voiceEnd: number };
export type SceneData = { id: string; type: string; narration: string; image?: ImageRef; props: any };
export type ImageRef = { src: string; credit?: string };

export type Episode = typeof data & {
  scenes: SceneData[];
  timing: { engine: string; totalSeconds: number; scenes: SceneTiming[]; words: Word[] };
};

export const episode = data as unknown as Episode;
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const palette = episode.palette;
export const sec = (s: number) => Math.round(s * FPS);
export const db = (d: number) => Math.pow(10, d / 20);
export const totalFrames = () => sec(episode.timing.totalSeconds);
