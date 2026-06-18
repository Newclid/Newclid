import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { onCircle } from '../../../../src/construction/entries/on_circle';

describe('on_circle entry slots', () => {
  it('has two pick slots and one derive slot', () => {
    expect(onCircle.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'derive']);
    expect(onCircle.edges).toEqual([]);
    expect(onCircle.circles).toEqual([]);
  });
});

describe('on_circle entry sketch', () => {
  it('records the point-on-circle construction with a radius edge', () => {
    const scene = new Scene();
    const { o, a, x } = addPoints(scene, { o: [0, 0], a: [3, 0], x: [0, 3] });
    const result = onCircle.sketch({ o, a, x }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'on_circle',
      bindings: { o, a, x },
      edges: [[o, x]],
      circles: [],
    });
  });
});

describe('on_circle derive slot project', () => {
  it('snaps x onto the circle of radius |oa| around o in the cursor direction', () => {
    const scene = new Scene();
    const { o, a } = addPoints(scene, { o: [0, 0], a: [5, 0] });
    const deriveSlot = onCircle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    // Cursor directly above o: result should be at (0, 5)
    const cursor = { x: 0, y: 10, _kind: 'world' as const };
    const pt = deriveSlot.project({ o, a }, scene, cursor);
    expect(pt.x).toBeCloseTo(0);
    expect(pt.y).toBeCloseTo(5);
  });

  it('falls back to the right direction when cursor is at o', () => {
    const scene = new Scene();
    const { o, a } = addPoints(scene, { o: [0, 0], a: [5, 0] });
    const deriveSlot = onCircle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    const cursor = { x: 0, y: 0, _kind: 'world' as const };
    const pt = deriveSlot.project({ o, a }, scene, cursor);
    expect(pt.x).toBeCloseTo(5);
    expect(pt.y).toBeCloseTo(0);
  });
});

describe('on_circle derive slot preview', () => {
  it('shows the circle once o and a are placed', () => {
    const scene = new Scene();
    const { o, a } = addPoints(scene, { o: [0, 0], a: [5, 0] });
    const deriveSlot = onCircle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    const prev = deriveSlot.preview({ o, a }, scene);
    expect(prev).toHaveLength(1);
    expect(prev[0].kind).toBe('circle');
  });

  it('shows nothing before o and a are placed', () => {
    const scene = new Scene();
    const { o } = addPoints(scene, { o: [0, 0] });
    const deriveSlot = onCircle.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');
    expect(deriveSlot.preview({ o }, scene)).toEqual([]);
  });
});

describe('on_circle entry validate', () => {
  it('rejects o === a', () => {
    const scene = new Scene();
    const { o } = addPoints(scene, { o: [0, 0] });
    expect(onCircle.validate!({ o, a: o }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct o and a', () => {
    const scene = new Scene();
    const { o, a } = addPoints(scene, { o: [0, 0], a: [5, 0] });
    expect(onCircle.validate!({ o, a }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(onCircle.validate!({}, scene)).toBeNull();
  });
});
