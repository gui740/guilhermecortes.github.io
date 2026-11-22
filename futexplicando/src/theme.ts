import { continueRender, delayRender, staticFile } from "remotion";
import fonts from "../public/fonts/fonts.json";

// Fontes Google (licença OFL) servidas localmente de public/fonts/
const loadLocalFonts = () => {
  if (typeof document === "undefined") return;
  const handle = delayRender("Carregando fontes locais");
  Promise.all(
    (fonts as [string, string, string, string][]).map(([family, weight, file, unicodeRange]) => {
      const face = new FontFace(family, `url(${staticFile(`fonts/${file}`)}) format('woff2')`, { weight, unicodeRange, display: "block" });
      document.fonts.add(face);
      return face.load();
    }),
  )
    .then(() => continueRender(handle))
    .catch((e) => {
      console.error(e);
      continueRender(handle);
    });
};
loadLocalFonts();

export const ANTON = "Anton, Impact, sans-serif";
export const BEBAS = "'Bebas Neue', Impact, sans-serif";
export const INTER = "Inter, Arial, sans-serif";

export const C = {
  // cor de destaque do vídeo: definida por composição via CSS var --accent (padrão: vermelho SPFC)
  red: "var(--accent, #E30613)",
  black: "#111111",
  white: "#F4EFE6",
  gray: "#8A8A8A",
  paper: "#F4EFE6",
  paperDark: "#E6DECF",
};
