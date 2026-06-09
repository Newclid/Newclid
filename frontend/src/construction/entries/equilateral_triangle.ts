import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

type Pt = { x: number; y: number };

/**
The two equilateral apexes for base a-b: both sit on the perpendicular bisector
at height (sqrt3/2)|ab| from the midpoint, one on each side, so either makes an
equal-sided triangle.
**/
function apexCandidates(a: Pt, b: Pt): { up: Pt; down: Pt } {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const len = Math.hypot(dx, dy);
  const mx = (a.x + b.x) / 2;
  const my = (a.y + b.y) / 2;
  // Unit perpendicular to the base, scaled to the equilateral apex height.
  const h = (Math.sqrt(3) / 2) * len;
  const ox = (-dy / len) * h;
  const oy = (dx / len) * h;
  return { up: { x: mx + ox, y: my + oy }, down: { x: mx - ox, y: my - oy } };
}

// The apex on whichever side of the base the cursor is (0 falls through to up).
function equilateralApex(a: Pt, b: Pt, cursor: Pt): Pt {
  const { up, down } = apexCandidates(a, b);
  const cross = (b.x - a.x) * (cursor.y - a.y) - (b.y - a.y) * (cursor.x - a.x);
  return cross < 0 ? down : up;
}

/**
Equilateral triangle. Slots a and b set the base; slot c is the apex, a derive
slot constrained to the equilateral position so the triangle is always equal-
sided. The cursor's side of the base decides whether the apex lands above or
below it.
**/
export const equilateralTriangle: CatalogEntry = {
  name: 'eq_triangle',
  label: 'Equilateral Triangle',
  shortcut: 'E',
  icon: () =>
    iconWrap([
      svgEl('polygon', {
        points: '11,4 19,18 3,18',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '11', cy: '4', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '19', cy: '18', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '3', cy: '18', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick the first base point (1 of 2)' },
    { name: 'b', kind: 'pick', label: 'Pick the second base point (2 of 2)' },
    {
      name: 'c',
      kind: 'derive',
      label: 'Place the apex above or below the base',
      // Snap the apex to the equilateral position on the cursor's side.
      project: (binds, scene, cursor) => {
        const a = scene.objects.get(binds.a as ObjectId) as PointObject;
        const b = scene.objects.get(binds.b as ObjectId) as PointObject;
        const apex = equilateralApex(a, b, cursor);
        return world(apex.x, apex.y);
      },
      // The two triangle sides already preview the apex (see entry-level
      // preview below), so the derive slot draws no extra guide line.
      preview: () => [],
    },
  ],
  edges: [{ pointIds: ['a', 'b'] }],
  circles: [],
  // While placing the apex, preview both possible triangles so the user sees
  // the apex can land above or below the base. The cursor-side apex is the one
  // the derive slot highlights as the point to be placed.
  preview: (binds, scene) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    const { up, down } = apexCandidates(a, b);
    return [up, down].flatMap((apex) => [
      { kind: 'auxLine' as const, from: world(a.x, a.y), to: world(apex.x, apex.y) },
      { kind: 'auxLine' as const, from: world(b.x, b.y), to: world(apex.x, apex.y) },
    ]);
  },
  sketch: (binds) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    return {
      kind: 'construction',
      name: 'eq_triangle',
      bindings: { a: aId, b: bId, c: cId },
      edges: [[aId, bId], [bId, cId], [cId, aId]],
      circles: [],
    };
  },
  jgex: [
    { def: 'eq_triangle', signature: ['c', 'a', 'b'], produces: ['c'] },
  ],
  validate: (binds) =>
    binds.a !== undefined && binds.b !== undefined && binds.a === binds.b
      ? 'Two distinct base points required'
      : null,
};
