import React, { useMemo } from "react";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const CORES_TIME = ["#E53935", "#1E88E5", "#111111", "#FFFFFF", "#43A047", "#FDD835", "#8E24AA", "#FB8C00"];
const PELES = ["#F2C29B", "#D9A27A", "#A86F4C", "#7A4B30", "#F6D0B0"];

type Ponto = { pos: [number, number, number]; look: [number, number, number] };

/** Câmera animada por quadros-chave (posição e alvo), interpolados com easing. */
const CameraRig: React.FC<{ keys: Ponto[] }> = ({ keys }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const { camera } = useThree();
  const u = Math.min(1, frame / Math.max(1, durationInFrames - 1));
  const n = keys.length - 1;
  const seg = Math.min(n - 1, Math.floor(u * n));
  const lt = u * n - seg;
  const e = lt < 0.5 ? 2 * lt * lt : 1 - Math.pow(-2 * lt + 2, 2) / 2;
  const a = keys[seg];
  const b = keys[seg + 1];
  const lerp = (p: number, q: number) => p + (q - p) * e;
  camera.position.set(lerp(a.pos[0], b.pos[0]), lerp(a.pos[1], b.pos[1]), lerp(a.pos[2], b.pos[2]));
  camera.lookAt(lerp(a.look[0], b.look[0]), lerp(a.look[1], b.look[1]), lerp(a.look[2], b.look[2]));
  return null;
};

