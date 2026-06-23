import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints, addCircle } from '../../../helpers/scene';
import { intersectionLC } from '../../../../src/construction/entries/intersection_lc';

describe('intersection_lc entry slots', () => {
  it('has two pick slots and one pick-existing slot', () => {
    expect(intersectionLC.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick-existing']);
  });
});

describe('intersection_lc entry sketch', () => {
  it('places two intersection points where the line crosses the circle', () => {
    const scene = new Scene();
    // Circle: center (5,0), through (8,0) → radius 3
    const { center: o, through } = addCircle(scene, [5, 0], [8, 0]);
    // Line: the x-axis (y=0) through (0,0) and (10,0) — it crosses the circle at (2,0) and (8,0)
    const { a, b } = addPoints(scene, { a: [0, 0], b: [10, 0] });

    const result = intersectionLC.sketch({ a, b, o }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'intersection_lc',
      bindings: { a, b, o, ra: through },
      edges: [],
      circles: [],
    });

    const bindings = (result as { bindings: Record<string, string> }).bindings;
    const x = scene.objects.get(bindings.x)!;
    const y = scene.objects.get(bindings.y)!;
    expect(x.kind).toBe('point');
    expect(y.kind).toBe('point');
    // The two x-coords should be 2 and 8 (order may vary)
    const xs = [x, y].map(p => p.kind === 'point' ? p.x : NaN).sort((a, b) => a - b);
    expect(xs[0]).toBeCloseTo(2);
    expect(xs[1]).toBeCloseTo(8);

    const lines = (result as { lines?: [string, string][] }).lines;
    expect(lines).toEqual([[a, b]]);
  });

  it('places a single tangent point when the line is tangent to the circle', () => {
    const scene = new Scene();
    // Circle: center (0,3), through (0,0) → radius 3 (tangent line is y=0)
    const { center: o } = addCircle(scene, [0, 3], [0, 0]);
    const { a, b } = addPoints(scene, { a: [-4, 0], b: [4, 0] });

    const result = intersectionLC.sketch({ a, b, o }, scene);
    const bindings = (result as { bindings: Record<string, string> }).bindings;
    expect(bindings.x).toBeDefined();
    expect(bindings.y).toBeUndefined();
  });
});

describe('intersection_lc entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(intersectionLC.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects picking a non-circle center', () => {
    const scene = new Scene();
    const { a, b, o } = addPoints(scene, { a: [0, 0], b: [4, 0], o: [5, 0] });
    expect(intersectionLC.validate!({ a, b, o }, scene)).toMatch(/centre of an existing circle/i);
  });

  it('rejects a line that misses the circle', () => {
    const scene = new Scene();
    const { center: o } = addCircle(scene, [0, 10], [3, 10]); // radius 3, far above x-axis
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    expect(intersectionLC.validate!({ a, b, o }, scene)).toMatch(/does not cross/i);
  });

  it('accepts a line that crosses the circle', () => {
    const scene = new Scene();
    const { center: o } = addCircle(scene, [2, 0], [5, 0]); // radius 3 on x-axis
    const { a, b } = addPoints(scene, { a: [0, 0], b: [6, 0] });
    expect(intersectionLC.validate!({ a, b, o }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(intersectionLC.validate!({}, scene)).toBeNull();
  });

  // returns null when only o is bound and no line points have been picked yet
  it('validate returns null when only o is provided (line and circle not yet set)', () => {
    const scene = new Scene();
    const { center: o } = addCircle(scene, [2, 0], [5, 0]);
    expect(intersectionLC.validate!({ o }, scene)).toBeNull();
  });

  // returns a circle-related error when o refers to a non-point object (circleAtCentre returns null)
  it('validate rejects o pointing to a non-point object', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [4, 0] });
    const circleId = scene.addObject({ kind: 'circle', mode: 'center-through', center: a, through: b });
    expect(intersectionLC.validate!({ a, b, o: circleId }, scene)).toMatch(/circle/i);
  });
});
