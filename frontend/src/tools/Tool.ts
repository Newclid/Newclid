// Tool strategy interface. The dispatcher routes pointer events to the
// active tool via toolRegistry, so dispatch is a single lookup with no
// per-tool branching at the call site.

import type { WorldPoint, ScreenPoint } from '../geometry/coords';
import type { ToolName } from '../geometry/types-object';
import type { Scene } from '../scene/scene';

// Context handed to a tool on every event. Tools mutate the scene
// through this handle rather than reaching for a singleton.
export interface ToolContext {
  scene: Scene;
  // Pointer position in world coordinates.
  world: WorldPoint;
  // Pointer position in screen pixels — used for tolerance / hit-test
  // math that has to stay invariant under zoom.
  screen: ScreenPoint;
  // Current zoom level in pixels-per-world-unit.
  scale: number;
  shiftKey: boolean;
}

// A preview shape rendered by the canvas while a tool is mid-action.
// Discriminated on `kind` so the renderer can branch on it. Adding a
// future preview shape (rubberLine, rubberCircleAbs, ...) is one new
// variant + one new switch arm in the renderer's preview pass.
//
// Positions here are plain {x, y} rather than branded WorldPoint:
// previews carry derived geometry that's already been resolved from
// the scene, and tool call sites build them as object literals.
export type ToolPreview =
  | { kind: 'highlightPoint'; pos: { x: number; y: number } }
  | { kind: 'rubberCircle'; center: { x: number; y: number }; radiusVec: { x: number; y: number } };

export interface Tool {
  readonly name: ToolName;
  // Called when the user left-clicks (button 0) on the canvas.
  onClick(ctx: ToolContext): void;
  // Called continuously as the cursor moves; returns preview shapes for
  // the renderer. Empty array = no preview this frame.
  onMove(ctx: ToolContext): ToolPreview[];
  // Called when the tool is deactivated (e.g. on tool switch). Clears
  // any transient state the tool was holding.
  onDeactivate(ctx: { scene: Scene }): void;
}
