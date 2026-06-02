import type { CatalogEntry } from '../catalog-types';
import type { ObjectId } from '../../geometry/types-object';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Segment through two points: a finite line with a beginning and an end.
Draws the segment a-b; does not create a new point.
**/
export const segment: CatalogEntry = {
  name: 'segment',
  label: 'Segment',
  shortcut: 'S',
  icon: () =>
    iconWrap([
      svgEl('line', {
        x1: '4', y1: '11', x2: '18', y2: '11',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '4', cy: '11', r: '1.8', fill: 'currentColor' }),
      svgEl('circle', { cx: '18', cy: '11', r: '1.8', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick first point' },
    { name: 'b', kind: 'pick', label: 'Pick second point' },
  ],
  edges: [{ pointIds: ['a', 'b'] }],
  circles: [],
  sketch: (binds) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    return {
      kind: 'construction',
      name: 'segment',
      bindings: { a: aId, b: bId },
      edges: [[aId, bId]],
      circles: [],
    };
  },
  validate: (binds) =>
    binds.a !== undefined && binds.b !== undefined && binds.a === binds.b
      ? 'Two distinct points required'
      : null,
};
