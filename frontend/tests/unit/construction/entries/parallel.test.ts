import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { parallel } from '../../../../src/construction/entries/parallel';

describe('parallel entry slots', () => {
  it('has three pick slots and no edges or circles', () => {
    expect(parallel.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick']);
    expect(parallel.edges).toEqual([]);
    expect(parallel.circles).toEqual([]);
  });
});

describe('parallel entry sketch', () => {
  it('creates a line through p parallel to a horizontal reference line', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [4, 0], p: [1, 3] });
    const result = parallel.sketch({ a, b, p }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'parallel',
      bindings: { a, b, p },
      edges: [],
      circles: [],
    });

    const qId = (result as { bindings: Record<string, string> }).bindings.q;
    const q = scene.objects.get(qId)!;
    // Parallel to horizontal: q should be at same y as p
    if (q.kind === 'point') {
      expect(q.y).toBeCloseTo(3);
    }

    const lines = (result as { lines?: [string, string][] }).lines;
    expect(lines).toEqual([[p, qId]]);
  });
});

describe('parallel entry preview', () => {
  it('previews a parallel line through the cursor when a and b are set', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const cursor = { x: 1, y: 3, _kind: 'world' as const };
    const prev = parallel.preview!({ a, b }, scene, cursor);
    expect(prev).toHaveLength(1);
    expect(prev[0].kind).toBe('auxLine');
  });

  it('previews nothing when a or b is missing', () => {
    const scene = new Scene();
    const cursor = { x: 1, y: 3, _kind: 'world' as const };
    expect(parallel.preview!({}, scene, cursor)).toEqual([]);
  });

  it('previews nothing for a degenerate reference line', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 1, y: 3, _kind: 'world' as const };
    expect(parallel.preview!({ a, b: a }, scene, cursor)).toEqual([]);
  });
});

describe('parallel entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(parallel.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects p on the reference line', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [4, 0], p: [2, 0] });
    expect(parallel.validate!({ a, b, p }, scene)).toMatch(/not lie on/i);
  });

  it('accepts p off the reference line', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [4, 0], p: [2, 3] });
    expect(parallel.validate!({ a, b, p }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(parallel.validate!({}, scene)).toBeNull();
  });
});
