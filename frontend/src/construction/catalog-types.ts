import type { GeoObject, ObjectId } from '../geometry/types-object';
import type { Scene } from '../scene/scene';
import type { WorldPoint } from '../geometry/coords';

// Bindings: maps slot name → picked ObjectId or computed scalar value.
export type Bindings = Record<string, ObjectId | number>;

// Distributive Omit so a union (e.g. CircleObject) keeps its discriminated arms.
type DistOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never;

/**
What an entry's sketch emits: any GeoObject minus its id (the scene assigns
it), or null when the slots already created everything (e.g. a bare point).
**/
export type SketchResult = DistOmit<GeoObject, 'id'> | null;

// Aux geometry shown while a construction is in progress.
export type DerivePreview =
  | { kind: 'auxLine'; from: WorldPoint; to: WorldPoint }
  | { kind: 'circle'; center: { x: number; y: number }; through: { x: number; y: number } };

// One input step in a construction
export type SlotSpec =
  | { name: string; kind: 'pick' | 'place-free'; label: string }
  | {
      name: string;
      kind: 'derive';
      label: string;
      preview: (b: Bindings, scene: Scene) => DerivePreview[];
      project: (b: Bindings, scene: Scene, cursor: WorldPoint) => WorldPoint;
    }
  | { name: string; kind: 'scalar'; label: string; defaultValue?: number };

// An edge to draw between two points (slot names, resolved to ids in sketch).
export interface EdgeSpec {
  pointIds: [string, string];
  style?: 'solid' | 'dashed';
}

// A circle to draw (slot names for center and radius).
export interface CircleSpec {
  centerSlot: string;
  radiusSlot: string;
}

// Construction names are open strings; built-in tools use BuiltInToolName.
export type ConstructionName = string;

export interface CatalogEntry {
  name: ConstructionName;         // e.g. 'trapezoid'
  label: string;                  // toolbar text
  shortcut: string;               // single key, e.g. 'T'
  icon: () => SVGSVGElement;      // returns a fresh <svg> each call
  slots: SlotSpec[];
  edges: EdgeSpec[];
  circles: CircleSpec[];
  // Final emit: caller passes the shape minus `id`, scene.addObject assigns it.
  // Returns null when the slots already created the geometry (e.g. a free point)
  // or the entry produces nothing on completion (e.g. select).
  sketch: (b: Bindings, scene: Scene) => SketchResult;
  // Optional guard. Returns null = OK, string = error message to console.warn.
  validate?: (b: Bindings, scene: Scene) => string | null;
  // Optional live preview while the construction is in progress, given the
  // current cursor — e.g. the circle a final point would form.
  preview?: (b: Bindings, scene: Scene, cursor: WorldPoint) => DerivePreview[];
  /**
  Optional hook fired after each slot is bound, before the construction
  finishes. Lets an entry emit intermediate objects, e.g. build the reference
  line as soon as its two points are placed.
  **/
  onSlotFilled?: (slotName: string, b: Bindings, scene: Scene) => void;
}


/**
 * One JGEX clause
 */
export interface JgexEmit {
  def: string;
  signature: string[]; // the positional argument list (slot names, in the exact order)
  produces: string[]; // names which of those slots is defined as a new point
  scalars?: string[]; // names which slots are bound to numbers
}

/**
 * One JGEX block on a catalog entry. 
 */
export type JgexBlock =
  | JgexEmit
  | { combine: 'intersect'; clauses: JgexEmit[] }; // intersect joins multiple clauses with ',' to describe a point as an intersection

export interface CatalogEntry {
  // ...existing fields unchanged...
  jgex?: JgexBlock[];
}