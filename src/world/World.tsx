import React, {useMemo, useLayoutEffect, useState} from 'react';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {staticFile, useDelayRender} from 'remotion';
import {STOPS, AMBIENT, COLORS, TOTAL} from '../data/stops.mjs';
import {makeT, buildCamera, FOV, ASPECT, TANH, HM, D, clamp, eOut, eBack, eIO, LEAD} from '../lib/path.mjs';
import {wordTexture, stampTexture, starTexture, moleculeCanvas} from '../lib/gfx';
import TL from '../timeline.json';

export const T = makeT(TL as any);
const tEnd = TOTAL;
const R = (ref: any) => (ref === 'end' ? tEnd : typeof ref === 'string' && ref.startsWith('end') ? tEnd + parseFloat(ref.slice(3)) : T(ref));
export const STARTS = STOPS.map((s: any) => R(s.start));
export const CAM = buildCamera(STARTS, tEnd);
const hex = (h: string) => new THREE.Vector3(parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255);
const C = Object.fromEntries(Object.entries(COLORS).map(([k, v]) => [k, hex(v as string)])) as Record<string, THREE.Vector3>;
const AMB = AMBIENT.map(([t, c]: any) => [R(t), c] as [number, string]);
/** pesos (cinza, vermelho, preto) do ambiente no instante t — degradê suave entre chaves */
export function ambientW(t: number) {
  const W: Record<string, number> = {gray: 0, red: 0, black: 0};
  let i = 0; while (i < AMB.length - 1 && AMB[i + 1][0] <= t) i++;
  const [t0, c0] = AMB[i], nx = AMB[i + 1];
  if (!nx || c0 === nx[1]) { W[c0] = 1; return W; }
  const u = clamp((t - t0) / Math.max(0.01, nx[0] - t0)), s = u * u * (3 - 2 * u);
  W[c0] += 1 - s; W[nx[1]] += s; return W;
}
export function palette(t: number) {
  const w = ambientW(t);
  const mix = (a: THREE.Vector3, b: THREE.Vector3, c: THREE.Vector3) => a.clone().multiplyScalar(w.gray).add(b.clone().multiplyScalar(w.red)).add(c.clone().multiplyScalar(w.black));
  return {
    fog: mix(C.gray, C.red, C.black),
    text: mix(C.ink, C.white, C.yellow),            // preto no cinza, branco no vermelho, amarelo no preto
    hl: mix(C.red, C.yellow, C.red),                // destaque: vermelho (amarelo sobre o vermelho)
    smoke: mix(new THREE.Vector3(1, 1, 1), new THREE.Vector3(1, .93, .9), new THREE.Vector3(.55, .55, .55)),
    w,
  };
}
const css = (v: THREE.Vector3) => `rgb(${Math.round(v.x * 255)},${Math.round(v.y * 255)},${Math.round(v.z * 255)})`;
export const cssColor = css;

// ---------------- material único para todos os cartões (folhas, fotos, textos, fumaça)
const VS = `varying vec2 vUv; varying float vDepth;
void main(){ vUv = uv; vec4 mv = modelViewMatrix * vec4(position,1.0); vDepth = -mv.z; gl_Position = projectionMatrix * mv; }`;
const FS = `uniform sampler2D map; uniform float uOpacity, uBias, uFogNear, uFogFar, uMode; uniform vec3 uFog, uTint;
varying vec2 vUv; varying float vDepth;
void main(){
  vec4 c = texture2D(map, vUv, uBias);
  vec3 col = c.rgb;
  if (uMode > 0.5 && uMode < 1.5) col = uTint;                                     // texto: cor dinâmica
  else if (uMode > 1.5 && uMode < 2.5) col = mix(uTint*0.28, mix(uTint, vec3(1.0), 0.45), c.r); // folha verde
  else if (uMode > 2.5) col = uTint;                                               // fumaça
  float f = smoothstep(uFogNear, uFogFar, vDepth);
  col = mix(col, uFog, f);
  float a = c.a * uOpacity;
  if (a < 0.004) discard;
  gl_FragColor = vec4(col, a);
}`;
function mat(map: THREE.Texture, mode = 0) {
  return new THREE.ShaderMaterial({
    vertexShader: VS, fragmentShader: FS, transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: {map: {value: map}, uOpacity: {value: 1}, uBias: {value: 0}, uFogNear: {value: 7}, uFogFar: {value: 40}, uMode: {value: mode}, uFog: {value: new THREE.Vector3()}, uTint: {value: new THREE.Vector3(1, 1, 1)}},
  });
}
const PLANE = new THREE.PlaneGeometry(1, 1);
function rng(seed: number) { let s = seed; return () => ((s = (s * 16807) % 2147483647) / 2147483647); }

