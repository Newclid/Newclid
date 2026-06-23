import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addCircle, addPoints } from '../../../helpers/scene';
import { intersectionCC } from '../../../../src/construction/entries/intersection_cc';

describe('intersection_cc entry slots', () => {
  it('has two pick-existing slots and no edges or circles', () => {
    expect(intersectionCC.slots.map(s => s.kind)).toEqual(['pick-existing', 'pick-existing']);
    expect(intersectionCC.edges).toEqual([]);
    expect(intersectionCC.circles).toEqual([]);
  });
});

describe('intersection_cc entry sketch', () => {
  it('places two intersection points of two overlapping circles', () => {
    const scene = new Scene();
    // Circle 1: center (-2, 0), radius 3 → through (1, 0)
    const { center: o, through: ra } = addCircle(scene, [-2, 0], [1, 0]);
    // Circle 2: center (2, 0), radius 3 → through (-1, 0)
    const { center: w, through: rb } = addCircle(scene, [2, 0], [-1, 0]);

    const result = intersectionCC.sketch({ o, w }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'intersection_cc',
      bindings: { o, w, ra, rb },
      edges: [],
      circles: [],
    });

    const bindings = (result as { bindings: Record<string, string> }).bindings;
    const x = scene.objects.get(bindings.x)!;
    const y = scene.objects.get(bindings.y)!;
    expect(x.kind).toBe('point');
    expect(y.kind).toBe('point');
    // Both intersection points lie on both circles: |x - o| ≈ 3 and |x - w| ≈ 3
    if (x.kind === 'point') {
      expect(Math.hypot(x.x - (-2), x.y)).toBeCloseTo(3);
      expect(Math.hypot(x.x - 2, x.y)).toBeCloseTo(3);
    }
  });

  it('places a single tangent point when circles are externally tangent', () => {
    const scene = new Scene();
    // Circle 1: center (0,0) radius 2, Circle 2: center (4,0) radius 2 → tangent at (2,0)
    const { center: o } = addCircle(scene, [0, 0], [2, 0]);
    const { center: w } = addCircle(scene, [4, 0], [2, 0]);

    const result = intersectionCC.sketch({ o, w }, scene);
    const bindings = (result as { bindings: Record<string, string> }).bindings;
    expect(bindings.x).toBeDefined();
    expect(bindings.y).toBeUndefined();
  });
});

describe('intersection_cc sketch with circumcircle center', () => {
  it('recognises a circumcircle construction center as a circle', () => {
    const scene = new Scene();
    // Build a circumcircle manually so intersectionCC can find it via bindings.x
    const { a, b, c } = addPoints(scene, { a: [0, 4], b: [-4, 0], c: [4, 0] });
    const xId = scene.addPoint(0, 0); // circumcenter of equilateral-ish triangle above
    scene.addObject({
      kind: 'construction',
      name: 'circumcircle',
      bindings: { a, b, c, x: xId },
      edges: [],
      circles: [],
      circumcircles: [[a, b, c]],
    });

    // A normal circle to intersect with
    const { center: w } = addPoints(scene, { center: [-3, 0] });
    const { through: wThrough } = { through: scene.addPoint(-6, 0) };
    scene.addObject({ kind: 'circle', mode: 'center-through', center: w, through: wThrough });

    // The circumcircle center is xId; validate should recognise it and return null (circles intersect)
    const err = intersectionCC.validate!({ o: xId, w }, scene);
    expect(err).toBeNull();
  });
});

describe('intersection_cc entry validate', () => {
  it('rejects o that is not a circle center', () => {
    const scene = new Scene();
    const { center: w } = addCircle(scene, [4, 0], [7, 0]);
    // Use a point id that doesn't have a circle
    const fakeId = 'p999';
    expect(intersectionCC.validate!({ o: fakeId, w }, scene)).toMatch(/centre of an existing circle/i);
  });

  it('rejects w that is not a circle center', () => {
    const scene = new Scene();
    const { center: o } = addCircle(scene, [0, 0], [3, 0]);
    const fakeId = 'p999';
    expect(intersectionCC.validate!({ o, w: fakeId }, scene)).toMatch(/centre of an existing circle/i);
  });

  it('rejects o === w', () => {
    const scene = new Scene();
    const { center: o } = addCircle(scene, [0, 0], [3, 0]);
    expect(intersectionCC.validate!({ o, w: o }, scene)).toMatch(/different circles/i);
  });

  it('rejects circles that do not intersect', () => {
    const scene = new Scene();
    const { center: o } = addCircle(scene, [0, 0], [1, 0]);  // radius 1
    const { center: w } = addCircle(scene, [10, 0], [11, 0]); // radius 1, far away
    expect(intersectionCC.validate!({ o, w }, scene)).toMatch(/do not intersect/i);
  });

  it('accepts two intersecting circles', () => {
    const scene = new Scene();
    const { center: o } = addCircle(scene, [0, 0], [3, 0]);
    const { center: w } = addCircle(scene, [4, 0], [1, 0]);
    expect(intersectionCC.validate!({ o, w }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(intersectionCC.validate!({}, scene)).toBeNull();
  });

  // validate should return an error mentioning circle when o points to a point with no circle centered there
  it('validate rejects a point with no circle centred there', () => {
    const scene = new Scene();
    const { o, w } = addPoints(scene, { o: [0, 0], w: [5, 0] });
    expect(intersectionCC.validate!({ o, w }, scene)).toMatch(/circle/i);
  });
});
