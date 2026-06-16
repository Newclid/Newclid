/**
In-memory store for scene objects, active tool, and transient tool state.
Notifies subscribers synchronously.
**/

import type { ConstructionObject, GeoObject, ObjectId, PointObject, ToolName } from '../geometry/types-object';
import { CONSTRUCTION_CATALOG } from '../construction/catalog';
import type { ToolPreview } from '../tools/tool'
import { distance } from '../geometry/primitives';
import type { WorldPoint } from '../geometry/coords';

/**
Distributive Omit so each variant of the union keeps its own keys.
addObject takes everything except `id`, which the scene assigns.
**/
type DistOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never;

export type ToolState = { firstPoint?: ObjectId } | null;

export interface SceneSnapshot {
  objects: Map<ObjectId, GeoObject>;
  nextId: number;
  nextLabelCode: number;
  undoStack?: UndoEntry[];
}

/**
One step of undo history: the scene state before an action, plus an optional
callback to rewind the active tool's in-progress slots in step with the scene.
**/
export interface UndoEntry {
  snapshot: SceneSnapshot;
  restoreTool?: () => void;
}

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
  tool: ToolName = 'select';
  toolState: ToolState = null;
  /**
  Transient previews from the active tool's onMove. Not part of emit()
  so a pointermove burst doesn't re-run every subscriber.
  **/
  previews: ToolPreview[] = [];
  // Current construction slot instruction shown in the canvas hint UI.
  slotHint: string | null = null;
  // Validation error from the last rejected click — shown in a separate box above the hint.
  slotError: string | null = null;

  private nextId = 1;
  private nextLabelCode = 65; // 'A'
  private listeners = new Set<() => void>();
  /**
  Undo history. Each entry pairs the scene snapshot taken just before a user
  action with an optional callback that rewinds the active tool's in-progress
  state, so undoing mid-construction steps back one slot rather than cancelling.
  Capped so long sessions don't grow without bound; oldest states drop first.
  **/
  private undoStack: UndoEntry[] = [];
  // Bumped by every real mutation so callers can tell whether a click changed
  // the scene (a click may advance a tool slot without touching the scene).
  private _revision = 0;
  private static readonly MAX_UNDO = 100;

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

  setSlotHint(s: string | null): void {
    this.slotHint = s;
    this.emit();
  }

  setSlotError(s: string | null): void {
    this.slotError = s;
    this.emit();
  }

  setPreviews(p: ToolPreview[]): void {
    this.previews = p;
  }

  addPoint(x: number, y: number): ObjectId {
    const id = `p${this.nextId++}`;
    const label = this.allocateLabel();
    this.objects.set(id, { id, kind: 'point', x, y, label });
    this._revision++;
    this.emit();
    return id;
  }

  // Cycle through A–Z then a–z (52 letters), skipping labels already in use so
  // wrap-around after many placements/deletions still produces valid single letters.
  // nextLabelCode stays a char code so SceneSnapshot round-trips unchanged.
  private allocateLabel(): string {
    const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    const usedLabels = new Set<string>();
    for (const o of this.objects.values()) {
      if (o.kind === 'point') usedLabels.add((o as PointObject).label);
    }
    // Map the stored char code to a position in LETTERS (handles legacy values safely).
    let pos = LETTERS.indexOf(String.fromCharCode(this.nextLabelCode));
    if (pos === -1) pos = 0;
    for (let i = 0; i < LETTERS.length; i++) {
      const idx = (pos + i) % LETTERS.length;
      const label = LETTERS[idx];
      if (!usedLabels.has(label)) {
        this.nextLabelCode = LETTERS.charCodeAt((idx + 1) % LETTERS.length);
        return label;
      }
    }
    // All 52 letters in use — still advance so repeated calls cycle through A, B, C…
    // rather than returning the same letter every time.
    this.nextLabelCode = LETTERS.charCodeAt((pos + 1) % LETTERS.length);
    return LETTERS[pos];
  }

  /**
  Generic add for any non-point GeoObject variant. Caller passes the
  shape minus `id`; the scene assigns the id and stores it.
  **/
  addObject(obj: DistOmit<GeoObject, 'id'>): ObjectId {
    const id = `o${this.nextId++}`;
    this.objects.set(id, { ...obj, id } as GeoObject);
    this._revision++;
    this.emit();
    return id;
  }

  movePoint(id: ObjectId, x: number, y: number): void {
    const o = this.objects.get(id);
    if (!o || o.kind !== 'point') return;
    this.objects.set(id, { ...o, x, y });
    this._revision++;
    this.emit();
  }

  setPointColor(id: ObjectId, color: string | undefined): void {
    const o = this.objects.get(id);
    if (!o || o.kind !== 'point') return;
    this.objects.set(id, { ...o, color });
    this._revision++;
    this.emit();
  }

  private referencedPointIds(obj: GeoObject): ObjectId[] {
    if (obj.kind === 'circle') {
      if (obj.mode === 'center-through') return [obj.center, obj.through];
      return [obj.p1, obj.p2, obj.p3];
    }
    if (obj.kind === 'construction') return Object.values(obj.bindings) as ObjectId[];
    return [];
  }

  private outputSlotNames(name: string): Set<string> {
    const entry = CONSTRUCTION_CATALOG[name];
    const result = new Set<string>();
    for (const block of entry?.jgex ?? []) {
      if ('combine' in block) block.clauses.forEach(c => c.produces.forEach(s => result.add(s)));
      else block.produces.forEach(s => result.add(s));
    }
    return result;
  }

  private outputPointIds(c: ConstructionObject): ObjectId[] {
    const slots = this.outputSlotNames(c.name);
    return [...slots].map(s => c.bindings[s]).filter((v): v is ObjectId => typeof v === 'string');
  }

  // Removes a specific output point from a construction's bindings and visual elements.
  // Returns true if the construction still has content to display.
  private partialRemoveOutput(c: ConstructionObject, pointId: ObjectId): boolean {
    for (const [k, v] of Object.entries(c.bindings)) {
      if (v === pointId) delete c.bindings[k];
    }
    c.edges = c.edges.filter(([a, b]) => a !== pointId && b !== pointId);
    if (c.lines) c.lines = c.lines.filter(([a, b]) => a !== pointId && b !== pointId);
    c.circles = c.circles.filter(circ => circ.center !== pointId);
    if (c.circumcircles) c.circumcircles = c.circumcircles.filter(t => !t.includes(pointId));
    return c.edges.length > 0 || (c.lines?.length ?? 0) > 0 ||
           c.circles.length > 0 || (c.circumcircles?.length ?? 0) > 0;
  }

  removeObject(id: ObjectId): void {
    if (!this.objects.has(id)) return;
    this._revision++;

    const toDelete = new Set<ObjectId>([id]);
    const queue: ObjectId[] = [id];

    while (queue.length > 0) {
      const current = queue.shift()!;
      this.objects.delete(current);

      for (const [k, v] of this.objects) {
        if (v.kind === 'point' || toDelete.has(k)) continue;
        if (!this.referencedPointIds(v).includes(current)) continue;

        if (v.kind === 'circle') {
          toDelete.add(k);
          queue.push(k);
        } else if (v.kind === 'construction') {
          const outputSlots = this.outputSlotNames(v.name);
          const deletedSlot = Object.entries(v.bindings).find(([, val]) => val === current)?.[0];
          const isOutput = deletedSlot !== undefined && outputSlots.has(deletedSlot);

          if (isOutput) {
            // Partial delete: remove just this output point and connected edges
            const hasContent = this.partialRemoveOutput(v, current);
            if (!hasContent) {
              toDelete.add(k);
              queue.push(k);
            }
          } else {
            // Full delete: input point gone → whole construction gone + cascade outputs
            toDelete.add(k);
            queue.push(k);
            for (const outputId of this.outputPointIds(v)) {
              if (!toDelete.has(outputId)) {
                toDelete.add(outputId);
                queue.push(outputId);
              }
            }
          }
        }
      }
    }

    this.emit();
  }

  renamePoint(id: ObjectId, label: string): void {
    const o = this.objects.get(id);
    if (!o || o.kind !== 'point') return;
    this.objects.set(id, { ...o, label });
    this._revision++;
    this.emit();
  }

  clear(): void {
    if (this.objects.size === 0 && this.toolState === null && this.previews.length === 0) return;
    this.objects.clear();
    this.toolState = null;
    this.previews = [];
    this.nextId = 1;
    this.nextLabelCode = 65;
    this.undoStack = [];
    this.emit();
  }

  // ---------- undo history ----------

  // Monotonic counter of real mutations. The dispatcher compares it across a
  // click to tell whether the scene changed (vs. only a tool slot advancing).
  get revision(): number {
    return this._revision;
  }

  /**
  Record one undo step: the pre-action scene snapshot plus an optional callback
  that rewinds the active tool's in-progress slots. Called once per user action
  by the dispatcher, so a multi-point construction is a single undo step.
  **/
  pushUndo(snapshot: SceneSnapshot, restoreTool?: () => void): void {
    this.undoStack.push({ snapshot, restoreTool });
    if (this.undoStack.length > Scene.MAX_UNDO) this.undoStack.shift();
  }

  // Revert the most recent recorded action, rewinding both scene and tool.
  // Returns false when history is empty.
  undo(): boolean {
    const entry = this.undoStack.pop();
    if (!entry) return false;
    const { snapshot } = entry;
    this.objects.clear();
    for (const [k, v] of snapshot.objects) this.objects.set(k, v);
    this.nextId = snapshot.nextId;
    this.nextLabelCode = snapshot.nextLabelCode;
    this.toolState = null;
    this.previews = [];
    // Rewind the tool's in-progress slots so the next click continues the
    // construction from the step we just undid.
    entry.restoreTool?.();
    this.emit();
    return true;
  }

  snapshot(): SceneSnapshot {
    return {
      objects: new Map(this.objects),
      nextId: this.nextId,
      nextLabelCode: this.nextLabelCode,
      undoStack: [...this.undoStack],
    };
  }

  restore(snap: SceneSnapshot): void {
    this.objects.clear();
    for (const [k, v] of snap.objects) this.objects.set(k, v);
    this.nextId = snap.nextId;
    this.nextLabelCode = snap.nextLabelCode;
    this.toolState = null;
    this.previews = [];
    this.undoStack = snap.undoStack ? [...snap.undoStack] : [];
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
