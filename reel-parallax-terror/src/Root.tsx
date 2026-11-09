import React from 'react';
import {Composition} from 'remotion';
import {Reel} from './Reel';
import {TIMING} from './config/cenas';
import {ALTURA, FPS, LARGURA} from './config/timing';

export const Root: React.FC = () => (
  <Composition id="Reel" component={Reel} durationInFrames={TIMING.total} fps={FPS} width={LARGURA} height={ALTURA} />
);
