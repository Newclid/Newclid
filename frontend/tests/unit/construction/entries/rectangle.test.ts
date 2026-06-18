import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { rectangle } from '../../../../src/construction/entries/rectangle';

describe('rectangle entry slots', () => {
  it('has two pick slots and no edges or circles', () => {
    expect(rectangle.slots.map(s => s.kind)).toEqual(['pick', 'pick']);
    expect(rectangle.edges).toEqual([]);
    expect(rectangle.circles).toEqual([]);
  });
});

describe('rectangle entry sketch', () => {
  it('computes b and d from opposite corners a and c', () => {
    const scene = new Scene();
    // a=(0,0), c=(4,3) → b=(4,0), d=(0,3)
    const { a, c } = addPoints(scene, { a: [0, 0], c: [4, 3] });
    const result = rectangle.sketch({ a, c }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'rectangle',
      bindings: { a, c },
      circles: [],
    });

    const bindings = (result as { bindings: Record<string, string> }).bindings;
    const b = scene.objects.get(bindings.b)!;
    const d = scene.objects.get(bindings.d)!;

    expect(b.kind).toBe('point');
    expect(d.kind).toBe('point');
    if (b.kind === 'point') {
      expect(b.x).toBeCloseTo(4);
      expect(b.y).toBeCloseTo(0);
    }
    if (d.kind === 'point') {
      expect(d.x).toBeCloseTo(0);
      expect(d.y).toBeCloseTo(3);
    }

    const edges = (result as { edges: [string, string][] }).edges;
    expect(edges).toEqual([[a, bindings.b], [bindings.b, c], [c, bindings.d], [bindings.d, a]]);
  });
});

describe('rectangle entry preview', () => {
  it('previews the four sides while placing c', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 4, y: 3, _kind: 'world' as const };
    const prev = rectangle.preview!({ a }, scene, cursor);
    expect(prev).toHaveLength(4);
    expect(prev.every(p => p.kind === 'auxLine')).toBe(true);
  });

  it('previews nothing before a is placed', () => {
    const scene = new Scene();
    const cursor = { x: 4, y: 3, _kind: 'world' as const };
    expect(rectangle.preview!({}, scene, cursor)).toEqual([]);
  });
});

describe('rectangle entry validate', () => {
  it('rejects a === c', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(rectangle.validate!({ a, c: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects corners on the same row (y equal)', () => {
    const scene = new Scene();
    const { a, c } = addPoints(scene, { a: [0, 0], c: [4, 0] });
    expect(rectangle.validate!({ a, c }, scene)).toMatch(/zero-area/i);
  });

  it('rejects corners on the same column (x equal)', () => {
    const scene = new Scene();
    const { a, c } = addPoints(scene, { a: [0, 0], c: [0, 3] });
    expect(rectangle.validate!({ a, c }, scene)).toMatch(/zero-area/i);
  });

  it('accepts valid opposite corners', () => {
    const scene = new Scene();
    const { a, c } = addPoints(scene, { a: [0, 0], c: [4, 3] });
    expect(rectangle.validate!({ a, c }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(rectangle.validate!({}, scene)).toBeNull();
  });
});
