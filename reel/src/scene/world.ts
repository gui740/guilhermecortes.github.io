import * as THREE from 'three';
import {CamPath, CAM_Y, VHS_START, FOCAL, ss, easeOutCubic} from './camera';
import {cardMat, tvMat, postMat, globals} from './materials';
import * as TX from './textures';
import {FILMS, HOOK_LINES, HOOKS, wordAt, KW_ALIASES, type Film, type TL, type Word} from '../content';
import screens from '../screens.json';

THREE.ColorManagement.enabled = false;
const FOV = 62;
const TAN_V = Math.tan(((FOV / 2) * Math.PI) / 180);
const HALF_W = 1.3; // meia largura do corredor
const SEG = 2.4; // módulo de prateleira
const NSEG = 30;
const ENTER = 6 / 30; // texto firma em 6 frames

export type Assets = {img: Record<string, HTMLImageElement | HTMLCanvasElement>};

const hash = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const clamp01 = (x: number) => Math.min(1, Math.max(0, x));

function texFrom(src: HTMLImageElement | HTMLCanvasElement, repeat = false) {
  const t = src instanceof HTMLCanvasElement ? new THREE.CanvasTexture(src) : new THREE.Texture(src);
  t.colorSpace = THREE.NoColorSpace; t.needsUpdate = true; t.anisotropy = 4;
  t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter; t.generateMipmaps = true;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; } else { t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; }
  return t;
}
type Card = THREE.Mesh<THREE.PlaneGeometry, THREE.ShaderMaterial> & {aspect: number};
const PLANE = new THREE.PlaneGeometry(1, 1);
function card(tex: THREE.Texture | null, aspect: number, o: Parameters<typeof cardMat>[1] = {}): Card {
  const m = new THREE.Mesh(PLANE, cardMat(tex, o)) as Card;
  m.aspect = aspect; m.frustumCulled = false; return m;
}
const U = (m: THREE.Mesh) => (m.material as THREE.ShaderMaterial).uniforms;

// Elemento agendado (entra vindo de trás no eixo Z, firma, fica, sai com a câmera passando)
type Sched = {
  keepDof?: boolean;
  obj: Card; shadow?: Card; tIn: number; tOut: number; enterDur?: number; exitDur?: number;
  // posição em espaço de tela da âncora: sx, sy (-1..1), d (profundidade), tamanho: h (fração da altura da tela) ou w (fração da largura)
  sx: number; sy: number; d: number; h?: number; w?: number; rot?: number;
  anchor: 'world' | 'cam'; anchorT: number; releaseT?: number; opacity?: number; grow?: boolean; fadeTo?: [number, number, number]; exitMode?: 'pass' | 'fade' | 'back';
  baseBlur?: number;
};

