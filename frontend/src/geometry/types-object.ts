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

export type GeoObject = PointObject;
export type GeoKind = GeoObject['kind'];

export type ToolName = 'select' | 'point';
