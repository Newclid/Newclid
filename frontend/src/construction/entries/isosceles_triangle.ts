import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

type Pt = { x: number; y: number };

/**
The apex for an isosceles triangle on base a-b: any point on the perpendicular
bisector of a-b. Projecting the cursor onto that bisector keeps the two legs
(apex-a and apex-b) equal at whatever height the cursor picks.
**/
function isoApex(a: Pt, b: Pt, cursor: Pt): Pt {
  const mx = (a.x + b.x) / 2;
  const my = (a.y + b.y) / 2;
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const len = Math.hypot(dx, dy);
  // Unit vector along the perpendicular bisector (perpendicular to the base).
  const nx = -dy / len;
  const ny = dx / len;
  // Project the cursor offset from the midpoint onto the bisector direction.
  const t = (cursor.x - mx) * nx + (cursor.y - my) * ny;
  return { x: mx + nx * t, y: my + ny * t };
}

// Endpoints of the perpendicular-bisector guide, spanning the base length each
// way from the midpoint so the apex's locus is visible without running offscreen.
function bisectorGuide(a: Pt, b: Pt): { from: Pt; to: Pt } {
  const mx = (a.x + b.x) / 2;
  const my = (a.y + b.y) / 2;
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const len = Math.hypot(dx, dy);
  const nx = -dy / len;
  const ny = dx / len;
  return {
    from: { x: mx - nx * len, y: my - ny * len },
    to: { x: mx + nx * len, y: my + ny * len },
  };
}

/**
Isosceles triangle. Slots a and b set the base; slot c is the apex, a derive
slot constrained to the perpendicular bisector of the base so the two legs stay
equal. The cursor's distance along the bisector sets the height (and the side).
**/
export const isoscelesTriangle: CatalogEntry = {
  name: 'iso_triangle',
  label: 'Isosceles Triangle',
  shortcut: 'I',
  icon: () =>
    iconWrap([
      // A tall, narrow triangle to read as isosceles rather than equilateral.
      svgEl('polygon', {
        points: '11,3 18,19 4,19',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '11', cy: '3', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '18', cy: '19', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '4', cy: '19', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick first base point' },
    { name: 'b', kind: 'pick', label: 'Pick second base point' },
    {
      name: 'c',
      kind: 'derive',
      label: 'Place the apex along the perpendicular bisector',
      // Snap the apex onto the perpendicular bisector so the legs stay equal.
      project: (binds, scene, cursor) => {
        const a = scene.objects.get(binds.a as ObjectId) as PointObject;
        const b = scene.objects.get(binds.b as ObjectId) as PointObject;
        const apex = isoApex(a, b, cursor);
        return world(apex.x, apex.y);
      },
      // Show the bisector the apex is constrained to, so it's clear it can slide
      // up or down to any height while staying isosceles.
      preview: (binds, scene) => {
        const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
        const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
        if (!a || !b) return [];
        const { from, to } = bisectorGuide(a, b);
        return [{ kind: 'auxLine', from: world(from.x, from.y), to: world(to.x, to.y) }];
      },
    },
  ],
  edges: [{ pointIds: ['a', 'b'] }],
  circles: [],
  // Preview the two equal legs to the apex the cursor currently selects.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    const apex = isoApex(a, b, cursor);
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
      name: 'iso_triangle',
      bindings: { a: aId, b: bId, c: cId },
      edges: [[aId, bId], [bId, cId], [cId, aId]],
      circles: [],
    };
  },
  // Tell the engine the apex is equidistant from the base points: iso_triangle_
  // vertex defines c with cong c a c b (the two legs equal).
  jgex: [
    { def: 'iso_triangle_vertex', signature: ['c', 'a', 'b'], produces: ['c'] },
  ],
  validate: (binds) =>
    binds.a !== undefined && binds.b !== undefined && binds.a === binds.b
      ? 'Two distinct base points required'
      : null,
};
