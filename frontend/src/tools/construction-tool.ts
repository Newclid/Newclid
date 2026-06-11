import { Tool, ToolContext, ToolPreview, ToolSnapshot } from './tool';
import type { CatalogEntry, SketchResult } from '../construction/catalog-types';
import { getOrCreatePoint, pickExistingPoint, snapHighlight } from './sharedHelpers';
import type { ObjectId, PointObject, ToolName } from '../geometry/types-object';
import type { Scene } from '../scene/scene';

type Coord = { x: number; y: number };

function coordinateMultisetsMatch(a: Coord[], b: Coord[]): boolean {
  if (a.length !== b.length) return false;
  const used = new Array(b.length).fill(false);
  for (const pa of a) {
    const i = b.findIndex((pb, j) => !used[j] && Math.abs(pa.x - pb.x) < 1e-9 && Math.abs(pa.y - pb.y) < 1e-9);
    if (i === -1) return false;
    used[i] = true;
  }
  return true;
}

function bindingCoords(bindings: Record<string, ObjectId | number>, scene: Scene): Coord[] {
  return Object.values(bindings)
    .map(id => scene.objects.get(id as ObjectId))
    .filter((o): o is PointObject => o?.kind === 'point')
    .map(p => ({ x: p.x, y: p.y }));
}

// Returns true if point pt lies on the infinite line through p and q (within 1e-9).
function onLine(p: Coord, q: Coord, pt: Coord): boolean {
  const cross = (pt.x - p.x) * (q.y - p.y) - (pt.y - p.y) * (q.x - p.x);
  return Math.abs(cross) < 1e-9;
}

// Returns true if every line in newLines matches a geometrically equal line in existingLines.
function linesAllMatch(
  newLines: [ObjectId, ObjectId][],
  existingLines: [ObjectId, ObjectId][],
  scene: Scene,
): boolean {
  for (const [p1id, q1id] of newLines) {
    const p1 = scene.objects.get(p1id);
    const q1 = scene.objects.get(q1id);
    if (!p1 || !q1 || p1.kind !== 'point' || q1.kind !== 'point') return false;
    const found = existingLines.some(([p2id, q2id]) => {
      const p2 = scene.objects.get(p2id);
      const q2 = scene.objects.get(q2id);
      if (!p2 || !q2 || p2.kind !== 'point' || q2.kind !== 'point') return false;
      return onLine(p1, q1, p2) && onLine(p1, q1, q2);
    });
    if (!found) return false;
  }
  return true;
}

function isDuplicateConstruction(obj: SketchResult, scene: Scene): boolean {
  if (!obj) return false;

  if (obj.kind === 'circle' && obj.mode === 'center-through') {
    const center = scene.objects.get(obj.center);
    const through = scene.objects.get(obj.through);
    if (!center || !through || center.kind !== 'point' || through.kind !== 'point') return false;
    const r = Math.hypot(through.x - center.x, through.y - center.y);
    for (const o of scene.objects.values()) {
      if (o.kind !== 'circle' || o.mode !== 'center-through') continue;
      const oc = scene.objects.get(o.center);
      const ot = scene.objects.get(o.through);
      if (!oc || !ot || oc.kind !== 'point' || ot.kind !== 'point') continue;
      if (
        Math.abs(oc.x - center.x) < 1e-9 &&
        Math.abs(oc.y - center.y) < 1e-9 &&
        Math.abs(Math.hypot(ot.x - oc.x, ot.y - oc.y) - r) < 1e-9
      ) return true;
    }
    return false;
  }

  if (obj.kind === 'construction') {
    const newCoords = bindingCoords(obj.bindings, scene);
    for (const o of scene.objects.values()) {
      if (o.kind !== 'construction' || o.name !== obj.name) continue;
      if (coordinateMultisetsMatch(newCoords, bindingCoords(o.bindings, scene))) return true;
      // Secondary check for line-emitting constructions: catch reversed reference direction.
      if (obj.lines?.length && o.lines?.length) {
        if (linesAllMatch(obj.lines as [ObjectId, ObjectId][], o.lines as [ObjectId, ObjectId][], scene)) return true;
      }
    }
  }

  return false;
}

export class ConstructionTool implements Tool {
  name: ToolName;
  private catalogEntry: CatalogEntry; // the blueprint (e.g. trapezoid)
  private bindings: Record<string, ObjectId> = {}; // slots filled so far
  private currentSlotIndex = 0; // which step the user is on

  constructor(catalogEntry: CatalogEntry) {
    this.catalogEntry = catalogEntry;
    this.name = catalogEntry.name;
  }

