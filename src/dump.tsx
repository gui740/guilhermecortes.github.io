import {SCENES, TRANSITIONS, HOOKS, LOOP_START, TOTAL} from './remotion/timeline';
const out: any = {transitions: TRANSITIONS, loop: LOOP_START, total: TOTAL, blocks: [], hooks: {}};
for (const S of SCENES) for (const B of S.blocks) out.blocks.push({scene: S.id, from: B.from, to: B.to, bg: B.bg, toks: (B.lines || []).flat().map((t) => ({t: t.t, at: t.at, hl: !!t.hl})),
  layers: B.layers.map((l: any) => l.k + (l.src ? ':' + l.src : '') + ('z' in l ? '@' + l.z : '')), nums: B.layers.filter((l: any) => l.k === 'num' || l.k === 'logo' || l.k === 'star').map((l: any) => ({k: l.k, at: l.at}))});
for (const k of ['A', 'B', 'C']) out.hooks[k] = (HOOKS as any)[k].scene.blocks.map((B: any) => ({from: B.from, to: B.to, bg: B.bg, toks: B.lines.flat().map((t: any) => ({t: t.t, at: t.at, hl: !!t.hl}))}));
console.log(JSON.stringify(out, null, 1));
