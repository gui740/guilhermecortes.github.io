import React, {useLayoutEffect, useMemo, useState} from 'react';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';
import {G, makeMat} from './material';
import {ELS, El, RING, doorOpenAt} from './scene';
import {ASPECT, FPS, STATIONS, beamAt, beamOnAt, camAt, clamp, kickAt, lerp, redAt, smooth, focusAt, stationWeight} from './timeline';

const CHAR = new THREE.Color('#1C1C1C');
const REDF = new THREE.Color('#1C1C1C').lerp(new THREE.Color('#F23B3B'), 0.2);
const hash = (n: number) => {
  const x = Math.sin(n * 127.1) * 43758.5453;
  return x - Math.floor(x);
};

// carrega todas as texturas uma vez
const useTextures = (paths: string[]) => {
  const [handle] = useState(() => delayRender('texturas'));
  const [tex, setTex] = useState<Record<string, THREE.Texture> | null>(null);
  useLayoutEffect(() => {
    const loader = new THREE.TextureLoader();
    const out: Record<string, THREE.Texture> = {};
    Promise.all(
      paths.map(
        (p) =>
          new Promise<void>((res, rej) =>
            loader.load(
              staticFile(p),
              (t) => {
                t.colorSpace = THREE.SRGBColorSpace;
                t.anisotropy = 4;
                t.generateMipmaps = true;
                t.minFilter = THREE.LinearMipmapLinearFilter;
                out[p] = t;
                res();
              },
              undefined,
              (e) => rej(e),
            ),
          ),
      ),
    ).then(() => {
      setTex(out);
      continueRender(handle);
    });
  }, []);
  return tex;
};

type Built = {el: El; mesh: THREE.Mesh; shadow?: THREE.Mesh; pivot: THREE.Object3D; mat: THREE.ShaderMaterial; smat?: THREE.ShaderMaterial};

const lineTex = (() => {
  const c = new THREE.DataTexture(new Uint8Array([40, 40, 40, 255]), 1, 1);
  c.needsUpdate = true;
  return c;
})();
const dashTex = (() => {
  const c = new THREE.DataTexture(new Uint8Array([0xf2, 0x3b, 0x3b, 255]), 1, 1);
  c.colorSpace = THREE.SRGBColorSpace;
  c.needsUpdate = true;
  return c;
})();

