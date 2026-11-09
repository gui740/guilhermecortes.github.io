import narr from '../data/narracao.json';
import {montarTiming, Narracao} from './timing';
export const TIMING = montarTiming(narr as Narracao);
export const CENAS = TIMING.cenas;
