import type { Tool } from './tool';
import type { ToolName } from '../geometry/types-object';
import { getOrCreatePoint, snapHighlight } from './sharedHelpers';
import { ConstructionTool } from './construction-tool';
import { CONSTRUCTION_CATALOG } from '../construction/catalog';

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

const builtIns: Record<ToolName, Tool> = {
  select: selectTool,
  point: pointTool,
  circle: circleTool,
};

// Cache so the same ConstructionTool instance is reused across tool switches;
// onDeactivate already resets transient state.
const constructionToolCache = new Map<string, Tool>();

/**
Look up a tool by name. Falls back from built-ins to the catalog of
construction entries. Returns undefined for unknown names.
**/
export function getTool(name: string): Tool | undefined {
  if (name in builtIns) return builtIns[name as ToolName];
  let t = constructionToolCache.get(name);
  if (!t) {
    const entry = CONSTRUCTION_CATALOG[name];
    if (!entry) return undefined;
    t = new ConstructionTool(entry);
    constructionToolCache.set(name, t);
  }
  return t;
}
