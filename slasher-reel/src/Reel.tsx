import React from 'react';
import {AbsoluteFill} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {World} from './World';
import {Overlay} from './Overlay';

export const Reel: React.FC<{cameraOnly?: boolean; captions?: boolean; variant?: 'A' | 'B' | 'C'}> = ({cameraOnly = false, captions = true, variant = 'A'}) => {
  return (
    <AbsoluteFill style={{background: '#1C1C1C'}}>
      <ThreeCanvas width={1080} height={1920} frameloop="never" gl={{antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance'}} camera={{fov: 50, near: 0.05, far: 200, position: [0, 0, 0]}}>
        <World cameraOnly={cameraOnly} variant={variant} />
      </ThreeCanvas>
      <Overlay captions={captions && !cameraOnly} hud variant={variant} />
    </AbsoluteFill>
  );
};
