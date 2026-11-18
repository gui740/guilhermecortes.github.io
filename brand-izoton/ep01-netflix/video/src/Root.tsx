import React from "react";
import { ColdOpenV2, COLD_OPEN_V2_DUR, COLD_OPEN_GUI_DUR } from "./v3/Rodada1";
import { Composition } from "remotion";
import { Episodio } from "./Episodio";
import { Capa } from "./Capa";
import { HookShort } from "./HookShort";
import { ColdOpen, Colagem, COLAGEM_GUI_DUR, FalaT04, TransicaoCap, Short02Hook } from "./v3/Amostra";
import timeline from "./timeline.json";

export const Root: React.FC = () => {
  const fps = timeline.fps;
  return (
    <>
      <Composition id="Episodio" component={Episodio} durationInFrames={Math.ceil(timeline.duracao * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="HookShort" component={HookShort} durationInFrames={1} fps={fps} width={1080} height={1920} defaultProps={{ texto: "TÍTULO", num: "SHORT 01" }} />
      <Composition id="V3ColdOpen" component={ColdOpen} durationInFrames={Math.round(28.6 * fps)} fps={fps} width={1920} height={1080} />
      {/* rodada 1 com a narração do Guilherme */}
      <Composition id="V3ColdOpen-v2-gui" component={ColdOpenV2} defaultProps={{ voz: "gui" as const }} durationInFrames={Math.round(COLD_OPEN_GUI_DUR * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3Colagem-v2-gui" component={Colagem} defaultProps={{ v2: true, voz: "gui" as const }} durationInFrames={Math.round(COLAGEM_GUI_DUR * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3TransicaoCap-v2-gui" component={TransicaoCap} defaultProps={{ voz: "gui" as const }} durationInFrames={Math.round(10.5 * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3ColdOpen-v2" component={ColdOpenV2} durationInFrames={Math.round(COLD_OPEN_V2_DUR * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3Colagem-v2" component={Colagem} defaultProps={{ v2: true }} durationInFrames={Math.round(13.9 * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3Colagem" component={Colagem} durationInFrames={Math.round(13.9 * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3FalaT04" component={FalaT04} durationInFrames={Math.round(25.36 * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3TransicaoCap-v2" component={TransicaoCap} durationInFrames={Math.round(10.5 * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3TransicaoCap" component={TransicaoCap} durationInFrames={Math.round(10.5 * fps)} fps={fps} width={1920} height={1080} />
      <Composition id="V3Short02Hook" component={Short02Hook} durationInFrames={Math.round(5.6 * fps)} fps={fps} width={1080} height={1920} />
      <Composition id="Capa" component={Capa} durationInFrames={1} fps={fps} width={1280} height={720} />
    </>
  );
};
