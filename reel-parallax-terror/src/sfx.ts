import {CENAS} from './config/cenas';
import {CenaId, TRANSICAO} from './config/timing';
import {tlGancho} from './scenes/Hook';
import {tlPossum} from './scenes/Possum';
import {tlCalvaire} from './scenes/Calvaire';
import {tlHagazussa} from './scenes/Hagazussa';
import {tlFechamento} from './scenes/Outro';

export type Sfx = {f: number; s: 'papel' | 'fita' | 'caneta' | 'rasgo' | 'queda' | 'whoosh' | 'batida'; v: number};

/** Todos os efeitos sonoros, em frames absolutos, amarrados aos mesmos tempos das animações. */
export const listaSfx = (): Sfx[] => {
  const out: Sfx[] = [];
  const add = (id: CenaId, f: number, s: Sfx['s'], v = 0.45) => out.push({f: CENAS[id].inicio + Math.max(0, Math.round(f)), s, v});

  const g = tlGancho();
  g.polas.forEach((p) => { add('gancho', p + 5, 'queda', 0.55); add('gancho', p + 9, 'fita', 0.25); });
  add('gancho', g.titulo, 'batida', 0.5);
  add('gancho', g.titulo + 2, 'papel', 0.4);
  add('gancho', g.seta, 'caneta', 0.45);
  add('gancho', g.circulo, 'caneta', 0.35);
  add('gancho', g.saida + 2, 'whoosh', 0.5);

  const p = tlPossum();
  add('possum', p.flip, 'papel', 0.5);
  add('possum', p.poster, 'queda', 0.45);
  [p.ficha, p.casa, p.philip, p.mala, p.boneco, p.maurice, p.philip2].forEach((f) => add('possum', f, 'papel', 0.4));
  [p.ficha + 4, p.casa + 7, p.boneco + 8].forEach((f) => add('possum', f, 'fita', 0.22));
  [p.nota, p.circMala, p.circBoneco, p.pior, p.setaSaida].forEach((f) => add('possum', f, 'caneta', 0.38));
  add('possum', CENAS.possum.saida, 'whoosh', 0.55);

  const c = tlCalvaire();
  [c.ficha, c.poster, c.marc, c.van, c.bartel, c.morador1, c.morador3, c.morador2, c.bar].forEach((f) => add('calvaire', f, 'papel', 0.38));
  [c.poster + 7, c.bar + 8].forEach((f) => add('calvaire', f, 'fita', 0.22));
  [c.circBartel, c.nota, c.xBar].forEach((f) => add('calvaire', f, 'caneta', 0.38));
  add('calvaire', CENAS.calvaire.saida - 2, 'rasgo', 0.6);

  const h = tlHagazussa();
  [h.ficha, h.cabana, h.albrun, h.cabra, h.cabra2, h.caveira, h.poster, h.albrun2].forEach((f) => add('hagazussa', f, 'papel', 0.38));
  add('hagazussa', h.cabana + 7, 'fita', 0.22);
  add('hagazussa', h.seculo, 'caneta', 0.38);
  h.estrela.forEach((f) => add('hagazussa', f, 'caneta', 0.22));
  add('hagazussa', CENAS.hagazussa.saida, 'whoosh', 0.4);

  const o = tlFechamento();
  add('fechamento', TRANSICAO - 3, 'queda', 0.5);
  add('fechamento', o.arroba + 4, 'queda', 0.5);
  add('fechamento', o.arroba + 6, 'fita', 0.25);
  add('fechamento', o.cta, 'batida', 0.55);
  return out;
};
