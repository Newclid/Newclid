import { ToolContext, ToolPreview } from './Tool';
import { pickNearestPoint } from '../geometry/hitTest';
import type { ObjectId } from '../geometry/types-object';

const SNAP_PX = 12; // If the cursor is within 12 pixels of the point it snaps to it instead of creating a new one

// Called on every onClick - mutates the scene
export function getOrCreatePoint(ctx: ToolContext): ObjectId {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  if (hit) return hit.id; // snap to existing point
  return ctx.scene.addPoint(ctx.world.x, ctx.world.y); // create a new one
}

// Runs the exact same detection - returns a preview instruction
export function snapHighlight(ctx: ToolContext): ToolPreview[] {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  return hit ? [{ kind: 'highlightPoint', pos: { x: hit.x, y: hit.y } }] : [];
}
// Called on every onMove (read only), so the highlight follows the cursor in real time, giving the user feedback before click

// Hit - tells the renderer to draw a highlight ring around the point
// No hit - returns empty array, nothing drawn