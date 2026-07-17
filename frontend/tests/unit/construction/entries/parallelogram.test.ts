import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { parallelogram } from '../../../../src/construction/entries/parallelogram';

describe('parallelogram entry slots', () => {
  it('has three pick slots and two edge specs', () => {
    expect(parallelogram.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick']);
    expect(parallelogram.edges).toEqual([
      { pointIds: ['a', 'b'] },
      { pointIds: ['b', 'c'] },
    ]);
  });
});

describe('parallelogram entry sketch', () => {
  it('computes the fourth vertex as a + c - b', () => {
    const scene = new Scene();
    // a=(0,0), b=(3,0), c=(3,2) → x = (0,2)
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [3, 0], c: [3, 2] });
    const result = parallelogram.sketch({ a, b, c }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'parallelogram',
      bindings: { a, b, c },
      circles: [],
    });

    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    expect(x.kind).toBe('point');
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(0);
      expect(x.y).toBeCloseTo(2);
    }

    const edges = (result as { edges: [string, string][] }).edges;
    expect(edges).toEqual([[a, b], [b, c], [c, xId], [xId, a]]);
  });
});

describe('parallelogram entry preview', () => {
  it('previews the full shape while placing c', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [3, 0] });
    const cursor = { x: 3, y: 2, _kind: 'world' as const };
    const prev = parallelogram.preview!({ a, b }, scene, cursor);
    expect(prev).toHaveLength(3);
    expect(prev.every(p => p.kind === 'auxLine')).toBe(true);
  });

  it('previews nothing before two points are placed', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 3, y: 2, _kind: 'world' as const };
    expect(parallelogram.preview!({ a }, scene, cursor)).toEqual([]);
  });
});

describe('parallelogram entry validate', () => {
  it('rejects duplicate points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [3, 0] });
    expect(parallelogram.validate!({ a, b, c: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects collinear points', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [2, 0], c: [4, 0] });
    expect(parallelogram.validate!({ a, b, c }, scene)).toMatch(/collinear/i);
  });

  it('accepts valid non-collinear distinct points', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [3, 0], c: [3, 2] });
    expect(parallelogram.validate!({ a, b, c }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(parallelogram.validate!({}, scene)).toBeNull();
  });

  // validate should return null when bound point IDs do not exist in the scene
  it('validate returns null when bound ids are not yet in the scene', () => {
    const scene = new Scene();
    expect(parallelogram.validate!({ a: 'p99', b: 'p100', c: 'p101' }, scene)).toBeNull();
  });
});
