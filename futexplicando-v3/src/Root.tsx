import React from "react";
import { Still } from "remotion";
import "./estilo/tokens";
import { CenaTeste, Elenco, FichaLusa } from "./estudio/Revisao";

export const RemotionRoot: React.FC = () => (
  <>
    <Still id="FichaLusa" component={FichaLusa} width={1080} height={1920} />
    <Still id="Elenco" component={Elenco} width={1080} height={1920} />
    <Still id="CenaTeste" component={CenaTeste} width={1080} height={1920} />
  </>
);
