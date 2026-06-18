import { Scene } from '../../src/scene/scene';
import type { ObjectId } from '../../src/geometry/types-object';

// Adds one named point per [x, y] entry and returns their assigned ids,
// so entry tests can write `const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] })`.
export function addPoints<const T extends Record<string, [number, number]>>(
  scene: Scene,
  coords: T,
): Record<keyof T, ObjectId> {
  const ids = {} as Record<keyof T, ObjectId>;
  for (const name of Object.keys(coords) as (keyof T)[]) {
    const [x, y] = coords[name];
    ids[name] = scene.addPoint(x, y);
  }
  return ids;
}

// Adds a center-through circle to the scene and returns the center and through point ids.
export function addCircle(
  scene: Scene,
  center: [number, number],
  through: [number, number],
): { center: ObjectId; through: ObjectId } {
  const centerId = scene.addPoint(center[0], center[1]);
  const throughId = scene.addPoint(through[0], through[1]);
  scene.addObject({ kind: 'circle', mode: 'center-through', center: centerId, through: throughId });
  return { center: centerId, through: throughId };
}
