import React from 'react';
import {Composition, Still} from 'remotion';
import {Main} from './Video';
import {Capa} from './Capa';
import {TOTAL} from './data/stops.mjs';
import {HOOKS} from './data/hooks';
const F = Math.round(TOTAL * 30);
export const Root: React.FC = () => (
  <>
    <Composition id="Video" component={Main} durationInFrames={F} fps={30} width={1080} height={1920} defaultProps={{audio: 'audio/mix.wav'}} />
    <Composition id="PreviewCamera" component={Main} durationInFrames={F} fps={30} width={540} height={960} defaultProps={{stations: false}} />
    {Object.entries(HOOKS).map(([id, h]) => (
      <Composition key={id} id={`Gancho${id}`} component={Main} durationInFrames={105} fps={30} width={1080} height={1920} defaultProps={{hook: h.els, audio: h.audio}} />
    ))}
    <Still id="Capa" component={Capa} width={1080} height={1920} />
  </>
);
