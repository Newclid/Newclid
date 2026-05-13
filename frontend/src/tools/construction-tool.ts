import { Tool, ToolContext, ToolPreview } from './Tool';
import type { CatalogEntry } from '../construction/catalog-types';
import { getOrCreatePoint, snapHighlight } from './sharedHelpers';
import type { ObjectId } from '../geometry/types-object';
import type { ToolName } from '../geometry/types-object';
import type { Scene } from '../scene/scene';

export class ConstructionTool implements Tool {
  name: ToolName;
  private catalogEntry: CatalogEntry; // the blueprint (e.g. triangle)
  private bindings: Record<string, ObjectId> = {}; // slots filled so far
  private currentSlotIndex = 0; // which step the user is on
  // "where are we in the construction right now?"

  constructor(catalogEntry: CatalogEntry) {
    this.catalogEntry = catalogEntry;
    this.name = catalogEntry.name;
  }

  // Every click advances the construction by one slot
  onClick(ctx: ToolContext): void {
    const slot = this.catalogEntry.slots[this.currentSlotIndex];
    if (!slot) return;

    if (slot.kind === 'pick' || slot.kind === 'place-free') {
      const pointId = getOrCreatePoint(ctx);
      this.bindings[slot.name] = pointId;
      this.currentSlotIndex++;

      if (this.currentSlotIndex >= this.catalogEntry.slots.length) {
        // Done: call sketch fn and add to scene
        const obj = this.catalogEntry.sketch(this.bindings, ctx.scene);
        ctx.scene.addObject(obj);
        // Reset for next use
        this.reset();
      }
    }
  }

    // Fires constantly as the mouse moves. 
    // A visual indicator of where the next point would land.
    // This is where a live preview of the in-progress shape would eventually go.
  onMove(ctx: ToolContext): ToolPreview[] {
    const slot = this.catalogEntry.slots[this.currentSlotIndex];
    if (!slot) return [];

    // Show snap highlight at cursor
    return snapHighlight(ctx);
  }

    // Called when the user switches to a different tool. 
    // It resets everything so no half-finished state leaks into the next session.
  onDeactivate(ctx: { scene: Scene }): void {
    this.reset();
  }

    // Wipes bindings and rewinds the slot index back to 0,
    // ready for the next construction of the same type.
  private reset(): void {
    this.bindings = {};
    this.currentSlotIndex = 0;
  }
}