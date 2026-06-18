import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { midpoint } from '../../../../src/construction/entries/midpoint';

describe('midpoint entry slots', () => {
  it('has two pick slots and one edge spec', () => {
    expect(midpoint.slots.map(s => s.kind)).toEqual(['pick', 'pick']);
    expect(midpoint.edges).toEqual([{ pointIds: ['a', 'b'] }]);
  });
});

describe('midpoint entry sketch', () => {
  it('creates a new point at the midpoint and draws the segment', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const countBefore = scene.objects.size;
    const result = midpoint.sketch({ a, b }, scene);

    expect(scene.objects.size).toBe(countBefore + 1);
    expect(result).toMatchObject({
      kind: 'construction',
      name: 'midpoint',
      bindings: { a, b },
      edges: [[a, b]],
      circles: [],
    });

    const mId = (result as { bindings: Record<string, string> }).bindings.m;
    const m = scene.objects.get(mId)!;
    expect(m.kind).toBe('point');
    if (m.kind === 'point') {
      expect(m.x).toBeCloseTo(2);
      expect(m.y).toBeCloseTo(0);
    }
  });

  it('colors the midpoint red', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 2], b: [4, 6] });
    const result = midpoint.sketch({ a, b }, scene);
    const mId = (result as { bindings: Record<string, string> }).bindings.m;
    const m = scene.objects.get(mId)!;
    if (m.kind === 'point') expect(m.color).toBe('red');
  });
});

describe('midpoint entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(midpoint.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 1] });
    expect(midpoint.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(midpoint.validate!({}, scene)).toBeNull();
  });
});