  // Every click advances the construction by one slot.
  onClick(ctx: ToolContext): void {
    const slot = this.catalogEntry.slots[this.currentSlotIndex];
    if (!slot) return;

    let pointId: ObjectId;
    if (slot.kind === 'pick') {
      pointId = getOrCreatePoint(ctx);
    } else if (slot.kind === 'pick-existing') {
      // Only reference points already in the scene; ignore clicks on empty space
      // so this slot can never spawn a stray, unconnected point.
      const existing = pickExistingPoint(ctx);
      if (!existing) return;
      pointId = existing;
    } else if (slot.kind === 'place-free') {
      // Always drop a fresh point at the cursor, never snapping to an existing
      // one — this is the plain point-placement step.
      pointId = ctx.scene.addPoint(ctx.world.x, ctx.world.y);
    } else if (slot.kind === 'derive') {
      // Project the cursor onto the constrained locus, then materialise a
      // fresh point at the projected position.
      const projected = slot.project(this.bindings, ctx.scene, ctx.world);
      pointId = ctx.scene.addPoint(projected.x, projected.y);
    } else {
      console.warn(`ConstructionTool: slot kind '${(slot as { kind: string }).kind}' not implemented`);
      return;
    }

    // Validate the tentative binding before committing it.
    const tentative = { ...this.bindings, [slot.name]: pointId };
    const err = this.catalogEntry.validate?.(tentative, ctx.scene);
    if (err) {
      ctx.scene.setSlotError(err);
      // Roll back the auto-created point so a rejected derive doesn't leak.
      if (slot.kind === 'derive') ctx.scene.removeObject(pointId);
      return;
    }

    this.bindings = tentative;
    this.currentSlotIndex++;

    /**
    Let the entry emit intermediate geometry now that this slot is bound,
    e.g. build the reference line once both of its points exist.
    **/
    this.catalogEntry.onSlotFilled?.(slot.name, this.bindings, ctx.scene);

    if (this.currentSlotIndex >= this.catalogEntry.slots.length) {
      // Snapshot before sketch so we can identify — and remove — any points it creates.
      const beforeSketch = new Set(ctx.scene.objects.keys());
      const obj = this.catalogEntry.sketch(this.bindings, ctx.scene);
      const sketchCreated = [...ctx.scene.objects.keys()].filter(id => !beforeSketch.has(id));

      if (isDuplicateConstruction(obj, ctx.scene)) {
        ctx.scene.setSlotError('This construction already exists');
        for (const id of sketchCreated) ctx.scene.removeObject(id as ObjectId);
        for (const s of this.catalogEntry.slots) {
          if (s.kind === 'derive') ctx.scene.removeObject(this.bindings[s.name] as ObjectId);
        }
        this.reset();
        return;
      }
      if (obj) ctx.scene.addObject(obj);
      this.reset();
    }
  }

  // Live preview: already-bound edges, plus per-slot aux geometry.
  onMove(ctx: ToolContext): ToolPreview[] {
    const previews: ToolPreview[] = [];
    const slot = this.catalogEntry.slots[this.currentSlotIndex];
    if (!slot) return previews;

    // Layer 1: any edges whose endpoints are already bound — partial shape.
    for (const e of this.catalogEntry.edges) {
      const aId = this.bindings[e.pointIds[0]];
      const bId = this.bindings[e.pointIds[1]];
      if (!aId || !bId) continue;
      const a = ctx.scene.objects.get(aId);
      const b = ctx.scene.objects.get(bId);
      if (a?.kind !== 'point' || b?.kind !== 'point') continue;
      previews.push({
        kind: 'partialEdge',
        from: { x: a.x, y: a.y },
        to: { x: b.x, y: b.y },
      });
    }

    // Layer 2: per-slot aux geometry + cursor preview.
    if (slot.kind === 'derive') {
      for (const aux of slot.preview(this.bindings, ctx.scene)) {
        if (aux.kind === 'auxLine') {
          previews.push({ kind: 'auxLine', from: aux.from, to: aux.to });
        } else if (aux.kind === 'circle') {
          previews.push({ kind: 'rubberCircle', center: aux.center, radiusVec: aux.through });
        } else if (aux.kind === 'point') {
          previews.push({ kind: 'highlightPoint', pos: { x: aux.at.x, y: aux.at.y } });
        }
      }
      const projected = slot.project(this.bindings, ctx.scene, ctx.world);
      previews.push({ kind: 'highlightPoint', pos: { x: projected.x, y: projected.y } });
    } else if (slot.kind === 'pick' || slot.kind === 'pick-existing') {
      previews.push(...snapHighlight(ctx));
    }
    // place-free always drops a new point (no snapping), scalar has no cursor
    // geometry — both fall through with nothing to preview.

    // Layer 3: entry-level live preview (e.g. the circle a final point forms).
    for (const p of this.catalogEntry.preview?.(this.bindings, ctx.scene, ctx.world) ?? []) {
      if (p.kind === 'auxLine') {
        previews.push({ kind: 'auxLine', from: p.from, to: p.to });
      } else if (p.kind === 'circle') {
        previews.push({ kind: 'rubberCircle', center: p.center, radiusVec: p.through });
      } else if (p.kind === 'point') {
        previews.push({ kind: 'highlightPoint', pos: { x: p.at.x, y: p.at.y } });
      }
    }

    return previews;
  }

  onDeactivate(_ctx: { scene: Scene }): void {
    this.reset();
  }

  // Label of the slot the user needs to fill next, or null when no
  // construction is in progress (tool is idle after reset).
  currentSlotLabel(): string | null {
    return this.catalogEntry.slots[this.currentSlotIndex]?.label ?? null;
  }

  // Snapshot the in-progress slots so undo can rewind exactly one step.
  captureState(): ToolSnapshot {
    return { bindings: { ...this.bindings }, currentSlotIndex: this.currentSlotIndex };
  }

  // Replay a captured state, e.g. after an undo rewinds the scene one click.
  restoreState(state: ToolSnapshot): void {
    this.bindings = { ...state.bindings };
    this.currentSlotIndex = state.currentSlotIndex;
  }

  private reset(): void {
    this.bindings = {};
    this.currentSlotIndex = 0;
  }
}
