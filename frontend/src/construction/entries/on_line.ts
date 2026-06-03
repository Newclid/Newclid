import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { projectOntoLine } from '../../geometry/primitives';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Point on a line. Slots a and b set the line; slot p is a point constrained to
lie on it. The derive slot projects the cursor onto line a-b, so the placed
point lands exactly on the line rather than near it.
**/
export const onLine: CatalogEntry = {
  name: 'on_line',
  label: 'Point on Line',
  shortcut: 'N',
  icon: () =>
    iconWrap([
      // A line with its two defining points and the placed point sitting on it.
      svgEl('line', {
        x1: '3', y1: '11', x2: '19', y2: '11',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '4', cy: '11', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '18', cy: '11', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '11', cy: '11', r: '2', fill: 'red' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick first point of the line' },
    { name: 'b', kind: 'pick', label: 'Pick second point of the line' },
    {
      name: 'p',
      kind: 'derive',
      label: 'Place the point on the line',
      // Show the line while the point is being placed so its landing spot reads.
      preview: (binds, scene) => {
        const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
        const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
        if (!a || !b) return [];
        const len = Math.hypot(b.x - a.x, b.y - a.y);
        if (len < 1e-9) return [];
        const ux = (b.x - a.x) / len;
        const uy = (b.y - a.y) / len;
        return [
          {
            kind: 'auxLine',
            from: world(a.x - ux * len, a.y - uy * len),
            to: world(b.x + ux * len, b.y + uy * len),
          },
        ];
      },
      // Snap the cursor onto the line so the point is exactly on it, not near it.
      project: (binds, scene, cursor) => {
        const a = scene.objects.get(binds.a as ObjectId) as PointObject;
        const b = scene.objects.get(binds.b as ObjectId) as PointObject;
        const f = projectOntoLine(a, b, cursor);
        return world(f.x, f.y);
      },
    },
  ],
  edges: [],
  circles: [],
  sketch: (binds) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const pId = binds.p as ObjectId;
    return {
      kind: 'construction',
      name: 'on_line',
      bindings: { a: aId, b: bId, p: pId },
      edges: [],
      lines: [[aId, bId]],
      circles: [],
    };
  },
  validate: (binds) =>
    binds.a !== undefined && binds.b !== undefined && binds.a === binds.b
      ? 'The two line points must be distinct'
      : null,
};
