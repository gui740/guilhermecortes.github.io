import React from "react";
import { Composition, Still } from "remotion";
import data from "./data/sao-paulo.json";
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
    </>
  );
};
