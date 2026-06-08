import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Tangent line to a circle at a point on it. Slot a is the point of tangency,
slot o the circle's centre; the tangent is the line through a perpendicular to
the radius o-a. A second point x on that line is computed (never placed by hand)
so the engine gets perp a x a o.
**/
export const tangentLine: CatalogEntry = {
  name: 'lc_tangent',
  label: 'Tangent to Circle',
  shortcut: 'Y',
  icon: () =>
    iconWrap([
      svgEl('circle', {
        cx: '9', cy: '11', r: '6',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      // The tangent line touching the circle at its rightmost point.
      svgEl('line', {
        x1: '15', y1: '3', x2: '15', y2: '19',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '9', cy: '11', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '15', cy: '11', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick the point on the circle where the tangent touches' },
    { name: 'o', kind: 'pick', label: 'Pick the centre of the circle' },
  ],
  edges: [],
  circles: [],
  // While placing the centre, treat the cursor as o and preview the circle
  // through a plus the tangent line at a, so the tangency is clear.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    if (!a) return [];
    const dx = cursor.x - a.x;
    const dy = cursor.y - a.y;
    const len = Math.hypot(dx, dy);
    if (len < 1e-9) return [];
    // Unit perpendicular to the radius a-o; the tangent runs along it through a.
    const px = -dy / len;
    const py = dx / len;
    return [
      { kind: 'circle', center: { x: cursor.x, y: cursor.y }, through: { x: a.x, y: a.y } },
      {
        kind: 'auxLine',
        from: world(a.x - px * len, a.y - py * len),
        to: world(a.x + px * len, a.y + py * len),
      },
    ];
  },
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const oId = binds.o as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const o = scene.objects.get(oId) as PointObject;

    // Perpendicular to the radius o-a, scaled to the radius length, gives a
    // second point so the renderer can draw the full tangent line.
    const dx = o.x - a.x;
    const dy = o.y - a.y;
    const xId = scene.addPoint(a.x - dy, a.y + dx);
    const radius = Math.hypot(dx, dy);

    return {
      kind: 'construction',
      name: 'lc_tangent',
      bindings: { a: aId, o: oId, x: xId },
      // The radius, drawn finite, with the tangent as a full line through a, and
      // the circle the line is tangent to (centre o, through a).
      edges: [[oId, aId]],
      lines: [[aId, xId]],
      circles: [{ center: oId, radius }],
    };
  },
  // Tell the engine the line a-x is tangent at a: lc_tangent defines x with
  // perp a x a o (the tangent is perpendicular to the radius o-a).
  jgex: [
    { def: 'lc_tangent', signature: ['x', 'a', 'o'], produces: ['x'] },
  ],
  validate: (binds) =>
    binds.a !== undefined && binds.o !== undefined && binds.a === binds.o
      ? 'The tangency point and the centre must be distinct'
      : null,
};
