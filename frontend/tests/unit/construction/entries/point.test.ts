import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { point } from '../../../../src/construction/entries/point';

describe('point entry', () => {
  it('has a single place-free slot', () => {
    expect(point.slots).toEqual([{ name: 'p', kind: 'place-free', label: 'Place a point' }]);
  });

  it('sketches nothing since the slot already placed the point', () => {
    const scene = new Scene();
    expect(point.sketch({}, scene)).toBeNull();
  });
});
