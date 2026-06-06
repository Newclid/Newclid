import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { circumcenter } from '../../geometry/primitives';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Circle through three points (the circumcircle). The user picks three
non-collinear points; the circle through them is drawn and its centre (the
circumcentre, equidistant from all three) is placed as a point.
**/
export const circumcircle: CatalogEntry = {
  name: 'circumcircle',
  label: 'Circle (3 points)',
  shortcut: 'O',
  icon: () =>
    iconWrap([
      svgEl('circle', {
        cx: '11', cy: '11', r: '7',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      // three points sitting on the circle
      svgEl('circle', { cx: '11', cy: '4', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '17', cy: '15', r: '1.6', fill: 'currentColor' }),
      svgEl('circle', { cx: '5', cy: '15', r: '1.6', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick a point on the circle (1 of 3)' },
    { name: 'b', kind: 'pick', label: 'Pick a point on the circle (2 of 3)' },
    { name: 'c', kind: 'pick', label: 'Pick a point on the circle (3 of 3)' },
  ],
  edges: [],
  circles: [],
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    const pa = scene.objects.get(aId) as PointObject;
    const pb = scene.objects.get(bId) as PointObject;
    const pc = scene.objects.get(cId) as PointObject;

    // The circumcentre; validate has rejected collinear points, so it exists.
    const cc = circumcenter(pa, pb, pc) ?? { x: pa.x, y: pa.y };
    const xId = scene.addPoint(cc.x, cc.y);

    return {
      kind: 'construction',
      name: 'circumcircle',
      bindings: { a: aId, b: bId, c: cId, x: xId },
      edges: [],
      circles: [],
      circumcircles: [[aId, bId, cId]],
    };
  },
  // While placing the third point, preview the circle through the two placed
  // points and the cursor. (Two points alone can't define a circle, so this
  // only shows once points a and b exist.)
  preview: (binds, scene, cursor) => {
    const pa = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    const pb = scene.objects.get(binds.b as ObjectId) as PointObject | undefined;
    if (!pa || !pb) return [];
    const cc = circumcenter(pa, pb, cursor);
    if (!cc) return []; // cursor collinear with a and b: no finite circle
    return [{ kind: 'circle', center: cc, through: { x: pa.x, y: pa.y } }];
  },
  // Tell the engine the centre is equidistant from the three points:
  // circumcenter defines x with cong x a x b, cong x b x c.
  jgex: [
    { def: 'circumcenter', signature: ['x', 'a', 'b', 'c'], produces: ['x'] },
  ],
  validate: (binds, scene) => {
    const { a, b, c } = binds;
    if (a === undefined || b === undefined || c === undefined) return null;
    if (a === b || b === c || a === c) return 'Three distinct points required';
    const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
    const pb = scene.objects.get(b as ObjectId) as PointObject | undefined;
    const pc = scene.objects.get(c as ObjectId) as PointObject | undefined;
    if (!pa || !pb || !pc) return null;
    // Reject (near-)collinear points: no unique circle through them.
    const cross = (pa.x - pb.x) * (pc.y - pb.y) - (pa.y - pb.y) * (pc.x - pb.x);
    if (Math.abs(cross) < 1e-9) return 'Points must not be collinear';
    return null;
  },
};
