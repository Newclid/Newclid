import type { WorldPoint, ScreenPoint } from '../geometry/coords';
import type { ToolName, ObjectId } from '../geometry/types-object';
import type { Scene } from '../scene/scene';

/**
A tool's restorable transient state: the slots bound so far and which step the
user is on. Captured before a click and replayed on undo so an in-progress
construction rewinds one slot in step with the scene.
**/
export interface ToolSnapshot {
  bindings: Record<string, ObjectId>;
  currentSlotIndex: number;
  createdInSlots: ObjectId[];
}

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
  | { kind: 'rubberCircle'; center: { x: number; y: number }; radiusVec: { x: number; y: number } }
  // Making sure for shapes like trapezoid will end up as trapezoids by controlling the last point for example
  // This shows where the last point can land to make it valid
  | { kind: 'auxLine'; from: { x: number; y: number }; to: { x: number; y: number } }
  // This is to let the viewer see the edges they already have created by the points they placed
  | { kind: 'partialEdge'; from: { x: number; y: number }; to: { x: number; y: number } }
  | { kind: 'selectHoverPoint'; pos: { x: number; y: number }; pointId: string };

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
  // Snapshot the tool's in-progress state so undo can rewind one slot.
  captureState?(): ToolSnapshot;
  // Restore a previously captured in-progress state.
  restoreState?(state: ToolSnapshot): void;
  // Label of the slot the user needs to fill next; null when idle.
  currentSlotLabel?(): string | null;
}
