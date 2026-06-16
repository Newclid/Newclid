import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { triangle } from '../../../../src/construction/entries/triangle';

describe('triangle entry slots', () => {
  it('has three pick slots and one edge spec', () => {
    expect(triangle.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick']);
    expect(triangle.edges).toEqual([{ pointIds: ['a', 'b'] }]);
    expect(triangle.circles).toEqual([]);
  });
});

describe('triangle entry sketch', () => {
  it('emits all three edges closing the triangle', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [4, 0], c: [2, 3] });
    expect(triangle.sketch({ a, b, c }, scene)).toMatchObject({
      kind: 'construction',
      name: 'triangle',
      bindings: { a, b, c },
      edges: [[a, b], [b, c], [c, a]],
      circles: [],
    });
  });
});

describe('triangle entry preview', () => {
  it('previews two open sides once a and b are placed', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const cursor = { x: 2, y: 3, _kind: 'world' as const };
    const prev = triangle.preview!({ a, b }, scene, cursor);
    expect(prev).toHaveLength(2);
    expect(prev[0].kind).toBe('auxLine');
    expect(prev[1].kind).toBe('auxLine');
  });

  it('previews nothing before two points are placed', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 2, y: 3, _kind: 'world' as const };
    expect(triangle.preview!({ a }, scene, cursor)).toEqual([]);
  });
});

describe('triangle entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(triangle.validate!({ a, b: a, c: b }, scene)).toMatch(/distinct/i);
  });

  it('rejects b === c', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(triangle.validate!({ a, b, c: b }, scene)).toMatch(/distinct/i);
  });

  it('rejects a === c', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(triangle.validate!({ a, b, c: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects collinear vertices', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [2, 0], c: [4, 0] });
    expect(triangle.validate!({ a, b, c }, scene)).toMatch(/collinear/i);
  });

  it('accepts non-collinear distinct vertices', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [4, 0], c: [2, 3] });
    expect(triangle.validate!({ a, b, c }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(triangle.validate!({ a, b }, scene)).toBeNull();
  });
});
