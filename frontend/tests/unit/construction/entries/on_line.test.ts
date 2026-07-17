import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { onLine } from '../../../../src/construction/entries/on_line';

describe('on_line entry slots', () => {
  it('has two pick slots and one derive slot', () => {
    expect(onLine.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'derive']);
    expect(onLine.edges).toEqual([]);
    expect(onLine.circles).toEqual([]);
  });
});

describe('on_line entry sketch', () => {
  it('records the point-on-line construction', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [4, 0], p: [2, 0] });
    const result = onLine.sketch({ a, b, p }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'on_line',
      bindings: { a, b, p },
      edges: [],
      circles: [],
    });
  });
});

describe('on_line derive slot project', () => {
  it('snaps cursor onto the horizontal line a-b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const deriveSlot = onLine.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    const cursor = { x: 2, y: 5, _kind: 'world' as const };
    const pt = deriveSlot.project({ a, b }, scene, cursor);
    expect(pt.x).toBeCloseTo(2);
    expect(pt.y).toBeCloseTo(0);
  });

  it('snaps cursor onto a diagonal line', () => {
    const scene = new Scene();
    // Line y=x: a=(0,0), b=(4,4)
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 4] });
    const deriveSlot = onLine.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    const cursor = { x: 3, y: 0, _kind: 'world' as const };
    const pt = deriveSlot.project({ a, b }, scene, cursor);
    expect(pt.x).toBeCloseTo(1.5);
    expect(pt.y).toBeCloseTo(1.5);
  });
});

describe('on_line derive slot inner preview', () => {
  it('returns empty — the line highlight is provided by the committed line object', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const deriveSlot = onLine.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');
    expect(deriveSlot.preview({ a, b }, scene)).toEqual([]);
  });
});

describe('on_line entry onSlotFilled', () => {
  it('adds the line object to the scene when slot b is filled', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const countBefore = scene.objects.size;
    onLine.onSlotFilled!('b', { a, b }, scene);
    expect(scene.objects.size).toBeGreaterThan(countBefore);
    const constructions = [...scene.objects.values()].filter(o => o.kind === 'construction');
    expect(constructions.length).toBeGreaterThan(0);
  });

  it('does nothing when slot a is filled', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const countBefore = scene.objects.size;
    onLine.onSlotFilled!('a', { a, b }, scene);
    expect(scene.objects.size).toBe(countBefore);
  });
});

describe('on_line entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(onLine.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct a and b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    expect(onLine.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(onLine.validate!({}, scene)).toBeNull();
  });
});
