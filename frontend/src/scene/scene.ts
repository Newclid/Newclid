// In-memory store for the scene plus the active tool.
//
// Holds geometric objects keyed by ID, the currently selected tool, and
// transient tool-specific state (e.g. the first clicked point of a
// half-built line). Notifies subscribers synchronously whenever any of
// those change, so any reader sees the latest state immediately;
// downstream renderers are expected to rAF-coalesce their redraws.

import type { GeoObject, ObjectId, PointObject, ToolName } from '../geometry/types-object';

// Distributive Omit so each variant of the union keeps its own keys.
// addObject takes everything except `id`, which the scene assigns.
type DistOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never;

export type ToolState = { firstPoint?: ObjectId } | null;

export class Scene {
  readonly objects = new Map<ObjectId, GeoObject>();
  // The canvas starts in the point tool so a fresh page lets the user
  // click to place a point without first selecting a tool.
  tool: ToolName = 'point';
  toolState: ToolState = null;

  private nextId = 1;
  private nextLabelCode = 65; // 'A'
  private listeners = new Set<() => void>();

  // ---------- read-only convenience ----------

  // Iterate only PointObjects from the heterogeneous `objects` map.
  *points(): IterableIterator<PointObject> {
    for (const o of this.objects.values()) {
      if (o.kind === 'point') yield o;
    }
  }

  // ---------- mutators ----------

  setTool(name: ToolName): void {
    if (this.tool === name) return;
    this.tool = name;
    this.toolState = null;
    this.emit();
  }

  setToolState(s: ToolState): void {
    this.toolState = s;
    this.emit();
  }

  addPoint(x: number, y: number): ObjectId {
    const id = `p${this.nextId++}`;
    const label = String.fromCharCode(this.nextLabelCode++);
    this.objects.set(id, { id, kind: 'point', x, y, label });
    this.emit();
    return id;
  }

  // Generic add for any non-point GeoObject variant. Caller passes the
  // shape minus `id`; the scene assigns the id and stores it.
  addObject(obj: DistOmit<GeoObject, 'id'>): ObjectId {
    const id = `o${this.nextId++}`;
    this.objects.set(id, { ...obj, id } as GeoObject);
    this.emit();
    return id;
  }

  movePoint(id: ObjectId, x: number, y: number): void {
    const o = this.objects.get(id);
    if (!o || o.kind !== 'point') return;
    this.objects.set(id, { ...o, x, y });
    this.emit();
  }

  removeObject(id: ObjectId): void {
    if (!this.objects.has(id)) return;
    this.objects.delete(id);
    this.emit();
  }

  clear(): void {
    if (this.objects.size === 0 && this.toolState === null) return;
    this.objects.clear();
    this.toolState = null;
    this.nextId = 1;
    this.nextLabelCode = 65;
    this.emit();
  }

  // ---------- pub/sub ----------

  subscribe(fn: () => void): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  private emit(): void {
    for (const fn of this.listeners) fn();
  }
}
