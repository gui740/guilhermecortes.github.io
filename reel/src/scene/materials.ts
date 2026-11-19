import * as THREE from 'three';
// Material único para cartões: textura com alpha, blur em px de tela (entrada do texto + profundidade de campo), névoa, sombra.
export const globals = {
  fogColor: {value: new THREE.Color('#1C1C1C')},
  fogDensity: {value: 0.055},
  focusNear: {value: 3.6},
  focusFar: {value: 9.0},
  nearMax: {value: 22.0},
  farMax: {value: 0.0},
  pxScale: {value: 1.0},
  time: {value: 0},
};
const vert = /* glsl */ `
varying vec2 vUv; varying float vDepth;
uniform vec4 uvXform;
void main(){ vUv = uv*uvXform.xy + uvXform.zw; vec4 mv = modelViewMatrix*vec4(position,1.0); vDepth = -mv.z; gl_Position = projectionMatrix*mv; }`;
const frag = /* glsl */ `
uniform sampler2D map; uniform float hasMap; uniform vec3 color; uniform float opacity; uniform float blurPx;
uniform vec3 fogColor; uniform float fogDensity; uniform float focusNear; uniform float focusFar; uniform float nearMax; uniform float farMax;
uniform float shadow; uniform float dof; uniform float pxScale; uniform float fogAmt; uniform float additive;
varying vec2 vUv; varying float vDepth;
const vec2 P[12] = vec2[12](vec2(-0.326,-0.406),vec2(-0.840,-0.074),vec2(-0.696,0.457),vec2(-0.203,0.621),vec2(0.962,-0.195),vec2(0.473,-0.480),vec2(0.519,0.767),vec2(0.185,-0.893),vec2(0.507,0.064),vec2(0.896,0.412),vec2(-0.322,-0.933),vec2(-0.792,-0.598));
vec4 S(vec2 uv){ vec4 c = hasMap>0.5 ? texture2D(map, uv) : vec4(1.0); c.rgb *= c.a; return c; }
void main(){
  float coc = nearMax*clamp((focusNear - vDepth)/max(focusNear-0.5,0.01),0.0,1.0) + farMax*clamp((vDepth-focusFar)/22.0,0.0,1.0);
  float r = (blurPx + coc*dof)*pxScale;
  vec2 px = fwidth(vUv);
  vec4 c = S(vUv);
  if (r > 0.7) {
    vec4 acc = c; for (int i=0;i<12;i++){ acc += S(vUv + P[i]*px*r*(i<6?0.55:1.0)); }
    c = acc/13.0;
  }
  vec3 rgb = c.a>0.0001 ? c.rgb/c.a : vec3(0.0);
  float a = c.a;
  rgb *= color;
  if (shadow > 0.5) { rgb = vec3(0.04); a *= 0.5; }
  a *= opacity;
  float f = (1.0 - exp(-pow(fogDensity*vDepth, 2.0)))*fogAmt;
  rgb = mix(rgb, fogColor, f);
  if (additive > 0.5) { rgb *= a*(1.0-f); a = 1.0; }
  if (a < 0.003) discard;
  gl_FragColor = vec4(rgb, a);
}`;
export function cardMat(map: THREE.Texture | null, o: {color?: string; opacity?: number; dof?: number; shadow?: boolean; fog?: number; additive?: boolean; depthWrite?: boolean; side?: THREE.Side} = {}) {
  const m = new THREE.ShaderMaterial({
    uniforms: {
      map: {value: map}, hasMap: {value: map ? 1 : 0}, color: {value: new THREE.Color(o.color ?? '#ffffff')}, opacity: {value: o.opacity ?? 1}, blurPx: {value: 0},
      shadow: {value: o.shadow ? 1 : 0}, dof: {value: o.dof ?? 1}, fogAmt: {value: o.fog ?? 1}, additive: {value: o.additive ? 1 : 0}, uvXform: {value: new THREE.Vector4(1, 1, 0, 0)},
      ...globals,
    },
    vertexShader: vert, fragmentShader: frag, transparent: true, depthWrite: o.depthWrite ?? false, side: o.side ?? THREE.DoubleSide,
    blending: o.additive ? THREE.AdditiveBlending : THREE.NormalBlending,
  });
  return m;
}
// Tela de TV de tubo: chuvisco + still do filme + scanlines
const tvFrag = /* glsl */ `
uniform sampler2D still; uniform float stillMix; uniform float time; uniform float seed; uniform float power; uniform float opacity;
uniform vec3 fogColor; uniform float fogDensity; uniform float focusNear; uniform float pxScale;
varying vec2 vUv; varying float vDepth;
float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
void main(){
  vec2 uv = vUv; vec2 q = uv*2.0-1.0;
  float vig = smoothstep(1.25, 0.35, length(q*vec2(0.9,1.0)));
  float n = h(floor(uv*vec2(160.0,120.0)) + floor(time*24.0)*vec2(3.1,7.7) + seed);
  float roll = 0.04*sin(uv.y*3.0 + time*2.0);
  vec3 st = texture2D(still, vec2(uv.x + roll*0.05, uv.y)).rgb;
  float lum = mix(n*0.55+0.12, dot(st, vec3(0.333))*0.95 + n*0.08, stillMix);
  lum *= 0.8 + 0.2*sin(uv.y*420.0);
  lum *= vig*power;
  vec3 rgb = vec3(lum)*vec3(0.93,0.93,0.93);
  float f = 1.0 - exp(-pow(fogDensity*vDepth, 2.0));
  rgb = mix(rgb, fogColor, f*0.85);
  float rr = clamp((focusNear - vDepth)/focusNear,0.0,1.0);
  gl_FragColor = vec4(rgb, opacity*(1.0-rr*0.25));
}`;
export function tvMat(still: THREE.Texture, seed: number) {
  return new THREE.ShaderMaterial({
    uniforms: {still: {value: still}, stillMix: {value: 0}, seed: {value: seed}, power: {value: 1}, opacity: {value: 1}, uvXform: {value: new THREE.Vector4(1, 1, 0, 0)}, ...globals},
    vertexShader: vert, fragmentShader: tvFrag, transparent: true, depthWrite: false,
  });
}
// Pós-processamento: zoom blur (só nas travessias) + granulado + vinheta
export const postMat = new THREE.ShaderMaterial({
  uniforms: {tDiffuse: {value: null}, zoom: {value: 0}, time: {value: 0}, grain: {value: 0.07}, vig: {value: 0.7}, fade: {value: 1}},
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.0,1.0); }`,
  fragmentShader: /* glsl */ `
  uniform sampler2D tDiffuse; uniform float zoom; uniform float time; uniform float grain; uniform float vig; uniform float fade; varying vec2 vUv;
  float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
  void main(){
    vec2 c = vec2(0.5,0.52); vec2 d = vUv - c; vec3 acc = vec3(0.0);
    if (zoom > 0.001) { for (int i=0;i<14;i++){ float t = float(i)/13.0; acc += texture2D(tDiffuse, c + d*(1.0 - zoom*t)).rgb; } acc /= 14.0; }
    else acc = texture2D(tDiffuse, vUv).rgb;
    float g = h(vUv*vec2(1080.0,1920.0) + fract(time)*91.7) - 0.5;
    acc += g*grain;
    float v = smoothstep(0.95, 0.25, length(d*vec2(1.0,0.75)));
    acc = mix(acc*(1.0-vig), acc, v);
    acc = mix(vec3(0.11), acc, fade);
    gl_FragColor = vec4(acc, 1.0);
  }`,
  depthTest: false, depthWrite: false,
});
