import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { isoscelesTriangle } from '../../../../src/construction/entries/isosceles_triangle';

describe('isosceles_triangle entry slots', () => {
  it('has two pick slots, one derive slot, and one edge spec', () => {
    expect(isoscelesTriangle.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'derive']);
    expect(isoscelesTriangle.edges).toEqual([{ pointIds: ['a', 'b'] }]);
  });
});

describe('isosceles_triangle entry sketch', () => {
  it('emits all three edges with the apex already placed', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [4, 0], c: [2, 3] });
    const result = isoscelesTriangle.sketch({ a, b, c }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'iso_triangle',
      bindings: { a, b, c },
      edges: [[a, b], [b, c], [c, a]],
      circles: [],
    });
  });
});

describe('isosceles_triangle derive slot project', () => {
  it('snaps the apex onto the perpendicular bisector of a-b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const deriveSlot = isoscelesTriangle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    // Cursor above the midpoint: apex should land at midpoint-x, above
    const cursor = { x: 2, y: 5, _kind: 'world' as const };
    const pt = deriveSlot.project({ a, b }, scene, cursor);
    expect(pt.x).toBeCloseTo(2); // midpoint x
    expect(pt.y).toBeGreaterThan(0);
  });
});

describe('isosceles_triangle derive slot preview', () => {
  it('shows the bisector guide once a and b are placed', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const deriveSlot = isoscelesTriangle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    const prev = deriveSlot.preview({ a, b }, scene);
    expect(prev).toHaveLength(1);
    expect(prev[0].kind).toBe('auxLine');
  });

  it('shows nothing before a and b are placed', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const deriveSlot = isoscelesTriangle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');
    expect(deriveSlot.preview({ a }, scene)).toEqual([]);
  });
});

describe('isosceles_triangle entry preview', () => {
  it('previews the two equal legs to the apex at the cursor', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const cursor = { x: 2, y: 3, _kind: 'world' as const };
    const prev = isoscelesTriangle.preview!({ a, b }, scene, cursor);
    expect(prev).toHaveLength(2);
    expect(prev.every(p => p.kind === 'auxLine')).toBe(true);
  });

  it('previews nothing before two points are placed', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 2, y: 3, _kind: 'world' as const };
    expect(isoscelesTriangle.preview!({ a }, scene, cursor)).toEqual([]);
  });
});

describe('isosceles_triangle entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(isoscelesTriangle.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct a and b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    expect(isoscelesTriangle.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(isoscelesTriangle.validate!({}, scene)).toBeNull();
  });
});
