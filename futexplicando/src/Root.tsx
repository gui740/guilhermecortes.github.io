import React from "react";
import { Composition, Still } from "remotion";
import { Episode } from "./Episode";
import { Cover } from "./Cover";
import { episode, FPS, HEIGHT, WIDTH, totalFrames } from "./lib/episode";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Episode" component={Episode} durationInFrames={totalFrames()} fps={FPS} width={WIDTH} height={HEIGHT} />
    <Still id="Capa" component={Cover} width={WIDTH} height={HEIGHT} />
  </>
);
void episode;
