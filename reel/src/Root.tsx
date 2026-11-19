import React from 'react';
import {Composition} from 'remotion';
import {Reel} from './Reel';
import tl from './timeline.json';
import tlB from './timeline_gB.json';
import tlC from './timeline_gC.json';
export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Reel" component={Reel} durationInFrames={tl.durationInFrames} fps={30} width={1080} height={1920} defaultProps={{hook: 'g'}} />
    <Composition id="GanchoB" component={Reel} durationInFrames={Math.round((tlB.hookEnd + 1.6) * 30)} fps={30} width={1080} height={1920} defaultProps={{hook: 'gB'}} />
    <Composition id="GanchoC" component={Reel} durationInFrames={Math.round((tlC.hookEnd + 1.6) * 30)} fps={30} width={1080} height={1920} defaultProps={{hook: 'gC'}} />
    <Composition id="Preview" component={Reel} durationInFrames={tl.durationInFrames} fps={30} width={540} height={960} defaultProps={{hook: 'g'}} />
    <Composition id="Capa" component={Reel} durationInFrames={1} fps={30} width={1080} height={1920} defaultProps={{hook: 'cover'}} />
  </>
);
