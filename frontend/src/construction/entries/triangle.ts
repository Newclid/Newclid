import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

export const triangle: CatalogEntry = {
  name: 'triangle',
  label: 'Triangle',
  shortcut: 'U',
  icon: () =>
    iconWrap([
      svgEl('polygon', {
        points: '9,3 20,19 2,17',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '9', cy: '3', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '20', cy: '19', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '2', cy: '17', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick the first vertex' },
    { name: 'b', kind: 'pick', label: 'Pick the second vertex' },
    { name: 'c', kind: 'pick', label: 'Pick the third vertex' },
  ],
  edges: [{ pointIds: ['a', 'b'] }],
  circles: [],
  // Preview the two open edges toward the cursor while the third vertex is being placed.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    return [
      { kind: 'auxLine' as const, from: world(b.x, b.y), to: world(cursor.x, cursor.y) },
      { kind: 'auxLine' as const, from: world(cursor.x, cursor.y), to: world(a.x, a.y) },
    ];
  },
  sketch: (binds) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    return {
      kind: 'construction',
      name: 'triangle',
      bindings: { a: aId, b: bId, c: cId },
      edges: [[aId, bId], [bId, cId], [cId, aId]],
      circles: [],
    };
  },
  jgex: [
    { def: 'triangle', signature: ['a', 'b', 'c'], produces: ['a', 'b', 'c'] },
  ],
  validate: (binds, scene) => {
    const { a, b, c } = binds;
    if (a !== undefined && b !== undefined && a === b) return 'Vertices must be distinct';
    if (b !== undefined && c !== undefined && b === c) return 'Vertices must be distinct';
    if (a !== undefined && c !== undefined && a === c) return 'Vertices must be distinct';
    if (a !== undefined && b !== undefined && c !== undefined) {
      const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
      const pb = scene.objects.get(b as ObjectId) as PointObject | undefined;
      const pc = scene.objects.get(c as ObjectId) as PointObject | undefined;
      if (pa && pb && pc) {
        const cross = (pb.x - pa.x) * (pc.y - pa.y) - (pb.y - pa.y) * (pc.x - pa.x);
        if (Math.abs(cross) < 1e-9) return 'Triangle vertices must not be collinear';
      }
    }
    return null;
  },
};
