import { describe, it, expect } from 'vitest';
import { world } from '../../../src/geometry/coords';
import {
  distance,
  distanceToCircle,
  projectOntoLine,
  circumcenter,
} from '../../../src/geometry/primitives';

describe('distance', () => {
  it('is zero for a point to itself', () => {
    expect(distance(world(2, 5), world(2, 5))).toBe(0);
  });

  it('computes the euclidean distance between two points', () => {
    expect(distance(world(0, 0), world(3, 4))).toBe(5);
  });

  it('is symmetric', () => {
    const a = world(1, 2);
    const b = world(7, -3);
    expect(distance(a, b)).toBeCloseTo(distance(b, a));
  });
});

describe('distanceToCircle', () => {
  it('is zero for a point exactly on the circle', () => {
    expect(distanceToCircle(world(5, 0), world(0, 0), 5)).toBeCloseTo(0);
  });

  it('is positive for a point outside the circle', () => {
    expect(distanceToCircle(world(10, 0), world(0, 0), 5)).toBeCloseTo(5);
  });

  it('is positive for a point inside the circle', () => {
    expect(distanceToCircle(world(1, 0), world(0, 0), 5)).toBeCloseTo(4);
  });
});

describe('projectOntoLine', () => {
  it('returns the point itself when it already lies on the line', () => {
    const p = projectOntoLine({ x: 0, y: 0 }, { x: 4, y: 0 }, { x: 2, y: 0 });
    expect(p.x).toBeCloseTo(2);
    expect(p.y).toBeCloseTo(0);
  });

  it('drops a perpendicular onto a horizontal line', () => {
    const p = projectOntoLine({ x: 0, y: 0 }, { x: 4, y: 0 }, { x: 2, y: 3 });
    expect(p.x).toBeCloseTo(2);
    expect(p.y).toBeCloseTo(0);
  });

  it('drops a perpendicular onto a vertical line', () => {
    const p = projectOntoLine({ x: 0, y: 0 }, { x: 0, y: 4 }, { x: 3, y: 2 });
    expect(p.x).toBeCloseTo(0);
    expect(p.y).toBeCloseTo(2);
  });

  it('extrapolates beyond the segment endpoints since the line is infinite', () => {
    const p = projectOntoLine({ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 5, y: 3 });
    expect(p.x).toBeCloseTo(5);
    expect(p.y).toBeCloseTo(0);
  });
});

describe('circumcenter', () => {
  it('finds the center of a right triangle at the midpoint of the hypotenuse', () => {
    const c = circumcenter({ x: 0, y: 0 }, { x: 4, y: 0 }, { x: 0, y: 4 });
    expect(c).not.toBeNull();
    expect(c!.x).toBeCloseTo(2);
    expect(c!.y).toBeCloseTo(2);
  });

  it('finds the center of a triangle equidistant from all vertices', () => {
    const p1 = { x: 0, y: 0 };
    const p2 = { x: 6, y: 0 };
    const p3 = { x: 3, y: 5 };
    const c = circumcenter(p1, p2, p3);
    expect(c).not.toBeNull();
    const d1 = Math.hypot(c!.x - p1.x, c!.y - p1.y);
    const d2 = Math.hypot(c!.x - p2.x, c!.y - p2.y);
    const d3 = Math.hypot(c!.x - p3.x, c!.y - p3.y);
    expect(d1).toBeCloseTo(d2);
    expect(d2).toBeCloseTo(d3);
  });

  it('returns null for collinear points', () => {
    const c = circumcenter({ x: 0, y: 0 }, { x: 1, y: 1 }, { x: 2, y: 2 });
    expect(c).toBeNull();
  });
});
