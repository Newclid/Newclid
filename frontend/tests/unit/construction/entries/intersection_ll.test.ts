import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { intersectionLL } from '../../../../src/construction/entries/intersection_ll';

describe('intersection_ll entry slots', () => {
  it('has four pick slots and no edges or circles', () => {
    expect(intersectionLL.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick', 'pick']);
    expect(intersectionLL.edges).toEqual([]);
    expect(intersectionLL.circles).toEqual([]);
  });
});

describe('intersection_ll entry sketch', () => {
  it('places the intersection of two perpendicular lines', () => {
    const scene = new Scene();
    // Line 1: y=0 (horizontal), Line 2: x=2 (vertical)
    const { a, b, c, d } = addPoints(scene, {
      a: [0, 0], b: [4, 0],
      c: [2, -2], d: [2, 2],
    });
    const result = intersectionLL.sketch({ a, b, c, d }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'intersection_ll',
      bindings: { a, b, c, d },
      edges: [],
      circles: [],
    });

    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    expect(x.kind).toBe('point');
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(2);
      expect(x.y).toBeCloseTo(0);
    }

    const lines = (result as { lines?: [string, string][] }).lines;
    expect(lines).toEqual([[a, b], [c, d]]);
  });

  it('places the intersection of two diagonal lines', () => {
    const scene = new Scene();
    // y = x and y = -x intersect at origin
    const { a, b, c, d } = addPoints(scene, {
      a: [-1, -1], b: [1, 1],
      c: [-1, 1], d: [1, -1],
    });
    const result = intersectionLL.sketch({ a, b, c, d }, scene);
    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(0);
      expect(x.y).toBeCloseTo(0);
    }
  });
});

describe('intersection_ll entry preview', () => {
  it('previews both lines and intersection point when a, b, c are set', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [4, 0], c: [2, -2] });
    const cursor = { x: 2, y: 2, _kind: 'world' as const };
    const prev = intersectionLL.preview!({ a, b, c }, scene, cursor);
    // two auxLines and one point
    expect(prev.some(p => p.kind === 'auxLine')).toBe(true);
    expect(prev.some(p => p.kind === 'point')).toBe(true);
  });

  it('previews nothing when fewer than three points are set', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const cursor = { x: 2, y: 2, _kind: 'world' as const };
    expect(intersectionLL.preview!({ a, b }, scene, cursor)).toEqual([]);
  });

  it('shows two auxLines but no intersection point for parallel lines', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [4, 0], c: [0, 2] });
    // cursor represents d at (4, 2) — parallel to a-b
    const cursor = { x: 4, y: 2, _kind: 'world' as const };
    const prev = intersectionLL.preview!({ a, b, c }, scene, cursor);
    const auxLines = prev.filter(p => p.kind === 'auxLine');
    const points = prev.filter(p => p.kind === 'point');
    expect(auxLines).toHaveLength(2);
    expect(points).toHaveLength(0);
  });
});

describe('intersection_ll entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(intersectionLL.validate!({ a: a, b: a, c: b, d: b }, scene)).toMatch(/distinct/i);
  });

  it('rejects c === d', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(intersectionLL.validate!({ a, b, c: b, d: b }, scene)).toMatch(/distinct/i);
  });

  it('rejects parallel lines', () => {
    const scene = new Scene();
    const { a, b, c, d } = addPoints(scene, {
      a: [0, 0], b: [4, 0],
      c: [0, 2], d: [4, 2],
    });
    expect(intersectionLL.validate!({ a, b, c, d }, scene)).toMatch(/parallel/i);
  });

  it('accepts intersecting lines', () => {
    const scene = new Scene();
    const { a, b, c, d } = addPoints(scene, {
      a: [0, 0], b: [4, 0],
      c: [2, -2], d: [2, 2],
    });
    expect(intersectionLL.validate!({ a, b, c, d }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(intersectionLL.validate!({}, scene)).toBeNull();
  });
});
