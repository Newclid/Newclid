import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { onAline } from '../../../../src/construction/entries/on_aline';

describe('on_aline entry slots', () => {
  it('has five pick-existing/pick slots and one derive slot', () => {
    const kinds = onAline.slots.map(s => s.kind);
    expect(kinds).toEqual(['pick-existing', 'pick-existing', 'pick-existing', 'pick-existing', 'pick-existing', 'derive']);
  });
});

describe('on_aline entry sketch', () => {
  it('records the angle-transfer construction with two lines', () => {
    const scene = new Scene();
    // Source angle: c=(1,0), d=(0,0), e=(0,1) → 90° at origin
    // Reference: a=(5,0), b=(5,3) with b on one ray
    // x somewhere on the transferred angle line
    const { c, d, e, b, a, x } = addPoints(scene, {
      c: [1, 0], d: [0, 0], e: [0, 1],
      b: [8, 0], a: [5, 0],
      x: [5, 3],
    });
    const result = onAline.sketch({ c, d, e, b, a, x }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'on_aline',
      circles: [],
    });

    const lines = (result as { lines?: [string, string][] }).lines;
    expect(lines).toContainEqual([a, b]);
    expect(lines).toContainEqual([a, x]);
  });
});

describe('on_aline derive slot project', () => {
  it('snaps cursor onto the nearest copied-angle line', () => {
    const scene = new Scene();
    // Copy 90° angle (c=x-axis arm, d=origin, e=y-axis arm) onto a=(5,0), b=(8,0)
    const { c, d, e, b, a } = addPoints(scene, {
      c: [1, 0], d: [0, 0], e: [0, 1],
      b: [8, 0], a: [5, 0],
    });
    const deriveSlot = onAline.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');

    // Cursor above a: should snap to the perpendicular (90° from the reference ray a-b)
    const cursor = { x: 5, y: 5, _kind: 'world' as const };
    const pt = deriveSlot.project({ c, d, e, b, a }, scene, cursor);
    // The point should be on the line through a (x=5)
    expect(pt.x).toBeCloseTo(5);
  });
});

describe('on_aline entry preview', () => {
  it('shows the reference ray and two copied-angle rays when all inputs are set', () => {
    const scene = new Scene();
    const { c, d, e, b, a } = addPoints(scene, {
      c: [1, 0], d: [0, 0], e: [0, 1],
      b: [8, 0], a: [5, 0],
    });
    const cursor = { x: 5, y: 5, _kind: 'world' as const };
    const prev = onAline.preview!({ c, d, e, b, a }, scene, cursor);
    expect(prev.length).toBe(3);
    expect(prev.every(p => p.kind === 'auxLine')).toBe(true);
  });

  it('shows nothing when not all inputs are placed', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [5, 0], b: [8, 0] });
    const cursor = { x: 5, y: 5, _kind: 'world' as const };
    expect(onAline.preview!({ a, b }, scene, cursor)).toEqual([]);
  });
});

describe('on_aline derive slot inner preview', () => {
  it('returns empty — preview is handled at the entry level', () => {
    const scene = new Scene();
    const { c, d, e, b, a } = addPoints(scene, {
      c: [1, 0], d: [0, 0], e: [0, 1],
      b: [8, 0], a: [5, 0],
    });
    const deriveSlot = onAline.slots.find(s => s.kind === 'derive')!;
    if (deriveSlot.kind !== 'derive') throw new Error('expected derive slot');
    expect(deriveSlot.preview({ c, d, e, b, a }, scene)).toEqual([]);
  });
});

describe('on_aline entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [5, 0] });
    expect(onAline.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects collinear source angle points', () => {
    const scene = new Scene();
    const { c, d, e } = addPoints(scene, { c: [0, 0], d: [1, 0], e: [2, 0] });
    expect(onAline.validate!({ c, d, e }, scene)).toMatch(/collinear/i);
  });

  it('accepts valid inputs', () => {
    const scene = new Scene();
    const { c, d, e, b, a } = addPoints(scene, {
      c: [1, 0], d: [0, 0], e: [0, 1],
      b: [8, 0], a: [5, 0],
    });
    expect(onAline.validate!({ c, d, e, b, a }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(onAline.validate!({}, scene)).toBeNull();
  });
});
