import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {AbsoluteFill, Audio, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {World} from './scene/world';

const IMAGES: Record<string, string> = {
  ghost_main: 'img/films/ghost_main.png', ghost_set: 'img/films/ghost_set.png', ghost_fg: 'img/films/ghost_fg.png',
  medium_main: 'img/films/medium_main.png', medium_set: 'img/films/medium_set.png', medium_fg: 'img/films/medium_fg.png',
  huesera_main: 'img/films/huesera_main.png', huesera_set: 'img/films/huesera_set.png',
};
for (const k of ['pop_bucket', 'tv_admiral', 'tv_discarded', 'tv_mitsubishi', 'tv_sylvania', 'vcr_jvc', 'vcr_magnavox', 'vcr_panasonic', 'vhs_back', 'vhs_front', 'vhs_kaseta', 'vhs_tdk']) IMAGES[k] = `img/kit/${k}.png`;
for (const f of ['ghost', 'medium', 'huesera']) for (let i = 0; i < 6; i++) IMAGES[`${f}_${i}`] = `img/stills/${f}_${i}.jpg`;

const loadImg = (src: string) => new Promise<HTMLImageElement>((res, rej) => { const i = new Image(); i.crossOrigin = 'anonymous'; i.onload = () => res(i); i.onerror = () => rej(new Error('img ' + src)); i.src = src; });
async function loadAll() {
  const fonts = [
    new FontFace('Anton', `url(${staticFile('fonts/Anton.ttf')})`),
    new FontFace('Playfair Display', `url(${staticFile('fonts/PlayfairItalic900.ttf')})`, {style: 'italic', weight: '900'}),
    new FontFace('Special Elite', `url(${staticFile('fonts/SpecialElite.ttf')})`),
    new FontFace('Inter', `url(${staticFile('fonts/InterBold.ttf')})`, {weight: '700'}),
  ];
  await Promise.all(fonts.map(async (f) => { await f.load(); (document.fonts as any).add(f); }));
  const img: Record<string, HTMLImageElement | HTMLCanvasElement> = {};
  await Promise.all(Object.entries(IMAGES).map(async ([k, v]) => { img[k] = await loadImg(staticFile(v)); }));
  // logo oficial (SVG) rasterizado em alta
  const svg = await loadImg(staticFile('img/prime_logo.svg'));
  const c = document.createElement('canvas'); c.width = 1600; c.height = Math.round(1600 * 26.6 / 84.6) + 40;
  c.getContext('2d')!.drawImage(svg, 0, 20, 1600, Math.round(1600 * 26.6 / 84.6));
  img['prime_logo'] = c;
  return {img};
}

export const Reel: React.FC<{hook: string}> = ({hook}) => {
  const frame = useCurrentFrame(); const {width, height, fps} = useVideoConfig();
  const ref = useRef<HTMLCanvasElement>(null); const world = useRef<World | null>(null);
  const [handle] = useState(() => delayRender('init world', {timeoutInMilliseconds: 120000}));
  const [ready, setReady] = useState(false);
  useEffect(() => {
    loadAll().then((assets) => {
      world.current = new World(ref.current!, width, height, assets, hook);
      world.current.render(frame / fps);
      setReady(true); continueRender(handle);
    }).catch((e) => { console.error(e); throw e; });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useLayoutEffect(() => { if (ready && world.current) world.current.render(frame / fps); }, [frame, ready, fps]);
  const audio = hook === 'cover' ? null : hook === 'g' ? 'audio/mix.wav' : `audio/mix_${hook}.wav`;
  return (
    <AbsoluteFill style={{background: '#1C1C1C'}}>
      <canvas ref={ref} width={width} height={height} style={{width: '100%', height: '100%'}} />
      {audio ? <Audio src={staticFile(audio)} /> : null}
    </AbsoluteFill>
  );
};
