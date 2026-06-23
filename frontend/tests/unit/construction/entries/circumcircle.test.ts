import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { circumcircle } from '../../../../src/construction/entries/circumcircle';

describe('circumcircle entry slots', () => {
  it('has three pick slots and no edges or circles', () => {
    expect(circumcircle.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick']);
    expect(circumcircle.edges).toEqual([]);
    expect(circumcircle.circles).toEqual([]);
  });
});

describe('circumcircle entry sketch', () => {
  it('places the circumcenter and draws the circle through three points', () => {
    const scene = new Scene();
    // Right triangle on x-axis: circumcenter is midpoint of hypotenuse = (2,0)
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [4, 0], c: [0, 4] });
    const result = circumcircle.sketch({ a, b, c }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'circumcircle',
      bindings: { a, b, c },
      edges: [],
      circles: [],
    });

    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    expect(x.kind).toBe('point');
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(2);
      expect(x.y).toBeCloseTo(2);
    }

    const circumcircles = (result as { circumcircles?: [string, string, string][] }).circumcircles;
    expect(circumcircles).toEqual([[a, b, c]]);
  });

  it('places an equilateral triangle circumcenter at the centroid', () => {
    const scene = new Scene();
    // Equilateral triangle with side 2: circumradius = 2/√3
    const h = Math.sqrt(3);
    const { a, b, c } = addPoints(scene, {
      a: [-1, 0], b: [1, 0], c: [0, h],
    });
    const result = circumcircle.sketch({ a, b, c }, scene);
    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(0);
      expect(x.y).toBeCloseTo(h / 3);
    }
  });

  // sketch falls back to pa coords when circumcenter returns null for collinear input
  it('sketch falls back to pa coords when points are collinear', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [1, 0], c: [2, 0] });
    const result = circumcircle.sketch({ a, b, c }, scene);
    const bindings = (result as { bindings: Record<string, string> }).bindings;
    const x = scene.objects.get(bindings.x)!;
    expect(x.kind).toBe('point');
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(0);
      expect(x.y).toBeCloseTo(0);
    }
  });
});

describe('circumcircle entry preview', () => {
  it('previews the circumcircle once two points are placed', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const cursor = { x: 2, y: 3, _kind: 'world' as const };
    const prev = circumcircle.preview!({ a, b }, scene, cursor);
    expect(prev).toHaveLength(1);
    expect(prev[0].kind).toBe('circle');
  });

  it('previews nothing before two points are placed', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 2, y: 3, _kind: 'world' as const };
    expect(circumcircle.preview!({ a }, scene, cursor)).toEqual([]);
  });

  it('previews nothing when cursor is collinear with a and b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    // Cursor on the same line → no unique circumcircle
    const cursor = { x: 2, y: 0, _kind: 'world' as const };
    expect(circumcircle.preview!({ a, b }, scene, cursor)).toEqual([]);
  });
});

describe('circumcircle entry validate', () => {
  it('rejects duplicate points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(circumcircle.validate!({ a, b, c: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects collinear points', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [2, 0], c: [4, 0] });
    expect(circumcircle.validate!({ a, b, c }, scene)).toMatch(/collinear/i);
  });

  it('accepts non-collinear distinct points', () => {
    const scene = new Scene();
    const { a, b, c } = addPoints(scene, { a: [0, 0], b: [4, 0], c: [2, 3] });
    expect(circumcircle.validate!({ a, b, c }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(circumcircle.validate!({}, scene)).toBeNull();
  });

  // validate returns null when bound ids reference points not yet in scene
  it('validate returns null when bound ids are not yet in the scene', () => {
    const scene = new Scene();
    expect(circumcircle.validate!({ a: 'p99', b: 'p100', c: 'p101' }, scene)).toBeNull();
  });
});
