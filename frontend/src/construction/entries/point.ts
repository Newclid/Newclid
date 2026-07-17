import type { CatalogEntry } from '../catalog-types';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Plain point placement. A single place-free slot drops a fresh point at the
click location (never snapping to an existing one); sketch returns null because
the point is already created by the slot, with no construction wrapping it.
**/
export const point: CatalogEntry = {
  name: 'point',
  label: 'Point',
  shortcut: 'P',
  icon: () =>
    iconWrap([
      svgEl('circle', { cx: '11', cy: '11', r: '3', fill: 'currentColor' }),
      svgEl(
        'text',
        {
          x: '15',
          y: '9',
          'font-family': 'var(--font-display)',
          'font-style': 'italic',
          'font-size': '9',
          fill: 'currentColor',
        },
        'A',
      ),
    ]),
  slots: [{ name: 'p', kind: 'place-free', label: 'Place a point' }],
  edges: [],
  circles: [],
  // The place-free slot already added the point; nothing more to emit.
  sketch: () => null,
};
