import type { Bindings } from './catalog-types';
import type { ObjectId } from '../geometry/types-object';
import type { Scene } from '../scene/scene';
import { line } from './entries/line';

// True when some construction already draws a full line through both points.
export function lineExists(scene: Scene, aId: ObjectId, bId: ObjectId): boolean {
  for (const o of scene.objects.values()) {
    if (o.kind !== 'construction') continue;
    for (const [p, q] of o.lines ?? []) {
      if ((p === aId && q === bId) || (p === bId && q === aId)) return true;
    }
  }
  return false;
}

/**
Draw the line through a and b as its own object, unless one already joins them.
Reuses the `line` entry so a line object has a single definition.
**/
export function ensureReferenceLine(scene: Scene, aId: ObjectId, bId: ObjectId): void {
  if (aId === bId || lineExists(scene, aId, bId)) return;
  const obj = line.sketch({ a: aId, b: bId }, scene);
  if (obj) scene.addObject(obj);
}

/**
Shared onSlotFilled for the perpendicular / parallel / foot entries: when the
second reference point (slot b) is placed, draw the line through a and b right
away so it is a committed object instead of a live preview.
**/
export function drawReferenceLineOnSlotB(slotName: string, b: Bindings, scene: Scene): void {
  if (slotName !== 'b') return;
  ensureReferenceLine(scene, b.a as ObjectId, b.b as ObjectId);
}
