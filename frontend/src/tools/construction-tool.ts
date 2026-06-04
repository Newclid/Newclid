import { Tool, ToolContext, ToolPreview } from './tool';
import type { CatalogEntry } from '../construction/catalog-types';
import { getOrCreatePoint, snapHighlight } from './sharedHelpers';
import type { ObjectId, ToolName } from '../geometry/types-object';
import type { Scene } from '../scene/scene';

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
      console.warn(`[${this.catalogEntry.name}] ${err}`);
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
      // Done: sketch may emit a final object, or null when the slots already
      // created everything (e.g. a bare point).
      const obj = this.catalogEntry.sketch(this.bindings, ctx.scene);
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
    } else if (slot.kind === 'pick') {
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

  private reset(): void {
    this.bindings = {};
    this.currentSlotIndex = 0;
  }
}