export class World {
  renderer: THREE.WebGLRenderer; scene = new THREE.Scene(); camera: THREE.PerspectiveCamera;
  rt: THREE.WebGLRenderTarget; postScene = new THREE.Scene(); postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  path: CamPath; tl: TL; words: Word[]; hook: string; W: number; H: number; tanH: number;
  sched: Sched[] = []; tex: Record<string, THREE.Texture> = {}; aspects: Record<string, number> = {};
  segs: any[] = []; walls: Card[] = []; ledges: Card[] = []; floor!: Card; ceil!: Card; dust!: THREE.Points; dustBase!: Float32Array;
  fogs: Card[] = []; curtains: {z: number; tp: number; strips: THREE.Group[]}[] = []; stationTVs: {screen: THREE.Mesh; film: Film; st: any; seed: number}[] = [];
  vhs1!: Card; vhs2!: Card; vhs1Shadow!: Card; signs: any[] = [];
  constructor(canvas: HTMLCanvasElement, W: number, H: number, assets: Assets, hook: string) {
    this.W = W; this.H = H; this.hook = hook; this.tanH = TAN_V * (W / H);
    const h = HOOKS[hook]; this.tl = h.tl; this.words = h.words; this.path = new CamPath(this.tl);
    this.renderer = new THREE.WebGLRenderer({canvas, antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance'});
    this.renderer.setPixelRatio(1); this.renderer.setSize(W, H, false);
    this.renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
    this.renderer.setClearColor(new THREE.Color('#1C1C1C'));
    this.rt = new THREE.WebGLRenderTarget(W, H, {samples: 0, colorSpace: THREE.NoColorSpace});
    this.camera = new THREE.PerspectiveCamera(FOV, W / H, 0.05, 120);
    globals.pxScale.value = W / 1080;
    const q = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), postMat); q.frustumCulled = false; this.postScene.add(q);
    for (const [k, v] of Object.entries(assets.img)) { this.tex[k] = texFrom(v); this.aspects[k] = (v as any).width / (v as any).height; }
    this.buildCorridor();
    if (hook === 'cover') this.buildCover(); else { this.buildHook(); this.buildStations(); this.buildOutro(); this.buildCurtains(); this.buildSigns(); }
  }
  // ---------- helpers de textura gerada ----------
  gen(key: string, f: () => TX.Tex, repeat = false) {
    if (!this.tex[key]) { const t = f(); this.tex[key] = texFrom(t.canvas, repeat); this.aspects[key] = t.w / t.h; }
    return this.tex[key];
  }
  add(o: THREE.Object3D) { this.scene.add(o); return o; }
  // ---------- cenário fixo ----------
  buildCorridor() {
    // prateleiras: atlas com 4 módulos lado a lado
    const atlas = document.createElement('canvas'); atlas.width = 4096; atlas.height = 1280;
    const g = atlas.getContext('2d')!;
    for (let i = 0; i < 4; i++) g.drawImage(TX.shelfTex(100 + i).canvas, i * 1024, 0);
    const shelfT = texFrom(atlas, true);
    const LEN = 84;
    for (const side of [-1, 1]) {
      const w = card(shelfT, LEN / 3.0, {fog: 1, color: '#bdbdbd'});
      w.scale.set(LEN, 3.0, 1); w.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2; w.position.set(side * (HALF_W + 0.1), 1.5, 0);
      (w as any).side = side; w.renderOrder = -10; this.walls.push(this.add(w) as Card);
      for (let r = 0; r < 5; r++) {
        const yTop = (r + 1) * 0.6 - 0.6 * 0.07 + 0.0; // topo da tábua coincide com a textura
        const top = card(null, 1, {color: '#5c5c5c'}); top.scale.set(LEN, 0.16, 1); top.rotation.set(-Math.PI / 2, 0, side < 0 ? Math.PI / 2 : -Math.PI / 2);
        top.position.set(side * (HALF_W + 0.02), 3.0 - yTop + 0.0, 0); top.renderOrder = -9; (top as any).side = side;
        const edge = card(null, 1, {color: '#8c8c8c'}); edge.scale.set(LEN, 0.035, 1); edge.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
        edge.position.set(side * (HALF_W - 0.06), 3.0 - yTop - 0.0175, 0); edge.renderOrder = -8; (edge as any).side = side;
        this.ledges.push(this.add(top) as Card, this.add(edge) as Card);
      }
    }
    const fl = card(texFrom(TX.floorTex().canvas, true), 1, {}); fl.scale.set(HALF_W * 2 + 0.4, LEN, 1); fl.rotation.x = -Math.PI / 2; fl.position.y = 0; fl.renderOrder = -12; this.floor = this.add(fl) as Card;
    const ce = card(null, 1, {color: '#161616'}); ce.scale.set(HALF_W * 2 + 0.4, LEN, 1); ce.rotation.x = Math.PI / 2; ce.position.y = 3.3; ce.renderOrder = -12; this.ceil = this.add(ce) as Card;
    // segmentos recicláveis
    const glow = this.gen('glow', () => TX.glowTex());
    const glowY = this.gen('glowY', () => TX.glowTex('242,230,58'));
    const neonP0 = this.gen('neonP0', () => TX.neonTex('play', false)), neonP1 = this.gen('neonP1', () => TX.neonTex('play', true));
    const neonS0 = this.gen('neonS0', () => TX.neonTex('star', false)), neonS1 = this.gen('neonS1', () => TX.neonTex('star', true));
    const tvKeys = ['tv_admiral', 'tv_discarded', 'tv_mitsubishi', 'tv_sylvania'];
    const vcrKeys = ['vcr_jvc', 'vcr_magnavox', 'vcr_panasonic'];
    const tapeKeys = ['vhs_back', 'vhs_front', 'vhs_kaseta', 'vhs_tdk'];
    for (let i = 0; i < NSEG; i++) {
      const grp = new THREE.Group(); this.add(grp);
      const posts = [-1, 1].map((s) => { const p = card(null, 1, {color: '#3a3a3a'}); p.scale.set(0.07, 3.05, 1); p.position.set(s * (HALF_W - 0.02), 1.52, 0); grp.add(p); return p; });
      const light = card(null, 1, {color: '#EDEDED', fog: 0.8}); light.scale.set(0.12, 1.5, 1); light.rotation.x = Math.PI / 2; light.position.set(0, 3.27, 0); grp.add(light);
      const lglow = card(glow, 1, {additive: true, opacity: 0.35, fog: 0.9}); lglow.scale.set(1.6, 2.6, 1); lglow.rotation.x = Math.PI / 2; lglow.position.set(0, 3.2, 0); grp.add(lglow);
      // pilha de TVs
      const stack = new THREE.Group(); grp.add(stack);
      const vcr = card(this.tex[vcrKeys[0]], this.aspects[vcrKeys[0]]); stack.add(vcr);
      const tv = card(this.tex[tvKeys[0]], this.aspects[tvKeys[0]]); stack.add(tv);
      const scr = new THREE.Mesh(PLANE, tvMat(this.tex['ghost_0'] ?? null as any, i * 1.7)); scr.frustumCulled = false; stack.add(scr);
      const tvShadow = card(this.tex[tvKeys[0]], 1, {shadow: true}); stack.add(tvShadow);
      // fita caída no chão
      const tape = card(this.tex[tapeKeys[0]], this.aspects[tapeKeys[0]]); tape.rotation.x = -Math.PI / 2; grp.add(tape);
      // pipoca
      const pop = card(this.tex['pop_bucket'], this.aspects['pop_bucket']); grp.add(pop);
      // neon (apagado, falha de vez em quando)
      const neon = card(neonP0, 1, {fog: 0.8}); grp.add(neon);
      const nglow = card(glowY, 1, {additive: true, opacity: 0, fog: 0.8}); grp.add(nglow);
      this.segs.push({grp, posts, light, lglow, stack, vcr, tv, scr, tvShadow, tape, pop, neon, nglow, neonTex: [neonP0, neonP1, neonS0, neonS1], tvKeys, vcrKeys, tapeKeys, n: -9999});
    }
    // névoa rolando
    for (let i = 0; i < 10; i++) {
      const f = card(this.gen('cloud' + (i % 3), () => TX.cloudTex(40 + (i % 3))), 2, {opacity: 0.16, dof: 0});
      f.scale.set(4.2, 1.6, 1); this.fogs.push(this.add(f) as Card);
    }
    // poeira
    const N = 420; const pos = new Float32Array(N * 3); this.dustBase = new Float32Array(N * 4);
    for (let i = 0; i < N; i++) { this.dustBase[i * 4] = hash(i * 3.1); this.dustBase[i * 4 + 1] = hash(i * 7.3); this.dustBase[i * 4 + 2] = hash(i * 1.9); this.dustBase[i * 4 + 3] = hash(i * 5.7); }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const pm = new THREE.PointsMaterial({color: 0xededed, size: 0.014, transparent: true, opacity: 0.55, depthWrite: false, sizeAttenuation: true, map: this.tex['glow'], alphaTest: 0.01});
    this.dust = new THREE.Points(geo, pm); this.dust.frustumCulled = false; this.add(this.dust);
    this.scene.fog = new THREE.FogExp2(0x1c1c1c, globals.fogDensity.value);
  }
  // ---------- agenda ----------
  push(s: Sched) {
    this.sched.push(s); this.add(s.obj); if (s.shadow) this.add(s.shadow);
    if (!(s as any).keepDof) { U(s.obj).dof.value = 0; if (s.shadow) U(s.shadow).dof.value = 0; }
    s.obj.visible = false; if (s.shadow) s.shadow.visible = false;
    return s;
  }
  kwCard(line: any, key: string) {
    const t = this.gen(key, () => TX.keywordTex(line)); return card(t, this.aspects[key], {});
  }
  imgCard(key: string, shadow = true) {
    const c = card(this.tex[key], this.aspects[key], {});
    const s = shadow ? card(this.tex[key], this.aspects[key], {shadow: true}) : undefined;
    return [c, s] as const;
  }
  buildHook() {
    const tl = this.tl; const cues = HOOK_LINES[this.hook] ?? HOOK_LINES.g;
    const ys = [0.47, 0.24, -0.07];
    const ws = this.hook === 'gB' ? [0.56, 0.76, 0.42] : [0.76, 0.72, 0.56];
    let prev = -1;
    cues.forEach((c, i) => {
      let tIn = wordAt(this.words, 'g', c.word, 0.4 + i * 0.7);
      tIn = Math.max(tIn - 0.08, prev + 0.5); prev = tIn;
      const m = this.kwCard(c.line, `hook_${this.hook}_${i}`);
      this.push({obj: m, tIn, tOut: tl.hookEnd + 0.45, sx: -0.07, sy: ys[i], d: 2.4, w: ws[i], anchor: 'cam', anchorT: 0, releaseT: tl.hookEnd, exitMode: 'pass', exitDur: 0.5});
      m.renderOrder = 100; m.material.depthTest = false;
    });
    // fita VHS do close inicial
    const vt = this.tex['vhs_front']; const a = this.aspects['vhs_front'];
    this.vhs1 = this.add(card(vt, a, {dof: 0})) as Card; this.vhs1.scale.set(0.6, 0.6 / a, 1);
    this.vhs1Shadow = this.add(card(vt, a, {shadow: true, dof: 0})) as Card; this.vhs1Shadow.scale.set(0.6, 0.6 / a, 1);
  }
  stationAnchor(s: any) { return this.path.z(s.titleIn + 0.8); }
  buildStations() {
    const tl = this.tl;
    tl.stations.forEach((s: any, i: number) => {
      const f = FILMS[i]; const key = `f${f.n}`;
      const red = !!f.red;
      const aliases = KW_ALIASES[f.kwA.word] ?? [f.kwA.word];
      let kwAt = s.aIn + 1.4;
      for (const al of aliases) { const t = wordAt(this.words, `${key}a`, al, -1); if (t > 0) { kwAt = t; break; } }
      const kwBt = Math.min(Math.max(wordAt(this.words, `${key}b`, f.kwB.word, s.bIn + 0.6), s.bIn + 0.25), s.logoIn - 1.55);
      const titleIn = s.titleIn - 0.22; // entra na pausa, firma no nome
      const endFade = s.end - 0.05;
      const AT = s.titleIn + 0.8;
      // número gigante no fundo (só ele), cresce
      const num = card(this.gen('num' + f.n, () => TX.numberTex(f.n)), 0, {dof: 0});
      num.aspect = this.aspects['num' + f.n];
      this.push({obj: num, tIn: s.numberIn, tOut: titleIn - 0.1, enterDur: 1.2, exitDur: 0.6, sx: 0.15, sy: 0.36, d: 13, h: 0.62, anchor: 'world', anchorT: AT, grow: true, fadeTo: [kwAt - 0.2, kwAt + 0.4, 0.3], exitMode: 'fade'});
      // camadas do filme: cenário -> principal -> objeto de primeiro plano
      const [setC, setS] = this.imgCard(f.id + '_set');
      this.push({obj: setC, shadow: setS, tIn: s.aIn, tOut: endFade, enterDur: 0.45, sx: 0.58, sy: 0.14, d: 7.0, h: 0.24, rot: -0.03, anchor: 'world', anchorT: AT, exitMode: 'fade', exitDur: 0.5});
      const [mainC, mainS] = this.imgCard(f.id + '_main');
      this.push({obj: mainC, shadow: mainS, tIn: s.aIn + 0.5, tOut: endFade + 0.1, enterDur: 0.45, sx: 0.42, sy: -0.11, d: 4.9, h: 0.50, anchor: 'world', anchorT: AT, exitMode: 'fade', exitDur: 0.5});
      const fgKey = f.fgKit ? 'vhs_kaseta' : f.id + '_fg';
      const [fgC] = this.imgCard(fgKey, false);
      this.push({keepDof: true, obj: fgC, tIn: s.aIn + 1.0, tOut: endFade, enterDur: 0.45, sx: -0.86, sy: -0.88, d: 2.0, h: f.fgKit ? 0.24 : 0.46, rot: f.fgKit ? 0.35 : 0.06, anchor: 'world', anchorT: AT, exitMode: 'fade', exitDur: 0.5});
      // palavra-chave da frase A
      const kA = this.kwCard(f.kwA, `kwA${f.n}`);
      this.push({obj: kA, tIn: Math.max(kwAt - 0.06, s.aIn + 1.5), tOut: titleIn - 0.3, exitDur: 0.35, sx: -0.06, sy: 0.44, d: 3.3, w: 0.78, anchor: 'world', anchorT: AT, exitMode: 'pass'});
      // estrela atrás do personagem (só na revelação)
      const star = card(this.gen('star', () => TX.starTex()), 1, {});
      this.push({obj: star, tIn: titleIn + 0.12, tOut: kwBt - 0.3, enterDur: 0.25, sx: 0.56, sy: 0.30, d: 6.4, h: 0.26, anchor: 'world', anchorT: AT, exitMode: 'fade', exitDur: 0.4});
      // TÍTULO (fica até o fim da estação; a câmera passa por ele na travessia)
      const tcol = red ? TX.C.red : TX.C.light;
      const tt = card(this.gen('title' + f.n, () => TX.titleTex(f.title, tcol)), 0, {});
      tt.aspect = this.aspects['title' + f.n];
      const tw = Math.min(0.80, 0.24 * (this.H / this.W) * tt.aspect * 1.0);
      this.push({obj: tt, tIn: titleIn, tOut: endFade + 0.15, sx: -0.08, sy: 0.50, d: 5.6, w: tw, anchor: 'world', anchorT: AT, exitMode: 'fade', exitDur: 0.5});
      // etiqueta ano · país (entra 0,5 s depois, sai antes da palavra B)
      const lb = card(this.gen('label' + f.n, () => TX.labelTex(f.label)), 0, {}); lb.aspect = this.aspects['label' + f.n];
      this.push({obj: lb, tIn: titleIn + 0.5, tOut: kwBt - 0.3, sx: -0.40, sy: 0.25, d: 4.6, w: 0.52, rot: 0.06, anchor: 'world', anchorT: AT, exitMode: 'back', exitDur: 0.3});
      // palavra-chave da frase B
      const kB = this.kwCard(f.kwB, `kwB${f.n}`);
      this.push({obj: kB, tIn: kwBt, tOut: s.logoIn - 0.1, exitDur: 0.3, sx: -0.22, sy: -0.06, d: 3.1, w: 0.56, anchor: 'world', anchorT: AT, exitMode: 'pass'});
      // selo PRIME VIDEO + linha tracejada
      const lg = card(this.tex['prime_logo'], this.aspects['prime_logo'], {});
      this.push({obj: lg, tIn: s.logoIn, tOut: endFade + 0.15, sx: -0.36, sy: 0.12, d: 4.3, w: 0.54, anchor: 'world', anchorT: AT, exitMode: 'fade', exitDur: 0.5});
      const ds = card(this.gen('dash', () => TX.dashTex()), 0, {opacity: 0.85}); ds.aspect = this.aspects['dash'];
      this.push({obj: ds, tIn: s.logoIn + 0.1, tOut: endFade + 0.15, sx: -0.60, sy: 0.28, d: 4.35, w: 0.12, rot: Math.PI / 2, anchor: 'world', anchorT: AT, exitMode: 'fade', exitDur: 0.5});
      // TVs de tubo mais próximas mostram stills do filme atual
      const zA = this.path.z(AT);
      for (const side of [-1, 1]) this.stationTVs.push({screen: null as any, film: f, st: {...s, zA, side}, seed: i * 10 + side});
    });
  }
  buildOutro() {
    const tl = this.tl; const t0 = tl.outroStart; const out = tl.diveStart - 0.35;
    const qT = wordAt(this.words, 'fe1', 'qual', t0 + 2.6);
    const items: [string, number, number, number, number][] = [['title3', -0.30, 0.48, 3.2, 0.50], ['title2', 0.22, 0.28, 4.2, 0.48], ['title1', -0.22, 0.07, 5.2, 0.44]];
    items.forEach(([k, sx, sy, d, w], i) => {
      const c = card(this.tex[k], this.aspects[k], {});
      this.push({obj: c, tIn: t0 + 0.95 + i * 0.12, tOut: out + 0.1 * i, sx, sy, d, w, anchor: 'cam', anchorT: 0, releaseT: out, exitMode: 'pass', exitDur: 0.55});
    });
    const hd = card(this.gen('handle', () => TX.smallTex('@talking_horror', '"Special Elite"', 64, TX.C.light)), 0, {}); hd.aspect = this.aspects['handle'];
    this.push({obj: hd, tIn: t0 + 1.6, tOut: out, sx: 0.0, sy: -0.44, d: 3.0, w: 0.40, anchor: 'cam', anchorT: 0, releaseT: out, exitMode: 'pass', exitDur: 0.5});
    const qq = card(this.gen('question', () => TX.questionTex([{t: 'QUAL CÊ VAI VER ', c: TX.C.light}, {t: 'PRIMEIRO?', c: TX.C.yellow}])), 0, {}); qq.aspect = this.aspects['question'];
    this.push({obj: qq, tIn: Math.max(qT - 0.05, t0 + 2.1), tOut: out, sx: -0.04, sy: -0.24, d: 3.0, w: 0.80, anchor: 'cam', anchorT: 0, releaseT: out, exitMode: 'pass', exitDur: 0.5});
    for (const s of this.sched) if (s.anchor === 'cam') { s.obj.renderOrder = 100; s.obj.material.depthTest = false; }
    const vt = this.tex['vhs_front']; const a = this.aspects['vhs_front'];
    this.vhs2 = this.add(card(vt, a, {dof: 0})) as Card; this.vhs2.scale.set(0.6, 0.6 / a, 1);
  }
  buildCurtains() {
    const st = this.gen('strip', () => TX.stripTex());
    for (const tr of this.tl.travs) {
      const tp = tr.start + 0.75; const z = this.path.z(tp);
      const strips: THREE.Group[] = []; const n = 15; const w = (HALF_W * 2) / n;
      for (let i = 0; i < n; i++) {
        const pivot = new THREE.Group(); pivot.position.set(-HALF_W + w * (i + 0.5), 3.05, z);
        const m = card(st, 0.1, {opacity: 0.30, dof: 1}); m.scale.set(w * 1.04, 3.0, 1); m.position.y = -1.5; pivot.add(m);
        this.add(pivot); strips.push(pivot);
      }
      this.curtains.push({z, tp, strips});
    }
  }
  buildSigns() {
    const names = [['TERROR', false], ['LANÇAMENTOS', true], ['TERROR', false]] as const;
    this.tl.travs.forEach((tr: any, i: number) => {
      const [txt, yel] = names[i % 3];
      const k = 'sign' + i; const m = card(this.gen(k, () => TX.signTex(txt, yel)), 0, {}); m.aspect = this.aspects[k];
      const z = this.path.z(tr.start + 0.75) - 3.2; m.scale.set(0.9, 0.9 / m.aspect, 1); m.position.set(i % 2 ? -0.6 : 0.6, 2.72, z);
      this.add(m); this.signs.push({m, z, t0: tr.start + 0.3, t1: tr.end + 0.1} as any);
    });
  }
  buildCover() {
    const items = [
      {line: {big: '3 TERRORES'}, sy: 0.50, w: 0.88},
      {line: {big: 'ESCONDIDOS', color: 'yellow'}, sy: 0.24, w: 0.86},
      {line: {small: 'no seu', big: 'PRIME'}, sy: -0.02, w: 0.62},
    ];
    items.forEach((it, i) => {
      const m = this.kwCard(it.line, 'cover' + i);
      this.push({obj: m, tIn: -1, tOut: 99, sx: -0.02, sy: it.sy, d: 2.4, w: it.w, anchor: 'cam', anchorT: 0});
      m.renderOrder = 100; m.material.depthTest = false;
    });
    const lg = card(this.tex['prime_logo'], this.aspects['prime_logo'], {});
    this.push({obj: lg, tIn: -1, tOut: 99, sx: 0.30, sy: -0.36, d: 2.4, w: 0.50, anchor: 'cam', anchorT: 0}); lg.renderOrder = 101; lg.material.depthTest = false;
    const [v] = this.imgCard('vhs_front', false);
    this.push({obj: v, tIn: -1, tOut: 99, sx: -0.22, sy: -0.80, d: 1.25, w: 1.6, rot: 0.16, anchor: 'cam', anchorT: 0, baseBlur: 0}); v.renderOrder = 99; v.material.depthTest = false;
    U(v).dof.value = 0;
  }
  // ---------- atualização por frame ----------
  camPose(t: number) {
    if (this.hook === 'cover') return {x: 0, y: CAM_Y, z: -14, lookX: 0, lookY: CAM_Y, lookZ: -14 - FOCAL, roll: 0};
    return this.path.pose(t);
  }
  placeAt(o: THREE.Object3D, base: {x: number; y: number; z: number}, sx: number, sy: number, d: number) {
    o.position.set(base.x + sx * d * this.tanH, base.y + sy * d * TAN_V, base.z - d);
  }
  updateSched(t: number, cam: {x: number; y: number; z: number}) {
    for (const s of this.sched) {
      const vis = t >= s.tIn && t < s.tOut + (s.exitDur ?? 0.35);
      s.obj.visible = vis; if (s.shadow) s.shadow.visible = vis;
      if (!vis) continue;
      const ed = s.enterDur ?? ENTER; const xd = s.exitDur ?? 0.35;
      const e = easeOutCubic(clamp01((t - s.tIn) / ed));
      const x = clamp01((t - s.tOut) / xd);
      let d = s.d + (1 - e) * 1.2; // vem de trás no eixo Z
      let op = (0.4 + 0.6 * e) * (s.opacity ?? 1);
      let blur = 12 * (1 - e) + (s.baseBlur ?? 0);
      let sc = s.grow ? 0.6 + 0.4 * easeOutCubic(clamp01((t - s.tIn) / ed)) : 0.9 + 0.1 * e;
      if (t < s.tIn + ed && !s.grow) op = op * clamp01((t - s.tIn) / (ed * 0.5) + 0.4);
      if (s.grow) { op = clamp01((t - s.tIn) / 0.5) * 0.92; blur = 6 * (1 - e); d = s.d + (1 - e) * 2.0; }
      if (s.fadeTo) { const [a, b, v] = s.fadeTo; op *= lerp(1, v, ss(a, b, t)); }
      if (x > 0) {
        if (s.exitMode === 'pass') { const k = x * x; d = lerp(d, 0.25, k); op *= 1 - ss(0.45, 1, x); blur += 10 * x; }
        else if (s.exitMode === 'back') { d += x * 2.0; op *= 1 - x; blur += 8 * x; }
        else { op *= 1 - x; }
      }
      // âncora
      let base: {x: number; y: number; z: number};
      if (s.anchor === 'cam') {
        const tt = s.releaseT !== undefined ? Math.min(t, s.releaseT) : t;
        const p = this.camPose(tt);
        base = {x: p.x, y: p.y, z: p.z};
        if (s.releaseT !== undefined && t > s.releaseT) {
          // liberado: a câmera avança e passa por ele
          d = d; // posição fica no mundo
        }
      } else {
        base = {x: 0, y: CAM_Y, z: this.path.z(s.anchorT)};
      }
      const hgt = s.h !== undefined ? s.h * 2 * s.d * TAN_V : (s.w! * 2 * s.d * this.tanH) / s.obj.aspect;
      const wid = hgt * s.obj.aspect;
      const kz = d / s.d; // mantém o tamanho angular coerente com a entrada vinda de trás
      this.placeAt(s.obj, base, s.sx * (s.d / d), s.sy * (s.d / d), d);
      if (s.anchor === 'world' || (s.releaseT !== undefined && t > s.releaseT) || s.anchor === 'cam') {
        // posição real em mundo para âncoras de câmera já liberadas usa a pose congelada
      }
      s.obj.scale.set(wid * sc, hgt * sc, 1);
      s.obj.rotation.set(0, 0, s.rot ?? 0);
      const u = U(s.obj); u.opacity.value = op; u.blurPx.value = blur;
      if (s.shadow) {
        s.shadow.position.copy(s.obj.position); s.shadow.position.x += wid * 0.025; s.shadow.position.y -= hgt * 0.03; s.shadow.position.z -= 0.25;
        s.shadow.scale.copy(s.obj.scale); s.shadow.rotation.copy(s.obj.rotation);
        const us = U(s.shadow); us.opacity.value = op * 0.9; us.blurPx.value = 14 + blur;
      }
      void kz;
    }
  }
  updateCorridor(t: number, cam: {x: number; y: number; z: number}, camZ: number) {
    const LEN = 84; const zc = camZ - LEN / 2 + 8;
    for (const w of this.walls) {
      w.position.z = zc; const side = (w as any).side;
      // atlas de 4 módulos (9,6 u) ancorado no mundo
      const rep = LEN / (SEG * 4); const start = zc + LEN / 2; // z do lado +x local
      const u = U(w).uvXform.value;
      if (side < 0) { u.set(rep, 1, -start / (SEG * 4), 0); } else { u.set(-rep, 1, (LEN - start) / (SEG * 4), 0); }
    }
    for (const l of this.ledges) l.position.z = zc;
    this.floor.position.z = zc; U(this.floor).uvXform.value.set(2, LEN / 1.6, 0, -(zc + LEN / 2) / 1.6);
    this.ceil.position.z = zc;
    // segmentos reciclados (o que passa da câmera volta no fundo)
    const first = Math.floor(-(camZ + 3) / SEG);
    for (let k = 0; k < NSEG; k++) {
      const n = first + k; const sg = this.segs[((n % NSEG) + NSEG) % NSEG];
      const z = -n * SEG;
      sg.grp.position.z = z;
      if (sg.n !== n) this.assignSeg(sg, n);
      // vida discreta
      const flick = hash(n * 9.1) < 0.12 ? (Math.sin(t * 23 + n) > 0.2 && Math.sin(t * 3.1 + n * 2) > 0.6 ? 0.15 : 1) : 1;
      U(sg.light).opacity.value = flick; U(sg.lglow).opacity.value = 0.16 * flick;
      if (sg.hasNeon) {
        const ph = (t * 0.23 + hash(n * 4.4)) % 1; const lit = ph < 0.07 && Math.sin(t * 40 + n) > -0.3;
        U(sg.neon).map.value = sg.neonTex[(sg.neonKind ? 2 : 0) + (lit ? 1 : 0)]; U(sg.nglow).opacity.value = lit ? 0.5 : 0;
      }
      if (sg.hasTV) {
        const um = (sg.scr.material as THREE.ShaderMaterial).uniforms; um.time.value = t;
        // TVs perto de uma estação mostram stills do filme atual
        let mix = 0; let still: THREE.Texture | null = null; let power = 0.85 + 0.15 * Math.sin(t * 2.3 + n);
        this.tl.stations?.forEach((s: any, i: number) => {
          const zA = this.path.z(s.titleIn + 0.8); const near = Math.abs(z - (zA - 3.6)) < 7 && t > s.numberIn - 1.5 && t < s.end + 1.0;
          if (near) { mix = 1; const f = FILMS[i]; const idx = Math.floor((t - s.start) / 1.3 + hash(n) * 6) % 6; still = this.tex[`${f.id}_${(idx + 6) % 6}`]; }
          if (s.silence && t >= s.silence[0] && t < s.silence[1]) power = 0.0;
        });
        um.stillMix.value = mix; if (still) um.still.value = still; um.power.value = power;
      }
    }
    // névoa rolando
    this.fogs.forEach((f, i) => {
      const span = 26; const zz = camZ - 2 - ((i * 2.7 + 1000 - camZ * 0) % span);
      const zw = Math.floor((camZ - 2 - zz) / span) * 0; void zw;
      const baseZ = -i * 2.6; const rel = ((camZ - baseZ) % span + span) % span; const z = camZ - 1.5 - (span - rel);
      f.position.set(Math.sin(t * 0.05 + i) * 0.6 + (i % 2 ? 0.4 : -0.4), i % 3 === 0 ? 1.7 : 0.35, z);
      f.rotation.set(0, 0, 0); U(f).opacity.value = 0.06 + 0.03 * Math.sin(t * 0.3 + i);
    });
    // poeira
    const P = (this.dust.geometry.attributes.position as THREE.BufferAttribute); const arr = P.array as Float32Array; const B = this.dustBase;
    for (let i = 0; i < arr.length / 3; i++) {
      const bx = B[i * 4], by = B[i * 4 + 1], bz = B[i * 4 + 2], bs = B[i * 4 + 3];
      const x = -HALF_W + ((bx * 2.6 + Math.sin(t * 0.2 + bs * 6) * 0.1 + t * 0.01) % 1 + 1) % 1 * 2.6;
      const y = 0.2 + (((by + t * 0.008 * (0.5 + bs)) % 1) + 1) % 1 * 3.0;
      const span = 14; const wz = -bz * span; const rel = (((camZ - wz) % span) + span) % span; const z = camZ - 0.4 - (span - rel);
      arr[i * 3] = x; arr[i * 3 + 1] = y; arr[i * 3 + 2] = z;
    }
    P.needsUpdate = true;
  }
  assignSeg(sg: any, n: number) {
    sg.n = n; const r = (k: number) => hash(n * 13.37 + k * 7.77);
    // pilha de TVs: em segmentos sorteados + garantidas ao lado de cada estação
    let tvSide = 0; let forceStill = false;
    const zSeg = -n * SEG;
    let stationSeg = false;
    this.tl.stations?.forEach((s: any) => { const zA = this.path.z(s.titleIn + 0.8); if (Math.abs(zSeg - (zA - 3.6)) < SEG / 2) { tvSide = -1; forceStill = true; } if (zSeg < zA + 1 && zSeg > zA - 9) stationSeg = true; });
    if (!tvSide && !stationSeg && r(2) < 0.32) tvSide = r(3) < 0.5 ? -1 : 1;
    sg.hasTV = !!tvSide; sg.stack.visible = !!tvSide;
    if (tvSide) {
      const tk = sg.tvKeys[Math.floor(r(4) * 4)]; const vk = sg.vcrKeys[Math.floor(r(5) * 3)];
      const tvW = 0.78 + r(6) * 0.2; const ta = this.aspects[tk]; const va = this.aspects[vk];
      const vcrW = 0.8; const vcrH = vcrW / va;
      U(sg.vcr).map.value = this.tex[vk]; sg.vcr.scale.set(vcrW, vcrH, 1); sg.vcr.position.set(0, vcrH / 2, 0);
      const tvH = tvW / ta; U(sg.tv).map.value = this.tex[tk]; sg.tv.scale.set(tvW, tvH, 1); sg.tv.position.set(0, vcrH + tvH / 2 - 0.01, 0.002);
      U(sg.tvShadow).map.value = this.tex[tk]; sg.tvShadow.scale.set(tvW, tvH, 1); sg.tvShadow.position.set(0.03, vcrH + tvH / 2 - 0.04, -0.06);
      const sr = (screens as any)[tk] as number[];
      const sw = (sr[2] - sr[0]) * tvW, sh = (sr[3] - sr[1]) * tvH;
      const cx = (sr[0] + sr[2]) / 2 - 0.5, cy = 0.5 - (sr[1] + sr[3]) / 2;
      sg.scr.scale.set(sw, sh, 1); sg.scr.position.set(cx * tvW, vcrH + tvH / 2 - 0.01 + cy * tvH, 0.006);
      sg.stack.position.set(tvSide * (HALF_W - (forceStill ? 0.36 : 0.42) - r(7) * 0.06), 0, forceStill ? 0 : (r(8) - 0.5) * 0.6);
      sg.stack.rotation.y = -tvSide * (0.42 + r(9) * 0.15);
      sg.forceStill = forceStill;
      if (forceStill) { const st = this.tl.stations.find((q: any) => Math.abs(zSeg - (this.path.z(q.titleIn + 0.8) - 3.6)) < SEG / 2); if (st) sg.stack.position.z = (this.path.z(st.titleIn + 0.8) - 3.6) - zSeg; }
    }
    // fita caída no chão
    sg.tape.visible = r(10) < 0.45;
    if (sg.tape.visible) {
      const k = sg.tapeKeys[Math.floor(r(11) * 4)]; const a = this.aspects[k]; U(sg.tape).map.value = this.tex[k];
      sg.tape.scale.set(0.34, 0.34 / a, 1); sg.tape.position.set((r(12) - 0.5) * 1.6, 0.012, (r(13) - 0.5) * 1.8); sg.tape.rotation.set(-Math.PI / 2, 0, r(14) * 6.28);
    }
    sg.pop.visible = r(15) < 0.1 && !tvSide;
    if (sg.pop.visible) { const s = r(16) < 0.5 ? -1 : 1; sg.pop.scale.set(0.42, 0.42 / this.aspects['pop_bucket'], 1); sg.pop.position.set(s * (HALF_W - 0.35), 0.21, 0.2); sg.pop.rotation.set(0, -s * 0.5, 0); }
    sg.hasNeon = r(17) < 0.14; sg.neon.visible = sg.nglow.visible = sg.hasNeon;
    if (sg.hasNeon) { const s = r(18) < 0.5 ? -1 : 1; sg.neonKind = r(19) < 0.5 ? 1 : 0; sg.neon.scale.set(0.55, 0.55, 1); sg.neon.position.set(s * (HALF_W - 0.12), 3.0, 0.3); sg.neon.rotation.set(0, -s * 1.0, 0); sg.nglow.scale.set(1.4, 1.4, 1); sg.nglow.position.copy(sg.neon.position); sg.nglow.rotation.copy(sg.neon.rotation); }
  }
  updateCurtains(t: number, camZ: number) {
    for (const c of this.curtains) {
      const dz = camZ - c.z; const near = dz < 3.2 && dz > -2.5 && t > c.tp - 1.0 && t < c.tp + 1.6; c.strips.forEach((p) => (p.visible = near));
      if (!near) continue;
      const fo = clamp01((3.2 - dz) / 1.2) * clamp01((dz + 2.5) / 1.0);
      c.strips.forEach((p) => { U(p.children[0] as THREE.Mesh).opacity.value = 0.30 * fo; });
      c.strips.forEach((p, i) => {
        const tp = c.tp + (Math.abs(p.position.x) * 0.02);
        const dx = 1 - Math.min(1, Math.abs(p.position.x) / (HALF_W * 1.1));
        let a: number;
        if (t < tp) a = -1.25 * (0.4 + 0.6 * dx) * ss(tp - 0.1, tp, t);
        else { const u = t - tp; a = -1.25 * (0.4 + 0.6 * dx) * Math.exp(-u * 2.6) * Math.cos(u * (7 + (i % 3))); }
        p.rotation.set(a, 0, Math.sin(i * 1.7 + t * 2) * 0.03 * (t > tp ? Math.exp(-(t - tp)) : 0));
      });
    }
  }
  render(t: number) {
    const p = this.camPose(t);
    const cam = this.camera; cam.position.set(p.x, p.y, p.z); cam.up.set(Math.sin(p.roll), Math.cos(p.roll), 0); cam.lookAt(p.lookX, p.lookY, p.lookZ);
    const camZ = this.hook === 'cover' ? -14 : this.path.z(t);
    globals.time.value = t;
    // névoa: degradê lento; vermelho na revelação do filme 1
    const st1 = this.tl.stations[2];
    const redAmt = this.hook === 'cover' ? 0 : ss(st1.titleIn, st1.titleIn + 1.4, t) * (1 - ss(st1.end - 0.2, this.tl.outroStart + 1.8, t));
    const fog = new THREE.Color('#1C1C1C').lerp(new THREE.Color('#F23B3B'), 0.26 * redAmt);
    globals.fogColor.value.copy(fog); (this.scene.fog as THREE.FogExp2).color.copy(fog); this.renderer.setClearColor(fog);
    // foco: na estação (~5 u); nas travessias o foco vai mais longe
    globals.focusNear.value = 4.2; globals.focusFar.value = 10.0;
    this.updateCorridor(t, p, camZ);
    if (this.hook !== 'cover') {
      this.updateCurtains(t, camZ);
      for (const sg of this.signs as any[]) sg.m.visible = t > sg.t0 && t < sg.t1;
      // fita do close inicial: depois cai no chão quando a câmera avança
      const a1 = this.aspects['vhs_front'];
      const drop = ss(this.tl.hookEnd - 0.1, this.tl.hookEnd + 0.9, t);
      this.vhs1.position.set(0 + drop * 0.35, CAM_Y - drop * (CAM_Y - 0.012), 0 - drop * 0.6);
      this.vhs1.rotation.set(-Math.PI / 2 * drop, 0, drop * 0.5);
      this.vhs1Shadow.visible = drop < 0.05; this.vhs1Shadow.position.set(0.012, CAM_Y - 0.014, -0.05);
      U(this.vhs1Shadow).blurPx.value = 16; U(this.vhs1Shadow).opacity.value = 0.6;
      U(this.vhs1).blurPx.value = 0; void a1;
      // fita do loop final: sobe para o centro e a câmera mergulha nela
      const z2 = this.path.vhs2Z; const rise = ss(this.tl.diveStart - 0.4, this.tl.diveStart + 0.08, t);
      this.vhs2.visible = t > this.tl.diveStart - 0.42;
      this.vhs2.position.set(0, lerp(0.3, CAM_Y, rise), z2); this.vhs2.rotation.set(0, 0, 0);
      U(this.vhs2).opacity.value = clamp01((t - (this.tl.diveStart - 0.42)) / 0.2);
      this.updateSched(t, p);
    } else this.updateSched(t, p);
    // motion blur só nas travessias (zoom blur proporcional à velocidade)
    const v = this.hook === 'cover' ? 0 : Math.abs(this.path.vel(t));
    const edge = this.hook === 'cover' ? 0 : ss(0.0, 0.2, t) * (1 - ss(this.path.lastT - 0.2, this.path.lastT, t));
    postMat.uniforms.zoom.value = Math.min(0.07, Math.max(0, (v - 2.0) / 10) * 0.07) * edge;
    postMat.uniforms.time.value = t;
    postMat.uniforms.grain.value = 0.06;
    this.renderer.setRenderTarget(this.rt); this.renderer.render(this.scene, cam);
    postMat.uniforms.tDiffuse.value = this.rt.texture;
    this.renderer.setRenderTarget(null); this.renderer.render(this.postScene, this.postCam);
  }
}
