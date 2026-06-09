import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Equal distance. Slots b and c set a reference length |bc|; slot a is the base
point (which may be b or c itself). Slot x is a derive slot constrained to the
circle of radius |bc| around a, so the distance x-a always equals b-c
(cong x a b c). The cursor's direction from a picks where on that circle x lands.
**/
export const eqdistance: CatalogEntry = {
  name: 'eqdistance',
  label: 'Equal Distance',
  shortcut: 'D',
  icon: () =>
    iconWrap([
      svgEl('circle', {
        cx: '8', cy: '11', r: '6',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      // Base a and the point x on the circle.
      svgEl('circle', { cx: '8', cy: '11', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '14', cy: '11', r: '1.6', fill: 'currentColor' }),
      // A short reference segment standing in for the length b-c.
      svgEl('line', {
        x1: '18', y1: '4', x2: '18', y2: '18',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
    ]),
  slots: [
    { name: 'b', kind: 'pick-existing', label: 'Pick the first point of the length to copy (1 of 2)' },
    { name: 'c', kind: 'pick-existing', label: 'Pick the second point of the length to copy (2 of 2)' },
    { name: 'a', kind: 'pick', label: 'Pick the point where you want to copy this length from' },
    {
      name: 'x',
      kind: 'derive',
      label: 'Place the new point at the same distance',
      // Snap x onto the circle of radius |bc| around a, in the cursor direction.
      project: (binds, scene, cursor) => {
        const a = scene.objects.get(binds.a as ObjectId) as PointObject;
        const b = scene.objects.get(binds.b as ObjectId) as PointObject;
        const c = scene.objects.get(binds.c as ObjectId) as PointObject;
        const r = Math.hypot(c.x - b.x, c.y - b.y);
        let dx = cursor.x - a.x;
        let dy = cursor.y - a.y;
        let len = Math.hypot(dx, dy);
        if (len < 1e-9) {
          dx = 1;
          dy = 0;
          len = 1;
        }
        return world(a.x + (dx / len) * r, a.y + (dy / len) * r);
      },
      // Show the circle x is constrained to (radius |bc| around a).
      preview: (binds, scene) => {
        const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
        const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
        const c = scene.objects.get(binds.c as ObjectId) as PointObject | undefined;
        if (!a || !b || !c) return [];
        const r = Math.hypot(c.x - b.x, c.y - b.y);
        return [{ kind: 'circle', center: { x: a.x, y: a.y }, through: { x: a.x + r, y: a.y } }];
      },
    },
  ],
  edges: [],
  circles: [],
  sketch: (binds) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    const xId = binds.x as ObjectId;
    return {
      kind: 'construction',
      name: 'eqdistance',
      bindings: { a: aId, b: bId, c: cId, x: xId },
      // Just the radius from the base to x; the locus circle is preview-only.
      edges: [[aId, xId]],
      circles: [],
    };
  },
  // Tell the engine x is as far from a as b is from c: eqdistance defines x with
  // cong x a b c.
  jgex: [
    { def: 'eqdistance', signature: ['x', 'a', 'b', 'c'], produces: ['x'] },
  ],
  validate: (binds) =>
    binds.b !== undefined && binds.c !== undefined && binds.b === binds.c
      ? 'The two reference points must be distinct'
      : null,
};
