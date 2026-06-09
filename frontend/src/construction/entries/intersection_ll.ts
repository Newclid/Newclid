import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

type Pt = { x: number; y: number };

/**
Intersection of line a-b and line c-d. Returns the crossing point, or null when
the lines are parallel (or coincident), in which case there is no single point.
**/
function lineIntersection(a: Pt, b: Pt, c: Pt, d: Pt): Pt | null {
  const denom = (b.x - a.x) * (d.y - c.y) - (b.y - a.y) * (d.x - c.x);
  if (Math.abs(denom) < 1e-9) return null;
  const t = ((c.x - a.x) * (d.y - c.y) - (c.y - a.y) * (d.x - c.x)) / denom;
  return { x: a.x + t * (b.x - a.x), y: a.y + t * (b.y - a.y) };
}

/**
Line-line intersection. Slots a, b set the first line and c, d the second; the
point x is computed at their crossing (never placed by hand), so it always lies
on both lines (coll x a b, coll x c d).
**/
export const intersectionLL: CatalogEntry = {
  name: 'intersection_ll',
  label: 'Intersection of Lines',
  shortcut: 'X',
  icon: () =>
    iconWrap([
      svgEl('line', {
        x1: '3', y1: '5', x2: '19', y2: '17',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('line', {
        x1: '3', y1: '17', x2: '19', y2: '5',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '11', cy: '11', r: '2', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick a point on the first line (1 of 2)' },
    { name: 'b', kind: 'pick', label: 'Pick another point on the first line (2 of 2)' },
    { name: 'c', kind: 'pick', label: 'Pick a point on the second line (1 of 2)' },
    { name: 'd', kind: 'pick', label: 'Pick another point on the second line (2 of 2)' },
  ],
  edges: [],
  circles: [],
  // While placing the last point, treat the cursor as d and preview both lines
  // plus the intersection so the user sees where x will land.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    const c = scene.objects.get(binds.c as ObjectId) as PointObject | undefined;
    if (!a || !b || !c) return [];
    const out: ReturnType<NonNullable<CatalogEntry['preview']>> = [
      { kind: 'auxLine', from: world(a.x, a.y), to: world(b.x, b.y) },
      { kind: 'auxLine', from: world(c.x, c.y), to: world(cursor.x, cursor.y) },
    ];
    const x = lineIntersection(a, b, c, cursor);
    if (x) out.push({ kind: 'point', at: world(x.x, x.y) });
    return out;
  },
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    const dId = binds.d as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const b = scene.objects.get(bId) as PointObject;
    const c = scene.objects.get(cId) as PointObject;
    const d = scene.objects.get(dId) as PointObject;

    // validate has already rejected parallel/coincident lines, so this is set.
    const x = lineIntersection(a, b, c, d) ?? { x: a.x, y: a.y };
    const xId = scene.addPoint(x.x, x.y);

    return {
      kind: 'construction',
      name: 'intersection_ll',
      bindings: { a: aId, b: bId, c: cId, d: dId, x: xId },
      edges: [],
      // The two lines whose crossing defines x.
      lines: [[aId, bId], [cId, dId]],
      circles: [],
    };
  },
  // Tell the engine x lies on both lines: intersection_ll defines x with
  // coll x a b and coll x c d.
  jgex: [
    { def: 'intersection_ll', signature: ['x', 'a', 'b', 'c', 'd'], produces: ['x'] },
  ],
  validate: (binds, scene) => {
    const { a, b, c, d } = binds;
    if (b !== undefined && a === b) return 'Line 1 needs two distinct points';
    if (d !== undefined && c === d) return 'Line 2 needs two distinct points';
    if (a === undefined || b === undefined || c === undefined || d === undefined) return null;
    const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
    const pb = scene.objects.get(b as ObjectId) as PointObject | undefined;
    const pc = scene.objects.get(c as ObjectId) as PointObject | undefined;
    const pd = scene.objects.get(d as ObjectId) as PointObject | undefined;
    if (!pa || !pb || !pc || !pd) return null;
    // npara/ncoll: parallel or coincident lines have no single intersection.
    if (!lineIntersection(pa, pb, pc, pd)) return 'Lines must not be parallel';
    return null;
  },
};
