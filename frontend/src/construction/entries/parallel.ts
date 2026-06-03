import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Parallel line. Pick two points for the reference line, then a third point the
new line runs through; the line through that point parallel to the reference
is drawn. While placing the third point, both the reference line and the
parallel preview live so you can see where it lands.
**/
export const parallel: CatalogEntry = {
  name: 'parallel',
  label: 'Parallel',
  shortcut: 'R',
  icon: () =>
    iconWrap([
      // Two parallel diagonal strokes.
      svgEl('line', {
        x1: '3', y1: '14', x2: '15', y2: '4',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('line', {
        x1: '7', y1: '18', x2: '19', y2: '8',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick first point of the line' },
    { name: 'b', kind: 'pick', label: 'Pick second point of the line' },
    { name: 'p', kind: 'pick', label: 'Pick the point the parallel runs through' },
  ],
  edges: [],
  circles: [],
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const pId = binds.p as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const b = scene.objects.get(bId) as PointObject;
    const p = scene.objects.get(pId) as PointObject;

    // Unit vector along the reference line; the parallel runs the same way.
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    const ux = (b.x - a.x) / len;
    const uy = (b.y - a.y) / len;

    // A second point on the parallel so the renderer can draw the line.
    const qId = scene.addPoint(p.x + ux * len, p.y + uy * len);

    return {
      kind: 'construction',
      name: 'parallel',
      bindings: { a: aId, b: bId, p: pId, q: qId },
      edges: [],
      lines: [[aId, bId], [pId, qId]],
      circles: [],
    };
  },
  // While placing the through-point, preview the reference line and the
  // parallel running through the cursor.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    if (len < 1e-9) return [];
    const ux = (b.x - a.x) / len;
    const uy = (b.y - a.y) / len;
    // Keep the preview a short stub scaled to the reference length; the full
    // infinite line is drawn only once the point is committed.
    const ext = len;
    return [
      {
        kind: 'auxLine',
        from: world(a.x - ux * ext, a.y - uy * ext),
        to: world(a.x + ux * ext, a.y + uy * ext),
      },
      {
        kind: 'auxLine',
        from: world(cursor.x - ux * ext, cursor.y - uy * ext),
        to: world(cursor.x + ux * ext, cursor.y + uy * ext),
      },
    ];
  },
  validate: (binds, scene) => {
    const { a, b, p } = binds;
    if (a === undefined || b === undefined) return null;
    if (a === b) return 'The two line points must be distinct';
    if (p === undefined) return null;
    const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
    const pb = scene.objects.get(b as ObjectId) as PointObject | undefined;
    const pp = scene.objects.get(p as ObjectId) as PointObject | undefined;
    if (!pa || !pb || !pp) return null;
    // A parallel through a point already on the line would just be that line.
    const cross = (pa.x - pb.x) * (pp.y - pb.y) - (pa.y - pb.y) * (pp.x - pb.x);
    if (Math.abs(cross) < 1e-9) return 'The point must not lie on the reference line';
    return null;
  },
};
