import React from "react";
import { Composition, Still } from "remotion";
import "./estilo/tokens";
import { CenaTeste, Elenco, FichaLusa } from "./estudio/Revisao";
import { Capa, ContatoCena, duracaoTotal, FPS, Historia, Video } from "./motor/Video";
import { TemposCena } from "./motor/tempo";
import historia from "../historias/lusa2013.json";
import tempos from "../videos/lusa2013/tempos.json";

const H = historia as unknown as Historia;
const T = tempos as TemposCena[];

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Lusa2013" component={Video} defaultProps={{ historia: H, tempos: T, trilha: `${H.id}/mix.wav` }} durationInFrames={duracaoTotal(T)} fps={FPS} width={1080} height={1920} />
    {H.cenas.map((c, i) => (
      <Still key={c.id} id={`Contato-${String(i + 1).padStart(2, "0")}-${c.id}`} component={ContatoCena} defaultProps={{ historia: H, tempos: T, cena: i }} width={12 + 3 * 364} height={650} />
    ))}
    <Still id={`Capa-${H.id}`} component={Capa} defaultProps={{ historia: H, tempos: T, cena: 0, plano: 0, t: 3 }} width={1080} height={1920} />
    <Still id="FichaLusa" component={FichaLusa} width={1080} height={1920} />
    <Still id="Elenco" component={Elenco} width={1080} height={1920} />
    <Still id="CenaTeste" component={CenaTeste} width={1080} height={1920} />
  </>
);
