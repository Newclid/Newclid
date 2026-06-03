import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';
import { drawReferenceLineOnSlotB } from '../reference-line';

/**
Perpendicular line through a point. Slots a and b set the reference line;
slot p is the point the perpendicular passes through. The reference line is
committed once a and b are placed (see onSlotFilled), so sketch emits only
the perpendicular through p.
**/
export const perpendicular: CatalogEntry = {
  name: 'perpendicular',
  label: 'Perpendicular',
  shortcut: 'E',
  icon: () =>
    iconWrap([
      // Reference line and perpendicular, with a small square for the right angle.
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
      lines: [[pId, qId]],
      circles: [],
    };
  },
  // Tell the engine the new line is perpendicular to the reference line:
  // on_tline defines q on the line through p perpendicular to a-b (clause:
  // perp q p a b).
  jgex: [
    { def: 'on_tline', signature: ['q', 'p', 'a', 'b'], produces: ['q'] },
  ],
  // Commit the reference line once its two points are placed.
  onSlotFilled: drawReferenceLineOnSlotB,
  // Preview the perpendicular through the cursor; the reference line is already drawn.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    if (len < 1e-9) return [];
    const ux = (b.x - a.x) / len;
    const uy = (b.y - a.y) / len;
    // Short stub scaled to the reference length; the full line is drawn on commit.
    const ext = len;
    return [
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
