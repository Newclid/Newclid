import { Tool, ToolContext, ToolPreview } from './Tool';
import type { CatalogEntry } from '../construction/catalog-types';
import { getOrCreatePoint, snapHighlight } from './sharedHelpers';
import type { ObjectId } from '../geometry/types-object';
import type { ToolName } from '../geometry/types-object';
import type { Scene } from '../scene/scene';

export class ConstructionTool implements Tool {
  name: ToolName;
  private catalogEntry: CatalogEntry;
  private bindings: Record<string, ObjectId> = {};
  private currentSlotIndex = 0;

  constructor(catalogEntry: CatalogEntry) {
    this.catalogEntry = catalogEntry;
    this.name = catalogEntry.name;
  }

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

  onMove(ctx: ToolContext): ToolPreview[] {
    const slot = this.catalogEntry.slots[this.currentSlotIndex];
    if (!slot) return [];

    // Show snap highlight at cursor
    return snapHighlight(ctx);
  }

  onDeactivate(ctx: { scene: Scene }): void {
    this.reset();
  }

  private reset(): void {
    this.bindings = {};
    this.currentSlotIndex = 0;
  }
}