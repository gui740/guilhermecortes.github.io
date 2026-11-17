import * as THREE from 'three';

// Material único para todos os recortes/planos do corredor.
// - luz de lanterna (cone a partir da câmera) + ambiente escuro
// - névoa exponencial com cor animada (carvão -> vermelho nas revelações)
// - profundidade de campo (blur de disco, raio em UV calculado por plano)
// - motion blur radial (acelerações)
// - silhueta (assassino escuro antes da revelação)
// - modo sombra (projeção suave atrás do recorte)
// - tremular (fitas)
const vert = /* glsl */ `
uniform float uTime;
uniform float uWave;
varying vec2 vUv;
varying vec3 vWorld;
void main(){
  vUv = uv;
  vec3 p = position;
  if (uWave > 0.0) {
    p.y += sin(uv.x * 18.0 + uTime * 9.0) * uWave * 0.5 + sin(uv.x * 7.0 - uTime * 5.0) * uWave;
    p.z += cos(uv.x * 11.0 + uTime * 7.0) * uWave * 2.0;
  }
  vec4 w = modelMatrix * vec4(p, 1.0);
  vWorld = w.xyz;
  gl_Position = projectionMatrix * viewMatrix * w;
}`;

const frag = /* glsl */ `
precision highp float;
uniform sampler2D map;
uniform float uOpacity;
uniform float uBlur;      // raio do desfoque em UV
uniform float uMotion;    // comprimento do motion blur em UV
uniform vec2 uRes;
uniform float uEmissive;  // 0 = depende da luz; 1 = sempre aceso (texto)
uniform float uSil;       // 0..1 silhueta
uniform float uShadow;    // 1 = desenha só a sombra
uniform vec3 uTint;
uniform vec3 uFogColor;
uniform float uFogDensity;
uniform vec3 uCamPos;
uniform vec3 uBeamDir;
uniform float uBeamOn;
uniform float uAmbient;
uniform float uFogMul;
varying vec2 vUv;
varying vec3 vWorld;

const vec2 TAPS[12] = vec2[12](
  vec2(-0.326,-0.406), vec2(-0.840,-0.074), vec2(-0.696,0.457), vec2(-0.203,0.621),
  vec2(0.962,-0.195), vec2(0.473,-0.480), vec2(0.519,0.767), vec2(0.185,-0.893),
  vec2(0.507,0.064), vec2(0.896,0.412), vec2(-0.322,-0.933), vec2(-0.792,-0.598));

vec4 samp(vec2 uv){
  if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) return vec4(0.0);
  return texture2D(map, uv);
}

void main(){
  vec4 c;
  float r = uBlur;
  if (r < 0.0006 && uMotion < 0.0006) {
    c = samp(vUv);
  } else {
    c = samp(vUv) * 0.16;
    float wsum = 0.16;
    for (int i = 0; i < 12; i++) {
      vec2 o = TAPS[i] * r;
      c += samp(vUv + o) * 0.07; wsum += 0.07;
    }
    if (uMotion > 0.0006) {
      vec2 sc = gl_FragCoord.xy / uRes - 0.5;
      vec2 dir = normalize(sc + 1e-4) * uMotion * (0.35 + length(sc) * 1.6);
      for (int i = 1; i <= 8; i++) {
        float f = float(i) / 8.0;
        c += samp(vUv - dir * f) * 0.09; wsum += 0.09;
      }
    }
    c /= wsum;
  }
  if (c.a < 0.003) discard;
  vec3 col = c.rgb / max(c.a, 1e-4);
  col *= uTint;

  vec3 toP = vWorld - uCamPos;
  float dist = length(toP);
  vec3 dirP = toP / max(dist, 1e-4);
  float cosA = dot(dirP, normalize(uBeamDir));
  float core = smoothstep(0.95, 0.985, cosA);
  float halo = smoothstep(0.80, 0.955, cosA) * 0.5;
  float att = 1.0 / (1.0 + 0.012 * dist * dist);
  float beam = (core * 1.6 + halo) * att * uBeamOn;
  float light = uAmbient + beam;
  vec3 lit = col * mix(light, 1.0, uEmissive);
  lit = mix(lit, vec3(0.012), uSil);

  float fog = 1.0 - exp(-uFogDensity * dist * uFogMul);
  lit = mix(lit, uFogColor, clamp(fog, 0.0, 1.0));

  float a = c.a * uOpacity;
  if (uShadow > 0.5) {
    gl_FragColor = vec4(vec3(0.0), a * 0.55 * (1.0 - fog));
    return;
  }
  gl_FragColor = vec4(lit, a);
}`;

export type CutUniforms = {
  map: {value: THREE.Texture | null};
  uOpacity: {value: number};
  uBlur: {value: number};
  uMotion: {value: number};
  uRes: {value: THREE.Vector2};
  uEmissive: {value: number};
  uSil: {value: number};
  uShadow: {value: number};
  uTint: {value: THREE.Color};
  uFogColor: {value: THREE.Color};
  uFogDensity: {value: number};
  uCamPos: {value: THREE.Vector3};
  uBeamDir: {value: THREE.Vector3};
  uBeamOn: {value: number};
  uAmbient: {value: number};
  uFogMul: {value: number};
  uTime: {value: number};
  uWave: {value: number};
};

// uniforms globais compartilhados (câmera, lanterna, névoa)
export const G = {
  uRes: {value: new THREE.Vector2(1080, 1920)},
  uFogColor: {value: new THREE.Color('#1C1C1C')},
  uFogDensity: {value: 0.032},
  uCamPos: {value: new THREE.Vector3()},
  uBeamDir: {value: new THREE.Vector3(0, 0, -1)},
  uBeamOn: {value: 1},
  uAmbient: {value: 0.2},
  uTime: {value: 0},
};

export const makeMat = (tex: THREE.Texture | null, opts: Partial<{emissive: number; shadow: boolean; wave: number; tint: string; fogMul: number}> = {}) => {
  const u = {
    map: {value: tex},
    uOpacity: {value: 1},
    uBlur: {value: 0},
    uMotion: {value: 0},
    uEmissive: {value: opts.emissive ?? 0},
    uSil: {value: 0},
    uShadow: {value: opts.shadow ? 1 : 0},
    uTint: {value: new THREE.Color(opts.tint ?? '#ffffff')},
    uWave: {value: opts.wave ?? 0},
    uFogMul: {value: opts.fogMul ?? 1},
    uRes: G.uRes,
    uFogColor: G.uFogColor,
    uFogDensity: G.uFogDensity,
    uCamPos: G.uCamPos,
    uBeamDir: G.uBeamDir,
    uBeamOn: G.uBeamOn,
    uAmbient: G.uAmbient,
    uTime: G.uTime,
  };
  const m = new THREE.ShaderMaterial({
    uniforms: u as unknown as Record<string, THREE.IUniform>,
    vertexShader: vert,
    fragmentShader: frag,
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  return m;
};
