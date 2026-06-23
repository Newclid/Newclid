import type { CatalogEntry } from '../catalog-types';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Select (cursor) mode. It has no slots, so clicks on the canvas are inert and
nothing is ever sketched; point dragging and selection are handled by the
pointer layer, not by this tool.
**/
export const select: CatalogEntry = {
  name: 'select',
  label: 'Edit Point',
  shortcut: 'V',
  icon: () =>
    iconWrap([
      svgEl('path', {
        d: 'M5 4 L5 18 L9 14 L11.5 19 L13.5 18 L11 13 L16 13 Z',
        fill: 'currentColor',
        stroke: 'currentColor',
        'stroke-width': '1',
        'stroke-linejoin': 'round',
      }),
    ]),
  slots: [],
  edges: [],
  circles: [],
  // No slots ever complete, so this is never called.
  sketch: () => null,
};
