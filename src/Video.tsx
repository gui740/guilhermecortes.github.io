import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {World} from './world/World';
import {Counter, Grain} from './Hud';
const FontFaces = () => (
  <style>{`@font-face{font-family:'Anton';src:url(${staticFile('fonts/Anton-normal-400.ttf')})}`}</style>
);
export const Main: React.FC<{stations?: boolean; audio?: string; hook?: any; hud?: boolean}> = ({stations = true, audio, hook, hud = true}) => {
  const frame = useCurrentFrame(); const {fps, width, height} = useVideoConfig();
  const k = width / 1080;
  return (
    <AbsoluteFill style={{backgroundColor: '#EDEDED'}}>
      <FontFaces />
      <ThreeCanvas width={width} height={height} camera={{fov: 50, near: 0.05, far: 120, position: [0, 0, 7]}} gl={{antialias: true, preserveDrawingBuffer: true}}>
        <World frame={frame} fps={fps} stations={stations} hook={hook} />
      </ThreeCanvas>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transform: `scale(${k})`, transformOrigin: '0 0'}}>
        {hud ? <Counter t={frame / fps} /> : null}
        <Grain frame={frame} />
      </div>
      {audio ? <Audio src={staticFile(audio)} /> : null}
    </AbsoluteFill>
  );
};