const LEAVES = ['leaf01', 'leaf02', 'leaf03', 'leaf04', 'leaf05', 'leaf06', 'leaf07', 'leaf08', 'ramo01', 'ramo02', 'ramo03', 'ramo07', 'ramo08'];
const SMOKES = ['smoke0', 'smoke1', 'smoke2', 'smoke3'];
function texList() {
  const s = new Set<string>([...LEAVES, ...SMOKES]);
  STOPS.forEach((st: any) => { st.els.forEach((e: any) => (e.tex ? s.add(e.tex) : 0)); if (st.cover) s.add(st.cover); });
  return [...s];
}
function useTextures() {
  const {delayRender, continueRender} = useDelayRender();
  const [state] = useState(() => ({h: delayRender('texturas'), tex: {} as Record<string, THREE.Texture>, ready: false}));
  const [ready, setReady] = useState(false);
  useLayoutEffect(() => {
    const L = new THREE.TextureLoader(); const names = texList();
    const fontsP = Promise.all([
      new FontFace('Anton', `url(${staticFile('fonts/Anton-normal-400.ttf')})`).load(),
      new FontFace('Playfair Display', `url(${staticFile('fonts/PlayfairDisplay-italic-900.ttf')})`, {style: 'italic', weight: '900'}).load(),
      new FontFace('Inter', `url(${staticFile('fonts/Inter-normal-700.ttf')})`, {weight: '700'}).load(),
    ]).then((fs) => fs.forEach((f) => (document.fonts as any).add(f)));
    const texP = Promise.all(names.map((n) => new Promise<void>((res, rej) => L.load(staticFile(`tex/${n}.png`), (t) => {
      t.colorSpace = THREE.NoColorSpace; t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; t.anisotropy = 4; state.tex[n] = t; res();
    }, undefined, () => rej(new Error('textura ' + n))))));
    Promise.all([fontsP, texP]).then(() => { state.ready = true; setReady(true); });
  }, []);
  return {tex: ready ? state.tex : null, release: () => continueRender(state.h)};
}

