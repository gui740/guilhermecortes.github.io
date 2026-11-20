import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const TITLE = "Anton";
export const SANS = "Inter";

loadFont({ family: TITLE, url: staticFile("fonts/Anton-Regular.ttf"), weight: "400" });
loadFont({ family: SANS, url: staticFile("fonts/Inter.ttf"), weight: "100 900" });
