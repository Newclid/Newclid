import type { WorldPoint } from './coords';

export function distance(a: WorldPoint, b: WorldPoint): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

export function distanceToCircle(p: WorldPoint, center: WorldPoint, radius: number): number {
  return Math.abs(distance(p, center) - radius);
}