const usePitchTexture = () =>
  useMemo(() => {
    const c = document.createElement("canvas");
    c.width = 1024;
    c.height = 660;
    const g = c.getContext("2d")!;
    for (let i = 0; i < 12; i++) {
      g.fillStyle = i % 2 ? "#3FA548" : "#35923E";
      g.fillRect((i * c.width) / 12, 0, c.width / 12 + 1, c.height);
    }
    g.strokeStyle = "#ffffff";
    g.lineWidth = 6;
    g.strokeRect(20, 20, c.width - 40, c.height - 40);
    g.beginPath();
    g.moveTo(c.width / 2, 20);
    g.lineTo(c.width / 2, c.height - 20);
    g.stroke();
    g.beginPath();
    g.arc(c.width / 2, c.height / 2, 90, 0, Math.PI * 2);
    g.stroke();
    g.strokeRect(20, c.height / 2 - 160, 160, 320);
    g.strokeRect(c.width - 180, c.height / 2 - 160, 160, 320);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, []);

const useBannerTexture = (linhas: string[]) =>
  useMemo(() => {
    const c = document.createElement("canvas");
    c.width = 1024;
    c.height = 256;
    const g = c.getContext("2d")!;
    g.fillStyle = "#0B6E3A";
    g.fillRect(0, 0, c.width, c.height);
    g.strokeStyle = "#FEDD00";
    g.lineWidth = 14;
    g.strokeRect(8, 8, c.width - 16, c.height - 16);
    g.fillStyle = "#FFFFFF";
    g.textAlign = "center";
    g.font = "900 96px 'Baloo 2', Arial";
    g.fillText(linhas[0], c.width / 2, 120);
    g.font = "800 60px 'Baloo 2', Arial";
    g.fillStyle = "#FEDD00";
    g.fillText(linhas[1] ?? "", c.width / 2, 200);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, [linhas]);

/** Torcida: dezenas/centenas de mini-personagens de cabeça redonda (instanciados). */
const Torcida3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { heads, bodies } = useMemo(() => {
    const hs: { p: THREE.Vector3; c: string; ph: number }[] = [];
    const bs: { p: THREE.Vector3; c: string; ph: number }[] = [];
    const rows = 9;
    for (let r = 0; r < rows; r++) {
      const rx = 64 + r * 3.4;
      const rz = 44 + r * 3.4;
      const y = 1.4 + r * 1.9;
      const n = Math.round(120 + r * 8);
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + r * 0.03;
        const seed = Math.sin(i * 12.9898 + r * 78.233) * 43758.5453;
        const rnd = seed - Math.floor(seed);
        if (rnd < 0.08) continue;
        const x = Math.cos(a) * rx;
        const z = Math.sin(a) * rz;
        const team = CORES_TIME[Math.floor(rnd * 997) % CORES_TIME.length];
        hs.push({ p: new THREE.Vector3(x, y + 1.25, z), c: PELES[Math.floor(rnd * 131) % PELES.length], ph: rnd * 6.28 });
        bs.push({ p: new THREE.Vector3(x, y + 0.35, z), c: team, ph: rnd * 6.28 });
      }
    }
    return { heads: hs, bodies: bs };
  }, []);
  const headRef = React.useRef<THREE.InstancedMesh>(null);
  const eyeRef = React.useRef<THREE.InstancedMesh>(null);
  const bodyRef = React.useRef<THREE.InstancedMesh>(null);
  const m = useMemo(() => new THREE.Matrix4(), []);
  const col = useMemo(() => new THREE.Color(), []);
  React.useLayoutEffect(() => {
    const hm = headRef.current;
    const bm = bodyRef.current;
    if (!hm || !bm) return;
    heads.forEach((h, i) => {
      hm.setColorAt(i, col.set(h.c));
      const j = Math.max(0, Math.sin(frame / 4 + h.ph)) * 0.35;
      m.makeTranslation(h.p.x, h.p.y + j, h.p.z);
      hm.setMatrixAt(i, m);
    });
    bodies.forEach((b, i) => {
      bm.setColorAt(i, col.set(b.c));
      const j = Math.max(0, Math.sin(frame / 4 + b.ph)) * 0.35;
      m.makeTranslation(b.p.x, b.p.y + j, b.p.z);
      bm.setMatrixAt(i, m);
    });
    const em = eyeRef.current;
    if (em) {
      heads.forEach((h, i) => {
        const j = Math.max(0, Math.sin(frame / 4 + h.ph)) * 0.35;
        const dir = new THREE.Vector3(-h.p.x, 0, -h.p.z).normalize();
        const side = new THREE.Vector3(-dir.z, 0, dir.x);
        [-1, 1].forEach((sgn, k) => {
          const p = h.p.clone().addScaledVector(dir, 0.72).addScaledVector(side, 0.3 * sgn);
          m.makeTranslation(p.x, p.y + j + 0.12, p.z);
          em.setMatrixAt(i * 2 + k, m);
        });
      });
      em.instanceMatrix.needsUpdate = true;
    }
    hm.instanceMatrix.needsUpdate = true;
    bm.instanceMatrix.needsUpdate = true;
    if (hm.instanceColor) hm.instanceColor.needsUpdate = true;
    if (bm.instanceColor) bm.instanceColor.needsUpdate = true;
  }, [frame, heads, bodies, col, m]);
  return (
    <>
      <instancedMesh ref={headRef} args={[undefined, undefined, heads.length]}>
        <sphereGeometry args={[0.85, 14, 12]} />
        <meshStandardMaterial roughness={0.6} emissive="#3a2a20" emissiveIntensity={0.15} />
      </instancedMesh>
      <instancedMesh ref={eyeRef} args={[undefined, undefined, heads.length * 2]}>
        <sphereGeometry args={[0.14, 6, 6]} />
        <meshBasicMaterial color="#1a1010" />
      </instancedMesh>
      <instancedMesh ref={bodyRef} args={[undefined, undefined, bodies.length]}>
        <boxGeometry args={[1.0, 1.0, 0.7]} />
        <meshStandardMaterial roughness={0.8} />
      </instancedMesh>
    </>
  );
};

const Trofeu3D: React.FC<{ y?: number }> = ({ y = 0 }) => {
  const frame = useCurrentFrame();
  const pts = useMemo(
    () =>
      [
        [0, 0],
        [2.2, 0],
        [2.2, 0.8],
        [1.6, 0.8],
        [0.5, 1.4],
        [0.5, 3.4],
        [1.2, 3.8],
        [2.6, 5.6],
        [3.0, 7.6],
        [2.8, 7.7],
      ].map(([x, yy]) => new THREE.Vector2(x, yy)),
    [],
  );
  return (
    <group position={[0, y, 0]} rotation={[0, frame / 40, 0]}>
      <mesh position={[0, -1.6, 0]}>
        <cylinderGeometry args={[3.2, 3.6, 3.2, 24]} />
        <meshStandardMaterial color="#2A1A10" />
      </mesh>
      <mesh>
        <latheGeometry args={[pts, 40]} />
        <meshStandardMaterial color="#F2C443" metalness={0.35} roughness={0.35} emissive="#7A5208" emissiveIntensity={0.45} />
      </mesh>
      {[-1, 1].map((s) => (
        <mesh key={s} position={[s * 3.0, 5.6, 0]} rotation={[0, 0, Math.PI / 2]}>
          <torusGeometry args={[1.0, 0.25, 10, 20, Math.PI]} />
          <meshStandardMaterial color="#F2C443" metalness={0.35} roughness={0.35} emissive="#7A5208" emissiveIntensity={0.45} />
        </mesh>
      ))}
    </group>
  );
};

