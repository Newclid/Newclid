import { describe, it, expect } from 'vitest';
import { world, screen } from '../../../src/geometry/coords';

describe('world', () => {
  it('carries the given x and y', () => {
    const p = world(3, -4);
    expect(p.x).toBe(3);
    expect(p.y).toBe(-4);
  });
});

describe('screen', () => {
  it('carries the given x and y', () => {
    const p = screen(10, 20);
    expect(p.x).toBe(10);
    expect(p.y).toBe(20);
  });
});
