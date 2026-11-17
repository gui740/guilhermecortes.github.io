import React from 'react';
import {Composition, Still} from 'remotion';
import {Capa} from './Capa';
import {Reel} from './Reel';
import {DURATION_FRAMES, FPS} from './timeline';

export const Root: React.FC = () => (
  <>
    <Composition id="Reel" component={Reel} durationInFrames={DURATION_FRAMES} fps={FPS} width={1080} height={1920} defaultProps={{cameraOnly: false, captions: true}} />
    <Composition id="PreviewCamera" component={Reel} durationInFrames={DURATION_FRAMES} fps={FPS} width={1080} height={1920} defaultProps={{cameraOnly: true, captions: false}} />
    <Still id="Capa" component={Capa} width={1080} height={1920} />
    {(['A', 'B', 'C'] as const).map((v) => (
      <Composition key={v} id={`Gancho${v}`} component={Reel} durationInFrames={90} fps={FPS} width={1080} height={1920} defaultProps={{cameraOnly: false, captions: true, variant: v}} />
    ))}
  </>
);
