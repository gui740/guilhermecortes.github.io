import React from 'react';
import {Composition, Still} from 'remotion';
import {World} from './World';
import {FPS, TOTAL_FRAMES} from './timeline';

export const Root: React.FC = () => (
  <>
    <Composition id="Reel" component={World} width={1080} height={1920} fps={FPS} durationInFrames={TOTAL_FRAMES} defaultProps={{hook: 'A', cover: false, captions: true}} />
    <Composition id="Hook" component={World} width={1080} height={1920} fps={FPS} durationInFrames={90} defaultProps={{hook: 'B', cover: false, captions: false}} />
    <Still id="Cover" component={World} width={1080} height={1920} defaultProps={{hook: 'A', cover: true, captions: false}} />
  </>
);
