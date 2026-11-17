import { loadFont as loadJost } from "@remotion/google-fonts/Jost";
import { loadFont as loadMono } from "@remotion/google-fonts/IBMPlexMono";

const jost = loadJost("normal", { weights: ["400", "500", "700", "800"], subsets: ["latin", "latin-ext"] });
const mono = loadMono("normal", { weights: ["400", "500", "600"], subsets: ["latin", "latin-ext"] });

export const FONT = jost.fontFamily;
export const MONO = mono.fontFamily;

// paleta do canal (monocromática) + acento de interface; cor só no material da Netflix
export const C = {
  branco: "#FFFFFF",
  apoio: "#D9D9D9",
  secundario: "#777777",
  tinta: "#292929",
  ambar: "#FFB000",
  netflix: "#E50914",
  netflixEscuro: "#B20710",
};

export const W = 1920;
export const H = 1080;
// faixa central segura 9:16
export const FAIXA = { x: 656, w: 608 };

export const SOMBRA = "18px 18px 30px rgba(0,0,0,0.22)";
