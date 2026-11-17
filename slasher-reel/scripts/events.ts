import {STATIONS, camZ, wt} from '../src/timeline';
import {DOOR_Z} from '../src/scene';
const cross = (z: number, d: number) => { for (let t = 0; t < 39.5; t += 1 / 240) if (camZ(t) - z <= d) return +t.toFixed(3); return -1; };
const [S3, S2, S1] = STATIONS;
const ev = {
  ripTape: cross(S3.killerZ - 2.4, 1.4),
  doorOpenStart: cross(DOOR_Z, 10), doorPass: cross(DOOR_Z, 0.5),
  cross3: cross(S3.killerZ, 0.8), cross2: cross(S2.killerZ, 0.8), cross1: cross(S1.killerZ, 0.8),
  reveal: STATIONS.map((s) => +s.tReveal.toFixed(3)), titles: STATIONS.map((s) => +s.tTitle.toFixed(3)),
  nao: wt('não'),
};
console.log(JSON.stringify(ev));
