import { ToolContext, ToolPreview } from './Tool';
import { pickNearestPoint } from '../geometry/hitTest';
import type { ObjectId } from '../geometry/types-object';

const SNAP_PX = 12;

export function getOrCreatePoint(ctx: ToolContext): ObjectId {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  if (hit) return hit.id;
  return ctx.scene.addPoint(ctx.world.x, ctx.world.y);
}

export function snapHighlight(ctx: ToolContext): ToolPreview[] {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  return hit ? [{ kind: 'highlightPoint', pos: { x: hit.x, y: hit.y } }] : [];
}