export const World: React.FC<{cameraOnly?: boolean; variant?: 'A' | 'B' | 'C'; atFrame?: number}> = ({cameraOnly, variant = 'A', atFrame}) => {
  const cur = useCurrentFrame();
  const frame = atFrame ?? cur;
  const t = frame / FPS;
  const {gl, scene, camera, size} = useThree();
  const els = useMemo(() => (cameraOnly ? ELS.filter((e) => e.kind !== 'text' && e.kind !== 'dash' && e.kind !== 'tag') : ELS.filter((e) => !e.variant || e.variant === variant)), [cameraOnly, variant]);
  const paths = useMemo(() => Array.from(new Set(els.map((e) => e.tex).filter(Boolean) as string[])), [els]);
  const tex = useTextures(paths);

  const built = useMemo(() => {
    if (!tex) return null;
    const root = new THREE.Group();
    const list: Built[] = [];
    for (const el of els) {
      let map: THREE.Texture | null = el.tex ? tex[el.tex] : el.kind === 'dash' ? dashTex : lineTex;
      if (map && el.uv) {
        map = map.clone();
        map.offset.set(el.uv[0], el.uv[1]);
        map.repeat.set(el.uv[2], el.uv[3]);
        map.wrapS = THREE.RepeatWrapping;
        map.needsUpdate = true;
      }
      const segs = el.wave ? 40 : 1;
      const geo = new THREE.PlaneGeometry(1, 1, segs, 1);
      const mat = makeMat(map, {emissive: el.emissive ?? (el.kind === 'line' ? 0.3 : 0), wave: el.wave, fogMul: el.fogMul});
      const mesh = new THREE.Mesh(geo, mat);
      mesh.frustumCulled = false;
      const pivot = new THREE.Object3D();
      pivot.add(mesh);
      root.add(pivot);
      let shadow: THREE.Mesh | undefined;
      let smat: THREE.ShaderMaterial | undefined;
      if (el.shadow) {
        smat = makeMat(map, {shadow: true});
        shadow = new THREE.Mesh(geo, smat);
        shadow.frustumCulled = false;
        shadow.renderOrder = -1;
        pivot.add(shadow);
      }
      list.push({el, mesh, shadow, pivot, mat, smat});
    }
    // poeira no ar
    const N = 700;
    const pts = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      pts[i * 3] = (hash(i) - 0.5) * 6;
      pts[i * 3 + 1] = (hash(i + 99) - 0.5) * 5;
      pts[i * 3 + 2] = hash(i + 7) * 30;
    }
    const pg = new THREE.BufferGeometry();
    pg.setAttribute('position', new THREE.BufferAttribute(pts, 3));
    const dust = new THREE.Points(pg, new THREE.PointsMaterial({color: '#EDEDED', size: 0.018, transparent: true, opacity: 0.55, depthWrite: false, sizeAttenuation: true}));
    dust.frustumCulled = false;
    root.add(dust);
    scene.add(root);
    return {root, list, dust, base: pts.slice()};
  }, [tex]);

  // ---------------------------------------------------------------- atualização por frame
  if (built) {
    const c = camAt(t);
    const cam = camera as THREE.PerspectiveCamera;
    cam.fov = c.fov;
    cam.aspect = ASPECT;
    cam.near = 0.05;
    cam.far = 200;
    cam.position.set(c.x, c.y, c.z);
    cam.up.set(Math.sin(c.roll), Math.cos(c.roll), 0);
    cam.lookAt(c.tx, c.ty, c.tz);
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld();
    const fwd = new THREE.Vector3(c.tx - c.x, c.ty - c.y, c.tz - c.z).normalize();
    const right = new THREE.Vector3().crossVectors(fwd, cam.up).normalize();
    const up = new THREE.Vector3().crossVectors(right, fwd).normalize();
    const b = beamAt(t);
    const beamDir = fwd.clone().add(right.clone().multiplyScalar(b.x)).add(up.clone().multiplyScalar(b.y)).normalize();
    G.uCamPos.value.set(c.x, c.y, c.z);
    G.uBeamDir.value.copy(beamDir);
    const on = beamOnAt(t);
    G.uBeamOn.value = on;
    G.uAmbient.value = 0.03 + 0.11 * on;
    G.uTime.value = t;
    G.uRes.value.set(size.width, size.height);
    G.uFogColor.value.copy(CHAR).lerp(REDF, redAt(t));
    const tanH = Math.tan(((c.fov / 2) * Math.PI) / 180);
    const focus = focusAt(t);
    const speed = c.speed;
    const kick = kickAt(t);
    const travelled = -c.z;
    const motionPx = clamp((speed - 4.5) * 1.5, 0, 24);

    type St = {x: number; y: number; z: number; opacity: number; scale: number; extraBlur: number; rotZ: number; rotY: number; rotX: number; D: number; sil: number};
    const states: St[] = [];
    for (const B of built.list) {
      const el = B.el;
      let x = el.x, y = el.y, z = el.z;
      let opacity = el.opacity ?? 1;
      let scale = 1;
      let extraBlur = 0;
      let rotZ = el.rotZ ?? 0;
      let rotY = el.rotY ?? 0;
      const rotX = el.rotX ?? 0;
      void extraBlur;
      if (el.ring !== undefined) {
        // corredor infinito: o que passa da câmera volta lá pro fundo
        const depth = ((((el.ring - travelled + 1.8) % RING) + RING) % RING) - 1.8;
        z = c.z - depth;
        opacity *= 1 - smooth(RING - 9, RING - 2.5, depth);
        // não poluir a frente do assassino na estação
        if (el.kind === 'tape' || el.kind === 'smoke' || (Math.abs(el.x) < 1.6 && el.hang)) {
          for (const s of STATIONS) {
            const w = stationWeight(s, t);
            if (w > 0 && z < s.killerZ + 9 && z > s.killerZ - 1.5) opacity *= 1 - (el.kind === 'smoke' ? 0.5 : 0.92) * w;
          }
        }
      }
      if (el.drift) x += el.drift * t;
      
      if (el.from !== undefined && t < el.from) opacity = 0;
      if (el.kind === 'tape' && el.ring !== undefined) opacity *= lerp(0.3, 1, smooth(1.5, 6, c.z - z));
      if (el.to !== undefined) opacity *= 1 - smooth(el.to - 0.2, el.to, t);
      // gancho e fecho: fitas do corredor recuam para não cruzar o texto (janelas com rampa suave)
      if (el.kind === 'tape' && el.ring !== undefined) {
        const wtape = smooth(0.1, 0.4, t) * (1 - smooth(4.5, 4.9, t)) + smooth(33.0, 33.4, t) * (1 - smooth(37.6, 37.9, t));
        opacity *= 1 - 0.75 * wtape * (1 - smooth(10, 16, c.z - z));
      }
      let D = (c.z - z);
      if (el.kind === 'text' || el.kind === 'tag' || el.kind === 'star' || el.kind === 'dash') {
        const t0 = el.t0 ?? 0;
        if (t < t0 - 0.0001 && t0 > 0.01) opacity = 0;
        else if (el.kind === 'text' && t0 > 0.01 && !el.noAnim) {
          const p = clamp((t - t0) / (5 / FPS));
          z -= 2.5 * (1 - p) * (1 - p);
          opacity *= 0.4 + 0.6 * p;
          extraBlur = 12 * (1 - p);
          scale = 0.9 + 0.1 * p;
          if (el.impact) {
            const f = Math.floor((t - t0) * FPS);
            if (f >= 0 && f < 3) {
              x += (hash(f + t0 * 13) - 0.5) * 0.07 * el.w;
              y += (hash(f + t0 * 7 + 3) - 0.5) * 0.07 * el.h;
            }
          }
        } else if (el.kind === 'star') {
          const p = clamp((t - t0) / 0.35);
          scale = p < 1 ? Math.sin(p * Math.PI * 0.5) * (1 + 0.18 * Math.sin(p * Math.PI)) : 1;
          rotZ += t * 0.15;
        } else if (el.kind === 'tag') {
          opacity *= clamp((t - t0) / 0.2);
        } else if (el.kind === 'dash') {
          opacity *= clamp((t - t0) / 0.06);
        }
        // elementos gráficos somem antes de virar borrão na lente
        if (el.kind === 'star') opacity *= smooth(2.6, 4.6, c.z - z);
        if (el.kind === 'dash' || el.kind === 'tag') opacity *= smooth(1.0, 2.2, c.z - z);
        // saída: a câmera passa pelo texto (ele corre até a lente)
        if (el.until !== undefined && t > el.until) {
          const q = clamp((t - el.until) / 0.32);
          const d0 = c.z - z;
          z += Math.max(0, d0 - 0.6) * 0.75 * q * q;
          opacity *= 1 - smooth(0.15, 0.85, q);
        }
        D = c.z - z;
        if (el.kind === 'text') opacity *= smooth(0.35, 1.2, D);
      }
      if (el.kind === 'line' && el.t0 !== undefined && t < el.t0) opacity = 0;
      let sil = 0;
      if (el.kind === 'killer' && el.station) {
        const s = el.station;
        sil = 1 - smooth(s.tReveal - 0.02, s.tReveal + 0.18, t);
        scale = 1 + 0.08 * smooth(s.tReveal, s.tReveal + 4 / FPS, t); // "dá um passo"
        opacity *= smooth(0.9, 1.9, D);
        // respira levemente
        y += Math.sin(t * 1.7) * 0.015;
      }
      states.push({x, y, z, opacity, scale, extraBlur, rotZ, rotY, rotX, D, sil});
    }
    // ---- margem de segurança por bloco (texto em leitura fica no quadro seguro: topo 250, base acima da legenda, direita 140)
    {
      const X0 = -1 + (2 * 60) / 1080, X1 = 1 - (2 * 140) / 1080, Y0 = -0.4, Y1 = 1 - (2 * 250) / 1920;
      const groups = new Map<string, number[]>();
      built.list.forEach((B, i) => {
        const el = B.el;
        const S = states[i];
        if (el.kind !== 'text' || S.opacity < 0.01) return;
        if (el.t0 !== undefined && t < el.t0) return;
        if (el.until !== undefined && t >= el.until) return;
        const g = el.group ?? el.key;
        if (!groups.has(g)) groups.set(g, []);
        groups.get(g)!.push(i);
      });
      for (const idx of groups.values()) {
        const info = idx.map((i) => {
          const S = states[i];
          const el = built.list[i].el;
          const Dd = (S.x - c.x) * fwd.x + (S.y - c.y) * fwd.y + (S.z - c.z) * fwd.z;
          const kx = Math.max(0.05, Dd) * tanH * ASPECT, ky = Math.max(0.05, Dd) * tanH;
          const rx = ((S.x - c.x) * right.x + (S.y - c.y) * right.y + (S.z - c.z) * right.z) / kx;
          const ry = ((S.x - c.x) * up.x + (S.y - c.y) * up.y + (S.z - c.z) * up.z) / ky;
          return {i, Dd, kx, ky, rx, ry, hw: (el.w * S.scale) / 2 / kx, hh: (el.h * S.scale) / 2 / ky};
        }).filter((o) => o.Dd > 0.4);
        if (!info.length) continue;
        let minx = Math.min(...info.map((o) => o.rx - o.hw)), maxx = Math.max(...info.map((o) => o.rx + o.hw));
        let miny = Math.min(...info.map((o) => o.ry - o.hh)), maxy = Math.max(...info.map((o) => o.ry + o.hh));
        const cx = (minx + maxx) / 2, cy = (miny + maxy) / 2;
        let f = 1;
        if (maxx - minx > (X1 - X0) * 0.96) f = Math.min(f, ((X1 - X0) * 0.96) / (maxx - minx));
        if (maxy - miny > (Y1 - Y0) * 0.96) f = Math.min(f, ((Y1 - Y0) * 0.96) / (maxy - miny));
        minx = cx + (minx - cx) * f; maxx = cx + (maxx - cx) * f; miny = cy + (miny - cy) * f; maxy = cy + (maxy - cy) * f;
        let dx = 0, dy = 0;
        if (minx < X0) dx = X0 - minx; else if (maxx > X1) dx = X1 - maxx;
        if (maxy > Y1) dy = Y1 - maxy; else if (miny < Y0) dy = Y0 - miny;
        for (const o of info) {
          const S = states[o.i];
          const nrx = cx + (o.rx - cx) * f + dx, nry = cy + (o.ry - cy) * f + dy;
          const ddx = (nrx - o.rx) * o.kx, ddy = (nry - o.ry) * o.ky;
          S.x += right.x * ddx + up.x * ddy; S.y += right.y * ddx + up.y * ddy; S.z += right.z * ddx + up.z * ddy;
          S.scale *= f;
        }
      }
    }

    built.list.forEach((B, i) => {
      const el = B.el;
      let {x, y, z, opacity, scale, extraBlur, rotZ, rotY, rotX, D, sil} = states[i];
      if (el.rip) {
        const r = smooth(2.0, 0.2, D);
        rotZ += el.rip.side * r * 1.1;
        x += el.rip.side * r * 1.6;
        y -= r * r * 0.8;
      }
      if (el.door) {
        const open = doorOpenAt(t, D);
        rotY = -el.door.side * open * 1.5;
      }
      // pivot (pendurados balançam no fio; batida forte balança mais)
      if (el.hang) {
        const sw = Math.sin(t * 1.3 + el.hang.phase) * el.hang.amp + kick * 0.12 * Math.sin(t * 9 + el.hang.phase);
        const L = el.hang.top - y;
        B.pivot.position.set(x, el.hang.top, z);
        B.pivot.rotation.set(0, 0, sw);
        B.mesh.position.set(0, -L, 0);
        B.mesh.rotation.set(rotX, rotY + Math.sin(t * 0.6 + el.hang.phase) * 0.35, rotZ);
      } else if (el.door) {
        B.pivot.position.set(el.door.hingeX, y, z);
        B.pivot.rotation.set(0, rotY, 0);
        B.mesh.position.set(-el.door.hingeX + x, 0, 0);
        B.mesh.rotation.set(0, 0, 0);
      } else {
        B.pivot.position.set(x, y, z);
        B.pivot.rotation.set(0, 0, 0);
        B.mesh.position.set(0, 0, 0);
        B.mesh.rotation.set(rotX, rotY, rotZ);
      }
      B.mesh.scale.set(el.w * scale, el.h * scale, 1);
      const visible = opacity > 0.003 && D > -0.5 && D < 80;
      B.pivot.visible = visible;
      if (!visible) return;
      // tamanho projetado (px) -> desfoque em UV
      const Dp = Math.max(0.15, D);
      const planePx = Math.max(8, ((el.w * scale) / (2 * Dp * tanH * ASPECT)) * size.width);
      const near = clamp((2.8 - Dp) / 1.7) * 13 + clamp((focus * 0.55 - Dp) / focus) * 3;
      const far = clamp((Dp - focus * 1.7) / (focus * 2.5)) * 4.5;
      let blurPx = (el.kind === 'text' ? clamp((1.3 - Dp) / 0.9) * 12 : near + far) + extraBlur;
      if (el.kind === 'smoke' || el.kind === 'line' || el.kind === 'dash') blurPx = 0;
      B.mat.uniforms.uBlur.value = blurPx / planePx;
      B.mat.uniforms.uMotion.value = el.kind === 'smoke' ? 0 : motionPx / planePx;
      B.mat.uniforms.uOpacity.value = opacity;
      B.mat.uniforms.uSil.value = sil;
      if (B.shadow && B.smat) {
        // sombra suave deslocada para trás
        B.shadow.position.copy(B.mesh.position).add(new THREE.Vector3(0.035 + el.h * scale * 0.025, -0.045 - el.h * scale * 0.03, -0.07));
        B.shadow.rotation.copy(B.mesh.rotation);
        B.shadow.scale.copy(B.mesh.scale);
        B.smat.uniforms.uBlur.value = (blurPx + 10) / planePx;
        B.smat.uniforms.uOpacity.value = opacity * (el.kind === 'text' ? 0.8 : 0.9);
        B.smat.uniforms.uMotion.value = 0;
      }
    });
    // poeira reciclada em volta da câmera
    const pos = built.dust.geometry.getAttribute('position') as THREE.BufferAttribute;
    for (let i = 0; i < pos.count; i++) {
      const bz = built.base[i * 3 + 2];
      const depth = (((bz - travelled * 1.0 + 0.5) % 30) + 30) % 30 - 0.5;
      pos.setXYZ(i, built.base[i * 3] + Math.sin(t * 0.4 + i) * 0.15, built.base[i * 3 + 1] + Math.sin(t * 0.3 + i * 0.7) * 0.1, c.z - depth);
    }
    pos.needsUpdate = true;
    (built.dust.material as THREE.PointsMaterial).opacity = 0.5 * on;
  }

  useLayoutEffect(() => {
    if (!built) return;
    gl.setClearColor(G.uFogColor.value.clone().multiplyScalar(0.7), 1);
    gl.render(scene, camera);
  });
  return null;
};
