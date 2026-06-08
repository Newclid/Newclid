import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import type { Scene } from '../../scene/scene';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

type Pt = { x: number; y: number };

interface PickedCircle {
  center: PointObject;
  through: ObjectId; // a point on the circle, defining its radius
  radius: number;
}

/**
Find the center-through circle whose centre is the given point, reading its
radius from the centre and the point it passes through. Returns null when no
circle is centred there.
**/
function circleAtCentre(scene: Scene, centreId: ObjectId): PickedCircle | null {
  const centre = scene.objects.get(centreId);
  if (centre?.kind !== 'point') return null;
  for (const o of scene.objects.values()) {
    if (o.kind !== 'circle' || o.mode !== 'center-through' || o.center !== centreId) continue;
    const through = scene.objects.get(o.through);
    if (through?.kind !== 'point') continue;
    return {
      center: centre,
      through: through.id,
      radius: Math.hypot(through.x - centre.x, through.y - centre.y),
    };
  }
  return null;
}

// The (0, 1 or 2) crossings of line a-b with the circle centred at o, radius r.
function lineCircleIntersections(a: Pt, b: Pt, o: Pt, r: number): Pt[] {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const len2 = dx * dx + dy * dy;
  if (len2 < 1e-12) return [];
  // Foot of the centre on the line, and the centre's distance to it.
  const t = ((o.x - a.x) * dx + (o.y - a.y) * dy) / len2;
  const fx = a.x + t * dx;
  const fy = a.y + t * dy;
  const dist = Math.hypot(o.x - fx, o.y - fy);
  if (dist > r + 1e-9) return []; // the line misses the circle
  const half = Math.sqrt(Math.max(0, r * r - dist * dist));
  if (half < 1e-9) return [{ x: fx, y: fy }]; // tangent: single point
  const len = Math.sqrt(len2);
  const ux = dx / len;
  const uy = dy / len;
  return [{ x: fx + ux * half, y: fy + uy * half }, { x: fx - ux * half, y: fy - uy * half }];
}

/**
Intersection of a line and a circle. Slots a and b set the line; slot o is the
centre of an existing circle, whose radius the tool reads. It places where the
line crosses that circle: both points, or a single point when the line is
tangent. Each crossing lies on the line and the circle (coll x a b, cong o x o ra).
**/
export const intersectionLC: CatalogEntry = {
  name: 'intersection_lc',
  label: 'Intersection of Line and Circle',
  shortcut: 'J',
  icon: () =>
    iconWrap([
      svgEl('circle', {
        cx: '11', cy: '12', r: '6',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('line', {
        x1: '3', y1: '7', x2: '19', y2: '17',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '6', cy: '9', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '16', cy: '15', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick a point on the line (1 of 2)' },
    { name: 'b', kind: 'pick', label: 'Pick another point on the line (2 of 2)' },
    { name: 'o', kind: 'pick-existing', label: 'Pick the centre of the circle' },
  ],
  edges: [],
  circles: [],
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const oId = binds.o as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const b = scene.objects.get(bId) as PointObject;
    const circ = circleAtCentre(scene, oId)!;
    const pts = lineCircleIntersections(a, b, circ.center, circ.radius);

    // ra is the circle's radius point, needed for the JGEX emit.
    const bindings: Record<string, ObjectId> = { a: aId, b: bId, o: oId, ra: circ.through };
    bindings.x = scene.addPoint(pts[0].x, pts[0].y);
    // A second, distinct crossing exists unless the line is tangent.
    if (pts.length > 1) {
      bindings.y = scene.addPoint(pts[1].x, pts[1].y);
    }

    return {
      kind: 'construction',
      name: 'intersection_lc',
      bindings,
      edges: [],
      // The secant line; the circle is the existing object the user picked.
      lines: [[aId, bId]],
      circles: [],
    };
  },
  /**
  x is one crossing (on the line and the circle); y is the other, defined as the
  second line-circle intersection through x. The y block is skipped on emit when
  the line is tangent and y was never created.
  **/
  jgex: [
    {
      combine: 'intersect',
      clauses: [
        { def: 'on_line', signature: ['x', 'a', 'b'], produces: ['x'] },
        { def: 'on_circle', signature: ['x', 'o', 'ra'], produces: ['x'] },
      ],
    },
    { def: 'intersection_lc', signature: ['y', 'a', 'o', 'x'], produces: ['y'] },
  ],
  validate: (binds, scene) => {
    const { a, b, o } = binds;
    if (a !== undefined && b !== undefined && a === b) return 'The line needs two distinct points';
    if (o !== undefined) {
      const circ = circleAtCentre(scene, o as ObjectId);
      if (!circ) return 'Pick the centre of an existing circle';
      if (a === undefined || b === undefined) return null;
      const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
      const pb = scene.objects.get(b as ObjectId) as PointObject | undefined;
      if (!pa || !pb) return null;
      if (lineCircleIntersections(pa, pb, circ.center, circ.radius).length === 0) {
        return 'The line does not cross the circle';
      }
    }
    return null;
  },
};
