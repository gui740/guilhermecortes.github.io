import React from 'react';
import {registerRoot, Composition, Still, staticFile, delayRender, continueRender} from 'remotion';
import {Reel, Gancho} from './Reel';
import {Capa} from './Capa';
import {TOTAL, HOOKS} from './timeline';

// Carrega as fontes antes de qualquer frame (medição de texto depende delas)
const handle = delayRender('fonts');
const faces = [
  new FontFace('Anton', `url(${staticFile('fonts/Anton.ttf')})`),
  new FontFace('PlayfairI', `url(${staticFile('fonts/PlayfairItalic.ttf')})`, {style: 'italic', weight: '400 900'}),
  new FontFace('InterB', `url(${staticFile('fonts/Inter.ttf')})`, {weight: '100 900'}),
];
Promise.all(faces.map((f) => f.load())).then((fs) => {fs.forEach((f) => (document as any).fonts.add(f)); continueRender(handle);});

const Root: React.FC = () => (
  <>
    <Composition id="Reel" component={Reel} durationInFrames={Math.round(TOTAL * 30)} fps={30} width={1080} height={1920} />
    <Composition id="GanchoA" component={Gancho} defaultProps={{v: 'A' as const}} durationInFrames={Math.round(HOOKS.A.dur * 30)} fps={30} width={1080} height={1920} />
    <Composition id="GanchoB" component={Gancho} defaultProps={{v: 'B' as const}} durationInFrames={Math.round(HOOKS.B.dur * 30)} fps={30} width={1080} height={1920} />
    <Composition id="GanchoC" component={Gancho} defaultProps={{v: 'C' as const}} durationInFrames={Math.round(HOOKS.C.dur * 30)} fps={30} width={1080} height={1920} />
    <Still id="Capa" component={Capa} width={1080} height={1920} />
  </>
);
registerRoot(Root);
