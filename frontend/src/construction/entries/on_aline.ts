import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

type Pt = { x: number; y: number };

/**
The two directions of the line through a that copy the source angle onto ray
a-b: one as (dc, de) and the mirror as (de, dc). In angles the copied direction
is dir(ab) + dir(dc) - dir(de); swapping the arms mirrors it across a-b.
**/
function alineAngles(a: Pt, b: Pt, c: Pt, d: Pt, e: Pt): { ang1: number; ang2: number } {
  const angAB = Math.atan2(b.y - a.y, b.x - a.x);
  const angDC = Math.atan2(c.y - d.y, c.x - d.x);
  const angDE = Math.atan2(e.y - d.y, e.x - d.x);
  return { ang1: angAB + angDC - angDE, ang2: angAB + angDE - angDC };
}

// Smallest difference between two line angles (mod 180 degrees).
function angDist180(u: number, v: number): number {
  const d = Math.abs(u - v) % Math.PI;
  return Math.min(d, Math.PI - d);
}

// Foot of cursor projected onto the line through a with direction angle ang.
function projectOnAngle(a: Pt, ang: number, cursor: Pt): Pt {
  const ux = Math.cos(ang);
  const uy = Math.sin(ang);
  const t = (cursor.x - a.x) * ux + (cursor.y - a.y) * uy;
  return { x: a.x + ux * t, y: a.y + uy * t };
}

/**
Angle transfer onto a line. Slots c, d, e set the source angle (dc, de) at vertex
d; slots a and b set the vertex and the reference ray a-b. Slot x is a derive
slot on the line through a that copies the angle, so angle x-a-b equals angle
c-d-e (eqangle a x a b d c d e). The angle can land on either side of a-b: the
cursor picks which, and the mirror side emits the swapped source arms.
**/
export const onAline: CatalogEntry = {
  name: 'on_aline',
  label: 'Angle Transfer (line)',
  shortcut: 'H',
  icon: () =>
    iconWrap([
      svgEl('line', {
        x1: '4', y1: '17', x2: '20', y2: '11',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('line', {
        x1: '4', y1: '17', x2: '13', y2: '4',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('path', {
        d: 'M11 14.5 A 7 7 0 0 0 8.2 9.4',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.1',
      }),
      svgEl('circle', { cx: '4', cy: '17', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '20', cy: '11', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'c', kind: 'pick-existing', label: 'Angle to copy: first arm point (c)' },
    { name: 'd', kind: 'pick-existing', label: 'Angle to copy: vertex (d)' },
    { name: 'e', kind: 'pick-existing', label: 'Angle to copy: second arm point (e)' },
    { name: 'a', kind: 'pick-existing', label: 'Vertex to copy the angle onto (a)' },
    { name: 'b', kind: 'pick-existing', label: 'Reference line point (b): the angle is measured from a-b' },
    {
      name: 'x',
      kind: 'derive',
      label: 'Place x (either side of a-b sets the angle direction)',
      // Snap x onto whichever of the two copied-angle lines is nearer the cursor.
      project: (binds, scene, cursor) => {
        const a = scene.objects.get(binds.a as ObjectId) as PointObject;
        const b = scene.objects.get(binds.b as ObjectId) as PointObject;
        const c = scene.objects.get(binds.c as ObjectId) as PointObject;
        const d = scene.objects.get(binds.d as ObjectId) as PointObject;
        const e = scene.objects.get(binds.e as ObjectId) as PointObject;
        const { ang1, ang2 } = alineAngles(a, b, c, d, e);
        const p1 = projectOnAngle(a, ang1, cursor);
        const p2 = projectOnAngle(a, ang2, cursor);
        const d1 = Math.hypot(p1.x - cursor.x, p1.y - cursor.y);
        const d2 = Math.hypot(p2.x - cursor.x, p2.y - cursor.y);
        const best = d2 < d1 ? p2 : p1;
        return world(best.x, best.y);
      },
      preview: () => [],
    },
  ],
  edges: [],
  circles: [],
  // Preview the reference ray a-b and both copied-angle lines, so the user sees
  // the angle can land on either side.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    const c = scene.objects.get(binds.c as ObjectId) as PointObject | undefined;
    const d = scene.objects.get(binds.d as ObjectId) as PointObject | undefined;
    const e = scene.objects.get(binds.e as ObjectId) as PointObject | undefined;
    if (!a || !b || !c || !d || !e) return [];
    const { ang1, ang2 } = alineAngles(a, b, c, d, e);
    const reach = Math.hypot(cursor.x - a.x, cursor.y - a.y);
    const len = Math.max(reach, Math.hypot(b.x - a.x, b.y - a.y)) * 1.1;
    const lineAt = (ang: number) => ({
      kind: 'auxLine' as const,
      from: world(a.x - Math.cos(ang) * len, a.y - Math.sin(ang) * len),
      to: world(a.x + Math.cos(ang) * len, a.y + Math.sin(ang) * len),
    });
    return [
      { kind: 'auxLine', from: world(a.x, a.y), to: world(b.x, b.y) },
      lineAt(ang1),
      lineAt(ang2),
    ];
  },
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    const dId = binds.d as ObjectId;
    const eId = binds.e as ObjectId;
    const xId = binds.x as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const b = scene.objects.get(bId) as PointObject;
    const c = scene.objects.get(cId) as PointObject;
    const d = scene.objects.get(dId) as PointObject;
    const e = scene.objects.get(eId) as PointObject;
    const x = scene.objects.get(xId) as PointObject;

    // Which side did x land on? Pick the source-arm order whose copied angle
    // matches x's direction, so the emitted eqangle is correct for that side.
    const { ang1, ang2 } = alineAngles(a, b, c, d, e);
    const angX = Math.atan2(x.y - a.y, x.x - a.x);
    const mirror = angDist180(angX, ang2) < angDist180(angX, ang1);

    return {
      kind: 'construction',
      name: 'on_aline',
      // On the mirror side the source arms swap (d e d c instead of d c d e).
      bindings: {
        a: aId,
        b: bId,
        c: mirror ? eId : cId,
        d: dId,
        e: mirror ? cId : eId,
        x: xId,
      },
      edges: [],
      // The copied-angle line through a and x.
      lines: [[aId, xId]],
      circles: [],
    };
  },
  // The angle x-a-b copies the angle at d: on_aline defines x with
  // eqangle a x a b d c d e (arms swapped on the mirror side).
  jgex: [
    { def: 'on_aline', signature: ['x', 'a', 'b', 'c', 'd', 'e'], produces: ['x'] },
  ],
  validate: (binds, scene) => {
    const { a, b, c, d, e } = binds;
    if (a !== undefined && b !== undefined && a === b) {
      return 'The reference ray needs two distinct points (a, b)';
    }
    if (c === undefined || d === undefined || e === undefined) return null;
    const pc = scene.objects.get(c as ObjectId) as PointObject | undefined;
    const pd = scene.objects.get(d as ObjectId) as PointObject | undefined;
    const pe = scene.objects.get(e as ObjectId) as PointObject | undefined;
    if (!pc || !pd || !pe) return null;
    // ncoll c d e: a flat source angle has no well-defined direction to copy.
    const cross = (pc.x - pd.x) * (pe.y - pd.y) - (pc.y - pd.y) * (pe.x - pd.x);
    if (Math.abs(cross) < 1e-9) return 'Points c, d and e must not be collinear';
    return null;
  },
};
