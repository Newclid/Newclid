import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { segment } from '../../../../src/construction/entries/segment';

describe('segment entry slots', () => {
  it('has two pick slots and one edge spec', () => {
    expect(segment.slots.map(s => s.kind)).toEqual(['pick', 'pick']);
    expect(segment.edges).toEqual([{ pointIds: ['a', 'b'] }]);
    expect(segment.circles).toEqual([]);
  });
});

describe('segment entry sketch', () => {
  it('emits a construction with an edge between the two points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [5, 0] });
    const result = segment.sketch({ a, b }, scene);
    expect(result).toMatchObject({
      kind: 'construction',
      name: 'segment',
      bindings: { a, b },
      edges: [[a, b]],
      circles: [],
    });
  });
});

describe('segment entry validate', () => {
  it('rejects the same point for both endpoints', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [1, 2] });
    expect(segment.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts two distinct points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [3, 4] });
    expect(segment.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts incomplete binding', () => {
    const scene = new Scene();
    expect(segment.validate!({}, scene)).toBeNull();
  });
});
