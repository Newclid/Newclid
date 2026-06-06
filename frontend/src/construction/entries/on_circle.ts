import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Point on a circle. Slot o is the centre, slot a a point on the circle (setting
the radius |oa|). Slot x is a derive slot constrained to that circle, so the
distance o-x always equals o-a (cong o x o a). The cursor's direction from o
picks where on the circle x lands.
**/
export const onCircle: CatalogEntry = {
  name: 'on_circle',
  label: 'Point on Circle',
  shortcut: 'Q',
  icon: () =>
    iconWrap([
      svgEl('circle', {
        cx: '11', cy: '11', r: '7',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      // Centre o, the radius point a, and x sitting on the circle.
      svgEl('circle', { cx: '11', cy: '11', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '11', cy: '4', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '18', cy: '11', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'o', kind: 'pick', label: "Pick the circle's centre" },
    { name: 'a', kind: 'pick', label: 'Pick a point on the circle (sets the radius)' },
    {
      name: 'x',
      kind: 'derive',
      label: 'Place x on the circle',
      // Snap x onto the circle of radius |oa| around o, in the cursor direction.
      project: (binds, scene, cursor) => {
        const o = scene.objects.get(binds.o as ObjectId) as PointObject;
        const a = scene.objects.get(binds.a as ObjectId) as PointObject;
        const r = Math.hypot(a.x - o.x, a.y - o.y);
        let dx = cursor.x - o.x;
        let dy = cursor.y - o.y;
        let len = Math.hypot(dx, dy);
        if (len < 1e-9) {
          dx = 1;
          dy = 0;
          len = 1;
        }
        return world(o.x + (dx / len) * r, o.y + (dy / len) * r);
      },
      // Show the circle x is constrained to (centre o through a).
      preview: (binds, scene) => {
        const o = scene.objects.get(binds.o as ObjectId) as PointObject | undefined;
        const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
        if (!o || !a) return [];
        return [{ kind: 'circle', center: { x: o.x, y: o.y }, through: { x: a.x, y: a.y } }];
      },
    },
  ],
  edges: [],
  circles: [],
  sketch: (binds) => {
    const oId = binds.o as ObjectId;
    const aId = binds.a as ObjectId;
    const xId = binds.x as ObjectId;
    return {
      kind: 'construction',
      name: 'on_circle',
      bindings: { o: oId, a: aId, x: xId },
      // The radius from the centre to the placed point.
      edges: [[oId, xId]],
      circles: [],
    };
  },
  // Tell the engine x is as far from o as a is: on_circle defines x with
  // cong o x o a.
  jgex: [
    { def: 'on_circle', signature: ['x', 'o', 'a'], produces: ['x'] },
  ],
  validate: (binds) =>
    binds.o !== undefined && binds.a !== undefined && binds.o === binds.a
      ? 'The centre and the point on the circle must be distinct'
      : null,
};
