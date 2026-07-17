import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { line } from '../../../../src/construction/entries/line';

describe('line entry slots', () => {
  it('has two pick slots and no edges or circles', () => {
    expect(line.slots.map(s => s.kind)).toEqual(['pick', 'pick']);
    expect(line.edges).toEqual([]);
    expect(line.circles).toEqual([]);
  });
});

describe('line entry sketch', () => {
  it('emits a construction with the two points on a line', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const result = line.sketch({ a, b }, scene);
    expect(result).toMatchObject({
      kind: 'construction',
      name: 'line',
      bindings: { a, b },
      edges: [],
      lines: [[a, b]],
      circles: [],
    });
  });
});

describe('line entry validate', () => {
  it('rejects the same point for both slots', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(line.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts two distinct points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(line.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts an incomplete binding', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(line.validate!({ a }, scene)).toBeNull();
  });

  it('accepts empty binding', () => {
    const scene = new Scene();
    expect(line.validate!({}, scene)).toBeNull();
  });
});