// ---------------- construção do mundo
type Card = {mesh: THREE.Mesh; m: THREE.ShaderMaterial; base: any; kind: string; e?: any; at?: number; out?: number; aspect?: number; extra?: any};
function place(e: any, k: number) {
  const dz = e.dz || 0, dd = HM - dz, zr = -k * D + dz;
  const hh = 2 * dd * TANH, ww = hh * ASPECT;
  return {x: (e.x / 1080 - 0.5) * ww, y: (0.5 - e.y / 1920) * hh, z: zr, s: (e.h / 1920) * hh};
}
function build(tex: Record<string, THREE.Texture>, opts: {stations: boolean; hook?: any}) {
  const root = new THREE.Group(); const cards: Card[] = []; const r = rng(4242);
  // fundo (cor da névoa) preso à câmera
  const bg = new THREE.Mesh(PLANE, new THREE.ShaderMaterial({uniforms: {uC: {value: new THREE.Vector3()}}, vertexShader: 'void main(){gl_Position=vec4(position.xy*2.0,0.9999,1.0);}', fragmentShader: 'uniform vec3 uC; void main(){gl_FragColor=vec4(uC,1.0);}', depthTest: false, depthWrite: false}));
  bg.renderOrder = -100; bg.frustumCulled = false; root.add(bg);
  // túnel: folhas em anéis ao redor do caminho, recicladas (L)
  const L = 46, N = 250;
  for (let i = 0; i < N; i++) {
    const name = LEAVES[Math.floor(r() * LEAVES.length)], t = tex[name];
    const green = r() < 0.09; const m = mat(t, green ? 2 : 0); if (green) m.uniforms.uTint.value = C.green.clone();
    const mesh = new THREE.Mesh(PLANE, m); const asp = (t.image as any).width / (t.image as any).height;
    const ang = r() * Math.PI * 2, crosser = false;
    const rad = crosser ? 0.35 + r() * 0.5 : 1;
    const rx = (crosser ? rad : 1.55 + r() * 1.2), ry = (crosser ? rad * 1.4 : 2.55 + r() * 1.4);
    const sz = (name.startsWith('ramo') ? 1.6 : 1.0) * (0.7 + r() * 0.85) * (crosser ? 0.7 : 1);
    mesh.scale.set(sz * asp * (r() < 0.5 ? -1 : 1), sz, 1);
    const base = {x: Math.cos(ang) * rx, y: Math.sin(ang) * ry, z0: (i / N) * L + r() * 0.3, rz: r() * Math.PI * 2, ry: (r() - .5) * 0.9, rx: (r() - .5) * 0.6, sw: 0.017 + r() * 0.035, sf: 0.6 + r() * 1.1, sp: r() * 6.28, L};
    root.add(mesh); cards.push({mesh, m, base, kind: 'leaf'});
  }
  // faixas de fumaça atravessando entre as camadas
  for (let i = 0; i < 22; i++) {
    const t = tex[SMOKES[i % 4]]; const m = mat(t, 3); const mesh = new THREE.Mesh(PLANE, m);
    const w = 7 + r() * 8; mesh.scale.set(w, w * 0.5 * (0.6 + r() * 0.6), 1);
    const base = {x: (r() - .5) * 5, y: (r() - .5) * 7, z0: (i / 22) * L + r() * 1.5, vx: (r() < .5 ? -1 : 1) * (0.12 + r() * 0.45), op: 0.16 + r() * 0.22, rz: (r() - .5) * 0.5, L};
    root.add(mesh); cards.push({mesh, m, base, kind: 'smoke'});
  }
  // partículas (pólen/poeira)
  const PN = 1100, pos = new Float32Array(PN * 3), seeds = new Float32Array(PN * 3);
  for (let i = 0; i < PN; i++) { seeds[i * 3] = (r() - .5) * 7; seeds[i * 3 + 1] = (r() - .5) * 11; seeds[i * 3 + 2] = r() * L; }
  const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pm = new THREE.ShaderMaterial({transparent: true, depthWrite: false, uniforms: {uC: {value: new THREE.Vector3(1, 1, 1)}, uFog: {value: new THREE.Vector3()}},
    vertexShader: 'varying float vD; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); vD=-mv.z; gl_PointSize = clamp(34.0/vD, 1.5, 22.0); gl_Position=projectionMatrix*mv; }',
    fragmentShader: 'uniform vec3 uC, uFog; varying float vD; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.1,d)*0.55*(1.0-smoothstep(10.0,38.0,vD)); if(a<0.01) discard; gl_FragColor=vec4(mix(uC,uFog,smoothstep(8.0,40.0,vD)),a); }'});
  const pts = new THREE.Points(pg, pm); pts.frustumCulled = false; root.add(pts);
  // estações
  if (opts.stations) STOPS.forEach((st: any, k: number) => {
    const els = k === 0 && opts.hook ? opts.hook : st.els;
    els.forEach((e: any, j: number) => {
      let t: THREE.Texture, aspect = 1, mode = 0, hPerPx = 1, extra: any = {}; let haloT: THREE.Texture | null = null;
      if (e.type === 'word') { const w = wordTexture(e.text, e.font); t = w.tex; haloT = w.halo; aspect = w.aspect; hPerPx = w.hPerPx; mode = 1; }
      else if (e.type === 'stamp') { const s = stampTexture(e.text, e.kind, 11 + j * 7 + k * 31); t = s.tex; aspect = s.aspect; mode = s.colored ? 0 : 1; }
      else if (e.type === 'star') { const s = starTexture(); t = s.tex; aspect = 1; }
      else if (e.type === 'molecule') { const s = moleculeCanvas(); t = s.tex; aspect = s.aspect; mode = 1; extra.draw = s.draw; extra.last = -1; }
      else if (e.type === 'puff') { t = tex.smoke2; aspect = 2; mode = 3; }
      else { t = tex[e.tex]; aspect = (t.image as any).width / (t.image as any).height; }
      const m = mat(t, mode); const mesh = new THREE.Mesh(PLANE, m); const p = place(e, k);
      const hgt = e.type === 'word' ? p.s * hPerPx : p.s;
      mesh.scale.set(hgt * aspect, hgt, 1);
      if (e.hook) { mesh.renderOrder = 20; m.depthTest = false; }
      if (haloT) {   // halo na cor do fundo, logo atrás da palavra
        const hm = mat(haloT, 1); const halo = new THREE.Mesh(PLANE, hm); halo.scale.set(hgt * aspect, hgt, 1);
        if (e.hook) { halo.renderOrder = 19; hm.depthTest = false; }
        mesh.add(halo); halo.position.set(0, 0, -0.004); halo.scale.set(1, 1, 1); extra.halo = hm; mesh.renderOrder = mesh.renderOrder || 1;
      }
      root.add(mesh);
      cards.push({mesh, m, base: {...p, rot: ((e.rot || 0) * Math.PI) / 180, sx: hgt * aspect, sy: hgt}, kind: e.type, e, at: R(e.at) - LEAD, out: e.out != null ? R(e.out) : undefined, extra});
    });
    if (st.cover) {   // revelação: folha gigante/fumaça no caminho, cobre a tela por 3–4 quadros na chegada
      const t = tex[st.cover]; const m = mat(t, st.cover.startsWith('smoke') ? 3 : 0); const mesh = new THREE.Mesh(PLANE, m);
      const asp = (t.image as any).width / (t.image as any).height; const s = st.cover.startsWith('smoke') ? 6 : 4.2;
      mesh.scale.set(s * asp, s, 1); root.add(mesh);
      cards.push({mesh, m, base: {x: 0.15, y: 0.1, z: -k * D + 6.2 + 3.2, rot: 0.6}, kind: 'cover'});
    }
  });
  // folha da abertura/fecho (loop)
  const om = mat(tex.leaf07, 0); om.depthTest = false; const ol = new THREE.Mesh(PLANE, om); ol.renderOrder = 10; ol.frustumCulled = false;
  const oasp = (tex.leaf07.image as any).width / (tex.leaf07.image as any).height; root.add(ol);
  return {root, cards, bg, pts, pg, seeds, PN, L, ol, oasp};
}

