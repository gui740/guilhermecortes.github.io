import timeline from "../public/timeline.json";
import events from "../public/events.json";
import cutMeta from "../public/cut/meta.json";
import { FPS } from "./theme";
export type TLWord = { w: string; t: number; e: number; line: string };
export type TLLine = { id: string; text: string; t: number; e: number; w0: number; w1: number };
export type TL = { duration: number; words: TLWord[]; lines: TLLine[] };
export const TLS = timeline as unknown as Record<string, TL> & { fps: number };
export const EVENTS = events as unknown as Record<string, { frames: number; duration: number }>;
export const CUT = cutMeta as Record<string, { w: number; h: number }>;
/** frame em que a palavra entra (1 frame antes da fala, para parecer cravado) */
export const wf = (t: number) => Math.max(0, Math.round(t * FPS) - 1);
export const sceneStart = (t: number) => Math.max(0, Math.round(t * FPS) - 3);
export const makeW = (tl: TL) => {
  const L = Object.fromEntries(tl.lines.map((l) => [l.id, l]));
  return {
    line: (id: string) => L[id],
    /** frame da i-ésima palavra da frase */
    w: (id: string, i: number) => wf(tl.words[L[id].w0 + i].t),
    words: (id: string) => tl.words.slice(L[id].w0, L[id].w1),
    /** legenda automática: 1 a 3 palavras por vez, na hora da fala */
    cap: (...ids: string[]) => {
      const out: { t: string; at: number }[] = [];
      for (const id of ids) {
        let cur: string[] = [], at = 0;
        for (const x of tl.words.slice(L[id].w0, L[id].w1)) {
          if (cur.length && (cur.length >= 3 || (cur.join(" ") + " " + x.w).length > 15)) { out.push({ t: cur.join(" "), at }); cur = []; }
          if (!cur.length) at = wf(x.t);
          cur.push(x.w.toLowerCase());
        }
        if (cur.length) out.push({ t: cur.join(" "), at });
      }
      return out;
    },
  };
};
