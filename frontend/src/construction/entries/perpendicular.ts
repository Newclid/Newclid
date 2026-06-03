import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Perpendicular line. Pick two points for the reference line, then a third
point the new line runs through; the line through that point at right angles
to the reference is drawn. While placing the third point, both the reference
line and the perpendicular preview live so you can see where it lands.
**/
export const perpendicular: CatalogEntry = {
  name: 'perpendicular',
  label: 'Perpendicular',
  shortcut: 'E',
  icon: () =>
    iconWrap([
      // The reference line (horizontal) and the perpendicular (vertical),
      // with a small square marking the right angle between them.
      svgEl('line', {
        x1: '4', y1: '17', x2: '20', y2: '17',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('line', {
        x1: '11', y1: '3', x2: '11', y2: '17',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('path', {
        d: 'M11 13 L15 13 L15 17',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1',
      }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick first point of the line' },
    { name: 'b', kind: 'pick', label: 'Pick second point of the line' },
    { name: 'p', kind: 'pick', label: 'Pick the point the perpendicular runs through' },
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

    // Unit vector along the reference line, rotated 90° for the perpendicular.
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    const ux = (b.x - a.x) / len;
    const uy = (b.y - a.y) / len;
    const dx = -uy;
    const dy = ux;

    // A second point on the perpendicular so the renderer can draw the line.
    const qId = scene.addPoint(p.x + dx * len, p.y + dy * len);

    return {
      kind: 'construction',
      name: 'perpendicular',
      bindings: { a: aId, b: bId, p: pId, q: qId },
      edges: [],
      lines: [[aId, bId], [pId, qId]],
      circles: [],
    };
  },
  // While placing the through-point, preview the reference line and the
  // perpendicular running through the cursor.
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
        from: world(cursor.x + uy * ext, cursor.y - ux * ext),
        to: world(cursor.x - uy * ext, cursor.y + ux * ext),
      },
    ];
  },
  validate: (binds) =>
    binds.a !== undefined && binds.b !== undefined && binds.a === binds.b
      ? 'The two line points must be distinct'
      : null,
};
