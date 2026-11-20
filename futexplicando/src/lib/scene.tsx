import React, { createContext, useContext } from "react";
import { FPS, Word } from "./episode";

type Ctx = { id: string; startSec: number; endSec: number; words: Word[] };
const SceneCtx = createContext<Ctx>({ id: "", startSec: 0, endSec: 0, words: [] });

export const SceneProvider: React.FC<Ctx & { children: React.ReactNode }> = ({ children, ...v }) => (
  <SceneCtx.Provider value={v}>{children}</SceneCtx.Provider>
);

export const useScene = () => useContext(SceneCtx);

const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");

/** Frame (relativo ao início da cena) em que a palavra `key` começa a ser falada. */
export const useWordFrame = (key: string | undefined, occurrence = 0, fallbackSec = 0): number => {
  const { words, startSec } = useScene();
  if (key) {
    const k = norm(key);
    const hits = words.filter((w) => norm(w.key) === k || norm(w.key).split(" ")[0] === k);
    const w = hits[Math.min(occurrence, hits.length - 1)];
    if (w) return Math.round((w.start - startSec) * FPS);
  }
  return Math.round(fallbackSec * FPS);
};

/** Duração da cena em frames. */
export const useSceneFrames = () => {
  const { startSec, endSec } = useScene();
  return Math.round((endSec - startSec) * FPS);
};
