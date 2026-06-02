import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

export const angleBisector: CatalogEntry = {
  name: 'angle_bisector',
  label: 'Angle Bisector',
  shortcut: 'B',
  icon: () =>
    iconWrap([
      // Two arms opening symmetrically above and below the horizontal,
      // so the bisector visibly splits the angle in half.
      svgEl('line', {
        x1: '4', y1: '11', x2: '20', y2: '5',
        stroke: 'currentColor', 'stroke-width': '1.2',
      }),
      svgEl('line', {
        x1: '4', y1: '11', x2: '20', y2: '17',
        stroke: 'currentColor', 'stroke-width': '1.2',
      }),
      // The bisector: horizontal, exactly between the two arms.
      svgEl('line', {
        x1: '4', y1: '11', x2: '20', y2: '11',
        stroke: 'red', 'stroke-width': '1.2',
      }),
      svgEl('circle', { cx: '20', cy: '11', r: '1.8', fill: 'red' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick first ray point' },
    { name: 'b', kind: 'pick', label: 'Pick angle vertex' },
    { name: 'c', kind: 'pick', label: 'Pick second ray point' },
  ],
  edges: [{ pointIds: ['a', 'b'] }, { pointIds: ['b', 'c'] }],
  circles: [],
  sketch: (binds, scene) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    const cId = binds.c as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const b = scene.objects.get(bId) as PointObject;
    const c = scene.objects.get(cId) as PointObject;

    // Unit vectors along the two arms, from the vertex b.
    const baLen = Math.hypot(a.x - b.x, a.y - b.y);
    const bcLen = Math.hypot(c.x - b.x, c.y - b.y);
    const uBA = { x: (a.x - b.x) / baLen, y: (a.y - b.y) / baLen };
    const uBC = { x: (c.x - b.x) / bcLen, y: (c.y - b.y) / bcLen };

    // The internal bisector direction is the (normalized) sum of the arm units.
    let dx = uBA.x + uBC.x;
    let dy = uBA.y + uBC.y;
    const dLen = Math.hypot(dx, dy);
    dx /= dLen;
    dy /= dLen;

    // Place x a natural distance out along the bisector ray from b.
    const L = (baLen + bcLen) / 2;
    const xId = scene.addPoint(b.x + dx * L, b.y + dy * L);
    scene.setPointColor(xId, 'red');

    return {
      kind: 'construction',
      name: 'angle_bisector',
      bindings: { x: xId, a: aId, b: bId, c: cId },
      edges: [[aId, bId], [bId, cId]],
      lines: [[bId, xId]],
      circles: [],
    };
  },
  jgex: [
    { def: 'angle_bisector', signature: ['x', 'a', 'b', 'c'], produces: ['x'] },
  ],
  validate: (binds, scene) => {
    const { a, b, c } = binds;
    if (a === undefined || b === undefined || c === undefined) return null;
    if (a === b || b === c || a === c) return 'Three distinct points required';
    const pa = scene.objects.get(a as ObjectId) as PointObject | undefined;
    const pb = scene.objects.get(b as ObjectId) as PointObject | undefined;
    const pc = scene.objects.get(c as ObjectId) as PointObject | undefined;
    if (!pa || !pb || !pc) return null;
    // ncoll a b c: reject (near-)collinear points via the cross product.
    const cross = (pa.x - pb.x) * (pc.y - pb.y) - (pa.y - pb.y) * (pc.x - pb.x);
    if (Math.abs(cross) < 1e-9) return 'Points must not be collinear';
    return null;
  },
};
