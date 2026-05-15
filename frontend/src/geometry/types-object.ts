/** 
All coordinates are in WORLD space (math-style, Y up).
Conversion to screen pixels happens only in the renderer.
**/

export type ObjectId = string;

export interface PointObject {
  id: ObjectId;
  kind: 'point';
  x: number;
  y: number;
  // Display label, e.g. 'A'. Auto-assigned A, B, C, … on creation.
  label: string;
  // Optional per-point render color. Defaults to the renderer's ink color.
  color?: string;
}

export interface ConstructionObject {
  id: ObjectId;
  kind: 'construction';
  name: string;  // which construction (e.g. 'triangle')
  bindings: Record<string, ObjectId>;  // slot → point/derived id
  edges: Array<[ObjectId, ObjectId]>;  // pairs of points to draw lines between
  circles: Array<{ center: ObjectId; radius: number }>;  // circles to draw
}

// Mode-tagged: 'center-through' is the variant in scope here. The
// 'three-points' arm is declared up front so renderer / cascade /
// serialize branches written today are already shaped for it; the
// 3-point tool itself ships in a follow-up prompt.
export type CircleObject =
  | { id: ObjectId; kind: 'circle'; mode: 'center-through'; center: ObjectId; through: ObjectId }
  | { id: ObjectId; kind: 'circle'; mode: 'three-points'; p1: ObjectId; p2: ObjectId; p3: ObjectId };

export type GeoObject = PointObject | CircleObject | ConstructionObject;
export type GeoKind = GeoObject['kind'];

export type ToolName = string;
