import type { WorldPoint, ScreenPoint } from '../geometry/coords';
import type { ToolName } from '../geometry/types-object';
import type { Scene } from '../scene/scene';

/**
Context handed to a tool on every event. Tools mutate the scene
through this handle rather than reaching for a singleton.
**/
export interface ToolContext {
  scene: Scene;
  // Pointer position in world coordinates.
  world: WorldPoint;
  /**
  Pointer in screen pixel, used for tolerance/hit-test math that
  must stay invariant under zoom.
  **/
  screen: ScreenPoint;
  // Current zoom level in pixels-per-world-unit.
  scale: number;
  shiftKey: boolean;
}

/**
Preview shape rendered while a tool is mid-action. Positions are plain
{x, y} since they're already resolved from the scene.
**/
export type ToolPreview =
  | { kind: 'highlightPoint'; pos: { x: number; y: number } }
  | { kind: 'rubberCircle'; center: { x: number; y: number }; radiusVec: { x: number; y: number } };

export interface Tool {
  readonly name: ToolName;
  // Called when the user left-clicks (button 0) on the canvas.
  onClick(ctx: ToolContext): void;
  /**
  Called continuously as the cursor moves, returns preview shapes.
  Empty array = no preview this frame.
  **/
  onMove(ctx: ToolContext): ToolPreview[];
  /**
  Called when the tool is deactivated (e.g. on tool switch). Clears
  any transient state the tool was holding.
  **/
  onDeactivate(ctx: { scene: Scene }): void;
}
