import React from 'react';
import {Composition, Still} from 'remotion';
import {Reel} from './Reel';
import {Cover} from './Cover';
import {FPS, TOTAL} from './data';

export const Root: React.FC = () => (
  <>
    <Composition id="Reel" component={Reel} durationInFrames={TOTAL} fps={FPS} width={1080} height={1920} />
    <Still id="Capa" component={Cover} width={1080} height={1920} />
  </>
);
