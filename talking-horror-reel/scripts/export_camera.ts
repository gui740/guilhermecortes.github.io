import {cameraSpeed, cameraAt} from '../src/camera';
import {STOPS, DURATION} from '../src/timeline';
const speeds: number[] = []; for (let f = 0; f <= DURATION * 30; f++) speeds.push(+cameraSpeed(Math.min(DURATION - 0.02, Math.max(0.02, f / 30))).toFixed(3));
console.log(JSON.stringify({duration: DURATION, speeds, stops: STOPS.map((s) => ({id: s.id, ta: s.ta, tt: s.tt, td: s.td}))}));
