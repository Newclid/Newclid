import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { eqdistance } from '../../../../src/construction/entries/eqdistance';

describe('eqdistance entry slots', () => {
  it('has two pick-existing slots, one pick slot, and one derive slot', () => {
    expect(eqdistance.slots.map(s => s.kind)).toEqual(['pick-existing', 'pick-existing', 'pick', 'derive']);
  });
});

describe('eqdistance entry sketch', () => {
  it('records the equal-distance construction with the given bindings', () => {
    const scene = new Scene();
    const { a, b, c, x } = addPoints(scene, { b: [0, 0], c: [3, 0], a: [5, 0], x: [8, 0] });
    const result = eqdistance.sketch({ a, b, c, x }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'eqdistance',
      bindings: { a, b, c, x },
      edges: [[a, x]],
      circles: [],
    });
  });
});

describe('eqdistance derive slot project', () => {
  it('snaps the cursor direction onto the circle of radius |bc| around a', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { b: [0, 0], c: [3, 0], a: [5, 5] });
    const deriveSlot = eqdistance.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    // Cursor directly to the right of a: result should be at (5+3, 5) = (8, 5)
    const cursor = { x: 10, y: 5, _kind: 'world' as const };
    const pt = deriveSlot.project({ a, b, c }, scene, cursor);
    expect(pt.x).toBeCloseTo(8);
    expect(pt.y).toBeCloseTo(5);
  });

  it('falls back to the right direction when cursor is at a', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { b: [0, 0], c: [3, 0], a: [5, 5] });
    const deriveSlot = eqdistance.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    // Cursor at a: should fall back to direction (1,0)
    const cursor = { x: 5, y: 5, _kind: 'world' as const };
    const pt = deriveSlot.project({ a, b, c }, scene, cursor);
    expect(pt.x).toBeCloseTo(8);
    expect(pt.y).toBeCloseTo(5);
  });
});

describe('eqdistance derive slot preview', () => {
  it('shows the constraint circle once a, b, c are all placed', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { b: [0, 0], c: [3, 0], a: [5, 5] });
    const deriveSlot = eqdistance.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    const prev = deriveSlot.preview({ a, b, c }, scene);
    expect(prev).toHaveLength(1);
    expect(prev[0].kind).toBe('circle');
  });

  it('shows nothing before all three anchor points are placed', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [5, 5], b: [0, 0] });
    const deriveSlot = eqdistance.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    expect(deriveSlot.preview({ a, b }, scene)).toEqual([]);
  });
});

describe('eqdistance entry validate', () => {
  it('rejects b === c', () => {
    const scene = new Scene();
    const { b } = addPoints(scene, { b: [0, 0] });
    expect(eqdistance.validate!({ b, c: b }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct b and c', () => {
    const scene = new Scene();
    const { b, c } = addPoints(scene, { b: [0, 0], c: [3, 0] });
    expect(eqdistance.validate!({ b, c }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(eqdistance.validate!({}, scene)).toBeNull();
  });
});
