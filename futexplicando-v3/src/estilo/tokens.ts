import { continueRender, delayRender, staticFile } from "remotion";
import fonts from "../../public/fonts/fonts.json";

/** Bíblia de estilo vetorial do @futexplicando v3 (reusar em todos os vídeos). */

// Fontes Google (licença OFL) servidas localmente de public/fonts/
const carregarFontes = () => {
  if (typeof document === "undefined") return;
  const h = delayRender("Carregando fontes locais");
  Promise.all(
    (fonts as [string, string, string, string][]).map(([family, weight, file, unicodeRange]) => {
      const face = new FontFace(family, `url(${staticFile(`fonts/${file}`)}) format('woff2')`, { weight, unicodeRange, display: "block" });
      document.fonts.add(face);
      return face.load();
    }),
  )
    .then(() => continueRender(h))
    .catch((e) => {
      console.error(e);
      continueRender(h);
    });
};
carregarFontes();

export const FONTE = {
  titulo: "Anton, Impact, sans-serif",
  apoio: "'Bebas Neue', Impact, sans-serif",
  redondo: "'Baloo 2', Arial, sans-serif",
  texto: "Inter, Arial, sans-serif",
};

/** Paleta: noite de estádio (azul profundo) + refletores quentes. */
export const COR = {
  contorno: "#2B1A10", // marrom-escuro, peso uniforme
  amarelo: "#FFD400",
  branco: "#FFFFFF",
  preto: "#0E0E12",
  ceuTopo: "#070F2E",
  ceuMeio: "#13285E",
  ceuBase: "#2A4E92",
  luzQuente: "#FFE2A8",
  aro: "#FFE6B8", // rim light quente
  sombra: "rgba(40, 20, 70, 0.28)", // tom único de sombra (cel)
  grama1: "#2E9E4F",
  grama2: "#38B25B",
  vermelho: "#E1251B",
};

/** Peso do contorno (px no viewBox do personagem 500x900). */
export const TRACO = 7;

/** Tons de pele. */
export const PELE = {
  clara: { base: "#F7CFAE", sombra: "#E6A986" },
  media: { base: "#E2A57B", sombra: "#C9855C" },
  morena: { base: "#B97A50", sombra: "#9A603C" },
  escura: { base: "#7E4E30", sombra: "#653B22" },
};
export type TomPele = keyof typeof PELE;
