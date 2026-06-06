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

// The (0, 1 or 2) intersection points of two circles given centre and radius.
function circleCircleIntersections(o: Pt, r1: number, w: Pt, r2: number): Pt[] {
  const dx = w.x - o.x;
  const dy = w.y - o.y;
  const d = Math.hypot(dx, dy);
  // Concentric, too far apart, or one strictly inside the other: no crossing.
  if (d < 1e-9 || d > r1 + r2 + 1e-9 || d < Math.abs(r1 - r2) - 1e-9) return [];
  const a = (r1 * r1 - r2 * r2 + d * d) / (2 * d);
  const h = Math.sqrt(Math.max(0, r1 * r1 - a * a));
  const mx = o.x + (a * dx) / d;
  const my = o.y + (a * dy) / d;
  if (h < 1e-9) return [{ x: mx, y: my }]; // tangent: single point
  const ox = (-dy / d) * h;
  const oy = (dx / d) * h;
  return [{ x: mx + ox, y: my + oy }, { x: mx - ox, y: my - oy }];
}

/**
Intersection of two circles. Slots o and w are the centres of two existing
circles; the tool reads each circle's radius and places the points where they
cross: both crossings, or a single point when the circles are tangent. Each
crossing lies on both circles (cong o x o ra, cong w x w rb).
**/
export const intersectionCC: CatalogEntry = {
  name: 'intersection_cc',
  label: 'Intersection of Circles',
  shortcut: 'Z',
  icon: () =>
    iconWrap([
      svgEl('circle', {
        cx: '8', cy: '11', r: '5',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', {
        cx: '14', cy: '11', r: '5',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '11', cy: '7', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '11', cy: '15', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'o', kind: 'pick-existing', label: "Pick the first circle's centre" },
    { name: 'w', kind: 'pick-existing', label: "Pick the second circle's centre" },
  ],
  edges: [],
  circles: [],
  sketch: (binds, scene) => {
    const oId = binds.o as ObjectId;
    const wId = binds.w as ObjectId;
    const c1 = circleAtCentre(scene, oId)!;
    const c2 = circleAtCentre(scene, wId)!;
    const pts = circleCircleIntersections(c1.center, c1.radius, c2.center, c2.radius);

    // ra and rb are the circles' radius points, needed for the JGEX emit.
    const bindings: Record<string, ObjectId> = { o: oId, w: wId, ra: c1.through, rb: c2.through };
    bindings.x = scene.addPoint(pts[0].x, pts[0].y);
    // A second, distinct crossing exists unless the circles are tangent.
    if (pts.length > 1) {
      bindings.y = scene.addPoint(pts[1].x, pts[1].y);
    }

    return {
      kind: 'construction',
      name: 'intersection_cc',
      bindings,
      edges: [],
      circles: [],
    };
  },
  /**
  x is one crossing (on both circles); y is the other, defined as the second
  circle-circle intersection through x. The y block is skipped on emit when the
  circles are tangent and y was never created.
  **/
  jgex: [
    {
      combine: 'intersect',
      clauses: [
        { def: 'on_circle', signature: ['x', 'o', 'ra'], produces: ['x'] },
        { def: 'on_circle', signature: ['x', 'w', 'rb'], produces: ['x'] },
      ],
    },
    { def: 'intersection_cc', signature: ['y', 'o', 'w', 'x'], produces: ['y'] },
  ],
  validate: (binds, scene) => {
    const { o, w } = binds;
    if (o !== undefined && !circleAtCentre(scene, o as ObjectId)) {
      return 'Pick the centre of an existing circle';
    }
    if (w !== undefined) {
      const c2 = circleAtCentre(scene, w as ObjectId);
      if (!c2) return 'Pick the centre of an existing circle';
      if (o === w) return 'Pick two different circles';
      const c1 = circleAtCentre(scene, o as ObjectId);
      if (c1 && circleCircleIntersections(c1.center, c1.radius, c2.center, c2.radius).length === 0) {
        return 'The two circles do not intersect';
      }
    }
    return null;
  },
};
