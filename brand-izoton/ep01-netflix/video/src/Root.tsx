import React from "react";
import { Composition } from "remotion";
import { Episodio } from "./Episodio";
import { Capa } from "./Capa";
import timeline from "./timeline.json";

export const Root: React.FC = () => {
  const fps = timeline.fps;
  return (
    <>
      <Composition id="Episodio" component={Episodio} durationInFrames={Math.ceil(timeline.duracao * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="Capa" component={Capa} durationInFrames={1} fps={fps} width={1280} height={720} />
    </>
  );
};
