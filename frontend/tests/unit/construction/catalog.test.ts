import { describe, it, expect } from 'vitest';
import { CONSTRUCTION_CATALOG } from '../../../src/construction/catalog';

describe('CONSTRUCTION_CATALOG', () => {
  it('keys every entry by its own name', () => {
    for (const [key, entry] of Object.entries(CONSTRUCTION_CATALOG)) {
      expect(entry.name).toBe(key);
    }
  });

  it('contains every expected built-in construction exactly once', () => {
    const expectedNames = [
      'select', 'point', 'circle', 'line', 'segment', 'midpoint',
      'angle_bisector', 'circumcircle', 'perpendicular', 'parallel', 'foot',
      'parallelogram', 'eq_triangle', 'iso_triangle', 'mirror', 'angle_mirror',
      'rectangle', 'eqdistance', 'lc_tangent', 'on_aline', 'intersection_ll',
      'intersection_cc', 'intersection_lc', 'on_circle', 'on_line', 'triangle',
    ];
    expect(Object.keys(CONSTRUCTION_CATALOG).sort()).toEqual(expectedNames.sort());
  });

  it('gives every entry a non-empty label and a single-character shortcut', () => {
    for (const entry of Object.values(CONSTRUCTION_CATALOG)) {
      expect(entry.label.length).toBeGreaterThan(0);
      expect(entry.shortcut).toHaveLength(1);
    }
  });

  it('builds a fresh, distinct SVG icon node on every call', () => {
    for (const entry of Object.values(CONSTRUCTION_CATALOG)) {
      const first = entry.icon();
      const second = entry.icon();
      expect(first.tagName.toLowerCase()).toBe('svg');
      expect(first).not.toBe(second);
    }
  });

  it('declares slots, edges and circles as arrays for every entry', () => {
    for (const entry of Object.values(CONSTRUCTION_CATALOG)) {
      expect(Array.isArray(entry.slots)).toBe(true);
      expect(Array.isArray(entry.edges)).toBe(true);
      expect(Array.isArray(entry.circles)).toBe(true);
    }
  });
});
