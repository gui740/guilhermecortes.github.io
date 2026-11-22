import React from "react";
import { Composition, Still } from "remotion";
import data from "./data/sao-paulo.json";
import palm from "./data/palmeiras.json";
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
    </>
  );
};
