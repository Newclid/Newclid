import type { CatalogEntry } from '../catalog-types';
import type { ObjectId } from '../../geometry/types-object';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Line through two points: infinite in both directions. Draws the full line
through a and b (the renderer extends it past the viewport); does not create
a new point.
**/
export const line: CatalogEntry = {
  name: 'line',
  label: 'Line',
  shortcut: 'L',
  icon: () =>
    iconWrap([
      // Runs to the icon edges to read as infinite, with two points on it.
      svgEl('line', {
        x1: '2', y1: '17', x2: '20', y2: '5',
        stroke: 'currentColor', 'stroke-width': '1.4',
      }),
      svgEl('circle', { cx: '8', cy: '13', r: '1.8', fill: 'currentColor' }),
      svgEl('circle', { cx: '14', cy: '9', r: '1.8', fill: 'currentColor' }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick the first point on the line' },
    { name: 'b', kind: 'pick', label: 'Pick the second point on the line' },
  ],
  edges: [],
  circles: [],
  sketch: (binds) => {
    const aId = binds.a as ObjectId;
    const bId = binds.b as ObjectId;
    return {
      kind: 'construction',
      name: 'line',
      bindings: { a: aId, b: bId },
      edges: [],
      lines: [[aId, bId]],
      circles: [],
    };
  },
  validate: (binds) =>
    binds.a !== undefined && binds.b !== undefined && binds.a === binds.b
      ? 'Two distinct points required'
      : null,
};
