import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';
import { drawReferenceLineOnSlotB } from '../reference-line';

// Orthogonal projection of p onto the line through a and b.
function projectOntoLine(
  a: { x: number; y: number },
  b: { x: number; y: number },
  p: { x: number; y: number },
): { x: number; y: number } {
  const abx = b.x - a.x;
  const aby = b.y - a.y;
  const len2 = abx * abx + aby * aby;
  const t = ((p.x - a.x) * abx + (p.y - a.y) * aby) / len2;
  return { x: a.x + t * abx, y: a.y + t * aby };
}

/**
Foot of perpendicular. Slots a and b set the reference line; slot p is the
external point. sketch creates the foot (p projected onto the line) and the
drop segment from p to it. The reference line is committed once a and b are
placed (see onSlotFilled).
**/
export const foot: CatalogEntry = {
  name: 'foot',
  label: 'Foot of Perpendicular',
  shortcut: 'F',
  icon: () =>
    iconWrap([
      // Reference line, external point, and the drop to the foot with a right-angle square.
      svgEl('line', {
        x1: '3', y1: '17', x2: '19', y2: '17',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('line', {
        x1: '11', y1: '4', x2: '11', y2: '17',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('path', {
        d: 'M11 13 L15 13 L15 17',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1',
      }),
      svgEl('circle', { cx: '11', cy: '4', r: '1.8', fill: 'currentColor' }),
      svgEl('circle', { cx: '11', cy: '17', r: '1.8', fill: 'red' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick a point on the line to project onto (1 of 2)' },
    { name: 'b', kind: 'pick', label: 'Pick another point on the line (2 of 2)' },
    { name: 'p', kind: 'pick', label: 'Pick the point you want to drop the perpendicular from' },
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

    // The foot is p projected onto the line, so it sits on the reference line.
    const f = projectOntoLine(a, b, p);
    const fId = scene.addPoint(f.x, f.y);
    scene.setPointColor(fId, 'red');

    return {
      kind: 'construction',
      name: 'foot',
      bindings: { a: aId, b: bId, p: pId, f: fId },
      edges: [[pId, fId]],
      circles: [],
    };
  },
  // Tell the engine the foot is the perpendicular projection onto the line:
  // foot defines f with perp f p a b and coll f a b.
  jgex: [
    { def: 'foot', signature: ['f', 'p', 'a', 'b'], produces: ['f'] },
  ],
  // Commit the reference line once its two points are placed.
  onSlotFilled: drawReferenceLineOnSlotB,
  // Preview the drop from the cursor to its foot; the reference line is already drawn.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    if (Math.hypot(b.x - a.x, b.y - a.y) < 1e-9) return [];
    const f = projectOntoLine(a, b, cursor);
    return [
      {
        kind: 'auxLine',
        from: world(cursor.x, cursor.y),
        to: world(f.x, f.y),
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
    // A point already on the line is its own foot, so there is nothing to drop.
    const cross = (pa.x - pb.x) * (pp.y - pb.y) - (pa.y - pb.y) * (pp.x - pb.x);
    if (Math.abs(cross) < 1e-9) return 'The point must not lie on the reference line';
    return null;
  },
};
