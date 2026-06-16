import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { angleBisector } from '../../../../src/construction/entries/angle_bisector';

describe('angle_bisector entry slots', () => {
  it('has three pick slots and two edge specs', () => {
    expect(angleBisector.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick']);
    expect(angleBisector.edges).toEqual([
      { pointIds: ['a', 'b'] },
      { pointIds: ['b', 'c'] },
    ]);
  });
});

describe('angle_bisector entry sketch', () => {
  it('places x on the bisector of a right angle at b', () => {
    const scene = new Scene();
    // a=(4,0), b=(0,0), c=(0,4): right angle at origin, bisector is y=x direction
    const { a, b, c } = addPoints(scene, { a: [4, 0], b: [0, 0], c: [0, 4] });
    const result = angleBisector.sketch({ a, b, c }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'angle_bisector',
      bindings: { a, b, c },
      circles: [],
    });

    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    expect(x.kind).toBe('point');
    if (x.kind === 'point') {
      // Bisector of 90° at origin along x and y axes is y=x direction
      expect(x.x).toBeCloseTo(x.y);
    }

    const edges = (result as { edges: [string, string][] }).edges;
    expect(edges).toEqual([[a, b], [b, c]]);

    const lines = (result as { lines?: [string, string][] }).lines;
    expect(lines).toEqual([[b, xId]]);
  });

  it('colors the bisector point red', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [4, 0], b: [0, 0], c: [0, 4] });
    const result = angleBisector.sketch({ a, b, c }, scene);
    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    if (x.kind === 'point') expect(x.color).toBe('red');
  });
});

describe('angle_bisector entry validate', () => {
  it('rejects duplicate points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(angleBisector.validate!({ a, b, c: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects collinear points', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [2, 0], c: [4, 0] });
    expect(angleBisector.validate!({ a, b, c }, scene)).toMatch(/collinear/i);
  });

  it('accepts non-collinear distinct points', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [4, 0], b: [0, 0], c: [0, 4] });
    expect(angleBisector.validate!({ a, b, c }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(angleBisector.validate!({}, scene)).toBeNull();
  });
});
