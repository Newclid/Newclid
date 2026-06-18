import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { angleMirror } from '../../../../src/construction/entries/angle_mirror';

describe('angle_mirror entry slots', () => {
  it('has three pick slots and no edges or circles', () => {
    expect(angleMirror.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick']);
    expect(angleMirror.edges).toEqual([]);
    expect(angleMirror.circles).toEqual([]);
  });
});

describe('angle_mirror entry sketch', () => {
  it('reflects a across the line b-c', () => {
    const scene = new Scene();
    // a=(0,2), b=(0,0), c=(4,0): mirror line is x-axis, reflection of (0,2) → (0,-2)
    const { a, b, c } = addPoints(scene, { a: [0, 2], b: [0, 0], c: [4, 0] });
    const result = angleMirror.sketch({ a, b, c }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'angle_mirror',
      bindings: { a, b, c },
      circles: [],
    });

    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    expect(x.kind).toBe('point');
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(0);
      expect(x.y).toBeCloseTo(-2);
    }

    const edges = (result as { edges: [string, string][] }).edges;
    expect(edges).toEqual([[b, a], [b, c], [b, xId]]);
  });

  it('reflects across a diagonal mirror line', () => {
    const scene = new Scene();
    // Mirror line y=x through b=(0,0), c=(1,1); reflect a=(1,0) → (0,1)
    const { a, b, c } = addPoints(scene, { a: [1, 0], b: [0, 0], c: [1, 1] });
    const result = angleMirror.sketch({ a, b, c }, scene);
    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(0);
      expect(x.y).toBeCloseTo(1);
    }
  });
});

describe('angle_mirror entry preview', () => {
  it('previews the mirror line and reflected arm once a and b are placed', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 2], b: [0, 0] });
    const cursor = { x: 4, y: 0, _kind: 'world' as const };
    const prev = angleMirror.preview!({ a, b }, scene, cursor);
    expect(prev.length).toBeGreaterThanOrEqual(3);
    expect(prev.some(p => p.kind === 'auxLine')).toBe(true);
    expect(prev.some(p => p.kind === 'point')).toBe(true);
  });

  it('previews nothing before a and b are placed', () => {
    const scene = new Scene();
    const cursor = { x: 4, y: 0, _kind: 'world' as const };
    expect(angleMirror.preview!({}, scene, cursor)).toEqual([]);
  });
});

describe('angle_mirror entry validate', () => {
  it('rejects duplicate points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(angleMirror.validate!({ a, b, c: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects collinear points', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [2, 0], c: [4, 0] });
    expect(angleMirror.validate!({ a, b, c }, scene)).toMatch(/collinear/i);
  });

  it('accepts valid non-collinear points', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 2], b: [0, 0], c: [4, 0] });
    expect(angleMirror.validate!({ a, b, c }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(angleMirror.validate!({}, scene)).toBeNull();
  });
});
