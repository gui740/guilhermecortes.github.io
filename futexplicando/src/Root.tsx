import React from "react";
import { Composition, Still } from "remotion";
import data from "./data/sao-paulo.json";
import palm from "./data/palmeiras.json";
import cor from "./data/corinthians.json";
import cdb from "./data/copa-do-brasil.json";
import fla from "./data/flamengo.json";
import { Flamengo } from "./videos/Flamengo/Flamengo";
import { CopaDoBrasil } from "./videos/CopaDoBrasil/CopaDoBrasil";
import { CapaCorinthians, Corinthians } from "./videos/Corinthians/Corinthians";
import { CapaPalmeiras, Palmeiras } from "./videos/Palmeiras/Palmeiras";
import { CapaSaoPaulo } from "./videos/SaoPaulo/Capa";
import { SaoPaulo } from "./videos/SaoPaulo/SaoPaulo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SaoPaulo"
        component={SaoPaulo}
        durationInFrames={Math.round(data.duracaoSegundos * data.fps)}
        fps={data.fps}
        width={data.width}
        height={data.height}
      />
      <Still id="CapaSaoPaulo" component={CapaSaoPaulo} width={data.width} height={data.height} />
      <Composition
        id="Palmeiras"
        component={Palmeiras}
        durationInFrames={Math.round(palm.duracaoSegundos * palm.fps)}
        fps={palm.fps}
        width={palm.width}
        height={palm.height}
      />
      <Still id="CapaPalmeiras" component={CapaPalmeiras} width={palm.width} height={palm.height} />
      <Composition
        id="Corinthians"
        component={Corinthians}
        durationInFrames={Math.round(cor.duracaoSegundos * cor.fps)}
        fps={cor.fps}
        width={cor.width}
        height={cor.height}
      />
      <Still id="CapaCorinthians" component={CapaCorinthians} width={cor.width} height={cor.height} />
      <Composition
        id="CopaDoBrasil"
        component={CopaDoBrasil}
        durationInFrames={Math.round(cdb.duracaoSegundos * cdb.fps)}
        fps={cdb.fps}
        width={cdb.width}
        height={cdb.height}
      />
      <Composition
        id="Flamengo"
        component={Flamengo}
        durationInFrames={Math.round(fla.duracaoSegundos * fla.fps)}
        fps={fla.fps}
        width={fla.width}
        height={fla.height}
      />
    </>
  );
};
