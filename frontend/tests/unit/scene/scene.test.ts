import { describe, it, expect, vi } from 'vitest';
import { Scene } from '../../../src/scene/scene';
import type { GeoObject } from '../../../src/geometry/types-object';

describe('Scene points()', () => {
  it('yields only point objects, skipping other kinds', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    scene.addObject({ kind: 'circle', mode: 'center-through', center: 'p1', through: 'p1' });
    const labels = [...scene.points()].map((p) => p.label);
    expect(labels).toEqual(['A']);
  });
});

describe('Scene tool state', () => {
  it('setTool switches the active tool, clears toolState and notifies', () => {
    const scene = new Scene();
    scene.setToolState({ firstPoint: 'p1' });
    const listener = vi.fn();
    scene.subscribe(listener);
    scene.setTool('circle');
    expect(scene.tool).toBe('circle');
    expect(scene.toolState).toBeNull();
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('setTool is a no-op when the tool is already active', () => {
    const scene = new Scene();
    scene.setToolState({ firstPoint: 'p1' });
    const listener = vi.fn();
    scene.subscribe(listener);
    scene.setTool(scene.tool);
    expect(listener).not.toHaveBeenCalled();
    expect(scene.toolState).toEqual({ firstPoint: 'p1' });
  });

  it('setToolState replaces the in-progress slot state and notifies', () => {
    const scene = new Scene();
    const listener = vi.fn();
    scene.subscribe(listener);
    scene.setToolState({ firstPoint: 'p1' });
    expect(scene.toolState).toEqual({ firstPoint: 'p1' });
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('setSlotHint updates the hint and notifies', () => {
    const scene = new Scene();
    const listener = vi.fn();
    scene.subscribe(listener);
    scene.setSlotHint('pick a center');
    expect(scene.slotHint).toBe('pick a center');
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('setSlotError updates the error and notifies', () => {
    const scene = new Scene();
    const listener = vi.fn();
    scene.subscribe(listener);
    scene.setSlotError('invalid selection');
    expect(scene.slotError).toBe('invalid selection');
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('setPreviews updates previews without notifying listeners', () => {
    const scene = new Scene();
    const listener = vi.fn();
    scene.subscribe(listener);
    scene.setPreviews([{ kind: 'highlightPoint', pos: { x: 1, y: 2 } }]);
    expect(scene.previews).toEqual([{ kind: 'highlightPoint', pos: { x: 1, y: 2 } }]);
    expect(listener).not.toHaveBeenCalled();
  });
});

describe('Scene.addPoint', () => {
  it('assigns an incrementing id and an auto label, bumps revision and notifies', () => {
    const scene = new Scene();
    const listener = vi.fn();
    scene.subscribe(listener);
    const before = scene.revision;
    const id = scene.addPoint(3, 4);
    const obj = scene.objects.get(id);
    expect(obj).toEqual({ id, kind: 'point', x: 3, y: 4, label: 'A' });
    expect(scene.revision).toBe(before + 1);
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('labels successive points A, B, C…', () => {
    const scene = new Scene();
    const ids = [scene.addPoint(0, 0), scene.addPoint(1, 1), scene.addPoint(2, 2)];
    const labels = ids.map((id) => scene.objects.get(id));
    expect(labels.map((o) => (o as { label: string }).label)).toEqual(['A', 'B', 'C']);
  });

  it('cycles into lowercase letters once A–Z are exhausted', () => {
    const scene = new Scene();
    for (let i = 0; i < 26; i++) scene.addPoint(i, 0);
    const id = scene.addPoint(99, 99);
    expect((scene.objects.get(id) as { label: string }).label).toBe('a');
  });

  it('skips over non-point objects while scanning for a free label', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(1, 0);
    scene.addObject({ kind: 'circle', mode: 'center-through', center: a, through: b });
    const id = scene.addPoint(2, 2);
    expect((scene.objects.get(id) as { label: string }).label).toBe('C');
  });

  it('falls back to A when a restored snapshot carries a legacy/invalid label code', () => {
    const scene = new Scene();
    scene.restore({ objects: new Map(), nextId: 1, nextLabelCode: 0 });
    const id = scene.addPoint(0, 0);
    expect((scene.objects.get(id) as { label: string }).label).toBe('A');
  });

  it('reuses a freed label once the cycle wraps back around to it', () => {
    const scene = new Scene();
    const ids = [];
    for (let i = 0; i < 52; i++) ids.push(scene.addPoint(i, 0)); // exhausts A-Z, a-z
    scene.removeObject(ids[0]); // frees 'A'
    const id = scene.addPoint(99, 99);
    expect((scene.objects.get(id) as { label: string }).label).toBe('A');
  });
});

describe('Scene.addObject', () => {
  it('assigns an id prefixed with "o", bumps revision and notifies', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(1, 0);
    const listener = vi.fn();
    scene.subscribe(listener);
    const before = scene.revision;
    const id = scene.addObject({ kind: 'circle', mode: 'center-through', center: a, through: b });
    expect(id.startsWith('o')).toBe(true);
    expect(scene.objects.get(id)).toEqual({ id, kind: 'circle', mode: 'center-through', center: a, through: b });
    expect(scene.revision).toBe(before + 1);
    expect(listener).toHaveBeenCalledTimes(1);
  });
});

describe('Scene.movePoint', () => {
  it('updates the coordinates of an existing point', () => {
    const scene = new Scene();
    const id = scene.addPoint(0, 0);
    scene.movePoint(id, 5, 6);
    expect(scene.objects.get(id)).toMatchObject({ x: 5, y: 6 });
  });

  it('bumps revision and notifies on a successful move', () => {
    const scene = new Scene();
    const id = scene.addPoint(0, 0);
    const listener = vi.fn();
    scene.subscribe(listener);
    const before = scene.revision;
    scene.movePoint(id, 5, 6);
    expect(scene.revision).toBe(before + 1);
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('is a no-op for an unknown id', () => {
    const scene = new Scene();
    const listener = vi.fn();
    scene.subscribe(listener);
    const before = scene.revision;
    scene.movePoint('missing', 1, 1);
    expect(scene.revision).toBe(before);
    expect(listener).not.toHaveBeenCalled();
  });

  it('is a no-op when the id refers to a non-point object', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(1, 0);
    const circleId = scene.addObject({ kind: 'circle', mode: 'center-through', center: a, through: b });
    const before = scene.revision;
    scene.movePoint(circleId, 9, 9);
    expect(scene.revision).toBe(before);
  });
});

describe('Scene.setPointColor', () => {
  it('sets the color of an existing point', () => {
    const scene = new Scene();
    const id = scene.addPoint(0, 0);
    scene.setPointColor(id, 'red');
    expect(scene.objects.get(id)).toMatchObject({ color: 'red' });
  });

  it('is a no-op for an unknown id', () => {
    const scene = new Scene();
    const before = scene.revision;
    scene.setPointColor('missing', 'red');
    expect(scene.revision).toBe(before);
  });
});

describe('Scene.removeObject', () => {
  it('removes the object and bumps revision', () => {
    const scene = new Scene();
    const id = scene.addPoint(0, 0);
    const before = scene.revision;
    scene.removeObject(id);
    expect(scene.objects.has(id)).toBe(false);
    expect(scene.revision).toBe(before + 1);
  });

  it('is a no-op for an unknown id', () => {
    const scene = new Scene();
    const listener = vi.fn();
    scene.subscribe(listener);
    const before = scene.revision;
    scene.removeObject('missing');
    expect(scene.revision).toBe(before);
    expect(listener).not.toHaveBeenCalled();
  });

  it('cascades to a center-through circle referencing the removed point', () => {
    const scene = new Scene();
    const center = scene.addPoint(0, 0);
    const through = scene.addPoint(1, 0);
    const circleId = scene.addObject({ kind: 'circle', mode: 'center-through', center, through });
    scene.removeObject(center);
    expect(scene.objects.has(circleId)).toBe(false);
  });

  it('cascades to a three-points circle when the removed point is p1, p2 or p3', () => {
    for (const which of ['p1', 'p2', 'p3'] as const) {
      const scene = new Scene();
      const p1 = scene.addPoint(0, 0);
      const p2 = scene.addPoint(1, 0);
      const p3 = scene.addPoint(0, 1);
      const circleId = scene.addObject({ kind: 'circle', mode: 'three-points', p1, p2, p3 });
      scene.removeObject({ p1, p2, p3 }[which]);
      expect(scene.objects.has(circleId)).toBe(false);
    }
  });

  it('leaves a three-points circle untouched when it does not reference the removed point', () => {
    const scene = new Scene();
    const p1 = scene.addPoint(0, 0);
    const p2 = scene.addPoint(1, 0);
    const p3 = scene.addPoint(0, 1);
    const other = scene.addPoint(5, 5);
    const circleId = scene.addObject({ kind: 'circle', mode: 'three-points', p1, p2, p3 });
    scene.removeObject(other);
    expect(scene.objects.has(circleId)).toBe(true);
  });

  it('leaves circles untouched when they do not reference the removed point', () => {
    const scene = new Scene();
    const center = scene.addPoint(0, 0);
    const through = scene.addPoint(1, 0);
    const other = scene.addPoint(5, 5);
    const circleId = scene.addObject({ kind: 'circle', mode: 'center-through', center, through });
    scene.removeObject(other);
    expect(scene.objects.has(circleId)).toBe(true);
  });

  it('cascades to a construction whose bindings reference the removed point', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(1, 0);
    const constructionId = scene.addObject({
      kind: 'construction',
      name: 'segment',
      bindings: { a, b },
      edges: [[a, b]],
      circles: [],
    });
    scene.removeObject(a);
    expect(scene.objects.has(constructionId)).toBe(false);
  });

  it('leaves a construction untouched when its bindings do not reference the removed point', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(1, 0);
    const unrelated = scene.addPoint(5, 5);
    const constructionId = scene.addObject({
      kind: 'construction',
      name: 'segment',
      bindings: { a, b },
      edges: [[a, b]],
      circles: [],
    });
    scene.removeObject(unrelated);
    expect(scene.objects.has(constructionId)).toBe(true);
  });
});

describe('Scene.clear', () => {
  it('resets objects, tool state, previews and id/label counters', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    scene.setToolState({ firstPoint: 'p1' });
    scene.setPreviews([{ kind: 'highlightPoint', pos: { x: 0, y: 0 } }]);
    scene.clear();
    expect(scene.objects.size).toBe(0);
    expect(scene.toolState).toBeNull();
    expect(scene.previews).toEqual([]);
    const id = scene.addPoint(9, 9);
    expect(id).toBe('p1');
    expect((scene.objects.get(id) as { label: string }).label).toBe('A');
  });

  it('clears the undo stack', () => {
    const scene = new Scene();
    scene.pushUndo(scene.snapshot());
    scene.addPoint(0, 0);
    scene.clear();
    expect(scene.undo()).toBe(false);
  });

  it('is a no-op and does not notify when already empty', () => {
    const scene = new Scene();
    const listener = vi.fn();
    scene.subscribe(listener);
    scene.clear();
    expect(listener).not.toHaveBeenCalled();
  });
});

describe('Scene undo history', () => {
  it('returns false when there is nothing to undo', () => {
    const scene = new Scene();
    expect(scene.undo()).toBe(false);
  });

  it('restores the snapshot taken before the action and notifies', () => {
    const scene = new Scene();
    scene.pushUndo(scene.snapshot());
    scene.addPoint(0, 0);
    const listener = vi.fn();
    scene.subscribe(listener);
    const result = scene.undo();
    expect(result).toBe(true);
    expect(scene.objects.size).toBe(0);
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it('clears in-progress tool state and previews on undo', () => {
    const scene = new Scene();
    scene.pushUndo(scene.snapshot());
    scene.addPoint(0, 0);
    scene.setToolState({ firstPoint: 'p1' });
    scene.setPreviews([{ kind: 'highlightPoint', pos: { x: 0, y: 0 } }]);
    scene.undo();
    expect(scene.toolState).toBeNull();
    expect(scene.previews).toEqual([]);
  });

  it('invokes the restoreTool callback bound to the undone entry', () => {
    const scene = new Scene();
    const restoreTool = vi.fn();
    scene.pushUndo(scene.snapshot(), restoreTool);
    scene.addPoint(0, 0);
    scene.undo();
    expect(restoreTool).toHaveBeenCalledTimes(1);
  });

  it('pops entries in last-in-first-out order across multiple undos', () => {
    const scene = new Scene();
    scene.pushUndo(scene.snapshot());
    const a = scene.addPoint(0, 0);
    scene.pushUndo(scene.snapshot());
    scene.addPoint(1, 1);
    scene.undo();
    expect(scene.objects.has(a)).toBe(true);
    expect(scene.objects.size).toBe(1);
    scene.undo();
    expect(scene.objects.size).toBe(0);
  });

  it('drops the oldest entry once the undo stack exceeds its cap', () => {
    const scene = new Scene();
    // Push one more than MAX_UNDO (100) snapshots, each before adding a point.
    for (let i = 0; i < 101; i++) {
      scene.pushUndo(scene.snapshot());
      scene.addPoint(i, 0);
    }
    // The oldest pushed snapshot (taken before any point existed) should have
    // been evicted, so after undoing everything available, one point remains.
    let undone = 0;
    while (scene.undo()) undone++;
    expect(undone).toBe(100);
    expect(scene.objects.size).toBe(1);
  });
});

describe('Scene.snapshot and Scene.restore', () => {
  it('captures a deep-enough copy that later mutations do not affect it', () => {
    const scene = new Scene();
    const id = scene.addPoint(0, 0);
    const snap = scene.snapshot();
    scene.movePoint(id, 9, 9);
    expect(snap.objects.get(id)).toMatchObject({ x: 0, y: 0 });
  });

  it('restores objects, id/label counters and undo stack from a snapshot', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    const snap = scene.snapshot();
    scene.addPoint(1, 1);
    scene.restore(snap);
    expect(scene.objects.size).toBe(1);
    const id = scene.addPoint(5, 5);
    expect((scene.objects.get(id) as { label: string }).label).toBe('B');
  });

  it('restore clears in-progress tool state and previews', () => {
    const scene = new Scene();
    const snap = scene.snapshot();
    scene.setToolState({ firstPoint: 'p1' });
    scene.setPreviews([{ kind: 'highlightPoint', pos: { x: 0, y: 0 } }]);
    scene.restore(snap);
    expect(scene.toolState).toBeNull();
    expect(scene.previews).toEqual([]);
  });

  it('restore falls back to an empty undo stack when the snapshot has none', () => {
    const scene = new Scene();
    scene.pushUndo(scene.snapshot());
    scene.addPoint(0, 0);
    const snap: ReturnType<Scene['snapshot']> = { objects: new Map(), nextId: 1, nextLabelCode: 65 };
    scene.restore(snap);
    expect(scene.undo()).toBe(false);
  });
});

describe('Scene.serialize', () => {
  it('serializes points', () => {
    const scene = new Scene();
    const id = scene.addPoint(1, 2);
    const out = scene.serialize();
    expect(out.points).toEqual([{ id, label: 'A', x: 1, y: 2 }]);
    expect(out.circles).toBeUndefined();
    expect(out.constructions).toBeUndefined();
  });

  it('serializes a center-through circle with a radius derived from its points', () => {
    const scene = new Scene();
    const center = scene.addPoint(0, 0);
    const through = scene.addPoint(3, 4);
    scene.addObject({ kind: 'circle', mode: 'center-through', center, through });
    const out = scene.serialize();
    expect(out.circles).toEqual([{ id: 'o3', kind: 'center-radius', center, radius: 5 }]);
  });

  it('skips a center-through circle whose endpoints are missing', () => {
    const scene = new Scene();
    const center = scene.addPoint(0, 0);
    scene.addObject({ kind: 'circle', mode: 'center-through', center, through: 'missing' });
    const out = scene.serialize();
    expect(out.circles).toBeUndefined();
  });

  it('omits three-points circles from serialization', () => {
    const scene = new Scene();
    const p1 = scene.addPoint(0, 0);
    const p2 = scene.addPoint(1, 0);
    const p3 = scene.addPoint(0, 1);
    scene.addObject({ kind: 'circle', mode: 'three-points', p1, p2, p3 });
    const out = scene.serialize();
    expect(out.circles).toBeUndefined();
  });

  it('serializes constructions', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(1, 0);
    scene.addObject({
      kind: 'construction',
      name: 'segment',
      bindings: { a, b },
      edges: [[a, b]],
      circles: [],
    });
    const out = scene.serialize();
    expect(out.constructions).toEqual([
      { id: 'o3', name: 'segment', bindings: { a, b }, edges: [[a, b]], circles: [] },
    ]);
  });
});

describe('Scene pub/sub', () => {
  it('notifies every subscribed listener on a mutation', () => {
    const scene = new Scene();
    const a = vi.fn();
    const b = vi.fn();
    scene.subscribe(a);
    scene.subscribe(b);
    scene.addPoint(0, 0);
    expect(a).toHaveBeenCalledTimes(1);
    expect(b).toHaveBeenCalledTimes(1);
  });

  it('stops notifying a listener once it unsubscribes', () => {
    const scene = new Scene();
    const listener = vi.fn();
    const unsubscribe = scene.subscribe(listener);
    unsubscribe();
    scene.addPoint(0, 0);
    expect(listener).not.toHaveBeenCalled();
  });
});

describe('GeoObject typing smoke check', () => {
  it('accepts a fully-formed circle object shape', () => {
    const circle: GeoObject = {
      id: 'c1',
      kind: 'circle',
      mode: 'center-through',
      center: 'p1',
      through: 'p2',
    };
    expect(circle.kind).toBe('circle');
  });
});
