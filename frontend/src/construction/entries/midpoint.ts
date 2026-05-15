import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

export const midpoint: CatalogEntry = {
  name: 'midpoint',
  label: 'Midpoint',
  shortcut: 'M',
  icon: () =>
    iconWrap([
      svgEl('line', {
        x1: '4', y1: '11', x2: '18', y2: '11',
        stroke: 'currentColor', 'stroke-width': '1.2',
      }),
      svgEl('circle', { cx: '4', cy: '11', r: '1.8', fill: 'currentColor' }),
      svgEl('circle', { cx: '18', cy: '11', r: '1.8', fill: 'currentColor' }),
      svgEl('circle', { cx: '11', cy: '11', r: '1.8', fill: 'red' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick first point' },
    { name: 'b', kind: 'pick', label: 'Pick second point' },
  ],
  edges: [{ pointIds: ['a', 'b'] }],
  circles: [],
  sketch: (b, scene) => {
    const aId = b.a as ObjectId;
    const bId = b.b as ObjectId;
    const a = scene.objects.get(aId) as PointObject;
    const bb = scene.objects.get(bId) as PointObject;
    const mId = scene.addPoint((a.x + bb.x) / 2, (a.y + bb.y) / 2);
    scene.setPointColor(mId, 'red');
    return {
      kind: 'construction',
      name: 'midpoint',
      bindings: { a: aId, b: bId, m: mId },
      edges: [[aId, bId]],
      circles: [],
    };
  },
  validate: (b) =>
    b.a !== undefined && b.b !== undefined && b.a === b.b
      ? 'Two distinct points required'
      : null,
};
