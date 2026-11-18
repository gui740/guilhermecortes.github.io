import React from "react";
import { EpisodioV3, EPISODIO_V3_DUR } from "./v3/EpisodioV3";
import { Short01V3, SHORT01_DUR, Short02V3, SHORT02_DUR } from "./v3/Shorts";
import { ShortN, SHORTS_CFG, duracaoShort } from "./v3/Shorts2";
import { ComHook, hookDur } from "./v3/hooks";
const S01H: React.FC = () => <ComHook shortId="SHORT01"><Short01V3 /></ComHook>;
const S02H: React.FC = () => <ComHook shortId="SHORT02"><Short02V3 /></ComHook>;
const SNH: React.FC<{ id: string }> = ({ id }) => <ComHook shortId={id}><ShortN id={id} /></ComHook>;
import { ColdOpenV2, COLD_OPEN_V2_DUR, COLD_OPEN_GUI_DUR } from "./v3/Rodada1";
import { Composition } from "remotion";
import { Episodio } from "./Episodio";
import { Capa, CapaV3 } from "./Capa";
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
      <Composition id="SHORT01-v3a" component={S01H} durationInFrames={Math.round((SHORT01_DUR + hookDur("SHORT01")) * fps)} fps={fps} width={1080} height={1920} />
      <Composition id="SHORT02-v3a" component={S02H} durationInFrames={Math.round((SHORT02_DUR + hookDur("SHORT02")) * fps)} fps={fps} width={1080} height={1920} />
      {SHORTS_CFG.map((c) => <Composition key={c.id} id={`${c.id}-v3`} component={SNH} defaultProps={{ id: c.id }} durationInFrames={Math.round((duracaoShort(c) + hookDur(c.id)) * fps)} fps={fps} width={1080} height={1920} />)}
      <Composition id="EpisodioV3" component={EpisodioV3} durationInFrames={Math.round(EPISODIO_V3_DUR * fps)} fps={fps} width={1920} height={1080} />
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
      <Composition id="CapaV3" component={CapaV3} durationInFrames={1} fps={fps} width={1280} height={720} />
    </>
  );
};
