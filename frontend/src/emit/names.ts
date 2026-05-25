import type { Scene } from '../scene/scene';
import type { ObjectId } from '../geometry/types-object';

/**
 * Assign each point a JGEX-style identifier in build order: a, b, ..., z,
 * a1, b1, ..., z1, a2, ...
 *
 * Build order matters because JGEX is sequential — each clause may
 * reference earlier names but not later ones. Maps preserve insertion
 * order
 *
 */
export function buildNameTable(scene: Scene): Map<ObjectId, string> {
  const names = new Map<ObjectId, string>();
  let n = 0;
  for (const o of scene.objects.values()) {
    if (o.kind !== 'point') continue;
    const letter = String.fromCharCode(97 + (n % 26));  // 'a'
    const suffix = Math.floor(n / 26);
    names.set(o.id, suffix === 0 ? letter : `${letter}${suffix}`);
    n++;
  }
  return names;
}