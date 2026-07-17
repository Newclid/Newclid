/** 
Snap hit-testing. tolerancePx is converted to world units via tolerancePx / scale 
so the snap radius stays a constant ~12 screen pixels regardless of
zoom.
**/

import type { GeoObject, ObjectId, PointObject } from './types-object';
import type { WorldPoint } from './coords';
import { distance } from './primitives';

export interface PickOptions {
  // Tolerance expressed in screen pixels.
  tolerancePx: number;
  // Current zoom (px per world unit).
  scale: number;
  // Optional kind filter
  kinds?: GeoObject['kind'][];
}

/** 
Find the existing point nearest to worldPos within the snap tolerance,
or null. Ignores non-point objects.
**/
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
