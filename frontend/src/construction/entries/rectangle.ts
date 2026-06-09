import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Rectangle from two opposite corners. The user places corner a and the opposite
corner c; the remaining corners b and d are computed as (c.x, a.y) and
(a.x, c.y), so the four points always form an axis-aligned rectangle rather than
an arbitrary quadrilateral. While placing c the whole rectangle previews live.
**/
export const rectangle: CatalogEntry = {
  name: 'rectangle',
  label: 'Rectangle',
  shortcut: 'T',
  icon: () =>
    iconWrap([
      svgEl('rect', {
        x: '4', y: '6', width: '15', height: '11',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '4', cy: '6', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '19', cy: '6', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '19', cy: '17', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '4', cy: '17', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick the first corner (1 of 2)' },
    { name: 'c', kind: 'pick', label: 'Pick the opposite corner (2 of 2)' },
  ],
  edges: [],
  circles: [],
  // While placing the opposite corner, treat the cursor as c and preview the
  // four sides so the user sees the full rectangle (corners b and d computed)
  // before clicking.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    if (!a) return [];
    const b = world(cursor.x, a.y);
    const c = world(cursor.x, cursor.y);
    const d = world(a.x, cursor.y);
    const aw = world(a.x, a.y);
    return [
      { kind: 'auxLine', from: aw, to: b },
      { kind: 'auxLine', from: b, to: c },
      { kind: 'auxLine', from: c, to: d },
      { kind: 'auxLine', from: d, to: aw },
    ];
  },
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const cId = binds.c as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const c = scene.objects.get(cId) as PointObject;

    // The two computed corners completing the rectangle a-b-c-d (in order).
    const bId = scene.addPoint(c.x, a.y);
    const dId = scene.addPoint(a.x, c.y);

    return {
      kind: 'construction',
      name: 'rectangle',
      bindings: { a: aId, b: bId, c: cId, d: dId },
      edges: [[aId, bId], [bId, cId], [cId, dId], [dId, aId]],
      circles: [],
    };
  },
  // The engine knows all four corners form a rectangle (right angles, opposite
  // sides parallel and equal): a b c d = rectangle a b c d.
  jgex: [
    { def: 'rectangle', signature: ['a', 'b', 'c', 'd'], produces: ['a', 'b', 'c', 'd'] },
  ],
  validate: (binds, scene) => {
    const { a, c } = binds;
    if (a === undefined || c === undefined) return null;
    if (a === c) return 'The two corners must be distinct';
    const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
    const pc = scene.objects.get(c as ObjectId) as PointObject | undefined;
    if (!pa || !pc) return null;
    // Reject a degenerate (zero-area) rectangle where the corners share a row
    // or column.
    if (Math.abs(pa.x - pc.x) < 1e-9 || Math.abs(pa.y - pc.y) < 1e-9) {
      return 'The corners must not be aligned (zero-area rectangle)';
    }
    return null;
  },
};
