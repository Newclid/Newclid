import type { CatalogEntry } from '../catalog-types';
import type { ObjectId, PointObject } from '../../geometry/types-object';
import { iconWrap, svgEl } from '../../ui/icon-helpers';

/**
Center-through circle. Slot a is the centre, slot b a point on the circle; the
radius is derived from the two points, so dragging either updates the rendered
circle. Emits a CircleObject rather than a construction.
**/
export const circle: CatalogEntry = {
  name: 'circle',
  label: 'Circle',
  shortcut: 'C',
  icon: () =>
    iconWrap([
      svgEl('circle', {
        cx: '11', cy: '11', r: '8',
        fill: 'none', stroke: 'currentColor', 'stroke-width': '1.6',
      }),
    ]),
  slots: [
    { name: 'a', kind: 'pick', label: 'Pick the centre of the circle' },
    { name: 'b', kind: 'pick', label: 'Pick a point on the circle to set the radius' },
  ],
  edges: [],
  circles: [],
  // While placing the second point, preview the circle the cursor would form.
  preview: (binds, scene, cursor) => {
    const a = scene.objects.get(binds.a as ObjectId) as PointObject | undefined;
    if (!a) return [];
    return [{ kind: 'circle', center: { x: a.x, y: a.y }, through: { x: cursor.x, y: cursor.y } }];
  },
  sketch: (binds) => ({
    kind: 'circle',
    mode: 'center-through',
    center: binds.a as ObjectId,
    through: binds.b as ObjectId,
  }),
  validate: (binds) =>
    binds.a !== undefined && binds.b !== undefined && binds.a === binds.b
      ? 'The centre and the point on the circle must be distinct'
      : null,
};
