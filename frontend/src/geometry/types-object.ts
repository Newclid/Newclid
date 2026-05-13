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
}

export type CircleObject =
  | { id: ObjectId; kind: 'circle'; mode: 'center-through'; center: ObjectId; through: ObjectId }
  | { id: ObjectId; kind: 'circle'; mode: 'three-points'; p1: ObjectId; p2: ObjectId; p3: ObjectId };

export type GeoObject = PointObject | CircleObject;
export type GeoKind = GeoObject['kind'];

export type ToolName = 'select' | 'point' | 'circle';
