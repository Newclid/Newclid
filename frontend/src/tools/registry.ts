import type { Tool, ToolContext, ToolPreview } from './Tool';
import type { ObjectId, ToolName } from '../geometry/types-object';
import { pickNearestPoint } from '../geometry/hitTest';

const SNAP_PX = 12;

function getOrCreatePoint(ctx: ToolContext): ObjectId {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  if (hit) return hit.id;
  return ctx.scene.addPoint(ctx.world.x, ctx.world.y);
}

function snapHighlight(ctx: ToolContext): ToolPreview[] {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  return hit ? [{ kind: 'highlightPoint', pos: { x: hit.x, y: hit.y } }] : [];
}

// Cursor mode: clicks on the canvas are inert (do nothing).
const selectTool: Tool = {
  name: 'select',
  onClick() {},
  onMove() {
    return [];
  },
  onDeactivate() {},
};

// Place a point at the click location, in world coordinates.
const pointTool: Tool = {
  name: 'point',
  onClick(ctx) {
    ctx.scene.addPoint(ctx.world.x, ctx.world.y);
  },
  onMove() {
    return [];
  },
  onDeactivate() {},
};

/**
Two-click center-through circle. Stores both point IDs, radius is
derived live, so dragging either point updates the rendered circle.
**/
const circleTool: Tool = {
  name: 'circle',
  onClick(ctx) {
    const pid = getOrCreatePoint(ctx);
    const ts = ctx.scene.toolState;
    if (!ts?.firstPoint) {
      ctx.scene.setToolState({ firstPoint: pid });
      return;
    }
    if (ts.firstPoint === pid) return;          // no zero-radius circle
    ctx.scene.addObject({
      kind: 'circle',
      mode: 'center-through',
      center: ts.firstPoint,
      through: pid,
    });
    ctx.scene.setToolState(null);
  },
  onMove(ctx) {
    const previews = snapHighlight(ctx);
    const ts = ctx.scene.toolState;
    if (!ts?.firstPoint) return previews;
    const first = ctx.scene.objects.get(ts.firstPoint);
    if (first?.kind !== 'point') return previews;
    previews.push({ kind: 'highlightPoint', pos: { x: first.x, y: first.y } });
    previews.push({
      kind: 'rubberCircle',
      center: { x: first.x, y: first.y },
      radiusVec: { x: ctx.world.x, y: ctx.world.y },
    });
    return previews;
  },
  onDeactivate(ctx) {
    ctx.scene.setToolState(null);
  },
};

export const toolRegistry: Record<ToolName, Tool> = {
  select: selectTool,
  point: pointTool,
  circle: circleTool,
};
