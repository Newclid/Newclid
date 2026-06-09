import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { world } from '../../geometry/coords';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

type Pt = { x: number; y: number };

/**
Reflect point a across the line through b and c: project a onto the line, then
step the same distance past it. The result x has ray b-x at the mirror image of
ray b-a about line b-c (eqangle b a b c b c b x), which is the angle mirror.
**/
function reflectAcrossLine(a: Pt, b: Pt, c: Pt): Pt {
  const dx = c.x - b.x;
  const dy = c.y - b.y;
  const len2 = dx * dx + dy * dy;
  // Degenerate line (b === c): nothing to reflect across, return a unchanged.
  if (len2 < 1e-12) return { x: a.x, y: a.y };
  const t = ((a.x - b.x) * dx + (a.y - b.y) * dy) / len2;
  const footX = b.x + t * dx;
  const footY = b.y + t * dy;
  return { x: 2 * footX - a.x, y: 2 * footY - a.y };
}

/**
Angle mirror. Slots a, b, c set the angle at vertex b; the image x is the
reflection of a across line b-c, so ray b-x mirrors ray b-a about b-c. The image
is computed, never placed by hand, so the angle relation always holds.
**/
export const angleMirror: CatalogEntry = {
  name: 'angle_mirror',
  label: 'Angle Mirror',
  shortcut: 'A',
  icon: () =>
    iconWrap([
      // Mirror line through the vertex, with the original and reflected arms.
      svgEl('line', {
        x1: '11', y1: '3', x2: '11', y2: '19',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('line', {
        x1: '11', y1: '14', x2: '4', y2: '6',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('line', {
        x1: '11', y1: '14', x2: '18', y2: '6',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '4', cy: '6', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '18', cy: '6', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick the point you want to mirror' },
    { name: 'b', kind: 'pick', label: 'Pick the vertex of the mirror angle' },
    { name: 'c', kind: 'pick', label: 'Pick a point on the mirror line' },
  ],
  edges: [],
  circles: [],
  // While placing the mirror-line point, treat the cursor as c and preview the
  // mirror line plus the reflected arm and image so the angle mirror is clear.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const b = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!a || !b) return [];
    const x = reflectAcrossLine(a, b, cursor);
    return [
      { kind: 'auxLine', from: world(b.x, b.y), to: world(cursor.x, cursor.y) },
      { kind: 'auxLine', from: world(b.x, b.y), to: world(a.x, a.y) },
      { kind: 'auxLine', from: world(b.x, b.y), to: world(x.x, x.y) },
      { kind: 'point', at: world(x.x, x.y) },
    ];
  },
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const b = scene.objects.get(bId) as PointObject;
    const c = scene.objects.get(cId) as PointObject;

    const x = reflectAcrossLine(a, b, c);
    const xId = scene.addPoint(x.x, x.y);

    return {
      kind: 'construction',
      name: 'angle_mirror',
      // The two arms of the angle and the reflected arm to the image.
      bindings: { a: aId, b: bId, c: cId, x: xId },
      edges: [[bId, aId], [bId, cId], [bId, xId]],
      circles: [],
    };
  },
  // Tell the engine ray b-x mirrors ray b-a about line b-c:
  // angle_mirror defines x with eqangle b a b c b c b x.
  jgex: [
    { def: 'angle_mirror', signature: ['x', 'a', 'b', 'c'], produces: ['x'] },
  ],
  validate: (binds, scene) => {
    const { a, b, c } = binds;
    if (a === undefined || b === undefined || c === undefined) return null;
    if (a === b || b === c || a === c) return 'Three distinct points required';
    const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
    const pb = scene.objects.get(b as ObjectId) as PointObject | undefined;
    const pc = scene.objects.get(c as ObjectId) as PointObject | undefined;
    if (!pa || !pb || !pc) return null;
    // ncoll a b c: a collinear angle has no well-defined mirror.
    const cross = (pa.x - pb.x) * (pc.y - pb.y) - (pa.y - pb.y) * (pc.x - pb.x);
    if (Math.abs(cross) < 1e-9) return 'Points must not be collinear';
    return null;
  },
};
