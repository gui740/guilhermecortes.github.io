import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
export const fontsReady = Promise.all([
  loadFont({ family: "Anton", url: staticFile("fonts/anton.woff2"), weight: "400" }),
  loadFont({ family: "PlayfairItalic", url: staticFile("fonts/playfair-italic.woff2"), weight: "400" }),
  loadFont({ family: "InterBold", url: staticFile("fonts/inter-bold.woff2"), weight: "400" }),
]);
