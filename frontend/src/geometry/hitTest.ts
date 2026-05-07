// Snap hit-testing. Pure math — no DOM, no events, no SVG. Lives in
// geometry/ alongside primitives and viewport because it's shared
// between tools (snapping during a build) and any future Select tool's
// drag-grab.
//
// tolerancePx is converted to world units via tolerancePx / scale so
// the snap radius stays a constant ~12 screen pixels regardless of
// zoom. As shapes other than points start to ship (line, segment,
// triangle, 3-point circle), pickObject (for non-point shapes) lands
// next to pickNearestPoint here.

import type { GeoObject, ObjectId, PointObject } from './types-object';
import type { WorldPoint } from './coords';
import { distance } from './primitives';

export interface PickOptions {
  // Tolerance expressed in screen pixels.
  tolerancePx: number;
  // Current zoom (px per world unit).
  scale: number;
  // Optional kind filter — currently only 'point' is queried, but the
  // shape lands now so future hit-tests don't change the signature.
  kinds?: GeoObject['kind'][];
}

// Find the existing point nearest to worldPos within the snap tolerance,
// or null. Iterates the heterogeneous map and ignores non-point objects.
export function pickNearestPoint(
  objects: Map<ObjectId, GeoObject>,
  worldPos: WorldPoint,
  opts: PickOptions,
): PointObject | null {
  if (opts.kinds && !opts.kinds.includes('point')) return null;
  const tol = opts.tolerancePx / opts.scale;
  let best: { obj: PointObject; d: number } | null = null;
  for (const o of objects.values()) {
    if (o.kind !== 'point') continue;
    const d = distance(worldPos, o as unknown as WorldPoint);
    if (d < tol && (!best || d < best.d)) best = { obj: o, d };
  }
  return best?.obj ?? null;
}
