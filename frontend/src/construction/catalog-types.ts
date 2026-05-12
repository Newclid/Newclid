//import type { ConstructionObject } from '../geometry/types-object'; TODO: Person B adds this
import type { ObjectId, ToolName } from '../geometry/types-object';
import type { Scene } from '../scene/scene';

// Rule slot kinds
type SlotKind = 'pick' | 'place-free' | 'derive' | 'scalar';

// One input step in a construction
interface SlotSpec {
  name: string;              // e.g. 'center', 'rimPoint'
  kind: SlotKind;
  label: string;             // UI text
}

// An edge to draw between two points
interface EdgeSpec {
  pointIds: [string, string]; // [slot1, slot2]
  style?: 'solid' | 'dashed'; 
}

// A circle to draw
interface CircleSpec {
  centerSlot: string;
  radiusSlot: string;
}

// Bindings: maps slot name → picked ObjectId or computed value
type Bindings = Record<string, ObjectId | number>;

// One construction definition
export interface CatalogEntry {
  name: ToolName;                  // e.g. 'triangle'
  slots: SlotSpec[];
  edges: EdgeSpec[];
  circles: CircleSpec[];
  sketch: (bindings: Bindings, scene: Scene) => any; // TODO: ConstructionObject
}

// All catalog entries keyed by name
export const CONSTRUCTION_CATALOG: Record<string, CatalogEntry> = {};