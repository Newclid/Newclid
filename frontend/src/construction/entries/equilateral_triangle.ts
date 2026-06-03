import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Apex of the equilateral triangle on base a-b, on whichever side of the base the
cursor is. The apex sits on the perpendicular bisector at height (sqrt3/2)|ab|
from the midpoint, so all three sides come out equal; the cursor only chooses
up or down.
**/
function equilateralApex(
  a: { x: number; y: number },
  b: { x: number; y: number },
  cursor: { x: number; y: number },
): { x: number; y: number } {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const len = Math.hypot(dx, dy);
  const mx = (a.x + b.x) / 2;
  const my = (a.y + b.y) / 2;
  // Unit perpendicular to the base and the equilateral apex height.
  const nx = -dy / len;
  const ny = dx / len;
  const h = (Math.sqrt(3) / 2) * len;
  // Which half-plane is the cursor in? (0 falls through to the +n side.)
  const cross = dx * (cursor.y - a.y) - dy * (cursor.x - a.x);
  const side = cross < 0 ? -1 : 1;
  return { x: mx + side * h * nx, y: my + side * h * ny };
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
    { name: 'a', kind: 'pick', label: 'Pick first base point' },
    { name: 'b', kind: 'pick', label: 'Pick second base point' },
    {
      name: 'c',
      kind: 'derive',
      label: 'Place the apex (above or below the base)',
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
  // While placing the apex, preview the two equal sides closing the triangle.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    const apex = equilateralApex(a, b, cursor);
    return [
      { kind: 'auxLine', from: world(a.x, a.y), to: world(apex.x, apex.y) },
      { kind: 'auxLine', from: world(b.x, b.y), to: world(apex.x, apex.y) },
    ];
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
