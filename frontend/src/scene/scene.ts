import type { PointObject, ObjectId } from '../geometry/types-object';

export class Scene {
  readonly points = new Map<ObjectId, PointObject>();
  private nextId = 1;
  private nextLabelCode = 65; // 'A'

  addPoint(x: number, y: number): ObjectId {
    const id = 'p${this.nextId++}';
    const label = String.fromCharCode(this.nextLabelCode++);
    this.points.set(id, { id, kind: 'point', x, y, label });
    return id;
  }
}