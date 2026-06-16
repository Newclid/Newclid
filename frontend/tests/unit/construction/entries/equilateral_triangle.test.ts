import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { equilateralTriangle } from '../../../../src/construction/entries/equilateral_triangle';

describe('equilateral_triangle entry slots', () => {
  it('has two pick slots, one derive slot, and one edge spec', () => {
    expect(equilateralTriangle.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'derive']);
    expect(equilateralTriangle.edges).toEqual([{ pointIds: ['a', 'b'] }]);
  });
});

describe('equilateral_triangle entry sketch', () => {
  it('emits all three edges with the apex already placed', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [2, 0], c: [1, Math.sqrt(3)] });
    const result = equilateralTriangle.sketch({ a, b, c }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'eq_triangle',
      bindings: { a, b, c },
      edges: [[a, b], [b, c], [c, a]],
      circles: [],
    });
  });
});

describe('equilateral_triangle entry derive slot project', () => {
  it('snaps the apex to the equilateral position above the base when cursor is above', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [2, 0] });
    const deriveSlot = equilateralTriangle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    const cursor = { x: 1, y: 5, _kind: 'world' as const }; // above the base
    const pt = deriveSlot.project({ a, b }, scene, cursor);
    expect(pt.y).toBeGreaterThan(0);
    expect(pt.x).toBeCloseTo(1);
  });

  it('snaps the apex below the base when cursor is below', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [2, 0] });
    const deriveSlot = equilateralTriangle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    const cursor = { x: 1, y: -5, _kind: 'world' as const }; // below the base
    const pt = deriveSlot.project({ a, b }, scene, cursor);
    expect(pt.y).toBeLessThan(0);
  });
});

describe('equilateral_triangle entry preview', () => {
  it('previews both apex candidates once a and b are placed', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [2, 0] });
    const cursor = { x: 1, y: 5, _kind: 'world' as const };
    const prev = equilateralTriangle.preview!({ a, b }, scene, cursor);
    // 4 auxLines: 2 sides for each of the 2 apex candidates
    expect(prev).toHaveLength(4);
    expect(prev.every(p => p.kind === 'auxLine')).toBe(true);
  });

  it('previews nothing before a and b are placed', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 1, y: 5, _kind: 'world' as const };
    expect(equilateralTriangle.preview!({ a }, scene, cursor)).toEqual([]);
  });
});

describe('equilateral_triangle derive slot inner preview', () => {
  it('returns empty — triangle sides are previewed at the entry level', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [2, 0] });
    const deriveSlot = equilateralTriangle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');
    expect(deriveSlot.preview({ a, b }, scene)).toEqual([]);
  });
});

describe('equilateral_triangle entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(equilateralTriangle.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct a and b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [2, 0] });
    expect(equilateralTriangle.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(equilateralTriangle.validate!({}, scene)).toBeNull();
  });
});
