// Pure geometry math. No DOM, no scene, no render imports. Inputs are
// WorldPoint-shaped (the branded {x, y, _kind: 'world'} from coords.ts);
// these primitives only read .x / .y so any structural subtype works,
// but call sites should pass branded WorldPoints so the brand is
// preserved end-to-end.
//
// distance and distanceToCircle are the building blocks for every
// future builder tool (line, segment, triangle, 3-point circle); written
// generically so those tools drop in without refactoring this file.

import type { WorldPoint } from './coords';

export function distance(a: WorldPoint, b: WorldPoint): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

// Absolute distance from p to the rim of the circle defined by
// (center, radius). Used by hit-testing once 3-point circles ship; for
// center-through circles the renderer derives radius via `distance`.
export function distanceToCircle(p: WorldPoint, center: WorldPoint, radius: number): number {
  return Math.abs(distance(p, center) - radius);
}
