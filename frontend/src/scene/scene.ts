/**
In-memory store for scene objects, active tool, and transient tool state.
Notifies subscribers synchronously.
**/

import type { GeoObject, ObjectId, PointObject, ToolName } from '../geometry/types-object';
import type { ToolPreview } from '../tools/tool';
import { distance } from '../geometry/primitives';
import type { WorldPoint } from '../geometry/coords';

/**
Distributive Omit so each variant of the union keeps its own keys.
addObject takes everything except `id`, which the scene assigns.
**/
type DistOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never;

export type ToolState = { firstPoint?: ObjectId } | null;

// Frontend -> backend snapshot.
export interface SerializedScene {
  points: { id: ObjectId; label: string; x: number; y: number }[];
  circles?: { id: ObjectId; kind: 'center-radius'; center: ObjectId; radius: number }[];
  constructions?: {
    id: ObjectId;
    name: string;
    bindings: Record<string, ObjectId>;
   edges: [string, string][]; // actual point ID pairs, style dropped
   circles: { center: string; radius: number }[]; // resolved center ID + computed radius
  }[];
}

export class Scene {
  readonly objects = new Map<ObjectId, GeoObject>();
  // Start in the point tool so a fresh page is immediately useful.
  tool: ToolName = 'point';
  toolState: ToolState = null;
  /**
  Transient previews from the active tool's onMove. Not part of emit()
  so a pointermove burst doesn't re-run every subscriber.
  **/
  previews: ToolPreview[] = [];

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

  setPreviews(p: ToolPreview[]): void {
    this.previews = p;
  }

  addPoint(x: number, y: number): ObjectId {
    const id = `p${this.nextId++}`;
    const label = String.fromCharCode(this.nextLabelCode++);
    this.objects.set(id, { id, kind: 'point', x, y, label });
    this.emit();
    return id;
  }

  /**
  Generic add for any non-point GeoObject variant. Caller passes the
  shape minus `id`; the scene assigns the id and stores it.
  **/
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
    /**
    Cascade: any shape referencing this id loses its definition.
    Adding line/segment/triangle later is one more `else if` arm.
    **/
    for (const [k, v] of this.objects) {
      if (v.kind === 'circle') {
        if (v.mode === 'center-through') {
          if (v.center === id || v.through === id) this.objects.delete(k);
        } else {
          if (v.p1 === id || v.p2 === id || v.p3 === id) this.objects.delete(k);
        }
      }
    }

    // Cascade: if a ConstructionObject references a deleted point, delete the construction
    for (const [k, v] of this.objects) {
      if (v.kind === 'construction') {
        const allBoundIds = Object.values(v.bindings);
        if (allBoundIds.includes(id)) this.objects.delete(k);
      }
    }
    this.emit();
  }

  clear(): void {
    if (this.objects.size === 0 && this.toolState === null && this.previews.length === 0) return;
    this.objects.clear();
    this.toolState = null;
    this.previews = [];
    this.nextId = 1;
    this.nextLabelCode = 65;
    this.emit();
  }

  /**
  Backend-ready snapshot. Only emit a key when at least one of that kind
  exists; circle radius is derived from points so drags pick up fresh.
  **/
  serialize(): SerializedScene {
    const points: SerializedScene['points'] = [];
    const circles: NonNullable<SerializedScene['circles']> = [];
    for (const o of this.objects.values()) {
      if (o.kind === 'point') {
        points.push({ id: o.id, label: o.label, x: o.x, y: o.y });
      } else if (o.kind === 'circle') {
        if (o.mode === 'center-through') {
          const c = this.objects.get(o.center);
          const t = this.objects.get(o.through);
          if (c?.kind !== 'point' || t?.kind !== 'point') continue;
          const radius = distance(
            c as unknown as WorldPoint,
            t as unknown as WorldPoint,
          );
          circles.push({ id: o.id, kind: 'center-radius', center: o.center, radius });
        }
        /**
        'three-points' arm intentionally omitted — ships with the
        3-point circle prompt.
        **/
      }
    }

    const constructions: SerializedScene['constructions'] = [];
    for (const o of this.objects.values()) {
      if (o.kind === 'construction') {
        constructions.push({
          id: o.id,
          name: o.name,
          bindings: o.bindings,
          edges: o.edges,
          circles: o.circles,
        });
      }
    }
    const out: SerializedScene = { points };
    if (circles.length > 0) out.circles = circles;
    if (constructions.length > 0) out.constructions = constructions;
    return out;
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
