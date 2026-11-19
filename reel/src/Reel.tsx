import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {AbsoluteFill, Audio, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {World} from './scene/world';
import capG from './captions.json';
import capB from './captions_gB.json';
import capC from './captions_gC.json';
const CAPS: Record<string, {text: string; start: number; end: number}[]> = {g: capG as any, gB: capB as any, gC: capC as any};

// Legenda: Anton (mesma família das palavras-chave), pequena, centrada acima da margem inferior de 420 px
const Caption: React.FC<{hook: string; t: number; scale: number}> = ({hook, t, scale}) => {
  const c = (CAPS[hook] ?? []).find((x) => t >= x.start && t < x.end);
  if (!c) return null;
  const k = Math.min(1, (t - c.start) / 0.13); const out = Math.min(1, Math.max(0, (c.end - t) / 0.1));
  const o = Math.min(k, out);
  return (
    <div style={{position: 'absolute', left: 140 * scale, right: 140 * scale, top: 1418 * scale, display: 'flex', justifyContent: 'center', pointerEvents: 'none'}}>
      <div style={{fontFamily: 'Anton', fontSize: 58 * scale, lineHeight: 1.1, color: '#EDEDED', letterSpacing: 0.6 * scale, padding: `${6 * scale}px ${18 * scale}px`,
        background: 'rgba(28,28,28,0.55)', borderRadius: 10 * scale, textShadow: `0 ${2 * scale}px ${8 * scale}px rgba(28,28,28,0.9)`, textAlign: 'center',
        opacity: o, transform: `translateY(${(1 - k) * 10 * scale}px)`}}>{c.text}</div>
    </div>
  );
};

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
      {hook !== 'cover' && ready ? <Caption hook={hook} t={frame / fps} scale={width / 1080} /> : null}
      {audio ? <Audio src={staticFile(audio)} /> : null}
    </AbsoluteFill>
  );
};
