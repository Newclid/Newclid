import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Parallelogram through three picked vertices a, b, c (in order). The fourth
vertex x is computed as a + c - b, never placed by hand, so the result is
always a true parallelogram (opposite sides parallel and equal) rather than an
arbitrary quadrilateral.
**/
export const parallelogram: CatalogEntry = {
  name: 'parallelogram',
  label: 'Parallelogram',
  shortcut: 'G',
  icon: () =>
    iconWrap([
      // A slanted four-sided outline so it reads as a parallelogram, not a box.
      svgEl('polygon', {
        points: '3,16 13,6 19,6 9,16',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '3', cy: '16', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '13', cy: '6', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '19', cy: '6', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '9', cy: '16', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick first vertex' },
    { name: 'b', kind: 'pick', label: 'Pick second vertex' },
    { name: 'c', kind: 'pick', label: 'Pick third vertex' },
  ],
  edges: [{ pointIds: ['a', 'b'] }, { pointIds: ['b', 'c'] }],
  circles: [],
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const b = scene.objects.get(bId) as PointObject;
    const c = scene.objects.get(cId) as PointObject;

    // Fourth vertex completing the parallelogram a-b-c-x: the diagonals a-c
    // and b-x share a midpoint, so x = a + c - b.
    const xId = scene.addPoint(a.x + c.x - b.x, a.y + c.y - b.y);

    return {
      kind: 'construction',
      name: 'parallelogram',
      bindings: { a: aId, b: bId, c: cId, x: xId },
      edges: [[aId, bId], [bId, cId], [cId, xId], [xId, aId]],
      circles: [],
    };
  },
  // While placing the third vertex, treat the cursor as c and preview the two
  // sides that close the shape (b-c and the derived x), so the user sees the
  // full parallelogram before clicking.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    const x = { x: a.x + cursor.x - b.x, y: a.y + cursor.y - b.y };
    return [
      { kind: 'auxLine', from: world(b.x, b.y), to: world(cursor.x, cursor.y) },
      { kind: 'auxLine', from: world(cursor.x, cursor.y), to: world(x.x, x.y) },
      { kind: 'auxLine', from: world(x.x, x.y), to: world(a.x, a.y) },
    ];
  },
  jgex: [
    { def: 'parallelogram', signature: ['x', 'a', 'b', 'c'], produces: ['x'] },
  ],
  validate: (binds, scene) => {
    const { a, b, c } = binds;
    if (a === undefined || b === undefined || c === undefined) return null;
    if (a === b || b === c || a === c) return 'Three distinct points required';
    const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
    const pb = scene.objects.get(b as ObjectId) as PointObject | undefined;
    const pc = scene.objects.get(c as ObjectId) as PointObject | undefined;
    if (!pa || !pb || !pc) return null;
    // ncoll a b c: reject (near-)collinear points via the cross product.
    const cross = (pa.x - pb.x) * (pc.y - pb.y) - (pa.y - pb.y) * (pc.x - pb.x);
    if (Math.abs(cross) < 1e-9) return 'Points must not be collinear';
    return null;
  },
};
