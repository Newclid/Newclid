// Discriminated union of every shape the scene can hold. All
// coordinates are in WORLD space (math-style, Y up); conversion to
// screen pixels happens only in the renderer.

export type ObjectId = string;

export interface PointObject {
  id: ObjectId;
  kind: 'point';
  x: number;
  y: number;
  // Display label, e.g. 'A'. Auto-assigned A, B, C, … on creation.
  label: string;
}

// Mode-tagged: 'center-through' is the variant in scope here. The
// 'three-points' arm is declared up front so renderer / cascade /
// serialize branches written today are already shaped for it; the
// 3-point tool itself ships in a follow-up prompt.
export type CircleObject =
  | { id: ObjectId; kind: 'circle'; mode: 'center-through'; center: ObjectId; through: ObjectId }
  | { id: ObjectId; kind: 'circle'; mode: 'three-points'; p1: ObjectId; p2: ObjectId; p3: ObjectId };

export type GeoObject = PointObject | CircleObject;
export type GeoKind = GeoObject['kind'];

export type ToolName = 'select' | 'point' | 'circle';
