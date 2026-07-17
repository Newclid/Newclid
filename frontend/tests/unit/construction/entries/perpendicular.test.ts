import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { perpendicular } from '../../../../src/construction/entries/perpendicular';

describe('perpendicular entry slots', () => {
  it('has three pick slots and no edges or circles', () => {
    expect(perpendicular.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick']);
    expect(perpendicular.edges).toEqual([]);
    expect(perpendicular.circles).toEqual([]);
  });
});

describe('perpendicular entry sketch', () => {
  it('creates a line through p perpendicular to a-b (horizontal base)', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [4, 0], p: [2, 2] });
    const result = perpendicular.sketch({ a, b, p }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'perpendicular',
      bindings: { a, b, p },
      edges: [],
      circles: [],
    });

    const bindings = (result as { bindings: Record<string, string> }).bindings;
    const qId = bindings.q;
    const q = scene.objects.get(qId)!;
    expect(q.kind).toBe('point');

    // The perpendicular to a horizontal line is vertical, so q.x should equal p.x
    if (q.kind === 'point') {
      expect(q.x).toBeCloseTo(2);
    }

    const lines = (result as { lines?: [string, string][] }).lines;
    expect(lines).toEqual([[p, qId]]);
  });

  it('creates a line through p perpendicular to a vertical reference', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [0, 4], p: [2, 2] });
    const result = perpendicular.sketch({ a, b, p }, scene);
    const qId = (result as { bindings: Record<string, string> }).bindings.q;
    const q = scene.objects.get(qId)!;
    // Perp to vertical is horizontal: q.y should equal p.y
    if (q.kind === 'point') {
      expect(q.y).toBeCloseTo(2);
    }
  });
});

describe('perpendicular entry preview', () => {
  it('previews a perpendicular line through the cursor when a and b are set', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const cursor = { x: 2, y: 2, _kind: 'world' as const };
    const prev = perpendicular.preview!({ a, b }, scene, cursor);
    expect(prev).toHaveLength(1);
    expect(prev[0].kind).toBe('auxLine');
  });

  it('previews nothing when a is missing', () => {
    const scene = new Scene();
    const cursor = { x: 2, y: 2, _kind: 'world' as const };
    expect(perpendicular.preview!({}, scene, cursor)).toEqual([]);
  });

  it('previews nothing when a and b are the same (degenerate)', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 2, y: 2, _kind: 'world' as const };
    expect(perpendicular.preview!({ a, b: a }, scene, cursor)).toEqual([]);
  });
});

describe('perpendicular entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(perpendicular.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct a and b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(perpendicular.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(perpendicular.validate!({}, scene)).toBeNull();
  });
});
