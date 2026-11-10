export const W = 1080;
export const H = 1920;
export const FPS = 30;
// Paleta fechada
export const C = { gray: "#EDEDED", red: "#F23B3B", black: "#1C1C1C", yellow: "#F2E63A", white: "#FFFFFF" };
export type Bg = "gray" | "red" | "black";
// Margens de segurança (UI do Instagram)
export const SAFE = { top: 250, bottom: 420, right: 140, left: 70 };
export const SAFE_W = W - SAFE.left - SAFE.right; // 870
// texto: preto no cinza, branco no vermelho, amarelo no preto
export const INK: Record<Bg, { main: string; small: string; hi: string }> = {
  gray: { main: C.black, small: C.black, hi: C.red },
  red: { main: C.white, small: C.white, hi: C.yellow },
  black: { main: C.yellow, small: C.gray, hi: C.yellow },
};
export const FAM = { anton: "Anton", serif: "PlayfairItalic", inter: "InterBold" } as const;
export const SX = { anton: 1, serif: 0.8, inter: 1 } as const; // serifada comprimida a 80%
