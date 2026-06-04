import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Mirror point (point reflection). Slot a is the point to reflect, slot b is the
centre of reflection; the image x is computed as 2b - a, never placed by hand,
so x, b and a are always collinear with b the midpoint (a true reflection)
rather than an arbitrary point.
**/
export const mirror: CatalogEntry = {
  name: 'mirror',
  label: 'Mirror Point',
  shortcut: 'K',
  icon: () =>
    iconWrap([
      // Two points reflected through a centre dot, all on one line.
      svgEl('line', {
        x1: '3', y1: '11', x2: '19', y2: '11',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '4', cy: '11', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '11', cy: '11', r: '2', fill: 'currentColor' }),
      svgEl('circle', { cx: '18', cy: '11', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick the point to reflect' },
    { name: 'b', kind: 'pick', label: 'Pick the mirror point (centre of reflection)' },
  ],
  edges: [],
  circles: [],
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const b = scene.objects.get(bId) as PointObject;

    // Image of a reflected through b: b is the midpoint of a-x, so x = 2b - a.
    const xId = scene.addPoint(2 * b.x - a.x, 2 * b.y - a.y);

    return {
      kind: 'construction',
      name: 'mirror',
      bindings: { a: aId, b: bId, x: xId },
      // A single segment from the point to its image; the centre b sits on it.
      edges: [[aId, xId]],
      circles: [],
    };
  },
  // While placing the centre, treat the cursor as b and preview the reflection
  // as one line from a to its image, with markers on the centre and the image
  // so the user sees both the mirror point and where the result will land.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    if (!a) return [];
    const x = world(2 * cursor.x - a.x, 2 * cursor.y - a.y);
    return [
      { kind: 'auxLine', from: world(a.x, a.y), to: x },
      { kind: 'point', at: world(cursor.x, cursor.y) },
      { kind: 'point', at: x },
    ];
  },
  // Tell the engine x is a's reflection through b: mirror defines x with
  // coll x a b and cong b a b x (b the midpoint of a-x).
  jgex: [
    { def: 'mirror', signature: ['x', 'a', 'b'], produces: ['x'] },
  ],
  validate: (binds) =>
    binds.a !== undefined && binds.b !== undefined && binds.a === binds.b
      ? 'The point and the mirror centre must be distinct'
      : null,
};
