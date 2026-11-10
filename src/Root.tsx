import React, { useEffect, useState } from "react";
import { Composition, Still, continueRender, delayRender } from "remotion";
import { FPS, W, H } from "./theme";
import { fontsReady } from "./fonts";
import { Reel, REEL_FRAMES } from "./Reel";
import { Capa, GanchoA, GanchoB, GanchoC } from "./Extras";

/** só renderiza depois que as fontes carregam (a medição de texto depende delas) */
const withFonts = (Comp: React.FC): React.FC => () => {
  const [handle] = useState(() => delayRender("fontes"));
  const [ok, setOk] = useState(false);
  useEffect(() => { fontsReady.then(() => { setOk(true); continueRender(handle); }); }, [handle]);
  return ok ? <Comp /> : null;
};
const ReelF = withFonts(Reel), A = withFonts(GanchoA), B = withFonts(GanchoB), Cc = withFonts(GanchoC), CapaF = withFonts(Capa);
export const Root: React.FC = () => (
  <>
    <Composition id="Reel" component={ReelF} durationInFrames={REEL_FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="GanchoA" component={A} durationInFrames={90} fps={FPS} width={W} height={H} />
    <Composition id="GanchoB" component={B} durationInFrames={90} fps={FPS} width={W} height={H} />
    <Composition id="GanchoC" component={Cc} durationInFrames={90} fps={FPS} width={W} height={H} />
    <Still id="Capa" component={CapaF} width={W} height={H} />
  </>
);
