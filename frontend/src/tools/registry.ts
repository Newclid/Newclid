// Concrete tools, keyed by name. The dispatcher resolves
// `toolRegistry[scene.tool]` and calls into it directly.

import type { Tool } from './Tool';
import type { ToolName } from '../geometry/types-object';

// Cursor mode: clicks on the canvas are inert.
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

export const toolRegistry: Record<ToolName, Tool> = {
  select: selectTool,
  point: pointTool,
};