/** Estádio 3D simples: gramado, arquibancada em anel, torcida, refletores, faixa e troféu. */
export const Estadio3D: React.FC<{ keys: Ponto[]; faixa?: string[]; trofeu?: boolean; ceu?: string }> = ({ keys, faixa = ["COPA DO BRASIL", ""], trofeu = true, ceu = "#7EC8FF" }) => {
  const { width, height } = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height} style={{ background: ceu }} camera={{ fov: 55, near: 0.5, far: 800, position: [0, 30, 120] }}>
      <CameraRig keys={keys} />
      <hemisphereLight args={["#ffffff", "#7a9a5a", 2.2]} />
      <ambientLight intensity={0.9} />
      <directionalLight position={[60, 120, 40]} intensity={2.4} />
      <directionalLight position={[-60, 80, -40]} intensity={1.0} />
      <Cena faixa={faixa} trofeu={trofeu} />
    </ThreeCanvas>
  );
};

const Cena: React.FC<{ faixa: string[]; trofeu: boolean }> = ({ faixa, trofeu }) => {
  const pitch = usePitchTexture();
  const banner = useBannerTexture(faixa);
  const standSegs = 64;
  return (
    <group>
      {/* chão externo */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.6, 0]}>
        <planeGeometry args={[600, 600]} />
        <meshStandardMaterial color="#6F8F4E" />
      </mesh>
      {/* gramado */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <planeGeometry args={[105, 68]} />
        <meshStandardMaterial map={pitch} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <planeGeometry args={[124, 86]} />
        <meshStandardMaterial color="#2E7D32" />
      </mesh>
      {/* arquibancada em anel (degraus) */}
      {Array.from({ length: 9 }).map((_, r) => (
        <mesh key={r} position={[0, 0.7 + r * 1.9, 0]} scale={[1, 1, (44 + r * 3.4) / (64 + r * 3.4)]}>
          <cylinderGeometry args={[66 + r * 3.4, 66 + r * 3.4, 1.9, standSegs, 1, true]} />
          <meshStandardMaterial color={r % 2 ? "#9AA5B4" : "#B7C0CC"} side={THREE.DoubleSide} />
        </mesh>
      ))}
      {/* parede externa e cobertura */}
      <mesh position={[0, 10, 0]} scale={[1, 1, 75 / 95]}>
        <cylinderGeometry args={[95, 95, 22, standSegs, 1, true]} />
        <meshStandardMaterial color="#E8EDF2" side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[0, 21.5, 0]} rotation={[-Math.PI / 2, 0, 0]} scale={[1, 75 / 95, 1]}>
        <ringGeometry args={[78, 97, standSegs]} />
        <meshStandardMaterial color="#F4F6F8" side={THREE.DoubleSide} />
      </mesh>
      <Torcida3D />
      {/* refletores */}
      {[
        [80, 60],
        [-80, 60],
        [80, -60],
        [-80, -60],
      ].map(([x, z], i) => (
        <group key={i} position={[x, 0, z]}>
          <mesh position={[0, 20, 0]}>
            <cylinderGeometry args={[0.8, 1.2, 40, 8]} />
            <meshStandardMaterial color="#555" />
          </mesh>
          <mesh position={[0, 41, 0]}>
            <boxGeometry args={[8, 4, 1]} />
            <meshStandardMaterial color="#FFF8D0" emissive="#FFF2A0" emissiveIntensity={0.8} />
          </mesh>
        </group>
      ))}
      {/* faixa da torcida */}
      <mesh position={[0, 9, -46.5]}>
        <planeGeometry args={[40, 10]} />
        <meshStandardMaterial map={banner} side={THREE.DoubleSide} />
      </mesh>
      {trofeu ? (
        <group position={[0, 1.6, 0]} scale={1.3}>
          <Trofeu3D />
        </group>
      ) : null}
    </group>
  );
};

/** Interpola um valor por segundos (helper para overlays 2D sincronizados). */
export const useT = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { t: frame / fps, frame, k: (a: number, b: number) => interpolate(frame / fps, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) };
};
