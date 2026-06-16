import { describe, it, expect } from 'vitest';
import { world } from '../../../src/geometry/coords';
import { pickNearestPoint } from '../../../src/geometry/hitTest';
import type { GeoObject, PointObject } from '../../../src/geometry/types-object';

function point(id: string, x: number, y: number): PointObject {
  return { id, kind: 'point', x, y, label: id };
}

describe('pickNearestPoint', () => {
  it('returns null when there are no objects', () => {
    const objects = new Map<string, GeoObject>();
    const result = pickNearestPoint(objects, world(0, 0), { tolerancePx: 12, scale: 50 });
    expect(result).toBeNull();
  });

  it('returns the point within tolerance', () => {
    const a = point('a', 1, 1);
    const objects = new Map<string, GeoObject>([['a', a]]);
    const result = pickNearestPoint(objects, world(1, 1), { tolerancePx: 12, scale: 50 });
    expect(result).toBe(a);
  });

  it('returns null when the nearest point is outside tolerance', () => {
    const a = point('a', 10, 10);
    const objects = new Map<string, GeoObject>([['a', a]]);
    // tolerance in world units = tolerancePx / scale = 12 / 50 = 0.24
    const result = pickNearestPoint(objects, world(0, 0), { tolerancePx: 12, scale: 50 });
    expect(result).toBeNull();
  });

  it('scales tolerance by the current zoom', () => {
    const a = point('a', 1, 0);
    const objects = new Map<string, GeoObject>([['a', a]]);
    // distance is 1 world unit; tol = 12 / scale must exceed 1 to hit.
    expect(
      pickNearestPoint(objects, world(0, 0), { tolerancePx: 12, scale: 50 }),
    ).toBeNull();
    expect(
      pickNearestPoint(objects, world(0, 0), { tolerancePx: 12, scale: 2 }),
    ).toBe(a);
  });

  it('picks the closest of several candidates within tolerance', () => {
    // tol = tolerancePx / scale = 12 / 50 = 0.24, so both points qualify.
    const near = point('near', 0.05, 0);
    const farther = point('farther', 0.2, 0);
    const objects = new Map<string, GeoObject>([
      ['near', near],
      ['farther', farther],
    ]);
    const result = pickNearestPoint(objects, world(0, 0), { tolerancePx: 12, scale: 50 });
    expect(result).toBe(near);
  });

  it('ignores a candidate outside tolerance even if no point has been picked yet', () => {
    const tooFar = point('tooFar', 0.3, 0);
    const objects = new Map<string, GeoObject>([['tooFar', tooFar]]);
    const result = pickNearestPoint(objects, world(0, 0), { tolerancePx: 12, scale: 50 });
    expect(result).toBeNull();
  });

  it('ignores non-point objects', () => {
    const circle: GeoObject = {
      id: 'c',
      kind: 'circle',
      mode: 'center-through',
      center: 'a',
      through: 'b',
    };
    const objects = new Map<string, GeoObject>([['c', circle]]);
    const result = pickNearestPoint(objects, world(0, 0), { tolerancePx: 12, scale: 50 });
    expect(result).toBeNull();
  });

  it('returns null when kinds filter excludes points', () => {
    const a = point('a', 0, 0);
    const objects = new Map<string, GeoObject>([['a', a]]);
    const result = pickNearestPoint(objects, world(0, 0), {
      tolerancePx: 12,
      scale: 50,
      kinds: ['circle'],
    });
    expect(result).toBeNull();
  });

  it('matches when kinds filter includes point', () => {
    const a = point('a', 0, 0);
    const objects = new Map<string, GeoObject>([['a', a]]);
    const result = pickNearestPoint(objects, world(0, 0), {
      tolerancePx: 12,
      scale: 50,
      kinds: ['point'],
    });
    expect(result).toBe(a);
  });
});