const camM = new THREE.Matrix4(), tmpV = new THREE.Vector3(), tmpQ = new THREE.Quaternion();
/** pose da folha de abertura em coordenadas de câmera: p=0 cobre a tela; p=1 já saiu */
function openingPose(p: number) {
  const e = eIO(p);
  return {x: -0.02 - e * 2.6, y: 0.31 + e * 1.7, z: -(0.42 + e * 2.4), rz: 0.35 + e * 1.4, ry: e * 0.8, s: 2.6};
}

export const World: React.FC<{frame: number; fps: number; stations?: boolean; hook?: any; tOverride?: number; camOverride?: any}> = ({frame, fps, stations = true, hook, tOverride, camOverride}) => {
  const {tex, release} = useTextures();
  const {camera, advance} = useThree();
  const W = useMemo(() => (tex ? build(tex, {stations, hook}) : null), [tex]);
  useLayoutEffect(() => { if (W) { advance(performance.now()); release(); } }, [W]);
  const t = tOverride ?? frame / fps;
  if (W) {
    const cam = camOverride ? camOverride(t) : CAM(t);
    const pc = camera as THREE.PerspectiveCamera;
    if (pc.fov !== FOV) { pc.fov = FOV; pc.near = 0.05; pc.far = 120; pc.updateProjectionMatrix(); }
    pc.position.set(cam.x, cam.y, cam.z); pc.up.set(0, 1, 0); pc.lookAt(cam.lx, cam.ly, cam.lz); pc.updateMatrixWorld();
    const P = palette(t);
    (W.bg.material as THREE.ShaderMaterial).uniforms.uC.value.copy(P.fog);
    const fogNear = 4.5, fogFar = 30;
    for (const c of W.cards) {
      const u = c.m.uniforms; u.uFog.value.copy(P.fog); u.uFogNear.value = fogNear; u.uFogFar.value = fogFar;
      const b = c.base, mesh = c.mesh;
      if (c.kind === 'leaf') {
        const ahead = (((cam.z - b.z0 + 1.6) % b.L) + b.L) % b.L - 1.6;
        mesh.position.set(b.x, b.y, cam.z - ahead);
        const sway = Math.sin(t * b.sf + b.sp) * b.sw;
        mesh.rotation.set(b.rx + sway * 0.6, b.ry, b.rz + sway);
        mesh.visible = ahead > -1.0;
        // profundidade de campo: frente desfocada, fundo levemente desfocado
        u.uBias.value = ahead < 2.4 ? 1.2 + 3.6 * clamp((2.4 - ahead) / 2.0) : ahead > 15 ? clamp((ahead - 15) / 14) * 1.3 : 0;
        u.uOpacity.value = clamp((ahead + 1.0) / 0.6);
        continue;
      }
      if (c.kind === 'smoke') {
        const ahead = (((cam.z - b.z0 + 2) % b.L) + b.L) % b.L - 2;
        let x = b.x + b.vx * t; x = ((x + 6) % 12 + 12) % 12 - 6;
        mesh.position.set(x, b.y, cam.z - ahead); mesh.rotation.set(0, 0, b.rz);
        u.uTint.value.copy(P.smoke); u.uOpacity.value = b.op * clamp((ahead + 1) / 2.5) * clamp((ahead + 2) / 1); u.uBias.value = 1.5;
        mesh.visible = ahead > -1.5; continue;
      }
      if (c.kind === 'cover') {
        const dc = cam.z - b.z; mesh.position.set(b.x, b.y, b.z); mesh.rotation.set(0, 0, b.rot);
        mesh.visible = dc > -0.1 && dc < 30; u.uBias.value = dc < 1.5 ? 2.5 : 0.4; u.uTint.value.copy(P.smoke); u.uOpacity.value = clamp(dc / 0.25) * (c.m.uniforms.uMode.value > 2.5 ? 0.95 : 1);
        continue;
      }
      // elementos de estação
      const e = c.e, at = c.at!; let vis = t >= at;
      if (e.type === 'word' && e.hook) vis = true;
      if (!vis) { mesh.visible = false; continue; }
      const age = t - at;
      let p = clamp(age / 0.16), op = 0.4 + 0.6 * eOut(p), sc = 0.9 + 0.1 * eOut(p), zoff = -0.8 * (1 - eOut(p)), bias = 3.6 * (1 - eOut(p));
      if (e.type === 'img' || e.type === 'star') { const q = clamp(age / 0.3); sc = 0.55 + 0.45 * eBack(q); op = clamp(age / 0.12); zoff = -0.5 * (1 - eOut(q)); bias = 2.5 * (1 - eOut(q)); }
      if (e.type === 'stamp') { const q = clamp(age / 0.14); sc = 2.4 - 1.4 * q * q * q; op = clamp(age / 0.08); zoff = 0; bias = 0; const k = Math.floor((age - 0.14) * fps); if (k >= 0 && k < 3) sc = [1.07, 0.97, 1.02][k]; }
      if (e.type === 'puff') { const q = clamp(age / 2.2); sc = 0.6 + 0.9 * eOut(q); op = 0.75 * Math.sin(Math.PI * q); bias = 1.5; u.uTint.value.copy(P.smoke); }
      if (e.type === 'molecule') { const q = clamp(age / e.dur); if (Math.abs(q - c.extra.last) > 0.004) { c.extra.draw(q); c.extra.last = q; } }
      let sx = 0, sy = 0;
      if (e.shake) { const k = Math.floor(age * fps); if (k < 3) { const a = [[14, -9], [-11, 8], [6, -4]][k]; sx = a[0] * 0.004; sy = a[1] * 0.004; } }
      if (e.faint) op *= 0.5;
      if (c.out != null && t >= c.out) { const q = clamp((t - c.out) / 0.35); op *= 1 - q; zoff += 1.2 * eOut(q); }
      // parting: elementos se abrem para os lados quando a câmera atravessa a estação
      const dc = cam.z - (b.z + zoff);
      let px = b.x, py = b.y;
      if (dc < 2.6) {
        const k2 = (2.6 - dc); const len = Math.hypot(px, py) || 1; const dx = len < 0.05 ? 0 : px / len, dy = len < 0.05 ? 1 : py / len;
        px += dx * k2 * k2 * 0.42; py += dy * k2 * k2 * 0.42; op *= clamp((dc - 0.25) / 0.6);
      }
      mesh.visible = op > 0.003 && dc > 0.15;
      mesh.position.set(px + sx, py + sy, b.z + zoff);
      mesh.rotation.set(0, 0, b.rot || 0);
      mesh.scale.set(b.sx * sc, b.sy * sc, 1);
      u.uOpacity.value = op; u.uBias.value = bias;
      if (c.extra.halo) { const hu = c.extra.halo.uniforms; hu.uTint.value.copy(P.fog); hu.uFog.value.copy(P.fog); hu.uOpacity.value = op * 0.78; hu.uBias.value = bias + 0.5; hu.uFogNear.value = u.uFogNear.value; hu.uFogFar.value = u.uFogFar.value; }
      if (e.type === 'word' || (e.type === 'stamp' && u.uMode.value > 0.5) || e.type === 'molecule') u.uTint.value.copy(e.hl ? P.hl : P.text);
      // texto atrás do recorte: some no nevoeiro só longe; perto fica nítido
      if (!e.hook) { u.uFogNear.value = 9; u.uFogFar.value = 44; }
    }
    // partículas
    const arr = W.pg.attributes.position.array as Float32Array;
    for (let i = 0; i < W.PN; i++) {
      const sx = W.seeds[i * 3], sy = W.seeds[i * 3 + 1], z0 = W.seeds[i * 3 + 2];
      const ahead = (((cam.z - z0 + 1) % W.L) + W.L) % W.L - 1;
      arr[i * 3] = sx + Math.sin(t * 0.5 + i) * 0.15; arr[i * 3 + 1] = sy + Math.sin(t * 0.37 + i * 1.7) * 0.2 + t * 0.05 % 1; arr[i * 3 + 2] = cam.z - ahead;
    }
    W.pg.attributes.position.needsUpdate = true;
    const pmu = (W.pts.material as THREE.ShaderMaterial).uniforms; pmu.uFog.value.copy(P.fog); pmu.uC.value.copy(P.w.black > 0.5 ? C.yellow : new THREE.Vector3(1, 1, 1));
    // folha do loop: abertura (0–0.55s) e mergulho final (últimos 0.6s)
    let op = -1;
    if (!camOverride) { if (t < 0.55) op = t / 0.55; else if (t > tEnd - 0.65) op = Math.max(0, 1 - (t - (tEnd - 0.65)) / 0.6); }
    if (op >= 0 && op < 1) {  // op=0 → folha cobrindo a tela (igual ao quadro 0)
      const pose = openingPose(Math.max(0, op));
      tmpV.set(pose.x, pose.y, pose.z).applyMatrix4(pc.matrixWorld); W.ol.position.copy(tmpV);
      W.ol.quaternion.copy(pc.quaternion); W.ol.rotateZ(pose.rz); W.ol.rotateY(pose.ry);
      W.ol.scale.set(pose.s * W.oasp, pose.s, 1); W.ol.visible = true;
      const ou = (W.ol.material as THREE.ShaderMaterial).uniforms; ou.uFog.value.copy(P.fog); ou.uFogNear.value = 50; ou.uFogFar.value = 60; ou.uBias.value = 0.6 * (1 - op);
    } else W.ol.visible = false;
  }
  return W ? <primitive object={W.root} /> : null;
};
